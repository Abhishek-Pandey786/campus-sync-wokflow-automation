# Docker Configurations

This directory contains Dockerfiles for containerizing the application.

## Files

- `Dockerfile.backend` - FastAPI backend container
- `Dockerfile.frontend` - React frontend container (Week 7)

## Usage

From the project root:

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild containers
docker-compose up -d --build
```

## Services

- **postgres**: PostgreSQL 15 database (port 5432)
- **backend**: FastAPI application (port 8000)
- **frontend**: React application (port 5173)

## Accessing Services

- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:5173
- PostgreSQL: localhost:5432

## Database Connection

Default credentials (change in production):

- User: workflow_user
- Password: workflow_pass
- Database: workflow_db
