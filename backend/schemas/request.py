"""
Service Request Pydantic Schemas
Request/Response models for service request operations
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

from db.models import RequestType, RequestStatus, WorkflowStage


# Base Request Schema
class ServiceRequestBase(BaseModel):
    """Base service request schema"""
    request_type: RequestType
    title: str = Field(..., min_length=5, max_length=255)
    description: Optional[str] = None
    priority: int = Field(default=1, ge=1, le=3)  # 1=Low, 2=Medium, 3=High


# Request Creation Schema
class ServiceRequestCreate(ServiceRequestBase):
    """Schema for creating a new service request"""
    pass


# Request Update Schema
class ServiceRequestUpdate(BaseModel):
    """Schema for updating a service request"""
    title: Optional[str] = Field(None, min_length=5, max_length=255)
    description: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=3)
    status: Optional[RequestStatus] = None


# Request Response Schema
class ServiceRequestResponse(ServiceRequestBase):
    """Schema for service request response"""
    id: int
    request_number: str
    status: RequestStatus
    current_stage: WorkflowStage
    student_id: int
    assigned_to: Optional[int] = None
    created_at: datetime
    assigned_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Request with Student Info
class ServiceRequestWithStudent(ServiceRequestResponse):
    """Service request response with student information"""
    student_name: Optional[str] = None
    student_email: Optional[str] = None
    assigned_admin_name: Optional[str] = None


# Request List Response
class ServiceRequestList(BaseModel):
    """Paginated list of service requests"""
    total: int
    page: int
    page_size: int
    requests: List[ServiceRequestResponse]


# Request Statistics
class RequestStatistics(BaseModel):
    """Statistics for service requests"""
    total_requests: int
    pending_requests: int
    in_progress_requests: int
    completed_requests: int
    rejected_requests: int
    by_stage: dict
    by_type: dict
    avg_completion_time_hours: Optional[float] = None
