# Setup Guide - Intelligent Workflow Automation System

Complete guide for setting up the development environment.

## Prerequisites

Before starting, ensure you have:

- **Python 3.9+** ([Download](https://www.python.org/downloads/))
- **Node.js 18+** ([Download](https://nodejs.org/))
- **PostgreSQL 14+** ([Download](https://www.postgresql.org/download/))
- **Git** ([Download](https://git-scm.com/downloads))
- **Docker Desktop** (Optional - [Download](https://www.docker.com/products/docker-desktop/))

---

## Method 1: Docker Setup (Recommended)

Fastest way to get started with all services containerized.

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd WorkFlow-Automation
```

### Step 2: Configure Environment

```bash
cd backend
cp .env.example .env
# Edit .env if needed (Docker defaults work out-of-box)
```

### Step 3: Start All Services

```bash
# From project root
docker-compose up -d
```

### Step 4: Run Migrations & Seed Data

```bash
# Access backend container
docker exec -it workflow_backend bash

# Run migrations
alembic upgrade head

# Seed database
python ../scripts/seed_data.py
```

### Step 5: Access Application

- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:5173 (Week 7+)

---

## Method 2: Local Setup

For development without Docker.

### Backend Setup

**1. Create PostgreSQL Database**

```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create database and user
CREATE DATABASE workflow_db;
CREATE USER workflow_user WITH PASSWORD 'workflow_pass';
GRANT ALL PRIVILEGES ON DATABASE workflow_db TO workflow_user;
\q
```

**2. Setup Python Environment**

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**3. Configure Environment**

```bash
cp .env.example .env
# Edit .env with your database credentials
```

**4. Initialize Database**

```bash
# Initialize Alembic (first time only)
alembic init alembic  # Skip if alembic/ already exists

# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

**5. Seed Database**

```bash
python ../scripts/seed_data.py
```

**6. Start Backend Server**

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup (Week 7)

**1. Install Dependencies**

```bash
cd frontend
npm install
```

**2. Configure Environment**

```bash
# Create .env.local
echo "VITE_API_URL=http://localhost:8000" > .env.local
```

**3. Start Development Server**

```bash
npm run dev
```

---

## Verification

### Test Backend Health

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "healthy",
  "database": "connected",
  "api": "operational",
  "ml_model": "not_loaded"
}
```

### Test API Documentation

Visit: http://localhost:8000/docs

You should see interactive Swagger UI with API endpoints.

### Test Database Connection

```bash
# Using psql
psql -U workflow_user -d workflow_db -h localhost

# List tables
\dt

# Expected tables:
# - users
# - service_requests
# - workflow_logs
# - stage_transitions
# - ml_predictions
# - alembic_version
```

---

## Testing Credentials

**Admin Account:**

- Email: admin@university.edu
- Password: Admin@123

**Student Account:**

- Email: alice.student@university.edu
- Password: Student@123

---

## Common Issues & Solutions

### Issue: Port 5432 Already in Use

**Solution**: Stop existing PostgreSQL or change port in docker-compose.yml

```bash
# Check what's using port
netstat -ano | findstr :5432  # Windows
lsof -i :5432                 # Mac/Linux

# Stop service or use different port
```

### Issue: Python Module Not Found

**Solution**: Ensure virtual environment is activated

```bash
# Check which Python
which python  # Should show venv path

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Alembic Migration Errors

**Solution**: Reset database and rerun migrations

```bash
# Drop all tables
psql -U workflow_user -d workflow_db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# Rerun migrations
alembic upgrade head
```

### Issue: Docker Container Won't Start

**Solution**: Check logs and rebuild

```bash
# View logs
docker-compose logs backend

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

---

## Development Workflow

### Making Database Changes

1. **Update model in** `backend/db/models.py`
2. **Create migration**:
   ```bash
   alembic revision --autogenerate -m "Description of change"
   ```
3. **Review migration** in `backend/alembic/versions/`
4. **Apply migration**:
   ```bash
   alembic upgrade head
   ```
5. **Rollback if needed**:
   ```bash
   alembic downgrade -1
   ```

### Testing API Changes

1. Start backend with `--reload` flag (auto-restart on changes)
2. Make code changes
3. Test in Swagger UI: http://localhost:8000/docs
4. Check logs in terminal

### Code Formatting

```bash
# Format Python code
black backend/

# Check linting
flake8 backend/
```

---

## Next Steps

- [ ] Complete Week 1 setup
- [ ] Verify all services running
- [ ] Test API endpoints in Swagger UI
- [ ] Proceed to Week 2: Authentication implementation

---

**Need Help?** Check project README.md or documentation in `docs/` folder.
