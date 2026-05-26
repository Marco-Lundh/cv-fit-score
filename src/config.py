from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    groq_api_key: str

    model_config = {"env_file": ".env"}


settings = Settings()
