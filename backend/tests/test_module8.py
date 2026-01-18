"""
Automated test script for Module 8: Settings & I18n.
"""

import requests
import sys
import os

# Add parent directory to path to import app utils directly for unit testing i18n
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.utils.i18n import get_message

# Configuration
BASE_URL = "http://localhost:8003" 
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

class TestModule8:
    def __init__(self):
        self.token = None
        
    def print_test(self, name, passed, details=""):
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] - {name}")
        if details and not passed:
            print(f"   Details: {details}")

    def test_i18n_util(self):
        print("\n=== 1. I18n Utility Unit Test ===")
        msg_fr = get_message("error_stock_insufficient", "fr")
        msg_en = get_message("error_stock_insufficient", "en")
        
        passed_fr = "Stock insuffisant" in msg_fr
        passed_en = "Insufficient stock" in msg_en
        
        self.print_test("French Translation", passed_fr, f"Got: {msg_fr}")
        self.print_test("English Translation", passed_en, f"Got: {msg_en}")
        
        # Test fallback
        msg_fallback = get_message("error_stock_insufficient", "es") # Should be FR default
        passed_fb = "Stock insuffisant" in msg_fallback
        self.print_test("Fallback to Default", passed_fb, f"Got: {msg_fallback}")

    def login(self):
        print("\n=== 2. Login ===")
        try:
            r = requests.post(f"{BASE_URL}/auth/login", data={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD})
            if r.status_code == 200:
                self.token = r.json()["access_token"]
                self.print_test("Login", True)
                return True
            else:
                self.print_test("Login", False, f"Status {r.status_code}")
                return False
        except Exception as e:
             self.print_test("Login", False, f"Connection error: {str(e)}")
             return False

    def get_headers(self):
        return {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

    def test_settings_api(self):
        print("\n=== 3. Settings API ===")
        
        # 1. Update Settings
        new_settings = {
            "pharmacy_name": "Pharmacie de Test",
            "bonus_percentage": 5.5,
            "currency": "USD"
        }
        r_put = requests.put(f"{BASE_URL}/settings", json=new_settings, headers=self.get_headers())
        if r_put.status_code == 200:
            resp = r_put.json()
            is_updated = (
                resp["pharmacy_name"] == "Pharmacie de Test" and 
                resp["bonus_percentage"] == 5.5 and
                resp["currency"] == "USD"
            )
            self.print_test("Update Settings", is_updated, f"Resp: {resp}")
        else:
            self.print_test("Update Settings", False, f"Status {r_put.status_code}")
            
        # 2. Get Settings (Verify Persistence)
        r_get = requests.get(f"{BASE_URL}/settings", headers=self.get_headers())
        if r_get.status_code == 200:
            resp = r_get.json()
            is_persisted = (
                resp["pharmacy_name"] == "Pharmacie de Test" and 
                resp["bonus_percentage"] == 5.5
            )
            self.print_test("Get Settings (Persistence)", is_persisted, f"Resp: {resp}")
        else:
            self.print_test("Get Settings", False, f"Status {r_get.status_code}")

if __name__ == "__main__":
    test = TestModule8()
    test.test_i18n_util()
    if test.login():
        test.test_settings_api()
