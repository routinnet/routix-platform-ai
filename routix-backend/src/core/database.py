from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData
from src.core.config import settings
import asyncio


# Database engine
if settings.database_url.startswith("sqlite"):
    # For SQLite, use aiosqlite
    database_url = settings.database_url.replace("sqlite://", "sqlite+aiosqlite://")
else:
    # For PostgreSQL, use asyncpg
    database_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(
    database_url,
    echo=True,
    future=True
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for models
class Base(DeclarativeBase):
    metadata = MetaData()


# Dependency to get database session
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Create tables
async def create_tables():
    from src.models import user, conversation, generation, algorithm
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Initialize database
async def init_db():
    await create_tables()
    
    # Create default algorithms
    from src.models.algorithm import Algorithm
    from sqlalchemy import select
    
    async with AsyncSessionLocal() as session:
        # Check if algorithms exist
        result = await session.execute(select(Algorithm))
        existing_algorithms = result.scalars().all()
        
        if not existing_algorithms:
            default_algorithms = [
                Algorithm(
                    id="basic",
                    name="basic",
                    display_name="Basic Generation",
                    description="Fast and cost-effective thumbnail generation",
                    cost_credits=1,
                    is_active=True,
                    parameters={"quality": "standard", "speed": "fast"}
                ),
                Algorithm(
                    id="premium",
                    name="premium", 
                    display_name="Premium Generation",
                    description="High-quality thumbnail generation with advanced AI",
                    cost_credits=3,
                    is_active=True,
                    parameters={"quality": "high", "speed": "medium"}
                ),
                Algorithm(
                    id="pro",
                    name="pro",
                    display_name="Pro Generation",
                    description="Professional-grade thumbnails with maximum quality",
                    cost_credits=5,
                    is_active=True,
                    parameters={"quality": "ultra", "speed": "slow"}
                )
            ]
            
            for algorithm in default_algorithms:
                session.add(algorithm)
            
            await session.commit()
