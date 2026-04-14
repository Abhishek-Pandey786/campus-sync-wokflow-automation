# Intelligent Workflow Automation and Delay Prediction System

> **MCA Final Year Project** - Christ University  
> Full-Stack EdTech Application with Applied Machine Learning

## Project Overview

An intelligent academic service request management system that predicts workflow delays using Machine Learning, provides real-time analytics, and identifies bottlenecks in service processing workflows.

### Core Features

- **Workflow Automation**: Manage academic service requests (certificates, hostel, IT support, etc.) through defined stages
- **ML-Powered Delay Prediction**: Binary classification using Logistic Regression, Random Forest, Gradient Boosting, SVM, and Neural Network (MLP)
- **Analytics Dashboard**: Real-time insights on workload distribution, processing times, and bottlenecks
- **Proactive Alerts**: Automatically flag requests predicted to be delayed; email notifications + admin escalation
- **Role-Based Access**: Student and Admin interfaces with distinct capabilities

### Tech Stack

- **Frontend**: React 18 + Vite + Tailwind CSS
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **ML**: Python + scikit-learn (LR, RF, GB, SVM, MLP)
- **Visualization**: Recharts
- **Notifications**: SMTP email alerts (configurable)
- **Deployment**: Docker + Docker Compose (local)

## Project Structure

```
WorkFlow-Automation/
├── frontend/               # React 18 + Vite + Tailwind CSS
├── backend/                # FastAPI application
│   ├── api/               # Route handlers (auth, requests, workflows, predictions, alerts)
│   ├── core/              # Config, security, dependencies
│   ├── db/                # Database models and connections
│   ├── ml/                # ML models and pipelines
│   ├── schemas/           # Pydantic schemas
│   └── services/          # Business logic (notifications, alerts, LLM)
├── data/                   # Datasets (synthetic + real)
├── notebooks/              # Jupyter notebooks (model comparison)
├── scripts/                # Utility scripts
├── docs/                   # Documentation
└── docker/                 # Docker configurations
```

## 🚀 Quick Start

**Fast Track (5 minutes):**

```bash
# 1. Start backend
cd backend
python -m uvicorn main:app --reload --port 8000

# 2. Start frontend (new terminal)
cd frontend
npm install  # first time only
npm run dev
```

**Access:** http://localhost:8000/docs (API) | http://localhost:5173 (UI)

### Prerequisites

- Python 3.9+
- Node.js 18+ (Week 7+)
- PostgreSQL 14+
- Docker (optional, recommended)

### Test Credentials

- **Admin**: admin@university.edu / Admin@123
- **Student**: alice.student@university.edu / Student@123

---

## 📚 Documentation

| Document                                                             | Description                      |
| -------------------------------------------------------------------- | -------------------------------- |
| [docs/database-schema.md](docs/database-schema.md)                   | Database ERD & relationships     |
| [docs/setup-guide.md](docs/setup-guide.md)                           | Detailed setup instructions      |
| [backend/README.md](backend/README.md)                               | Backend architecture             |
| [frontend/README.md](frontend/README.md)                             | React frontend (Vite + Tailwind) |
| [notebooks/model_comparison.ipynb](notebooks/model_comparison.ipynb) | 5-model ML comparison notebook   |

---

## Development Roadmap

✅ Week 1: Database Foundation & FastAPI Setup  
✅ Week 2: User Management & Authentication  
✅ Week 3: Workflow Engine & Request Management  
✅ Week 4: Workflow Logging & Synthetic Data Generation  
✅ Week 5: ML Model Training Pipeline (98.68% accuracy)  
✅ Week 6: ML Prediction API + LLM Explanation (Gemini)  
✅ Week 7: React Frontend (Vite + Tailwind, 6 pages)  
✅ Week 8: Analytics Dashboard (Recharts, delay insights)  
✅ Week 9: Proactive Alerts, Email Notifications, Admin Escalation  
✅ Option A: SMTP Email Alerts + Model Retraining Endpoint  
✅ Option C: 5-Model Comparison (SVM + MLP added) + Jupyter Notebook  
⬜ Week 10: Testing & Documentation

## Key Differentiators

Unlike traditional student portals (CRUD-only systems), this project offers:

- **Predictive Analytics**: Forecast delays before they happen
- **Bottleneck Detection**: Identify congestion in workflow stages
- **Actionable Insights**: Data-driven recommendations for workflow optimization
- **Proactive Management**: Alert-based system with email notifications and admin escalation

## ML Model Details

**Task**: Binary Classification (Delayed vs On-time)

**Features**:

- Request type (categorical)
- Current workflow stage
- Time of day / Day of week
- Handler workload
- Historical processing duration per stage

**Models Evaluated**:

- Logistic Regression (baseline) — best_model.pkl
- Random Forest (ensemble)
- Gradient Boosting (boosted ensemble)
- Support Vector Machine — SVM (Option C)
- Neural Network / MLP (Option C)

**Best Model**: Logistic Regression (best F1 on synthetic data)

**Evaluation Metrics**:

- Precision, Recall, F1-score
- Confusion Matrix
- ROC-AUC Curve

See [notebooks/model_comparison.ipynb](notebooks/model_comparison.ipynb) for the full 5-model comparison with EDA, ROC curves, and feature importance plots.

---

## API Endpoints (29 total)

| Tag              | Count | Highlights                                                       |
| ---------------- | ----- | ---------------------------------------------------------------- |
| Authentication   | 10    | JWT login, register, refresh                                     |
| Service Requests | 6     | CRUD + status transitions                                        |
| Workflows        | 7     | Stage advance, logs, status                                      |
| ML Predictions   | 5     | `/predict/delay`, `/batch`, `/retrain`, `/model-info`, `/health` |
| Alerts           | 3     | `GET /alerts`, `POST /alerts/scan`, `POST /alerts/{id}/escalate` |
| Health           | 2     | `/`, `/health`                                                   |

---

## Contributing

This is an academic project. For issues or suggestions, please contact the project author.

## License

MIT License - Academic Project

## Author

**MCA Final Year Student**
Abhishek Pandey
Christ University  
Academic Year: 2025-2026

---

**Status**: Week 9 + Option A + Option C Complete ✅
