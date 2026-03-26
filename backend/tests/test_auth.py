"""
Test Suite 1: Authentication Endpoints
Tests: /auth/register, /auth/login, /auth/me, /auth/users (admin-only)
"""

import pytest
from tests.conftest import (
    ADMIN_DATA, STUDENT_DATA,
    create_user_in_db, get_token, auth_headers,
)


class TestRegister:
    """POST /auth/register"""

    def test_register_student_success(self, client):
        """A new student can register with valid credentials."""
        resp = client.post("/auth/register", json={
            "email": "new@university.edu",
            "password": "Secure@123",
            "full_name": "New Student",
            "role": "student",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "new@university.edu"
        assert data["role"] == "student"
        assert "hashed_password" not in data  # password must never be exposed

    def test_register_duplicate_email_fails(self, client, db):
        """Registering with an already-used email returns 400."""
        create_user_in_db(db, STUDENT_DATA)
        resp = client.post("/auth/register", json={
            "email": STUDENT_DATA["email"],
            "password": "Another@123",
            "full_name": "Duplicate User",
            "role": "student",
        })
        assert resp.status_code == 400
        assert "already registered" in resp.json()["detail"].lower()

    def test_register_weak_password_fails(self, client):
        """Pydantic validator must reject a password missing uppercase letters."""
        resp = client.post("/auth/register", json={
            "email": "weak@university.edu",
            "password": "alllower1",   # no uppercase
            "full_name": "Weak Password",
            "role": "student",
        })
        assert resp.status_code == 422  # Unprocessable Entity

    def test_register_missing_field_fails(self, client):
        """Registering without a required field returns 422."""
        resp = client.post("/auth/register", json={
            "email": "incomplete@university.edu",
            # 'password' is missing
            "full_name": "Incomplete",
            "role": "student",
        })
        assert resp.status_code == 422


class TestLogin:
    """POST /auth/login"""

    def test_login_admin_success(self, client, db):
        """Admin can log in and receive a JWT token."""
        create_user_in_db(db, ADMIN_DATA)
        resp = client.post("/auth/login", data={
            "username": ADMIN_DATA["email"],
            "password": ADMIN_DATA["password"],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["role"] == "admin"

    def test_login_student_success(self, client, db):
        """Student can log in and receive a JWT token."""
        create_user_in_db(db, STUDENT_DATA)
        resp = client.post("/auth/login", data={
            "username": STUDENT_DATA["email"],
            "password": STUDENT_DATA["password"],
        })
        assert resp.status_code == 200
        assert resp.json()["user"]["role"] == "student"

    def test_login_wrong_password_fails(self, client, db):
        """Login with incorrect password returns 401."""
        create_user_in_db(db, STUDENT_DATA)
        resp = client.post("/auth/login", data={
            "username": STUDENT_DATA["email"],
            "password": "WrongPass@999",
        })
        assert resp.status_code == 401

    def test_login_nonexistent_user_fails(self, client):
        """Login with an email that doesn't exist returns 401."""
        resp = client.post("/auth/login", data={
            "username": "ghost@university.edu",
            "password": "Ghost@123",
        })
        assert resp.status_code == 401


class TestGetMe:
    """GET /auth/me"""

    def test_get_me_authenticated(self, client, db):
        """Authenticated user retrieves their own profile."""
        create_user_in_db(db, STUDENT_DATA)
        token = get_token(client, STUDENT_DATA["email"], STUDENT_DATA["password"])
        resp = client.get("/auth/me", headers=auth_headers(token))
        assert resp.status_code == 200
        assert resp.json()["email"] == STUDENT_DATA["email"]

    def test_get_me_unauthenticated(self, client):
        """Unauthenticated request to /auth/me returns 401."""
        resp = client.get("/auth/me")
        assert resp.status_code == 401


class TestAdminOnlyRoutes:
    """GET /auth/users — admin-only endpoint"""

    def test_admin_can_list_users(self, client, db):
        """Admin can list all users."""
        create_user_in_db(db, ADMIN_DATA)
        token = get_token(client, ADMIN_DATA["email"], ADMIN_DATA["password"])
        resp = client.get("/auth/users", headers=auth_headers(token))
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_student_cannot_list_users(self, client, db):
        """Student is forbidden from accessing the admin-only users list."""
        create_user_in_db(db, STUDENT_DATA)
        token = get_token(client, STUDENT_DATA["email"], STUDENT_DATA["password"])
        resp = client.get("/auth/users", headers=auth_headers(token))
        assert resp.status_code == 403
