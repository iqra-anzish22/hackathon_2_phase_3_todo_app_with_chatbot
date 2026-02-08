"""
Database configuration and connection management.
Provides async SQLAlchemy engine and session management for PostgreSQL.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlmodel import SQLModel
from .config import settings


# Create async engine for PostgreSQL
# Note: asyncpg handles SSL automatically for Neon, no connect_args needed
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,   # Recycle connections after 1 hour
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    """
    Dependency for getting database sessions.
    Yields an async session and ensures it's closed after use.
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """
    Initialize database by creating all tables.
    Should be called on application startup.
    """
    try:
        # Import all models to ensure they're registered with SQLModel
        from ..models.user import User

        print("[INIT] Initializing database...")
        print(f"[DB] Using PostgreSQL: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'configured'}")

        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(SQLModel.metadata.create_all)

        print("[OK] Database tables created successfully")
        print("   - users table")

    except Exception as e:
        print(f"[ERROR] Database initialization failed: {str(e)}")
        print(f"   Error type: {type(e).__name__}")
        raise


async def close_db():
    """
    Close database connections.
    Should be called on application shutdown.
    """
    try:
        await engine.dispose()
        print("[OK] Database connections closed")
    except Exception as e:
        print(f"[ERROR] Database shutdown error: {str(e)}")
        raise
