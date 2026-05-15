from dataclasses import dataclass, field
from typing import Any, Optional, Dict
from datetime import datetime, timezone


@dataclass
class GuardrailViolationDetail:
    """Details of a triggered guardrail."""
    rule_name: str
    severity: str
    message: str
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

