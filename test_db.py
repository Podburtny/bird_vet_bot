from sqlalchemy import text

from database import engine


def test() -> None:
    with engine.connect() as conn:
        result = conn.execute(text("select 1"))
        print("DB OK:", result.scalar())


if __name__ == "__main__":
    test()