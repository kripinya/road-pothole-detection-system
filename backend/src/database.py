"""Database connection and session management.

Uses SQLAlchemy 2.0 async engine with asyncpg driver.
Each API request gets its own session via dependency injection.
"""

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from src.config import settings

# Create the async engine (connection pool to PostgreSQL)
# echo=True logs every SQL query in development -- turn off in production
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=5,
    max_overflow=10,
)

# Session factory -- creates new database sessions
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for all ORM models.

    Every model you create will inherit from this class.
    SQLAlchemy uses it to track all your tables and generate
    CREATE TABLE statements.
    """
    pass


async def get_db():
    """FastAPI dependency that provides a database session.

    Usage in a route:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...

    The session is automatically closed after the request completes,
    even if an error occurs (that's what the finally block does).
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
