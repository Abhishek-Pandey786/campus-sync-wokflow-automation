"""
Alerts Service (Week 9)
Scans active service requests, runs ML predictions, flags high-risk requests,
calculates SLA countdowns, and triggers email notifications.
"""

import joblib
import numpy as np
import logging
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session

from db.models import ServiceRequest, RequestStatus, MLPrediction
from core.config import settings
from services.notifications import notify_high_risk_request

logger = logging.getLogger(__name__)

# SLA hours per request type
SLA_MAP: Dict[str, int] = {
    "certificate": 72,
    "hostel":      48,
    "it_support":  24,
    "library":     48,
    "exam":        96,
    "transcript":  120,
}

# Model paths
MODEL_DIR = "ml/models"

_model_cache: Dict[str, Any] = {}


def _load_models() -> Dict[str, Any]:
    """Load ML models (cached after first load)."""
    if _model_cache:
        return _model_cache
    try:
        _model_cache["model"]               = joblib.load(f"{MODEL_DIR}/best_model.pkl")
        _model_cache["feature_columns"]     = joblib.load(f"{MODEL_DIR}/feature_columns.pkl")
        _model_cache["label_encoder_type"]  = joblib.load(f"{MODEL_DIR}/label_encoder_type.pkl")
        _model_cache["label_encoder_stage"] = joblib.load(f"{MODEL_DIR}/label_encoder_stage.pkl")
    except Exception as exc:
        logger.error(f"[ALERTS] Failed to load ML models: {exc}")
        _model_cache["error"] = str(exc)
    return _model_cache


def _predict_for_request(req: ServiceRequest, models: Dict[str, Any]) -> float:
    """Run ML prediction for a single ServiceRequest. Returns probability (0-1)."""
    if "error" in models:
        return 0.0

    try:
        req_type = req.request_type.value if hasattr(req.request_type, "value") else str(req.request_type)
        stage    = req.current_stage.value if hasattr(req.current_stage, "value") else "created"

        try:
            type_enc  = int(models["label_encoder_type"].transform([req_type])[0])
        except Exception:
            type_enc = 0

        try:
            stage_enc = int(models["label_encoder_stage"].transform([stage])[0])
        except Exception:
            stage_enc = 5

        hour      = req.created_at.hour if req.created_at else 9
        dow       = req.created_at.weekday() if req.created_at else 0
        priority  = int(req.priority or 1)
        workload  = 3  # default workload estimate
        sla       = SLA_MAP.get(req_type, 48)

        # Default stage durations (hours) – will be updated as workflow progresses
        stage_dur = [4.0, 6.0, 8.0, 10.0, 12.0]
        total_dur = sum(stage_dur)

        features = [
            type_enc,
            priority,
            hour,
            dow,
            1 if dow >= 5 else 0,                            # is_weekend
            1 if hour in [10, 11, 14, 15, 16] else 0,        # is_peak_hour
            1 if 8 <= hour <= 17 else 0,                     # is_business_hours
            1 if priority == 3 else 0,                       # is_high_priority
            1 if priority == 1 else 0,                       # is_low_priority
            workload,
            1 if workload > 5 else 0,                        # high_workload
            sla,
            *stage_dur,                                      # 5 stage durations
            total_dur,
            stage_enc,
        ]

        arr = np.array(features).reshape(1, -1)
        return float(models["model"].predict_proba(arr)[0][1])

    except Exception as exc:
        logger.error(f"[ALERTS] Prediction error for request {req.id}: {exc}")
        return 0.0


def _hours_remaining(req: ServiceRequest) -> Optional[float]:
    """Return hours left before SLA breach. Negative if already breached."""
    if not req.created_at:
        return None
    req_type = req.request_type.value if hasattr(req.request_type, "value") else str(req.request_type)
    sla_h    = SLA_MAP.get(req_type, 48)

    # Make created_at timezone-aware if needed
    created = req.created_at
    if created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)

    elapsed   = (datetime.now(timezone.utc) - created).total_seconds() / 3600
    return round(sla_h - elapsed, 2)


def _urgency(hours_left: Optional[float]) -> str:
    if hours_left is None:
        return "medium"
    if hours_left <= 0:
        return "critical"
    if hours_left < 6:
        return "critical"
    if hours_left < 24:
        return "high"
    if hours_left < 48:
        return "medium"
    return "low"


def _save_prediction(db: Session, req: ServiceRequest, score: float) -> None:
    """Persist prediction result to ml_predictions table."""
    try:
        pred = MLPrediction(
            service_request_id=req.id,
            prediction_type="alert_scan",
            predicted_label="delayed" if score >= settings.DELAY_RISK_THRESHOLD else "on_time",
            confidence_score=score,
            model_version=settings.MODEL_VERSION,
            features_used=None,
        )
        db.add(pred)
        db.commit()
    except Exception as exc:
        logger.error(f"[ALERTS] Could not save prediction for request {req.id}: {exc}")
        db.rollback()


def get_high_risk_requests(db: Session) -> List[Dict]:
    """
    Return current high-risk requests without triggering notifications.
    Useful for the GET /alerts endpoint.
    """
    models = _load_models()

    active_requests = (
        db.query(ServiceRequest)
        .filter(ServiceRequest.status.in_([RequestStatus.PENDING, RequestStatus.IN_PROGRESS]))
        .all()
    )

    high_risk = []
    for req in active_requests:
        score      = _predict_for_request(req, models)
        hours_left = _hours_remaining(req)

        if score >= settings.DELAY_RISK_THRESHOLD:
            req_type = req.request_type.value if hasattr(req.request_type, "value") else str(req.request_type)
            high_risk.append({
                "request_id":      req.id,
                "request_number":  req.request_number,
                "request_type":    req_type,
                "title":           req.title,
                "student_id":      req.student_id,
                "student_name":    req.student.full_name if req.student else "Unknown",
                "status":          req.status.value if hasattr(req.status, "value") else str(req.status),
                "current_stage":   req.current_stage.value if hasattr(req.current_stage, "value") else str(req.current_stage),
                "priority":        req.priority,
                "risk_score":      round(score, 4),
                "risk_percent":    round(score * 100, 1),
                "hours_remaining": hours_left,
                "urgency":         _urgency(hours_left),
                "sla_hours":       SLA_MAP.get(req_type, 48),
                "created_at":      req.created_at.isoformat() if req.created_at else None,
            })

    # Sort: critical first, then by ascending hours_remaining
    high_risk.sort(
        key=lambda x: (
            {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(x["urgency"], 9),
            x["hours_remaining"] if x["hours_remaining"] is not None else 9999,
        )
    )
    return high_risk


def run_alert_scan(db: Session) -> Dict:
    """
    Full alert scan: predict all active requests, flag high-risk ones,
    save predictions, and send email notifications.
    Returns a summary dict.
    """
    models   = _load_models()
    if "error" in models:
        return {"error": models["error"], "scanned": 0, "flagged": 0, "notified": 0}

    active_requests = (
        db.query(ServiceRequest)
        .filter(ServiceRequest.status.in_([RequestStatus.PENDING, RequestStatus.IN_PROGRESS]))
        .all()
    )

    scanned  = 0
    flagged  = 0
    notified = 0
    alerts   = []

    for req in active_requests:
        scanned   += 1
        score      = _predict_for_request(req, models)
        hours_left = _hours_remaining(req)
        urgency    = _urgency(hours_left)
        req_type   = req.request_type.value if hasattr(req.request_type, "value") else str(req.request_type)

        _save_prediction(db, req, score)

        if score >= settings.DELAY_RISK_THRESHOLD:
            flagged += 1
            student_name = req.student.full_name if req.student else "Unknown"

            sent = notify_high_risk_request(
                request_id=req.id,
                request_number=req.request_number,
                request_type=req_type,
                student_name=student_name,
                risk_score=score,
                urgency=urgency,
                hours_remaining=hours_left,
            )
            if sent:
                notified += 1

            alerts.append({
                "request_id":      req.id,
                "request_number":  req.request_number,
                "request_type":    req_type,
                "risk_score":      round(score, 4),
                "urgency":         urgency,
                "hours_remaining": hours_left,
                "email_sent":      sent,
            })

    logger.info(
        f"[ALERT-SCAN] scanned={scanned} flagged={flagged} notified={notified}"
    )

    return {
        "scan_time":  datetime.now(timezone.utc).isoformat(),
        "scanned":    scanned,
        "flagged":    flagged,
        "notified":   notified,
        "threshold":  settings.DELAY_RISK_THRESHOLD,
        "alerts":     alerts,
    }
