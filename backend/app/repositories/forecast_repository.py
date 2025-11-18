"""
Forecast Repository - Database layer for forecast operations.
Handles CRUD operations for forecasts, time series, and metrics.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

import asyncpg


class ForecastRepository:
    """Repository for forecast data operations."""

    def __init__(self, pool: asyncpg.Pool):
        """Initialize repository with database connection pool."""
        self.pool = pool

    async def create_forecast(
        self,
        product_id: str,
        product_code: str,
        product_name: str,
        category: str,
        forecast_units: int,
        forecast_horizon: str,
        forecast_start_date: date,
        forecast_end_date: date,
        current_stock: Optional[int] = None,
        trend: Optional[str] = None,
        change_percent: Optional[float] = None,
        confidence: Optional[float] = None,
        langgraph_job_id: Optional[UUID] = None,
        model_type: str = "Prophet + LLM",
        model_metadata: Optional[Dict[str, Any]] = None,
    ) -> UUID:
        """Create a new forecast record."""
        forecast_id = uuid4()

        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO forecasts (
                    id, product_id, product_code, product_name, category,
                    forecast_units, current_stock, trend, change_percent, confidence,
                    forecast_horizon, forecast_start_date, forecast_end_date,
                    langgraph_job_id, model_type, model_metadata
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
                """,
                forecast_id,
                product_id,
                product_code,
                product_name,
                category,
                forecast_units,
                current_stock,
                trend,
                change_percent,
                confidence,
                forecast_horizon,
                forecast_start_date,
                forecast_end_date,
                langgraph_job_id,
                model_type,
                model_metadata,
            )

        return forecast_id

    async def get_latest_forecasts(
        self,
        product_codes: Optional[List[str]] = None,
        category: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get latest forecasts with optional filters."""
        query = """
            SELECT 
                id, product_code, product_code as product_id, product_name, category,
                forecast_units, current_stock, trend, change_percent, confidence,
                forecast_horizon, created_at
            FROM latest_forecasts
            WHERE 1=1
        """
        params = []
        param_count = 1

        if category:
            query += f" AND category = ${param_count}"
            params.append(category)
            param_count += 1

        if product_codes:
            query += f" AND product_code = ANY(${param_count})"
            params.append(product_codes)
            param_count += 1

        query += f" ORDER BY created_at DESC LIMIT ${param_count}"
        params.append(limit)

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            return [dict(row) for row in rows]

    async def get_forecast_by_id(self, forecast_id: UUID) -> Optional[Dict[str, Any]]:
        """Get a single forecast by ID."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT * FROM forecasts WHERE id = $1
                """,
                forecast_id,
            )
            return dict(row) if row else None

    async def save_timeseries(
        self,
        forecast_id: UUID,
        timeseries_data: List[Dict[str, Any]],
    ) -> int:
        """Save time series data for a forecast."""
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                # Delete existing timeseries for this forecast
                await conn.execute(
                    "DELETE FROM forecast_timeseries WHERE forecast_id = $1",
                    forecast_id,
                )

                # Insert new timeseries
                rows = [
                    (
                        uuid4(),
                        forecast_id,
                        point["date"],
                        point.get("actual"),
                        point.get("forecast"),
                        point.get("upper_bound"),
                        point.get("lower_bound"),
                        point.get("is_historical", False),
                    )
                    for point in timeseries_data
                ]

                await conn.executemany(
                    """
                    INSERT INTO forecast_timeseries (
                        id, forecast_id, date, actual, forecast, 
                        upper_bound, lower_bound, is_historical
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    """,
                    rows,
                )

        return len(rows)

    async def get_timeseries(self, forecast_id: UUID) -> List[Dict[str, Any]]:
        """Get time series data for a forecast."""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT 
                    date, actual, forecast, upper_bound, lower_bound, is_historical
                FROM forecast_timeseries
                WHERE forecast_id = $1
                ORDER BY date ASC
                """,
                forecast_id,
            )
            return [dict(row) for row in rows]

    async def save_metrics(
        self,
        forecast_id: UUID,
        mape: Optional[float] = None,
        rmse: Optional[float] = None,
        mae: Optional[float] = None,
        r_squared: Optional[float] = None,
        training_data_points: Optional[int] = None,
        test_data_points: Optional[int] = None,
        last_trained_at: Optional[datetime] = None,
        model_version: Optional[str] = None,
    ) -> UUID:
        """Save forecast metrics."""
        metrics_id = uuid4()

        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO forecast_metrics (
                    id, forecast_id, mape, rmse, mae, r_squared,
                    training_data_points, test_data_points, last_trained_at, model_version
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """,
                metrics_id,
                forecast_id,
                mape,
                rmse,
                mae,
                r_squared,
                training_data_points,
                test_data_points,
                last_trained_at,
                model_version,
            )

        return metrics_id

    async def get_metrics(self, forecast_id: UUID) -> Optional[Dict[str, Any]]:
        """Get metrics for a forecast."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT * FROM forecast_metrics WHERE forecast_id = $1
                ORDER BY created_at DESC LIMIT 1
                """,
                forecast_id,
            )
            return dict(row) if row else None

    async def get_forecasts_by_job(self, job_id: UUID) -> List[Dict[str, Any]]:
        """Get all forecasts generated by a specific LangGraph job."""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM forecasts WHERE langgraph_job_id = $1
                ORDER BY created_at DESC
                """,
                job_id,
            )
            return [dict(row) for row in rows]

    async def get_forecast_aggregates(self) -> Dict[str, Any]:
        """Get aggregated forecast statistics."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT 
                    COUNT(*) as total_forecasts,
                    COUNT(DISTINCT product_code) as total_products,
                    SUM(forecast_units) as total_forecast_units,
                    AVG(confidence) as avg_confidence,
                    MAX(created_at) as latest_forecast_date
                FROM forecasts
                WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
                """
            )
            return dict(row) if row else {}
