import logging
from config import settings


def setup_logging():
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def main():
    setup_logging()

    logger = logging.getLogger(__name__)
    logger.info("Bird Vet Bot starting...")
    logger.info("Config loaded successfully")


if __name__ == "__main__":
    main()