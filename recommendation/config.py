import logging
from pydantic import Field
from pydantic_settings import BaseSettings
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    RESEND_API_KEY: str
    URL_DATABASE: str
    SECRET_KEY: str

    class Config:
        env_file = ".env"


settings = Settings()
