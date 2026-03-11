"""
Service Request API Endpoints
CRUD operations for service requests
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import datetime

from core.dependencies import get_db, get_current_user, require_admin
from db.models import User, ServiceRequest, WorkflowLog, StageTransition, UserRole, RequestStatus, WorkflowStage
from schemas.request import (
    ServiceRequestCreate,
    ServiceRequestUpdate,
    ServiceRequestResponse,
    ServiceRequestWithStudent,
    ServiceRequestList,
    RequestStatistics
)

router = APIRouter()


def generate_request_number(db: Session) -> str:
    """Generate unique request number"""
    last_request = db.query(ServiceRequest).order_by(ServiceRequest.id.desc()).first()
    if last_request:
        last_num = int(last_request.request_number.split('-')[-1])
        return f"REQ-2024-{last_num + 1:03d}"
    return "REQ-2024-001"


@router.post("/", response_model=ServiceRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_service_request(
    request_data: ServiceRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new service request (Student only)
    """
    # Only students can create requests
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can create service requests"
        )
    
    # Generate unique request number
    request_number = generate_request_number(db)
    
    # Create service request
    new_request = ServiceRequest(
        request_number=request_number,
        request_type=request_data.request_type,
        title=request_data.title,
        description=request_data.description,
        priority=request_data.priority,
        status=RequestStatus.PENDING,
        current_stage=WorkflowStage.CREATED,
        student_id=current_user.id
    )
    
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    
    # Create initial workflow log
    log = WorkflowLog(
        service_request_id=new_request.id,
        handler_id=None,
        stage=WorkflowStage.CREATED,
        action="Request created by student",
        notes=f"Request submitted: {request_data.title}",
        handler_workload=0
    )
    db.add(log)
    
    # Create initial stage transition
    now = datetime.utcnow()
    transition = StageTransition(
        service_request_id=new_request.id,
        from_stage=None,
        to_stage=WorkflowStage.CREATED,
        transition_duration=None,
        handler_workload=0,
        time_of_day=now.hour,
        day_of_week=now.weekday(),
        transitioned_at=now
    )
    db.add(transition)
    
    db.commit()
    
    return new_request


@router.get("/", response_model=List[ServiceRequestResponse])
async def list_service_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    status_filter: Optional[RequestStatus] = None,
    stage_filter: Optional[WorkflowStage] = None,
    type_filter: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """
    List service requests with filters
    - Students see only their own requests
    - Admins see all requests
    """
    query = db.query(ServiceRequest)
    
    # Role-based filtering
    if current_user.role == UserRole.STUDENT:
        query = query.filter(ServiceRequest.student_id == current_user.id)
    
    # Apply filters
    if status_filter:
        query = query.filter(ServiceRequest.status == status_filter)
    if stage_filter:
        query = query.filter(ServiceRequest.current_stage == stage_filter)
    if type_filter:
        query = query.filter(ServiceRequest.request_type == type_filter)
    
    # Order by created_at descending
    query = query.order_by(ServiceRequest.created_at.desc())
    
    # Pagination
    requests = query.offset(skip).limit(limit).all()
    
    return requests


@router.get("/statistics", response_model=RequestStatistics)
async def get_request_statistics(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get statistics about service requests (Admin only)
    """
    total = db.query(ServiceRequest).count()
    pending = db.query(ServiceRequest).filter(ServiceRequest.status == RequestStatus.PENDING).count()
    in_progress = db.query(ServiceRequest).filter(ServiceRequest.status == RequestStatus.IN_PROGRESS).count()
    completed = db.query(ServiceRequest).filter(ServiceRequest.status == RequestStatus.COMPLETED).count()
    rejected = db.query(ServiceRequest).filter(ServiceRequest.status == RequestStatus.REJECTED).count()
    
    # Count by stage
    by_stage = {}
    for stage in WorkflowStage:
        count = db.query(ServiceRequest).filter(ServiceRequest.current_stage == stage).count()
        by_stage[stage.value] = count
    
    # Count by type
    by_type = {}
    from db.models import RequestType
    for req_type in RequestType:
        count = db.query(ServiceRequest).filter(ServiceRequest.request_type == req_type).count()
        by_type[req_type.value] = count
    
    # Average completion time
    completed_requests = db.query(ServiceRequest).filter(
        ServiceRequest.status == RequestStatus.COMPLETED,
        ServiceRequest.completed_at.isnot(None)
    ).all()
    
    avg_completion_time = None
    if completed_requests:
        total_hours = sum(
            (req.completed_at - req.created_at).total_seconds() / 3600
            for req in completed_requests
        )
        avg_completion_time = total_hours / len(completed_requests)
    
    return RequestStatistics(
        total_requests=total,
        pending_requests=pending,
        in_progress_requests=in_progress,
        completed_requests=completed,
        rejected_requests=rejected,
        by_stage=by_stage,
        by_type=by_type,
        avg_completion_time_hours=avg_completion_time
    )


@router.get("/{request_id}", response_model=ServiceRequestResponse)
async def get_service_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific service request by ID
    """
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
            detail="Not authorized to view this request"
        )
    
    return request


@router.put("/{request_id}", response_model=ServiceRequestResponse)
async def update_service_request(
    request_id: int,
    update_data: ServiceRequestUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a service request
    - Students can update their own pending requests (title, description, priority)
    - Admins can update status
    """
    request = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service request not found"
        )
    
    # Authorization check
    if current_user.role == UserRole.STUDENT:
        if request.student_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this request"
            )
        if request.status != RequestStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only update pending requests"
            )
        # Students cannot update status
        if update_data.status is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Students cannot update request status"
            )
    
    # Apply updates
    if update_data.title is not None:
        request.title = update_data.title
    if update_data.description is not None:
        request.description = update_data.description
    if update_data.priority is not None:
        request.priority = update_data.priority
    if update_data.status is not None and current_user.role == UserRole.ADMIN:
        old_status = request.status
        request.status = update_data.status
        
        # Log status change
        log = WorkflowLog(
            service_request_id=request.id,
            handler_id=current_user.id,
            stage=request.current_stage,
            action=f"Status changed from {old_status.value} to {update_data.status.value}",
            notes="Status updated by admin",
            handler_workload=0
        )
        db.add(log)
    
    db.commit()
    db.refresh(request)
    
    return request


@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a service request
    - Students can delete their own pending requests
    - Admins can delete any request
    """
    request = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service request not found"
        )
    
    # Authorization check
    if current_user.role == UserRole.STUDENT:
        if request.student_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this request"
            )
        if request.status != RequestStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only delete pending requests"
            )
    
    db.delete(request)
    db.commit()
    
    return None
