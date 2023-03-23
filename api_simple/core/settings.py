from datetime import timedelta

from dotenv import load_dotenv
from pydantic import BaseSettings, PostgresDsn

load_dotenv()


class Settings(BaseSettings):
    grpc_port: int = ...
    grpc_host: str = ...


settings = Settings()
