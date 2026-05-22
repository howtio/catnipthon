from __future__ import annotations

import logging


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(f"catnip.{name}")
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter(
                "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
                datefmt="%Y-%m-%dT%H:%M:%S",
            )
        )
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
    return logger
