"""PostgreSQL database connection management."""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import asyncpg
from dotenv import load_dotenv

load_dotenv()

# Database configuration from environment variables
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://denso_user:denso_password_2025@localhost:5432/denso_forecast"
)


class Database:
    """Database connection pool manager."""
    
    def __init__(self):
        self.pool: asyncpg.Pool | None = None
    
    async def connect(self):
        """Create database connection pool."""
        if self.pool is None:
            self.pool = await asyncpg.create_pool(
                DATABASE_URL,
                min_size=2,
                max_size=10,
                command_timeout=60,
                max_queries=50000,
                max_inactive_connection_lifetime=300,
            )
            print("✅ Database connection pool created")
    
    async def disconnect(self):
        """Close database connection pool."""
        if self.pool:
            await self.pool.close()
            self.pool = None
            print("✅ Database connection pool closed")
    
    async def close(self):
        """Alias for disconnect() - close database connection pool."""
        await self.disconnect()
    
    async def fetch_one(self, query: str, *args):
        """Fetch one row."""
        async with self.pool.acquire() as connection:
            return await connection.fetchrow(query, *args)
    
    async def fetch_all(self, query: str, *args):
        """Fetch all rows."""
        async with self.pool.acquire() as connection:
            return await connection.fetch(query, *args)
    
    async def execute(self, query: str, *args):
        """Execute query without return."""
        async with self.pool.acquire() as connection:
            return await connection.execute(query, *args)
    
    @asynccontextmanager
    async def transaction(self):
        """Context manager for database transactions."""
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                yield connection


# Global database instance
db = Database()


async def init_db():
    """Initialize database connection."""
    await db.connect()


async def close_db():
    """Close database connection."""
    await db.disconnect()


async def get_db() -> Database:
    """Dependency for FastAPI routes."""
    return db
