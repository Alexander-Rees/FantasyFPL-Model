import os
import psycopg2
from psycopg2 import Error

# DB Config
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'postgres'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD'),
    'port': int(os.getenv('DB_PORT', '5432'))
}

def verify_db():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Check if column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='player' AND column_name='predicted_points';
        """)
        col = cursor.fetchone()
        if col:
            print("✅ Column 'predicted_points' exists.")
        else:
            print("❌ Column 'predicted_points' MISSING.")
            return

        # Check if data is populated
        cursor.execute("SELECT count(*) FROM player WHERE predicted_points > 0")
        count = cursor.fetchone()[0]
        print(f"✅ Players with predicted points: {count}")
        
        if count > 0:
            print("\nSample predictions:")
            cursor.execute("SELECT name, predicted_points FROM player WHERE predicted_points > 0 ORDER BY predicted_points DESC LIMIT 5")
            for row in cursor.fetchall():
                print(f"   {row[0]}: {row[1]}")
        else:
            print("❌ No predictions found in DB.")

        cursor.close()
        conn.close()
        
    except Error as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_db()
