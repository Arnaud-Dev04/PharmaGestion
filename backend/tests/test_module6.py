"""
Automated test script for Module 6: Restocking.
"""

import requests
import json
from datetime import date

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# Colors (No color for Windows)
GREEN = ""
RED = ""
YELLOW = ""
RESET = ""

class TestModule6:
    def __init__(self):
        self.token = None
        self.medicine_id = None
        self.supplier_id = None
        self.initial_quantity = 0
        self.order_id = None
        
    def print_test(self, name, passed, details=""):
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] - {name}")
        if details and not passed:
            print(f"   Details: {details}")

    def login(self):
        print("\n=== 1. Login ===")
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
             self.print_test("Login", False, str(e))
             return False

    def get_headers(self):
        return {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

    def setup_data(self):
        print("\n=== 2. Setup Data (Get Medicine & Supplier) ===")
        # Get a medicine
        r_med = requests.get(f"{BASE_URL}/medicines?page=1&page_size=1", headers=self.get_headers())
        if r_med.status_code == 200 and len(r_med.json()["items"]) > 0:
            med = r_med.json()["items"][0]
            self.medicine_id = med["id"]
            self.initial_quantity = med["quantity"]
            self.print_test("Get Medicine", True, f"ID: {self.medicine_id}, Stock: {self.initial_quantity}")
        else:
            self.print_test("Get Medicine", False, "No medicine found")
            return False

        # Get a supplier
        r_sup = requests.get(f"{BASE_URL}/suppliers?page=1&page_size=1", headers=self.get_headers())
        if r_sup.status_code == 200 and len(r_sup.json()["items"]) > 0:
            sup = r_sup.json()["items"][0]
            self.supplier_id = sup["id"]
            self.print_test("Get Supplier", True, f"ID: {self.supplier_id}")
        else:
            self.print_test("Get Supplier", False, "No supplier found")
            return False
            
        return True

    def test_low_stock(self):
        print("\n=== 3. Test Low Stock Endpoint ===")
        r = requests.get(f"{BASE_URL}/restock/low-stock", headers=self.get_headers())
        if r.status_code == 200:
            items = r.json()
            # Just verify it returns a list
            self.print_test("Low Stock List", True, f"Count: {len(items)}")
        else:
            self.print_test("Low Stock List", False, f"Status {r.status_code}")

    def test_create_order(self):
        print("\n=== 4. Create Draft Order ===")
        data = {
            "supplier_id": self.supplier_id,
            "items": [
                {
                    "medicine_id": self.medicine_id,
                    "quantity": 10,
                    "price_buy": 500
                }
            ]
        }
        r = requests.post(f"{BASE_URL}/restock/create", json=data, headers=self.get_headers())
        
        if r.status_code == 200:
            order = r.json()
            self.order_id = order["id"]
            is_draft = order["status"] == "draft"
            self.print_test("Create Order", is_draft, f"ID: {self.order_id}, Status: {order['status']}")
            return is_draft
        else:
            self.print_test("Create Order", False, f"Status {r.status_code}")
            return False

    def test_confirm_order(self):
        print("\n=== 5. Confirm Order & Check Stock ===")
        if not self.order_id:
            self.print_test("Confirm Order", False, "No order ID")
            return

        r = requests.post(f"{BASE_URL}/restock/{self.order_id}/confirm", headers=self.get_headers())
        if r.status_code == 200:
            order = r.json()
            is_confirmed = order["status"] == "confirmed"
            self.print_test("Confirm Status", is_confirmed, f"New Status: {order['status']}")
            
            # Use enrichment or get medicine again
            r_med = requests.get(f"{BASE_URL}/medicines/{self.medicine_id}", headers=self.get_headers())
            if r_med.status_code == 200:
                new_qty = r_med.json()["quantity"]
                expected = self.initial_quantity + 10
                is_updated = new_qty == expected
                self.print_test("Stock Update", is_updated, f"Old: {self.initial_quantity}, Added: 10, New: {new_qty}")
            else:
                self.print_test("Stock Update", False, "Could not fetch medicine")
        else:
            self.print_test("Confirm Order", False, f"Status {r.status_code}: {r.text}")


if __name__ == "__main__":
    test = TestModule6()
    if test.login():
        if test.setup_data():
            test.test_low_stock()
            if test.test_create_order():
                test.test_confirm_order()
