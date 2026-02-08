# 🚀 Local Development Startup Guide

## ✅ What Was Fixed

### Problems Solved:
1. ✅ Backend no longer hangs on unreachable Neon database
2. ✅ Switched to **SQLite** for local development (no cloud DB needed)
3. ✅ Fixed environment variable mismatches (secrets, ports, URLs)
4. ✅ Backend startup is now non-blocking (FastAPI /docs loads even if DB fails)
5. ✅ CORS configured for both port 3000 and 3001
6. ✅ Better-auth configured with matching secrets

### Configuration Changes:
- **Backend**: Uses `sqlite+aiosqlite:///./local.db`
- **Frontend**: Uses `sqlite://./local.db`
- **Shared Secret**: `rPW1fa7hXGmqdsjXeZBxo1nBv642WGFM` (matches on both sides)
- **CORS**: Allows `http://localhost:3000` and `http://localhost:3001`

---

## 🎯 Quick Start

### Option 1: Using Batch Scripts (Easiest)

**Terminal 1 - Backend:**
```bash
cd C:\Users\anzis\Desktop\phase2_hack2\backend
start-backend.bat
```

**Terminal 2 - Frontend:**
```bash
cd C:\Users\anzis\Desktop\phase2_hack2\frontend
start-frontend.bat
```

### Option 2: Manual Commands

**Terminal 1 - Backend:**
```bash
cd C:\Users\anzis\Desktop\phase2_hack2
.venv\Scripts\activate
cd backend
uvicorn src.main:app --reload --port 8001
```

**Terminal 2 - Frontend:**
```bash
cd C:\Users\anzis\Desktop\phase2_hack2\frontend
npm run dev
```

---

## 🔍 Verification Steps

### 1. Verify Backend is Running
Open browser and check:
- ✅ http://localhost:8001 - Should show API info
- ✅ http://localhost:8001/docs - Should load Swagger UI
- ✅ http://localhost:8001/health - Should show health status

**Expected Backend Console Output:**
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
[INFO] Health Check: http://localhost:8001/health
INFO:     Uvicorn running on http://127.0.0.1:8001
```

### 2. Verify Frontend is Running
Check console output:
```
▲ Next.js 15.5.12
- Local:        http://localhost:3001  (or 3000 if available)
✓ Ready in X.Xs
```

**Important:** Note which port Next.js actually uses (3000 or 3001)

### 3. Update Frontend Port if Needed
If Next.js runs on port **3001** (not 3000), verify `.env.local`:
```bash
BETTER_AUTH_URL=http://localhost:3001
```

If it's wrong, update it and restart the frontend.

---

## 🧪 Test Signup Flow

### Step 1: Open Frontend
Navigate to: http://localhost:3001/signup (or 3000 if that's the port)

### Step 2: Create Test Account
- **Email**: test@example.com
- **Password**: testpassword123 (min 8 characters)
- Click **Sign Up**

### Step 3: Expected Behavior
✅ **Success**: Redirects to `/tasks` page
❌ **Failure**: Shows error message

### Common Issues & Solutions

#### Issue: "Failed to initialize database adapter"
**Cause**: Better-auth can't connect to database
**Solution**:
1. Stop frontend (Ctrl+C)
2. Delete `frontend/.next` folder
3. Verify `frontend/.env.local` has correct `DATABASE_URL`
4. Restart frontend

#### Issue: "Registration Failed - Unable to create account"
**Cause**: Better-auth database tables not created
**Solution**:
1. Check frontend console for errors
2. Verify `frontend/local.db` file exists
3. Check that `pg` package is installed: `cd frontend && npm list pg`

#### Issue: Backend /docs doesn't load
**Cause**: Backend still trying to connect to Neon
**Solution**:
1. Verify `backend/.env` has `DATABASE_URL=sqlite+aiosqlite:///./local.db`
2. Restart backend
3. Check backend console for errors

#### Issue: CORS errors in browser console
**Cause**: Frontend port doesn't match CORS configuration
**Solution**:
1. Check which port frontend is using (3000 or 3001)
2. Verify `backend/.env` has both ports in CORS_ORIGINS
3. Restart backend

---

## 📁 Database Files

After successful startup, you should see:
- `backend/local.db` - Backend SQLite database (tasks, users)
- `frontend/local.db` - Frontend SQLite database (better-auth tables)

**Note**: These are separate databases. Better-auth manages its own user/session tables.

---

## 🔧 Troubleshooting

### Reset Everything
If things are broken, reset:

```bash
# Stop both servers (Ctrl+C in both terminals)

# Backend cleanup
cd C:\Users\anzis\Desktop\phase2_hack2\backend
del local.db

# Frontend cleanup
cd C:\Users\anzis\Desktop\phase2_hack2\frontend
rmdir /s /q .next
del local.db

# Restart both servers
```

### Check Environment Variables
```bash
# Backend
cd C:\Users\anzis\Desktop\phase2_hack2\backend
type .env

# Frontend
cd C:\Users\anzis\Desktop\phase2_hack2\frontend
type .env.local
```

Both should have matching `BETTER_AUTH_SECRET`.

---

## ✅ Success Checklist

- [ ] Backend starts without hanging
- [ ] http://localhost:8001/docs loads successfully
- [ ] Frontend starts and shows port number
- [ ] Can access signup page
- [ ] Can create a test account
- [ ] Redirects to /tasks after signup
- [ ] No CORS errors in browser console

---

## 🎉 You're Ready!

Once all checks pass, your hackathon project is ready for local development!

**Next Steps:**
1. Test signin flow at http://localhost:3001/signin
2. Implement task management features
3. Test API endpoints via /docs
