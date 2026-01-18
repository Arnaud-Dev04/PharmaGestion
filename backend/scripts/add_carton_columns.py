import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "pharmacy_local.db")

def add_columns():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Add boxes_per_carton column
        try:
            cursor.execute("ALTER TABLE medicines ADD COLUMN boxes_per_carton INTEGER DEFAULT 1")
            print("Added column: boxes_per_carton")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("Column boxes_per_carton already exists")
            else:
                print(f"Error adding boxes_per_carton: {e}")

        # Add carton_type column
        try:
            cursor.execute("ALTER TABLE medicines ADD COLUMN carton_type TEXT DEFAULT 'Carton'")
            print("Added column: carton_type")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("Column carton_type already exists")
            else:
                print(f"Error adding carton_type: {e}")

        conn.commit()
        print("Migration completed successfully.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_columns()
