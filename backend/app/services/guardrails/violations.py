from app.services.guardrails.types import GuardrailViolationDetail


class GuardrailViolationException(Exception):
    """Base exception for all guardrail violations."""
    def __init__(self, detail: GuardrailViolationDetail):
        super().__init__(detail.message)
        self.detail = detail


class RefundLimitViolation(GuardrailViolationException):
    """Raised when an agent attempts to approve a refund over the threshold."""
    pass


class SensitiveDataViolation(GuardrailViolationException):
    """Raised when there is a mismatch in customer data ownership or cross-session leakage."""
    pass


class InfiniteLoopViolation(GuardrailViolationException):
    """Raised when an agent gets stuck in a loop."""
    pass


class UnauthorizedActionViolation(GuardrailViolationException):
    """Raised when an agent attempts an action it does not have permission for."""
    pass
