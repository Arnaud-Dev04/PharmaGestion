"""
Script to check and update license expiry date
"""
import sqlite3
import os
from datetime import date, timedelta

# Database path
DB_PATH = 'pharmacy_local.db'

def check_and_update_license():
    print(f"[*] Connecting to: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check current license
    cursor.execute("SELECT value FROM settings WHERE key = 'license_expiry_date'")
    result = cursor.fetchone()
    
    if result:
        current_expiry = result[0]
        print(f"[*] Current license expiry: {current_expiry}")
    else:
        current_expiry = None
        print("[*] No license expiry date found in database")
    
    # Set to 1 year from now
    new_expiry = (date.today() + timedelta(days=365)).isoformat()
    print(f"[*] Setting new expiry date: {new_expiry}")
    
    if result:
        cursor.execute("UPDATE settings SET value = ? WHERE key = 'license_expiry_date'", (new_expiry,))
    else:
        cursor.execute("INSERT INTO settings (key, value) VALUES ('license_expiry_date', ?)", (new_expiry,))
    
    conn.commit()
    conn.close()
    
    print("[OK] License updated successfully!")
    print(f"[OK] New expiry date: {new_expiry}")

if __name__ == "__main__":
    check_and_update_license()
