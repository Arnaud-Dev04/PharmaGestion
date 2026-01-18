
import sqlite3
import os

DB_PATH = os.path.join(os.getenv('APPDATA'), 'PharmaGestion', 'pharmacy.db')

def add_column():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        # Try local dev path
        local_db = "pharmacy.db"
        if os.path.exists(local_db):
            print(f"Found local DB at {local_db}")
            conn = sqlite3.connect(local_db)
        else:
            return
    else:
        conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT expiry_alert_threshold FROM medicines LIMIT 1")
        print("Column 'expiry_alert_threshold' already exists.")
    except sqlite3.OperationalError:
        print("Adding 'expiry_alert_threshold' column...")
        try:
            cursor.execute("ALTER TABLE medicines ADD COLUMN expiry_alert_threshold INTEGER NOT NULL DEFAULT 30")
            conn.commit()
            print("Column added successfully.")
        except Exception as e:
            print(f"Error adding column: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_column()
