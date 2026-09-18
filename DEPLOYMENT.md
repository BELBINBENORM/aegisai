# Deployment

## Render
Deploy the API as a web service and the worker as a background worker using the same image. Set environment variables from `.env.example`.

## Neon
Set `DATABASE_URL` to the Neon PostgreSQL connection string and ensure the `vector` extension is available. Run `alembic upgrade head` during deployment.

## Redis
AegisAI uses managed Upstash Redis through its HTTP-based Python SDK. Set `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN`. Keep these values in environment secrets and never commit them.

## Object storage
The current implementation uses a provider-neutral storage boundary with local filesystem support. For multi-instance production deployment, replace `LocalFileStorage` with an object-storage adapter and keep `storage_key` in PostgreSQL.

## CI/CD
GitHub Actions compiles the code and runs pytest before deployment.


## Tavily Remote MCP

AegisAI uses Tavily's hosted Remote MCP server for web research. Set these environment variables:

```env
WEB_SEARCH_URL=https://mcp.tavily.com/mcp/
WEB_SEARCH_API_KEY=your_tavily_api_key
WEB_SEARCH_TIMEOUT_SECONDS=30
```

The API key is sent as an `Authorization: Bearer` header. Do not commit the key to Git.
