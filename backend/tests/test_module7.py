"""
Automated test script for Module 7: Reports.
"""

import requests
import os
from datetime import date

# Configuration
BASE_URL = "http://localhost:8002" # Using port 8002 as confirmed in previous steps
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

class TestModule7:
    def __init__(self):
        self.token = None
        
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
             self.print_test("Login", False, f"Connection error: {str(e)}")
             return False

    def get_headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    def test_stock_excel(self):
        print("\n=== 2. Stock Excel Report ===")
        url = f"{BASE_URL}/reports/stock/excel"
        r = requests.get(url, headers=self.get_headers())
        
        if r.status_code == 200:
            content_type = r.headers.get("content-type", "")
            size = len(r.content)
            is_valid = "spreadsheet" in content_type or "excel" in content_type or size > 0
            
            self.print_test("Download Stock Excel", is_valid, f"Size: {size} bytes, Type: {content_type}")
            
            # Save for manual inspection
            with open("test_report_stock.xlsx", "wb") as f:
                f.write(r.content)
        else:
            self.print_test("Download Stock Excel", False, f"Status {r.status_code}")

    def test_sales_excel(self):
        print("\n=== 3. Sales Excel Report ===")
        today = date.today().isoformat()
        url = f"{BASE_URL}/reports/sales/excel?start_date={today}&end_date={today}"
        r = requests.get(url, headers=self.get_headers())
        
        if r.status_code == 200:
            size = len(r.content)
            self.print_test("Download Sales Excel", True, f"Size: {size} bytes")
             # Save for manual inspection
            with open("test_report_sales.xlsx", "wb") as f:
                f.write(r.content)
        else:
             self.print_test("Download Sales Excel", False, f"Status {r.status_code}")

    def test_financial_pdf(self):
        print("\n=== 4. Financial PDF Report ===")
        url = f"{BASE_URL}/reports/financial/pdf?period=month"
        r = requests.get(url, headers=self.get_headers())
        
        if r.status_code == 200:
            content_type = r.headers.get("content-type", "")
            size = len(r.content)
            is_pdf = "pdf" in content_type and size > 0
            
            self.print_test("Download Financial PDF", is_pdf, f"Size: {size} bytes, Type: {content_type}")
             # Save for manual inspection
            with open("test_report_financial.pdf", "wb") as f:
                f.write(r.content)
        else:
            self.print_test("Download Financial PDF", False, f"Status {r.status_code}")

if __name__ == "__main__":
    test = TestModule7()
    if test.login():
        test.test_stock_excel()
        test.test_sales_excel()
        test.test_financial_pdf()
