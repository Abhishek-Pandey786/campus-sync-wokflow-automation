"""
pytest configuration & shared fixtures
All tests use an in-memory SQLite database so they never touch the production DB.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.database import Base
from db.models import User, UserRole
from core.security import get_password_hash
from core.dependencies import get_db

# ── In-memory test database ──────────────────────────────────────────────────
TEST_DATABASE_URL = "sqlite:///./test_temp.db"

engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Provide a clean test database session for every test."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Create all tables before each test; drop them after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db():
    """Yield a raw DB session for direct ORM operations in tests."""
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture(scope="function")
def client():
    """FastAPI TestClient with the production app wired to the test DB."""
    from main import app
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ── Reusable data helpers ─────────────────────────────────────────────────────

ADMIN_DATA = {
    "email": "admin@university.edu",
    "password": "Admin@123",
    "full_name": "Test Admin",
    "username": "testadmin",
    "role": "admin",
}

STUDENT_DATA = {
    "email": "student@university.edu",
    "password": "Student@123",
    "full_name": "Test Student",
    "username": "teststudent",
    "role": "student",
}


def create_user_in_db(db, data: dict):
    """Helper: directly INSERT a user into the test DB, bypassing the API."""
    user = User(
        email=data["email"],
        username=data.get("username", data["email"].split("@")[0]),
        hashed_password=get_password_hash(data["password"]),
        full_name=data["full_name"],
        role=UserRole.ADMIN if data.get("role") == "admin" else UserRole.STUDENT,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_token(client, email: str, password: str) -> str:
    """Helper: obtain a JWT token via the login endpoint."""
    resp = client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )
    assert resp.status_code == 200, f"Login failed: {resp.json()}"
    return resp.json()["access_token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
