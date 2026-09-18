import asyncio
from google.genai import errors

async def with_retries(operation, max_retries=3):
    for attempt in range(max_retries):
        try: return await operation()
        except (errors.ServerError, TimeoutError, ConnectionError):
            if attempt == max_retries - 1: raise
            await asyncio.sleep(2 ** attempt)
