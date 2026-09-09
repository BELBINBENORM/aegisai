from google import genai

from app.config.settings import settings


client = genai.Client(api_key=settings.gemini_api_key)


async def generate_embedding(text: str):
    response = await client.aio.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config={
            "output_dimensionality": 768,
        },
    )

    return response.embeddings[0].values