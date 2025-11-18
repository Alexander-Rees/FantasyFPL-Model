#!/usr/bin/env python3
"""
Test database connection script
Tests if we can connect to Supabase PostgreSQL database
"""
import os
import sys
import psycopg2
from psycopg2 import Error

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME', 'postgres'),
    'port': int(os.getenv('DB_PORT', '5432'))
}

def test_connection():
    """Test database connection"""
    print("=" * 60)
    print("Testing Supabase PostgreSQL Connection")
    print("=" * 60)
    
    # Check environment variables
    print("\n📋 Environment Variables:")
    print(f"  DB_HOST: {DB_CONFIG['host']}")
    print(f"  DB_PORT: {DB_CONFIG['port']}")
    print(f"  DB_USER: {DB_CONFIG['user']}")
    print(f"  DB_NAME: {DB_CONFIG['database']}")
    print(f"  DB_PASSWORD: {'*' * len(DB_CONFIG['password']) if DB_CONFIG['password'] else 'NOT SET'}")
    
    if not DB_CONFIG['password']:
        print("\n❌ ERROR: DB_PASSWORD environment variable is not set!")
        print("   Set it with: export DB_PASSWORD='your-password'")
        return False
    
    # Test connection
    print("\n🔌 Attempting to connect...")
    try:
        # Add SSL mode for Supabase connections
        connection = psycopg2.connect(**DB_CONFIG, sslmode='require')
        print("✅ Connection successful!")
        
        # Test a simple query
        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ PostgreSQL version: {version[0][:50]}...")
        
        # Check if player table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'player'
            );
        """)
        table_exists = cursor.fetchone()[0]
        
        if table_exists:
            cursor.execute("SELECT COUNT(*) FROM player;")
            player_count = cursor.fetchone()[0]
            print(f"✅ Player table exists with {player_count} players")
        else:
            print("⚠️  Player table does not exist yet (this is OK if database is new)")
        
        cursor.close()
        connection.close()
        print("\n✅ All tests passed!")
        return True
        
    except Error as e:
        print(f"\n❌ Connection failed: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Check that DB_HOST is correct (should start with 'db.')")
        print("   2. Verify DB_PASSWORD is correct")
        print("   3. Ensure your IP is allowed in Supabase (Settings → Database → Connection Pooling)")
        print("   4. Check that the database is running in Supabase dashboard")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)

