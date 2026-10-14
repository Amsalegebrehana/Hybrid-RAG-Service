from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / '.env', extra='ignore')

    chunk_size: int = 800
    chunk_overlap: int = 100

    embedding_model: str = 'BAAI/bge-small-en-v1.5'
    query_prompt: str = 'Represent this sentence for searching relevant passages: '

    @model_validator(mode='after')
    def _check_chunking(self) -> 'Settings':
        if not 0 <= self.chunk_overlap < self.chunk_size:
            raise ValueError('chunk_overlap must be >= 0 and < chunk_size')
        return self


settings = Settings()
