import atexit
import json
import logging
import logging.config
import pathlib
from typing import Any, Dict


def init_looger() -> logging.Logger:
    logger: logging.Logger = logging.getLogger(__name__)
    config_file = pathlib.Path(".//log_config.json")
    with open(config_file) as f:
        config: Dict[str, Any] = json.load(f)
    logging.config.dictConfig(config)
    if queue_handler := logging.getHandlerByName("queue_handler"):
        queue_handler.listener.start()
        atexit.register(queue_handler.listener.stop)
    return logger


def main() -> None:
    logger: logging.Logger = init_looger()
    logger.debug("This is debug", extra={"foo": "bar"})
    logger.info("This is info", extra={"foo": "bar"})
    logger.warning("This is warning", extra={"foo": "bar"})
    logger.error("This is error", extra={"foo": "bar"})
    logger.critical("This is critical", extra={"foo": "bar"})
    logger.log(
        logging.INFO,
        "",
        extra={
            "if message field is empty": "then MinimalJsonFormatter wont print it on terminal."
        },
    )


if __name__ == "__main__":
    main()
