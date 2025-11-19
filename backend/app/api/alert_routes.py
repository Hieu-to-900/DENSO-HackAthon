"""Alert API routes."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query

from app.database.connection import Database, get_db
from app.models.alert import Alert, AlertCreate, AlertStats, AlertUpdate
from app.repositories.alert_repository import AlertRepository

router = APIRouter(prefix="/alerts", tags=["alerts"])


def get_alert_repo(db: Database = Depends(get_db)) -> AlertRepository:
    """Dependency to get alert repository."""
    return AlertRepository(db)


@router.post("/", response_model=Alert, status_code=201)
async def create_alert(
    alert: AlertCreate,
    repo: AlertRepository = Depends(get_alert_repo),
):
    """Create a new alert."""
    try:
        return await repo.create_alert(alert)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create alert: {str(e)}")


@router.get("/", response_model=List[Alert])
async def get_alerts(
    since: Optional[datetime] = Query(None, description="Get alerts after this timestamp"),
    severity: Optional[str] = Query(None, pattern="^(high|medium|low)$"),
    alert_type: Optional[str] = Query(None),
    unread_only: bool = Query(False),
    product_code: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    repo: AlertRepository = Depends(get_alert_repo),
):
    """Get alerts with filtering."""
    try:
        return await repo.get_alerts(
            since=since,
            severity=severity,
            alert_type=alert_type,
            unread_only=unread_only,
            product_code=product_code,
            limit=limit,
            offset=offset,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch alerts: {str(e)}")


@router.get("/stats", response_model=AlertStats)
async def get_alert_stats(
    repo: AlertRepository = Depends(get_alert_repo),
):
    """Get alert statistics."""
    try:
        return await repo.get_alert_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch stats: {str(e)}")


@router.get("/unread-summary")
async def get_unread_summary(
    repo: AlertRepository = Depends(get_alert_repo),
):
    """Get unread alerts summary."""
    try:
        return await repo.get_unread_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch summary: {str(e)}")


@router.get("/{alert_id}", response_model=Alert)
async def get_alert(
    alert_id: UUID,
    repo: AlertRepository = Depends(get_alert_repo),
):
    """Get alert by ID."""
    alert = await repo.get_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.patch("/{alert_id}", response_model=Alert)
async def update_alert(
    alert_id: UUID,
    update: AlertUpdate,
    repo: AlertRepository = Depends(get_alert_repo),
):
    """Update alert (mark as read/dismissed)."""
    alert = await repo.update_alert(alert_id, update)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.post("/{alert_id}/mark-read", response_model=Alert)
async def mark_alert_read(
    alert_id: UUID,
    user_id: Optional[str] = Query(None),
    repo: AlertRepository = Depends(get_alert_repo),
):
    """Mark alert as read."""
    update = AlertUpdate(read=True, read_by=user_id)
    alert = await repo.update_alert(alert_id, update)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.post("/{alert_id}/dismiss", response_model=Alert)
async def dismiss_alert(
    alert_id: UUID,
    repo: AlertRepository = Depends(get_alert_repo),
):
    """Dismiss alert."""
    update = AlertUpdate(dismissed=True)
    alert = await repo.update_alert(alert_id, update)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

@router.post("/demo/yokohama-hagibis")
async def demo_yokohama_hagibis():
    """
    Demo alert: Tắc nghẽn cảng Yokohama do bão Hagibis.
    Không ghi vào DB, chỉ trả về payload giả để frontend test.
    """
    return {
        "id": str(uuid4()),
        "title": "Tắc nghẽn cảng Yokohama do bão Hagibis",
        "message": (
            "Bão Hagibis gây tắc nghẽn nghiêm trọng tại cảng Yokohama, "
            "ảnh hưởng lịch trình xuất khẩu phụ tùng ô tô."
        ),
        "severity": "high",
        "alert_type": "logistics",
        "source": "Nikkei Asia",
        "risk_score": 0.85,
        "tags": ["bão", "cảng biển", "logistics", "Nhật Bản"],
        "created_at": datetime.utcnow().isoformat(),
        "read": False,
        "dismissed": False,
    }


@router.delete("/cleanup")
async def cleanup_old_alerts(
    days: int = Query(90, ge=30, le=365, description="Delete alerts older than this many days"),
    repo: AlertRepository = Depends(get_alert_repo),
):
    """Delete old alerts (cleanup)."""
    try:
        deleted_count = await repo.delete_old_alerts(days)
        return {"deleted_count": deleted_count, "message": f"Deleted alerts older than {days} days"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cleanup alerts: {str(e)}")
