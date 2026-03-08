from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str

    ALLOWED_USER_IDS: str
    ADMIN_ID: int

    OPENROUTER_API_KEY: str

    DATABASE_URL: str

    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_BUCKET: str

    SENTRY_DSN: str | None = None

    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"

    @property
    def allowed_user_ids(self) -> List[int]:
        return [int(x) for x in self.ALLOWED_USER_IDS.split(",")]


settings = Settings()