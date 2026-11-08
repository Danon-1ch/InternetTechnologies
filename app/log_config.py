import logging
import os

DEFAULT_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def status_level(status_code: int) -> int:
    if status_code >= 500:
        return logging.ERROR
    if status_code >= 400:
        return logging.WARNING
    return logging.INFO


def setup_logging() -> None:
    level = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)
    handler: logging.Handler = logging.StreamHandler()
    log_file = os.getenv("LOG_FILE")
    if log_file:
        handler = logging.FileHandler(log_file)
    handler.setFormatter(
        logging.Formatter(
            os.getenv("LOG_FORMAT", DEFAULT_FORMAT),
            os.getenv("LOG_DATE_FORMAT", DEFAULT_DATE_FORMAT),
        )
    )
    logger = logging.getLogger("app")
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False
