from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    bot_token: SecretStr
    admins: List[int]

    postgres_user: str
    postgres_password: SecretStr
    postgres_db: str
    postgres_host: str
    postgres_port: int

    mongo_host: str
    mongo_port: int
    mongo_db: str

    redis_host: str
    redis_port: int
    redis_db: int = 0

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("admins", mode="before")
    def split_admins(cls, v):
        if isinstance(v, str):
            return [int(admin.strip()) for admin in v.split(",")]
        return v


config = Settings()
