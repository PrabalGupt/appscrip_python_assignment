# from pydantic import BaseSettings, Field
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")
    rate_limit_requests: int = Field(3, env="RATE_LIMIT_REQUESTS")
    rate_limit_window_seconds: int = Field(60, env="RATE_LIMIT_WINDOW_SECONDS")
    jwt_secret: str = Field(..., env="JWT_SECRET")
    jwt_algorithm: str = Field("HS256", env="JWT_ALGORITHM")
    jwt_expire_minutes: int = Field(60, env="JWT_EXPIRE_MINUTES")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
