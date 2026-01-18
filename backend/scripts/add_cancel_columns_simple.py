import sqlite3
import os

DB_FILE = "pharmacy_local.db"

def add_cancel_columns():
    if not os.path.exists(DB_FILE):
        print(f"Database file {DB_FILE} not found!")
        return

    print(f"Connecting to {DB_FILE}...")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # Check status column
        try:
            cursor.execute("SELECT status FROM sales LIMIT 1")
            print("Column 'status' already exists.")
        except sqlite3.OperationalError:
            print("Adding column 'status'...")
            cursor.execute("ALTER TABLE sales ADD COLUMN status VARCHAR(20) DEFAULT 'completed' NOT NULL")
            print("Added 'status' column.")

        # Check cancelled_at column
        try:
            cursor.execute("SELECT cancelled_at FROM sales LIMIT 1")
            print("Column 'cancelled_at' already exists.")
        except sqlite3.OperationalError:
            print("Adding column 'cancelled_at'...")
            cursor.execute("ALTER TABLE sales ADD COLUMN cancelled_at DATETIME")
            print("Added 'cancelled_at' column.")
            
        conn.commit()
        print("Migration successful.")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_cancel_columns()
