# Deployment Guide
## CampusSync — Intelligent Workflow Automation System

---

## Prerequisites

Ensure the following are installed on the host machine:

| Tool | Minimum Version | Install Guide |
|------|----------------|---------------|
| Python | 3.11+ | [python.org](https://python.org) |
| Node.js | 18+ | [nodejs.org](https://nodejs.org) |
| npm | 9+ | Bundled with Node.js |
| Docker | 24+ | [docker.com](https://docker.com) (optional, for containerized deploy) |
| Docker Compose | v2+ | Bundled with Docker Desktop |

---

## Option A: Local Development (Recommended for Demo)

### 1. Clone / Open the Project

```powershell
cd "d:\Documents\Christ University\6th-Trimester\WorkFlow-Automation"
```

### 2. Backend Setup

```powershell
cd backend

# Create virtual environment
python -m venv ../.venv

# Activate virtual environment (Windows)
..\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Configure environment variables** — Edit `backend/.env`:
```env
SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=sqlite:///./workflow_test.db
ACCESS_TOKEN_EXPIRE_MINUTES=1440
GOOGLE_API_KEY=your-gemini-api-key     # Optional: for LLM explanations
```

**Initialize the database and seed data:**
```powershell
# From the backend directory (with venv active)
python -c "from db.database import Base, engine; Base.metadata.create_all(bind=engine)"
python ../scripts/seed_data.py
```

**Start the backend server:**
```powershell
python -m uvicorn main:app --reload --port 8000
```

The API will be available at: `http://localhost:8000`  
Interactive docs (Swagger UI): `http://localhost:8000/docs`

---

### 3. ML Model Setup

The pre-trained models are already saved in `backend/ml/models/`. No retraining is needed for a demo.

To retrain from scratch:
```powershell
# From project root (with venv active)
python scripts/generate_synthetic_data.py   # Regenerate dataset (optional)
python scripts/train_models.py              # Train and save all models
```

---

### 4. Frontend Setup

```powershell
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at: `http://localhost:5173`

---

### 5. Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | `admin@university.edu` | `Admin@123` |
| Student | Register a new account via the Student Portal on the login page |

---

## Option B: Docker Compose (Production-Style)

This deploys everything in containers using the included Docker setup.

### 1. Configure Environment

Create a `.env` file in the project root:
```env
SECRET_KEY=your-production-secret-key
GOOGLE_API_KEY=your-gemini-api-key
```

### 2. Build and Start Containers

```powershell
# From project root
docker-compose up --build
```

This starts:
- **Backend container** — FastAPI on port `8000`
- **Frontend container** — React served by Nginx on port `80`

### 3. Access the Application

| Service | URL |
|---------|-----|
| Frontend | `http://localhost` |
| Backend API | `http://localhost:8000` |
| API Docs | `http://localhost:8000/docs` |

### 4. Stop Containers

```powershell
docker-compose down
```

---

## Project File Structure (Reference)

```
WorkFlow-Automation/
│
├── backend/                    # FastAPI application
│   ├── main.py                 # App entry point, router registration
│   ├── requirements.txt        # Python dependencies
│   ├── .env                    # Environment config (not committed to git)
│   ├── workflow_test.db        # SQLite database (development)
│   ├── api/                    # Route handlers (auth, requests, workflows, predictions, alerts)
│   ├── core/                   # Security, config, dependencies
│   ├── db/                     # Database models, SQLAlchemy session
│   ├── schemas/                # Pydantic request/response models
│   ├── services/               # LLM, notifications, alerts services
│   └── ml/
│       ├── models/             # Serialized .pkl model files
│       └── training_report.txt # Model performance comparison
│
├── frontend/                   # React 18 + Vite application
│   ├── src/
│   │   ├── pages/              # 6 page components
│   │   ├── components/         # 5 reusable components
│   │   ├── api/                # Axios HTTP client layer
│   │   ├── context/            # AuthContext (JWT state)
│   │   └── index.css           # Global design system
│   ├── index.html
│   └── package.json
│
├── scripts/                    # Utility scripts
│   ├── generate_synthetic_data.py  # Creates training dataset
│   ├── train_models.py             # Trains & saves ML models
│   └── seed_data.py                # Seeds admin user + sample requests
│
├── data/
│   └── raw/
│       └── synthetic_requests.csv  # 1,201-row ML training dataset
│
├── notebooks/
│   └── model_comparison.ipynb  # Jupyter notebook: 5-model comparison
│
├── docker/
│   ├── Dockerfile.backend      # Python container config
│   ├── Dockerfile.frontend     # Node build → Nginx serve
│   └── nginx.conf              # Frontend static file server config
│
├── docs/                       # Project documentation
│   ├── api-documentation.md    # All 29 REST API endpoints
│   ├── ml-pipeline.md          # ML feature engineering & training
│   ├── user-guide.md           # Admin & Student user manuals
│   ├── deployment-guide.md     # This file
│   ├── database-schema.md      # Database table schemas
│   └── setup-guide.md          # Initial setup instructions
│
└── docker-compose.yml          # Multi-service orchestration
```

---

## Backend Dependencies (Key Packages)

```
fastapi            # REST API framework
uvicorn            # ASGI server
sqlalchemy         # ORM (database access)
pydantic           # Request/response validation
python-jose        # JWT token generation/validation
passlib[bcrypt]    # Password hashing
scikit-learn       # ML model training and inference
pandas             # Data manipulation
numpy              # Numerical computation
joblib             # Model serialization (.pkl files)
google-generativeai # Google Gemini LLM API
```

---

## Troubleshooting

### Backend won't start
- Ensure the virtual environment is activated: `..\.venv\Scripts\activate`
- Check that `backend/.env` exists with required variables
- Verify Python version: `python --version` (needs 3.11+)

### ML predictions return errors
- Check that all `.pkl` files exist in `backend/ml/models/`
- If missing, run: `python scripts/train_models.py` from the project root
- Verify with: `GET http://localhost:8000/predict/health`

### Frontend won't compile
- Run `npm install` in the `frontend/` directory to install missing packages
- Check Node.js version: `node --version` (needs 18+)
- Clear cache: `npm cache clean --force` then `npm install`

### Database errors
- Delete `backend/workflow_test.db` and re-run the seed script to reset from scratch
- Re-seed: `python scripts/seed_data.py` (from project root with venv active)

### Docker build failures
- Ensure Docker Desktop is running
- Try: `docker-compose down -v` then `docker-compose up --build`
