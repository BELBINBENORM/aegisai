# AegisAI

AegisAI is a single-agent, tool-using study AI platform following the locked architecture in `AegisAI_Final_Architecture_and_Implementation_Plan.txt`.

## Architecture
FastAPI -> Main Agent -> MCP -> RAG / Memory / Web -> Verification -> Final Answer.

PostgreSQL + pgvector stores durable application, document and vector data. Production uses managed Neon PostgreSQL with pgvector and managed Upstash Redis for cache, distributed rate limiting and the durable ingestion queue. Render hosts the API and worker containers.

The Docker image contains only the AegisAI application. It does **not** include PostgreSQL or pgvector. pgvector remains enabled in the Neon database and the Python `pgvector` package is still required by the application.

Uploaded binaries use a storage abstraction with local filesystem for development.

## Docker / Render

Build the application image:

```bash
docker build -t aegisai .
```

Run it by supplying the same environment variables used by the deployed application, including the Neon `DATABASE_URL` and Upstash Redis REST credentials:

```bash
docker run --env-file .env -p 8000:8000 aegisai
```

For production, use the same image for the API service and the worker service, with the worker command:

```bash
python -m worker.worker
```

Do not start a PostgreSQL/pgvector container for the production architecture; Neon provides PostgreSQL + pgvector.

## Run locally without Docker

1. Copy `.env.example` to `.env`.
2. Install dependencies with `pip install -r requirements.txt`.
3. Run migrations with `alembic upgrade head`.
4. Start the API with `uvicorn app.main:app --reload`.
5. Open `http://localhost:8000/docs` and send `X-API-Key: dev-api-key`.

## Core endpoints
- `POST /sessions`
- `GET /sessions`
- `POST /sessions/{session_id}/documents`
- `GET /sessions/{session_id}/documents`
- `GET /sessions/{session_id}/documents/{document_id}`
- `DELETE /sessions/{session_id}/documents/{document_id}`
- `POST /sessions/{session_id}/chat`
- `POST /sessions/{session_id}/chat/stream`
- `GET /jobs/{job_id}`
- `GET /mcp/tools`
- `POST /mcp/tools/{name}`
- `GET /health`

## Important implementation boundary
The Main Agent never parses/chunks/embeds documents and never accesses PostgreSQL or Redis directly. Those responsibilities stay in application services and MCP tools. The repository intentionally has no supervisor, RAG agent, research agent, tool agent, verification agent, or approval workflow.
