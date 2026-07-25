from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from config import settings
from models.db import Base

url = settings.database_url
connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}

engine = create_engine(
    url,
    echo=False,
    pool_pre_ping=True,
    connect_args=connect_args,
)

# Схема БД создаётся напрямую (SQLite, один файл) — alembic не нужен.
Base.metadata.create_all(engine)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db_session() -> Session:
    with SessionLocal() as session:
        yield session
