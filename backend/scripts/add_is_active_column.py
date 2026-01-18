import sqlite3
import os

DB_PATH = 'pharmacy_local.db'

def migrate():
    print(f"Migrating database at: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print("Database not found!")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(medicines)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'is_active' not in columns:
            print("Adding 'is_active' column...")
            cursor.execute("ALTER TABLE medicines ADD COLUMN is_active BOOLEAN DEFAULT 1 NOT NULL")
            print("Column added successfully.")
        else:
            print("'is_active' column already exists.")
            
        conn.commit()
        print("Migration complete.")
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
