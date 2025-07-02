# config/logging_config.py
import logging.config
from pathlib import Path

def setup_logging():
    """
    Configures logging for the entire application.
    - Creates a 'logs' directory if it doesn't exist.
    - Sets up logging to both console (INFO) and a rotating file (DEBUG).
    - Silences noisy third-party libraries.
    """
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "app.log"

    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "default",
                "filename": log_file,
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8",
            },
        },
        "loggers": {
            # Silence noisy libraries by setting their level to WARNING or ERROR
            "openai": {"level": "WARNING", "handlers": ["console", "file"], "propagate": False},
            "httpx": {"level": "WARNING", "handlers": ["console", "file"], "propagate": False},
            "httpcore": {"level": "WARNING", "handlers": ["console", "file"], "propagate": False},
            "chromadb": {"level": "WARNING", "handlers": ["console", "file"], "propagate": False},
            "unstructured": {"level": "WARNING", "handlers": ["console", "file"], "propagate": False},
            "pdfminer": {"level": "ERROR", "handlers": ["console", "file"], "propagate": False},
            "googleapiclient": {"level": "WARNING", "handlers": ["console", "file"], "propagate": False},
        },
        "root": {
            "level": "DEBUG",  # Capture all levels, handlers will filter
            "handlers": ["console", "file"],
        },
    }

    logging.config.dictConfig(LOGGING_CONFIG)
    logging.info("Logging configured successfully.")