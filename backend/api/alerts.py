"""
Alerts API Router (Week 9)
Endpoints for proactive delay-risk alerts and admin intervention.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone

from db.database import get_db
from db.models import ServiceRequest, RequestStatus, WorkflowStage, WorkflowLog
from core.dependencies import get_current_user, require_admin
from db.models import User
from services.alerts_service import get_high_risk_requests, run_alert_scan
from services.notifications import notify_escalation

router = APIRouter()


# ─────────────── Response schemas ────────────────

class AlertItem(BaseModel):
    request_id:      int
    request_number:  str
    request_type:    str
    title:           str
    student_id:      int
    student_name:    str
    status:          str
    current_stage:   str
    priority:        int
    risk_score:      float
    risk_percent:    float
    hours_remaining: Optional[float]
    urgency:         str
    sla_hours:       int
    created_at:      Optional[str]

    class Config:
        from_attributes = True


class ScanResult(BaseModel):
    scan_time:  str
    scanned:    int
    flagged:    int
    notified:   int
    threshold:  float
    alerts:     list


class EscalateRequest(BaseModel):
    notes: Optional[str] = ""


# ─────────────── Endpoints ────────────────

@router.get("", response_model=list[AlertItem])
async def list_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return all currently active requests with delay-risk ≥ threshold.
    Sorted by urgency (critical → high → medium → low).
    Requires authentication.
    """
    try:
        return get_high_risk_requests(db)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Alert scan failed: {str(exc)}",
        )


@router.post("/scan", response_model=ScanResult)
async def trigger_scan(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Manually trigger an alert scan and send email notifications.
    Admin only.
    """
    try:
        result = run_alert_scan(db)
        return result
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scan failed: {str(exc)}",
        )


@router.post("/{request_id}/escalate")
async def escalate_request(
    request_id: int,
    body: EscalateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Mark a request as high priority and log the escalation.
    Admin only.
    """
    req = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    # Bump priority to 3 (high)
    req.priority = 3

    # Log the escalation in workflow_logs
    log_entry = WorkflowLog(
        service_request_id=req.id,
        handler_id=current_user.id,
        stage=req.current_stage,
        action="Escalated by admin due to delay risk",
        notes=body.notes or "",
        handler_workload=0,
    )
    db.add(log_entry)
    db.commit()
    db.refresh(req)

    # Send notification
    req_type = req.request_type.value if hasattr(req.request_type, "value") else str(req.request_type)
    notify_escalation(
        request_id=req.id,
        request_number=req.request_number,
        request_type=req_type,
        escalated_by=current_user.full_name or current_user.email,
        notes=body.notes or "",
    )

    return {
        "message":        f"Request {req.request_number} escalated successfully",
        "request_id":     req.id,
        "request_number": req.request_number,
        "new_priority":   req.priority,
        "escalated_by":   current_user.email,
        "escalated_at":   datetime.now(timezone.utc).isoformat(),
    }
