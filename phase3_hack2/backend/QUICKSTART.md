# 🚀 Quick Start Guide

## Start Backend (Windows)

### Method 1: Using Batch Script (Easiest)
```bash
cd backend
start-backend.bat
```

### Method 2: Manual Command
```bash
cd backend
python -m uvicorn src.main:app --host 127.0.0.1 --port 8001 --reload
```

## Access Swagger UI

Open browser: **http://127.0.0.1:8001/docs**

## Test Authentication

### Method 1: Using Test Script
```bash
cd backend
test-auth.bat
```

### Method 2: Manual Testing

**1. Signup:**
```bash
curl -X POST http://127.0.0.1:8001/api/auth/signup \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"user@example.com\",\"password\":\"pass12345\",\"name\":\"John Doe\"}"
```

**2. Signin:**
```bash
curl -X POST http://127.0.0.1:8001/api/auth/signin \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"user@example.com\",\"password\":\"pass12345\"}"
```

**3. Get Profile (use token from signin):**
```bash
curl -X GET http://127.0.0.1:8001/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Verify Database

### SQLite (Current Setup):
```bash
cd backend
sqlite3 local.db "SELECT email, name, created_at FROM users;"
```

### Switch to Neon PostgreSQL:
1. Copy `.env.neon` to `.env`
2. Restart backend
3. Tables auto-create on startup

## Troubleshooting

**Port 8001 in use?**
```bash
netstat -ano | findstr ":8001"
taskkill //PID <PID> //F
```

**Auth endpoints not showing?**
- Clear browser cache
- Restart backend with `--reload`
- Check http://127.0.0.1:8001/openapi.json

**Database errors?**
- Check `.env` file exists
- Verify DATABASE_URL is correct
- Ensure backend directory is writable

## Success Indicators

✅ Backend starts without errors
✅ Swagger UI shows signup/signin endpoints
✅ Can register new user
✅ Can login with credentials
✅ JWT token works for protected routes
✅ Database stores users correctly
✅ Logs show authentication events

## Files Created

- `start-backend.bat` - Start backend server
- `test-auth.bat` - Test all auth endpoints
- `SETUP-GUIDE.md` - Complete documentation
- `.env.neon` - Neon PostgreSQL configuration

## Next Steps

1. Start backend: `start-backend.bat`
2. Open Swagger: http://127.0.0.1:8001/docs
3. Test signup/signin in Swagger UI
4. Integrate with frontend using JWT tokens

For detailed documentation, see **SETUP-GUIDE.md**
