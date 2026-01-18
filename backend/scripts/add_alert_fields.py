
import sqlite3
import os

DB_FILE = "pharmacy_local.db"

def add_alert_columns():
    if not os.path.exists(DB_FILE):
        print(f"Database {DB_FILE} not found.")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Columns to ensure exist
    # name, type, default value
    columns_to_add = [
        ("min_stock_alert", "INTEGER", "10"),
        ("expiry_alert_threshold", "INTEGER", "30")
    ]

    for col_name, col_type, default_val in columns_to_add:
        try:
            print(f"Attempting to add column {col_name}...")
            # SQLite doesn't support IF NOT EXISTS for ADD COLUMN directly in all versions, 
            # but we can try and catch the error.
            cursor.execute(f"ALTER TABLE medicines ADD COLUMN {col_name} {col_type} DEFAULT {default_val}")
            print(f"Column {col_name} added successfully.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"Column {col_name} already exists. Updating nulls to default...")
                # Update NULLs to default if it exists
                cursor.execute(f"UPDATE medicines SET {col_name} = {default_val} WHERE {col_name} IS NULL")
            else:
                print(f"Error adding {col_name}: {e}")

    conn.commit()
    conn.close()
    print("Alert fields migration completed.")

if __name__ == "__main__":
    add_alert_columns()
