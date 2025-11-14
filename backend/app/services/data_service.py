"""Data service for generating and managing product data."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

# Add src directory to path to import mock data
workspace_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(workspace_root / "src"))

from agent.internal_data_mock import (
    get_all_product_codes,
    get_internal_data_for_product,
)
from app.utils.data_generator import generate_ev_inverter_data


class DataService:
    """Service for managing product data."""

    @staticmethod
    def get_ev_inverter_data(
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        days: int = 365,
    ) -> Dict[str, Any]:
        """Get EV Inverter data, optionally filtered by date range.

        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
            days: Number of days of historical data to generate

        Returns:
            Dictionary with historical_data, product_info, competitor_data
        """
        data = generate_ev_inverter_data(start_date=start_date, days=days)

        # Filter by date range if provided
        if start_date or end_date:
            df = data["historical_data"]
            if start_date:
                df = df[df["date"] >= pd.to_datetime(start_date)]
            if end_date:
                df = df[df["date"] <= pd.to_datetime(end_date)]
            data["historical_data"] = df

        return data

    @staticmethod
    def get_products() -> list[Dict[str, Any]]:
        """Get list of available products.

        Returns:
            List of product dictionaries
        """
        products = []
        for product_code in get_all_product_codes():
            product_data = get_internal_data_for_product(product_code)
            products.append({
                "product_id": product_code,
                "name": product_data["product_name"],
                "category": product_data["category"],
                "subcategory": product_data["subcategory"],
                "unit_price": product_data["unit_price"],
                "product_lifecycle": product_data["product_lifecycle"],
            })
        return products

    @staticmethod
    def get_product_status(product_code: str) -> Dict[str, Any]:
        """Get current status for a single product.

        Args:
            product_code: Product code (e.g., INV-001)

        Returns:
            Dictionary with product status information
        """
        product_data = get_internal_data_for_product(product_code)

        # Get last 5 months sales
        sales_data = product_data["historical_sales"][-5:]
        recent_sales = [s["quantity"] for s in sales_data]

        # Calculate trends
        if len(recent_sales) >= 2:
            growth = (
                ((recent_sales[-1] - recent_sales[0]) / recent_sales[0]) * 100
                if recent_sales[0] > 0
                else 0
            )
        else:
            growth = 0

        # Get inventory status
        inventory = product_data["inventory_levels"]
        stock_ratio = (
            inventory["current_stock"] / inventory["max_stock"]
            if inventory["max_stock"] > 0
            else 0
        )

        return {
            "product_code": product_code,
            "product_name": product_data["product_name"],
            "category": product_data["category"],
            "unit_price": product_data["unit_price"],
            "product_lifecycle": product_data["product_lifecycle"],
            "current_month_sales": recent_sales[-1] if recent_sales else 0,
            "last_5_months_avg": sum(recent_sales) / len(recent_sales) if recent_sales else 0,
            "growth_rate": round(growth, 2),
            "current_stock": inventory["current_stock"],
            "safety_stock": inventory["safety_stock"],
            "reorder_point": inventory["reorder_point"],
            "stock_status": inventory["stock_status"],
            "stock_ratio": round(stock_ratio * 100, 1),
            "warehouse_location": inventory["warehouse_location"],
            "quality_score": round(product_data["quality_metrics"]["customer_satisfaction"], 1),
            "defect_rate": product_data["quality_metrics"]["defect_rate"],
        }

    @staticmethod
    def get_all_products_status() -> List[Dict[str, Any]]:
        """Get status for all products.

        Returns:
            List of product status dictionaries
        """
        statuses = []
        for product_code in get_all_product_codes():
            statuses.append(DataService.get_product_status(product_code))
        return statuses

