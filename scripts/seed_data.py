"""
Database Seed Script
Populates database with initial test data for development
"""

import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from passlib.context import CryptContext

from backend.db.database import SessionLocal, engine
from backend.db.models import (
    Base, User, ServiceRequest, WorkflowLog, StageTransition, MLPrediction,
    UserRole, RequestType, WorkflowStage, RequestStatus
)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def seed_users(db: Session):
    """Create initial users (students and admins)"""
    print("🌱 Seeding users...")
    
    users = [
        # Admins
        User(
            email="admin@university.edu",
            username="admin",
            hashed_password=hash_password("Admin@123"),
            full_name="System Administrator",
            role=UserRole.ADMIN,
            is_active=True
        ),
        User(
            email="john.admin@university.edu",
            username="john_admin",
            hashed_password=hash_password("Admin@123"),
            full_name="John Admin",
            role=UserRole.ADMIN,
            is_active=True
        ),
        User(
            email="sarah.admin@university.edu",
            username="sarah_admin",
            hashed_password=hash_password("Admin@123"),
            full_name="Sarah Admin",
            role=UserRole.ADMIN,
            is_active=True
        ),
        
        # Students
        User(
            email="alice.student@university.edu",
            username="alice_student",
            hashed_password=hash_password("Student@123"),
            full_name="Alice Johnson",
            role=UserRole.STUDENT,
            is_active=True
        ),
        User(
            email="bob.student@university.edu",
            username="bob_student",
            hashed_password=hash_password("Student@123"),
            full_name="Bob Smith",
            role=UserRole.STUDENT,
            is_active=True
        ),
        User(
            email="charlie.student@university.edu",
            username="charlie_student",
            hashed_password=hash_password("Student@123"),
            full_name="Charlie Brown",
            role=UserRole.STUDENT,
            is_active=True
        ),
        User(
            email="diana.student@university.edu",
            username="diana_student",
            hashed_password=hash_password("Student@123"),
            full_name="Diana Prince",
            role=UserRole.STUDENT,
            is_active=True
        ),
    ]
    
    db.add_all(users)
    db.commit()
    print(f"✅ Created {len(users)} users (3 admins, 4 students)")
    return users


def seed_service_requests(db: Session, users: list):
    """Create sample service requests"""
    print("🌱 Seeding service requests...")
    
    # Get students and admins
    students = [u for u in users if u.role == UserRole.STUDENT]
    admins = [u for u in users if u.role == UserRole.ADMIN]
    
    requests = []
    request_types = [RequestType.CERTIFICATE, RequestType.HOSTEL, RequestType.IT_SUPPORT, RequestType.LIBRARY]
    
    # Create 10 sample requests
    for i in range(1, 11):
        student = students[i % len(students)]
        request_type = request_types[i % len(request_types)]
        
        # Vary the stages for different requests
        if i <= 3:
            stage = WorkflowStage.CREATED
            status = RequestStatus.PENDING
            assigned_to = None
            assigned_at = None
        elif i <= 6:
            stage = WorkflowStage.ASSIGNED
            status = RequestStatus.IN_PROGRESS
            assigned_to = admins[i % len(admins)].id
            assigned_at = datetime.utcnow() - timedelta(hours=i)
        elif i <= 8:
            stage = WorkflowStage.VERIFIED
            status = RequestStatus.IN_PROGRESS
            assigned_to = admins[i % len(admins)].id
            assigned_at = datetime.utcnow() - timedelta(days=1)
        else:
            stage = WorkflowStage.COMPLETED
            status = RequestStatus.COMPLETED
            assigned_to = admins[i % len(admins)].id
            assigned_at = datetime.utcnow() - timedelta(days=3)
        
        request = ServiceRequest(
            request_number=f"REQ-2024-{i:03d}",
            request_type=request_type,
            title=f"{request_type.value.replace('_', ' ').title()} Request #{i}",
            description=f"Sample {request_type.value} request for testing purposes",
            status=status,
            current_stage=stage,
            priority=1 if i % 3 == 0 else 2,
            student_id=student.id,
            assigned_to=assigned_to,
            created_at=datetime.utcnow() - timedelta(days=i),
            assigned_at=assigned_at,
            completed_at=datetime.utcnow() if stage == WorkflowStage.COMPLETED else None
        )
        requests.append(request)
    
    db.add_all(requests)
    db.commit()
    print(f"✅ Created {len(requests)} service requests")
    return requests


def seed_workflow_logs(db: Session, requests: list, users: list):
    """Create workflow logs for service requests"""
    print("🌱 Seeding workflow logs...")
    
    admins = [u for u in users if u.role == UserRole.ADMIN]
    logs = []
    
    for request in requests:
        # Log creation
        logs.append(WorkflowLog(
            service_request_id=request.id,
            handler_id=None,
            stage=WorkflowStage.CREATED,
            action="Request created by student",
            notes="Initial request submission",
            handler_workload=0,
            processing_duration=None,
            created_at=request.created_at
        ))
        
        # Log assignment if assigned
        if request.assigned_to:
            logs.append(WorkflowLog(
                service_request_id=request.id,
                handler_id=request.assigned_to,
                stage=WorkflowStage.ASSIGNED,
                action=f"Request assigned to admin",
                notes="Assigned for processing",
                handler_workload=2,
                processing_duration=15.0,  # 15 minutes
                created_at=request.assigned_at
            ))
        
        # Log verification if in verified stage or beyond
        if request.current_stage in [WorkflowStage.VERIFIED, WorkflowStage.APPROVED, 
                                     WorkflowStage.PROCESSED, WorkflowStage.COMPLETED]:
            logs.append(WorkflowLog(
                service_request_id=request.id,
                handler_id=request.assigned_to,
                stage=WorkflowStage.VERIFIED,
                action="Request verified",
                notes="Documents verified and approved",
                handler_workload=3,
                processing_duration=30.0,
                created_at=request.assigned_at + timedelta(hours=1)
            ))
        
        # Log completion if completed
        if request.current_stage == WorkflowStage.COMPLETED:
            logs.append(WorkflowLog(
                service_request_id=request.id,
                handler_id=request.assigned_to,
                stage=WorkflowStage.COMPLETED,
                action="Request completed",
                notes="Request successfully processed and delivered",
                handler_workload=2,
                processing_duration=120.0,  # 2 hours
                created_at=request.completed_at
            ))
    
    db.add_all(logs)
    db.commit()
    print(f"✅ Created {len(logs)} workflow logs")


def seed_stage_transitions(db: Session, requests: list):
    """Create stage transitions for ML training"""
    print("🌱 Seeding stage transitions...")
    
    transitions = []
    
    for request in requests:
        created_time = request.created_at
        
        # Transition 1: NULL -> CREATED
        transitions.append(StageTransition(
            service_request_id=request.id,
            from_stage=None,
            to_stage=WorkflowStage.CREATED,
            transition_duration=None,
            handler_workload=0,
            time_of_day=created_time.hour,
            day_of_week=created_time.weekday(),
            transitioned_at=created_time
        ))
        
        # Transition 2: CREATED -> ASSIGNED (if assigned)
        if request.assigned_to:
            transitions.append(StageTransition(
                service_request_id=request.id,
                from_stage=WorkflowStage.CREATED,
                to_stage=WorkflowStage.ASSIGNED,
                transition_duration=15.0,
                handler_workload=2,
                time_of_day=request.assigned_at.hour,
                day_of_week=request.assigned_at.weekday(),
                transitioned_at=request.assigned_at
            ))
        
        # More transitions for advanced stages
        if request.current_stage in [WorkflowStage.VERIFIED, WorkflowStage.COMPLETED]:
            verified_time = request.assigned_at + timedelta(hours=1)
            transitions.append(StageTransition(
                service_request_id=request.id,
                from_stage=WorkflowStage.ASSIGNED,
                to_stage=WorkflowStage.VERIFIED,
                transition_duration=60.0,
                handler_workload=3,
                time_of_day=verified_time.hour,
                day_of_week=verified_time.weekday(),
                transitioned_at=verified_time
            ))
        
        if request.current_stage == WorkflowStage.COMPLETED:
            transitions.append(StageTransition(
                service_request_id=request.id,
                from_stage=WorkflowStage.VERIFIED,
                to_stage=WorkflowStage.COMPLETED,
                transition_duration=180.0,
                handler_workload=2,
                time_of_day=request.completed_at.hour,
                day_of_week=request.completed_at.weekday(),
                transitioned_at=request.completed_at
            ))
    
    db.add_all(transitions)
    db.commit()
    print(f"✅ Created {len(transitions)} stage transitions")


def main():
    """Main seed function"""
    print("\n" + "="*50)
    print("🌱 DATABASE SEEDING STARTED")
    print("="*50 + "\n")
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Create session
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_users = db.query(User).count()
        if existing_users > 0:
            print("⚠️  Database already contains data!")
            response = input("Do you want to clear and reseed? (yes/no): ")
            if response.lower() != 'yes':
                print("❌ Seeding cancelled")
                return
            
            # Clear existing data
            print("🗑️  Clearing existing data...")
            db.query(MLPrediction).delete()
            db.query(StageTransition).delete()
            db.query(WorkflowLog).delete()
            db.query(ServiceRequest).delete()
            db.query(User).delete()
            db.commit()
            print("✅ Existing data cleared")
        
        # Seed data
        users = seed_users(db)
        requests = seed_service_requests(db, users)
        seed_workflow_logs(db, requests, users)
        seed_stage_transitions(db, requests)
        
        print("\n" + "="*50)
        print("✅ DATABASE SEEDING COMPLETED SUCCESSFULLY!")
        print("="*50)
        print("\n📊 Summary:")
        print(f"   • Users: {db.query(User).count()}")
        print(f"   • Service Requests: {db.query(ServiceRequest).count()}")
        print(f"   • Workflow Logs: {db.query(WorkflowLog).count()}")
        print(f"   • Stage Transitions: {db.query(StageTransition).count()}")
        print("\n🔑 Login Credentials:")
        print("   Admin: admin@university.edu / Admin@123")
        print("   Student: alice.student@university.edu / Student@123")
        print()
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
