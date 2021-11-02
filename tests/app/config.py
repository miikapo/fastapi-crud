import os

from typing import Type


class Config:
    SQLALCHEMY_DATABASE_URI_SYNC = "postgresql://user:password@postgres:5432/db"
    SQLALCHEMY_DATABASE_URI = "postgresql+asyncpg://user:password@postgres:5432/db"


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI_SYNC = "postgresql://user:password@postgres-test:5432/db"
    SQLALCHEMY_DATABASE_URI = "postgresql+asyncpg://user:password@postgres-test:5432/db"


def get_config() -> Type[Config]:
    env = os.getenv("ENV", "").lower()
    if env == "development":
        return Config
    return TestConfig


app_config = get_config()
