from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    grpc_port: int = ...
    grpc_host: str = ...

    authjwt_secret_key: str = ...
    authjwt_algorithm: str = ...


settings = Settings()
