import sqlite3

DB_PATH = "pharmacy_local.db"

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        print("Checking restock_items table...")
        cursor.execute("PRAGMA table_info(restock_items)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if "expiry_date" not in columns:
            print("Adding expiry_date column...")
            cursor.execute("ALTER TABLE restock_items ADD COLUMN expiry_date DATE")
            conn.commit()
            print("Success.")
        else:
            print("Column expiry_date already exists.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
