# Database Schema Documentation

## Entity Relationship Diagram (ERD)

### Core Entities

```
┌─────────────┐
│    User     │
├─────────────┤
│ id (PK)     │
│ email       │
│ username    │
│ password    │
│ full_name   │
│ role        │ ← ENUM: student, admin
│ is_active   │
│ created_at  │
└─────────────┘
       │
       │ 1:N (as student)
       │
       ▼
┌─────────────────────┐
│  ServiceRequest     │
├─────────────────────┤
│ id (PK)             │
│ request_number      │ ← REQ-2024-001
│ request_type        │ ← ENUM: certificate, hostel, it_support, library, exam, transcript
│ title               │
│ description         │
│ status              │ ← ENUM: pending, in_progress, completed, rejected
│ current_stage       │ ← ENUM: created, assigned, verified, approved, processed, completed
│ priority            │ ← 1=Low, 2=Medium, 3=High
│ student_id (FK)     │ → User.id
│ assigned_to (FK)    │ → User.id (admin)
│ created_at          │
│ assigned_at         │
│ completed_at        │
└─────────────────────┘
       │
       │ 1:N
       │
       ▼
┌─────────────────────┐
│   WorkflowLog       │
├─────────────────────┤
│ id (PK)             │
│ service_request_id  │ → ServiceRequest.id
│ handler_id (FK)     │ → User.id
│ stage               │
│ action              │
│ notes               │
│ handler_workload    │ ← Number of requests handler has
│ processing_duration │ ← Minutes in previous stage
│ created_at          │
└─────────────────────┘

       ▼
┌─────────────────────┐
│  StageTransition    │
├─────────────────────┤
│ id (PK)             │
│ service_request_id  │ → ServiceRequest.id
│ from_stage          │
│ to_stage            │
│ transition_duration │
│ handler_workload    │
│ time_of_day         │ ← 0-23 (hour)
│ day_of_week         │ ← 0=Monday, 6=Sunday
│ transitioned_at     │
└─────────────────────┘

       ▼
┌─────────────────────┐
│   MLPrediction      │
├─────────────────────┤
│ id (PK)             │
│ service_request_id  │ → ServiceRequest.id
│ prediction_type     │
│ predicted_label     │ ← "delayed" or "on_time"
│ confidence_score    │ ← 0.0 to 1.0
│ model_version       │
│ features_used       │
│ predicted_at        │
│ actual_label        │ ← Filled after completion
│ is_accurate         │ ← prediction == actual
└─────────────────────┘
```

## Table Descriptions

### 1. User

**Purpose**: Stores student and admin user accounts.

**Key Fields**:

- `role`: Differentiates students (submit requests) from admins (process requests)
- `is_active`: Soft delete mechanism

**Relationships**:

- One user can create many service requests (as student)
- One admin can be assigned to many service requests

---

### 2. ServiceRequest

**Purpose**: Core entity representing academic service requests.

**Key Fields**:

- `request_number`: Human-readable unique identifier (e.g., REQ-2024-001)
- `request_type`: Category of service (certificate, hostel, IT support, etc.)
- `current_stage`: Tracks request's position in workflow lifecycle
- `priority`: Used for queue management and urgency

**Workflow Stages**:

1. **Created** → Request submitted by student
2. **Assigned** → Assigned to admin handler
3. **Verified** → Admin verifies request validity
4. **Approved** → Management approval obtained
5. **Processed** → Request is being fulfilled
6. **Completed** → Request finalized and delivered

**Relationships**:

- Belongs to one student (creator)
- Assigned to one admin (processor)
- Has many workflow logs (audit trail)
- Has many stage transitions (for ML features)
- Has many ML predictions

---

### 3. WorkflowLog

**Purpose**: Detailed audit trail of all actions taken on a request.

**Key Fields**:

- `action`: Description of what happened (e.g., "Stage advanced to Verified")
- `handler_workload`: Snapshot of handler's total assigned requests at log time
- `processing_duration`: Time spent in previous stage (calculated feature for ML)

**ML Relevance**: Provides raw data for feature engineering.

---

### 4. StageTransition

**Purpose**: Optimized table for ML feature extraction and analytics.

**Key Fields**:

- `from_stage` → `to_stage`: Explicit transition tracking
- `transition_duration`: Time spent in `from_stage` before moving to `to_stage`
- `time_of_day`, `day_of_week`: Temporal features for ML model
- `handler_workload`: Contextual feature indicating system load

**ML Relevance**: Primary table for training delay prediction model.

---

### 5. MLPrediction

**Purpose**: Stores ML model predictions for analysis and retraining.

**Key Fields**:

- `predicted_label`: Binary classification result (delayed/on_time)
- `confidence_score`: Model's certainty (0.0 to 1.0)
- `model_version`: Tracks which model version made prediction
- `actual_label`: Ground truth filled after request completion
- `is_accurate`: For model performance monitoring

**ML Relevance**: Enables continuous model evaluation and feedback loop.

---

## Indexes

Performance-critical indexes:

```sql
-- User lookups
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- Request queries
CREATE INDEX idx_requests_student ON service_requests(student_id);
CREATE INDEX idx_requests_assigned ON service_requests(assigned_to);
CREATE INDEX idx_requests_stage ON service_requests(current_stage);
CREATE INDEX idx_requests_type ON service_requests(request_type);
CREATE INDEX idx_requests_created ON service_requests(created_at);

-- Workflow analytics
CREATE INDEX idx_logs_request ON workflow_logs(service_request_id);
CREATE INDEX idx_logs_created ON workflow_logs(created_at);

-- ML feature extraction
CREATE INDEX idx_transitions_request ON stage_transitions(service_request_id);
CREATE INDEX idx_transitions_time ON stage_transitions(transitioned_at);

-- Prediction queries
CREATE INDEX idx_predictions_request ON ml_predictions(service_request_id);
CREATE INDEX idx_predictions_time ON ml_predictions(predicted_at);
```

## Data Flow Example

**Scenario**: Student submits a certificate request

1. **User Authentication**

   - Student logs in → JWT token issued

2. **Request Creation**

   - POST /requests/create
   - Insert into `service_requests` (current_stage = "created")
   - Insert into `workflow_logs` (action = "Request created")
   - Insert into `stage_transitions` (from_stage = NULL, to_stage = "created")

3. **ML Prediction**

   - POST /predict/delay (internal call)
   - Extract features from request context
   - Run ML model inference
   - Insert into `ml_predictions` (predicted_label = "on_time", confidence = 0.85)

4. **Admin Assignment**

   - Admin views pending requests
   - PUT /requests/{id}/assign
   - Update `service_requests` (assigned_to = admin_id, current_stage = "assigned")
   - Insert into `workflow_logs` (action = "Request assigned to Admin X")
   - Insert into `stage_transitions` (from_stage = "created", to_stage = "assigned", duration = 15 mins)

5. **Stage Progression**

   - Admin advances through: Verified → Approved → Processed → Completed
   - Each transition creates entries in `workflow_logs` and `stage_transitions`

6. **Analytics Query**
   - GET /analytics/bottlenecks
   - Aggregates `stage_transitions` to find stages with longest avg duration
   - Joins with `ml_predictions` to correlate delays with predictions

---

## Constraints & Business Rules

1. **User Constraints**:

   - Email must be unique
   - Username must be unique
   - Password must be hashed (never store plaintext)

2. **Request Constraints**:

   - Student cannot assign requests to themselves
   - Only admins can advance workflow stages
   - Cannot skip stages (must follow: Created → Assigned → ... → Completed)
   - Cannot go backwards in workflow (no stage reversal)

3. **Workflow Rules**:

   - Every stage transition must be logged
   - Completed requests cannot be modified
   - Rejected requests terminate workflow

4. **ML Prediction Rules**:
   - Prediction generated at request creation and each stage transition
   - Confidence score must be between 0.0 and 1.0
   - Actual label filled only after request completion

---

## Sample Data Queries

### Get requests stuck in "Verified" stage for >3 days

```sql
SELECT r.id, r.request_number, r.request_type, r.current_stage,
       EXTRACT(EPOCH FROM (NOW() - st.transitioned_at))/3600 as hours_in_stage
FROM service_requests r
JOIN stage_transitions st ON r.id = st.service_request_id
WHERE r.current_stage = 'verified'
  AND st.to_stage = 'verified'
  AND st.transitioned_at < NOW() - INTERVAL '3 days'
ORDER BY hours_in_stage DESC;
```

### Admin workload distribution

```sql
SELECT u.full_name, u.email,
       COUNT(r.id) as assigned_requests,
       AVG(EXTRACT(EPOCH FROM (r.completed_at - r.assigned_at))/3600) as avg_completion_hours
FROM users u
LEFT JOIN service_requests r ON u.id = r.assigned_to
WHERE u.role = 'admin'
  AND r.status = 'completed'
GROUP BY u.id, u.full_name, u.email
ORDER BY assigned_requests DESC;
```

### ML Prediction accuracy

```sql
SELECT model_version,
       COUNT(*) as total_predictions,
       SUM(CASE WHEN is_accurate THEN 1 ELSE 0 END) as correct_predictions,
       ROUND(AVG(CASE WHEN is_accurate THEN 1 ELSE 0 END) * 100, 2) as accuracy_percentage
FROM ml_predictions
WHERE actual_label IS NOT NULL
GROUP BY model_version;
```

---

## Migration Strategy

Using Alembic for database migrations:

```bash
# Initialize Alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

**Status**: ✅ Schema designed and implemented (Week 1)  
**Next**: Setup Alembic migrations and seed data script
