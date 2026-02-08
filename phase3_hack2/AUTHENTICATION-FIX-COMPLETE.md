# Authentication Fix - Complete Guide

## Issues Fixed

### 1. **Removed Incorrect SQLite Database Files**
- Deleted `backend/local.db` and `frontend/local.db`
- Backend now uses Neon PostgreSQL exclusively
- Frontend no longer has database access

### 2. **Auto-Include Auth Token in API Requests**
**File**: `frontend/src/lib/api.ts`

Added automatic token retrieval from localStorage:
```typescript
function getAccessToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('access_token');
}

// In apiRequest function:
const authToken = token || getAccessToken();
if (authToken) {
  headers['Authorization'] = `Bearer ${authToken}`;
}
```

**Impact**: All API requests now automatically include the JWT token, so protected routes work correctly.

### 3. **Fixed CORS Configuration**
**File**: `backend/.env`

Updated CORS origins to include `127.0.0.1`:
```env
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000
```

**Impact**: Frontend can now make requests from both `localhost` and `127.0.0.1`.

### 4. **Cleaned Frontend Environment**
**File**: `frontend/.env.local`

Removed `DATABASE_URL` (frontend doesn't need database access):
```env
BETTER_AUTH_SECRET=rPW1fa7hXGmqdsjXeZBxo1nBv642WGFM
NEXT_PUBLIC_API_URL=http://127.0.0.1:8001
BETTER_AUTH_URL=http://localhost:3000
```

## How to Start the Application

### Step 1: Start Backend
```bash
cd backend
uvicorn src.main:app --reload --port 8001
```

**Expected Output**:
```
INFO:     Uvicorn running on http://127.0.0.1:8001
INFO:     Application startup complete.
```

### Step 2: Start Frontend (in new terminal)
```bash
cd frontend
npm run dev
```

**Expected Output**:
```
- ready started server on 0.0.0.0:3000, url: http://localhost:3000
```

### Step 3: Test Authentication

1. **Open Browser**: http://localhost:3000/signin

2. **Create Account**:
   - Click "Sign up" link
   - Email: `your@email.com`
   - Password: `yourpassword123` (min 8 characters)
   - Name: `Your Name`
   - Click "Sign up"

3. **Sign In**:
   - Email: `your@email.com`
   - Password: `yourpassword123`
   - Click "Sign in"

4. **Expected Result**:
   - You should be redirected to `/tasks`
   - You should see the tasks page (not the sign-in page)
   - No "Authentication Required" error

## Testing with Test Script

Run the automated test:
```bash
TEST-AUTH-COMPLETE.bat
```

This will:
1. Check if backend is running
2. Test signup endpoint
3. Test signin endpoint
4. Verify CORS configuration

## Troubleshooting

### Issue: "Authentication Required" Error Still Appears

**Check Browser Console** (F12 → Console):
```javascript
// Check if token is stored
localStorage.getItem('access_token')
// Should return a JWT token string

// Check if user is stored
localStorage.getItem('user')
// Should return user JSON
```

**If token is null**:
- Sign-in request failed
- Check Network tab (F12 → Network) for the POST request to `/api/auth/signin`
- Look for error response

### Issue: CORS Error in Browser Console

**Error**: `Access to fetch at 'http://127.0.0.1:8001/api/auth/signin' from origin 'http://localhost:3000' has been blocked by CORS policy`

**Fix**: Restart backend after updating `.env` file:
```bash
# Stop backend (Ctrl+C)
# Start again
cd backend
uvicorn src.main:app --reload --port 8001
```

### Issue: Backend Not Running

**Error**: `Failed to fetch` or `ERR_CONNECTION_REFUSED`

**Fix**: Start backend:
```bash
cd backend
uvicorn src.main:app --reload --port 8001
```

### Issue: Database Connection Error

**Error**: `Could not connect to database`

**Check**: Verify Neon PostgreSQL connection in `backend/.env`:
```env
DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_9NdKqixjCGr5@ep-wild-glitter-aipjit0i-pooler.c-4.us-east-1.aws.neon.tech/neondb
```

**Test Connection**:
```bash
cd backend
python -c "import sys; sys.path.insert(0, 'src'); from core.database import engine; import asyncio; asyncio.run(engine.connect())"
```

### Issue: Invalid Credentials

**Error**: `Invalid email or password`

**Possible Causes**:
1. User doesn't exist - sign up first
2. Wrong password - check for typos
3. Database has old data - try different email

**Create Test User**:
```bash
curl -X POST http://127.0.0.1:8001/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123","name":"Test User"}'
```

## Verification Checklist

- [ ] Backend running on http://127.0.0.1:8001
- [ ] Frontend running on http://localhost:3000
- [ ] No `local.db` files in backend or frontend directories
- [ ] `backend/.env` has correct `DATABASE_URL` (Neon PostgreSQL)
- [ ] `backend/.env` has CORS origins including `127.0.0.1:3000`
- [ ] `frontend/.env.local` does NOT have `DATABASE_URL`
- [ ] Can access http://127.0.0.1:8001/health (returns `{"status":"healthy"}`)
- [ ] Can sign up new user
- [ ] Can sign in with existing user
- [ ] After sign-in, redirected to `/tasks` (not back to `/signin`)
- [ ] Browser localStorage has `access_token` and `user`

## Architecture Overview

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│   Frontend      │         │   Backend       │         │   Neon DB       │
│   (Next.js)     │────────▶│   (FastAPI)     │────────▶│  (PostgreSQL)   │
│   Port 3000     │  HTTP   │   Port 8001     │  SQL    │                 │
└─────────────────┘         └─────────────────┘         └─────────────────┘
        │
        │ localStorage
        ▼
  ┌──────────────┐
  │ access_token │
  │ user (JSON)  │
  └──────────────┘
```

**Authentication Flow**:
1. User submits email/password on `/signin` page
2. Frontend sends POST to `http://127.0.0.1:8001/api/auth/signin`
3. Backend validates credentials against Neon PostgreSQL
4. Backend returns JWT token + user data
5. Frontend stores token in localStorage
6. Frontend redirects to `/tasks`
7. Protected layout checks localStorage for token
8. All API requests automatically include token in Authorization header

## Summary

The authentication error was caused by:
1. **Missing auto-token inclusion** - API requests weren't including the JWT token
2. **CORS mismatch** - Backend didn't allow requests from `127.0.0.1:3000`
3. **Incorrect database files** - SQLite files with wrong schema were present
4. **Frontend database config** - Frontend had unnecessary `DATABASE_URL`

All issues have been fixed. Follow the startup steps above to test the application.
