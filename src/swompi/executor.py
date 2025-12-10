import os
import tempfile
import yaml
import re
import time
import docker
from schema import Schema, Optional, SchemaError, And, Or
from git import Repo, GitCommandError
from functions import update_build_status_to_running, finalize_build
from models import BuildStatus

class Executor:
    def __init__(self, db_session_factory, s3_client, config):
        self.db_session_factory = db_session_factory
        self.s3_client = s3_client
        self.config = config

    def run_build(self, build_id, request_json):
        with self.db_session_factory() as db_session:
            update_build_status_to_running(db_session, build_id)
            repo_url = request_json['repository']['clone_url']
            commit_sha = request_json['after']

            workspace_path, workspace_object = self._prepare_workspace(build_id)

            try:
                self._clone_repo(repo_url, commit_sha, workspace_path)
                config_data = self._read_and_validate_config(workspace_path)
                env_dict = self._create_enviroment_dict(workspace_path, request_json, config_data, build_id)
                self._create_build_script(workspace_path, config_data)
                self._run_docker_container(build_id, workspace_path, config_data, env_dict)
                time.sleep(10000)
            except Exception as e:
                print(f"ERROR during build {build_id}: {e}")
                self._mark_build_as_failed(build_id, str(e))
            finally:
                self._cleanup_workspace(workspace_object)

    def _prepare_workspace(self, build_id):
        workspace_path = tempfile.TemporaryDirectory(prefix=f"swompi_build_{build_id}_")

        return workspace_path.name, workspace_path

    def _clone_repo(self, repo_url, commit_sha, workspace_path):
        try:
            print(f"Cloning {repo_url} into {workspace_path}")
            repo = Repo.clone_from(repo_url, workspace_path)
            print(f"Checking out commit {commit_sha}")
            repo.git.checkout(commit_sha)
        except GitCommandError as e:
            raise RuntimeError(f"Failed to clone repo or checkout commit: {e}")

    def _read_and_validate_config(self, workspace_path):
        non_empty_list_of_strings = And([str], lambda l: len(l) > 0, error='This list cannot be empty')

        valid_image_name = And(str, lambda s: not re.search(r'\s', s), error='Image name cannot contain whitespace')

        CONFIG_SCHEMA = Schema({
            "image": valid_image_name,
            Optional("variables"): {str: Or(int, str)},
            Optional("before_script"): [str],
            "scripts": non_empty_list_of_strings,
            Optional("after_script"): [str],
            Optional("artifacts"): {
                "paths": non_empty_list_of_strings
            }
        })

        file_path = self._find_config_file(workspace_path)

        try:
            with open(file_path, 'r') as f:
                configuration = yaml.safe_load(f)

            if configuration is None:
                raise Exception("Configuration file is empty or invalid.")

            CONFIG_SCHEMA.validate(configuration)
            
            print(f"Configuration file {file_path} is valid.")
            return configuration

        except yaml.YAMLError as e:
            raise Exception(f"YAML syntax error: {e}")
        except SchemaError as e:
            raise Exception(f"Configuration error: {e}")
        except Exception as e:
            raise Exception(f"ERROR during read configuration {e}")

    def _find_config_file(self, workspace_path):
        config_filename = '.swompi.yml'
        for root, dirs, files in os.walk(workspace_path):
            if config_filename in files:
                return os.path.join(root, config_filename)
            break 
        return None

        if len(result) > 1:
            raise Exception("Found multiple .swompi.yml files in root directory")
        if len(result) < 1:
            raise Exception("Not found .swompi.yml files in root directory")
        
        return result[0]

    def _create_enviroment_dict(self, workspace_path, request_json, config_data, build_id):
        env_dict = {
            "CI_COMMIT_SHA": request_json['after'],
            "CI_COMMIT_MESSAGE": request_json['head_commit']['message'],
            "CI_COMMIT_AUTHOR": request_json['head_commit']['author']['username'],
            "CI_PROJECT_DIR": "/app",
            "CI_REPO_URL": request_json['repository']['html_url'],
            "CI_BUILD_ID": build_id,
            "CI_SERVER_NAME": "Swompi-Runner",
            "CI_COMMIT_REF_NAME": self._parse_ref(request_json['ref'])
        }

        env_dict = env_dict | config_data["variables"]
        print(f"Enviroment dictionary succesfully created {env_dict}")
        return env_dict

    def _parse_ref(self, ref_string):
        parts = ref_string.split('/')
        if len(parts) < 3 or parts[0] != 'refs':
            return None
        return '/'.join(parts[2:])

    def _create_build_script(self, workspace_path, config_data):
        script_file_path = os.path.join(workspace_path, "_run.sh")
        with open(script_file_path, "w") as f:
            f.write("set -e\n")
            for command in config_data["before_script"]:
                f.write(f"{command}\n")

            for command in config_data["scripts"]:
                f.write(f"{command}\n")
        print(f"Script file succesfully created {script_file_path}")

    def _run_docker_container(self, build_id, workspace_path, config_data, env_dict):
        client = docker.from_env()
        volume = {workspace_path: {
            "bind": "/app",
            "mode": "rw"
        }}
        cmd = ["sh", "/app/_run.sh"]
        container = None
        try:
            container = client.containers.create(
                image=config_data["image"],
                command=cmd,
                environment=env_dict,
                volumes=volume,
                working_dir='/app',
                tty=False
            )
            
            container.start()
            
            log_stream = container.logs(stream=True, stdout=True, stderr=True)
            
            print("Container is running, capturing logs...")
            log_file_path = os.path.join(workspace_path, "build.log")
            
            with open(log_file_path, "w", encoding="utf-8") as f:
                for log_chunk in log_stream:
                    line = log_chunk.decode('utf-8')
                    if line.endswith("stderr\n"):
                        f.write(f"STDERR: {line[:-8]}\n")
                    else:
                        f.write(f"STDOUT: {line}")

            result = container.wait()
            exit_code = result['StatusCode']
            
            print(f"Container finished with exit code: {exit_code}")
            print(f"Log file available here: {log_file_path}")

            if exit_code != 0:
                self._mark_build_as_failed(build_id, "Error during build. Check logs for more.")

        except docker.errors.ImageNotFound as e:
            self._mark_build_as_failed(build_id, e)
        except Exception as e:
            raise Exception(f"ERROR during running docker container: {e}")

        finally:
            if container:
                container.remove()

    def _mark_build_as_failed(self, build_id, error):
        with self.db_session_factory() as db_session:
            finalize_build(db_session, build_id, BuildStatus.failed, "None")
            print(f"Marking build {build_id} as FAILED. Reason: {error}")

    def _cleanup_workspace(self, workspace_path):
        print(f"Cleaning up workspace: {workspace_path.name}")
        workspace_path.cleanup()
