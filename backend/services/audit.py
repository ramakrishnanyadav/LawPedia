"""
Structured Audit Logging Service
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("lawpedia.audit")

_AUDIT_LOGS: list[dict[str, Any]] = []


def log_audit_event(event_type: str, user_id: str, tenant_id: str, details: dict[str, Any]) -> dict[str, Any]:
    """
    Records an immutable audit log entry.
    """
    entry = {
        "log_id": f"AUDIT_{len(_AUDIT_LOGS) + 1:06d}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "user_id": user_id,
        "tenant_id": tenant_id,
        "details": details
    }
    _AUDIT_LOGS.append(entry)
    logger.info(f"AUDIT_EVENT: {json.dumps(entry)}")
    return entry


def get_audit_logs(tenant_id: str) -> list[dict[str, Any]]:
    """
    Retrieves audit logs filtered by tenant_id.
    """
    return [log for log in _AUDIT_LOGS if log["tenant_id"] == tenant_id]
