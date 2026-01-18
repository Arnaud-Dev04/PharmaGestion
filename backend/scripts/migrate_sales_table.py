"""
Migrate the sales table to add missing columns.
Run this ONCE to update existing database without losing data.
"""

import sqlite3
import os
import sys

def migrate_sales_table():
    """Add missing columns to sales table."""
    
    # APPDATA database path
    db_path = os.path.join(os.environ.get('APPDATA', ''), 'PharmaGestion', 'pharmacy_local.db')
    
    if not os.path.exists(db_path):
        print(f"[ERROR] Database not found at: {db_path}")
        return False
    
    print(f"[*] Migrating APPDATA database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get existing columns
        cursor.execute("PRAGMA table_info(sales)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"[DEBUG] Existing columns: {columns}")
        
        migrations_done = []
        
        # Add status column if missing
        if 'status' not in columns:
            print("[*] Adding column 'status'...")
            cursor.execute("""
                ALTER TABLE sales 
                ADD COLUMN status VARCHAR(20) DEFAULT 'completed' NOT NULL
            """)
            migrations_done.append('status')
        else:
            print("[OK] Column 'status' already exists")
        
        # Add cancelled_at column if missing
        if 'cancelled_at' not in columns:
            print("[*] Adding column 'cancelled_at'...")
            cursor.execute("""
                ALTER TABLE sales 
                ADD COLUMN cancelled_at DATETIME
            """)
            migrations_done.append('cancelled_at')
        else:
            print("[OK] Column 'cancelled_at' already exists")
        
        # Add cancelled_by column if missing
        if 'cancelled_by' not in columns:
            print("[*] Adding column 'cancelled_by'...")
            cursor.execute("""
                ALTER TABLE sales 
                ADD COLUMN cancelled_by INTEGER
            """)
            migrations_done.append('cancelled_by')
        else:
            print("[OK] Column 'cancelled_by' already exists")
        
        # Add insurance_provider column if missing
        if 'insurance_provider' not in columns:
            print("[*] Adding column 'insurance_provider'...")
            cursor.execute("""
                ALTER TABLE sales 
                ADD COLUMN insurance_provider VARCHAR(100)
            """)
            migrations_done.append('insurance_provider')
        else:
            print("[OK] Column 'insurance_provider' already exists")
        
        # Add insurance_card_id column if missing
        if 'insurance_card_id' not in columns:
            print("[*] Adding column 'insurance_card_id'...")
            cursor.execute("""
                ALTER TABLE sales 
                ADD COLUMN insurance_card_id VARCHAR(50)
            """)
            migrations_done.append('insurance_card_id')
        else:
            print("[OK] Column 'insurance_card_id' already exists")
        
        # Add coverage_percent column if missing
        if 'coverage_percent' not in columns:
            print("[*] Adding column 'coverage_percent'...")
            cursor.execute("""
                ALTER TABLE sales 
                ADD COLUMN coverage_percent FLOAT DEFAULT 0.0
            """)
            migrations_done.append('coverage_percent')
        else:
            print("[OK] Column 'coverage_percent' already exists")
        
        if migrations_done:
            conn.commit()
            print(f"[OK] Migration successful! Added columns: {', '.join(migrations_done)}")
        else:
            print("[OK] No migration needed. All columns already exist.")
        
        # Verify all columns were added
        cursor.execute("PRAGMA table_info(sales)")
        updated_columns = [column[1] for column in cursor.fetchall()]
        
        required_columns = ['status', 'cancelled_at', 'cancelled_by', 'insurance_provider', 'insurance_card_id', 'coverage_percent']
        missing = [col for col in required_columns if col not in updated_columns]
        
        if missing:
            print(f"[ERROR] Verification failed! Missing columns: {missing}")
            return False
        else:
            print("[OK] Verification passed. All required columns exist.")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("SALES TABLE MIGRATION")
    print("Adding missing columns to sales table")
    print("=" * 60)
    print()
    
    success = migrate_sales_table()
    
    print()
    if success:
        print("[SUCCESS] Migration completed!")
    else:
        print("[FAILED] Migration failed!")
    
    input("\nPress Enter to exit...")
