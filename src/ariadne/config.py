import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    openrouter_base_url: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    openrouter_model: str = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
    openrouter_embedding_model: str = os.getenv("OPENROUTER_EMBEDDING_MODEL", "openai/text-embedding-3-large")

    storage_dir: str = os.getenv("ARIADNE_STORAGE_DIR", "~/.ariadne")

    @property
    def resolved_storage_dir(self) -> str:
        return os.path.expanduser(self.storage_dir)

    def validate(self):
        if not self.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY is not set in environment or .env file.")

settings = Settings()
