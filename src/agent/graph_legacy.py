"""AI Demand Forecasting Graph - Legacy version (kept for reference).

This is the original graph implementation with comprehensive forecasting features.
Kept in a separate file for future reference.
"""

from __future__ import annotations

import random
from datetime import datetime
from typing import Any, Dict

import pandas as pd
from langgraph.graph import StateGraph
from langgraph.runtime import Runtime

from agent.competitor_analysis import adjust_forecast_for_competitors, analyze_competitor_impact
from agent.data_integration import (
    cleanse_data,
    generate_mock_competitor_data,
    generate_mock_product_info,
    generate_mock_sales_data,
    validate_data,
)
from agent.new_product_forecast import forecast_new_product
from agent.pattern_recognition import analyze_patterns
from agent.promotional_analysis import analyze_promotional_impact, predict_promotional_demand
from agent.realtime_adjustment import adjust_forecast_realtime
from agent.scenario_planning import generate_scenarios
from agent.seasonal_forecast import forecast_seasonal_demand
from agent.supply_chain import optimize_supply_chain
from agent.types import Context, State


async def load_and_cleanse_data(
    state: State,
    runtime: Runtime[Context],
) -> Dict[str, Any]:
    """Load and cleanse historical data.

    If no data provided, generates mock data for proof of concept.
    """
    # If data already provided, just cleanse it
    if state.historical_data is not None:
        df_clean = cleanse_data(state.historical_data)
        validation = validate_data(df_clean)

        # Generate product info if not provided
        if state.product_info is None and len(df_clean) > 0:
            product_ids = df_clean["product_id"].unique().tolist()
            state.product_info = generate_mock_product_info(product_ids)

        return {
            "historical_data": df_clean,
            "product_info": state.product_info,
        }

    # Generate mock data for proof of concept
    product_id = runtime.context.get("product_id", "PROD001") if runtime.context else "PROD001"
    if state.product_id:
        product_id = state.product_id

    start_date = datetime.now() - pd.Timedelta(days=365)
    promotional_dates = [
        start_date + pd.Timedelta(days=i)
        for i in range(0, 365, 30)
        if random.random() < 0.3  # 30% chance of promotion on these days
    ]
    df = generate_mock_sales_data(
        product_id=product_id,
        start_date=start_date,
        days=365,
        base_demand=100.0,
        seasonal_amplitude=20.0,
        trend=0.1,
        promotional_days=promotional_dates,
    )

    df_clean = cleanse_data(df)
    product_info = generate_mock_product_info([product_id])

    # Generate competitor data
    competitor_data = generate_mock_competitor_data(
        product_id=product_id,
        start_date=start_date,
        days=365,
    )

    return {
        "historical_data": df_clean,
        "product_info": product_info,
        "competitor_data": competitor_data,
        "product_id": product_id,
    }


def route_forecast_mode(state: State) -> str:
    """Route to appropriate forecast workflow based on mode."""
    mode = state.forecast_mode

    if mode == "new_product" and state.new_product_id:
        return "new_product_forecast"
    elif mode == "promotional":
        return "promotional_analysis"
    elif mode == "seasonal":
        return "seasonal_forecast"
    else:
        return "seasonal_forecast"  # Comprehensive mode starts with seasonal


# Legacy graph - kept for reference
graph_legacy = (
    StateGraph(State, context_schema=Context)
    # Data loading and cleansing
    .add_node("load_data", load_and_cleanse_data)
    # Pattern recognition (always run first for comprehensive analysis)
    .add_node("pattern_recognition", analyze_patterns)
    # Seasonal forecasting
    .add_node("seasonal_forecast", forecast_seasonal_demand)
    # New product forecasting
    .add_node("new_product_forecast", forecast_new_product)
    # Promotional analysis
    .add_node("promotional_analysis", analyze_promotional_impact)
    .add_node("promotional_demand", predict_promotional_demand)
    # Competitor analysis
    .add_node("competitor_analysis", analyze_competitor_impact)
    .add_node("competitor_adjustment", adjust_forecast_for_competitors)
    # Supply chain optimization
    .add_node("supply_chain", optimize_supply_chain)
    # Scenario planning
    .add_node("scenario_planning", generate_scenarios)
    # Real-time adjustment
    .add_node("realtime_adjustment", adjust_forecast_realtime)
    # Edges - comprehensive workflow
    .add_edge("__start__", "load_data")
    .add_edge("load_data", "pattern_recognition")
    .add_conditional_edges(
        "pattern_recognition",
        route_forecast_mode,
        {
            "new_product_forecast": "new_product_forecast",
            "promotional_analysis": "promotional_analysis",
            "seasonal_forecast": "seasonal_forecast",
        },
    )
    # Seasonal forecast path (comprehensive mode)
    .add_edge("seasonal_forecast", "promotional_analysis")
    .add_edge("promotional_analysis", "promotional_demand")
    .add_edge("promotional_demand", "competitor_analysis")
    .add_edge("competitor_analysis", "competitor_adjustment")
    .add_edge("competitor_adjustment", "supply_chain")
    .add_edge("supply_chain", "scenario_planning")
    .add_edge("scenario_planning", "realtime_adjustment")
    # New product path
    .add_edge("new_product_forecast", "supply_chain")
    # Final compilation
    .compile(name="AI Demand Forecasting (Legacy)")
)

