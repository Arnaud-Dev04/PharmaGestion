"""
Automated test script for Module 4: Point de Vente (POS).
Run this script to validate all Module 4 functionalities.
"""

import requests
import json
from datetime import date, timedelta

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


class TestModule4:
    def __init__(self):
        self.admin_token = None
        self.test_results = []
        self.medicine_ids = []
        self.sale_ids = []
        self.customer_phone = "+25779999999"
    
    def print_header(self, text):
        print(f"\n{BLUE}{'=' * 60}")
        print(f"{text}")
        print(f"{'=' * 60}{RESET}\n")
    
    def print_test(self, test_name, passed, details=""):
        status = f"{GREEN}[PASS]{RESET}" if passed else f"{RED}[FAIL]{RESET}"
        print(f"{status} - {test_name}")
        if details:
            print(f"   {YELLOW}{details}{RESET}")
        self.test_results.append((test_name, passed))
    
    def login_admin(self):
        """Login as admin and get token."""
        self.print_header("1. LOGIN ADMIN")
        
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data={
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD
            }
        )
        
        passed = response.status_code == 200
        if passed:
            self.admin_token = response.json()["access_token"]
            self.print_test("Admin login", True, f"Token received")
        else:
            self.print_test("Admin login", False, f"Status: {response.status_code}")
        
        return passed
    
    def get_headers(self):
        """Get authorization headers."""
        return {
            "Authorization": f"Bearer {self.admin_token}",
            "Content-Type": "application/json"
        }
    
    def setup_test_data(self):
        """Create test medicines with stock."""
        self.print_header("2. SETUP TEST DATA")
        
        # Create family
        response = requests.post(
            f"{BASE_URL}/config/families",
            headers=self.get_headers(),
            json={"name": "Test POS Family"}
        )
        family_id = response.json()["id"] if response.status_code == 201 else 1
        
        # Create medicines with stock
        medicines = [
            {
                "code": "POS-001",
                "name": "Test Medicine A",
                "family_id": family_id,
                "quantity": 100,
                "price_buy": 500.0,
                "price_sell": 1000.0,
                "min_stock_alert": 10
            },
            {
                "code": "POS-002",
                "name": "Test Medicine B",
                "family_id": family_id,
                "quantity": 50,
                "price_buy": 1000.0,
                "price_sell": 1500.0,
                "min_stock_alert": 10
            },
            {
                "code": "POS-003",
                "name": "Test Medicine C (Low Stock)",
                "family_id": family_id,
                "quantity": 5,
                "price_buy": 200.0,
                "price_sell": 300.0,
                "min_stock_alert": 10
            }
        ]
        
        for medicine in medicines:
            response = requests.post(
                f"{BASE_URL}/stock/medicines",
                headers=self.get_headers(),
                json=medicine
            )
            
            if response.status_code == 201:
                med_id = response.json()["id"]
                self.medicine_ids.append(med_id)
                self.print_test(f"Create medicine '{medicine['name']}'", True, f"ID: {med_id}, Stock: {medicine['quantity']}")
            elif response.status_code == 400:
                # Medicine already exists, try to get it
                response = requests.get(
                    f"{BASE_URL}/stock/medicines?search={medicine['code']}",
                    headers=self.get_headers()
                )
                if response.status_code == 200 and response.json()["total"] > 0:
                    med_id = response.json()["items"][0]["id"]
                    self.medicine_ids.append(med_id)
                    self.print_test(f"Use existing medicine '{medicine['name']}'", True, f"ID: {med_id}")
        
        print(f"\n{YELLOW}Test data ready: {len(self.medicine_ids)} medicines{RESET}")
    
    def test_sale_without_customer(self):
        """Test creating a sale without customer."""
        self.print_header("3. SALE WITHOUT CUSTOMER")
        
        if len(self.medicine_ids) < 2:
            self.print_test("Sale without customer", False, "Not enough test medicines")
            return
        
        sale_data = {
            "items": [
                {"medicine_id": self.medicine_ids[0], "quantity": 5},
                {"medicine_id": self.medicine_ids[1], "quantity": 3}
            ],
            "payment_method": "cash"
        }
        
        response = requests.post(
            f"{BASE_URL}/sales/create",
            headers=self.get_headers(),
            json=sale_data
        )
        
        passed = response.status_code == 201
        if passed:
            data = response.json()
            self.sale_ids.append(data["id"])
            details = f"Invoice: {data['code']}, Total: {data['total_amount']} FBu, Customer: None"
            self.print_test("Create sale without customer", True, details)
            
            # Verify no bonus
            if data["bonus_earned"] == 0:
                self.print_test("No bonus without customer", True, "Bonus: 0")
        else:
            self.print_test("Create sale without customer", False, f"Status: {response.status_code}, Error: {response.text}")
    
    def test_sale_with_new_customer(self):
        """Test creating a sale with new customer (auto-registration)."""
        self.print_header("4. SALE WITH NEW CUSTOMER (AUTO-REGISTRATION)")
        
        if len(self.medicine_ids) < 1:
            self.print_test("Sale with new customer", False, "Not enough test medicines")
            return
        
        sale_data = {
            "items": [
                {"medicine_id": self.medicine_ids[0], "quantity": 10}
            ],
            "payment_method": "cash",
            "customer_phone": self.customer_phone,
            "customer_first_name": "Test",
            "customer_last_name": "Customer"
        }
        
        response = requests.post(
            f"{BASE_URL}/sales/create",
            headers=self.get_headers(),
            json=sale_data
        )
        
        passed = response.status_code == 201
        if passed:
            data = response.json()
            self.sale_ids.append(data["id"])
            bonus = data["bonus_earned"]
            expected_bonus = int(data["total_amount"] * 0.05)
            
            details = f"Invoice: {data['code']}, Total: {data['total_amount']} FBu, Bonus: {bonus}"
            self.print_test("Create sale with new customer", True, details)
            
            # Verify customer created
            if data["customer"]:
                self.print_test("Customer auto-registered", True, f"Name: {data['customer']['first_name']} {data['customer']['last_name']}")
            
            # Verify bonus calculated (5%)
            if bonus == expected_bonus:
                self.print_test("Bonus calculated correctly (5%)", True, f"{bonus} points")
            else:
                self.print_test("Bonus calculated correctly (5%)", False, f"Expected {expected_bonus}, got {bonus}")
        else:
            self.print_test("Create sale with new customer", False, f"Status: {response.status_code}, Error: {response.text}")
    
    def test_sale_with_existing_customer(self):
        """Test creating a sale with existing customer (bonus accumulation)."""
        self.print_header("5. SALE WITH EXISTING CUSTOMER (BONUS ACCUMULATION)")
        
        if len(self.medicine_ids) < 1:
            self.print_test("Sale with existing customer", False, "Not enough test medicines")
            return
        
        sale_data = {
            "items": [
                {"medicine_id": self.medicine_ids[1], "quantity": 5}
            ],
            "payment_method": "mobile_money",
            "customer_phone": self.customer_phone
        }
        
        response = requests.post(
            f"{BASE_URL}/sales/create",
            headers=self.get_headers(),
            json=sale_data
        )
        
        passed = response.status_code == 201
        if passed:
            data = response.json()
            self.sale_ids.append(data["id"])
            bonus = data["bonus_earned"]
            total_points = data["customer"]["total_points"] if data["customer"] else 0
            
            details = f"Invoice: {data['code']}, Bonus: +{bonus}, Total Points: {total_points}"
            self.print_test("Create sale with existing customer", True, details)
            
            # Verify customer identified
            if data["customer"] and data["customer"]["phone"] == self.customer_phone:
                self.print_test("Existing customer identified", True, f"Phone: {data['customer']['phone']}")
            
            # Verify bonus accumulated
            if total_points > bonus:
                self.print_test("Bonus points accumulated", True, f"Total: {total_points} points")
        else:
            self.print_test("Create sale with existing customer", False, f"Status: {response.status_code}, Error: {response.text}")
    
    def test_stock_decrement(self):
        """Test that stock is decremented after sale."""
        self.print_header("6. STOCK DECREMENT VERIFICATION")
        
        if len(self.medicine_ids) < 1:
            self.print_test("Stock decrement", False, "No test medicines")
            return
        
        # Get current stock
        response = requests.get(
            f"{BASE_URL}/stock/medicines/{self.medicine_ids[0]}",
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            stock = response.json()["quantity"]
            initial_stock = 100  # From setup
            expected_decrease = 5 + 10  # From sale 1 and sale 2
            
            if stock < initial_stock:
                self.print_test("Stock decremented", True, f"Current: {stock} (decreased from {initial_stock})")
            else:
                self.print_test("Stock decremented", False, f"Stock unchanged: {stock}")
        else:
            self.print_test("Stock decrement", False, "Failed to get medicine")
    
    def test_insufficient_stock(self):
        """Test error when trying to sell more than available stock."""
        self.print_header("7. INSUFFICIENT STOCK ERROR")
        
        if len(self.medicine_ids) < 3:
            self.print_test("Insufficient stock error", False, "Not enough test medicines")
            return
        
        # Try to sell more than available (Medicine C has only 5 units)
        sale_data = {
            "items": [
                {"medicine_id": self.medicine_ids[2], "quantity": 10}
            ],
            "payment_method": "cash"
        }
        
        response = requests.post(
            f"{BASE_URL}/sales/create",
            headers=self.get_headers(),
            json=sale_data
        )
        
        # Should get 400 error
        passed = response.status_code == 400
        if passed:
            error = response.json().get("detail", "")
            self.print_test("Insufficient stock rejected", True, f"Error: {error[:60]}...")
        else:
            self.print_test("Insufficient stock rejected", False, f"Expected 400, got {response.status_code}")
    
    def test_invoice_code_generation(self):
        """Test invoice code generation sequence."""
        self.print_header("8. INVOICE CODE GENERATION")
        
        if len(self.sale_ids) < 2:
            self.print_test("Invoice code generation", False, "Not enough sales created")
            return
        
        # Get sales and check invoice codes
        codes = []
        for sale_id in self.sale_ids[:2]:
            response = requests.get(
                f"{BASE_URL}/sales/{sale_id}",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                code = response.json()["code"]
                codes.append(code)
        
        if len(codes) >= 2:
            # Check format INV-YYYY-NNNN
            valid_format = all(code.startswith("INV-2") and len(code.split('-')) == 3 for code in codes)
            
            if valid_format:
                self.print_test("Invoice code format", True, f"Format: {codes[0]}")
            
            # Check sequential
            numbers = [int(code.split('-')[-1]) for code in codes]
            sequential = numbers[1] == numbers[0] + 1
            
            if sequential:
                self.print_test("Invoice codes sequential", True, f"{codes[0]} -> {codes[1]}")
            else:
                self.print_test("Invoice codes sequential", False, f"{codes}")
    
    def test_pdf_invoice(self):
        """Test PDF invoice generation."""
        self.print_header("9. PDF INVOICE GENERATION")
        
        if len(self.sale_ids) < 1:
            self.print_test("PDF invoice", False, "No sales to generate invoice")
            return
        
        sale_id = self.sale_ids[0]
        response = requests.get(
            f"{BASE_URL}/sales/invoice/{sale_id}",
            headers=self.get_headers()
        )
        
        passed = response.status_code == 200 and response.headers.get("content-type") == "application/pdf"
        
        if passed:
            pdf_size = len(response.content)
            self.print_test("PDF invoice generated", True, f"Size: {pdf_size} bytes")
            
            # Save PDF for manual verification
            filename = f"test_invoice_{sale_id}.pdf"
            with open(filename, "wb") as f:
                f.write(response.content)
            self.print_test("PDF saved for verification", True, f"File: {filename}")
        else:
            self.print_test("PDF invoice generated", False, f"Status: {response.status_code}")
    
    def print_summary(self):
        """Print test summary."""
        self.print_header("TEST SUMMARY")
        
        total = len(self.test_results)
        passed = sum(1 for _, p in self.test_results if p)
        failed = total - passed
        
        print(f"Total tests: {total}")
        print(f"{GREEN}Passed: {passed}{RESET}")
        print(f"{RED}Failed: {failed}{RESET}")
        print(f"Success rate: {(passed/total*100):.1f}%")
        
        if failed > 0:
            print(f"\n{RED}Failed tests:{RESET}")
            for name, p in self.test_results:
                if not p:
                    print(f"  - {name}")
        
        print(f"\n{BLUE}{'=' * 60}{RESET}")
        if failed == 0:
            print(f"{GREEN}[SUCCESS] ALL TESTS PASSED! Module 4 is functional!{RESET}")
        else:
            print(f"{YELLOW}[WARNING] Some tests failed. Please review.{RESET}")
        print(f"{BLUE}{'=' * 60}{RESET}\n")


def main():
    print(f"{BLUE}")
    print("=" * 60)
    print("  MODULE 4 - AUTOMATED TESTS")
    print("  Point de Vente (POS)")
    print("=" * 60)
    print(f"{RESET}")
    
    tester = TestModule4()
    
    # Run tests
    if not tester.login_admin():
        print(f"{RED}Failed to login. Is the server running?{RESET}")
        return
    
    tester.setup_test_data()
    tester.test_sale_without_customer()
    tester.test_sale_with_new_customer()
    tester.test_sale_with_existing_customer()
    tester.test_stock_decrement()
    tester.test_insufficient_stock()
    tester.test_invoice_code_generation()
    tester.test_pdf_invoice()
    
    # Summary
    tester.print_summary()


if __name__ == "__main__":
    main()
