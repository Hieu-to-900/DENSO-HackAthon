# app/api/routes/notification_routes.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.email_service import send_assignment_email

router = APIRouter(prefix="/notifications", tags=["notifications"])


class AssignmentEmailRequest(BaseModel):
    to_email: str
    assignee_name: str
    risk_title: str


@router.post("/assignment-email")
async def assignment_email(payload: AssignmentEmailRequest):
    subject = f"[DENSO Forecast] Nhiệm vụ mới: {payload.risk_title}"
    body = f"""
    <p>Chào {payload.assignee_name},</p>
    <p>Bạn vừa được phân công xử lý rủi ro: <b>{payload.risk_title}</b>.</p>
    <p>Vui lòng đăng nhập Action Board để xem chi tiết.</p>
    <p>Trân trọng,<br/>DENSO Forecast Suite</p>
    """

    try:
        send_assignment_email(payload.to_email, subject, body)
        return {"status": "sent"}
    except Exception as e:
        print("[Email] Error:", e)
        raise HTTPException(status_code=500, detail=f"Failed to send email: {e}")