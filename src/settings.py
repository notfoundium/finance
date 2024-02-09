from pydantic import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str

    RABBITMQ_DEFAULT_USER: str
    RABBITMQ_DEFAULT_PASS: str
    RABBITMQ_DEFAULT_VHOST: str


settings = Settings(_env_file=".env", _env_file_encoding="utf-8")
