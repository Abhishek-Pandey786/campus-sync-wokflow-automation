"""
Test Suite 2: Service Request CRUD Endpoints
Tests: POST/GET /requests/, GET /requests/{id}, statistics
"""

import pytest
from tests.conftest import (
    ADMIN_DATA, STUDENT_DATA,
    create_user_in_db, get_token, auth_headers,
)

SAMPLE_REQUEST = {
    "request_type": "certificate",
    "title": "Bonafide Certificate",
    "description": "Need bonafide certificate for bank account.",
    "priority": 2,
}


class TestCreateRequest:
    """POST /requests/"""

    def test_student_can_create_request(self, client, db):
        """Student creates a new service request and gets back a request number."""
        create_user_in_db(db, STUDENT_DATA)
        token = get_token(client, STUDENT_DATA["email"], STUDENT_DATA["password"])
        resp = client.post("/requests/", json=SAMPLE_REQUEST, headers=auth_headers(token))
        assert resp.status_code == 201
        data = resp.json()
        assert data["request_type"] == "certificate"
        assert data["request_number"].startswith("REQ-")
        assert data["priority"] == 2

    def test_admin_cannot_create_request(self, client, db):
        """Admins are not permitted to create student service requests."""
        create_user_in_db(db, ADMIN_DATA)
        token = get_token(client, ADMIN_DATA["email"], ADMIN_DATA["password"])
        resp = client.post("/requests/", json=SAMPLE_REQUEST, headers=auth_headers(token))
        assert resp.status_code == 403

    def test_unauthenticated_cannot_create_request(self, client):
        """Un-authenticated users cannot create requests."""
        resp = client.post("/requests/", json=SAMPLE_REQUEST)
        assert resp.status_code == 401

    def test_create_request_invalid_type_fails(self, client, db):
        """An invalid request_type value must be rejected with 422."""
        create_user_in_db(db, STUDENT_DATA)
        token = get_token(client, STUDENT_DATA["email"], STUDENT_DATA["password"])
        bad_request = {**SAMPLE_REQUEST, "request_type": "pizza"}  # not a valid type
        resp = client.post("/requests/", json=bad_request, headers=auth_headers(token))
        assert resp.status_code == 422


class TestListRequests:
    """GET /requests/"""

    def test_student_sees_only_own_requests(self, client, db):
        """A student's request list is scoped to their own submissions only."""
        # Create two different students
        create_user_in_db(db, STUDENT_DATA)
        create_user_in_db(db, {
            **ADMIN_DATA,
            "email": "other@university.edu",
            "role": "student",
            "username": "otherstudent",
        })

        token1 = get_token(client, STUDENT_DATA["email"], STUDENT_DATA["password"])
        # student1 submits a request
        client.post("/requests/", json=SAMPLE_REQUEST, headers=auth_headers(token1))

        # student2 should see an empty list
        token2 = get_token(client, "other@university.edu", ADMIN_DATA["password"])
        resp = client.get("/requests/", headers=auth_headers(token2))
        assert resp.status_code == 200
        assert len(resp.json()) == 0

    def test_admin_sees_all_requests(self, client, db):
        """Admin can see all requests across all students."""
        create_user_in_db(db, STUDENT_DATA)
        create_user_in_db(db, ADMIN_DATA)

        student_token = get_token(client, STUDENT_DATA["email"], STUDENT_DATA["password"])
        client.post("/requests/", json=SAMPLE_REQUEST, headers=auth_headers(student_token))

        admin_token = get_token(client, ADMIN_DATA["email"], ADMIN_DATA["password"])
        resp = client.get("/requests/", headers=auth_headers(admin_token))
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_unauthenticated_cannot_list_requests(self, client):
        """A request to /requests/ without a token returns 401."""
        resp = client.get("/requests/")
        assert resp.status_code == 401


class TestGetRequestById:
    """GET /requests/{request_id}"""

    def test_student_can_get_own_request(self, client, db):
        """Student can retrieve the details of their own request by ID."""
        create_user_in_db(db, STUDENT_DATA)
        token = get_token(client, STUDENT_DATA["email"], STUDENT_DATA["password"])
        created = client.post("/requests/", json=SAMPLE_REQUEST, headers=auth_headers(token)).json()
        request_id = created["id"]

        resp = client.get(f"/requests/{request_id}", headers=auth_headers(token))
        assert resp.status_code == 200
        assert resp.json()["id"] == request_id

    def test_get_nonexistent_request_returns_404(self, client, db):
        """Fetching a request ID that doesn't exist returns 404."""
        create_user_in_db(db, STUDENT_DATA)
        token = get_token(client, STUDENT_DATA["email"], STUDENT_DATA["password"])
        resp = client.get("/requests/99999", headers=auth_headers(token))
        assert resp.status_code == 404


class TestRequestStatistics:
    """GET /requests/statistics/summary"""

    def test_admin_can_get_statistics(self, client, db):
        """Admin can retrieve aggregated request statistics."""
        create_user_in_db(db, ADMIN_DATA)
        token = get_token(client, ADMIN_DATA["email"], ADMIN_DATA["password"])
        resp = client.get("/requests/statistics", headers=auth_headers(token))
        assert resp.status_code == 200
        data = resp.json()
        assert "total_requests" in data

    def test_student_cannot_get_statistics(self, client, db):
        """Students are blocked from accessing the statistics endpoint."""
        create_user_in_db(db, STUDENT_DATA)
        token = get_token(client, STUDENT_DATA["email"], STUDENT_DATA["password"])
        resp = client.get("/requests/statistics", headers=auth_headers(token))
        assert resp.status_code == 403
