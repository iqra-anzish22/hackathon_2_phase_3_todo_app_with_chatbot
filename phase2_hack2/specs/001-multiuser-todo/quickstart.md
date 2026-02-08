# Quickstart Guide: Multi-User Todo Web Application

**Feature**: 001-multiuser-todo
**Date**: 2026-02-04
**Purpose**: Setup and run instructions for local development

## Overview

This guide provides step-by-step instructions to set up and run the Multi-User Todo Web Application locally. The application consists of two independent services: a Next.js frontend and a FastAPI backend.

**Prerequisites**:
- Node.js 18+ and npm/yarn
- Python 3.11+
- Neon PostgreSQL account (free tier available)
- Git

---

## Architecture Overview

```
┌─────────────────┐         HTTP/REST API        ┌─────────────────┐
│                 │    (JWT Authentication)      │                 │
│  Next.js        │◄────────────────────────────►│  FastAPI        │
│  Frontend       │                              │  Backend        │
│  (Port 3000)    │                              │  (Port 8000)    │
│                 │                              │                 │
│  - Better Auth  │                              │  - JWT Verify   │
│  - UI/UX        │                              │  - SQLModel     │
│  - API Client   │                              │  - Business     │
└─────────────────┘                              └────────┬────────┘
                                                          │
                                                          │
                                                          ▼
                                                 ┌─────────────────┐
                                                 │  Neon           │
                                                 │  PostgreSQL     │
                                                 │  (Cloud)        │
                                                 └─────────────────┘
```

---

## Part 1: Database Setup (Neon PostgreSQL)

### Step 1: Create Neon Account

1. Visit [https://neon.tech](https://neon.tech)
2. Sign up for a free account
3. Create a new project named "multiuser-todo"

### Step 2: Get Connection String

1. In Neon dashboard, navigate to your project
2. Click "Connection Details"
3. Copy the connection string (format: `postgresql://user:pass@host/db`)
4. Save this for backend configuration

**Example Connection String**:
```
postgresql://user:password@ep-cool-name-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
```

### Step 3: Verify Connection

```bash
# Test connection using psql (optional)
psql "postgresql://user:password@host/db?sslmode=require"
```

---

## Part 2: Backend Setup (FastAPI)

### Step 1: Navigate to Backend Directory

```bash
cd backend
```

### Step 2: Create Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**requirements.txt** (create if not exists):
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlmodel==0.0.14
psycopg2-binary==2.9.9
python-jose[cryptography]==3.3.0
python-dotenv==1.0.0
pydantic==2.5.3
pydantic-settings==2.1.0
alembic==1.13.1
```

### Step 4: Configure Environment Variables

Create `.env` file in `backend/` directory:

```bash
# Copy example file
cp .env.example .env

# Edit .env with your values
```

**backend/.env**:
```
# Shared secret (MUST match frontend)
BETTER_AUTH_SECRET=your-secret-key-min-32-chars-here

# Neon PostgreSQL connection
DATABASE_URL=postgresql+asyncpg://user:password@host/db?sslmode=require

# Application settings
DEBUG=true
ENVIRONMENT=development

# CORS settings
CORS_ORIGINS=http://localhost:3000
```

**Generate Secure Secret**:
```bash
# Generate random 32-character secret
openssl rand -base64 32
```

### Step 5: Initialize Database

```bash
# Run database migrations
alembic upgrade head

# Or if migrations not set up yet, create tables directly
python -c "from src.core.database import init_db; import asyncio; asyncio.run(init_db())"
```

### Step 6: Run Backend Server

```bash
# Start FastAPI server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 7: Verify Backend

Open browser and navigate to:
- API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Check: [http://localhost:8000/health](http://localhost:8000/health) (if implemented)

---

## Part 3: Frontend Setup (Next.js)

### Step 1: Navigate to Frontend Directory

```bash
# Open new terminal
cd frontend
```

### Step 2: Install Dependencies

```bash
# Using npm
npm install

# Or using yarn
yarn install
```

**package.json** (key dependencies):
```json
{
  "dependencies": {
    "next": "^15.0.0",
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "better-auth": "^1.0.0",
    "typescript": "^5.3.0"
  }
}
```

### Step 3: Configure Environment Variables

Create `.env.local` file in `frontend/` directory:

```bash
# Copy example file
cp .env.local.example .env.local

# Edit .env.local with your values
```

**frontend/.env.local**:
```
# Shared secret (MUST match backend)
BETTER_AUTH_SECRET=your-secret-key-min-32-chars-here

# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth configuration
BETTER_AUTH_URL=http://localhost:3000
```

**Important**: Use the SAME `BETTER_AUTH_SECRET` as backend!

### Step 4: Run Frontend Server

```bash
# Start Next.js development server
npm run dev

# Or with yarn
yarn dev
```

**Expected Output**:
```
  ▲ Next.js 15.0.0
  - Local:        http://localhost:3000
  - Network:      http://192.168.1.x:3000

 ✓ Ready in 2.5s
```

### Step 5: Verify Frontend

Open browser and navigate to:
- Home: [http://localhost:3000](http://localhost:3000)
- Sign Up: [http://localhost:3000/signup](http://localhost:3000/signup)
- Sign In: [http://localhost:3000/signin](http://localhost:3000/signin)

---

## Part 4: End-to-End Testing

### Test 1: User Registration

1. Navigate to [http://localhost:3000/signup](http://localhost:3000/signup)
2. Enter email and password
3. Submit form
4. Verify redirect to tasks page
5. Check browser cookies for `auth-token`

### Test 2: Task Creation

1. On tasks page, enter task title
2. Optionally add description
3. Submit form
4. Verify task appears in list
5. Check browser DevTools Network tab for API call to `POST /api/tasks`

### Test 3: Task Operations

1. **View**: Click on task to see details
2. **Edit**: Update task title or description
3. **Complete**: Toggle completion checkbox
4. **Delete**: Click delete button

### Test 4: Multi-User Isolation

1. Open incognito/private browser window
2. Sign up with different email
3. Create tasks in second account
4. Verify tasks from first account are NOT visible
5. Verify API returns only current user's tasks

### Test 5: Authentication

1. Sign out from application
2. Try to access [http://localhost:3000/tasks](http://localhost:3000/tasks)
3. Verify redirect to sign-in page
4. Sign in again
5. Verify redirect back to tasks page

---

## Part 5: Troubleshooting

### Backend Issues

**Issue**: `ModuleNotFoundError: No module named 'fastapi'`
- **Solution**: Activate virtual environment and reinstall dependencies
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

**Issue**: `sqlalchemy.exc.OperationalError: could not connect to server`
- **Solution**: Verify DATABASE_URL in .env is correct
- Check Neon dashboard for correct connection string
- Ensure `?sslmode=require` is appended

**Issue**: `401 Unauthorized` on all API requests
- **Solution**: Verify BETTER_AUTH_SECRET matches in both .env files
- Check JWT token is being sent in Authorization header
- Verify token is not expired

### Frontend Issues

**Issue**: `Error: Cannot find module 'better-auth'`
- **Solution**: Install dependencies
```bash
npm install
```

**Issue**: `CORS error` when calling API
- **Solution**: Verify backend CORS_ORIGINS includes `http://localhost:3000`
- Check backend is running on port 8000

**Issue**: Redirect loop between signin and tasks
- **Solution**: Clear browser cookies
- Check Better Auth configuration
- Verify middleware.ts is correctly configured

### Database Issues

**Issue**: `relation "tasks" does not exist`
- **Solution**: Run database migrations
```bash
cd backend
alembic upgrade head
```

**Issue**: Connection timeout to Neon
- **Solution**: Check internet connection
- Verify Neon project is active (not suspended)
- Check firewall settings

---

## Part 6: Development Workflow

### Running Both Services

**Terminal 1 (Backend)**:
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate
uvicorn src.main:app --reload --port 8000
```

**Terminal 2 (Frontend)**:
```bash
cd frontend
npm run dev
```

### Making Changes

**Backend Changes**:
- Edit files in `backend/src/`
- FastAPI auto-reloads on file changes
- Check terminal for errors

**Frontend Changes**:
- Edit files in `frontend/src/`
- Next.js auto-reloads on file changes
- Check browser console for errors

### Database Changes

```bash
# Create new migration
cd backend
alembic revision --autogenerate -m "Description of change"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

---

## Part 7: Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v
```

### Frontend Tests

```bash
cd frontend
npm run test
```

### Manual Testing Checklist

- [ ] User can sign up with email/password
- [ ] User can sign in with credentials
- [ ] User can create task with title only
- [ ] User can create task with title and description
- [ ] User can view list of their tasks
- [ ] User can view individual task details
- [ ] User can update task title
- [ ] User can update task description
- [ ] User can toggle task completion
- [ ] User can delete task
- [ ] User cannot see other users' tasks
- [ ] Unauthenticated user redirected to signin
- [ ] Session persists across page refresh
- [ ] Expired token redirects to signin

---

## Part 8: Environment Variables Reference

### Backend (.env)

| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| BETTER_AUTH_SECRET | Yes | `Kx9mP2vN8qR5tY7wZ3aB6cD1eF4gH0jL` | JWT signing secret (32+ chars) |
| DATABASE_URL | Yes | `postgresql+asyncpg://...` | Neon PostgreSQL connection |
| DEBUG | No | `true` | Enable debug logging |
| ENVIRONMENT | No | `development` | Environment name |
| CORS_ORIGINS | Yes | `http://localhost:3000` | Allowed CORS origins |

### Frontend (.env.local)

| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| BETTER_AUTH_SECRET | Yes | `Kx9mP2vN8qR5tY7wZ3aB6cD1eF4gH0jL` | JWT signing secret (MUST match backend) |
| NEXT_PUBLIC_API_URL | Yes | `http://localhost:8000` | Backend API base URL |
| BETTER_AUTH_URL | Yes | `http://localhost:3000` | Frontend base URL |

---

## Part 9: Production Deployment

### Backend Deployment

1. Set environment variables on hosting platform
2. Use production DATABASE_URL from Neon
3. Set `DEBUG=false`
4. Use production CORS_ORIGINS
5. Enable HTTPS
6. Run with production ASGI server (e.g., Gunicorn + Uvicorn)

### Frontend Deployment

1. Build production bundle: `npm run build`
2. Set production environment variables
3. Deploy to Vercel/Netlify/similar
4. Update NEXT_PUBLIC_API_URL to production backend URL
5. Ensure HTTPS enabled

### Security Checklist

- [ ] BETTER_AUTH_SECRET is strong and unique
- [ ] DATABASE_URL uses SSL (`?sslmode=require`)
- [ ] HTTPS enabled on both frontend and backend
- [ ] CORS_ORIGINS restricted to production domains
- [ ] Environment variables not committed to git
- [ ] Debug mode disabled in production
- [ ] Database backups configured

---

## Summary

**Setup Time**: ~15-20 minutes
**Services**: 2 (Frontend + Backend)
**Database**: Neon PostgreSQL (cloud)
**Ports**: 3000 (frontend), 8000 (backend)

**Quick Start Commands**:
```bash
# Backend
cd backend && source venv/bin/activate && uvicorn src.main:app --reload

# Frontend (new terminal)
cd frontend && npm run dev
```

**Access Points**:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

For issues, refer to the Troubleshooting section or check the project documentation.
