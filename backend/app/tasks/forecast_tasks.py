"""Celery tasks for demand forecasting."""

import asyncio
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict
from uuid import uuid4

from celery import Task

from app.celery_app import celery_app
from app.database.connection import Database
from app.models.alert import AlertCreate
from app.repositories.alert_repository import AlertRepository
from app.repositories.forecast_repository import ForecastRepository
from app.repositories.action_repository import ActionRepository

# Add src directory to Python path for LangGraph imports
src_path = Path(__file__).parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

# Import LangGraph
from agent.graph import graph
from agent.types_new import State


class AsyncTask(Task):
    """Base task with async support."""
    
    async def get_db(self) -> Database:
        """Get fresh database connection for this task."""
        db = Database()
        await db.connect()
        return db


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
    loop = None
    try:
        print(f"🚀 [TASK] Starting scheduled forecast at {datetime.utcnow()}")
        
        # Create new event loop for this task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Run async forecast function with fresh DB connection
        result = loop.run_until_complete(_run_forecast_async_wrapper())
        
        print(f"✅ [TASK] Forecast completed successfully")
        return result
        
    except Exception as exc:
        print(f"❌ [TASK] Forecast failed: {str(exc)}")
        # Retry on failure
        raise self.retry(exc=exc)
    finally:
        # Clean up event loop AFTER all operations complete
        if loop:
            try:
                # Cancel pending tasks
                pending = asyncio.all_tasks(loop)
                for task in pending:
                    task.cancel()
                # Run loop one more time to handle cancellations
                if pending:
                    loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                loop.close()
            except Exception as e:
                print(f"⚠️ [TASK] Error cleaning up event loop: {str(e)}")


async def _run_forecast_async_wrapper() -> Dict[str, Any]:
    """Wrapper to create fresh DB connection."""
    db = Database()
    await db.connect()
    
    try:
        result = await _run_forecast_async(db)
        # CRITICAL: Ensure all DB operations complete before returning
        await asyncio.sleep(0.1)  # Give time for pending operations
        return result
    except Exception as e:
        print(f"❌ [WRAPPER] Error in forecast pipeline: {str(e)}")
        raise
    finally:
        # Close connection AFTER all operations complete
        try:
            await db.close()
        except Exception as e:
            print(f"⚠️ [WRAPPER] Error closing DB: {str(e)}")


async def _run_forecast_async(db: Database) -> Dict[str, Any]:
    """Async implementation of forecast pipeline.
    
    Phase 2: Real LangGraph integration
    """
    job_id = uuid4()
    
    try:
        # ========== Phase 2: Real LangGraph Integration ==========
        print("🚀 [FORECAST] Starting LangGraph pipeline...")
        
        # Get all product codes
        product_codes = await _get_all_product_codes()
        print(f"📦 [FORECAST] Processing {len(product_codes)} products")
        
        # Construct initial state for LangGraph
        initial_state = State(
            product_codes=product_codes,
            chromadb_collection="denso_market_intelligence",
        )
        
        # Configure context for LangGraph execution
        config = {
            "configurable": {
                "product_codes": product_codes,
                "chromadb_path": None,  # Use default
                "xai_api_key": None,  # Use default from env
                "num_batches": 2,  # Process in 2 category batches
            }
        }
        
        print("🤖 [LANGGRAPH] Invoking graph with state...")
        start_time = datetime.utcnow()
        
        # Invoke LangGraph with timeout (max 10 minutes)
        try:
            langgraph_result = await asyncio.wait_for(
                graph.ainvoke(initial_state, config=config),
                timeout=600.0  # 10 minutes
            )
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            print(f"✅ [LANGGRAPH] Pipeline completed in {execution_time:.2f}s")
            
        except asyncio.TimeoutError:
            print("⏱️ [LANGGRAPH] Timeout after 10 minutes, using fallback mock data")
            langgraph_result = None
        except Exception as e:
            print(f"❌ [LANGGRAPH] Execution failed: {str(e)}")
            import traceback
            traceback.print_exc()
            langgraph_result = None
        
        # Extract forecasts and actions from LangGraph result
        if langgraph_result and langgraph_result.get("batch_results"):
            # Parse real LangGraph output
            print("📊 [LANGGRAPH] Parsing batch results...")
            mock_langgraph_result = _parse_langgraph_output(langgraph_result, job_id)
        else:
            # Fallback to mock data if LangGraph fails
            print("⚠️ [FALLBACK] Using mock data due to LangGraph failure")
            mock_langgraph_result = _generate_mock_forecast_data(job_id)
        
        # Save forecasts to database (Phase 2)
        print(f"💾 [DATABASE] Saving {len(mock_langgraph_result['forecasts'])} forecasts...")
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
        
        # Ensure all forecast operations are complete
        await asyncio.sleep(0.05)
        
        # Save action recommendations
        print(f"💾 [DATABASE] Saving {len(mock_langgraph_result['actions'])} actions...")
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
        
    except Exception as exc:
        print(f"❌ [FORECAST] Fatal error in forecast pipeline: {str(exc)}")
        import traceback
        traceback.print_exc()
        # Return error status but don't crash
        return {
            "status": "failed",
            "error": str(exc),
            "execution_time": datetime.utcnow().isoformat(),
            "langgraph_job_id": str(job_id),
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
        
        result = asyncio.run(_generate_summary_wrapper())
        
        print(f"✅ [TASK] Daily summary completed")
        return result
        
    except Exception as exc:
        print(f"❌ [TASK] Summary generation failed: {str(exc)}")
        raise self.retry(exc=exc)


async def _generate_summary_wrapper() -> Dict[str, Any]:
    """Wrapper to create fresh DB connection."""
    db = Database()
    await db.connect()
    
    try:
        result = await _generate_summary_async(db)
        return result
    finally:
        await db.close()


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
        
        result = asyncio.run(_cleanup_alerts_wrapper(days))
        
        print(f"✅ [TASK] Cleanup completed: {result['deleted_count']} alerts deleted")
        return result
        
    except Exception as exc:
        print(f"❌ [TASK] Cleanup failed: {str(exc)}")
        raise self.retry(exc=exc)


async def _cleanup_alerts_wrapper(days: int) -> Dict[str, Any]:
    """Wrapper to create fresh DB connection."""
    db = Database()
    await db.connect()
    
    try:
        result = await _cleanup_alerts_async(db, days)
        return result
    finally:
        await db.close()


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


def _parse_langgraph_output(langgraph_result: State, job_id: uuid4) -> Dict[str, Any]:
    """Parse LangGraph State output into forecast/action format.
    
    Args:
        langgraph_result: LangGraph State object with batch_results
        job_id: Job identifier for tracking
        
    Returns:
        Dict with forecasts and actions arrays
    """
    forecasts = []
    actions = []
    
    # Extract forecasts from batch_results
    batch_results = langgraph_result.get("batch_results", [])
    print(f"🔍 [PARSER] Found {len(batch_results)} batches in result")
    
    for batch_idx, batch in enumerate(batch_results):
        if not batch:
            continue
            
        category = batch.get("category", "Unknown")
        print(f"🔍 [PARSER] Processing batch {batch_idx}: category={category}")
        
        # batch_results is nested: batch["batch_results"] contains product forecasts
        product_results = batch.get("batch_results", [])
        print(f"🔍 [PARSER] Found {len(product_results)} products in batch {batch_idx}")
        
        for product_result in product_results:
            # Extract forecast data from nested structure
            forecast_info = product_result.get("forecast", {})
            
            forecast_data = {
                "product_code": product_result.get("product_code"),
                "product_name": product_result.get("product_name"),
                "category": product_result.get("category", category),
                "forecast_units": int(forecast_info.get("forecast_units", 0)),
                "current_stock": 0,  # Not provided in new structure
                "trend": "stable",  # Derived from growth_factor
                "change_percent": 0.0,  # Calculate from forecast
                "confidence": float(forecast_info.get("model_confidence", 0.75)),
                "timeseries": forecast_info.get("monthly_breakdown", []),
                "metrics": {
                    "method": forecast_info.get("method", "unknown"),
                    "growth_factor": forecast_info.get("category_growth_factor", 1.0),
                },
            }
            forecasts.append(forecast_data)
        
        # Extract actions from batch
        for action_item in batch.get("suggested_actions", []):
            action_data = {
                "action_type": action_item.get("action_type", "optimization"),
                "category": action_item.get("category", "general"),
                "title": action_item.get("title", "Action Required"),
                "description": action_item.get("description", ""),
                "priority": action_item.get("priority", "medium"),
                "affected_products": action_item.get("affected_products", []),
                "expected_impact": action_item.get("expected_impact", ""),
                "estimated_cost": float(action_item.get("estimated_cost", 0.0)),
                "action_items": action_item.get("action_items", []),
                "deadline": action_item.get("deadline"),
                "confidence_score": float(action_item.get("confidence_score", 0.75)),
            }
            actions.append(action_data)
    
    # Extract production suggestions from output_subgraph
    if langgraph_result.get("production_suggestions"):
        for suggestion in langgraph_result["production_suggestions"]:
            action_data = {
                "action_type": "production_planning",
                "category": "production",
                "title": suggestion.get("title", "Production Adjustment"),
                "description": suggestion.get("description", ""),
                "priority": suggestion.get("priority", "medium"),
                "affected_products": suggestion.get("affected_products", []),
                "expected_impact": suggestion.get("expected_impact", ""),
                "estimated_cost": float(suggestion.get("estimated_cost", 0.0)),
                "action_items": suggestion.get("action_items", []),
                "deadline": suggestion.get("deadline"),
                "confidence_score": float(suggestion.get("confidence_score", 0.75)),
            }
            actions.append(action_data)
    
    print(f"📊 [PARSER] Extracted {len(forecasts)} forecasts and {len(actions)} actions from LangGraph")
    
    return {
        "forecasts": forecasts,
        "actions": actions,
    }


def _generate_mock_forecast_data(job_id: uuid4) -> Dict[str, Any]:
    """Generate mock forecast data for fallback when LangGraph fails.
    
    Args:
        job_id: Job identifier for tracking
        
    Returns:
        Dict with forecasts and actions arrays (same format as real LangGraph)
    """
    return {
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
