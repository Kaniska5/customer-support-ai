# Monitoring & Observability

## Overview
The monitoring layer ensures full traceability of agent decisions, tool invocations, guardrail triggers, and escalations.

## Components

### Event Logger
- Stores persistent logs into PostgreSQL (`AgentLog`, `GuardrailEvent`, `EscalationLog`).
- Records latency, token usage, LLM models used, and confidence scores.

### Redis Pub/Sub (Live Monitor)
- The `Monitor` class (`backend/app/services/monitoring/monitor.py`) publishes real-time events to Redis channels.
- Channels: `agent_events`, `guardrail_events`, `escalation_events`.

### LangSmith Integration
- The platform fully integrates with LangSmith.
- Enable by setting `LANGCHAIN_TRACING_V2=true` in the configuration.
- Allows tracing complex agent graphs, debugging token usage, and observing nested tool calls.

## API Integration
The `/analytics/live-events` endpoint provides Server-Sent Events (SSE) subscriptions to the frontend, streaming data directly from Redis Pub/Sub.
