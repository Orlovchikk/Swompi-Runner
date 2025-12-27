from pydantic_settings import BaseSettings

class AppConfig(BaseSettings):
    POSTGRES_DB: str = "postgres"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOSTNAME: str = "database"
    S3_ENDPOINT_URL: str = "http://garage:3900"
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_DEFAULT_REGION: str = "garage"
    TELEGRAM_BOT_TOKEN: str