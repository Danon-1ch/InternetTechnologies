import logging

import pytest

from app.log_config import DEFAULT_DATE_FORMAT, DEFAULT_FORMAT, setup_logging, status_level

pytestmark = pytest.mark.unit


@pytest.fixture(autouse=True)
def restore_app_logger():
    logger = logging.getLogger("app")
    handlers = list(logger.handlers)
    level = logger.level
    yield
    for handler in logger.handlers:
        if handler not in handlers:
            handler.close()
    logger.handlers[:] = handlers
    logger.setLevel(level)


@pytest.mark.parametrize(
    ("status_code", "level"),
    [
        (200, logging.INFO),
        (404, logging.WARNING),
        (500, logging.ERROR),
    ],
)
def test_status_level(status_code, level):
    assert status_level(status_code) == level


def test_setup_logging_uses_env_and_stream(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "debug")
    monkeypatch.setenv("LOG_FORMAT", "%(levelname)s:%(message)s")
    monkeypatch.setenv("LOG_DATE_FORMAT", "%H:%M")
    monkeypatch.delenv("LOG_FILE", raising=False)

    setup_logging()

    logger = logging.getLogger("app")
    assert logger.level == logging.DEBUG
    assert logger.propagate is False
    assert len(logger.handlers) == 1
    assert type(logger.handlers[0]) is logging.StreamHandler
    assert logger.handlers[0].formatter._fmt == "%(levelname)s:%(message)s"
    assert logger.handlers[0].formatter.datefmt == "%H:%M"


def test_setup_logging_uses_defaults_for_invalid_level(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "not-a-level")
    monkeypatch.delenv("LOG_FORMAT", raising=False)
    monkeypatch.delenv("LOG_DATE_FORMAT", raising=False)
    monkeypatch.delenv("LOG_FILE", raising=False)

    setup_logging()

    handler = logging.getLogger("app").handlers[0]
    assert logging.getLogger("app").level == logging.INFO
    assert handler.formatter._fmt == DEFAULT_FORMAT
    assert handler.formatter.datefmt == DEFAULT_DATE_FORMAT


def test_setup_logging_writes_to_file(monkeypatch, tmp_path):
    log_file = tmp_path / "app.log"
    monkeypatch.setenv("LOG_FILE", str(log_file))

    setup_logging()
    handler = logging.getLogger("app").handlers[0]
    logging.getLogger("app").warning("hello")

    assert isinstance(handler, logging.FileHandler)
    assert "hello" in log_file.read_text(encoding="utf-8")
