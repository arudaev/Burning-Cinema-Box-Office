from pydantic import EmailStr
from pydantic.config import ConfigDict
from pydantic_settings import BaseSettings

from burningbackend import __version__
from burningbackend.app.core.enums import LogLevel


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", case_sensitive=True)

    # Application
    PROJECT_NAME: str = "Burning Register API"
    PROJECT_VERSION: str = __version__
    API_V1_STR: str = "v1"
    DEBUG: bool = False
    CORS_ORIGINS: list[str] = ["http://localhost:8080"]
    USE_CORRELATION_ID: bool = True

    UVICORN_HOST: str = "0.0.0.0"
    UVICORN_PORT: int = 8080

    LOG_LEVEL: str = LogLevel.INFO

    # MongoDB
    MONGODB_URI: str = "mongodb://localhost:27017/"
    MONGODB_DB_NAME: str = "burningregister"

    # Superuser
    FIRST_SUPERUSER: str = "admin"
    FIRST_SUPERUSER_EMAIL: EmailStr = "admin@example.com"
    FIRST_SUPERUSER_PASSWORD: str = "changeme"

    # Authentication — SECRET_KEY has no default; must be supplied via env var
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 1
    SECRET_KEY: str


settings = Settings()
