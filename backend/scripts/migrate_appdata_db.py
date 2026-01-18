"""
Migrate the APPDATA database (used by compiled backend).
"""

import sqlite3
import os

def migrate_appdata_database():
    """Add expiry_alert_threshold column to medicines table in APPDATA."""
    
    # APPDATA database path
    db_path = os.path.join(os.environ.get('APPDATA', ''), 'PharmaGestion', 'pharmacy_local.db')
    
    if not os.path.exists(db_path):
        print(f"[ERROR] Database not found at: {db_path}")
        return False
    
    print(f"[*] Migrating APPDATA database: {db_path}")
    
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
        
        # Add the missing column
        print("[*] Adding column 'expiry_alert_threshold' to medicines table...")
        cursor.execute("""
            ALTER TABLE medicines 
            ADD COLUMN expiry_alert_threshold INTEGER DEFAULT 30
        """)
        
        conn.commit()
        print("[OK] Migration successful! Column added with default value of 30 days.")
        
        # Verify
        cursor.execute("PRAGMA table_info(medicines)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'expiry_alert_threshold' in columns:
            print("[OK] Verification passed!")
        else:
            print("[ERROR] Verification failed!")
            return False
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("APPDATA DATABASE MIGRATION")
    print("=" * 60)
    print()
    
    success = migrate_appdata_database()
    
    print()
    if success:
        print("[SUCCESS] Migration completed!")
    else:
        print("[FAILED] Migration failed!")
    
    input("\nPress Enter to exit...")
