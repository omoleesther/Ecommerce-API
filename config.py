import logging
from pydantic import Field
from pydantic_settings import BaseSettings
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    RESEND_API_KEY: str
    URL_DATABASE: str
    SECRET_KEY: str
    PAYSTACK_TEST_SECRET_KEY: str
    BASE_URL: str = "http://127.0.0.1:8000"

    class Config:
        env_file = ".env"


settings = Settings()
