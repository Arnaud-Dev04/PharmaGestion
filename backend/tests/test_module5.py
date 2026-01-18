"""
Automated test script for Module 5: Dashboard & History.
RUN AFTER Module 3 & 4 tests (requires data).
"""

import requests
import json
from datetime import date, timedelta, datetime

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# Colors for output (Removed for Windows compatibility)
GREEN = ""
RED = ""
YELLOW = ""
BLUE = ""
RESET = ""


class TestModule5:
    def __init__(self):
        self.admin_token = None
        self.test_results = []
        self.user_id = None
        
    def print_header(self, text):
        print(f"\n{'=' * 60}")
        print(f"{text}")
        print(f"{'=' * 60}\n")
    
    def print_test(self, test_name, passed, details=""):
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] - {test_name}")
        if details:
            print(f"   Details: {details}")
        self.test_results.append((test_name, passed))
    
    def login_admin(self):
        self.print_header("1. LOGIN ADMIN")
        try:
            response = requests.post(f"{BASE_URL}/auth/login", data={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD})
            if response.status_code == 200:
                self.admin_token = response.json()["access_token"]
                
                # Get user info to find ID
                me_resp = requests.get(f"{BASE_URL}/auth/me", headers=self.get_headers())
                if me_resp.status_code == 200:
                    self.user_id = me_resp.json()["id"]
                    
                self.print_test("Admin login", True, f"Token received, User ID: {self.user_id}")
                return True
            else:
                self.print_test("Admin login", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Admin login", False, f"Exception: {str(e)}")
            return False
            
    def get_headers(self):
        return {"Authorization": f"Bearer {self.admin_token}", "Content-Type": "application/json"}

    def test_dashboard_stats(self):
        """Test dashboard statistics endpoint."""
        self.print_header("2. DASHBOARD STATISTICS")
        
        response = requests.get(f"{BASE_URL}/dashboard/stats", headers=self.get_headers())
        
        passed = response.status_code == 200
        if passed:
            data = response.json()
            
            # Verify specific keys exist
            keys = ["total_medicines", "sales_this_week", "medicines_expired", "medicines_low_stock", "revenue_chart"]
            all_keys = all(k in data for k in keys)
            
            if all_keys:
                self.print_test("Stats keys present", True)
                self.print_test("Total Medicines", True, f"Count: {data['total_medicines']}")
                self.print_test("Sales This Week", True, f"Amount: {data['sales_this_week']}")
                self.print_test("Low Stock Alerts", True, f"Count: {data['medicines_low_stock']}")
                
                # Verify chart data
                chart = data["revenue_chart"]
                if isinstance(chart, list) and len(chart) > 0:
                    self.print_test("Revenue Chart Data", True, f"{len(chart)} days returned")
                else:
                    self.print_test("Revenue Chart Data", False, "Empty or invalid list")
            else:
                self.print_test("Stats keys present", False, f"Missing keys. Got: {list(data.keys())}")
        else:
            self.print_test("Get stats endpoint", False, f"Status: {response.status_code}")

    def test_sales_history_basic(self):
        """Test sales history list."""
        self.print_header("3. SALES HISTORY - BASIC")
        
        response = requests.get(f"{BASE_URL}/sales/history", headers=self.get_headers())
        
        passed = response.status_code == 200
        if passed:
            data = response.json()
            total = data.get("total", 0)
            items = data.get("items", [])
            
            self.print_test("Get history endpoint", True, f"Total records: {total}")
            
            if len(items) > 0:
                first = items[0]
                has_enriched = "items" in first
                if has_enriched:
                    self.print_test("History items enriched", True, "Contains medicine details")
                else:
                    self.print_test("History items enriched", False, f"Keys: {list(first.keys())}")
        else:
            self.print_test("Get history endpoint", False, f"Status: {response.status_code}")

    def test_sales_history_filters(self):
        """Test filters on sales history."""
        self.print_header("4. SALES HISTORY - FILTERS")
        
        # 1. Test Date Filter (Today)
        today = date.today().isoformat()
        response = requests.get(f"{BASE_URL}/sales/history?start_date={today}&end_date={today}", headers=self.get_headers())
        
        if response.status_code == 200:
            count = response.json()["total"]
            self.print_test(f"Filter by date ({today})", True, f"Found {count} sales")
            
        # 2. Test User Filter
        if self.user_id:
            response = requests.get(f"{BASE_URL}/sales/history?user_id={self.user_id}", headers=self.get_headers())
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                if items:
                    # Verify all returned sales belong to this user
                    all_correct = all(s["user_id"] == self.user_id for s in items)
                    self.print_test(f"Filter by user ID {self.user_id}", all_correct, f"Found {data['total']} sales. All match: {all_correct}")
                else:
                     self.print_test(f"Filter by user ID {self.user_id}", True, "No sales found for user (acceptable if empty DB)")

        # 3. Test Amount Filter (Min Amount)
        min_amt = 1000
        response = requests.get(f"{BASE_URL}/sales/history?min_amount={min_amt}", headers=self.get_headers())
        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])
            if items:
                # Verify amounts
                all_correct = all(s["total_amount"] >= min_amt for s in items)
                failed_items = [s["total_amount"] for s in items if s["total_amount"] < min_amt]
                self.print_test(f"Filter min_amount >= {min_amt}", all_correct, f"Found {data['total']} sales. Failures: {failed_items}")
            else:
                self.print_test(f"Filter min_amount >= {min_amt}", True, "No sales found > 1000")

    def print_summary(self):
        self.print_header("TEST SUMMARY")
        total = len(self.test_results)
        passed = sum(1 for _, p in self.test_results if p)
        failed = total - passed
        print(f"Total: {total}, Passed: {passed}, Failed: {failed}")

if __name__ == "__main__":
    tester = TestModule5()
    if tester.login_admin():
        tester.test_dashboard_stats()
        tester.test_sales_history_basic()
        tester.test_sales_history_filters()
        tester.print_summary()
