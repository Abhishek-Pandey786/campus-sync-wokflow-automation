# Backend — FastAPI Application

## Directory Structure

```
backend/
├── main.py                # FastAPI app + CORS + router registration
├── config.py              # Settings (DB URL, JWT secret, SMTP config)
├── database.py            # SQLAlchemy engine + session factory
├── models.py              # ORM models (User, ServiceRequest, WorkflowStage, Alert)
├── schemas.py             # Pydantic request/response schemas
├── auth.py                # JWT token creation + verification
├── requirements.txt       # Python dependencies
│
├── api/                   # Route handlers (29 endpoints)
│   ├── auth.py            # POST /register, POST /login, GET /me, etc. (Week 2)
│   ├── requests.py        # CRUD for service requests (Week 3)
│   ├── workflows.py       # Stage transitions + history (Week 3)
│   ├── predictions.py     # ML predict + retrain + LLM explain (Week 6)
│   └── alerts.py          # Proactive alerts: scan, list, escalate (Week 9)
│
└── services/              # Business logic layer
    ├── notifications.py   # SMTP email notifications (Option A)
    ├── alerts_service.py  # Alert scanning engine (Week 9)
    └── llm_service.py     # Google Gemini LLM explanations (Week 6)
```

## Setup

1. **Create virtual environment**:

   ```bash
   python -m venv venv
   venv\Scripts\activate   # Windows
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Start server**:
   ```bash
   cd backend
   python main.py
   ```

## API Documentation

Once running, visit:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints Summary

| Category    | Count | Prefix         |
| ----------- | ----- | -------------- |
| Auth        | 10    | /api/auth      |
| Requests    | 6     | /api/requests  |
| Workflows   | 7     | /api/workflows |
| Predictions | 5     | /api/predict   |
| Alerts      | 3     | /api/alerts    |
| Health      | 2     | /              |

## Current Status

✅ Authentication + JWT (Week 2)  
✅ Request management (Week 3)  
✅ Workflow state machine (Week 3)  
✅ ML pipeline — 5 models, 98.68% accuracy (Weeks 5–7)  
✅ LLM integration — Google Gemini (Week 6)  
✅ Analytics endpoints (Week 8)  
✅ Proactive alerts + email notifications (Week 9 + Option A)
