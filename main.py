import asyncio
import logging

import sentry_sdk

from bot import bot, dp
from config import settings
from handlers import register_routers
from middlewares.access_control import AccessControlMiddleware
from middlewares.logging import LoggingMiddleware


def setup_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def setup_sentry() -> None:
    if settings.SENTRY_DSN:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            traces_sample_rate=0.0,
        )


async def main() -> None:
    setup_logging()
    setup_sentry()

    logger = logging.getLogger(__name__)

    dp.update.middleware(LoggingMiddleware())
    dp.update.middleware(AccessControlMiddleware())

    register_routers(dp)

    logger.info("Bird Vet Bot starting...")
    logger.info("Allowed users: %s", settings.allowed_user_ids)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())