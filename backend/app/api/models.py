"""Pydantic models for API requests and responses."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal

from pydantic import BaseModel, Field


class ForecastRequest(BaseModel):
    """Request model for forecast endpoint."""

    product_id: str = Field(..., description="Product identifier")
    forecast_mode: Literal["seasonal", "new_product", "promotional", "comprehensive"] = Field(
        default="comprehensive",
        description="Forecast mode",
    )
    forecast_horizon_days: int = Field(default=30, ge=7, le=90, description="Forecast horizon in days")
    start_date: datetime | None = Field(None, description="Start date for historical data")
    end_date: datetime | None = Field(None, description="End date for historical data")


class ProductInfo(BaseModel):
    """Product information model."""

    product_id: str
    name: str
    category: str


class HistoricalDataPoint(BaseModel):
    """Historical data point model."""

    date: str
    product_id: str
    sales: float
    price: float
    promotion: int


class ForecastResponse(BaseModel):
    """Response model for forecast endpoint."""

    product_id: str
    forecast_mode: str
    forecast_horizon_days: int
    historical_data: List[HistoricalDataPoint] | None = None
    pattern_analysis: Dict[str, Any] | None = None
    seasonal_forecast: Dict[str, Any] | None = None
    new_product_forecast: Dict[str, Any] | None = None
    promotional_analysis: Dict[str, Any] | None = None
    promotional_demand: Dict[str, Any] | None = None
    competitor_analysis: Dict[str, Any] | None = None
    competitor_adjusted_forecast: Dict[str, Any] | None = None
    supply_chain_optimization: Dict[str, Any] | None = None
    scenario_planning: Dict[str, Any] | None = None
    realtime_adjustment: Dict[str, Any] | None = None


class HistoricalDataResponse(BaseModel):
    """Response model for historical data endpoint."""

    product_id: str
    data: List[HistoricalDataPoint]
    total_records: int


class SupplyChainMetrics(BaseModel):
    """Supply chain metrics model."""

    product_id: str
    metrics: Dict[str, Any]


class ScenarioData(BaseModel):
    """Scenario planning data model."""

    product_id: str
    scenarios: Dict[str, Any]


class ProductStatus(BaseModel):
    """Product status model."""

    product_code: str
    product_name: str
    category: str
    unit_price: float
    product_lifecycle: str
    current_month_sales: int
    last_5_months_avg: float
    growth_rate: float
    current_stock: int
    safety_stock: int
    reorder_point: int
    stock_status: str
    stock_ratio: float
    warehouse_location: str
    quality_score: float
    defect_rate: float
