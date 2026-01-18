
import sqlite3
import os

DB_FILE = "pharmacy_local.db"

def fix_admin():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        print("Updating admin user role to 'admin'...")
        cursor.execute("UPDATE users SET role='admin' WHERE username='admin'")
        
        if cursor.rowcount == 0:
            print("User 'admin' not found. Creating it.")
            # Create if not exists (fail-safe, though unlikely needed if login worked)
            # Hash for 'admin123'
            pwd_hash = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW" 
            cursor.execute("INSERT INTO users (username, password_hash, role, is_active) VALUES (?, ?, ?, ?)", 
                           ('admin', pwd_hash, 'admin', 1)) 
        else:
            print(f"Updated {cursor.rowcount} row(s).")
            
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")

    conn.close()

if __name__ == "__main__":
    fix_admin()
