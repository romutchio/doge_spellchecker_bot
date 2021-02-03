from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    TELEGRAM_TOKEN: str = Field(..., env='TELEGRAM_TOKEN')


settings = Settings()
