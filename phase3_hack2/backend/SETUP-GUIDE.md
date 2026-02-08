# 🔐 Complete Authentication System Setup Guide

## ✅ System Features

- **POST /api/auth/signup** - Register new user
- **POST /api/auth/signin** - Login existing user
- **GET /api/auth/me** - Get current user profile (JWT protected)
- **JWT Authentication** with Bearer tokens
- **Password Hashing** with bcrypt
- **Structured Logging** with JSON format
- **Swagger UI** at http://127.0.0.1:8001/docs
- **Auto-create database tables** on startup
- **Error handling** with proper status codes

---

## 📦 Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**Required packages:**
- fastapi - Web framework
- uvicorn - ASGI server
- sqlmodel - ORM with Pydantic integration
- asyncpg - PostgreSQL async driver
- aiosqlite - SQLite async driver
- python-jose - JWT token handling
- passlib[bcrypt] - Password hashing
- pydantic-settings - Environment configuration

---

## ⚙️ Step 2: Configure Environment

### Option A: SQLite (Local Development - Current Setup)

Your `.env` file is already configured for SQLite:

```env
BETTER_AUTH_SECRET=rPW1fa7hXGmqdsjXeZBxo1nBv642WGFM
DATABASE_URL=sqlite+aiosqlite:///./local.db
DEBUG=true
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

**Pros:** No cloud database needed, instant setup
**Cons:** Not suitable for production deployment

### Option B: Neon PostgreSQL (Production)

To use Neon PostgreSQL, update your `.env`:

```env
BETTER_AUTH_SECRET=rPW1fa7hXGmqdsjXeZBxo1nBv642WGFM
DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_9NdKqixjCGr5@ep-wild-glitter-aipjit0i-pooler.c-4.us-east-1.aws.neon.tech/neondb
DEBUG=true
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

**Important:** Remove `?sslmode=require&channel_binding=require` from the Neon URL. The code handles SSL automatically.

---

## 🚀 Step 3: Start Backend

### Windows:

```bash
cd backend
python -m uvicorn src.main:app --host 127.0.0.1 --port 8001 --reload
```

### Expected Output:

```
================================================================================
[START] Starting FastAPI Backend
================================================================================
[INIT] Initializing database...
[DB] Using SQLite database: ./local.db
[OK] Database tables created successfully
   - users table
   - tasks table
================================================================================

INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
[OK] FastAPI application started successfully
[INFO] API Documentation: http://localhost:8001/docs
[INFO] Health Check: http://localhost:8001/health
```

---

## 📖 Step 4: Access Swagger UI

Open your browser and navigate to:

```
http://127.0.0.1:8001/docs
```

You should see:
- **Authentication** section with:
  - POST /api/auth/signup
  - POST /api/auth/signin
  - GET /api/auth/me
- **tasks** section with task management endpoints
- **Authorize** button (🔓) in the top right

---

## 🧪 Step 5: Test Authentication

### Test 1: Signup (Register New User)

**Request:**
```bash
curl -X POST http://127.0.0.1:8001/api/auth/signup \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"john@example.com\",
    \"password\": \"securepass123\",
    \"name\": \"John Doe\"
  }"
```

**Expected Response (201 Created):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJleHAiOjE3Mzg4NjI0MDAsImlhdCI6MTczODc3NjAwMH0.xyz...",
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

**Backend Logs:**
```json
{"timestamp": "2026-02-05T10:00:00Z", "level": "INFO", "message": "User signup successful", "module": "auth", "function": "signup", "event_type": "user_signup", "user_id": "550e8400-e29b-41d4-a716-446655440000"}
```

### Test 2: Signup with Duplicate Email (Error Case)

**Request:**
```bash
curl -X POST http://127.0.0.1:8001/api/auth/signup \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"john@example.com\",
    \"password\": \"anotherpass\",
    \"name\": \"Another User\"
  }"
```

**Expected Response (400 Bad Request):**
```json
{
  "error_code": "EMAIL_ALREADY_EXISTS",
  "message": "An account with this email already exists"
}
```

### Test 3: Signin (Login)

**Request:**
```bash
curl -X POST http://127.0.0.1:8001/api/auth/signin \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"john@example.com\",
    \"password\": \"securepass123\"
  }"
```

**Expected Response (200 OK):**
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

### Test 4: Signin with Wrong Password (Error Case)

**Request:**
```bash
curl -X POST http://127.0.0.1:8001/api/auth/signin \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"john@example.com\",
    \"password\": \"wrongpassword\"
  }"
```

**Expected Response (401 Unauthorized):**
```json
{
  "error_code": "INVALID_CREDENTIALS",
  "message": "Invalid email or password"
}
```

### Test 5: Get Current User (Protected Endpoint)

**Request:**
```bash
curl -X GET http://127.0.0.1:8001/api/auth/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
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

### Test 6: Get Current User Without Token (Error Case)

**Request:**
```bash
curl -X GET http://127.0.0.1:8001/api/auth/me
```

**Expected Response (401 Unauthorized):**
```json
{
  "error_code": "MISSING_TOKEN",
  "message": "Authentication required. Please sign in."
}
```

---

## 🎯 Step 6: Test in Swagger UI

1. **Open Swagger UI:** http://127.0.0.1:8001/docs

2. **Test Signup:**
   - Click on `POST /api/auth/signup`
   - Click "Try it out"
   - Enter:
     ```json
     {
       "email": "test@example.com",
       "password": "testpass123",
       "name": "Test User"
     }
     ```
   - Click "Execute"
   - Copy the `access_token` from the response

3. **Authorize Swagger:**
   - Click the "Authorize" button (🔓) at the top right
   - Enter: `Bearer <your_access_token>`
   - Click "Authorize"
   - Click "Close"

4. **Test Protected Endpoint:**
   - Click on `GET /api/auth/me`
   - Click "Try it out"
   - Click "Execute"
   - You should see your user profile

---

## 🔍 Step 7: Verify Database

### SQLite:

```bash
cd backend
sqlite3 local.db
```

```sql
-- View all users
SELECT * FROM users;

-- Count users
SELECT COUNT(*) FROM users;

-- Exit
.quit
```

### Neon PostgreSQL:

Use the Neon web console or connect with psql:

```bash
psql "postgresql://neondb_owner:npg_9NdKqixjCGr5@ep-wild-glitter-aipjit0i-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"
```

```sql
-- View all users
SELECT id, email, name, created_at FROM users;
```

---

## 📊 Backend Logs Explained

The backend uses structured JSON logging. Here's what you'll see:

### Startup Logs:
```
[START] Starting FastAPI Backend
[INIT] Initializing database...
[DB] Using SQLite database: ./local.db
[OK] Database tables created successfully
[OK] FastAPI application started successfully
```

### Authentication Logs:
```json
{"timestamp": "2026-02-05T10:00:00Z", "level": "INFO", "message": "User signup successful", "event_type": "user_signup", "user_id": "abc-123"}
{"timestamp": "2026-02-05T10:01:00Z", "level": "INFO", "message": "User signin successful", "event_type": "user_signin", "user_id": "abc-123"}
{"timestamp": "2026-02-05T10:02:00Z", "level": "WARNING", "message": "Authentication failed: Missing Authorization header", "event_type": "auth_failure"}
```

### Error Logs:
```json
{"timestamp": "2026-02-05T10:03:00Z", "level": "ERROR", "message": "Database connection failed", "exception": "..."}
```

---

## 🐛 Troubleshooting

### Problem 1: Port 8001 Already in Use

**Error:**
```
ERROR: [Errno 10048] error while attempting to bind on address ('127.0.0.1', 8001)
```

**Solution:**
```bash
# Find process using port 8001
netstat -ano | findstr ":8001"

# Kill the process (replace PID with actual process ID)
taskkill //PID <PID> //F

# Or use a different port
python -m uvicorn src.main:app --host 127.0.0.1 --port 8002
```

### Problem 2: Signup/Signin Not Appearing in Swagger

**Solution:**
- Clear browser cache and refresh
- Check that auth routes are registered in `src/main.py`:
  ```python
  app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
  ```
- Restart the backend with `--reload` flag

### Problem 3: Database Connection Failed

**Error:**
```
[ERROR] Database initialization failed
```

**Solution for SQLite:**
- Ensure the backend directory is writable
- Check that `DATABASE_URL=sqlite+aiosqlite:///./local.db` in `.env`

**Solution for Neon:**
- Verify the connection string is correct
- Remove `?sslmode=require&channel_binding=require` from URL
- Check that your Neon database is active (not suspended)

### Problem 4: JWT Token Invalid

**Error:**
```json
{
  "error_code": "INVALID_TOKEN",
  "message": "Invalid authentication token. Please sign in again."
}
```

**Solution:**
- Ensure `BETTER_AUTH_SECRET` is the same in backend and frontend
- Check that the token is passed as: `Authorization: Bearer <token>`
- Token expires after 24 hours - get a new token by signing in again

### Problem 5: CORS Errors

**Error in browser console:**
```
Access to fetch at 'http://127.0.0.1:8001/api/auth/signup' from origin 'http://localhost:3000' has been blocked by CORS policy
```

**Solution:**
- Add your frontend URL to `CORS_ORIGINS` in `.env`:
  ```env
  CORS_ORIGINS=http://localhost:3000,http://localhost:3001
  ```
- Restart the backend

---

## 🎉 Success Checklist

- [ ] Backend starts without errors
- [ ] Swagger UI accessible at http://127.0.0.1:8001/docs
- [ ] Signup endpoint visible in Swagger
- [ ] Signin endpoint visible in Swagger
- [ ] Can register a new user successfully
- [ ] Can login with correct credentials
- [ ] Login fails with wrong password
- [ ] Can access /api/auth/me with valid token
- [ ] /api/auth/me fails without token
- [ ] Database contains user records
- [ ] Logs show authentication events

---

## 📁 Project Structure

```
backend/
├── src/
│   ├── main.py                    # FastAPI app entry point
│   ├── core/
│   │   ├── config.py              # Environment configuration
│   │   ├── database.py            # Database connection
│   │   ├── security.py            # JWT & password hashing
│   │   ├── logging.py             # Structured logging
│   │   └── errors.py              # Custom exceptions
│   ├── api/
│   │   ├── dependencies.py        # JWT authentication dependency
│   │   └── routes/
│   │       ├── auth.py            # Auth endpoints
│   │       └── tasks.py           # Task endpoints
│   ├── models/
│   │   ├── user.py                # User database model
│   │   └── task.py                # Task database model
│   └── schemas/
│       ├── auth.py                # Auth request/response schemas
│       └── errors.py              # Error response schemas
├── .env                           # Environment variables
├── requirements.txt               # Python dependencies
└── local.db                       # SQLite database (auto-created)
```

---

## 🔐 Security Features

1. **Password Hashing:** Passwords are hashed with bcrypt (never stored in plain text)
2. **JWT Tokens:** Secure token-based authentication with expiration
3. **HTTPS Ready:** SSL configuration for Neon PostgreSQL
4. **CORS Protection:** Configurable allowed origins
5. **Input Validation:** Pydantic schemas validate all inputs
6. **Error Handling:** No sensitive data leaked in error messages
7. **Structured Logging:** Security events logged without exposing secrets

---

## 🚀 Next Steps

1. **Frontend Integration:** Use the JWT token in Authorization headers
2. **Token Refresh:** Implement refresh token mechanism for long sessions
3. **Email Verification:** Add email verification flow
4. **Password Reset:** Implement forgot password functionality
5. **Rate Limiting:** Add rate limiting to prevent brute force attacks
6. **Production Deployment:** Deploy to cloud platform with Neon PostgreSQL

---

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review backend logs for error messages
3. Verify all environment variables are set correctly
4. Ensure all dependencies are installed
