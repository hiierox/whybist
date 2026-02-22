from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env')
    DATABASE_URL: str = 'postgresql+asyncpg://user:pass@host:port/db'
    SECRET_KEY: str = ''

ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

settings = Settings()
