
import sqlite3
import os

DB_FILE = "pharmacy_local.db"

def add_columns():
    if not os.path.exists(DB_FILE):
        print(f"Database {DB_FILE} not found.")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    columns_to_add = [
        ("sale_type", "TEXT DEFAULT 'packaging'"),
        ("discount_percent", "REAL DEFAULT 0.0")
    ]

    for col_name, col_type in columns_to_add:
        try:
            print(f"Adding column {col_name} to sale_items...")
            cursor.execute(f"ALTER TABLE sale_items ADD COLUMN {col_name} {col_type}")
            print(f"Column {col_name} added successfully.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"Column {col_name} already exists.")
            else:
                print(f"Error adding {col_name}: {e}")

    conn.commit()
    conn.close()
    print("Migration completed.")

if __name__ == "__main__":
    add_columns()
