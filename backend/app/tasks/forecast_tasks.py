"""Celery tasks for demand forecasting."""

import asyncio
from datetime import date, datetime, timedelta
from typing import Any, Dict
from uuid import uuid4

from celery import Task

from app.celery_app import celery_app
from app.database.connection import Database
from app.models.alert import AlertCreate
from app.repositories.alert_repository import AlertRepository
from app.repositories.forecast_repository import ForecastRepository
from app.repositories.action_repository import ActionRepository


class AsyncTask(Task):
    """Base task with async support."""
    
    _db: Database = None
    
    @property
    def db(self) -> Database:
        """Get database connection."""
        if self._db is None:
            self._db = Database()
            # Initialize connection pool
            asyncio.run(self._db.connect())
        return self._db


@celery_app.task(
    bind=True,
    base=AsyncTask,
    name="app.tasks.forecast_tasks.run_scheduled_forecast",
    max_retries=3,
    default_retry_delay=300,  # 5 minutes
)
def run_scheduled_forecast(self) -> Dict[str, Any]:
    """Run demand forecast pipeline every 2 hours.
    
    This task:
    1. Triggers LangGraph forecast pipeline
    2. Generates alerts based on forecast results
    3. Stores alerts in database
    4. Returns execution summary
    """
    try:
        print(f"🚀 [TASK] Starting scheduled forecast at {datetime.utcnow()}")
        
        # Run async forecast function
        result = asyncio.run(_run_forecast_async(self.db))
        
        print(f"✅ [TASK] Forecast completed successfully")
        return result
        
    except Exception as exc:
        print(f"❌ [TASK] Forecast failed: {str(exc)}")
        # Retry on failure
        raise self.retry(exc=exc)


async def _run_forecast_async(db: Database) -> Dict[str, Any]:
    """Async implementation of forecast pipeline.
    
    Phase 1: Mock implementation
    Phase 2: Real LangGraph integration
    """
    # TODO Phase 2: Integrate with LangGraph
    # from src.agent.graph import graph
    # result = await graph.ainvoke({
    #     "product_codes": await _get_all_product_codes(),
    #     "chromadb_collection": "external_market_data"
    # })
    
    # Phase 1: Mock forecast execution for testing
    print("📊 [FORECAST] Running mock forecast pipeline...")
    await asyncio.sleep(2)  # Simulate processing
    
    # Mock LangGraph output
    job_id = uuid4()
    mock_langgraph_result = {
        "forecasts": [
            {
                "product_code": "BUGI-IRIDIUM-VCH20",
                "product_name": "Bugi Iridium VCH20",
                "category": "Spark_Plugs",
                "forecast_units": 4500,
                "current_stock": 3200,
                "trend": "increasing",
                "change_percent": 15.5,
                "confidence": 0.87,
                "timeseries": [
                    {"date": date.today() + timedelta(days=i), "forecast": 150 + i*2, "upper_bound": 170 + i*2, "lower_bound": 130 + i*2}
                    for i in range(30)
                ],
                "metrics": {
                    "mape": 8.5,
                    "rmse": 45.2,
                    "mae": 38.1,
                    "r_squared": 0.89,
                },
            },
            {
                "product_code": "AC-COMPRESSOR-6SEU14C",
                "product_name": "AC Compressor 6SEU14C",
                "category": "AC_System",
                "forecast_units": 2800,
                "current_stock": 3500,
                "trend": "stable",
                "change_percent": -2.3,
                "confidence": 0.92,
                "timeseries": [
                    {"date": date.today() + timedelta(days=i), "forecast": 93 + i, "upper_bound": 105 + i, "lower_bound": 81 + i}
                    for i in range(30)
                ],
                "metrics": {
                    "mape": 5.2,
                    "rmse": 28.7,
                    "mae": 24.3,
                    "r_squared": 0.93,
                },
            },
        ],
        "actions": [
            {
                "action_type": "capacity_planning",
                "category": "production",
                "title": "Increase Spark Plug Production Capacity",
                "description": "Forecast shows 15% demand increase for spark plugs. Recommend scheduling additional shifts.",
                "priority": "high",
                "affected_products": ["BUGI-IRIDIUM-VCH20", "BUGI-PLATIN-PK16TT"],
                "expected_impact": "+2,500 units capacity",
                "estimated_cost": 150000.0,
                "action_items": [
                    {"task": "Schedule 2 additional shifts", "owner": "Production Manager"},
                    {"task": "Order raw materials", "owner": "Procurement Team"},
                ],
                "deadline": datetime.utcnow() + timedelta(days=30),
                "confidence_score": 0.85,
            },
            {
                "action_type": "inventory_optimization",
                "category": "inventory",
                "title": "Reduce AC Compressor Stock Levels",
                "description": "Stable demand with high inventory. Recommend reducing reorder quantities.",
                "priority": "medium",
                "affected_products": ["AC-COMPRESSOR-6SEU14C"],
                "expected_impact": "-25% inventory holding cost",
                "estimated_cost": 0.0,
                "action_items": [
                    {"task": "Adjust reorder point to 2,500 units", "owner": "Inventory Manager"},
                    {"task": "Review supplier contracts", "owner": "Procurement Team"},
                ],
                "deadline": datetime.utcnow() + timedelta(days=14),
                "confidence_score": 0.78,
            },
        ],
    }
    
    # Save forecasts to database (Phase 2)
    forecast_repo = ForecastRepository(db.pool)
    action_repo = ActionRepository(db.pool)
    saved_forecast_ids = []
    
    for forecast_data in mock_langgraph_result["forecasts"]:
        # Create forecast record
        forecast_id = await forecast_repo.create_forecast(
            product_id=forecast_data["product_code"],  # Use product_code as ID for now
            product_code=forecast_data["product_code"],
            product_name=forecast_data["product_name"],
            category=forecast_data["category"],
            forecast_units=forecast_data["forecast_units"],
            forecast_horizon="30_days",
            forecast_start_date=date.today(),
            forecast_end_date=date.today() + timedelta(days=30),
            current_stock=forecast_data.get("current_stock"),
            trend=forecast_data.get("trend"),
            change_percent=forecast_data.get("change_percent"),
            confidence=forecast_data.get("confidence"),
            langgraph_job_id=job_id,
            model_type="Prophet + LLM",
        )
        saved_forecast_ids.append(forecast_id)
        
        # Save timeseries data
        await forecast_repo.save_timeseries(forecast_id, forecast_data.get("timeseries", []))
        
        # Save metrics
        metrics = forecast_data.get("metrics", {})
        if metrics:
            await forecast_repo.save_metrics(
                forecast_id=forecast_id,
                mape=metrics.get("mape"),
                rmse=metrics.get("rmse"),
                mae=metrics.get("mae"),
                r_squared=metrics.get("r_squared"),
                last_trained_at=datetime.utcnow(),
            )
        
        print(f"💾 [FORECAST] Saved forecast for {forecast_data['product_code']} (ID: {forecast_id})")
    
    # Save action recommendations
    saved_action_ids = []
    for action_data in mock_langgraph_result["actions"]:
        action_id = await action_repo.create_action(
            forecast_id=saved_forecast_ids[0] if saved_forecast_ids else None,
            action_type=action_data["action_type"],
            category=action_data["category"],
            title=action_data["title"],
            description=action_data["description"],
            priority=action_data["priority"],
            affected_products=action_data["affected_products"],
            expected_impact=action_data.get("expected_impact"),
            estimated_cost=action_data.get("estimated_cost"),
            action_items=action_data.get("action_items"),
            deadline=action_data.get("deadline"),
            confidence_score=action_data.get("confidence_score"),
            langgraph_job_id=job_id,
        )
        saved_action_ids.append(action_id)
        print(f"💾 [ACTION] Saved action: {action_data['title']} (ID: {action_id})")
    
    # Generate alerts (existing Phase 1 logic)
    mock_alerts = [
        {
            "alert_type": "capacity_warning",
            "severity": "high",
            "message": "Production capacity projected to reach 95% utilization in Q1 2025",
            "affected_products": ["BUGI-IRIDIUM-VCH20", "AC-COMPRESSOR-6SEU14C"],
            "affected_categories": ["Spark_Plugs", "AC_System"],
            "impact_description": "Forecast demand exceeds current capacity by 2,500 units",
            "action_required": "Schedule additional shifts or contract third-party manufacturers",
            "source": "scheduled_job",
            "metadata": {
                "forecast_period": "Q1_2025",
                "utilization_rate": 0.95,
                "shortfall_units": 2500,
                "execution_time": datetime.utcnow().isoformat(),
                "langgraph_job_id": str(job_id),
            },
            "priority_score": 90,
        },
        {
            "alert_type": "demand_spike",
            "severity": "medium",
            "message": "15% demand increase detected for Spark Plugs category",
            "affected_products": ["BUGI-IRIDIUM-VCH20", "BUGI-PLATIN-PK16TT"],
            "affected_categories": ["Spark_Plugs"],
            "impact_description": "Market analysis indicates increased vehicle maintenance activity",
            "action_required": "Increase raw material orders and adjust production schedule",
            "source": "scheduled_job",
            "metadata": {
                "demand_increase": 0.15,
                "market_factor": "seasonal",
                "confidence": 0.87,
            },
            "priority_score": 70,
        },
    ]
    
    # Store alerts in database
    repo = AlertRepository(db)
    created_alerts = []
    
    for alert_data in mock_alerts:
        alert = AlertCreate(**alert_data)
        created_alert = await repo.create_alert(alert)
        created_alerts.append(created_alert)
        print(f"🔔 [ALERT] Created: {created_alert.alert_type} - {created_alert.severity}")
    
    return {
        "status": "completed",
        "execution_time": datetime.utcnow().isoformat(),
        "langgraph_job_id": str(job_id),
        "forecasts_saved": len(saved_forecast_ids),
        "actions_saved": len(saved_action_ids),
        "alerts_generated": len(created_alerts),
        "forecast_ids": [str(fid) for fid in saved_forecast_ids],
        "action_ids": [str(aid) for aid in saved_action_ids],
        "alert_ids": [str(alert.id) for alert in created_alerts],
        "summary": {
            "high_severity": sum(1 for a in created_alerts if a.severity == "high"),
            "medium_severity": sum(1 for a in created_alerts if a.severity == "medium"),
            "low_severity": sum(1 for a in created_alerts if a.severity == "low"),
        },
    }


@celery_app.task(
    bind=True,
    base=AsyncTask,
    name="app.tasks.forecast_tasks.generate_daily_summary",
)
def generate_daily_summary(self) -> Dict[str, Any]:
    """Generate daily forecast summary report.
    
    Runs every day at 8 AM to summarize alerts and forecasts.
    """
    try:
        print(f"📊 [TASK] Generating daily summary at {datetime.utcnow()}")
        
        result = asyncio.run(_generate_summary_async(self.db))
        
        print(f"✅ [TASK] Daily summary completed")
        return result
        
    except Exception as exc:
        print(f"❌ [TASK] Summary generation failed: {str(exc)}")
        raise self.retry(exc=exc)


async def _generate_summary_async(db: Database) -> Dict[str, Any]:
    """Generate summary report."""
    repo = AlertRepository(db)
    stats = await repo.get_alert_stats()
    
    summary = {
        "date": datetime.utcnow().date().isoformat(),
        "total_alerts": stats.total_alerts,
        "unread_alerts": stats.unread_count,
        "alerts_by_severity": stats.by_severity,
        "alerts_by_type": stats.by_type,
        "latest_alert": stats.latest_alert.isoformat() if stats.latest_alert else None,
    }
    
    print(f"📈 [SUMMARY] Total alerts: {stats.total_alerts}, Unread: {stats.unread_count}")
    
    # TODO: Send summary email/Slack notification
    # await send_email_summary(summary)
    # await send_slack_summary(summary)
    
    return summary


@celery_app.task(
    bind=True,
    base=AsyncTask,
    name="app.tasks.forecast_tasks.cleanup_old_alerts",
)
def cleanup_old_alerts(self, days: int = 90) -> Dict[str, Any]:
    """Cleanup alerts older than specified days.
    
    Runs weekly on Sunday at midnight.
    
    Args:
        days: Delete alerts older than this many days (default: 90)
    """
    try:
        print(f"🧹 [TASK] Starting cleanup of alerts older than {days} days")
        
        result = asyncio.run(_cleanup_alerts_async(self.db, days))
        
        print(f"✅ [TASK] Cleanup completed: {result['deleted_count']} alerts deleted")
        return result
        
    except Exception as exc:
        print(f"❌ [TASK] Cleanup failed: {str(exc)}")
        raise self.retry(exc=exc)


async def _cleanup_alerts_async(db: Database, days: int) -> Dict[str, Any]:
    """Cleanup old alerts."""
    repo = AlertRepository(db)
    deleted_count = await repo.delete_old_alerts(days)
    
    return {
        "deleted_count": deleted_count,
        "threshold_days": days,
        "execution_time": datetime.utcnow().isoformat(),
    }


# Helper function for Phase 2 integration
async def _get_all_product_codes() -> list[str]:
    """Get all product codes from category mock data.
    
    Phase 2: Replace with real database query.
    """
    # TODO: Import from category_products_mock
    return [
        "BUGI-IRIDIUM-VCH20",
        "BUGI-PLATIN-PK16TT",
        "AC-COMPRESSOR-6SEU14C",
        "AC-EVAPORATOR-CORE",
        "AC-CONDENSER-CORE",
    ]
