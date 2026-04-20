from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str

    APP_NAME: str = "Pickla API V1"
    DEBUG: bool = False

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60


settings = Settings()
