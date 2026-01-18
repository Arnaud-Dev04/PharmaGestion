"""
Automated test script for Module 3: Stock & Suppliers Management.
Run this script to validate all Module 3 functionalities.
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


class TestModule3:
    def __init__(self):
        self.admin_token = None
        self.pharmacist_token = None
        self.test_results = []
        self.family_ids = []
        self.type_ids = []
        self.medicine_ids = []
        self.supplier_ids = []
    
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
    
    def get_headers(self, token=None):
        """Get authorization headers."""
        if token is None:
            token = self.admin_token
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def test_create_families(self):
        """Test creating medicine families."""
        self.print_header("2. CREATE FAMILIES")
        
        families = ["Antibiotiques", "Antipaludiques", "Antidouleurs"]
        
        for family_name in families:
            response = requests.post(
                f"{BASE_URL}/config/families",
                headers=self.get_headers(),
                json={"name": family_name}
            )
            
            passed = response.status_code == 201
            if passed:
                family_id = response.json()["id"]
                self.family_ids.append(family_id)
                self.print_test(f"Create family '{family_name}'", True, f"ID: {family_id}")
            else:
                self.print_test(f"Create family '{family_name}'", False, f"Status: {response.status_code}")
    
    def test_list_families(self):
        """Test listing families."""
        self.print_header("3. LIST FAMILIES")
        
        response = requests.get(
            f"{BASE_URL}/config/families",
            headers=self.get_headers()
        )
        
        passed = response.status_code == 200 and len(response.json()) >= 3
        details = f"Found {len(response.json())} families" if passed else f"Status: {response.status_code}"
        self.print_test("List families", passed, details)
    
    def test_create_types(self):
        """Test creating medicine types."""
        self.print_header("4. CREATE TYPES")
        
        types = ["Plaquette", "Flacon", "Ampoule", "Sachet"]
        
        for type_name in types:
            response = requests.post(
                f"{BASE_URL}/config/types",
                headers=self.get_headers(),
                json={"name": type_name}
            )
            
            passed = response.status_code == 201
            if passed:
                type_id = response.json()["id"]
                self.type_ids.append(type_id)
                self.print_test(f"Create type '{type_name}'", True, f"ID: {type_id}")
            else:
                self.print_test(f"Create type '{type_name}'", False, f"Status: {response.status_code}")
    
    def test_create_suppliers(self):
        """Test creating suppliers."""
        self.print_header("5. CREATE SUPPLIERS")
        
        suppliers = [
            {
                "name": "Pharma Distributeur SA",
                "phone": "+25771234567",
                "email": "contact@pharmadist.bi",
                "contact_name": "Jean Dupont"
            },
            {
                "name": "Medic Import SARL",
                "phone": "+25772345678",
                "email": "info@medicimport.bi",
                "contact_name": "Marie Niyonzima"
            }
        ]
        
        for supplier in suppliers:
            response = requests.post(
                f"{BASE_URL}/suppliers",
                headers=self.get_headers(),
                json=supplier
            )
            
            passed = response.status_code == 201
            if passed:
                supplier_id = response.json()["id"]
                self.supplier_ids.append(supplier_id)
                self.print_test(f"Create supplier '{supplier['name']}'", True, f"ID: {supplier_id}")
            else:
                self.print_test(f"Create supplier '{supplier['name']}'", False, f"Status: {response.status_code}")
    
    def test_create_medicines(self):
        """Test creating medicines."""
        self.print_header("6. CREATE MEDICINES")
        
        today = date.today()
        future_date = (today + timedelta(days=365)).isoformat()
        past_date = (today - timedelta(days=30)).isoformat()
        
        medicines = [
            {
                "code": "MED-001",
                "name": "Paracétamol 500mg",
                "family_id": self.family_ids[2] if len(self.family_ids) > 2 else None,
                "type_id": self.type_ids[0] if len(self.type_ids) > 0 else None,
                "quantity": 100,
                "price_buy": 500.0,
                "price_sell": 800.0,
                "expiry_date": future_date,
                "min_stock_alert": 20
            },
            {
                "code": "MED-002",
                "name": "Amoxicilline 250mg",
                "family_id": self.family_ids[0] if len(self.family_ids) > 0 else None,
                "type_id": self.type_ids[0] if len(self.type_ids) > 0 else None,
                "quantity": 8,
                "price_buy": 1000.0,
                "price_sell": 1500.0,
                "expiry_date": future_date,
                "min_stock_alert": 20
            },
            {
                "code": "MED-003",
                "name": "Vitamine C 1000mg",
                "family_id": self.family_ids[2] if len(self.family_ids) > 2 else None,
                "type_id": self.type_ids[3] if len(self.type_ids) > 3 else None,
                "quantity": 50,
                "price_buy": 300.0,
                "price_sell": 500.0,
                "expiry_date": past_date,
                "min_stock_alert": 10
            },
            {
                "code": "MED-004",
                "name": "Aspirine 100mg",
                "family_id": self.family_ids[2] if len(self.family_ids) > 2 else None,
                "type_id": self.type_ids[0] if len(self.type_ids) > 0 else None,
                "quantity": 5,
                "price_buy": 200.0,
                "price_sell": 350.0,
                "expiry_date": past_date,
                "min_stock_alert": 15
            }
        ]
        
        for medicine in medicines:
            response = requests.post(
                f"{BASE_URL}/stock/medicines",
                headers=self.get_headers(),
                json=medicine
            )
            
            passed = response.status_code == 201
            if passed:
                med_id = response.json()["id"]
                self.medicine_ids.append(med_id)
                details = f"ID: {med_id}, Low stock: {response.json()['is_low_stock']}, Expired: {response.json()['is_expired']}"
                self.print_test(f"Create medicine '{medicine['name']}'", True, details)
            else:
                self.print_test(f"Create medicine '{medicine['name']}'", False, f"Status: {response.status_code}")
    
    def test_list_medicines(self):
        """Test listing medicines with pagination."""
        self.print_header("7. LIST MEDICINES")
        
        response = requests.get(
            f"{BASE_URL}/stock/medicines?page=1&page_size=10",
            headers=self.get_headers()
        )
        
        passed = response.status_code == 200
        if passed:
            data = response.json()
            details = f"Total: {data['total']}, Page: {data['page']}, Items: {len(data['items'])}"
            self.print_test("List medicines with pagination", True, details)
        else:
            self.print_test("List medicines with pagination", False, f"Status: {response.status_code}")
    
    def test_search_medicines(self):
        """Test searching medicines."""
        self.print_header("8. SEARCH & FILTERS")
        
        # Search by name
        response = requests.get(
            f"{BASE_URL}/stock/medicines?search=paracetamol",
            headers=self.get_headers()
        )
        passed = response.status_code == 200 and response.json()["total"] >= 1
        self.print_test("Search by name", passed, f"Found {response.json()['total']} results" if passed else "")
        
        # Filter by family
        if len(self.family_ids) > 0:
            response = requests.get(
                f"{BASE_URL}/stock/medicines?family_id={self.family_ids[0]}",
                headers=self.get_headers()
            )
            passed = response.status_code == 200
            self.print_test("Filter by family", passed, f"Found {response.json()['total']} results" if passed else "")
        
        # Filter low stock
        response = requests.get(
            f"{BASE_URL}/stock/medicines?is_low_stock=true",
            headers=self.get_headers()
        )
        passed = response.status_code == 200 and response.json()["total"] >= 2
        self.print_test("Filter low stock", passed, f"Found {response.json()['total']} low stock" if passed else "")
        
        # Filter expired
        response = requests.get(
            f"{BASE_URL}/stock/medicines?is_expired=true",
            headers=self.get_headers()
        )
        passed = response.status_code == 200 and response.json()["total"] >= 2
        self.print_test("Filter expired", passed, f"Found {response.json()['total']} expired" if passed else "")
    
    def test_stock_alerts(self):
        """Test stock alerts endpoint."""
        self.print_header("9. STOCK ALERTS")
        
        response = requests.get(
            f"{BASE_URL}/stock/alerts",
            headers=self.get_headers()
        )
        
        passed = response.status_code == 200
        if passed:
            data = response.json()
            details = f"Low stock: {len(data['low_stock'])}, Expired: {len(data['expired'])}, Total: {data['total_alerts']}"
            self.print_test("Get stock alerts", True, details)
        else:
            self.print_test("Get stock alerts", False, f"Status: {response.status_code}")
    
    def test_update_medicine(self):
        """Test updating a medicine."""
        self.print_header("10. UPDATE MEDICINE")
        
        if len(self.medicine_ids) > 0:
            response = requests.put(
                f"{BASE_URL}/stock/medicines/{self.medicine_ids[0]}",
                headers=self.get_headers(),
                json={"quantity": 150, "price_sell": 850.0}
            )
            
            passed = response.status_code == 200
            if passed:
                details = f"Quantity: {response.json()['quantity']}, Price: {response.json()['price_sell']}"
                self.print_test("Update medicine", True, details)
            else:
                self.print_test("Update medicine", False, f"Status: {response.status_code}")
    
    def test_duplicate_code(self):
        """Test duplicate code validation."""
        self.print_header("11. VALIDATION - DUPLICATE CODE")
        
        response = requests.post(
            f"{BASE_URL}/stock/medicines",
            headers=self.get_headers(),
            json={
                "code": "MED-001",
                "name": "Test Duplicate",
                "quantity": 10,
                "price_buy": 100,
                "price_sell": 150,
                "min_stock_alert": 5
            }
        )
        
        passed = response.status_code == 400
        self.print_test("Reject duplicate code", passed, "Correctly rejected" if passed else "Should be 400")
    
    def test_nonexistent_medicine(self):
        """Test accessing non-existent medicine."""
        self.print_header("12. VALIDATION - NON-EXISTENT")
        
        response = requests.get(
            f"{BASE_URL}/stock/medicines/9999",
            headers=self.get_headers()
        )
        
        passed = response.status_code == 404
        self.print_test("Get non-existent medicine", passed, "Correctly returns 404" if passed else "Should be 404")
    
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
            print(f"{GREEN}[SUCCESS] ALL TESTS PASSED! Module 3 is functional!{RESET}")
        else:
            print(f"{YELLOW}[WARNING] Some tests failed. Please review.{RESET}")
        print(f"{BLUE}{'=' * 60}{RESET}\n")


def main():
    print(f"{BLUE}")
    print("=" * 60)
    print("  MODULE 3 - AUTOMATED TESTS")
    print("  Stock & Suppliers Management")
    print("=" * 60)
    print(f"{RESET}")
    
    tester = TestModule3()
    
    # Run tests
    if not tester.login_admin():
        print(f"{RED}Failed to login. Is the server running?{RESET}")
        return
    
    tester.test_create_families()
    tester.test_list_families()
    tester.test_create_types()
    tester.test_create_suppliers()
    tester.test_create_medicines()
    tester.test_list_medicines()
    tester.test_search_medicines()
    tester.test_stock_alerts()
    tester.test_update_medicine()
    tester.test_duplicate_code()
    tester.test_nonexistent_medicine()
    
    # Summary
    tester.print_summary()


if __name__ == "__main__":
    main()
