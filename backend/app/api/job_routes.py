"""Job management API routes for Celery tasks."""

from typing import Any, Dict

from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException

from app.celery_app import celery_app
from app.tasks.forecast_tasks import run_scheduled_forecast

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/forecast/trigger", status_code=202)
async def trigger_forecast() -> Dict[str, Any]:
    """Manually trigger forecast job.
    
    Returns job ID for tracking.
    """
    try:
        print("🎯 [API] Triggering forecast job...")
        
        # Trigger async task
        task = run_scheduled_forecast.delay()
        
        print(f"✅ [API] Task queued: {task.id}")
        print(f"📊 [API] Task state: {task.state}")
        
        return {
            "job_id": task.id,
            "status": task.state.lower(),
            "message": "Forecast job triggered successfully",
        }
    except Exception as e:
        print(f"❌ [API] Failed to trigger job: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to trigger job: {str(e)}")


@router.get("/forecast/{job_id}")
async def get_job_status(job_id: str) -> Dict[str, Any]:
    """Get job status by ID.
    
    Possible states:
    - PENDING: Task waiting to be executed
    - STARTED: Task has been started
    - SUCCESS: Task completed successfully
    - FAILURE: Task failed
    - RETRY: Task is waiting for retry
    """
    try:
        task_result = AsyncResult(job_id, app=celery_app)
        
        response = {
            "job_id": job_id,
            "status": task_result.state,
            "result": None,
            "error": None,
        }
        
        if task_result.state == "PENDING":
            response["message"] = "Job is pending execution"
        
        elif task_result.state == "STARTED":
            response["message"] = "Job is running"
            response["progress"] = task_result.info.get("progress", 0) if task_result.info else 0
        
        elif task_result.state == "SUCCESS":
            response["message"] = "Job completed successfully"
            response["result"] = task_result.result
        
        elif task_result.state == "FAILURE":
            response["message"] = "Job failed"
            response["error"] = str(task_result.info)
        
        elif task_result.state == "RETRY":
            response["message"] = "Job is being retried"
            response["retry_count"] = task_result.info.get("retries", 0) if task_result.info else 0
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {str(e)}")


@router.get("/forecast/history")
async def get_job_history(limit: int = 10) -> Dict[str, Any]:
    """Get recent forecast job history.
    
    Note: This requires result backend to be configured.
    """
    # TODO: Implement job history tracking
    # For now, return placeholder
    return {
        "jobs": [],
        "total": 0,
        "message": "Job history tracking not yet implemented",
    }


@router.post("/forecast/{job_id}/cancel")
async def cancel_job(job_id: str) -> Dict[str, Any]:
    """Cancel a running job.
    
    Note: Only pending/started jobs can be cancelled.
    """
    try:
        task_result = AsyncResult(job_id, app=celery_app)
        
        if task_result.state in ["PENDING", "STARTED"]:
            task_result.revoke(terminate=True)
            return {
                "job_id": job_id,
                "status": "cancelled",
                "message": "Job cancelled successfully",
            }
        else:
            return {
                "job_id": job_id,
                "status": task_result.state,
                "message": f"Job cannot be cancelled (current state: {task_result.state})",
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel job: {str(e)}")


@router.get("/stats")
async def get_celery_stats() -> Dict[str, Any]:
    """Get Celery worker statistics.
    
    Requires Celery workers to be running.
    """
    try:
        # Get active tasks
        inspect = celery_app.control.inspect()
        
        active_tasks = inspect.active()
        scheduled_tasks = inspect.scheduled()
        registered_tasks = inspect.registered()
        
        return {
            "workers": {
                "active": len(active_tasks) if active_tasks else 0,
                "active_tasks": active_tasks or {},
            },
            "scheduled_tasks": scheduled_tasks or {},
            "registered_tasks": list(registered_tasks.values())[0] if registered_tasks else [],
        }
        
    except Exception as e:
        # Workers might not be running
        return {
            "error": str(e),
            "message": "Celery workers not responding. Make sure workers are running.",
        }
