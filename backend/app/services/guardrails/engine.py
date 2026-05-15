import logging
from typing import Any, Dict, List
from app.services.agent.state import GraphState
from app.services.guardrails.policies import (
    BasePolicy,
    RefundApprovalPolicy,
    SensitiveDataPolicy,
    InfiniteLoopPolicy,
    UnauthorizedActionPolicy
)
from app.services.guardrails.violations import GuardrailViolationException
from app.database.session import SessionLocal
from app.services.monitoring.event_logger import log_guardrail_event

logger = logging.getLogger(__name__)

class GuardrailEngine:
    """
    Central engine to evaluate guardrail policies.
    """
    def __init__(self):
        self.policies: List[BasePolicy] = [
            RefundApprovalPolicy(),
            SensitiveDataPolicy(),
            InfiniteLoopPolicy(),
            UnauthorizedActionPolicy()
        ]

    def evaluate_all(self, state: GraphState, action_input: Dict[str, Any]) -> None:
        """
        Runs all registered policies against the current state and action.
        Raises the specific GuardrailViolationException if a policy fails.
        """
        for policy in self.policies:
            try:
                policy.evaluate(state, action_input)
            except GuardrailViolationException as e:
                logger.warning(f"[Guardrail] Policy {policy.name} violated: {e.detail.message}")
                self._record_violation(state, e)
                raise e

    def _record_violation(self, state: GraphState, exception: GuardrailViolationException):
        """Records the violation using the event logger."""
        try:
            # Save the event to Postgres asynchronously or in a separate session
            with SessionLocal() as db:
                log_guardrail_event(
                    db=db,
                    session_id=state.get("session_id", "unknown"),
                    rule_name=exception.detail.rule_name,
                    triggered=True,
                    severity=exception.detail.severity,
                    payload=exception.detail.payload,
                    action_taken="blocked_or_escalated"
                )
        except Exception as e:
            logger.error(f"Failed to record guardrail violation: {str(e)}")

# Singleton instance
guardrail_engine = GuardrailEngine()
