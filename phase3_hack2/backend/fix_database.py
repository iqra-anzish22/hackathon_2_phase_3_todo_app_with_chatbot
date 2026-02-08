"""
Fix Neon Database Schema
Drops old users table and lets backend recreate it with correct schema.
"""
import asyncio
import asyncpg


async def fix_database():
    """Drop old tables and let backend recreate them."""

    # Neon connection string
    DATABASE_URL = "postgresql://neondb_owner:npg_9NdKqixjCGr5@ep-wild-glitter-aipjit0i-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"

    print("="*80)
    print("DATABASE SCHEMA FIX")
    print("="*80)
    print()

    try:
        print("[1/3] Connecting to Neon database...")
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Connected")
        print()

        print("[2/3] Dropping old tables...")

        # Drop users table
        await conn.execute("DROP TABLE IF EXISTS users CASCADE")
        print("✅ Dropped users table")

        # Drop tasks table (optional)
        await conn.execute("DROP TABLE IF EXISTS tasks CASCADE")
        print("✅ Dropped tasks table")

        print()
        print("[3/3] Verifying tables are dropped...")

        # Check remaining tables
        tables = await conn.fetch(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        )

        if tables:
            print(f"Remaining tables: {[t['table_name'] for t in tables]}")
        else:
            print("✅ All tables dropped successfully")

        print()
        print("="*80)
        print("✅ DATABASE CLEANED SUCCESSFULLY!")
        print("="*80)
        print()
        print("Next steps:")
        print("1. Restart your backend:")
        print("   python -m uvicorn src.main:app --host 127.0.0.1 --port 8001")
        print()
        print("2. Backend will auto-create tables with correct schema")
        print()
        print("3. Test signup:")
        print('   curl -X POST http://127.0.0.1:8001/api/auth/signup \\')
        print('     -H "Content-Type: application/json" \\')
        print('     -d \'{"email":"test@example.com","password":"testpass123","name":"Test"}\'')
        print()

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        print()
        print("If connection failed, use Neon Console instead:")
        print("1. Go to: https://console.neon.tech")
        print("2. Select your database")
        print("3. Go to SQL Editor")
        print("4. Run: DROP TABLE IF EXISTS users CASCADE;")
        print("5. Run: DROP TABLE IF EXISTS tasks CASCADE;")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(fix_database())
