
import sqlite3
import os

DB_FILE = "pharmacy_local.db"

def check_schema():
    if not os.path.exists(DB_FILE):
        print(f"Database {DB_FILE} not found.")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        print("Checking sale_items schema...")
        cursor.execute("PRAGMA table_info(sale_items)")
        columns = cursor.fetchall()
        print(f"{'CID':<5} {'Name':<20} {'Type':<15} {'NotNull':<10}")
        print("-" * 50)
        found_sale_type = False
        found_discount = False
        
        for col in columns:
            print(f"{col[0]:<5} {col[1]:<20} {col[2]:<15} {col[3]:<10}")
            if col[1] == 'sale_type':
                found_sale_type = True
            if col[1] == 'discount_percent':
                found_discount = True
                
        print("-" * 50)
        if found_sale_type and found_discount:
            print("[OK] Columns 'sale_type' and 'discount_percent' found.")
        else:
            print("[ERROR] MISSING COLUMNS!")
            if not found_sale_type: print("- Missing sale_type")
            if not found_discount: print("- Missing discount_percent")

    except Exception as e:
        print(f"Error: {e}")

    conn.close()

if __name__ == "__main__":
    check_schema()
