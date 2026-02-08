# Quickstart Guide: Multi-User Todo Application - Deployment Ready

**Feature**: 003-deployment-readiness
**Date**: 2026-02-05
**Purpose**: Complete setup and deployment guide for reviewers and operators

## Overview

This guide provides comprehensive instructions to set up, run, and verify the Multi-User Todo Web Application. The application is deployment-ready with environment validation, health monitoring, and operational logging.

**Setup Time**: ~15 minutes
**Prerequisites**: Node.js 18+, Python 3.11+, Git
**Services**: Frontend (Next.js), Backend (FastAPI), Database (Neon PostgreSQL)

---

## Quick Start (TL;DR)

```bash
# 1. Clone and navigate
git clone <repository-url>
cd phase2_hack2

# 2. Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your DATABASE_URL and BETTER_AUTH_SECRET
uvicorn src.main:app --reload

# 3. Frontend setup (new terminal)
cd frontend
npm install
cp .env.local.example .env.local
# Edit .env.local with same BETTER_AUTH_SECRET
npm run dev

# 4. Access
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
# Health Check: http://localhost:8000/health
```

---

## Architecture Overview

```
┌─────────────────┐         HTTP/REST API        ┌─────────────────┐
│  Next.js        │    (JWT Authentication)      │  FastAPI        │
│  Frontend       │◄────────────────────────────►│  Backend        │
│  Port 3000      │                              │  Port 8000      │
│                 │                              │                 │
│  - Better Auth  │                              │  - JWT Verify   │
│  - UI/UX        │                              │  - SQLModel     │
│  - API Client   │                              │  - Health Check │
│  - Error        │                              │  - Logging      │
│    Handling     │                              │  - Validation   │
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

**Key Features**:
- ✅ Multi-user task management with JWT authentication
- ✅ Environment validation (fail fast on misconfiguration)
- ✅ Health check endpoint for monitoring
- ✅ Structured logging for operational visibility
- ✅ Independent frontend/backend services
- ✅ Comprehensive error handling

---

## Prerequisites

### Required Software

| Software | Version | Purpose | Installation |
|----------|---------|---------|--------------|
| Python | 3.11+ | Backend runtime | https://python.org |
| Node.js | 18+ | Frontend runtime | https://nodejs.org |
| npm | 9+ | Package manager | Included with Node.js |
| Git | 2.x | Version control | https://git-scm.com |

### Required Accounts

| Service | Purpose | Sign Up |
|---------|---------|---------|
| Neon PostgreSQL | Database hosting | https://neon.tech (free tier) |

### Verification

```bash
# Verify installations
python --version    # Should show 3.11+
node --version      # Should show v18+
npm --version       # Should show 9+
git --version       # Should show 2.x
```

---

## Part 1: Database Setup (Neon PostgreSQL)

### Step 1: Create Neon Account

1. Visit https://neon.tech
2. Sign up for free account
3. Verify email address

### Step 2: Create Project

1. Click "New Project"
2. Project name: `multiuser-todo`
3. Region: Choose closest to you (e.g., US East)
4. Click "Create Project"

### Step 3: Get Connection String

1. In project dashboard, click "Connection Details"
2. Copy the connection string (format: `postgresql://user:pass@host/db`)
3. **Important**: Keep this secure, you'll need it for backend configuration

**Example Connection String**:
```
postgresql://user:password@ep-cool-name-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
```

### Step 4: Verify Connection (Optional)

```bash
# Test connection using psql (if installed)
psql "postgresql://user:password@host/db?sslmode=require"
```

---

## Part 2: Backend Setup (FastAPI)

### Step 1: Navigate to Backend Directory

```bash
cd backend
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate

# Verify activation (prompt should show (venv))
```

### Step 3: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

**Expected Output**:
```
Successfully installed fastapi-0.109.0 uvicorn-0.27.0 sqlmodel-0.0.14 ...
```

### Step 4: Configure Environment Variables

```bash
# Copy example file
cp .env.example .env

# Edit .env with your values
# Windows: notepad .env
# macOS/Linux: nano .env
```

**backend/.env** (edit these values):
```bash
# Generate secret: openssl rand -base64 32
BETTER_AUTH_SECRET=your-secret-key-min-32-chars-here

# Your Neon connection string (add +asyncpg after postgresql)
DATABASE_URL=postgresql+asyncpg://user:password@host/db?sslmode=require

# Application settings
DEBUG=true
ENVIRONMENT=development

# Frontend URL for CORS
CORS_ORIGINS=http://localhost:3000
```

**⚠️ Important**:
- `BETTER_AUTH_SECRET` must be at least 32 characters
- `DATABASE_URL` must include `+asyncpg` after `postgresql`
- `DATABASE_URL` must end with `?sslmode=require`
- Generate secret with: `openssl rand -base64 32`

### Step 5: Initialize Database

```bash
# Run database migrations
alembic upgrade head
```

**Expected Output**:
```
INFO  [alembic.runtime.migration] Running upgrade -> abc123, create tasks table
```

### Step 6: Start Backend Server

```bash
# Start FastAPI server with auto-reload
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

Open browser and test these endpoints:

1. **Root**: http://localhost:8000
   - Should show: `{"message": "Multi-User Todo API", "status": "running"}`

2. **Health Check**: http://localhost:8000/health
   - Should show: `{"status": "healthy", "database": "connected", "timestamp": "..."}`

3. **API Documentation**: http://localhost:8000/docs
   - Should show interactive Swagger UI

**✅ Backend is ready when**:
- Server starts without errors
- Health check returns `"status": "healthy"`
- API docs are accessible

---

## Part 3: Frontend Setup (Next.js)

### Step 1: Open New Terminal

**Important**: Keep backend terminal running, open a new terminal for frontend

```bash
# Navigate to frontend directory
cd frontend
```

### Step 2: Install Dependencies

```bash
# Using npm
npm install

# Or using yarn
yarn install
```

**Expected Output**:
```
added 1234 packages in 30s
```

### Step 3: Configure Environment Variables

```bash
# Copy example file
cp .env.local.example .env.local

# Edit .env.local with your values
# Windows: notepad .env.local
# macOS/Linux: nano .env.local
```

**frontend/.env.local** (edit these values):
```bash
# MUST match backend secret exactly
BETTER_AUTH_SECRET=your-secret-key-min-32-chars-here

# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Frontend URL for Better Auth
BETTER_AUTH_URL=http://localhost:3000
```

**⚠️ Critical**:
- `BETTER_AUTH_SECRET` MUST be identical to backend
- Use the SAME secret you generated for backend
- If secrets don't match, authentication will fail

### Step 4: Start Frontend Server

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

1. **Home**: http://localhost:3000
   - Should show landing page

2. **Sign Up**: http://localhost:3000/signup
   - Should show registration form

3. **Sign In**: http://localhost:3000/signin
   - Should show login form

**✅ Frontend is ready when**:
- Server starts without errors
- Pages load without console errors
- Forms are visible and functional

---

## Part 4: End-to-End Verification

### Test 1: User Registration

1. Navigate to http://localhost:3000/signup
2. Enter email: `test@example.com`
3. Enter password: `password123`
4. Click "Sign Up"
5. **Expected**: Redirect to tasks page
6. **Verify**: Browser has `auth-token` cookie

### Test 2: Task Creation

1. On tasks page, enter task title: "Test Task"
2. Optionally add description
3. Click "Create Task"
4. **Expected**: Task appears in list
5. **Verify**: Network tab shows `POST /api/tasks` with 201 response

### Test 3: Task Operations

1. **View**: Click on task to see details
2. **Edit**: Update task title, click save
3. **Complete**: Toggle completion checkbox
4. **Delete**: Click delete button, confirm
5. **Expected**: All operations succeed

### Test 4: Multi-User Isolation

1. Open incognito/private browser window
2. Sign up with different email: `user2@example.com`
3. Create tasks in second account
4. **Expected**: Tasks from first account NOT visible
5. **Verify**: Each user sees only their own tasks

### Test 5: Authentication Protection

1. Sign out from application
2. Try to access http://localhost:3000/tasks directly
3. **Expected**: Redirect to sign-in page
4. Sign in again
5. **Expected**: Redirect back to tasks page

### Test 6: Health Monitoring

1. Open http://localhost:8000/health
2. **Expected**: `{"status": "healthy", "database": "connected"}`
3. Stop database (or disconnect network)
4. Refresh health endpoint
5. **Expected**: `{"status": "unhealthy", "database": "disconnected"}`

---

## Part 5: Troubleshooting

### Backend Issues

#### Issue: `ModuleNotFoundError: No module named 'fastapi'`

**Cause**: Virtual environment not activated or dependencies not installed

**Solution**:
```bash
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall dependencies
pip install -r requirements.txt
```

#### Issue: `ValidationError: BETTER_AUTH_SECRET field required`

**Cause**: Missing environment variable

**Solution**:
```bash
# Verify .env file exists
ls -la .env

# Check .env contains BETTER_AUTH_SECRET
cat .env | grep BETTER_AUTH_SECRET

# If missing, add it:
echo "BETTER_AUTH_SECRET=$(openssl rand -base64 32)" >> .env
```

#### Issue: `OperationalError: could not connect to server`

**Cause**: Invalid DATABASE_URL or database unreachable

**Solution**:
1. Verify DATABASE_URL in .env is correct
2. Check Neon dashboard for correct connection string
3. Ensure `+asyncpg` is added: `postgresql+asyncpg://...`
4. Ensure `?sslmode=require` is at the end
5. Test connection: `psql "your-connection-string"`

#### Issue: `401 Unauthorized` on all API requests

**Cause**: BETTER_AUTH_SECRET mismatch between frontend and backend

**Solution**:
```bash
# Check backend secret
cat backend/.env | grep BETTER_AUTH_SECRET

# Check frontend secret
cat frontend/.env.local | grep BETTER_AUTH_SECRET

# They MUST match exactly
# If different, update one to match the other and restart both services
```

### Frontend Issues

#### Issue: `Error: Cannot find module 'next'`

**Cause**: Dependencies not installed

**Solution**:
```bash
cd frontend
npm install
```

#### Issue: `CORS error` when calling API

**Cause**: Backend CORS_ORIGINS doesn't include frontend URL

**Solution**:
```bash
# Check backend .env
cat backend/.env | grep CORS_ORIGINS

# Should be: CORS_ORIGINS=http://localhost:3000
# If wrong, update and restart backend
```

#### Issue: Redirect loop between signin and tasks

**Cause**: Authentication state issue

**Solution**:
1. Clear browser cookies
2. Clear browser local storage
3. Restart frontend server
4. Try signing in again

### Database Issues

#### Issue: `relation "tasks" does not exist`

**Cause**: Database migrations not run

**Solution**:
```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

#### Issue: Connection timeout to Neon

**Cause**: Network issue or Neon project suspended

**Solution**:
1. Check internet connection
2. Visit Neon dashboard, verify project is active
3. Check firewall settings
4. Try different network (mobile hotspot)

---

## Part 6: Environment Variables Reference

### Backend (.env)

| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| `BETTER_AUTH_SECRET` | ✅ Yes | `Kx9mP2vN8qR5tY7wZ3aB6cD1eF4gH0jL` | JWT signing secret (32+ chars, must match frontend) |
| `DATABASE_URL` | ✅ Yes | `postgresql+asyncpg://user:pass@host/db?sslmode=require` | Neon PostgreSQL connection (note +asyncpg) |
| `CORS_ORIGINS` | ✅ Yes | `http://localhost:3000` | Allowed CORS origins (frontend URL) |
| `DEBUG` | ❌ No | `true` | Enable debug logging (default: false) |
| `ENVIRONMENT` | ❌ No | `development` | Environment name (default: development) |

### Frontend (.env.local)

| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| `BETTER_AUTH_SECRET` | ✅ Yes | `Kx9mP2vN8qR5tY7wZ3aB6cD1eF4gH0jL` | JWT signing secret (MUST match backend exactly) |
| `NEXT_PUBLIC_API_URL` | ✅ Yes | `http://localhost:8000` | Backend API base URL |
| `BETTER_AUTH_URL` | ✅ Yes | `http://localhost:3000` | Frontend base URL for Better Auth |

---

## Part 7: Operational Features

### Environment Validation

**Backend**:
- Validates all required environment variables at startup
- Fails fast with clear error messages if variables missing
- Example error: `"Missing required environment variable: BETTER_AUTH_SECRET"`

**Frontend**:
- Validates NEXT_PUBLIC_API_URL at build time
- Validates BETTER_AUTH_SECRET at runtime
- Clear error messages indicate which variable is missing

### Health Monitoring

**Endpoint**: `GET http://localhost:8000/health`

**Healthy Response** (200 OK):
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2026-02-05T12:34:56.789Z"
}
```

**Unhealthy Response** (503 Service Unavailable):
```json
{
  "status": "unhealthy",
  "database": "disconnected",
  "timestamp": "2026-02-05T12:34:56.789Z",
  "error": "Database connection failed"
}
```

**Usage**:
- Monitoring tools can poll this endpoint
- Load balancers can use for health checks
- No authentication required (public endpoint)

### Structured Logging

**Backend logs** (JSON format to stdout):
```json
{
  "timestamp": "2026-02-05T12:34:56.789Z",
  "level": "WARNING",
  "message": "JWT token expired",
  "module": "api.dependencies",
  "function": "get_current_user",
  "event_type": "auth_failure"
}
```

**What's logged**:
- ✅ Authentication failures (invalid/expired JWT)
- ✅ Authorization failures (wrong task owner)
- ✅ Database connection errors
- ✅ Startup configuration errors
- ❌ NOT logged: JWT tokens, passwords, credentials

**Viewing logs**:
```bash
# Backend logs appear in terminal where uvicorn is running
# Filter by event type:
uvicorn src.main:app --reload | grep "auth_failure"
```

---

## Part 8: Service Independence

### Running Backend Independently

```bash
cd backend
source venv/bin/activate
uvicorn src.main:app --reload

# Access API docs: http://localhost:8000/docs
# Access health check: http://localhost:8000/health
# Backend runs without frontend
```

### Running Frontend Independently

```bash
cd frontend
npm run dev

# Frontend starts: http://localhost:3000
# If backend unavailable, shows clear error messages
# Frontend handles API failures gracefully
```

---

## Summary

**Setup Complete When**:
- ✅ Backend starts without errors
- ✅ Health check returns "healthy"
- ✅ Frontend starts without errors
- ✅ User can sign up and create tasks
- ✅ Multi-user isolation verified
- ✅ Authentication protection working

**Access Points**:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

**Next Steps**:
- Review API documentation at /docs
- Test all user stories from spec.md
- Verify operational features (health check, logging)
- Deploy to production (see deployment guide)

For issues not covered here, check:
- Backend logs in terminal
- Frontend console in browser DevTools
- Network tab in browser DevTools
- Health check endpoint status
