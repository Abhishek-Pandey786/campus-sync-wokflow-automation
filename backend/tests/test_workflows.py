"""
Test Suite 4: Workflow Pipeline Endpoints
Tests: assign, advance stage, reject, history (logs)

Actual route prefix: /workflows/{request_id}/...
- POST /workflows/{id}/assign   — body: {"admin_id": int}
- POST /workflows/{id}/advance  — body: {"notes": str | null}
- POST /workflows/{id}/reject   — query param: rejection_notes=str
- GET  /workflows/{id}/logs     — returns list of workflow logs
"""

import pytest
from tests.conftest import (
    ADMIN_DATA, STUDENT_DATA,
    create_user_in_db, get_token, auth_headers,
)

SAMPLE_REQUEST = {
    "request_type": "it_support",
    "title": "VPN not connecting",
    "description": "Unable to connect to university VPN from home.",
    "priority": 3,
}


def get_user_id(client, token: str) -> int:
    """Helper: get the logged-in user's ID via /auth/me."""
    resp = client.get("/auth/me", headers=auth_headers(token))
    assert resp.status_code == 200
    return resp.json()["id"]


def create_request_and_get_id(client, student_token: str) -> int:
    """Helper: create a request and return its ID."""
    resp = client.post("/requests/", json=SAMPLE_REQUEST, headers=auth_headers(student_token))
    assert resp.status_code == 201
    return resp.json()["id"]


class TestAssignWorkflow:
    """POST /workflows/{request_id}/assign  — body: {"admin_id": <int>}"""

    def test_admin_can_assign_request(self, client, db):
        """Admin successfully assigns a request to themselves."""
        create_user_in_db(db, STUDENT_DATA)
        create_user_in_db(db, ADMIN_DATA)
        stu_token = get_token(client, STUDENT_DATA["email"], STUDENT_DATA["password"])
        adm_token = get_token(client, ADMIN_DATA["email"], ADMIN_DATA["password"])

        request_id = create_request_and_get_id(client, stu_token)
        admin_id   = get_user_id(client, adm_token)

        resp = client.post(
            f"/workflows/{request_id}/assign",
            json={"admin_id": admin_id},
            headers=auth_headers(adm_token),
        )
        assert resp.status_code == 200
        assert "assigned_to" in resp.json()

    def test_student_cannot_assign_request(self, client, db):
        """Students are forbidden from assigning requests (admin-only endpoint)."""
        create_user_in_db(db, STUDENT_DATA)
        stu_token  = get_token(client, STUDENT_DATA["email"], STUDENT_DATA["password"])
        request_id = create_request_and_get_id(client, stu_token)
        student_id = get_user_id(client, stu_token)

        resp = client.post(
            f"/workflows/{request_id}/assign",
            json={"admin_id": student_id},
            headers=auth_headers(stu_token),
        )
        assert resp.status_code == 403

    def test_assign_nonexistent_request_fails(self, client, db):
        """Assigning a request that doesn't exist returns 404."""
        create_user_in_db(db, ADMIN_DATA)
        adm_token = get_token(client, ADMIN_DATA["email"], ADMIN_DATA["password"])
        admin_id  = get_user_id(client, adm_token)

        resp = client.post(
            "/workflows/99999/assign",
            json={"admin_id": admin_id},
            headers=auth_headers(adm_token),
        )
        assert resp.status_code == 404


class TestAdvanceStage:
    """POST /workflows/{request_id}/advance  — body: {"notes": str | null}"""

    def _setup_assigned_request(self, client, db):
        """Create a request and assign it, returning (request_id, adm_token)."""
        create_user_in_db(db, STUDENT_DATA)
        create_user_in_db(db, ADMIN_DATA)
        stu_token  = get_token(client, STUDENT_DATA["email"], STUDENT_DATA["password"])
        adm_token  = get_token(client, ADMIN_DATA["email"], ADMIN_DATA["password"])
        request_id = create_request_and_get_id(client, stu_token)
        admin_id   = get_user_id(client, adm_token)
        client.post(
            f"/workflows/{request_id}/assign",
            json={"admin_id": admin_id},
            headers=auth_headers(adm_token),
        )
        return request_id, adm_token, stu_token

    def test_admin_can_advance_stage(self, client, db):
        """Admin successfully advances an assigned request to the next stage."""
        request_id, adm_token, _ = self._setup_assigned_request(client, db)

        resp = client.post(
            f"/workflows/{request_id}/advance",
            json={"notes": "Verified — all documents in order"},
            headers=auth_headers(adm_token),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "current_stage" in data
        assert data["current_stage"] == "verified"

    def test_student_cannot_advance_stage(self, client, db):
        """Students cannot advance request stages."""
        request_id, adm_token, stu_token = self._setup_assigned_request(client, db)

        resp = client.post(
            f"/workflows/{request_id}/advance",
            json={"notes": "Student trying to self-approve"},
            headers=auth_headers(stu_token),
        )
        assert resp.status_code == 403


class TestRejectWorkflow:
    """POST /workflows/{request_id}/reject  — query param: rejection_notes=str"""

    def test_admin_can_reject_request(self, client, db):
        """Admin can reject a request with a mandatory reason."""
        create_user_in_db(db, STUDENT_DATA)
        create_user_in_db(db, ADMIN_DATA)
        stu_token  = get_token(client, STUDENT_DATA["email"], STUDENT_DATA["password"])
        adm_token  = get_token(client, ADMIN_DATA["email"], ADMIN_DATA["password"])
        request_id = create_request_and_get_id(client, stu_token)

        resp = client.post(
            f"/workflows/{request_id}/reject",
            params={"rejection_notes": "Duplicate submission — already handled"},
            headers=auth_headers(adm_token),
        )
        assert resp.status_code == 200

    def test_student_cannot_reject_request(self, client, db):
        """Students are not permitted to reject requests."""
        create_user_in_db(db, STUDENT_DATA)
        stu_token  = get_token(client, STUDENT_DATA["email"], STUDENT_DATA["password"])
        request_id = create_request_and_get_id(client, stu_token)

        resp = client.post(
            f"/workflows/{request_id}/reject",
            params={"rejection_notes": "I don't want this anymore"},
            headers=auth_headers(stu_token),
        )
        assert resp.status_code == 403


class TestWorkflowHistory:
    """GET /workflows/{request_id}/logs  — full workflow log list"""

    def test_logs_returned_after_assign(self, client, db):
        """After assigning a request, the logs endpoint returns at least one entry."""
        create_user_in_db(db, STUDENT_DATA)
        create_user_in_db(db, ADMIN_DATA)
        stu_token  = get_token(client, STUDENT_DATA["email"], STUDENT_DATA["password"])
        adm_token  = get_token(client, ADMIN_DATA["email"], ADMIN_DATA["password"])
        request_id = create_request_and_get_id(client, stu_token)
        admin_id   = get_user_id(client, adm_token)

        # Assign so that at least one log entry is created
        client.post(
            f"/workflows/{request_id}/assign",
            json={"admin_id": admin_id},
            headers=auth_headers(adm_token),
        )

        resp = client.get(f"/workflows/{request_id}/logs", headers=auth_headers(adm_token))
        assert resp.status_code == 200
        logs = resp.json()
        assert isinstance(logs, list)
        assert len(logs) >= 1
