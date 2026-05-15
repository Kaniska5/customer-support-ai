# Success Metrics (KPI Engine)

## Overview
The KPI Engine (`backend/app/services/analytics/kpi_engine.py`) continuously aggregates system performance to measure the success of the Agentic AI rollout.

## Tracked Metrics

1. **Auto Resolution Rate**: Percentage of customer inquiries resolved entirely by the AI without human intervention.
2. **Escalation Rate**: Percentage of sessions that required human escalation.
3. **Guardrail Violation Rate**: Frequency at which safety policies intercept agent actions.
4. **Average Response Time**: End-to-end latency of the LLM and LangGraph pipeline.

## Extensibility
Future metrics can be added directly to the `KPIEngine` class and exposed via the `/analytics/overview` API.
