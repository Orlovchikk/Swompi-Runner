import os
import tempfile
import yaml
import re
from git import Repo, GitCommandError
from schema import Schema, Optional, SchemaError, And, Or

class Executor:
    def __init__(self, db_session_factory, s3_client, config):
        self.db_session_factory = db_session_factory
        self.s3_client = s3_client
        self.config = config

    def run_build(self, build_id, repo_url, commit_sha):
        workspace_path, workspace_object = self._prepare_workspace(build_id)

        try:
            self._clone_repo(repo_url, commit_sha, workspace_path)
            config_data = self._read_and_validate_config(workspace_path)
            print(config_data)
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

    def _mark_build_as_failed(self, build_id, error):
        print(f"Marking build {build_id} as FAILED. Reason: {error}")
        pass

    def _cleanup_workspace(self, workspace_path):
        print(f"Cleaning up workspace: {workspace_path.name}")
        workspace_path.cleanup()
