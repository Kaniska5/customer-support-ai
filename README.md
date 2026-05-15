# Agentic E-commerce Customer Support AI

An enterprise-grade, multi-agent AI system built to automate e-commerce customer support workflows. Powered by LangGraph, FastAPI, and Postgres, this platform orchestrates specialized agents to resolve customer inquiries, process refunds, and track orders with robust safety guardrails.

## Architecture

- **LangGraph Orchestrator**: Manages state, handles intent routing, and prevents infinite loops.
- **Specialized Agents**:
  - `Order Tracking Agent`: Retrieves order status and shipping details.
  - `Refund Agent`: Checks eligibility and recommends refunds.
  - `FAQ Agent`: Answers common questions using RAG (FAISS + HuggingFace).
  - `Escalation Agent`: Hands off complex or sensitive tasks to humans.
- **Guardrails Engine**: A policy-based safety layer enforcing refund thresholds, data privacy, and looping limits.
- **Real-time Monitoring**: Tracks latency, confidence scores, and violations via Redis Pub/Sub and LangSmith.

## Folder Structure

```text
├── backend
│   ├── app
│   │   ├── api          # FastAPI routes & endpoints
│   │   ├── core         # Pydantic settings & config
│   │   ├── database     # SQLAlchemy connection & session
│   │   ├── models       # Database schema
│   │   └── services     # Business logic
│   │       ├── agent    # LangGraph orchestration
│   │       ├── analytics # KPI engine
│   │       ├── guardrails # Policy engine
│   │       └── monitoring # Pub/Sub & event logging
├── frontend             # React UI
└── docs                 # Architecture and design documents
```

## Setup Instructions

### Prerequisites
- Python 3.10+
- PostgreSQL
- Node.js
- Redis (Required for pub/sub monitoring)

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

### Environment Variables
Configure these in `.env`:
- `DATABASE_URL`
- `REDIS_URL`
- `GEMINI_API_KEY` or `OPENAI_API_KEY`
- `LANGCHAIN_TRACING_V2=true`
- `LANGSMITH_API_KEY`

## API Endpoints

- `GET /api/v1/analytics/overview` - KPI dashboard stats
- `GET /api/v1/analytics/live-events` - SSE for real-time monitoring
- `POST /api/v1/chat` - Interaction endpoint for the agentic graph

## Design Decisions
- **Modularity**: Agents and guardrails are decoupled. Policies can be added to the guardrail engine without changing agent logic.
- **Observability First**: All tool calls and decisions are logged persistently and broadcasted via Redis.
- **Fallbacks**: LLM providers seamlessly fail over (Gemini -> OpenAI) using Langchain's `with_fallbacks`.

For more details, see the `docs/` folder.
