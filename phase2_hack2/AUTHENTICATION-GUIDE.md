# 🔐 FastAPI Authentication System - Complete Guide

## ✅ What Was Built

A complete JWT-based authentication system with:
- **User registration** (`/api/auth/signup`)
- **User login** (`/api/auth/signin`)
- **Profile endpoint** (`/api/auth/me`)
- **Password hashing** with bcrypt
- **JWT tokens** valid for 24 hours
- **Full Swagger documentation** at `/docs`

---

## 📁 File Structure

```
backend/
├── src/
│   ├── models/
│   │   └── user.py              # User model with password_hash
│   ├── schemas/
│   │   └── auth.py              # Auth request/response schemas
│   ├── api/
│   │   └── routes/
│   │       ├── auth.py          # Auth endpoints (NEW)
│   │       └── tasks.py         # Task endpoints
│   ├── core/
│   │   ├── security.py          # Password hashing + JWT creation
│   │   ├── database.py          # SQLite database
│   │   └── config.py            # Environment config
│   └── main.py                  # FastAPI app with auth router
├── .env                         # Environment variables
└── local.db                     # SQLite database (auto-created)
```

---

## 🚀 Start the Backend

**Terminal 1:**
```powershell
cd C:\Users\anzis\Desktop\phase2_hack2
.venv\Scripts\Activate.ps1
cd backend
uvicorn src.main:app --reload --port 8001
```

**Expected Output:**
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

[OK] FastAPI application started successfully
[INFO] API Documentation: http://localhost:8001/docs
```

---

## 📖 API Documentation

Open your browser: **http://localhost:8001/docs**

You should now see these endpoints under **Authentication** section:
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/signin` - Login existing user
- `GET /api/auth/me` - Get current user profile

---

## 🧪 Testing the Endpoints

### 1. Register a New User (Signup)

**Endpoint:** `POST /api/auth/signup`

**Request Body:**
```json
{
  "email": "test@example.com",
  "password": "securepass123",
  "name": "Test User"
}
```

**Response (201 Created):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "test@example.com",
    "name": "Test User",
    "email_verified": false,
    "created_at": "2026-02-05T10:00:00Z"
  }
}
```

**Using curl:**
```bash
curl -X POST "http://localhost:8001/api/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"securepass123","name":"Test User"}'
```

---

### 2. Login (Signin)

**Endpoint:** `POST /api/auth/signin`

**Request Body:**
```json
{
  "email": "test@example.com",
  "password": "securepass123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "test@example.com",
    "name": "Test User",
    "email_verified": false,
    "created_at": "2026-02-05T10:00:00Z"
  }
}
```

**Using curl:**
```bash
curl -X POST "http://localhost:8001/api/auth/signin" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"securepass123"}'
```

---

### 3. Get Current User Profile

**Endpoint:** `GET /api/auth/me`

**Headers:**
```
Authorization: Bearer <your_access_token>
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "test@example.com",
  "name": "Test User",
  "email_verified": false,
  "created_at": "2026-02-05T10:00:00Z"
}
```

**Using curl:**
```bash
curl -X GET "http://localhost:8001/api/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 🎯 Testing in Swagger UI (/docs)

### Step 1: Register a User
1. Open http://localhost:8001/docs
2. Find `POST /api/auth/signup` under **Authentication**
3. Click **Try it out**
4. Enter:
   ```json
   {
     "email": "demo@example.com",
     "password": "password123",
     "name": "Demo User"
   }
   ```
5. Click **Execute**
6. **Copy the `access_token`** from the response

### Step 2: Authorize in Swagger
1. Click the **🔓 Authorize** button at the top right
2. Enter: `Bearer YOUR_ACCESS_TOKEN`
3. Click **Authorize**
4. Click **Close**

### Step 3: Test Protected Endpoint
1. Find `GET /api/auth/me`
2. Click **Try it out**
3. Click **Execute**
4. You should see your user profile!

---

## 🔒 Security Features

✅ **Password Hashing**: Passwords are hashed with bcrypt (never stored in plain text)
✅ **JWT Tokens**: Secure tokens with 24-hour expiration
✅ **Email Validation**: Pydantic validates email format
✅ **Password Length**: Minimum 8 characters enforced
✅ **Unique Emails**: Database constraint prevents duplicate accounts
✅ **Email Verification Disabled**: For hackathon speed (can be enabled later)

---

## 🐛 Troubleshooting

### Issue: "Email already exists"
**Solution**: Use a different email or delete `backend/local.db` to reset

### Issue: "Invalid credentials"
**Solution**: Check email/password are correct (case-sensitive)

### Issue: "Authentication required"
**Solution**: Include `Authorization: Bearer <token>` header

### Issue: Endpoints not showing in /docs
**Solution**: 
1. Restart backend server
2. Check console for errors
3. Verify `auth.py` router is imported in `main.py`

### Issue: Database error on startup
**Solution**:
```bash
cd backend
rm local.db
# Restart server - database will be recreated
```

---

## 📝 Environment Variables

**backend/.env:**
```env
BETTER_AUTH_SECRET=rPW1fa7hXGmqdsjXeZBxo1nBv642WGFM
DATABASE_URL=sqlite+aiosqlite:///./local.db
DEBUG=true
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3001,http://localhost:3000
```

---

## ✅ Success Checklist

- [ ] Backend starts without errors
- [ ] http://localhost:8001/docs loads
- [ ] See "Authentication" section in docs
- [ ] Can register new user via `/api/auth/signup`
- [ ] Receive JWT token in response
- [ ] Can login via `/api/auth/signin`
- [ ] Can access `/api/auth/me` with token
- [ ] `backend/local.db` file exists

---

## 🎉 You're Ready!

Your FastAPI authentication system is complete and ready for your hackathon project!

**Next Steps:**
1. Test all three endpoints in Swagger UI
2. Integrate with your frontend
3. Use the JWT token for protected task endpoints
4. Build your hackathon features!
