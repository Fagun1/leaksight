"""
Structured JSON logging for log aggregation (PROJECT_SPEC_CONTINUATION §9.2).
"""
import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Optional


class StructuredFormatter(logging.Formatter):
    """Outputs JSON-structured log lines."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info),
            }
        for key in ["url", "domain", "worker_id", "rumor_id", "source_id", "duration_ms", "status_code", "component", "event_type"]:
            if hasattr(record, key):
                log_entry[key] = getattr(record, key)
        return json.dumps(log_entry)


def setup_logging(level: str = "INFO", component: str = "app"):
    """Configure structured logging."""
    import logging.handlers
    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper()))
    root.handlers.clear()
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(StructuredFormatter())
    root.addHandler(console)
    return root


class ComponentLogger:
    """Component-specific logger with context fields."""

    def __init__(self, component: str):
        self.logger = logging.getLogger(component)
        self.component = component

    def _log(self, level: int, message: str, **kwargs):
        extra = {"component": self.component, **kwargs}
        self.logger.log(level, message, extra=extra)

    def info(self, message: str, **kwargs):
        self._log(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs):
        self._log(logging.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs):
        self._log(logging.ERROR, message, **kwargs)

    def debug(self, message: str, **kwargs):
        self._log(logging.DEBUG, message, **kwargs)
