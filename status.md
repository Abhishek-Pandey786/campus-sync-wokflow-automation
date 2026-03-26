# CampusSync — Project Status & Technical Report

> **CampusSync: Intelligent Workflow Automation & Delay Prediction System**
> Christ University · MCA 6th Trimester · 2026

---

## 1. Project Overview

**CampusSync** is a full-stack web application designed to automate and optimize the management of university service requests (certificates, hostel issues, IT support, library services, exams, transcripts). It uses **machine learning** to predict potential processing delays before they happen and provides **proactive alerts** to administrators. The system also integrates **Google Gemini LLM** to generate human-readable explanations for each delay prediction.

### Problem Statement
University administrative offices handle large volumes of service requests from students. These requests pass through multiple approval stages and are prone to delays due to factors like handler workload, time of submission, request priority, and day of the week. Without a predictive system, staff can only react to delays after they occur, leading to poor student satisfaction and SLA breaches.

### Solution
CampusSync provides:
1. **Automated multi-stage workflow tracking** across 6 stages (Created → Assigned → Verified → Approved → Processed → Completed)
2. **ML-powered delay prediction** using trained classification models (98.68% accuracy)
3. **LLM-generated explanations** via Google Gemini API for each prediction
4. **Proactive alert scanning** that identifies at-risk requests before SLA breaches
5. **Email notifications** (SMTP) to administrators when high-risk requests are detected
6. **Modern glassmorphism dashboard** for real-time monitoring and analytics

### Repository
- **GitHub**: https://github.com/Abhishek-Pandey786/campus-sync-wokflow-automation
- **License**: Academic / University Project

---

## 2. System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT (Browser)                        │
│  React 18 + Vite + Tailwind CSS + Lucide Icons + Recharts      │
│  Glassmorphism Dark Theme · Teal/Amber University Palette       │
└────────────────────────┬────────────────────────────────────────┘
                         │  HTTP/REST (JSON)
                         │  JWT Bearer Token Auth
┌────────────────────────▼────────────────────────────────────────┐
│                      FastAPI Backend (Python 3.11+)              │
│  ┌──────────┐ ┌───────────┐ ┌───────────┐ ┌─────────────────┐  │
│  │ Auth API │ │Requests   │ │Workflows  │ │ Predictions API │  │
│  │ (10 eps) │ │API (6 eps)│ │API (7 eps)│ │ (5 endpoints)   │  │
│  └──────────┘ └───────────┘ └───────────┘ └────────┬────────┘  │
│  ┌──────────┐                                      │           │
│  │Alerts API│ ← ─ ─ Alert Scanner Service ─ ─ ─ ─ ┘           │
│  │ (3 eps)  │                                                   │
│  └──────────┘                                                   │
│                                                                 │
│  ┌─────────────────────┐  ┌──────────────────────────────────┐  │
│  │ ML Prediction Engine│  │ Google Gemini LLM Service        │  │
│  │ scikit-learn models │  │ Explanation + Recommendation     │  │
│  │ (LogReg, RF, GB)    │  │ Generation via Gemini API        │  │
│  └─────────┬───────────┘  └──────────────────────────────────┘  │
│            │                                                    │
│  ┌─────────▼───────────┐  ┌──────────────────────────────────┐  │
│  │   SQLAlchemy ORM    │  │ SMTP Notification Service        │  │
│  │   5 Database Models │  │ Email alerts for high-risk reqs  │  │
│  └─────────┬───────────┘  └──────────────────────────────────┘  │
└────────────┼────────────────────────────────────────────────────┘
             │
┌────────────▼────────────┐
│  SQLite (dev) /         │
│  PostgreSQL (prod)      │
│  5 tables, relationships│
└─────────────────────────┘
```

### Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Frontend** | React | 18.x | Component-based UI framework |
| **Build Tool** | Vite | 5.4.x | Fast dev server and bundler |
| **Styling** | Tailwind CSS | 3.x | Utility-first CSS with custom design system |
| **Icons** | Lucide React | latest | SVG icon library (GraduationCap, Brain, etc.) |
| **Charts** | Recharts | latest | Data visualization (Bar, Pie charts) |
| **Backend** | FastAPI | latest | Async Python REST API framework |
| **ORM** | SQLAlchemy | latest | Database abstraction and relationships |
| **Auth** | JWT (python-jose) | — | Token-based authentication |
| **Password** | bcrypt (passlib) | — | Secure password hashing |
| **ML** | scikit-learn | latest | Classification models for delay prediction |
| **LLM** | Google Gemini (google-genai) | — | Natural language explanations |
| **Email** | smtplib / SMTP | — | Alert email notifications |
| **Database** | SQLite (dev) / PostgreSQL (prod) | — | Relational data storage |
| **Containerization** | Docker + Docker Compose | — | Deployment packaging |
| **Config** | Pydantic Settings | — | Environment variable validation |

---

## 3. Project Structure

```
CampusSync/
│
├── backend/                          # FastAPI Backend
│   ├── main.py                       # Application entry point, CORS, lifespan
│   ├── core/
│   │   └── config.py                 # Pydantic Settings (env vars)
│   ├── db/
│   │   ├── database.py               # SQLAlchemy engine + session
│   │   └── models.py                 # 5 ORM models (User, ServiceRequest, etc.)
│   ├── api/
│   │   ├── auth.py                   # 10 endpoints: register, login, me, users, etc.
│   │   ├── requests.py               # 6 endpoints: CRUD + statistics
│   │   ├── workflows.py              # 7 endpoints: assign, advance, reject, logs, timeline
│   │   ├── predictions.py            # 5 endpoints: predict, batch, retrain, model-info, health
│   │   └── alerts.py                 # 3 endpoints: list, scan, escalate
│   ├── services/
│   │   ├── alerts_service.py         # Background alert scanner logic
│   │   ├── llm_service.py            # Gemini LLM integration for explanations
│   │   └── notifications.py          # SMTP email notification service
│   └── ml/
│       ├── models/                   # Trained model files (.pkl)
│       │   ├── best_model.pkl        # Best performing model (Logistic Regression)
│       │   ├── logistic_regression.pkl
│       │   ├── random_forest.pkl
│       │   ├── gradient_boosting.pkl
│       │   ├── scaler.pkl            # Feature scaler
│       │   ├── feature_columns.pkl   # Feature column order
│       │   ├── label_encoder_type.pkl
│       │   └── label_encoder_stage.pkl
│       └── training_report.txt       # Model comparison results
│
├── frontend/                         # React + Vite Frontend
│   ├── index.html                    # Entry HTML with CampusSync branding
│   ├── vite.config.js                # Vite configuration
│   ├── tailwind.config.js            # Custom teal/amber design system
│   ├── package.json                  # Dependencies and scripts
│   └── src/
│       ├── main.jsx                  # React DOM entry
│       ├── App.jsx                   # Router + Layout with dot-grid background
│       ├── index.css                 # Glassmorphism design system (CSS)
│       ├── api/
│       │   ├── client.js             # Axios HTTP client with JWT interceptor
│       │   ├── auth.js               # Auth API calls
│       │   ├── requests.js           # Requests API calls
│       │   ├── workflows.js          # Workflow API calls
│       │   ├── predictions.js        # Predictions API calls
│       │   └── alerts.js             # Alerts API calls
│       ├── context/
│       │   └── AuthContext.jsx        # Global auth state (React Context)
│       ├── components/
│       │   ├── Navbar.jsx             # Glassmorphism navbar with GraduationCap
│       │   ├── ProtectedRoute.jsx     # Route guard for authenticated pages
│       │   ├── LoadingSpinner.jsx     # Reusable spinner + skeleton loader
│       │   ├── StatsCard.jsx          # Animated count-up stat cards
│       │   ├── RequestTable.jsx       # Service request table with icons
│       │   └── PredictionResult.jsx   # SVG gauge + AI explanation display
│       └── pages/
│           ├── LoginPage.jsx          # Login with rotating logo ring
│           ├── DashboardPage.jsx      # Main dashboard with stats + ML status
│           ├── RequestsPage.jsx       # Request list + detail drawer
│           ├── PredictionsPage.jsx    # ML prediction form + results
│           ├── AnalyticsPage.jsx      # Charts and data visualization
│           └── AlertsPage.jsx         # Risk alerts + escalation
│
├── scripts/
│   ├── generate_synthetic_data.py    # Generates 1,201 training records
│   ├── train_models.py               # Trains and compares ML models
│   ├── seed_data.py                  # Seeds database with sample requests
│   └── analyze_data.py               # Data analysis and EDA
│
├── data/
│   ├── raw/                          # Raw synthetic dataset (CSV)
│   ├── processed/                    # Feature-engineered data
│   └── exports/                      # Exported reports
│
├── notebooks/
│   └── *.ipynb                       # Jupyter notebooks for EDA and experiments
│
├── docker/
│   ├── Dockerfile.backend            # Backend container
│   ├── Dockerfile.frontend           # Frontend container (nginx)
│   └── nginx.conf                    # Nginx reverse proxy config
│
├── docker-compose.yml                # Multi-container orchestration
├── README.md                         # Project documentation
└── .gitignore                        # Git exclusion rules
```

---

## 4. Backend — API Endpoints (31 Total)

### 4.1 Authentication API (`/auth`) — 10 Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|:---:|
| POST | `/auth/register` | Register new user (student/admin) | ❌ |
| POST | `/auth/login` | Login → returns JWT access token | ❌ |
| GET | `/auth/me` | Get current user profile | ✅ |
| PUT | `/auth/me` | Update current user profile | ✅ |
| POST | `/auth/change-password` | Change password | ✅ |
| POST | `/auth/logout` | Logout (client-side token discard) | ✅ |
| GET | `/auth/users` | List all users (admin only) | ✅ Admin |
| GET | `/auth/users/{id}` | Get specific user | ✅ Admin |
| PUT | `/auth/users/{id}/activate` | Activate user account | ✅ Admin |
| PUT | `/auth/users/{id}/deactivate` | Deactivate user account | ✅ Admin |

### 4.2 Service Requests API (`/requests`) — 6 Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|:---:|
| POST | `/requests/` | Create new service request | ✅ |
| GET | `/requests/` | List requests (with filters) | ✅ |
| GET | `/requests/statistics` | Get request statistics | ✅ |
| GET | `/requests/{id}` | Get specific request | ✅ |
| PUT | `/requests/{id}` | Update request | ✅ |
| DELETE | `/requests/{id}` | Delete request | ✅ Admin |

### 4.3 Workflows API (`/workflows`) — 7 Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|:---:|
| POST | `/workflows/{id}/assign` | Assign request to admin | ✅ Admin |
| POST | `/workflows/{id}/advance` | Advance workflow stage | ✅ Admin |
| POST | `/workflows/{id}/reject` | Reject request | ✅ Admin |
| POST | `/workflows/{id}/logs` | Add workflow log entry | ✅ |
| GET | `/workflows/{id}/logs` | Get workflow logs | ✅ |
| GET | `/workflows/{id}/transitions` | Get stage transitions | ✅ |
| GET | `/workflows/{id}/timeline` | Get full workflow timeline | ✅ |

### 4.4 ML Predictions API (`/predict`) — 5 Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|:---:|
| POST | `/predict/delay` | Predict delay for a request | ✅ |
| POST | `/predict/batch` | Batch predictions | ✅ |
| POST | `/predict/retrain` | Retrain model with new data | ✅ Admin |
| GET | `/predict/model-info` | Get loaded model details | ✅ |
| GET | `/predict/health` | ML pipeline health check | ✅ |

### 4.5 Alerts API (`/alerts`) — 3 Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|:---:|
| GET | `/alerts` | List all active high-risk alerts | ✅ |
| POST | `/alerts/scan` | Trigger proactive risk scan | ✅ Admin |
| POST | `/alerts/{id}/escalate` | Escalate a flagged request | ✅ Admin |

### 4.6 Health Check Endpoints — 2 Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Basic API health check |
| GET | `/health` | Detailed health (DB, ML, API status) |

---

## 5. Database Schema (5 Tables)

### 5.1 Users Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer PK | Auto-increment primary key |
| email | String(255) | Unique email address |
| username | String(100) | Unique username |
| hashed_password | String(255) | bcrypt hashed password |
| full_name | String(255) | Display name |
| role | Enum(student, admin) | User role for RBAC |
| is_active | Boolean | Account status |
| created_at | DateTime | Account creation timestamp |
| updated_at | DateTime | Last update timestamp |

### 5.2 Service Requests Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer PK | Auto-increment primary key |
| request_number | String(50) | Unique identifier (e.g., REQ-2024-001) |
| request_type | Enum | certificate, hostel, it_support, library, exam, transcript |
| title | String(255) | Request title |
| description | Text | Detailed description |
| status | Enum | pending, in_progress, completed, rejected |
| current_stage | Enum | created, assigned, verified, approved, processed, completed |
| priority | Integer | 1=Low, 2=Medium, 3=High |
| student_id | FK → users.id | Requesting student |
| assigned_to | FK → users.id | Assigned admin (nullable) |
| created_at / assigned_at / completed_at / updated_at | DateTime | Lifecycle timestamps |

### 5.3 Workflow Logs Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer PK | Primary key |
| service_request_id | FK → service_requests.id | Related request |
| handler_id | FK → users.id | Admin who performed action |
| stage | Enum(WorkflowStage) | Stage at time of log |
| action | String(255) | Description (e.g., "Stage advanced to Verified") |
| notes | Text | Optional admin notes |
| handler_workload | Integer | Handler's concurrent request count |
| processing_duration | Float | Time spent in previous stage (minutes) |
| created_at | DateTime | Log timestamp |

### 5.4 Stage Transitions Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer PK | Primary key |
| service_request_id | FK | Related request |
| from_stage | Enum | Previous stage (NULL for creation) |
| to_stage | Enum | New stage |
| transition_duration | Float | Minutes spent in from_stage |
| handler_workload | Integer | Handler workload at transition |
| time_of_day | Integer(0-23) | Hour of transition |
| day_of_week | Integer(0-6) | Day of transition (0=Monday) |
| transitioned_at | DateTime | Transition timestamp |

### 5.5 ML Predictions Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer PK | Primary key |
| service_request_id | FK | Related request |
| prediction_type | String | "delay_classification" |
| predicted_label | String | "delayed" or "on_time" |
| confidence_score | Float(0-1) | Model confidence |
| model_version | String | e.g., "v1" |
| features_used | Text (JSON) | Feature values used |
| predicted_at | DateTime | Prediction timestamp |
| actual_label | String | Filled after completion (for evaluation) |
| is_accurate | Boolean | prediction == actual (for evaluation) |

---

## 6. Machine Learning Pipeline

### 6.1 Data Generation
- **Script**: `scripts/generate_synthetic_data.py`
- **Output**: `data/raw/synthetic_requests.csv`
- **Records**: 1,201 synthetic service requests
- **Distribution**: Realistic patterns for request types, priorities, submission times, handler workloads, and delay outcomes

### 6.2 Feature Engineering (19 Features)

| # | Feature | Type | Description |
|---|---------|------|-------------|
| 1 | request_type | Categorical (encoded) | Type of service request |
| 2 | priority | Integer (1-3) | Request priority level |
| 3 | created_hour | Integer (0-23) | Hour of request submission |
| 4 | created_day_of_week | Integer (0-6) | Day of submission |
| 5 | handler_workload | Integer | Number of concurrent requests being handled |
| 6 | stage_created_duration | Float | Hours spent in "Created" stage |
| 7 | stage_assigned_duration | Float | Hours spent in "Assigned" stage |
| 8 | stage_verified_duration | Float | Hours spent in "Verified" stage |
| 9 | stage_approved_duration | Float | Hours spent in "Approved" stage |
| 10 | stage_processed_duration | Float | Hours spent in "Processed" stage |
| 11 | total_duration | Float | Sum of all stage durations |
| 12 | max_stage_duration | Float | Longest individual stage |
| 13 | avg_stage_duration | Float | Average across stages |
| 14 | duration_variance | Float | Variance in stage durations |
| 15 | is_high_priority | Binary | priority == 3 |
| 16 | is_peak_hours | Binary | 9 AM – 5 PM submission |
| 17 | is_weekend | Binary | Saturday or Sunday submission |
| 18 | workload_x_priority | Float | Interaction: workload × priority |
| 19 | final_stage | Categorical (encoded) | Final workflow stage reached |

### 6.3 Models Trained and Compared

| Model | Accuracy | Precision | Recall | F1 Score | ROC-AUC |
|-------|:--------:|:---------:|:------:|:--------:|:-------:|
| **Logistic Regression** ⭐ | **98.68%** | **96.77%** | **98.36%** | **97.56%** | **99.95%** |
| Random Forest | 98.68% | 98.33% | 96.72% | 97.52% | 99.77% |
| Gradient Boosting | 98.25% | 98.31% | 95.08% | 96.67% | 95.73% |

**Selected Best Model**: Logistic Regression (based on highest F1 Score)

### 6.4 Model Artifacts
| File | Purpose |
|------|---------|
| `best_model.pkl` | Trained Logistic Regression classifier |
| `logistic_regression.pkl` | Individual LR model |
| `random_forest.pkl` | Individual RF model |
| `gradient_boosting.pkl` | Individual GB model |
| `scaler.pkl` | StandardScaler for feature normalization |
| `feature_columns.pkl` | Ordered list of 19 features |
| `label_encoder_type.pkl` | Encoder for request_type |
| `label_encoder_stage.pkl` | Encoder for final_stage |

### 6.5 Prediction Flow
```
User Input (form) → Feature Construction (19 features) → Scaler Transform
    → Model.predict_proba() → Probability Score (0.0 – 1.0)
    → Gemini LLM → Natural Language Explanation + Recommendation
    → Response to Frontend
```

---

## 7. Google Gemini LLM Integration

### Service: `backend/services/llm_service.py`

The LLM integration provides:
1. **Delay Explanation**: Natural language explanation of why a request might be delayed, citing specific feature values (e.g., "High handler workload of 8 combined with a low priority of 1 suggests processing will be deprioritized")
2. **Recommendation**: Actionable advice for administrators (e.g., "Consider reassigning to a less loaded handler or escalating priority")
3. **Contributing Factors**: Numbered list of the top factors driving the prediction

**Model used**: Google Gemini (via `google-genai` SDK)
**Fallback**: If Gemini API is unavailable, the system provides rule-based explanations

---

## 8. Alert & Notification System

### Service: `backend/services/alerts_service.py`

1. **Proactive Scan**: Admin triggers `/alerts/scan` → system scans all active (non-completed) requests
2. **Risk Scoring**: For each request, the ML model calculates delay probability
3. **Urgency Classification**:
   - **Critical** (≥80% risk): Red badge, pulse-glow animation
   - **High** (60-79%): Orange badge
   - **Medium** (40-59%): Amber badge
   - **Low** (<40%): Green badge
4. **SLA Tracking**: Hours remaining until SLA breach, with countdown display
5. **Email Notifications**: `backend/services/notifications.py` sends SMTP emails to admins for flagged requests
6. **Escalation**: Admins can escalate flagged requests with notes

---

## 9. Frontend — UI/UX Design

### Design System
- **Theme**: Dark glassmorphism with teal (#0d9488) primary and amber/gold (#f59e0b) accent
- **Background**: Gradient from slate-950 to teal-950 with subtle dot-grid pattern overlay
- **Cards**: Semi-transparent glass cards (`bg-white/[0.04]`, `backdrop-blur-xl`) with glowing teal borders on hover
- **Typography**: Inter font family (Google Fonts), 300–800 weight range
- **Iconography**: Lucide React SVG icons throughout (GraduationCap as brand logo)
- **Animations**: Fade-in, slide-up, count-up stats, pulse-glow on critical alerts, rotating dashed ring on login

### Pages (6 Total)

#### 9.1 Login Page
- Gradient background with animated floating teal/amber blobs
- Rotating dashed border ring around GraduationCap logo icon
- Glassmorphism login card with icon-prefixed inputs (Mail, Lock icons)
- Gradient "Sign In" button with loading spinner state
- Demo credentials display and "Christ University · MCA · CampusSync" footer

#### 9.2 Dashboard Page
- 4 animated stat cards (Total Requests, Delay Rate, Pending, Completed) with count-up animation
- API health indicator (green pulse dot) and ML model status
- ML Model Status card showing model type, 98.68% accuracy, F1 score, feature count
- Request Types breakdown with color-coded gradient progress bars

#### 9.3 Requests Page
- Glass filter bar with search input (Search icon), type dropdown, status dropdown, and reset button
- Request table with status icons, priority dot indicators, and hover row highlighting
- Animated slide-in detail drawer showing request metadata + workflow timeline
- Timeline with stage-specific Lucide icons and teal connecting line
- Pagination controls (Prev/Next)

#### 9.4 Predictions Page
- Quick preset buttons (Low Risk ✅, Medium Risk ⚠️, High Risk 🔺) with hover scale
- Two-column glass form: Request Details (left) + Stage Durations (right)
- Range sliders with teal-to-amber gradient tracks
- Real-time total duration calculation with gradient text
- PredictionResult component with animated SVG circular gauge, AI explanation card, numbered contributing factors, and recommendation card

#### 9.5 Analytics Page
- 4 summary badges with staggered entrance animations (Total, Delayed, Delay Rate, On-Time)
- 4 chart panels in 2×2 grid:
  - Requests by Type (teal bar chart)
  - Delay Rate by Type (amber bar chart)
  - Status Distribution (donut/pie chart, multi-color)
  - Delay by Priority Level (stacked bar: green on-time + red delayed)
- Glass chart wrappers with custom tooltip styling

#### 9.6 Alerts Page
- 4 urgency summary cards (Critical, High, Medium, Low) with appropriate colors
- Critical alerts have `animate-pulse-glow` effect
- Each alert card shows: request number, type, student name, current stage, SLA countdown, risk score bar
- Admin escalation inputs with "Escalate" button per alert
- Scan trigger button for admins
- Scan result and error notification banners

### Shared Components
| Component | Description |
|-----------|-------------|
| `Navbar.jsx` | Sticky glassmorphism header with GraduationCap logo, navigation links with teal-to-amber active indicator, user avatar + role, mobile hamburger menu |
| `LoadingSpinner.jsx` | Reusable animated spinner + SkeletonCard grid for loading states |
| `StatsCard.jsx` | Stat display with Lucide icon, count-up animation (requestAnimationFrame), gradient accent border, hover glow |
| `RequestTable.jsx` | Data table with status/priority icons, skeleton loading, empty state, row click handler |
| `PredictionResult.jsx` | SVG circular progress gauge, status badge, star confidence rating, AI explanation + contributing factors + recommendation |
| `ProtectedRoute.jsx` | Route guard that redirects to /login if not authenticated |

---

## 10. Authentication & Security

- **JWT Tokens**: Generated on login, 30-minute expiry, HS256 algorithm
- **Password Hashing**: bcrypt via passlib
- **Role-Based Access Control (RBAC)**:
  - `student`: Can create requests, view own requests, make predictions
  - `admin`: Full access — assign, advance, reject, scan alerts, escalate, manage users
- **Protected Routes**: Frontend uses `ProtectedRoute` component; backend uses `Depends(get_current_user)`
- **CORS**: Configured to allow frontend origins (`localhost:5173`, `localhost:3000`)
- **Environment Variables**: Secrets stored in `.env` (gitignored), loaded via Pydantic Settings

---

## 11. Deployment Setup

### Docker Configuration
- `docker/Dockerfile.backend`: Python 3.11-slim + pip install + uvicorn
- `docker/Dockerfile.frontend`: Node 18-alpine + npm build + nginx serve
- `docker/nginx.conf`: Reverse proxy for frontend → API
- `docker-compose.yml`: Multi-container orchestration (backend + frontend + optional PostgreSQL)

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | SQLite (dev) / PostgreSQL (prod) |
| `SECRET_KEY` | JWT signing secret | Must change in production |
| `GEMINI_API_KEY` | Google Gemini API key | Optional |
| `SMTP_HOST` | Email server | smtp.gmail.com |
| `SMTP_PORT` | Email port | 587 |
| `SMTP_USER` | Email sender address | Optional |
| `SMTP_PASSWORD` | Email app password | Optional |
| `EMAIL_ENABLED` | Enable email notifications | False |
| `DELAY_RISK_THRESHOLD` | Min probability to flag | 0.70 |
| `ADMIN_EMAIL` | Default admin account | admin@university.edu |
| `ADMIN_PASSWORD` | Default admin password | Admin@123 |

---

## 12. Scripts & Utilities

| Script | Purpose | Output |
|--------|---------|--------|
| `scripts/generate_synthetic_data.py` | Generates 1,201 realistic training records with delay labels | `data/raw/synthetic_requests.csv` |
| `scripts/train_models.py` | Trains 3 models, compares metrics, selects best, saves artifacts | `backend/ml/models/*.pkl` + `training_report.txt` |
| `scripts/seed_data.py` | Seeds database with sample users, requests, and workflow logs | Populated SQLite/PostgreSQL |
| `scripts/analyze_data.py` | Exploratory data analysis with statistics and distributions | Console output / plots |

---

## 13. Current Implementation Status

| Component | Status | Details |
|-----------|:------:|---------|
| Backend API (31 endpoints) | ✅ Complete | All 5 routers fully functional |
| Database Models (5 tables) | ✅ Complete | SQLAlchemy ORM with relationships |
| JWT Authentication + RBAC | ✅ Complete | Login, register, role-based access |
| ML Training Pipeline | ✅ Complete | 3 models trained, best selected (98.68%) |
| ML Prediction API | ✅ Complete | Real-time single + batch prediction |
| Gemini LLM Explanations | ✅ Complete | API integrated with fallback |
| Alert Scanner + Escalation | ✅ Complete | Proactive risk detection |
| Email Notifications (SMTP) | ✅ Complete | Admin alert emails |
| Synthetic Data Generation | ✅ Complete | 1,201 records |
| Frontend — Login Page | ✅ Complete | Glassmorphism + rotating ring |
| Frontend — Dashboard | ✅ Complete | Stats, ML status, breakdowns |
| Frontend — Requests Page | ✅ Complete | Table, filters, detail drawer |
| Frontend — Predictions Page | ✅ Complete | Form, presets, SVG gauge results |
| Frontend — Analytics Page | ✅ Complete | 4 charts, summary badges |
| Frontend — Alerts Page | ✅ Complete | Risk cards, escalation, scan |
| Frontend — CampusSync Branding | ✅ Complete | Teal/amber university palette |
| Docker Setup | ✅ Complete | Backend + Frontend Dockerfiles |
| API Documentation (Swagger) | ✅ Auto-generated | FastAPI /docs endpoint |

---

## 14. What a Full Production Deployment Would Include

### Currently Implemented (MVP)
Everything listed in Section 13 above — a fully functional system with ML predictions, LLM explanations, proactive alerts, and a polished UI.

### Future Enhancements for Production

#### 14.1 Testing & Quality
- Unit tests for all API endpoints (pytest)
- Integration tests for workflow stage transitions
- Frontend component tests (React Testing Library / Vitest)
- End-to-end tests (Playwright or Cypress)
- Load testing (Locust or k6)
- Test coverage reports (≥80% target)

#### 14.2 Advanced ML Features
- Model versioning and A/B testing
- Automated retraining pipeline (MLflow / scheduled jobs)
- Feature store for real-time feature serving
- Model drift detection and monitoring
- Additional models: SVM, MLP Neural Network, XGBoost
- SHAP values for model interpretability
- Time-series forecasting for workload prediction

#### 14.3 Frontend Enhancements
- Student-role specific views (my requests, track status)
- Real-time WebSocket notifications (push alerts)
- Request creation form for students
- Admin request assignment panel with drag-and-drop
- Mobile-first responsive improvements
- PWA (Progressive Web App) support
- Dark/light theme toggle
- i18n (internationalization) support

#### 14.4 Backend & Infrastructure
- PostgreSQL in production with connection pooling
- Redis caching for frequent queries
- Background task queue (Celery + Redis)
- API rate limiting
- Structured logging (JSON) with log aggregation (ELK stack)
- Health check endpoint enhancements (DB, Redis, ML, SMTP)
- Automated database migrations (Alembic)
- CI/CD pipeline (GitHub Actions)
- Kubernetes deployment with auto-scaling
- HTTPS with SSL/TLS certificates
- API versioning (v1, v2)

#### 14.5 Security Enhancements
- Refresh token rotation
- Password reset via email
- Two-factor authentication (2FA)
- Input validation and sanitization
- SQL injection prevention audit
- Rate limiting on auth endpoints
- Audit logging for all admin actions

#### 14.6 Analytics & Reporting
- Exportable PDF/Excel reports
- Custom date range filters
- Department-wise analytics
- SLA compliance dashboard
- Trend analysis and forecasting
- Real-time analytics with streaming data

---

## 15. How to Run the Project

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git

### Backend Setup
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
# Create .env file with required variables
python -m uvicorn main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:5173
```

### First-Time Data Setup
```bash
cd scripts
python generate_synthetic_data.py   # Generate training data
python train_models.py              # Train ML models
python seed_data.py                 # Seed database with sample data
```

### Default Login Credentials
- **Email**: admin@university.edu
- **Password**: Admin@123

---

## 16. Key Metrics Summary

| Metric | Value |
|--------|-------|
| Total Backend Endpoints | 31 |
| Database Tables | 5 |
| ML Models Trained | 3 |
| Best Model Accuracy | 98.68% |
| Best Model F1 Score | 97.56% |
| Best Model ROC-AUC | 99.95% |
| Engineered Features | 19 |
| Training Records | 1,201 |
| Frontend Pages | 6 |
| Shared Components | 6 |
| Request Types Supported | 6 |
| Workflow Stages | 6 |
| User Roles | 2 (student, admin) |

---

*Last updated: March 11, 2026*
*CampusSync v1.0.0 — Christ University MCA Program*
