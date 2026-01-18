
import sqlite3
import os

DB_FILE = "pharmacy_local.db"

def fix_roles():
    if not os.path.exists(DB_FILE):
        print(f"Database {DB_FILE} not found.")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        # Normalize PHARMACIST -> pharmacist
        print("Normalizing 'PHARMACIST' to 'pharmacist'...")
        cursor.execute("UPDATE users SET role = 'pharmacist' WHERE role = 'PHARMACIST'")
        print(f"Updated {cursor.rowcount} pharmacists.")

        # Normalize ADMIN -> admin
        print("Normalizing 'ADMIN' to 'admin'...")
        cursor.execute("UPDATE users SET role = 'admin' WHERE role = 'ADMIN'")
        print(f"Updated {cursor.rowcount} admins.")
        
        # Verify
        cursor.execute("SELECT username, role FROM users")
        users = cursor.fetchall()
        print("\nCurrent Users:")
        for u in users:
            print(f"- {u[0]}: {u[1]}")

        conn.commit()
    except Exception as e:
        print(f"Error: {e}")

    conn.close()

if __name__ == "__main__":
    fix_roles()
