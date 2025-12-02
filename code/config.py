from pydantic_settings import BaseSettings

class AppConfig(BaseSettings):
    DATABASE_URL: str
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    GITHUB_WEBHOOK_SECRET: str
    TELEGRAM_BOT_TOKEN: str
    TEMP_BUILD_DIR: str = '/tmp/builds'

    class Config:
        env_file = "example.env" # поменять на .env