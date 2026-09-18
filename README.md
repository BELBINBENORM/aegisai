# AegisAI

AegisAI is a single-agent, tool-using study AI platform following the locked architecture in `AegisAI_Final_Architecture_and_Implementation_Plan.txt`.

## Architecture
FastAPI -> Main Agent -> MCP -> RAG / Memory / Web -> Verification -> Final Answer.

PostgreSQL + pgvector stores durable application, document and vector data. Managed Upstash Redis provides cache, distributed rate limiting and the durable ingestion queue. A separate worker performs document extraction, chunking, embedding and indexing. Uploaded binaries use a storage abstraction with local filesystem for development.

## Run locally
1. Copy `.env.example` to `.env`.
2. Start `docker compose up --build`.
3. Run migrations with `alembic upgrade head`.
4. Open `http://localhost:8000/docs` and send `X-API-Key: dev-api-key`.

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
