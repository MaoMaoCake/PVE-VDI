from pydantic import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "PVE VDI"

    class Config:
        env_file = 'backend/backend.env'
        env_file_encoding = 'utf-8'

@lru_cache()
def get_settings():
    return Settings()