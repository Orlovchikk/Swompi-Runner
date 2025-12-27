import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
import os
import shutil
import py7zr

class FileStorageRepository:
    def __init__(self, config):
        self.s3_client = self._create_s3_client(config)
        self.BUCKET = "swompi-runner"
        self._ensure_buckets_exist()

    def _create_s3_client(self, config):
        s3 = boto3.resource('s3')

        s3_client = boto3.client(
            's3',
            endpoint_url=config.S3_ENDPOINT_URL,
            aws_access_key_id=config.S3_ACCESS_KEY,
            aws_secret_access_key=config.S3_SECRET_KEY,
            region_name=config.S3_DEFAULT_REGION,
            config=Config(
            signature_version='s3v4',
            s3={'addressing_style': 'path'}
        )
        )
        return s3_client

    def _ensure_buckets_exist(self):
        try:
            self.s3_client.head_bucket(Bucket=self.BUCKET)
        except ClientError as e:
            if e.response['Error']['Code'] in ['404', '403', '400']:
                print(f"Bucket '{self.BUCKET}' not found. Creating it...")
                self.s3_client.create_bucket(Bucket=self.BUCKET)
            else:
                raise

    def upload_logs_and_artifacts(self, build_id: int, workspace_path: str, artifacts: None | list[str]) -> str:
        object_key = f"{build_id}.7z"
        archive_filename = f"build_{build_id}_archive.7z"
        archive_dir = os.path.join(workspace_path, archive_filename)
        staging_dir = os.path.join(workspace_path, "archive")
        os.makedirs(staging_dir)
        
        shutil.move(os.path.join(workspace_path, "build.log"), staging_dir)
        
        if artifacts:
            for artifact in artifacts:
                artifact_path = os.path.join(workspace_path, artifact)
                if os.path.exists(artifact_path):
                    shutil.move(artifact_path, staging_dir)
        
        print(f"Creating archive at: {archive_dir}")
        with py7zr.SevenZipFile(archive_dir, 'w') as archive:
            archive.writeall(staging_dir, 'build_files')

        print(f"Uploading {archive_dir} to S3 as {object_key}...")

        self.s3_client.upload_file(
            archive_dir,
            self.BUCKET,
            object_key
        )

        print(f"Logs and artifacts for build {build_id} uploaded to {self.BUCKET}/{object_key}")
        return object_key

    def download_file_to_path(self, object_key: str, download_path: str):
        try:
            self.s3_client.download_file(self.BUCKET, object_key, download_path)
            print(f"File {self.BUCKET}/{object_key} downloaded to {download_path}")
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                print(f"File not found: {self.BUCKET}/{object_key}")
                return False
            else:
                raise