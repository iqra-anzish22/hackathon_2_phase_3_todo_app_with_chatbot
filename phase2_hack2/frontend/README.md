# Multi-User Todo Frontend

Next.js frontend for the Multi-User Todo Web Application with Better Auth authentication and deployment readiness features.

## Features

- ✅ User authentication (sign up, sign in)
- ✅ Session persistence with JWT tokens
- ✅ Task management (create, read, update, delete)
- ✅ Task completion toggle
- ✅ Environment variable validation (fail-fast on build/startup)
- ✅ Comprehensive error handling with user-friendly messages
- ✅ Responsive design for desktop and mobile
- ✅ Protected routes with automatic redirect

## Prerequisites

- Node.js 18+
- npm or yarn
- Backend API running on http://localhost:8000

## Setup

1. Install dependencies:
```bash
npm install
# or
yarn install
```

2. Configure environment variables:
```bash
cp .env.local.example .env.local
# Edit .env.local with your actual values
```

3. Run development server:
```bash
npm run dev
# or
yarn dev
```

The application will be available at http://localhost:3000

## Project Structure

```
frontend/
├── src/
│   ├── app/                 # Next.js App Router pages
│   │   ├── (auth)/         # Authentication pages (signin, signup)
│   │   ├── (protected)/    # Protected routes (tasks)
│   │   ├── layout.tsx      # Root layout
│   │   └── page.tsx        # Landing page
│   ├── components/         # React components
│   ├── lib/                # Utilities (auth, api client)
│   └── types/              # TypeScript type definitions
├── tests/                  # Test files
├── package.json            # Node dependencies
└── .env.local.example     # Environment variable template
```

## Environment Variables

**All required variables must be set before building or starting the application. The application will fail with clear error messages if any are missing.**

### Required Variables

- `BETTER_AUTH_SECRET`: JWT signing secret (must match backend exactly)
  - Generate with: `openssl rand -base64 32`
  - **CRITICAL**: Must be identical to backend secret
- `NEXT_PUBLIC_API_URL`: Backend API URL
  - Example: `http://localhost:8000`
  - Used for all API requests
- `BETTER_AUTH_URL`: Frontend URL for Better Auth
  - Example: `http://localhost:3000`

**Example .env.local file:**
```bash
BETTER_AUTH_SECRET=your-secret-key-min-32-chars-here
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_URL=http://localhost:3000
```

### Environment Validation

The application validates `NEXT_PUBLIC_API_URL` at startup. If missing, you'll see:

```
Error: Missing required environment variable: NEXT_PUBLIC_API_URL
Add NEXT_PUBLIC_API_URL to your .env.local file
Example: NEXT_PUBLIC_API_URL=http://localhost:8000
See frontend/.env.local.example for configuration
```

## Features

- User authentication (sign up, sign in)
- Session persistence with JWT tokens
- Task management (create, read, update, delete)
- Task completion toggle
- Responsive design for desktop and mobile
- Protected routes with automatic redirect
- Comprehensive error handling with user-friendly messages

## Troubleshooting

### Missing Environment Variables

**Error:** `Missing required environment variable: NEXT_PUBLIC_API_URL`

**Solution:**
1. Create `.env.local` file in frontend directory
2. Copy contents from `.env.local.example`
3. Set `NEXT_PUBLIC_API_URL=http://localhost:8000`
4. Restart the development server

### Authentication Errors

**Error:** `401 Unauthorized` or session expired

**Solution:**
1. Verify `BETTER_AUTH_SECRET` matches backend exactly
2. Check backend is running on the correct port
3. Clear browser cookies and try signing in again

### API Connection Errors

**Error:** Frontend shows "API unavailable" or network errors

**Solution:**
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check `NEXT_PUBLIC_API_URL` in `.env.local` is correct
3. Verify CORS is configured correctly in backend
4. Check browser console for detailed error messages

### Build Errors

**Error:** Build fails with environment variable errors

**Solution:**
1. Ensure all required variables are in `.env.local`
2. Restart the build process after adding variables
3. Check for typos in variable names (case-sensitive)

## Development

Build for production:
```bash
npm run build
npm start
```

Run linter:
```bash
npm run lint
```

## Authentication Flow

1. User signs up or signs in via Better Auth
2. Better Auth issues JWT token stored in HTTP-only cookie
3. Frontend middleware protects routes and redirects unauthenticated users
4. API client automatically includes JWT token in all requests
5. Backend verifies token and enforces task ownership

## API Integration

All API calls go through `src/lib/api.ts` which:
- Adds Authorization header with JWT token
- Handles 401 errors (expired token)
- Provides consistent error handling
- Supports all CRUD operations for tasks
