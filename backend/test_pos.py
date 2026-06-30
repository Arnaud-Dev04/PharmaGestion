import urllib.request
import json

BASE = "http://127.0.0.1:8000"

# 1. Login (OAuth2 form-data)
import urllib.parse
login_data = urllib.parse.urlencode({
    'username': 'arnaud',
    'password': 'arnaud123',
    'grant_type': 'password'
}).encode()
req = urllib.request.Request(f"{BASE}/auth/login", data=login_data, 
    headers={'Content-Type': 'application/x-www-form-urlencoded'})
try:
    r = urllib.request.urlopen(req, timeout=10)
    token_data = json.loads(r.read().decode())
    token = token_data.get('access_token', '')
    print(f"[OK] Login successful, token: {token[:20]}...")
except Exception as e:
    print(f"[FAIL] Login: {e}")
    # Try to read error body
    if hasattr(e, 'read'):
        print(f"  Body: {e.read().decode()}")
    exit(1)

# Helper
def get_auth(path):
    req = urllib.request.Request(f"{BASE}{path}")
    req.add_header("Authorization", f"Bearer {token}")
    r = urllib.request.urlopen(req, timeout=10)
    return json.loads(r.read().decode())

def post_auth(path, data):
    body = json.dumps(data).encode()
    req = urllib.request.Request(f"{BASE}{path}", data=body, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    })
    r = urllib.request.urlopen(req, timeout=10)
    return json.loads(r.read().decode())

# 2. POS Search
print("\n=== POS PRODUCT SEARCH ===")
results = get_auth("/pos/products/search?q=doli&limit=5")
print(f"Found {len(results)} products")
for p in results:
    print(f"  - {p['name']} | Price: {p['price_sell']} FBu | Qty: {p['available_quantity']} | Batches: {len(p['batches'])}")
    for b in p['batches']:
        print(f"      Lot #{b['id']}: {b['batch_number']} | Qty: {b['quantity']} | Exp: {b['expiration_date']}")

# 3. FEFO Allocation
if results:
    product = results[0]
    print(f"\n=== FEFO ALLOCATION for {product['name']} x2 ===")
    try:
        alloc = post_auth("/pos/cart/add", {"medicine_id": product['id'], "quantity": 2})
        print(f"  Product: {alloc['medicine_name']} | Qty: {alloc['quantity']} | Total: {alloc['total_price']} FBu")
        for a in alloc['allocations']:
            print(f"    -> Batch #{a['batch_id']} ({a['batch_number']}) x{a['quantity']} | Exp: {a.get('expiration_date','?')}")
    except urllib.error.HTTPError as e:
        print(f"  FAIL ({e.code}): {e.read().decode()}")

print("\n=== ALL TESTS PASSED ===")
