import datetime as dt
import json
import logging
from typing import Any, Dict, Optional, Set, Union, override

LOG_RECORD_BUILTIN_ATTRS: Set[str] = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
    "taskName",
}


class MinimalJsonFormatter(logging.Formatter):
    def __init__(self, fmt_keys: Optional[Dict[str, str]] = None) -> None:
        logging.Formatter.__init__(self)
        self.fmt_keys: Dict[str, str] = fmt_keys or {}

    @override
    def format(self, record: logging.LogRecord) -> Dict[str, Optional[Any]]:
        message = {
            key: getattr(record, key, None) or getattr(record, val, None)
            for key, val in self.fmt_keys.items()
        }
        if record.exc_info:
            message["exc_info"] = self.formatException(record.exc_info)
        if record.stack_info:
            message["stack_info"] = self.formatStack(record.stack_info)
        if record.msg:
            message["message"] = record.msg
        message.update(
            {
                key: val
                for key, val in record.__dict__.items()
                if key not in LOG_RECORD_BUILTIN_ATTRS
            }
        )
        return json.dumps(message, ensure_ascii=False, default=str)


class JSONFormatter(logging.Formatter):
    def __init__(self, fmt_keys: Optional[Dict[str, str]] = None) -> None:
        logging.Formatter.__init__(self)
        self.fmt_keys: Dict[str, str] = fmt_keys or {}

    @override
    def format(self, record: logging.LogRecord) -> str:
        record_dict: Dict[str, str] = self.__get_record_dict(record)
        return json.dumps(record_dict, ensure_ascii=False, default=str)

    def __get_record_dict(self, record: logging.LogRecord) -> Dict[str, str]:
        always_fields: Dict[str, str] = {
            "timestamp": dt.datetime.fromtimestamp(
                record.created, tz=dt.timezone.utc
            ).isoformat(),
            "message": record.getMessage(),
        }
        if record.exc_info is not None:
            always_fields["exc_info"] = self.formatException(record.exc_info)

        if record.stack_info is not None:
            always_fields["stack_info"] = self.formatStack(record.stack_info)

        message: Dict[str, Union[str, Any]] = {
            key: (
                msg_val
                if (msg_val := always_fields.pop(val, None)) is not None
                else getattr(record, val)
            )
            for key, val in self.fmt_keys.items()
        }
        message.update(always_fields)

        for key, val in record.__dict__.items():
            if key not in LOG_RECORD_BUILTIN_ATTRS:
                message[key] = val

        return message


class DebugFilter(logging.Filter):
    @override
    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno <= logging.INFO


class NoCriticalFilter(logging.Filter):
    @override
    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno <= logging.CRITICAL
