from pydantic_settings import BaseSettings , SettingsConfigDict

class Settings(BaseSettings):

    app_name: str = "AegisAI"
    environment: str = "development"
    
    database_url: str

    gemini_api_key: str




    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra='ignore',
        )
    @property
    def async_database_url(self) -> str:
        return (
            self.database_url
            .replace("postgresql://", "postgresql+asyncpg://")
            .split("?")[0]
        )
        
settings = Settings()