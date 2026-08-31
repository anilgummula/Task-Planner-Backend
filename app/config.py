from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 days

    google_client_id: str
    google_client_secret: str

    gemini_api_key: str
    gemini_model: str = "gemini-2.5-flash"

    frontend_origin: str = "https://flowline-2050.netlify.app"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()

