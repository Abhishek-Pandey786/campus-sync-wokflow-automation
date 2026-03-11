"""
Workflow Pydantic Schemas
Request/Response models for workflow operations
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from db.models import WorkflowStage


# Workflow Log Base Schema
class WorkflowLogBase(BaseModel):
    """Base workflow log schema"""
    action: str = Field(..., min_length=3, max_length=255)
    notes: Optional[str] = None


# Workflow Log Creation Schema
class WorkflowLogCreate(WorkflowLogBase):
    """Schema for creating a workflow log"""
    pass


# Workflow Log Response Schema
class WorkflowLogResponse(WorkflowLogBase):
    """Schema for workflow log response"""
    id: int
    service_request_id: int
    handler_id: Optional[int] = None
    stage: WorkflowStage
    handler_workload: int
    processing_duration: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Workflow Log with Handler Info
class WorkflowLogWithHandler(WorkflowLogResponse):
    """Workflow log response with handler information"""
    handler_name: Optional[str] = None
    handler_email: Optional[str] = None


# Request Assignment Schema
class AssignRequest(BaseModel):
    """Schema for assigning a request to an admin"""
    admin_id: int


# Stage Advancement Schema
class AdvanceStage(BaseModel):
    """Schema for advancing request to next stage"""
    notes: Optional[str] = None


# Stage Transition Response
class StageTransitionResponse(BaseModel):
    """Schema for stage transition response"""
    id: int
    service_request_id: int
    from_stage: Optional[WorkflowStage] = None
    to_stage: WorkflowStage
    transition_duration: Optional[float] = None
    handler_workload: int
    time_of_day: int
    day_of_week: int
    transitioned_at: datetime
    
    class Config:
        from_attributes = True


# Workflow Timeline Response
class WorkflowTimeline(BaseModel):
    """Complete timeline of a service request"""
    request_id: int
    request_number: str
    current_stage: WorkflowStage
    logs: List[WorkflowLogWithHandler]
    transitions: List[StageTransitionResponse]
