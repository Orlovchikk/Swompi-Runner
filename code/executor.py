import os
import tempfile
import yaml
import re
from git import Repo, GitCommandError
from schema import Schema, Optional, SchemaError, And, Or
import time

class Executor:
    def __init__(self, db_session_factory, s3_client, config):
        self.db_session_factory = db_session_factory
        self.s3_client = s3_client
        self.config = config

    def run_build(self, build_id, request_json):
        repo_url = request_json['repository']['clone_url']
        commit_sha = request_json['after']

        workspace_path, workspace_object = self._prepare_workspace(build_id)

        try:
            self._clone_repo(repo_url, commit_sha, workspace_path)
            config_data = self._read_and_validate_config(workspace_path)
            self._create_enviroment_file(workspace_path, request_json, config_data, build_id)
            self._create_build_script(workspace_path, config_data)
            self._run_docker_container(workspace_path, config_data)
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

    def _create_enviroment_file(self, workspace_path, request_json, config_data, build_id):
        env_file_path = os.path.join(workspace_path, ".swompi.env")
        with open(env_file_path, "w") as f:
            ci_commit_sha = request_json['after']
            ci_commit_message = request_json['head_commit']['message']
            ci_commit_author = request_json['head_commit']['author']['username']
            ci_repo_url = request_json['repository']['html_url']
            ci_commit_ref_name = self._parse_ref(request_json['ref'])
            f.write(f'CI_COMMIT_SHA="{ci_commit_sha}"\n')
            f.write(f'CI_COMMIT_MESSAGE="{ci_commit_message}"\n')
            f.write(f'CI_COMMIT_AUTHOR="{ci_commit_author}"\n')
            f.write('CI_PROJECT_DIR="/app"\n')
            f.write(f'CI_REPO_URL="{ci_repo_url}\n')
            f.write(f'CI_BUILD_ID="build_id}\n')
            f.write('CI_SERVER_NAME="Swompi-Runner"\n')
            f.write(f'CI_COMMIT_REF_NAME="{ci_commit_ref_name}"\n')

            print(config_data, config_data["variables"])
            for variable, value in config_data["variables"].items():
                f.write(f'{variable}="{value}"\n')
            print(f"Enviroment file succesfully created {env_file_path}")

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

    def _run_docker_container(self, workspace_path, config_data):
        pass
    
    def _mark_build_as_failed(self, build_id, error):
        print(f"Marking build {build_id} as FAILED. Reason: {error}")
        pass

    def _cleanup_workspace(self, workspace_path):
        print(f"Cleaning up workspace: {workspace_path.name}")
        workspace_path.cleanup()
