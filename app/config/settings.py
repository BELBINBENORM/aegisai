from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = 'AegisAI'
    environment: str = 'development'
    database_url: str = 'postgresql://postgres:postgres@db:5432/aegisai'
    database_echo: bool = False
    api_key: str = 'dev-api-key'
    mcp_api_key: str = 'dev-mcp-key'
    gemini_api_key: str = ''
    model_name: str = 'gemini-2.5-flash'
    embedding_model: str = 'gemini-embedding-001'
    embedding_dimensions: int = 768
    upstash_redis_rest_url: str | None = None
    upstash_redis_rest_token: str | None = None
    object_storage_dir: str = './storage'
    max_upload_bytes: int = 20 * 1024 * 1024
    max_agent_steps: int = 6
    max_clarifications: int = 3
    max_tool_calls: int = 10
    max_agent_seconds: int = 90
    cache_ttl_seconds: int = 300
    gemini_input_price: float = 0.0
    gemini_output_price: float = 0.0
    web_search_url: str | None = None
    web_search_api_key: str | None = None
    web_search_timeout_seconds: float = 30.0
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    @property
    def async_database_url(self) -> str:
        value = self.database_url
        if value.startswith('postgresql+asyncpg://'):
            return value
        return value.replace('postgresql://', 'postgresql+asyncpg://', 1).split('?')[0]

settings = Settings()
