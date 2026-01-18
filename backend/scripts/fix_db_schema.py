import sqlite3
import os
import sys

# Default to local DB for dev environment, matching app/database/core.py behavior when not frozen
DB_FILE = "pharmacy_local.db"

def fix_database_schema():
    if not os.path.exists(DB_FILE):
        print(f"Database {DB_FILE} not found in current directory. Checking AppData...")
        # Fallback/Check AppData just in case
        app_data = os.getenv('APPDATA')
        if app_data:
            alt_db = os.path.join(app_data, "PharmaGestion", "pharmacy_local.db")
            if os.path.exists(alt_db):
                print(f"Found database in AppData: {alt_db}")
                # We could fix this one too, or Ask. For now, let's fix the one we found.
                # But since the user is running from local dir, we MUST fix the local one if it exists.
                pass 
    
    if not os.path.exists(DB_FILE):
         print(f"Error: {DB_FILE} not found in {os.getcwd()}")
         return
    if not os.path.exists(DB_FILE):
        print(f"Database {DB_FILE} not found. Nothing to fix.")
        return

    print(f"Opening database: {DB_FILE}")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # 1. Fix Medicines Table
    print("Checking 'medicines' table...")
    medicine_columns = [
        ("min_stock_alert", "INTEGER", "10"),
        ("expiry_alert_threshold", "INTEGER", "30")
    ]
    
    for col_name, col_type, default_val in medicine_columns:
        try:
            print(f"  Attempting to add column '{col_name}'...")
            cursor.execute(f"ALTER TABLE medicines ADD COLUMN {col_name} {col_type} DEFAULT {default_val}")
            print(f"  Column '{col_name}' added successfully.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"  Column '{col_name}' already exists.")
                # Update NULLs to default
                cursor.execute(f"UPDATE medicines SET {col_name} = {default_val} WHERE {col_name} IS NULL")
            else:
                print(f"  Error adding '{col_name}': {e}")

    # 2. Fix Sales Table
    print("Checking 'sales' table...")
    sales_columns = [
        ("cancelled_by", "INTEGER", "NULL"),
        ("status", "VARCHAR(20)", "'completed'"),
        ("cancelled_at", "DATETIME", "NULL")
    ]

    for col_name, col_type, default_val in sales_columns:
        try:
            print(f"  Attempting to add column '{col_name}'...")
            cursor.execute(f"ALTER TABLE sales ADD COLUMN {col_name} {col_type} DEFAULT {default_val}")
            print(f"  Column '{col_name}' added successfully.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"  Column '{col_name}' already exists.")
            else:
                print(f"  Error adding '{col_name}': {e}")

    conn.commit()
    conn.close()
    print("Database schema fix completed successfully.")

if __name__ == "__main__":
    fix_database_schema()
