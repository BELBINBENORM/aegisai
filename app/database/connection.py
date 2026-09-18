from urllib.parse import urlparse
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from app.config.settings import settings

parsed = urlparse(settings.async_database_url)
connect_args = {'ssl': True} if parsed.hostname not in {'db', 'localhost', '127.0.0.1'} else {}
# AsyncPG connections are bound to the event loop that created them. NullPool avoids
# reusing a connection after pytest-asyncio switches loops between tests.
pool_kwargs = {'poolclass': NullPool} if settings.environment in {'test', 'development'} else {}
engine = create_async_engine(
    settings.async_database_url,
    echo=settings.database_echo,
    pool_pre_ping=True,
    connect_args=connect_args,
    **pool_kwargs,
)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
