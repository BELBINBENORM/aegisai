# AegisAI

Production-oriented AI platform with a centralized Main Agent, Advanced RAG, MCP, agent memory, planning, verification, security, evaluation, observability, and streaming.

## Live Deployment

- **API:** https://aegisai-x721.onrender.com
- **GitHub:** https://github.com/BELBINBENORM/aegisai

## Architecture

AegisAI uses a **Main Agent as the central orchestrator**. It coordinates reasoning, memory, retrieval, tools, clarification, and response generation.

```text
                         ┌─────────────────────┐
                         │       Client        │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   Render - API      │
                         │      FastAPI        │
                         └──────────┬──────────┘
                                    │
                         ┌──────────▼──────────┐
                         │     Main Agent      │
                         │   Orchestration     │
                         └──────┬────┬─────┬───┘
                                │    │     │
              ┌─────────────────┘    │     └──────────────────┐
              ▼                      ▼                        ▼
       ┌─────────────┐       ┌─────────────┐          ┌─────────────┐
       │ MCP Tools   │       │    Neon     │          │   Gemini    │
       │ Retrieval   │       │ PostgreSQL  │          │ LLM + Embed │
       │ Memory      │       │ + pgvector  │          └─────────────┘
       │ Web Search  │       └─────────────┘
       └─────────────┘
              │
              ▼
       ┌─────────────┐
       │   Upstash   │
       │ Queue/Cache │
       └──────┬──────┘
              │
              ▼
       ┌─────────────┐
       │    Voroa    │
       │   Worker    │
       │ Background  │
       │ Processing  │
       └─────────────┘
```

## Production Infrastructure

| Component | Responsibility |
|---|---|
| **Render** | API RAM/CPU and FastAPI service |
| **Voroa** | Background worker RAM/CPU |
| **Upstash Redis** | Queue, cache, and distributed infrastructure |
| **Neon PostgreSQL** | Persistent application data and pgvector |
| **Gemini** | LLM generation and embeddings |
| **Tavily Remote MCP** | Web research/search |
| **Local/Object Storage** | Uploaded document files |

## Infrastructure Flow

```text
User
  │
  ▼
Render API
  │
  ├──► Neon PostgreSQL
  │       ├── Users
  │       ├── Sessions
  │       ├── Messages
  │       ├── Documents
  │       ├── Chunks
  │       ├── Memories
  │       └── Jobs
  │
  ├──► Upstash Redis
  │       ├── Cache
  │       └── Job Queue
  │
  └──► Main Agent
          ├──► Gemini
          ├──► MCP tools
          └──► Web research

Document Upload
  │
  ▼
Render API
  │
  ├──► Store document
  ├──► Create Job in Neon
  └──► Push Job to Upstash
             │
             ▼
        Voroa Worker
             │
             ▼
        PDF/Text extraction
             │
             ▼
        Chunking
             │
             ▼
        Embeddings
             │
             ▼
        Neon + pgvector
```

## Main Agent

The Main Agent is responsible for coordinating the application's AI workflow.

```text
User Request
     │
     ▼
Main Agent
     │
     ├── Understand request
     ├── Load relevant memory/context
     ├── Decide whether tools are required
     ├── Retrieve information
     ├── Ask clarification when required
     ├── Perform bounded tool calls
     ├── Verify/organize information
     └── Generate final response
```

## MCP Tools

The MCP boundary exposes controlled tools to the agent:

- `hybrid_search`
- `get_chat_history`
- `get_memories`
- `search_web`

MCP provides a controlled interface between agent reasoning and external/application capabilities.

## Document Processing

Document ingestion is handled asynchronously.

```text
Upload
  │
  ▼
Create Document
  │
  ▼
Create Job
  │
  ▼
Upstash Queue
  │
  ▼
Voroa Worker
  │
  ├── Extract text
  ├── Split into chunks
  ├── Generate embeddings
  └── Store chunks/vectors
```

This keeps heavy document processing away from the API compute.

## RAG

The RAG pipeline uses PostgreSQL with pgvector.

```text
User Query
    │
    ▼
Embedding
    │
    ▼
Hybrid Search
    │
    ├── Semantic/vector retrieval
    ├── Keyword/context retrieval
    └── Relevant document chunks
              │
              ▼
          Main Agent
              │
              ▼
          Final Answer
```

## Memory

The system supports agent memory and stored conversational context.

Memory-related information is persisted in Neon and exposed to the Main Agent through controlled application/MCP interfaces.

## Clarification

Clarification is used when the agent does not have enough information to safely or accurately proceed.

```text
User Request
     │
     ▼
Main Agent
     │
     ├── Enough information ─────► Continue
     │
     └── Missing information
                │
                ▼
          Ask Clarification
                │
                ▼
          User Response
                │
                ▼
          Continue Agent Flow
```

The architecture uses clarification rather than the previous human-in-the-loop approval concept.

## Job System

Jobs handle asynchronous work such as document ingestion.

The API creates the job and places it into Upstash. The Voroa worker consumes the queue and performs the heavy processing.

```text
API
 │
 ├── Create Job → Neon
 │
 └── Enqueue → Upstash
                    │
                    ▼
                 Worker
                    │
                    ▼
              Process Job
                    │
                    ▼
               Update Neon
```

## Cache

Upstash Redis is used for cache infrastructure through the official async Redis client.

If Upstash is not configured or unavailable, the application can continue without the Redis client being available.

## Database

Neon PostgreSQL is the persistent database.

The database includes application entities such as:

- Users
- Sessions
- Messages
- Documents
- Chunks
- Memories
- Jobs
- Other application state defined by the schema

Vector data is stored using PostgreSQL/pgvector.

## API

The API is implemented with FastAPI.

Main areas include:

- Authentication/API protection
- Sessions
- Chat
- Documents
- MCP
- Health checks
- Agent-related compatibility endpoints

The primary chat flow is exposed through the session-based API.

## Security

The project includes application-level controls around:

- API authentication
- MCP authentication
- Resource ownership
- Upload validation
- File size limits
- Agent step limits
- Tool-call limits
- Clarification limits
- Agent execution time limits

## Configuration

Important environment variables:

```env
APP_NAME=AegisAI
ENVIRONMENT=development

DATABASE_URL=

API_KEY=
MCP_API_KEY=

GEMINI_API_KEY=
MODEL_NAME=gemini-2.5-flash

EMBEDDING_MODEL=gemini-embedding-001
EMBEDDING_DIMENSIONS=768

UPSTASH_REDIS_REST_URL=
UPSTASH_REDIS_REST_TOKEN=

OBJECT_STORAGE_DIR=./storage

MAX_UPLOAD_BYTES=20971520
MAX_AGENT_STEPS=6
MAX_CLARIFICATIONS=3
MAX_TOOL_CALLS=10
MAX_AGENT_SECONDS=90

WEB_SEARCH_URL=https://mcp.tavily.com/mcp/
WEB_SEARCH_API_KEY=
WEB_SEARCH_TIMEOUT_SECONDS=30
```

## Local Development

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the API:

```bash
uvicorn app.main:app --reload
```

Run the worker:

```bash
python -m worker.worker
```

## Docker

The project provides Docker support for both API and worker.

```text
docker-compose
     │
     ├── API container
     │
     └── Worker container
```

Production persistence remains external:

```text
Docker API/Worker
      │
      ├──► Neon
      └──► Upstash
```

Local document storage is mounted as a persistent Docker volume.

## CI

GitHub Actions runs tests against isolated CI services.

```text
GitHub Actions
      │
      ├── Temporary PostgreSQL + pgvector
      ├── Temporary Redis
      ├── Alembic migrations
      ├── Compile checks
      └── Pytest
```

The CI database is temporary and **is not the production Neon database**.

The Gemini API key is provided through the GitHub Actions secret:

```text
GEMINI_API_KEY
```

The CI workflow enables the pgvector extension before running Alembic migrations.

## Deployment

### Render

Render hosts the FastAPI API.

```text
Root Directory: blank
Dockerfile Path: ./Dockerfile
Health Check: /health
```

### Voroa

Voroa hosts the background worker.

```text
Worker: aegisai-worker
Repository: BELBINBENORM/aegisai
Branch: main
Start command: python -m worker.worker
```

The worker connects to the same Neon and Upstash infrastructure used by the API.

## Responsibility Split

| Layer | Responsibility |
|---|---|
| Client | User interaction |
| Render | API compute |
| Main Agent | Reasoning and orchestration |
| MCP | Controlled tool boundary |
| Gemini | Generation and embeddings |
| Neon | Persistent relational/vector data |
| Upstash | Queue and cache |
| Voroa | Background processing |
| Storage | Uploaded document files |

