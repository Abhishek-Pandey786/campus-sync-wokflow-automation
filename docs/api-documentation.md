# API Documentation
## CampusSync — Intelligent Workflow Automation System

**Base URL:** `http://localhost:8000`  
**Authentication:** Bearer JWT Token (OAuth2)  
**Content-Type:** `application/json`

---

## Authentication

All protected endpoints require the following HTTP header:

```
Authorization: Bearer <access_token>
```

Tokens are obtained from the `/auth/login` endpoint.

---

## 1. Authentication Routes `/auth`

### POST `/auth/register`
Register a new user account.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | ✅ | Valid university email address |
| `password` | string | ✅ | Min 8 chars, must include uppercase, lowercase, digit |
| `full_name` | string | ✅ | User's full name |
| `username` | string | ✅ | Unique username |
| `role` | string | ✅ | `"student"` or `"admin"` |

**Response:** `201 Created` — UserResponse object  
**Errors:** `400` Email/username already exists

---

### POST `/auth/login`
Login and receive a JWT access token.

> Uses OAuth2 `multipart/form-data` format (not JSON).

| Field | Type | Description |
|-------|------|-------------|
| `username` | string | Email or username |
| `password` | string | User password |

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "admin@university.edu",
    "full_name": "System Administrator",
    "role": "admin"
  }
}
```
**Errors:** `401` Invalid credentials, `403` Account inactive

---

### GET `/auth/me`
Get the currently authenticated user's profile.

🔒 **Auth Required**

**Response:** `200 OK` — UserResponse object

---

### PUT `/auth/me`
Update the current user's profile (full name or email).

🔒 **Auth Required**

| Field | Type | Description |
|-------|------|-------------|
| `full_name` | string | Optional — new full name |
| `email` | string | Optional — new email (must be unique) |

---

### POST `/auth/change-password`
Change the current user's password.

🔒 **Auth Required**

| Field | Type | Description |
|-------|------|-------------|
| `current_password` | string | Current password for verification |
| `new_password` | string | New strong password |

---

### GET `/auth/users`
List all registered users. 🔒 **Admin Only**

| Query Param | Default | Description |
|-------------|---------|-------------|
| `skip` | 0 | Pagination offset |
| `limit` | 100 | Max records to return |

---

### PUT `/auth/users/{user_id}/activate`
Activate a user account. 🔒 **Admin Only**

### PUT `/auth/users/{user_id}/deactivate`
Deactivate a user account. 🔒 **Admin Only** (Cannot deactivate self)

---

## 2. Service Request Routes `/requests`

### POST `/requests/`
Create a new service request. 🔒 **Student Only**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `request_type` | string | ✅ | One of: `certificate`, `hostel`, `it_support`, `library`, `exam`, `transcript` |
| `title` | string | ✅ | Brief title of the request |
| `description` | string | ✅ | Detailed description |
| `priority` | integer | ✅ | `1` (Low), `2` (Medium), `3` (High) |

**Response:** `201 Created` — ServiceRequestResponse with auto-generated request number (e.g., `REQ-2024-001`)

---

### GET `/requests/`
List service requests. 🔒 **Auth Required**

- **Students** see only their own requests
- **Admins** see all requests across all students

| Query Param | Type | Description |
|-------------|------|-------------|
| `status` | string | Filter by status (pending/in_progress/completed/rejected) |
| `request_type` | string | Filter by request type |
| `priority` | integer | Filter by priority (1/2/3) |
| `skip` | integer | Pagination offset |
| `limit` | integer | Max results (default: 50) |

---

### GET `/requests/{request_id}`
Get a single request by ID. 🔒 **Auth Required**

Students can only view their own requests. Admins can view any.

---

### PUT `/requests/{request_id}`
Update a service request. 🔒 **Auth Required**

Students can update their own pending requests. Admins can update any.

---

### DELETE `/requests/{request_id}`
Delete a request. 🔒 **Auth Required**

Students can delete their own pending requests only.

---

### GET `/requests/statistics/summary`
Get aggregated request statistics. 🔒 **Admin Only**

**Response:**
```json
{
  "total_requests": 120,
  "pending": 35,
  "in_progress": 42,
  "completed": 38,
  "rejected": 5,
  "by_type": { "certificate": 30, "hostel": 25, ... },
  "by_priority": { "1": 40, "2": 50, "3": 30 }
}
```

---

## 3. Workflow Routes `/workflows`

### POST `/workflows/{request_id}/assign`
Assign a request to the current admin. 🔒 **Admin Only**

Moves the request from `created` → `assigned` stage. Records the assigning admin's ID.

---

### POST `/workflows/{request_id}/advance`
Advance the request to the next workflow stage. 🔒 **Admin Only**

**Workflow Stages (in order):**
```
created → assigned → verified → approved → processed → completed
```

| Body Field | Type | Description |
|------------|------|-------------|
| `notes` | string | Optional notes for the stage transition |

Records exact time spent in the previous stage for analytics.

---

### POST `/workflows/{request_id}/reject`
Reject a service request. 🔒 **Admin Only**

| Query Param | Type | Required | Description |
|-------------|------|----------|-------------|
| `reason` | string | ✅ | Mandatory reason for rejection |

Sets request status to `rejected` and logs the reason.

---

### GET `/workflows/{request_id}/history`
Get the full workflow history for a request. 🔒 **Auth Required**

Returns a chronological log of all stage transitions with timestamps and admin notes.

---

## 4. ML Prediction Routes `/predict`

### POST `/predict/delay`
🔒 **Auth Required** — Predict delay probability for a hypothetical or live request using the trained ML model.

**Request Body:**
```json
{
  "request_type": "certificate",
  "priority": 1,
  "created_hour": 16,
  "created_day_of_week": 4,
  "handler_workload": 9,
  "stage_created_duration": 6,
  "stage_assigned_duration": 10,
  "stage_verified_duration": 15,
  "stage_approved_duration": 15,
  "stage_processed_duration": 22,
  "final_stage": "completed"
}
```

**Response:**
```json
{
  "prediction_score": 0.9625,
  "is_likely_delayed": true,
  "confidence": "high",
  "explanation": "This certificate request has a 96% delay probability...",
  "contributing_factors": [
    "Handler workload is critically high (9 concurrent requests)",
    "Submission on Friday — weekend effect reduces throughput"
  ],
  "recommendation": "Escalate to a senior administrator immediately...",
  "model_name": "LogisticRegression",
  "timestamp": "2026-03-25T15:30:00"
}
```

---

### GET `/predict/health`
Public endpoint — Get status of the loaded ML model.

**Response:**
```json
{
  "model_loaded": true,
  "model_type": "LogisticRegression",
  "feature_count": 19,
  "model_file": "backend/ml/models/best_model.pkl",
  "last_trained": "2026-02-28T10:55:16"
}
```

---

### POST `/predict/retrain`
Retrain the ML models with latest data. 🔒 **Admin Only**

Triggers the full training pipeline: data loading → feature engineering → 3-model comparison → save best model.

---

## 5. Alerts Routes `/alerts`

### GET `/alerts/`
Get requests currently flagged as high-risk by the ML model. 🔒 **Admin Only**

Returns all active requests with a predicted delay probability > 70%.

---

### GET `/alerts/summary`
Get a summary count of current high-risk alerts. 🔒 **Admin Only**

---

## SLA Reference Table

| Request Type | SLA Limit | Priority Impact |
|-------------|-----------|-----------------|
| `it_support` | 24 hours | High priority routes to senior tech |
| `hostel` | 48 hours | Accommodation office |
| `library` | 48 hours | Library services desk |
| `certificate` | 72 hours | Registrar's office |
| `exam` | 96 hours | Examination cell |
| `transcript` | 120 hours | Records department |

---

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| `200` | Success |
| `201` | Resource created |
| `400` | Bad request / validation error |
| `401` | Unauthenticated (missing/expired token) |
| `403` | Forbidden (insufficient role/permissions) |
| `404` | Resource not found |
| `422` | Unprocessable entity (body schema mismatch) |
| `503` | ML models not loaded (run training first) |
