"""
SQLAlchemy Database Models
Defines all database tables and relationships
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Boolean, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from db.database import Base


# Enums for type safety
class UserRole(str, enum.Enum):
    STUDENT = "student"
    ADMIN = "admin"


class RequestType(str, enum.Enum):
    CERTIFICATE = "certificate"
    HOSTEL = "hostel"
    IT_SUPPORT = "it_support"
    LIBRARY = "library"
    EXAM = "exam"
    TRANSCRIPT = "transcript"


class WorkflowStage(str, enum.Enum):
    CREATED = "created"
    ASSIGNED = "assigned"
    VERIFIED = "verified"
    APPROVED = "approved"
    PROCESSED = "processed"
    COMPLETED = "completed"


class RequestStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"


# Database Models

class User(Base):
    """User model for students and admins"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.STUDENT, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    service_requests = relationship("ServiceRequest", back_populates="student", foreign_keys="ServiceRequest.student_id")
    assigned_requests = relationship("ServiceRequest", back_populates="assigned_admin", foreign_keys="ServiceRequest.assigned_to")
    workflow_logs = relationship("WorkflowLog", back_populates="handler")


class ServiceRequest(Base):
    """Service request model - main entity for workflow tracking"""
    __tablename__ = "service_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    request_number = Column(String(50), unique=True, index=True, nullable=False)  # e.g., REQ-2024-001
    request_type = Column(Enum(RequestType), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(Enum(RequestStatus), default=RequestStatus.PENDING, nullable=False)
    current_stage = Column(Enum(WorkflowStage), default=WorkflowStage.CREATED, nullable=False, index=True)
    priority = Column(Integer, default=1)  # 1=Low, 2=Medium, 3=High
    
    # Relationships
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    assigned_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    student = relationship("User", back_populates="service_requests", foreign_keys=[student_id])
    assigned_admin = relationship("User", back_populates="assigned_requests", foreign_keys=[assigned_to])
    workflow_logs = relationship("WorkflowLog", back_populates="service_request")
    stage_transitions = relationship("StageTransition", back_populates="service_request")
    predictions = relationship("MLPrediction", back_populates="service_request")


class WorkflowLog(Base):
    """Detailed logging of all workflow activities"""
    __tablename__ = "workflow_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    service_request_id = Column(Integer, ForeignKey("service_requests.id"), nullable=False, index=True)
    handler_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Admin who performed action
    stage = Column(Enum(WorkflowStage), nullable=False)
    action = Column(String(255), nullable=False)  # e.g., "Stage advanced to Verified"
    notes = Column(Text, nullable=True)
    handler_workload = Column(Integer, default=0)  # Number of requests handler has at this moment
    processing_duration = Column(Float, nullable=True)  # Time spent in previous stage (minutes)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    service_request = relationship("ServiceRequest", back_populates="workflow_logs")
    handler = relationship("User", back_populates="workflow_logs")


class StageTransition(Base):
    """Tracks stage transitions for ML feature engineering"""
    __tablename__ = "stage_transitions"
    
    id = Column(Integer, primary_key=True, index=True)
    service_request_id = Column(Integer, ForeignKey("service_requests.id"), nullable=False, index=True)
    from_stage = Column(Enum(WorkflowStage), nullable=True)  # NULL for initial creation
    to_stage = Column(Enum(WorkflowStage), nullable=False)
    transition_duration = Column(Float, nullable=True)  # Minutes spent in from_stage
    handler_workload = Column(Integer, default=0)
    time_of_day = Column(Integer, nullable=False)  # 0-23 (hour)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    transitioned_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    service_request = relationship("ServiceRequest", back_populates="stage_transitions")


class MLPrediction(Base):
    """Stores ML prediction results for delay forecasting"""
    __tablename__ = "ml_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    service_request_id = Column(Integer, ForeignKey("service_requests.id"), nullable=False, index=True)
    prediction_type = Column(String(50), default="delay_classification")  # Type of prediction
    predicted_label = Column(String(50), nullable=False)  # "delayed" or "on_time"
    confidence_score = Column(Float, nullable=False)  # 0.0 to 1.0
    model_version = Column(String(50), nullable=False)  # e.g., "v1", "random_forest_v2"
    features_used = Column(Text, nullable=True)  # JSON string of features
    predicted_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Actual outcome (for model evaluation)
    actual_label = Column(String(50), nullable=True)  # Filled after request completion
    is_accurate = Column(Boolean, nullable=True)  # prediction == actual
    
    # Relationships
    service_request = relationship("ServiceRequest", back_populates="predictions")
