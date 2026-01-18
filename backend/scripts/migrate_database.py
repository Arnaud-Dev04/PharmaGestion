"""
Database migration script to add missing expiry_alert_threshold column.
Run this ONCE to update existing database without losing data.
"""

import sqlite3
import os
import sys

def migrate_database():
    """Add expiry_alert_threshold column to medicines table if it doesn't exist."""
    
    # Determine database path
    if getattr(sys, "frozen", False):
        # Running as compiled executable
        db_path = os.path.join(os.environ.get('APPDATA', '.'), 'PharmaGestion', 'pharmacy_local.db')
    else:
        # Running as Python script
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'pharmacy_local.db')
    
    if not os.path.exists(db_path):
        print(f"[ERROR] Database not found at: {db_path}")
        return False
    
    print(f"[*] Migrating database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(medicines)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'expiry_alert_threshold' in columns:
            print("[OK] Column 'expiry_alert_threshold' already exists. No migration needed.")
            conn.close()
            return True
        
        # Add the missing column with a default value of 30 days
        print("[*] Adding column 'expiry_alert_threshold' to medicines table...")
        cursor.execute("""
            ALTER TABLE medicines 
            ADD COLUMN expiry_alert_threshold INTEGER DEFAULT 30
        """)
        
        conn.commit()
        print("[OK] Migration successful! Column added with default value of 30 days.")
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(medicines)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'expiry_alert_threshold' in columns:
            print("[OK] Verification passed. Column exists in database.")
        else:
            print("[ERROR] Verification failed. Column not found after migration.")
            return False
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("DATABASE MIGRATION SCRIPT")
    print("Adding expiry_alert_threshold column to medicines table")
    print("=" * 60)
    print()
    
    success = migrate_database()
    
    print()
    if success:
        print("[SUCCESS] Database migration completed successfully!")
    else:
        print("[FAILED] Database migration failed. Please check errors above.")
    
    input("\nPress Enter to exit...")
