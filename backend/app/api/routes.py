"""API routes for demand forecasting dashboard."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api.models import (
    ForecastRequest,
    ForecastResponse,
    HistoricalDataPoint,
    HistoricalDataResponse,
    ProductInfo,
    ProductStatus,
    ScenarioData,
    SupplyChainMetrics,
)
from app.services.data_service import DataService
from app.services.forecast_service import ForecastService

router = APIRouter()


@router.get("/products", response_model=list[ProductInfo])
async def get_products():
    """Get list of available products."""
    products = DataService.get_products()
    return [ProductInfo(**p) for p in products]


@router.get("/historical/{product_id}", response_model=HistoricalDataResponse)
async def get_historical_data(
    product_id: str,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
):
    """Get historical sales data for a product.

    Args:
        product_id: Product identifier
        start_date: Optional start date filter
        end_date: Optional end date filter

    Returns:
        Historical data response
    """
    if product_id != "DENSO_EV_INVERTER":
        raise HTTPException(status_code=404, detail="Product not found")

    data = DataService.get_ev_inverter_data(start_date=start_date, end_date=end_date)

    historical_data = data["historical_data"]
    if historical_data is None or len(historical_data) == 0:
        raise HTTPException(status_code=404, detail="No historical data found")

    # Convert to list of dicts
    historical_data["date"] = historical_data["date"].astype(str)
    data_points = historical_data.to_dict("records")

    return HistoricalDataResponse(
        product_id=product_id,
        data=data_points,
        total_records=len(data_points),
    )


@router.post("/forecast", response_model=ForecastResponse)
async def run_forecast(request: ForecastRequest):
    """Run demand forecasting for a product.

    Args:
        request: Forecast request with parameters

    Returns:
        Complete forecast results
    """
    try:
        # Get data for the product
        data = DataService.get_ev_inverter_data(
            start_date=request.start_date,
            end_date=request.end_date,
        )

        # Run forecast
        result = await ForecastService.run_forecast(
            product_id=request.product_id,
            forecast_mode=request.forecast_mode,
            forecast_horizon_days=request.forecast_horizon_days,
            historical_data=data["historical_data"],
            product_info=data["product_info"],
            competitor_data=data["competitor_data"],
        )

        # Convert historical data to proper format
        historical_data_points = None
        if result.get("historical_data"):
            historical_data_points = [
                HistoricalDataPoint(**item) for item in result["historical_data"]
            ]

        return ForecastResponse(
            product_id=result["product_id"],
            forecast_mode=result["forecast_mode"],
            forecast_horizon_days=result["forecast_horizon_days"],
            historical_data=historical_data_points,
            pattern_analysis=result.get("pattern_analysis"),
            seasonal_forecast=result.get("seasonal_forecast"),
            new_product_forecast=result.get("new_product_forecast"),
            promotional_analysis=result.get("promotional_analysis"),
            promotional_demand=result.get("promotional_demand"),
            competitor_analysis=result.get("competitor_analysis"),
            competitor_adjusted_forecast=result.get("competitor_adjusted_forecast"),
            supply_chain_optimization=result.get("supply_chain_optimization"),
            scenario_planning=result.get("scenario_planning"),
            realtime_adjustment=result.get("realtime_adjustment"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecast failed: {str(e)}")


@router.get("/forecast/{product_id}", response_model=ForecastResponse)
async def get_latest_forecast(
    product_id: str,
    forecast_mode: str = "comprehensive",
    forecast_horizon_days: int = 30,
):
    """Get latest forecast for a product (runs forecast if needed).

    Args:
        product_id: Product identifier
        forecast_mode: Forecast mode
        forecast_horizon_days: Forecast horizon

    Returns:
        Forecast results
    """
    request = ForecastRequest(
        product_id=product_id,
        forecast_mode=forecast_mode,
        forecast_horizon_days=forecast_horizon_days,
    )
    return await run_forecast(request)


@router.get("/supply-chain/{product_id}", response_model=SupplyChainMetrics)
async def get_supply_chain_metrics(product_id: str):
    """Get supply chain optimization metrics for a product.

    Args:
        product_id: Product identifier

    Returns:
        Supply chain metrics
    """
    # Run forecast to get supply chain data
    request = ForecastRequest(product_id=product_id, forecast_mode="comprehensive")
    forecast_result = await run_forecast(request)

    if not forecast_result.supply_chain_optimization:
        raise HTTPException(status_code=404, detail="Supply chain data not available")

    return SupplyChainMetrics(
        product_id=product_id,
        metrics=forecast_result.supply_chain_optimization,
    )


@router.get("/scenarios/{product_id}", response_model=ScenarioData)
async def get_scenarios(product_id: str):
    """Get scenario planning data for a product.

    Args:
        product_id: Product identifier

    Returns:
        Scenario planning data
    """
    # Run forecast to get scenario data
    request = ForecastRequest(product_id=product_id, forecast_mode="comprehensive")
    forecast_result = await run_forecast(request)

    if not forecast_result.scenario_planning:
        raise HTTPException(status_code=404, detail="Scenario data not available")

    return ScenarioData(
        product_id=product_id,
        scenarios=forecast_result.scenario_planning,
    )


@router.get("/products/status", response_model=list[ProductStatus])
async def get_all_products_status():
    """Get status overview for all tracked products.

    Returns:
        List of product status dictionaries with key metrics
    """
    return DataService.get_all_products_status()


@router.get("/products/{product_code}/status", response_model=ProductStatus)
async def get_product_status(product_code: str):
    """Get detailed status for a specific product.

    Args:
        product_code: Product code (e.g., INV-001)

    Returns:
        Product status dictionary
    """
    try:
        return DataService.get_product_status(product_code)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

