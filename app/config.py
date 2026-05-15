from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = "development"
    secret_key: str = "dev-secret-key"

    database_url: str = "sqlite+aiosqlite:///./dev.db"

    redis_url: str = "redis://localhost:6379/0"

    token_expire_seconds: int = 3600

    address_api_url: str = "https://www.meiguodizhi.com/api/v1/dz"
    address_api_referer: str = "https://www.meiguodizhi.com/"
    address_api_timeout: float = 10.0
    address_api_mock_on_failure: bool = True

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
