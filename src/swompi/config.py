from pydantic_settings import BaseSettings

class AppConfig(BaseSettings):
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOSTNAME: str
    S3_ENDPOINT_URL: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_DEFAULT_REGION: str
    GITHUB_WEBHOOK_SECRET: str
    TELEGRAM_BOT_TOKEN: str

    class Config:
        env_file = ".env"