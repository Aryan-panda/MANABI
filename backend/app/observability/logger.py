import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional


class StructuredJsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Inject context attributes if set on record
        for attr in [
            "correlation_id",
            "request_id",
            "user_id",
            "conversation_id",
            "agent_id",
            "execution_id",
            "provider",
            "model",
            "latency_ms",
            "token_usage",
            "retrieval_latency_ms",
            "tool_latency_ms",
            "cache_hit",
            "error",
        ]:
            val = getattr(record, attr, None)
            if val is not None:
                log_data[attr] = val

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def setup_structured_logging(level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("manabi")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Avoid adding duplicate handlers if reloaded
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredJsonFormatter())
        logger.addHandler(handler)
        logger.propagate = False
        
    return logger


platform_logger = setup_structured_logging()
