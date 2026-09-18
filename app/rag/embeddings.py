from app.config.settings import settings

class EmbeddingProvider:
    async def embed(self, text: str) -> list[float]:
        if not settings.gemini_api_key:
            return [0.0] * settings.embedding_dimensions
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=settings.gemini_api_key)
        try:
            result = client.models.embed_content(
                model=settings.embedding_model,
                contents=text,
                config=types.EmbedContentConfig(
                    output_dimensionality=settings.embedding_dimensions
                ),
            )
            return list(result.embeddings[0].values)
        except Exception:
            # Keep ingestion/search operational when the configured provider is unavailable.
            # The vector store dimension remains stable and callers can still run keyword paths.
            return [0.0] * settings.embedding_dimensions

async def generate_embedding(text: str) -> list[float]:
    return await EmbeddingProvider().embed(text)
