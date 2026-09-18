import asyncio
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import text
from app.database.connection import engine


ROOT = Path(__file__).resolve().parents[1]
ALEMBIC_VERSIONS = ROOT / "alembic" / "versions"


async def reset_database():
    print("Resetting database...")

    async with engine.begin() as conn:
        # 1. Remove everything from public schema
        await conn.execute(
            text("DROP SCHEMA IF EXISTS public CASCADE")
        )

        # 2. Recreate public schema
        await conn.execute(
            text("CREATE SCHEMA public")
        )

        # 3. Enable pgvector
        await conn.execute(
            text("CREATE EXTENSION IF NOT EXISTS vector")
        )

    await engine.dispose()

    print("Database reset successfully.")
    print("public schema recreated.")
    print("pgvector extension enabled.")


def reset_alembic_versions():
    print("Removing Alembic migration versions...")

    ALEMBIC_VERSIONS.mkdir(parents=True, exist_ok=True)

    for item in ALEMBIC_VERSIONS.iterdir():
        if item.name == "__pycache__":
            shutil.rmtree(item)
        elif item.is_file():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)

    print("Alembic versions cleaned.")


async def main():
    await reset_database()
    reset_alembic_versions()

    print()
    print("FULL RESET COMPLETE")
    print("Database: fresh")
    print("pgvector: enabled")
    print("Alembic versions: removed")
    print()
    print("Next:")
    print('  alembic revision --autogenerate -m "initial schema"')
    print("  alembic upgrade head")


if __name__ == "__main__":
    asyncio.run(main())