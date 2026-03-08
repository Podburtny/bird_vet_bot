from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from config import settings


engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db_session() -> Session:
    with SessionLocal() as session:
        yield session