"""
Migration script to add missing columns to medicines table.
Adds: expiry_alert_threshold and is_active columns
"""

import sqlite3
import os

# Database path (local user database)
DB_PATH = os.path.join(os.environ.get('APPDATA', '.'), 'PharmaGestion', 'pharmacy_local.db')

def migrate():
    print(f"[*] Connecting to database: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] Database file not found: {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(medicines)")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Add expiry_alert_threshold if missing
        if 'expiry_alert_threshold' not in columns:
            print("[*] Adding column: expiry_alert_threshold")
            cursor.execute("""
                ALTER TABLE medicines 
                ADD COLUMN expiry_alert_threshold INTEGER DEFAULT 30 NOT NULL
            """)
            print("[OK] Column expiry_alert_threshold added")
        else:
            print("[SKIP] Column expiry_alert_threshold already exists")
        
        # Add is_active if missing
        if 'is_active' not in columns:
            print("[*] Adding column: is_active")
            cursor.execute("""
                ALTER TABLE medicines 
                ADD COLUMN is_active INTEGER DEFAULT 1 NOT NULL
            """)
            print("[OK] Column is_active added")
        else:
            print("[SKIP] Column is_active already exists")
        
        conn.commit()
        print("[OK] Migration completed successfully!")
        
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
