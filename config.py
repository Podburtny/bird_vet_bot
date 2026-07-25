from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str

    ALLOWED_USER_IDS: str = ""
    ADMIN_ID: int | None = None

    OPENROUTER_API_KEY: str

    # Локальное хранилище: SQLite-файл и папка с фото внутри DATA_DIR.
    DATA_DIR: str = "data"
    DATABASE_URL: str | None = None

    # Модели OpenRouter
    ANSWER_MODEL: str = "anthropic/claude-sonnet-4.5"
    SUMMARY_MODEL: str = "google/gemini-2.0-flash"
    TRANSCRIBE_MODEL: str = "google/gemini-2.5-flash"

    # Новый кейс после стольких часов тишины
    CASE_TIMEOUT_HOURS: float = 4.0

    SENTRY_DSN: str | None = None
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"

    @property
    def allowed_user_ids(self) -> List[int]:
        return [int(x) for x in self.ALLOWED_USER_IDS.split(",") if x.strip()]

    @property
    def data_path(self) -> Path:
        path = Path(self.DATA_DIR)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"sqlite:///{self.data_path / 'birdvet.sqlite3'}"


settings = Settings()
