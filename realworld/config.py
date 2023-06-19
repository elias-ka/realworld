import logging

from pydantic import SecretStr
from starlette.config import Config

config = Config(".env")

LOG_LEVEL = config("LOG_LEVEL", cast=str, default=logging.WARNING)
DATABASE_HOSTNAME = config("DATABASE_HOSTNAME", cast=str, default="localhost")
DATABASE_PORT = config("DATABASE_PORT", cast=str, default="5432")
DATABASE_NAME = config("DATABASE_NAME", cast=str, default="realworld")
DATABASE_CREDENTIALS = config("DATABASE_CREDENTIALS", cast=SecretStr)
(
    _DATABASE_CREDENTIALS_USER,
    _DATABASE_CREDENTIAL_PASSWORD,
) = DATABASE_CREDENTIALS.get_secret_value().split(":")
DATABASE_ENGINE_POOL_SIZE = config("DATABASE_ENGINE_POOL_SIZE", cast=int, default=10)
SQL_ALCHEMY_DATABASE_URI = f"postgresql+psycopg://{_DATABASE_CREDENTIALS_USER}:{_DATABASE_CREDENTIAL_PASSWORD}@{DATABASE_HOSTNAME}:{DATABASE_PORT}/{DATABASE_NAME}"
