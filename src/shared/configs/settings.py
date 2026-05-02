from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["dev", "stg", "prod"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str
    TEST_DATABASE_URL: str

    REDIS_URL: str

    APP_NAME: str = "Pickla API V1"
    ENVIRONMENT: Environment = "dev"

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    @property
    def debug(self) -> bool:
        return self.ENVIRONMENT == "dev"

    @property
    def log_json(self) -> bool:
        return self.ENVIRONMENT in ("stg", "prod")


settings = Settings()
