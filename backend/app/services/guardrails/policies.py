import abc
from typing import Any, Dict
from app.services.agent.state import GraphState
from app.core.config import settings
from app.services.guardrails.types import GuardrailViolationDetail
from app.services.guardrails.violations import (
    RefundLimitViolation,
    SensitiveDataViolation,
    InfiniteLoopViolation,
    UnauthorizedActionViolation
)


class BasePolicy(abc.ABC):
    """Base class for all guardrail policies."""
    
    @property
    @abc.abstractmethod
    def name(self) -> str:
        pass

    @abc.abstractmethod
    def evaluate(self, state: GraphState, action_input: Dict[str, Any]) -> None:
        """
        Evaluates the policy against the current state and action.
        Raises a GuardrailViolationException if the policy is violated.
        """
        pass


class RefundApprovalPolicy(BasePolicy):
    name = "RefundApprovalGuardrail"

    def evaluate(self, state: GraphState, action_input: Dict[str, Any]) -> None:
        if action_input.get("action") == "approve_refund":
            amount = action_input.get("amount", 0.0)
            if amount > settings.REFUND_APPROVAL_LIMIT:
                detail = GuardrailViolationDetail(
                    rule_name=self.name,
                    severity="critical",
                    message=f"Refund amount {amount} exceeds approval limit of {settings.REFUND_APPROVAL_LIMIT}.",
                    payload={"requested_amount": amount, "limit": settings.REFUND_APPROVAL_LIMIT}
                )
                raise RefundLimitViolation(detail)


class SensitiveDataPolicy(BasePolicy):
    name = "SensitiveDataProtectionGuardrail"

    def evaluate(self, state: GraphState, action_input: Dict[str, Any]) -> None:
        # Check if the agent is trying to access data for a different customer
        requested_customer_id = action_input.get("customer_id")
        current_customer_id = state.get("customer_id")
        
        if requested_customer_id and current_customer_id and str(requested_customer_id) != str(current_customer_id):
            detail = GuardrailViolationDetail(
                rule_name=self.name,
                severity="critical",
                message="Cross-session data access attempted. Customer ID mismatch.",
                payload={"requested_customer": requested_customer_id, "session_customer": current_customer_id}
            )
            raise SensitiveDataViolation(detail)


class InfiniteLoopPolicy(BasePolicy):
    name = "InfiniteAgentLoopPrevention"

    def evaluate(self, state: GraphState, action_input: Dict[str, Any]) -> None:
        # Validate hop limit
        timeline = state.get("timeline", [])
        agent_steps = [t for t in timeline if t.get("agent") not in ("orchestrator", "synthesizer")]
        
        if len(agent_steps) >= settings.MAX_AGENT_HOPS:
            detail = GuardrailViolationDetail(
                rule_name=self.name,
                severity="warning",
                message=f"Agent hop limit ({settings.MAX_AGENT_HOPS}) exceeded. Forcing escalation.",
                payload={"total_hops": len(agent_steps)}
            )
            raise InfiniteLoopViolation(detail)

        # Detect repeated routing (e.g., faq -> refund -> faq -> refund)
        if len(agent_steps) >= 4:
            recent_agents = [t.get("agent") for t in agent_steps[-4:]]
            if recent_agents[0] == recent_agents[2] and recent_agents[1] == recent_agents[3]:
                 detail = GuardrailViolationDetail(
                    rule_name=self.name,
                    severity="warning",
                    message="Circular routing detected.",
                    payload={"recent_path": recent_agents}
                )
                 raise InfiniteLoopViolation(detail)


class UnauthorizedActionPolicy(BasePolicy):
    name = "UnauthorizedActionGuardrail"

    def evaluate(self, state: GraphState, action_input: Dict[str, Any]) -> None:
        # Example: agents cannot override escalation once set
        if action_input.get("action") == "cancel_escalation":
            detail = GuardrailViolationDetail(
                rule_name=self.name,
                severity="critical",
                message="Agent attempted to override an escalation.",
                payload={"action": "cancel_escalation"}
            )
            raise UnauthorizedActionViolation(detail)
