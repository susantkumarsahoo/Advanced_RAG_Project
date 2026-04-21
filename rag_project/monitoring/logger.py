import logging
import os
from logging.handlers import RotatingFileHandler


def get_logger(logger_name: str,
               log_dir: str = "logs",
               level: int = logging.INFO) -> logging.Logger:

    logger = logging.getLogger(logger_name)

    if logger.handlers:
        return logger

    os.makedirs(log_dir, exist_ok=True)

    log_file_path = os.path.join(log_dir, f"{logger_name}.log")

    logger.setLevel(level)
    logger.propagate = False

    formatter = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    )

    # Rotating file handler (production standard)
    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=10 * 1024 * 1024,
        backupCount=5
    )
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger




