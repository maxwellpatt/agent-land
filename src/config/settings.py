from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None

    default_model: str = "openai:gpt-4o"
    temperature: float = 0.7

    log_level: str = "INFO"
    log_file: str = "logger.txt"

    debug: bool = False


settings = Settings()
