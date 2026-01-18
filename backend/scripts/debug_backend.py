import os
import sys
import sqlite3
import datetime
import requests

# Configuration
DB_PATH = "pharmacy_local.db"
API_URL = "http://localhost:8000"

def log(msg, status="INFO"):
    colors = {
        "INFO": "\033[94m", # Blue
        "SUCCESS": "\033[92m", # Green
        "WARNING": "\033[93m", # Yellow
        "ERROR": "\033[91m", # Red
        "RESET": "\033[0m"
    }
    prefix = f"{colors.get(status, '')}[{status}]{colors['RESET']}"
    print(f"{prefix} {msg}")

def check_database():
    log("Checking Database Connection...")
    if not os.path.exists(DB_PATH):
        log(f"Database file not found at {DB_PATH}", "ERROR")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check Tables
        tables = ["users", "medicines", "sales", "sale_items", "settings"]
        for table in tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if not cursor.fetchone():
                log(f"Table '{table}' MISSING!", "ERROR")
            else:
                log(f"Table '{table}' found.", "SUCCESS")

        # Check Critical Columns
        # Medicine hierarchy
        cursor.execute("PRAGMA table_info(medicines)")
        columns = [row[1] for row in cursor.fetchall()]
        required_cols = ["boxes_per_carton", "units_per_packaging", "price_sell"]
        for col in required_cols:
            if col not in columns:
                log(f"Column '{col}' missing in medicines table!", "ERROR")
            else:
                log(f"Column '{col}' exists in medicines.", "SUCCESS")
                
        conn.close()
        return True
    except Exception as e:
        log(f"Database Error: {e}", "ERROR")
        return False

def check_users():
    log("\nChecking Users...")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT username, role, is_active FROM users")
        users = cursor.fetchall()
        
        if not users:
            log("No users found in database!", "WARNING")
        else:
            for u in users:
                status = "Active" if u[2] else "Inactive"
                log(f"User: {u[0]} | Role: {u[1]} | Status: {status}", "INFO")
                
        conn.close()
    except Exception as e:
        log(f"User Check Error: {e}", "ERROR")

def check_stock_integrity():
    log("\nChecking Stock Integrity...")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check for zero or negative prices/units
        cursor.execute("SELECT name FROM medicines WHERE units_per_packaging <= 0 OR price_sell < 0")
        bad_medicines = cursor.fetchall()
        if bad_medicines:
             log(f"Found {len(bad_medicines)} medicines with invalid units/price!", "WARNING")
             for m in bad_medicines[:5]:
                 log(f" - {m[0]}", "WARNING")
        else:
            log("Medicine integrity looks valid.", "SUCCESS")
            
        conn.close()
    except Exception as e:
        log(f"Stock Check Error: {e}", "ERROR")

def check_api_health():
    log("\nChecking API Health (if running)...")
    try:
        resp = requests.get(f"{API_URL}/health", timeout=2)
        if resp.status_code == 200:
             log("API is RUNNING and Healthy.", "SUCCESS")
        else:
             log(f"API returned status {resp.status_code}", "WARNING")
    except:
        log("API is NOT responsive (make sure uvicorn is running).", "WARNING")

if __name__ == "__main__":
    print("==========================================")
    print("   PHARMA SOFTWARE - BACKEND DIAGNOSTICS")
    print("==========================================\n")
    
    db_ok = check_database()
    if db_ok:
        check_users()
        check_stock_integrity()
    
    check_api_health()
    
    print("\n==========================================")
    print("   DIAGNOSTICS COMPLETE")
    print("==========================================")
