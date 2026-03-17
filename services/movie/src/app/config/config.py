from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env')
    KINOPOISK_API_KEY: str = ''
    REDIS_HOST: str = 'redis'
    REDIS_PORT: int = 6379


settings = Settings()
