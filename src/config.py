from functools import lru_cache
from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_FILE = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    groq_api_key: str = ""

    model_config = SettingsConfigDict(env_file=_ENV_FILE)

    @model_validator(mode="after")
    def check_api_key(self) -> "Settings":
        if not self.groq_api_key:
            raise ValueError(
                "GROQ_API_KEY is not set. "
                "Add it to .env or the environment."
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
