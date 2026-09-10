import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import text
from app.database.connection import engine


async def main():
    async with engine.begin() as conn:
        await conn.execute(
            text(
                """
                DROP TABLE IF EXISTS
                    messages,
                    sessions,
                    memories,
                    document_chunks,
                    documents,
                    users
                CASCADE;
                """
            )
        )

    await engine.dispose()


asyncio.run(main())