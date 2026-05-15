# Enterprise Guardrails Engine

## Overview
The Guardrails Engine provides a centralized, policy-based safety layer to intercept and prevent unwanted agent actions. It is located in `backend/app/services/guardrails/`.

## Architecture
The engine (`guardrail_engine`) evaluates all registered policies concurrently or sequentially. If a policy fails, a specific `GuardrailViolationException` is raised, triggering an automatic escalation and event log.

### Supported Policies

1. **Refund Approval Limit**
   - **Rule**: Agents cannot approve refunds exceeding the `REFUND_APPROVAL_LIMIT` (e.g., $200).
   - **Action**: Escalates to human agent.

2. **Sensitive Data Protection**
   - **Rule**: Validates cross-session data requests. An agent cannot fetch order details for Customer B while servicing a session for Customer A.
   - **Action**: Blocks action and raises a severe alert.

3. **Infinite Loop Prevention**
   - **Rule**: Analyzes `GraphState.timeline` to detect circular paths or exceeding `MAX_AGENT_HOPS`.
   - **Action**: Forces escalation.

4. **Unauthorized Action Prevention**
   - **Rule**: Prevents agents from altering immutable system states, such as overriding an escalation flag.
   - **Action**: Blocks action.
