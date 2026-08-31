from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://planner:planner@postgres:5432/planner_db"
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 days

    google_client_id: str = ""
    google_client_secret: str = ""

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    frontend_origin: str = "http://localhost:5173"

    class Config:
        env_file = ".env"


settings = Settings()
