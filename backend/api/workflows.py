"""
Workflow Management API Endpoints
Operations for workflow state management and logging
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime

from core.dependencies import get_db, get_current_user, require_admin
from db.models import (
    User, ServiceRequest, WorkflowLog, StageTransition,
    UserRole, RequestStatus, WorkflowStage
)
from schemas.workflow import (
    WorkflowLogCreate,
    WorkflowLogResponse,
    WorkflowLogWithHandler,
    AssignRequest,
    AdvanceStage,
    StageTransitionResponse,
    WorkflowTimeline
)

router = APIRouter()


# Define stage progression mapping
STAGE_PROGRESSION = {
    WorkflowStage.CREATED: WorkflowStage.ASSIGNED,
    WorkflowStage.ASSIGNED: WorkflowStage.VERIFIED,
    WorkflowStage.VERIFIED: WorkflowStage.APPROVED,
    WorkflowStage.APPROVED: WorkflowStage.PROCESSED,
    WorkflowStage.PROCESSED: WorkflowStage.COMPLETED,
}


@router.post("/{request_id}/assign", response_model=dict)
async def assign_request(
    request_id: int,
    assignment: AssignRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Assign a service request to an admin (Admin only)
    """
    # Get the request
    request = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service request not found"
        )
    
    # Verify the admin exists
    admin = db.query(User).filter(
        User.id == assignment.admin_id,
        User.role == UserRole.ADMIN
    ).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found"
        )
    
    # Update request
    old_stage = request.current_stage
    request.assigned_to = assignment.admin_id
    request.assigned_at = datetime.utcnow()
    request.current_stage = WorkflowStage.ASSIGNED
    request.status = RequestStatus.IN_PROGRESS
    
    # Create workflow log
    admin_workload = db.query(ServiceRequest).filter(
        ServiceRequest.assigned_to == assignment.admin_id,
        ServiceRequest.status == RequestStatus.IN_PROGRESS
    ).count()
    
    log = WorkflowLog(
        service_request_id=request.id,
        handler_id=current_user.id,
        stage=WorkflowStage.ASSIGNED,
        action=f"Request assigned to {admin.full_name}",
        notes=f"Assigned by {current_user.full_name}",
        handler_workload=admin_workload
    )
    db.add(log)
    
    # Create stage transition
    now = datetime.utcnow()
    if old_stage != WorkflowStage.ASSIGNED:
        transition = StageTransition(
            service_request_id=request.id,
            from_stage=old_stage,
            to_stage=WorkflowStage.ASSIGNED,
            transition_duration=None,
            handler_workload=admin_workload,
            time_of_day=now.hour,
            day_of_week=now.weekday(),
            transitioned_at=now
        )
        db.add(transition)
    
    db.commit()
    
    return {
        "message": f"Request {request.request_number} assigned to {admin.full_name}",
        "assigned_to": admin.full_name,
        "admin_id": admin.id
    }


@router.post("/{request_id}/advance", response_model=dict)
async def advance_stage(
    request_id: int,
    advance_data: AdvanceStage,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Advance a service request to the next workflow stage (Admin only)
    """
    # Get the request
    request = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service request not found"
        )
    
    # Check if already completed
    if request.current_stage == WorkflowStage.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request is already completed"
        )
    
    # Get next stage
    next_stage = STAGE_PROGRESSION.get(request.current_stage)
    if not next_stage:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot advance from current stage"
        )
    
    # Calculate duration in previous stage
    last_transition = db.query(StageTransition).filter(
        StageTransition.service_request_id == request_id,
        StageTransition.to_stage == request.current_stage
    ).order_by(StageTransition.transitioned_at.desc()).first()
    
    duration = None
    if last_transition:
        duration = (datetime.utcnow() - last_transition.transitioned_at).total_seconds() / 60  # minutes
    
    # Update request
    old_stage = request.current_stage
    request.current_stage = next_stage
    
    # Update status based on stage
    if next_stage == WorkflowStage.COMPLETED:
        request.status = RequestStatus.COMPLETED
        request.completed_at = datetime.utcnow()
    else:
        request.status = RequestStatus.IN_PROGRESS
    
    # Get handler workload
    handler_workload = 0
    if request.assigned_to:
        handler_workload = db.query(ServiceRequest).filter(
            ServiceRequest.assigned_to == request.assigned_to,
            ServiceRequest.status == RequestStatus.IN_PROGRESS
        ).count()
    
    # Create workflow log
    log = WorkflowLog(
        service_request_id=request.id,
        handler_id=current_user.id,
        stage=next_stage,
        action=f"Stage advanced from {old_stage.value} to {next_stage.value}",
        notes=advance_data.notes or f"Advanced by {current_user.full_name}",
        handler_workload=handler_workload,
        processing_duration=duration
    )
    db.add(log)
    
    # Create stage transition
    now = datetime.utcnow()
    transition = StageTransition(
        service_request_id=request.id,
        from_stage=old_stage,
        to_stage=next_stage,
        transition_duration=duration,
        handler_workload=handler_workload,
        time_of_day=now.hour,
        day_of_week=now.weekday(),
        transitioned_at=now
    )
    db.add(transition)
    
    db.commit()
    
    return {
        "message": f"Request {request.request_number} advanced to {next_stage.value}",
        "previous_stage": old_stage.value,
        "current_stage": next_stage.value,
        "duration_minutes": duration
    }


@router.post("/{request_id}/logs", response_model=WorkflowLogResponse, status_code=status.HTTP_201_CREATED)
async def add_workflow_log(
    request_id: int,
    log_data: WorkflowLogCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Add a custom workflow log entry (Admin only)
    """
    # Get the request
    request = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service request not found"
        )
    
    # Get handler workload
    handler_workload = db.query(ServiceRequest).filter(
        ServiceRequest.assigned_to == current_user.id,
        ServiceRequest.status == RequestStatus.IN_PROGRESS
    ).count()
    
    # Create log
    log = WorkflowLog(
        service_request_id=request.id,
        handler_id=current_user.id,
        stage=request.current_stage,
        action=log_data.action,
        notes=log_data.notes,
        handler_workload=handler_workload
    )
    
    db.add(log)
    db.commit()
    db.refresh(log)
    
    return log


@router.get("/{request_id}/logs", response_model=List[WorkflowLogWithHandler])
async def get_workflow_logs(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all workflow logs for a service request
    """
    # Get the request
    request = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service request not found"
        )
    
    # Authorization check
    if current_user.role == UserRole.STUDENT and request.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view these logs"
        )
    
    # Get logs
    logs = db.query(WorkflowLog).filter(
        WorkflowLog.service_request_id == request_id
    ).order_by(WorkflowLog.created_at.asc()).all()
    
    # Enrich with handler information
    enriched_logs = []
    for log in logs:
        log_dict = {
            "id": log.id,
            "service_request_id": log.service_request_id,
            "handler_id": log.handler_id,
            "stage": log.stage,
            "action": log.action,
            "notes": log.notes,
            "handler_workload": log.handler_workload,
            "processing_duration": log.processing_duration,
            "created_at": log.created_at,
            "handler_name": None,
            "handler_email": None
        }
        
        if log.handler_id:
            handler = db.query(User).filter(User.id == log.handler_id).first()
            if handler:
                log_dict["handler_name"] = handler.full_name
                log_dict["handler_email"] = handler.email
        
        enriched_logs.append(WorkflowLogWithHandler(**log_dict))
    
    return enriched_logs


@router.get("/{request_id}/transitions", response_model=List[StageTransitionResponse])
async def get_stage_transitions(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all stage transitions for a service request
    """
    # Get the request
    request = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service request not found"
        )
    
    # Authorization check
    if current_user.role == UserRole.STUDENT and request.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view these transitions"
        )
    
    # Get transitions
    transitions = db.query(StageTransition).filter(
        StageTransition.service_request_id == request_id
    ).order_by(StageTransition.transitioned_at.asc()).all()
    
    return transitions


@router.get("/{request_id}/timeline", response_model=WorkflowTimeline)
async def get_workflow_timeline(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get complete workflow timeline (logs + transitions) for a service request
    """
    # Get the request
    request = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service request not found"
        )
    
    # Authorization check
    if current_user.role == UserRole.STUDENT and request.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this timeline"
        )
    
    # Get logs with handler info
    logs = db.query(WorkflowLog).filter(
        WorkflowLog.service_request_id == request_id
    ).order_by(WorkflowLog.created_at.asc()).all()
    
    enriched_logs = []
    for log in logs:
        log_dict = {
            "id": log.id,
            "service_request_id": log.service_request_id,
            "handler_id": log.handler_id,
            "stage": log.stage,
            "action": log.action,
            "notes": log.notes,
            "handler_workload": log.handler_workload,
            "processing_duration": log.processing_duration,
            "created_at": log.created_at,
            "handler_name": None,
            "handler_email": None
        }
        
        if log.handler_id:
            handler = db.query(User).filter(User.id == log.handler_id).first()
            if handler:
                log_dict["handler_name"] = handler.full_name
                log_dict["handler_email"] = handler.email
        
        enriched_logs.append(WorkflowLogWithHandler(**log_dict))
    
    # Get transitions
    transitions = db.query(StageTransition).filter(
        StageTransition.service_request_id == request_id
    ).order_by(StageTransition.transitioned_at.asc()).all()
    
    return WorkflowTimeline(
        request_id=request.id,
        request_number=request.request_number,
        current_stage=request.current_stage,
        logs=enriched_logs,
        transitions=[StageTransitionResponse.from_orm(t) for t in transitions]
    )


@router.post("/{request_id}/reject", response_model=dict)
async def reject_request(
    request_id: int,
    rejection_notes: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Reject a service request (Admin only)
    """
    # Get the request
    request = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service request not found"
        )
    
    # Check if already completed or rejected
    if request.status in [RequestStatus.COMPLETED, RequestStatus.REJECTED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Request is already {request.status.value}"
        )
    
    # Update request
    request.status = RequestStatus.REJECTED
    request.completed_at = datetime.utcnow()
    
    # Create workflow log
    log = WorkflowLog(
        service_request_id=request.id,
        handler_id=current_user.id,
        stage=request.current_stage,
        action="Request rejected",
        notes=rejection_notes,
        handler_workload=0
    )
    db.add(log)
    
    db.commit()
    
    return {
        "message": f"Request {request.request_number} has been rejected",
        "status": request.status.value
    }
