"""
Test Suite 3: Core Security Utilities & API Health
Tests: password hashing, JWT tokens, health endpoints
"""

import pytest
from datetime import timedelta

from core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token,
)


class TestPasswordHashing:
    """Unit tests for bcrypt password hashing utilities."""

    def test_hash_is_not_plaintext(self):
        """The hashed password must be different from the original."""
        plain = "Secure@123"
        hashed = get_password_hash(plain)
        assert hashed != plain

    def test_verify_correct_password(self):
        """verify_password returns True for the correct password."""
        plain = "Correct@Pass1"
        hashed = get_password_hash(plain)
        assert verify_password(plain, hashed) is True

    def test_verify_wrong_password(self):
        """verify_password returns False for an incorrect password."""
        hashed = get_password_hash("Correct@Pass1")
        assert verify_password("Wrong@Pass1", hashed) is False

    def test_two_hashes_differ(self):
        """Every bcrypt hash includes a random salt, so two hashes of the same
        password must always produce different strings (no rainbow tables)."""
        plain = "Same@Pass1"
        assert get_password_hash(plain) != get_password_hash(plain)


class TestJWTTokens:
    """Unit tests for JWT creation and decoding."""

    def test_create_and_decode_token(self):
        """A created token must decode back to the original payload."""
        payload = {"sub": "42", "role": "student"}
        token = create_access_token(data=payload)
        decoded = decode_access_token(token)
        assert decoded is not None
        assert decoded["sub"] == "42"
        assert decoded["role"] == "student"

    def test_expired_token_returns_none(self):
        """A token with a negative expiry (already expired) must return None."""
        payload = {"sub": "99", "role": "admin"}
        token = create_access_token(data=payload, expires_delta=timedelta(seconds=-1))
        decoded = decode_access_token(token)
        assert decoded is None

    def test_tampered_token_returns_none(self):
        """A modified token signature must be rejected and return None."""
        token = create_access_token(data={"sub": "1", "role": "student"})
        tampered = token[:-5] + "XXXXX"
        assert decode_access_token(tampered) is None

    def test_admin_role_in_token(self):
        """Token for an admin must contain role='admin'."""
        token = create_access_token(data={"sub": "1", "role": "admin"})
        decoded = decode_access_token(token)
        assert decoded["role"] == "admin"


class TestHealthEndpoints:
    """Integration tests for the public health check endpoints."""

    def test_root_endpoint_is_healthy(self, client):
        """GET / must return status=healthy with app metadata."""
        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "app" in data
        assert "version" in data

    def test_health_endpoint_returns_status(self, client):
        """GET /health must return database and API operational status."""
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "database" in data
        assert "api" in data

    def test_ml_model_health_endpoint(self, client):
        """GET /predict/health must return model status (public, no auth needed)."""
        resp = client.get("/predict/health")
        assert resp.status_code == 200
        data = resp.json()
        assert "model_loaded" in data
        assert "status" in data
