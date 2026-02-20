from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env')
    DATABASE_URL: str = 'postgresql+asyncpg://user:pass@host:port/db'


settings = Settings()
