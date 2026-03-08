import asyncio
import asyncpg

from config import settings


async def main() -> None:
    dsn = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

    print("DATABASE_URL =", dsn)

    conn = await asyncpg.connect(
        dsn=dsn,
        ssl="require",
        timeout=20,
    )

    value = await conn.fetchval("select 1")
    print("DB OK:", value)

    await conn.close()


if __name__ == "__main__":
    asyncio.run(main())