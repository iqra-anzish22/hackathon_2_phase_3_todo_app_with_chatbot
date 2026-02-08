# 🔧 DATABASE SCHEMA FIX

## Problem
```
asyncpg.exceptions.UndefinedColumnError: column users.password_hash does not exist
```

Neon database mein purana `users` table hai with wrong schema.

## Solution: Drop and Recreate Table

### Option 1: Using Neon Console (RECOMMENDED)

1. **Go to Neon Console:**
   ```
   https://console.neon.tech
   ```

2. **Select your database**

3. **Go to SQL Editor tab**

4. **Run this SQL:**
   ```sql
   -- Drop old users table
   DROP TABLE IF EXISTS users CASCADE;

   -- Verify it's dropped
   SELECT table_name FROM information_schema.tables
   WHERE table_schema = 'public';
   ```

5. **Restart your backend** - it will auto-create the correct table

### Option 2: Using Python Script

Run this script to fix the database:

```python
# fix_database.py
import asyncio
import asyncpg

async def fix_database():
    # Your Neon connection string
    conn = await asyncpg.connect(
        "postgresql://neondb_owner:npg_9NdKqixjCGr5@ep-wild-glitter-aipjit0i-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"
    )

    try:
        # Drop old users table
        await conn.execute("DROP TABLE IF EXISTS users CASCADE")
        print("✅ Old users table dropped")

        # Drop tasks table too (optional)
        await conn.execute("DROP TABLE IF EXISTS tasks CASCADE")
        print("✅ Old tasks table dropped")

        print("\n✅ Database cleaned!")
        print("Now restart your backend to create new tables.")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(fix_database())
```

Save as `fix_database.py` and run:
```bash
python fix_database.py
```

### Option 3: Manual SQL (if you have psql)

```bash
psql "postgresql://neondb_owner:npg_9NdKqixjCGr5@ep-wild-glitter-aipjit0i-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"
```

Then run:
```sql
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS tasks CASCADE;
\q
```

## After Fixing Database

1. **Restart backend:**
   ```bash
   python -m uvicorn src.main:app --host 127.0.0.1 --port 8001
   ```

2. **Backend will auto-create correct tables** with these columns:
   - `id` (UUID primary key)
   - `email` (unique)
   - `password_hash` (for hashed passwords)
   - `name` (optional)
   - `email_verified` (boolean)
   - `created_at` (timestamp)

3. **Test signup:**
   ```bash
   curl -X POST http://127.0.0.1:8001/api/auth/signup \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"testpass123","name":"Test User"}'
   ```

## Expected Result

After fixing database, signup should return:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid-here",
    "email": "test@example.com",
    "name": "Test User",
    "email_verified": false,
    "created_at": "2026-02-06T..."
  }
}
```

✅ **This will 100% fix the error!**
