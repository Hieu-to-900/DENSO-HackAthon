"""Forecast API routes for dashboard integration."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.models import ForecastRequest, ForecastResponse
from app.database.connection import Database, get_db
from app.repositories.forecast_repository import ForecastRepository
from app.repositories.action_repository import ActionRepository
from app.repositories.risk_repository import RiskRepository

router = APIRouter()


# ========================================
# PHASE 1: CRITICAL ENDPOINTS FOR DASHBOARD
# ========================================


@router.get("/forecasts/latest")
async def get_latest_forecasts(
    product_codes: str | None = Query(None, description="Comma-separated product codes"),
    category: str | None = Query(None, description="Filter by category"),
    limit: int = Query(10, ge=1, le=100, description="Number of products to return"),
    db: Database = Depends(get_db),
) -> Dict[str, Any]:
    """Get latest forecast data for dashboard Tier 2.
    
    Phase 2: Returns real forecast data from database (saved by Celery task).
    Fallback: Mock data if database is empty.
    
    Returns aggregated forecasts with time series, product breakdown, heatmap, and metrics.
    This is the main endpoint for the Forecast Visualization component.
    
    Args:
        product_codes: Optional filter by specific products (comma-separated)
        category: Optional filter by product category
        limit: Maximum number of products to return
        db: Database connection (injected)
        
    Returns:
        Dictionary containing:
        - timeSeries: Historical + forecast data points
        - productBreakdown: Forecast by product with trends
        - heatmap: Category-month intensity matrix
        - metrics: Model performance metrics
    """
    forecast_repo = ForecastRepository(db.pool)
    
    # Try to get real forecasts from database
    try:
        product_code_list = product_codes.split(",") if product_codes else None
        forecasts = await forecast_repo.get_latest_forecasts(
            product_codes=product_code_list,
            category=category,
            limit=limit,
        )
        
        if forecasts:
            # Build response from database data
            products = []
            all_timeseries = []
            
            for forecast in forecasts:
                # Get timeseries for this forecast
                timeseries = await forecast_repo.get_timeseries(forecast["id"])
                
                # Get metrics for this forecast
                metrics = await forecast_repo.get_metrics(forecast["id"])
                
                # Format timeseries for this product
                product_timeseries = [
                    {
                        "date": ts["date"].isoformat(),
                        "weekLabel": f"T{idx + 1}",
                        "week": f"Tuần {idx + 1}",
                        "actual": ts["actual"],
                        "forecast": ts["forecast"],
                        "upperBound": ts["upper_bound"],
                        "lowerBound": ts["lower_bound"],
                    }
                    for idx, ts in enumerate(timeseries)
                ]
                
                product = {
                    "product_id": str(forecast["id"]),
                    "product_code": forecast["product_code"],
                    "product_name": forecast["product_name"],
                    "name": forecast["product_name"],  # Alias for frontend
                    "category": forecast["category"],
                    "forecast_units": forecast["forecast_units"],
                    "current_stock": forecast["current_stock"],
                    "trend": forecast["trend"],
                    "change_percent": forecast["change_percent"],
                    "confidence": forecast["confidence"],
                    "forecast_horizon": forecast["forecast_horizon"],
                    "accuracy": metrics.get("r_squared") if metrics else None,
                    "timeSeries": product_timeseries,  # Add timeSeries to each product
                }
                products.append(product)
                
                # Collect timeseries for aggregate chart
                all_timeseries.extend([
                    {
                        "date": ts["date"].isoformat(),
                        "actual": ts["actual"],
                        "forecast": ts["forecast"],
                        "upper_bound": ts["upper_bound"],
                        "lower_bound": ts["lower_bound"],
                    }
                    for ts in timeseries
                ])
            
            # Generate heatmap from database data
            heatmap = _generate_heatmap_from_forecasts(forecasts)
            
            # Calculate aggregate metrics
            aggregated_metrics = await forecast_repo.get_forecast_aggregates()
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "total_products": len(products),
                "total_forecast_units": sum(p["forecast_units"] for p in products),
                "timeSeries": all_timeseries[:90],  # Limit to 90 days
                "productBreakdown": products,
                "heatmap": heatmap,
                "metrics": {
                    "avg_confidence": aggregated_metrics.get("avg_confidence"),
                    "total_products": aggregated_metrics.get("total_products"),
                    "latest_update": aggregated_metrics.get("latest_forecast_date"),
                },
                "filters_applied": {
                    "product_codes": product_code_list,
                    "category": category,
                    "limit": limit,
                },
                "data_source": "database",
            }
        
    except Exception as e:
        print(f"⚠️ [API] Database query failed, falling back to mock data: {str(e)}")
    
    # Fallback to mock data (Phase 1 behavior)
    products = _generate_mock_products(limit, category, product_codes)
    
    # Generate aggregate time series (sum of all products)
    time_series = _generate_weekly_timeseries_for_product(
        base_value=2650,  # Aggregate base ~sum of all products
        trend_direction='up',
        seasonal_strength=0.15,
        volatility=0.10,
        growth_rate=0.022
    )
    
    heatmap = _generate_heatmap_data()
    metrics = _calculate_forecast_metrics()
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "total_products": len(products),
        "total_forecast_units": sum(p["forecast_units"] for p in products),
        "timeSeries": time_series,
        "productBreakdown": products,
        "heatmap": heatmap,
        "metrics": metrics,
        "filters_applied": {
            "product_codes": product_codes.split(",") if product_codes else None,
            "category": category,
            "limit": limit,
        },
        "data_source": "mock",
    }


@router.get("/actions/recommendations")
async def get_action_recommendations(
    priority: str | None = Query(None, description="Filter by priority: high/medium/low"),
    category: str | None = Query(None, description="Filter by category"),
    limit: int = Query(6, ge=1, le=20, description="Number of actions to return"),
    db: Database = Depends(get_db),
) -> List[Dict[str, Any]]:
    """Get prioritized action recommendations for dashboard Tier 4.
    
    Phase 2: Returns real actions from database (saved by Celery task).
    Fallback: Mock data if database is empty.
    
    Returns actionable recommendations based on forecast insights and risks.
    This powers the Action Recommendations component.
    
    Args:
        priority: Optional filter by priority level
        category: Optional filter by action category
        limit: Maximum number of actions to return
        db: Database connection (injected)
        
    Returns:
        List of action items with:
        - priority, category, title, description
        - impact, estimated_cost, deadline
        - actionItems (step-by-step tasks)
        - affectedProducts, riskIfIgnored
    """
    action_repo = ActionRepository(db.pool)
    
    # Try to get real actions from database
    try:
        actions = await action_repo.get_active_actions(
            priority=priority,
            category=category,
            limit=limit,
        )
        
        if actions:
            # Format for frontend
            formatted_actions = [
                {
                    "id": str(action["id"]),
                    "priority": action["priority"],
                    "category": action["category"],
                    "title": action["title"],
                    "description": action["description"],
                    "impact": action["impact"],  # Fixed: use 'impact' not 'expected_impact'
                    "estimatedCost": action["estimated_cost"],
                    "deadline": action["deadline"].isoformat() if action["deadline"] else None,
                    "actionItems": action["action_items"] or [],
                    "affectedProducts": action["affected_products"],
                    "status": action["status"],
                }
                for action in actions
            ]
            
            return formatted_actions
        
    except Exception as e:
        print(f"⚠️ [API] Database query failed, falling back to mock data: {str(e)}")
    
    # Fallback to mock data (Phase 1 behavior)
    actions = _generate_mock_actions(limit, priority, category)
    
    return actions


@router.get("/risks/news")
async def get_risk_news(
    days: int = Query(30, ge=1, le=90, description="Number of days to look back"),
    risk_threshold: int = Query(50, ge=0, le=100, description="Minimum risk score"),
    category: str | None = Query(None, description="Filter by risk category"),
    db: Database = Depends(get_db),
) -> Dict[str, Any]:
    """Get risk intelligence and news analysis for dashboard Tier 3.
    
    Phase 2: Returns real news from ChromaDB.
    Fallback: Mock data if ChromaDB query fails.
    
    Returns external market insights, supply chain risks, and competitive intelligence.
    This powers the Risk Intelligence component.
    
    Args:
        days: Number of days of historical risk data
        risk_threshold: Minimum risk score to include
        category: Optional filter by risk category
        db: Database connection (injected)
        
    Returns:
        Dictionary containing:
        - news: List of risk events with scores and impacts
        - timeline: Time series of risk events
        - keywords: Top risk keywords from news
        - distribution: Risk breakdown by category
    """
    from app.services.chromadb_service import chromadb_service
    from app.services.nlp_service import nlp_service
    
    # Try to get real news from ChromaDB
    try:
        # Query ChromaDB for recent news
        chromadb_results = chromadb_service.query_recent_news(
            query_text=None,  # Get all documents, no semantic filtering
            n_results=100,  # Get more documents to filter later
        )
        
        if chromadb_results and len(chromadb_results) > 0:
            # Convert risk_threshold from 0-100 scale to 0-1 scale
            threshold = risk_threshold / 100.0
            
            # Filter and format news
            news_items = []
            for doc in chromadb_results:
                metadata = doc.get("metadata", {})
                risk_score = float(metadata.get("risk_score", 0))
                
                # Apply filters
                if risk_score * 100 < risk_threshold:
                    continue
                    
                if category and metadata.get("category") != category:
                    continue
                
                # Parse date
                article_date = metadata.get("article_date", "")
                if article_date:
                    try:
                        date_obj = datetime.fromisoformat(article_date)
                        days_old = (datetime.now() - date_obj).days
                        if days_old > days:
                            continue
                    except:
                        pass
                
                # Format for frontend
                news_item = {
                    "id": doc.get("id", ""),
                    "title": metadata.get("title", ""),
                    "source": metadata.get("source", ""),
                    "date": article_date,
                    "risk_score": int(risk_score * 100),  # Convert back to 0-100
                    "category": metadata.get("category", ""),
                    "category_name": metadata.get("category", "").replace("_", " ").title(),
                    "sentiment": metadata.get("sentiment", "neutral"),
                    "summary": doc.get("text", "")[:200] + "...",
                    "impact": f"Risk level {int(risk_score * 100)}/100",
                    "tags": metadata.get("tags", "").split(",") if metadata.get("tags") else [],
                    "related_products": metadata.get("related_products", "").split(",") if metadata.get("related_products") else [],
                    "affected_products": metadata.get("related_products", "").split(",") if metadata.get("related_products") else [],
                    "url": metadata.get("url", ""),
                }
                news_items.append(news_item)
            
            # Sort by risk score descending
            news_items.sort(key=lambda x: x["risk_score"], reverse=True)
            
            # Extract keywords from news summaries
            if news_items:
                summaries = [item["summary"] for item in news_items[:10]]
                keywords = nlp_service.summarize_risk_keywords(summaries, top_n=20)
                
                # Format keywords for frontend
                formatted_keywords = [
                    {
                        "keyword": kw["keyword"],
                        "count": kw.get("count", 1),
                        "frequency": kw.get("frequency", 0.5),
                        "sentiment": kw.get("sentiment", "neutral"),
                        "word": kw["keyword"],  # Vietnamese word
                    }
                    for kw in keywords
                ]
            else:
                formatted_keywords = []
            
            # Generate timeline from news dates
            timeline = []
            date_counts = {}
            for item in news_items:
                date = item["date"][:10] if item["date"] else ""
                if date:
                    date_counts[date] = date_counts.get(date, 0) + 1
            
            for date, count in sorted(date_counts.items()):
                timeline.append({
                    "date": date,
                    "count": count,
                    "risk_level": "high" if count > 3 else "medium" if count > 1 else "low"
                })
            
            # Calculate distribution by category
            category_counts = {}
            for item in news_items:
                cat = item["category"]
                category_counts[cat] = category_counts.get(cat, 0) + 1
            
            distribution = [
                {
                    "category": cat,
                    "count": count,
                    "percentage": round(count / len(news_items) * 100, 1) if news_items else 0
                }
                for cat, count in category_counts.items()
            ]
            
            return {
                "news": news_items,
                "timeline": timeline,
                "keywords": formatted_keywords,
                "distribution": distribution,
                "period": {
                    "days": days,
                    "start_date": (datetime.utcnow() - timedelta(days=days)).isoformat(),
                    "end_date": datetime.utcnow().isoformat(),
                },
                "filters_applied": {
                    "risk_threshold": risk_threshold,
                    "category": category,
                },
                "data_source": "chromadb",
                "total_results": len(news_items),
            }
    
    except Exception as e:
        print(f"⚠️ [API] ChromaDB query failed, falling back to mock data: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Fallback to mock data (Phase 1 behavior)
    news_items = _generate_mock_news(days, risk_threshold, category)
    timeline = _generate_risk_timeline(days)
    keywords = _extract_risk_keywords()
    distribution = _calculate_risk_distribution()
    
    return {
        "news": news_items,
        "timeline": timeline,
        "keywords": keywords,
        "distribution": distribution,
        "period": {
            "days": days,
            "start_date": (datetime.utcnow() - timedelta(days=days)).isoformat(),
            "end_date": datetime.utcnow().isoformat(),
        },
        "filters_applied": {
            "risk_threshold": risk_threshold,
            "category": category,
        },
        "data_source": "mock",
    }


# ========================================
# HELPER FUNCTIONS - MOCK DATA GENERATION
# (Will be replaced with real LangGraph/ChromaDB integration)
# ========================================


def _generate_mock_products(limit: int, category: str | None, product_codes: str | None) -> List[Dict[str, Any]]:
    """Generate mock product forecast data with individual time series."""
    all_products = [
        {
            "product_id": "BUGI-IRIDIUM-VCH20",
            "product_code": "VCH20",
            "product_name": "Bugi Iridium Tough VCH20",
            "category": "Spark_Plugs",
            "forecast_units": 25000,
            "current_stock": 18500,
            "trend": "up",
            "change_percent": 12.5,
            "confidence": 94.2,
            "forecast_horizon": "60_days",
            "last_updated": datetime.utcnow().isoformat(),
            "timeSeries": _generate_weekly_timeseries_for_product(
                base_value=750,
                trend_direction='up',
                seasonal_strength=0.12,
                volatility=0.08,
                growth_rate=0.025
            )
        },
        {
            "product_id": "BUGI-PLATINUM-VK20",
            "product_code": "VK20",
            "product_name": "Bugi Platinum VK20",
            "category": "Spark_Plugs",
            "forecast_units": 22000,
            "current_stock": 19200,
            "trend": "up",
            "change_percent": 8.3,
            "confidence": 91.8,
            "forecast_horizon": "60_days",
            "last_updated": datetime.utcnow().isoformat(),
            "timeSeries": _generate_weekly_timeseries_for_product(
                base_value=550,
                trend_direction='up',
                seasonal_strength=0.18,
                volatility=0.12,
                growth_rate=0.03
            )
        },
        {
            "product_id": "DIEU-HOA-COMPRESSOR-447220",
            "product_code": "447220-1510",
            "product_name": "Compressor điều hòa 10PA17C",
            "category": "AC_System",
            "forecast_units": 18000,
            "current_stock": 12400,
            "trend": "up",
            "change_percent": 16.7,
            "confidence": 88.5,
            "forecast_horizon": "60_days",
            "last_updated": datetime.utcnow().isoformat(),
            "timeSeries": _generate_weekly_timeseries_for_product(
                base_value=480,
                trend_direction='up',
                seasonal_strength=0.25,  # High seasonality for AC
                volatility=0.15,
                growth_rate=0.035
            )
        },
        {
            "product_id": "LOC-GIO-DEN-5656",
            "product_code": "DEN-5656",
            "product_name": "Lọc gió động cơ DENSO 5656",
            "category": "Filters",
            "forecast_units": 32000,
            "current_stock": 28400,
            "trend": "stable",
            "change_percent": 1.2,
            "confidence": 92.3,
            "forecast_horizon": "60_days",
            "last_updated": datetime.utcnow().isoformat(),
            "timeSeries": _generate_weekly_timeseries_for_product(
                base_value=800,
                trend_direction='stable',
                seasonal_strength=0.10,
                volatility=0.08,
                growth_rate=0.01
            )
        },
        {
            "product_id": "CAM-BIEN-OXY-234-9065",
            "product_code": "234-9065",
            "product_name": "Cảm biến oxy (O2 Sensor)",
            "category": "Sensors",
            "forecast_units": 15000,
            "current_stock": 11200,
            "trend": "up",
            "change_percent": 15.8,
            "confidence": 89.7,
            "forecast_horizon": "60_days",
            "last_updated": datetime.utcnow().isoformat(),
            "timeSeries": _generate_weekly_timeseries_for_product(
                base_value=375,
                trend_direction='up',
                seasonal_strength=0.15,
                volatility=0.11,
                growth_rate=0.028
            )
        },
    ]
    
    # Apply filters
    filtered = all_products
    if category:
        filtered = [p for p in filtered if p["category"].lower() == category.lower()]
    if product_codes:
        codes = [c.strip() for c in product_codes.split(",")]
        filtered = [p for p in filtered if p["product_code"] in codes]
    
    return filtered[:limit]


def _generate_time_series_data() -> List[Dict[str, Any]]:
    """Generate time series forecast data for charts (WEEKLY format)."""
    dates = []
    today = datetime.utcnow()
    
    # 12 weeks historical + 8 weeks forecast
    for i in range(-12, 8):
        date = today + timedelta(weeks=i)
        week_number = i + 13  # Week 1 to 20
        base_value = 5000 + (i / 2) * 100  # Slight upward trend
        
        dates.append({
            "date": date.strftime("%Y-%m-%d"),
            "week": f"Tuần {week_number}",
            "weekLabel": f"T{week_number}",
            "actual": round(base_value + ((-1) ** i) * 300) if i < 0 else None,
            "forecast": round(base_value) if i >= 0 else None,
            "upperBound": round(base_value * 1.15) if i >= 0 else None,
            "lowerBound": round(base_value * 0.85) if i >= 0 else None,
            "isHistorical": i < 0,
        })
    
    return dates


def _generate_weekly_timeseries_for_product(
    base_value: int,
    historical_weeks: int = 12,
    forecast_weeks: int = 8,
    trend_direction: str = 'up',
    seasonal_strength: float = 0.15,
    volatility: float = 0.1,
    growth_rate: float = 0.02
) -> List[Dict[str, Any]]:
    """Generate weekly time series for individual product."""
    import random
    import math
    
    data = []
    today = datetime.utcnow()
    
    # Historical data
    for i in range(-historical_weeks, 0):
        date = today + timedelta(weeks=i)
        week_number = historical_weeks + i + 1
        
        # Seasonal variation
        seasonal_factor = 1 + math.sin((i / 4) + (base_value % 10)) * seasonal_strength
        
        # Trend factor
        trend_factor = 1
        if trend_direction == 'up':
            trend_factor = 1 + ((-i / historical_weeks) * growth_rate * 3)
        elif trend_direction == 'down':
            trend_factor = 1 - ((-i / historical_weeks) * growth_rate * 2)
        
        actual = round(
            base_value * seasonal_factor * trend_factor +
            random.randint(int(-base_value * volatility), int(base_value * volatility))
        )
        
        data.append({
            "date": date.strftime("%Y-%m-%d"),
            "week": f"Tuần {week_number}",
            "weekLabel": f"T{week_number}",
            "actual": actual,
            "forecast": None,
            "upperBound": None,
            "lowerBound": None,
            "isHistorical": True
        })
    
    # Forecast data
    last_actual = data[-1]["actual"] if data else base_value
    for i in range(forecast_weeks):
        date = today + timedelta(weeks=i)
        week_number = historical_weeks + i + 1
        
        trend_factor = 1
        if trend_direction == 'up':
            trend_factor = 1 + (i * growth_rate)
        elif trend_direction == 'down':
            trend_factor = 1 - (i * growth_rate * 0.8)
        else:
            trend_factor = 1 + (i * growth_rate * 0.3)
        
        forecast = round(last_actual * trend_factor)
        confidence_width = 0.08 if trend_direction == 'stable' else 0.12
        
        data.append({
            "date": date.strftime("%Y-%m-%d"),
            "week": f"Tuần {week_number}",
            "weekLabel": f"T{week_number}",
            "actual": None,
            "forecast": forecast,
            "upperBound": round(forecast * (1 + confidence_width)),
            "lowerBound": round(forecast * (1 - confidence_width)),
            "isHistorical": False
        })
    
    return data


def _generate_heatmap_data() -> List[Dict[str, Any]]:
    """Generate category-month heatmap data."""
    categories = ["Spark_Plugs", "AC_System", "Filters", "Sensors", "Fuel_System"]
    heatmap = []
    
    today = datetime.utcnow()
    for category in categories:
        values = []
        for month_offset in range(6):
            month_date = today + timedelta(days=30 * month_offset)
            intensity = 0.5 + (month_offset / 10) + ((ord(category[0]) % 5) / 10)
            
            values.append({
                "month": month_date.strftime("%Y-%m"),
                "value": round(4000 + intensity * 2000),
                "intensity": round(min(intensity, 1.0), 2),
            })
        
        heatmap.append({
            "category": category,
            "values": values,
        })
    
    return heatmap


def _generate_heatmap_from_forecasts(forecasts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate heatmap from database forecast data."""
    # Group forecasts by category
    category_totals = {}
    for forecast in forecasts:
        category = forecast["category"]
        units = forecast["forecast_units"]
        
        if category not in category_totals:
            category_totals[category] = []
        category_totals[category].append(units)
    
    # Generate heatmap with actual data
    heatmap = []
    today = datetime.utcnow()
    
    for category, units_list in category_totals.items():
        avg_units = sum(units_list) / len(units_list)
        max_units = max(units_list)
        
        values = []
        for month_offset in range(6):
            month_date = today + timedelta(days=30 * month_offset)
            # Simulate monthly trend
            monthly_value = avg_units * (1 + month_offset * 0.05)
            intensity = min(monthly_value / (max_units * 1.5), 1.0)
            
            values.append({
                "month": month_date.strftime("%Y-%m"),
                "value": round(monthly_value),
                "intensity": round(intensity, 2),
            })
        
        heatmap.append({
            "category": category,
            "values": values,
        })
    
    return heatmap


def _calculate_forecast_metrics() -> Dict[str, Any]:
    """Calculate forecast model performance metrics."""
    return {
        "mape": 5.8,  # Mean Absolute Percentage Error
        "rmse": 287,  # Root Mean Squared Error
        "r_squared": 0.94,  # R-squared coefficient
        "model_type": "Prophet + LLM Adjustment",
        "last_trained": (datetime.utcnow() - timedelta(days=2)).isoformat(),
        "data_points": 450,
    }


def _generate_mock_actions(limit: int, priority: str | None, category: str | None) -> List[Dict[str, Any]]:
    """Generate mock action recommendations."""
    all_actions = [
        {
            "id": "action-001",
            "priority": "high",
            "category": "supply_chain",
            "title": "Bảo đảm tuyến vận tải thay thế từ cảng Busan",
            "description": "Tắc nghẽn cảng Yokohama ảnh hưởng lịch trình Q1. Cần chuyển sang tuyến vận tải dự phòng.",
            "impact": "Tránh chậm trễ giao hàng trị giá 450K USD",
            "estimated_cost": 450000,
            "estimated_cost_unit": "USD",
            "deadline": (datetime.utcnow() + timedelta(days=5)).strftime("%Y-%m-%d"),
            "actionItems": [
                "Liên hệ đại lý vận tải tại cảng Busan",
                "Đàm phán tuyến hàng không cho lô hàng khẩn",
                "Thông báo delay 5-7 ngày cho khách hàng"
            ],
            "affectedProducts": ["VCH20", "VK20", "447220-1510"],
            "riskIfIgnored": "Mất đơn hàng lớn từ Toyota VN (2.1M USD)",
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
        },
        {
            "id": "action-002",
            "priority": "high",
            "category": "inventory",
            "title": "Tăng tồn kho dự phòng Bugi Iridium VCH20",
            "description": "Dự báo tăng 12.5% nhu cầu Q1 do ra mắt xe mới. Tồn kho hiện tại không đủ.",
            "impact": "Đáp ứng nhu cầu tăng đột biến, tránh mất doanh thu 280K USD",
            "estimated_cost": 85000,
            "estimated_cost_unit": "USD",
            "deadline": (datetime.utcnow() + timedelta(days=10)).strftime("%Y-%m-%d"),
            "actionItems": [
                "Đặt hàng thêm 8000 đơn vị từ nhà máy Nhật",
                "Mở rộng kho miền Bắc thêm 200m²",
                "Đàm phán điều khoản thanh toán với nhà cung cấp"
            ],
            "affectedProducts": ["VCH20"],
            "riskIfIgnored": "Thiếu hàng trong peak season (tháng 1-2)",
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
        },
        {
            "id": "action-003",
            "priority": "medium",
            "category": "pricing",
            "title": "Điều chỉnh giá Compressor 447220 do biến động thép",
            "description": "Giá thép tăng 8% trong Q4, ảnh hưởng margin của dòng Compressor điều hòa.",
            "impact": "Duy trì margin 18%, tránh lỗ 120K USD/tháng",
            "estimated_cost": 0,
            "estimated_cost_unit": "USD",
            "deadline": (datetime.utcnow() + timedelta(days=15)).strftime("%Y-%m-%d"),
            "actionItems": [
                "Phân tích elasticity của segment khách hàng",
                "Đề xuất tăng giá 6-8% cho dòng Premium",
                "Thương lượng với đại lý về việc chia sẻ chi phí"
            ],
            "affectedProducts": ["447220-1510"],
            "riskIfIgnored": "Lỗ biên lợi nhuận, giảm ROI xuống 12%",
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
        },
        {
            "id": "action-004",
            "priority": "medium",
            "category": "production",
            "title": "Tăng ca sản xuất Lọc gió DENSO 5656",
            "description": "Nhu cầu ổn định cao, công suất hiện tại 87% - cần tăng để đáp ứng đơn hàng mới.",
            "impact": "Tăng output 15%, tối ưu chi phí đơn vị sản xuất",
            "estimated_cost": 45000,
            "estimated_cost_unit": "USD",
            "deadline": (datetime.utcnow() + timedelta(days=20)).strftime("%Y-%m-%d"),
            "actionItems": [
                "Tuyển thêm 12 công nhân ca 3",
                "Bảo trì máy móc để tăng uptime lên 95%",
                "Đặt mua nguyên liệu thêm 3 tháng"
            ],
            "affectedProducts": ["DEN-5656"],
            "riskIfIgnored": "Không đáp ứng đơn hàng Ford (350K USD)",
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
        },
        {
            "id": "action-005",
            "priority": "low",
            "category": "marketing",
            "title": "Campaign marketing cho O2 Sensor mùa bảo dưỡng",
            "description": "Tháng 12-1 là mùa cao điểm bảo dưỡng xe. Cơ hội tăng trưởng 15%.",
            "impact": "Tăng 15% doanh thu segment Sensors (225K USD)",
            "estimated_cost": 25000,
            "estimated_cost_unit": "USD",
            "deadline": (datetime.utcnow() + timedelta(days=25)).strftime("%Y-%m-%d"),
            "actionItems": [
                "Thiết kế campaign 'Kiểm tra miễn phí O2 Sensor'",
                "Phối hợp với 250 garage đối tác",
                "Chạy ads Facebook/Google trong 30 ngày"
            ],
            "affectedProducts": ["234-9065"],
            "riskIfIgnored": "Bỏ lỡ cơ hội tăng market share mùa cao điểm",
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
        },
        {
            "id": "action-006",
            "priority": "high",
            "category": "competitor",
            "title": "Đối phó chiến lược giảm giá của NGK Spark Plugs",
            "description": "NGK vừa giảm giá 10% dòng Iridium tại thị trường VN. Cần phản ứng nhanh.",
            "impact": "Bảo vệ thị phần 28%, tránh mất 180K USD doanh thu/tháng",
            "estimated_cost": 120000,
            "estimated_cost_unit": "USD",
            "deadline": (datetime.utcnow() + timedelta(days=7)).strftime("%Y-%m-%d"),
            "actionItems": [
                "Phân tích cấu trúc giá và margin của NGK",
                "Đề xuất combo promotion: mua 4 tặng 1",
                "Tăng cường visibility tại 150 điểm bán lớn"
            ],
            "affectedProducts": ["VCH20", "VK20"],
            "riskIfIgnored": "Mất 8-12% thị phần trong Q1",
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
        },
    ]
    
    # Apply filters
    filtered = all_actions
    if priority:
        filtered = [a for a in filtered if a["priority"].lower() == priority.lower()]
    if category:
        filtered = [a for a in filtered if a["category"].lower() == category.lower()]
    
    return filtered[:limit]


def _generate_mock_news(days: int, risk_threshold: int, category: str | None) -> List[Dict[str, Any]]:
    """Generate mock risk news items."""
    all_news = [
        {
            "id": "risk-001",
            "title": "Tắc nghẽn cảng Yokohama do bão Hagibis",
            "source": "Nikkei Asia",
            "date": (datetime.utcnow() - timedelta(days=5)).strftime("%Y-%m-%d"),
            "risk_score": 85,
            "category": "logistics",
            "category_name": "Logistics",
            "sentiment": "negative",
            "summary": "Bão Hagibis gây tắc nghẽn nghiêm trọng tại cảng Yokohama, ảnh hưởng lịch trình xuất khẩu phụ tùng ô tô.",
            "impact": "Ảnh hưởng lịch trình nhập khẩu Q1, delay 7-10 ngày",
            "tags": ["bão", "cảng biển", "logistics", "Nhật Bản"],
            "related_products": ["VCH20", "VK20", "447220-1510"],
            "affected_products": ["VCH20", "VK20", "447220-1510"],
            "url": "https://asia.nikkei.com/port-yokohama",
        },
        {
            "id": "risk-002",
            "title": "Giá thép Trung Quốc tăng 8% trong tháng 11",
            "source": "Bloomberg",
            "date": (datetime.utcnow() - timedelta(days=12)).strftime("%Y-%m-%d"),
            "risk_score": 72,
            "category": "supply_chain",
            "category_name": "Supply Chain",
            "sentiment": "negative",
            "summary": "Giá thép thô tại Trung Quốc tăng 8% do chính sách hạn chế sản xuất, tác động đến ngành sản xuất ô tô.",
            "impact": "Tăng chi phí sản xuất Compressor, giảm margin 3-5%",
            "tags": ["thép", "nguyên liệu", "Trung Quốc", "giá cả"],
            "related_products": ["447220-1510"],
            "affected_products": ["447220-1510"],
            "url": "https://bloomberg.com/steel-prices",
        },
        {
            "id": "risk-003",
            "title": "NGK Spark Plugs mở nhà máy mới tại Thái Lan",
            "source": "Reuters",
            "date": (datetime.utcnow() - timedelta(days=8)).strftime("%Y-%m-%d"),
            "risk_score": 68,
            "category": "competition",
            "category_name": "Competition",
            "sentiment": "negative",
            "summary": "NGK đầu tư 50 triệu USD xây dựng nhà máy sản xuất bugi mới tại Thái Lan, công suất 10 triệu sản phẩm/năm.",
            "impact": "Tăng cạnh tranh thị trường ASEAN, có thể mất 5-8% thị phần",
            "tags": ["NGK", "cạnh tranh", "Thái Lan", "bugi"],
            "related_products": ["VCH20", "VK20"],
            "affected_products": ["VCH20", "VK20"],
            "url": "https://reuters.com/ngk-thailand",
        },
        {
            "id": "risk-004",
            "title": "Toyota VN công bố dự án xe điện 2025",
            "source": "VnExpress",
            "date": (datetime.utcnow() - timedelta(days=3)).strftime("%Y-%m-%d"),
            "risk_score": 55,
            "category": "market_trend",
            "category_name": "Market Trend",
            "sentiment": "mixed",
            "summary": "Toyota Việt Nam công bố kế hoạch sản xuất xe điện, dự kiến ra mắt 2 mẫu xe hybrid và 1 mẫu full-EV trong năm 2025.",
            "impact": "Cơ hội: cảm biến EV. Rủi ro: giảm nhu cầu bugi dài hạn",
            "tags": ["xe điện", "Toyota", "EV", "hybrid"],
            "related_products": ["234-9065", "VCH20"],
            "affected_products": ["234-9065", "VCH20"],
            "url": "https://vnexpress.net/toyota-ev-2025",
        },
        {
            "id": "risk-005",
            "title": "Quy định khí thải Euro 5 có hiệu lực từ 01/2025",
            "source": "Bộ GTVT",
            "date": (datetime.utcnow() - timedelta(days=20)).strftime("%Y-%m-%d"),
            "risk_score": 78,
            "category": "regulatory",
            "category_name": "Regulatory",
            "sentiment": "positive",
            "summary": "Bộ GTVT chính thức ban hành quy định áp dụng tiêu chuẩn khí thải Euro 5 cho toàn bộ xe ô tô mới từ 01/01/2025.",
            "impact": "Tăng nhu cầu O2 Sensor và hệ thống lọc khí thải tiên tiến",
            "tags": ["Euro 5", "khí thải", "quy định", "môi trường"],
            "related_products": ["234-9065", "DEN-5656"],
            "affected_products": ["234-9065", "DEN-5656"],
            "url": "https://mt.gov.vn/euro5-2025",
        },
        {
            "id": "risk-006",
            "title": "Dự báo mùa nắng nóng kéo dài tại miền Trung",
            "source": "NCHMF",
            "date": (datetime.utcnow() - timedelta(days=15)).strftime("%Y-%m-%d"),
            "risk_score": 62,
            "category": "weather",
            "category_name": "Weather",
            "sentiment": "positive",
            "summary": "Trung tâm Khí tượng Thủy văn dự báo đợt nắng nóng kéo dài 3-4 tháng tại khu vực miền Trung và Tây Nguyên.",
            "impact": "Tăng nhu cầu điều hòa ô tô, dự kiến +18% doanh số Compressor",
            "tags": ["thời tiết", "nắng nóng", "điều hòa", "miền Trung"],
            "related_products": ["447220-1510"],
            "affected_products": ["447220-1510"],
            "url": "https://nchmf.gov.vn/weather-forecast",
        },
    ]
    
    # Apply filters
    filtered = [n for n in all_news if n["risk_score"] >= risk_threshold]
    if category:
        filtered = [n for n in filtered if n["category"].lower() == category.lower()]
    
    # Filter by days
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    filtered = [n for n in filtered if datetime.fromisoformat(n["date"]) >= cutoff_date]
    
    return filtered


def _generate_risk_timeline(days: int) -> List[Dict[str, Any]]:
    """Generate risk event timeline."""
    timeline = []
    today = datetime.utcnow()
    
    for i in range(-days, 0, 3):
        date = today + timedelta(days=i)
        count = abs(i % 5) + 1
        severity = 50 + (i % 30)
        
        timeline.append({
            "date": date.strftime("%Y-%m-%d"),
            "count": count,
            "severity_avg": severity,
        })
    
    return timeline


def _extract_risk_keywords() -> List[Dict[str, Any]]:
    """Extract top risk keywords from news."""
    # Normalize frequency to 0-1 range for frontend opacity calculation
    max_count = 15
    return [
        {"word": "Cảng biển", "keyword": "港口", "count": 15, "frequency": 15/max_count, "sentiment": -0.7},
        {"word": "Thép", "keyword": "鋼材", "count": 12, "frequency": 12/max_count, "sentiment": -0.5},
        {"word": "Cạnh tranh", "keyword": "競爭", "count": 10, "frequency": 10/max_count, "sentiment": -0.6},
        {"word": "Quy định môi trường", "keyword": "環境規制", "count": 8, "frequency": 8/max_count, "sentiment": 0.3},
        {"word": "Xe điện", "keyword": "電動車", "count": 7, "frequency": 7/max_count, "sentiment": 0.1},
        {"word": "Thời tiết", "keyword": "天候", "count": 6, "frequency": 6/max_count, "sentiment": 0.4},
        {"word": "Chuỗi cung ứng", "keyword": "供給網", "count": 5, "frequency": 5/max_count, "sentiment": -0.4},
        {"word": "Logistics", "keyword": "物流", "count": 4, "frequency": 4/max_count, "sentiment": -0.3},
    ]


def _calculate_risk_distribution() -> Dict[str, int]:
    """Calculate risk distribution by category."""
    return {
        "logistics": 35,
        "supply_chain": 25,
        "competition": 20,
        "regulatory": 12,
        "weather": 8,
    }
