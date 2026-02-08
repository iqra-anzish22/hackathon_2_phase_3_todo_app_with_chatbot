# 🚀 FastAPI Authentication Backend - Complete Setup Guide

## ✅ What's Included

This is a **complete, production-ready authentication backend** with:

- **POST /api/auth/signup** - Register new users
- **POST /api/auth/signin** - Login users
- **GET /api/auth/me** - Get current user (JWT protected)
- JWT authentication with 24-hour token expiry
- bcrypt password hashing
- PostgreSQL (Neon) database with async operations
- Structured error handling
- Swagger UI documentation

---

## 📦 Installation

### Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements-auth.txt
```

**Dependencies installed:**
- fastapi - Web framework
- uvicorn - ASGI server
- sqlmodel - ORM with Pydantic
- asyncpg - PostgreSQL async driver
- python-jose - JWT handling
- passlib[bcrypt] - Password hashing
- pydantic[email] - Email validation

### Step 2: Configure Environment

Copy `.env.auth` to `.env`:

```bash
copy .env.auth .env
```

**Edit `.env` with your settings:**

```env
# JWT Secret (keep secure!)
BETTER_AUTH_SECRET=rPW1fa7hXGmqdsjXeZBxo1nBv642WGFM

# Neon PostgreSQL Database
DATABASE_URL=postgresql+asyncpg://user:password@host/database

# CORS Origins
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# App Settings
DEBUG=true
ENVIRONMENT=development
```

**Get your Neon DATABASE_URL:**
1. Go to https://console.neon.tech
2. Select your project
3. Copy the connection string
4. Change `postgresql://` to `postgresql+asyncpg://`
5. Remove `?sslmode=require&channel_binding=require` from the end

---

## 🚀 Running the Backend

### Method 1: Direct Command

```bash
cd backend
python -m uvicorn src.main:app --host 127.0.0.1 --port 8001 --reload
```

### Method 2: Using Startup Script

```bash
cd backend
START-AUTH.bat
```

**Expected Output:**

```
================================================================================
[START] Starting FastAPI Authentication Backend
================================================================================
[INIT] Initializing database...
[DB] Using PostgreSQL: ep-wild-glitter-aipjit0i-pooler.c-4.us-east-1.aws.neon.tech/neondb
[OK] Database tables created successfully
   - users table
================================================================================

INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
[OK] FastAPI application started successfully
[INFO] API Documentation: http://127.0.0.1:8001/docs
[INFO] Health Check: http://127.0.0.1:8001/health
[INFO] Authentication endpoints:
       POST /api/auth/signup
       POST /api/auth/signin
       GET  /api/auth/me
```

---

## 🧪 Testing the API

### Test 1: Health Check

```bash
curl http://127.0.0.1:8001/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-02-05T10:00:00Z"
}
```

### Test 2: Signup (Register New User)

```bash
curl -X POST http://127.0.0.1:8001/api/auth/signup \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"john@example.com\",\"password\":\"securepass123\",\"name\":\"John Doe\"}"
```

**Expected Response (201 Created):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "john@example.com",
    "name": "John Doe",
    "email_verified": false,
    "created_at": "2026-02-05T10:00:00Z"
  }
}
```

**Copy the `access_token` for next tests!**

### Test 3: Signin (Login)

```bash
curl -X POST http://127.0.0.1:8001/api/auth/signin \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"john@example.com\",\"password\":\"securepass123\"}"
```

**Expected Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": { ... }
}
```

### Test 4: Get Current User (Protected)

```bash
curl -X GET http://127.0.0.1:8001/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Expected Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "john@example.com",
  "name": "John Doe",
  "email_verified": false,
  "created_at": "2026-02-05T10:00:00Z"
}
```

### Test 5: Error Cases

**Duplicate Email (400):**
```bash
curl -X POST http://127.0.0.1:8001/api/auth/signup \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"john@example.com\",\"password\":\"pass123\",\"name\":\"Jane\"}"
```

**Response:**
```json
{
  "error_code": "EMAIL_ALREADY_EXISTS",
  "message": "An account with this email already exists"
}
```

**Wrong Password (401):**
```bash
curl -X POST http://127.0.0.1:8001/api/auth/signin \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"john@example.com\",\"password\":\"wrongpass\"}"
```

**Response:**
```json
{
  "error_code": "INVALID_CREDENTIALS",
  "message": "Invalid email or password"
}
```

**Missing Token (401):**
```bash
curl -X GET http://127.0.0.1:8001/api/auth/me
```

**Response:**
```json
{
  "error_code": "MISSING_TOKEN",
  "message": "Authentication required. Please sign in."
}
```

---

## 📖 Swagger UI Testing

### Step 1: Open Swagger UI

Open browser: **http://127.0.0.1:8001/docs**

### Step 2: Test Signup

1. Find **POST /api/auth/signup** under "Authentication"
2. Click "Try it out"
3. Enter request body:
```json
{
  "email": "test@example.com",
  "password": "testpass123",
  "name": "Test User"
}
```
4. Click "Execute"
5. **Copy the `access_token`** from response

### Step 3: Authorize Swagger

1. Click **"Authorize"** button (🔓) at top right
2. Enter: `Bearer <your_access_token>`
3. Click "Authorize"
4. Click "Close"

### Step 4: Test Protected Endpoint

1. Find **GET /api/auth/me**
2. Click "Try it out"
3. Click "Execute"
4. Should see your user profile

---

## 🗄️ Database Verification

### Check Neon Console

1. Go to https://console.neon.tech
2. Select your database
3. Go to "Tables" tab
4. You should see `users` table
5. Click on it to view user records

### SQL Query

```sql
SELECT id, email, name, email_verified, created_at
FROM users
ORDER BY created_at DESC;
```

---

## 📁 Project Structure

```
backend/
├── src/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entry point
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # Environment configuration
│   │   ├── database.py            # Database connection
│   │   ├── security.py            # JWT & password hashing
│   │   └── errors.py              # Custom exceptions
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py                # User database model
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── auth.py                # Request/response schemas
│   └── api/
│       ├── __init__.py
│       ├── dependencies.py        # JWT authentication
│       └── routes/
│           ├── __init__.py
│           └── auth.py            # Auth endpoints
├── .env                           # Environment variables
├── .env.auth                      # Template
├── requirements-auth.txt          # Dependencies
└── START-AUTH.bat                 # Startup script
```

---

## 🐛 Troubleshooting

### Issue: "Failed to load environment variables"

**Solution:** Ensure `.env` file exists in `backend/` directory with all required variables.

### Issue: "Database initialization failed"

**Check:**
1. DATABASE_URL is correct
2. Using `postgresql+asyncpg://` prefix
3. Removed `?sslmode=require&channel_binding=require`
4. Neon database is active (not suspended)

### Issue: "Port 8001 already in use"

**Solution:**
```bash
netstat -ano | findstr ":8001"
taskkill /PID <PID> /F
```

### Issue: "JWT token invalid"

**Check:**
1. Token format: `Authorization: Bearer <token>`
2. Token not expired (24 hours)
3. `BETTER_AUTH_SECRET` is set correctly

---

## ✅ Success Checklist

- [ ] Backend starts without errors
- [ ] Swagger UI accessible at http://127.0.0.1:8001/docs
- [ ] Can register new user (signup)
- [ ] Receives JWT token in response
- [ ] Can login with credentials (signin)
- [ ] Can access /api/auth/me with token
- [ ] /api/auth/me fails without token (401)
- [ ] User appears in Neon database
- [ ] Duplicate email returns 400 error
- [ ] Wrong password returns 401 error

---

## 🎉 You're Done!

Your authentication backend is **complete and working**:

✅ FastAPI with async operations
✅ JWT authentication (24-hour expiry)
✅ bcrypt password hashing
✅ PostgreSQL (Neon) database
✅ Structured error handling
✅ Swagger UI documentation
✅ CORS configured
✅ Production-ready

**Start the backend:**
```bash
cd backend
python -m uvicorn src.main:app --host 127.0.0.1 --port 8001 --reload
```

**Test it:**
- Swagger UI: http://127.0.0.1:8001/docs
- Health: http://127.0.0.1:8001/health

**All endpoints working!** 🚀
