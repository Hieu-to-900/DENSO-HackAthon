"""
Risk Intelligence Repository - Database layer for risk news and keywords.
Handles CRUD operations for external risk data from ChromaDB and keyword extraction.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

import asyncpg


class RiskRepository:
    """Repository for risk intelligence operations."""

    def __init__(self, pool: asyncpg.Pool):
        """Initialize repository with database connection pool."""
        self.pool = pool

    async def create_news(
        self,
        chromadb_id: str,
        title: str,
        summary: str,
        source: str,
        published_at: datetime,
        url: Optional[str] = None,
        risk_score: Optional[float] = None,
        sentiment: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        affected_products: Optional[List[str]] = None,
        related_forecasts: Optional[List[str]] = None,
        embedding_vector: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> UUID:
        """Create a new risk news entry from ChromaDB."""
        news_id = uuid4()

        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO risk_news (
                    id, chromadb_id, title, summary, source, url, published_at,
                    risk_score, sentiment, category, tags, affected_products,
                    related_forecasts, embedding_vector, metadata, last_synced_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, CURRENT_TIMESTAMP)
                """,
                news_id,
                chromadb_id,
                title,
                summary,
                source,
                url,
                published_at,
                risk_score,
                sentiment,
                category,
                tags,
                affected_products,
                related_forecasts,
                embedding_vector,
                metadata,
            )

        return news_id

    async def get_recent_news(
        self,
        days: int = 30,
        risk_threshold: Optional[float] = None,
        category: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Get recent risk news with optional filters."""
        query = """
            SELECT 
                id, title, summary, source, url, published_at,
                risk_score, sentiment, category, tags, affected_products,
                related_forecasts
            FROM recent_risk_news
            WHERE 1=1
        """
        params = []
        param_count = 1

        if risk_threshold is not None:
            query += f" AND risk_score >= ${param_count}"
            params.append(risk_threshold)
            param_count += 1

        if category:
            query += f" AND category = ${param_count}"
            params.append(category)
            param_count += 1

        query += f" LIMIT ${param_count}"
        params.append(limit)

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            return [dict(row) for row in rows]

    async def get_news_by_id(self, news_id: UUID) -> Optional[Dict[str, Any]]:
        """Get a single news entry by ID."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT * FROM risk_news WHERE id = $1
                """,
                news_id,
            )
            return dict(row) if row else None

    async def get_news_by_chromadb_id(
        self, chromadb_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get news by ChromaDB document ID."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT * FROM risk_news WHERE chromadb_id = $1
                """,
                chromadb_id,
            )
            return dict(row) if row else None

    async def update_news_sync(self, news_id: UUID) -> bool:
        """Update last sync timestamp for a news entry."""
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                """
                UPDATE risk_news
                SET last_synced_at = CURRENT_TIMESTAMP
                WHERE id = $1
                """,
                news_id,
            )
            return result == "UPDATE 1"

    async def upsert_news_from_chromadb(
        self, chromadb_documents: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Sync news from ChromaDB - insert new and update existing."""
        created_count = 0
        updated_count = 0

        async with self.pool.acquire() as conn:
            async with conn.transaction():
                for doc in chromadb_documents:
                    chromadb_id = doc["id"]

                    # Check if exists
                    existing = await conn.fetchrow(
                        "SELECT id FROM risk_news WHERE chromadb_id = $1",
                        chromadb_id,
                    )

                    if existing:
                        # Update
                        await conn.execute(
                            """
                            UPDATE risk_news
                            SET 
                                title = $2,
                                summary = $3,
                                risk_score = $4,
                                sentiment = $5,
                                tags = $6,
                                embedding_vector = $7,
                                metadata = $8,
                                last_synced_at = CURRENT_TIMESTAMP
                            WHERE chromadb_id = $1
                            """,
                            chromadb_id,
                            doc.get("title"),
                            doc.get("summary"),
                            doc.get("risk_score"),
                            doc.get("sentiment"),
                            doc.get("tags"),
                            doc.get("embedding"),
                            doc.get("metadata"),
                        )
                        updated_count += 1
                    else:
                        # Insert
                        await conn.execute(
                            """
                            INSERT INTO risk_news (
                                id, chromadb_id, title, summary, source, url, published_at,
                                risk_score, sentiment, category, tags, affected_products,
                                embedding_vector, metadata, last_synced_at
                            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, CURRENT_TIMESTAMP)
                            """,
                            uuid4(),
                            chromadb_id,
                            doc.get("title"),
                            doc.get("summary"),
                            doc.get("source"),
                            doc.get("url"),
                            doc.get("published_at"),
                            doc.get("risk_score"),
                            doc.get("sentiment"),
                            doc.get("category"),
                            doc.get("tags"),
                            doc.get("affected_products"),
                            doc.get("embedding"),
                            doc.get("metadata"),
                        )
                        created_count += 1

        return {"created": created_count, "updated": updated_count}

    async def create_keyword(
        self,
        keyword: str,
        frequency: float,
        sentiment: Optional[str] = None,
        count: int = 1,
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None,
        related_news: Optional[List[str]] = None,
    ) -> UUID:
        """Create a keyword extraction record."""
        keyword_id = uuid4()

        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO risk_keywords (
                    id, keyword, frequency, sentiment, count,
                    period_start, period_end, related_news
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """,
                keyword_id,
                keyword,
                frequency,
                sentiment,
                count,
                period_start,
                period_end,
                related_news,
            )

        return keyword_id

    async def get_top_keywords(
        self,
        limit: int = 50,
        days: int = 30,
        sentiment: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get top keywords from recent period."""
        query = """
            SELECT 
                keyword, 
                SUM(count) as total_count,
                AVG(frequency) as avg_frequency,
                sentiment,
                ARRAY_AGG(DISTINCT related_news) as all_related_news
            FROM risk_keywords
            WHERE created_at >= CURRENT_DATE - $1::interval
        """
        params = [f"{days} days"]
        param_count = 2

        if sentiment:
            query += f" AND sentiment = ${param_count}"
            params.append(sentiment)
            param_count += 1

        query += f"""
            GROUP BY keyword, sentiment
            ORDER BY total_count DESC, avg_frequency DESC
            LIMIT ${param_count}
        """
        params.append(limit)

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            return [dict(row) for row in rows]

    async def bulk_create_keywords(
        self, keywords: List[Dict[str, Any]]
    ) -> List[UUID]:
        """Create multiple keywords in a single transaction."""
        keyword_ids = [uuid4() for _ in keywords]

        async with self.pool.acquire() as conn:
            async with conn.transaction():
                rows = [
                    (
                        keyword_ids[i],
                        kw["keyword"],
                        kw["frequency"],
                        kw.get("sentiment"),
                        kw.get("count", 1),
                        kw.get("period_start"),
                        kw.get("period_end"),
                        kw.get("related_news"),
                    )
                    for i, kw in enumerate(keywords)
                ]

                await conn.executemany(
                    """
                    INSERT INTO risk_keywords (
                        id, keyword, frequency, sentiment, count,
                        period_start, period_end, related_news
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    """,
                    rows,
                )

        return keyword_ids

    async def get_risk_statistics(self) -> Dict[str, Any]:
        """Get risk intelligence statistics."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT 
                    COUNT(*) as total_news,
                    AVG(risk_score) as avg_risk_score,
                    COUNT(*) FILTER (WHERE risk_score >= 0.7) as high_risk_count,
                    COUNT(*) FILTER (WHERE sentiment = 'negative') as negative_count,
                    COUNT(*) FILTER (WHERE sentiment = 'positive') as positive_count,
                    MAX(published_at) as latest_news_date
                FROM risk_news
                WHERE published_at >= CURRENT_DATE - INTERVAL '30 days'
                """
            )
            return dict(row) if row else {}

    async def search_news_by_keyword(
        self, keyword: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Full-text search in news titles and summaries."""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT 
                    id, title, summary, source, published_at, risk_score, sentiment
                FROM risk_news
                WHERE 
                    title ILIKE $1 OR summary ILIKE $1
                ORDER BY published_at DESC
                LIMIT $2
                """,
                f"%{keyword}%",
                limit,
            )
            return [dict(row) for row in rows]
