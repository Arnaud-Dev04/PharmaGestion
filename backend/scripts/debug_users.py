
import sqlite3
import os

DB_FILE = "pharmacy_local.db"

def list_users():
    if not os.path.exists(DB_FILE):
        print(f"Database {DB_FILE} not found.")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, username, role, is_active FROM users")
        users = cursor.fetchall()
        print(f"{'ID':<5} {'Username':<20} {'Role':<15} {'Active':<10}")
        print("-" * 50)
        for u in users:
            print(f"{u[0]:<5} {u[1]:<20} {u[2]:<15} {u[3]:<10}")
    except Exception as e:
        print(f"Error: {e}")

    conn.close()

if __name__ == "__main__":
    list_users()
