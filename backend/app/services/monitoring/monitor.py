import json
import logging
from typing import Any, Dict, Optional
import redis
from app.core.config import settings

logger = logging.getLogger(__name__)

class Monitor:
    """
    Main monitoring class tying events, metrics, and alerts together.
    Publishes real-time events to Redis Pub/Sub for the Observability API.
    """
    def __init__(self):
        self.redis_client = None
        try:
            if settings.REDIS_URL:
                self.redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
        except Exception as e:
            logger.error(f"Failed to connect to Redis for monitoring: {e}")

    def publish_event(self, channel: str, event_type: str, payload: Dict[str, Any]):
        """Publishes an event to a Redis channel."""
        if not self.redis_client:
            return

        message = {
            "type": event_type,
            "data": payload
        }
        try:
            self.redis_client.publish(channel, json.dumps(message))
        except Exception as e:
            logger.error(f"Redis publish failed: {e}")

    def track_agent_step(self, session_id: str, agent_name: str, action: str, details: Dict[str, Any]):
        """Tracks an agent step and broadcasts it."""
        payload = {
            "session_id": session_id,
            "agent_name": agent_name,
            "action": action,
            "details": details
        }
        self.publish_event("agent_events", "agent_step", payload)

    def track_guardrail_violation(self, session_id: str, rule_name: str, details: Dict[str, Any]):
        """Tracks a guardrail violation and broadcasts it."""
        payload = {
            "session_id": session_id,
            "rule_name": rule_name,
            "details": details
        }
        self.publish_event("guardrail_events", "violation", payload)

    def track_escalation(self, session_id: str, reason: str, details: Dict[str, Any]):
        """Tracks an escalation event."""
        payload = {
            "session_id": session_id,
            "reason": reason,
            "details": details
        }
        self.publish_event("escalation_events", "escalation", payload)

monitor = Monitor()
