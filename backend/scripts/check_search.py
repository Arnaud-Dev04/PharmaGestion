import requests

# Login
response = requests.post(
    "http://localhost:8000/auth/login",
    data={"username": "admin", "password": "admin123"}
)
token = response.json()["access_token"]

# Get medicines
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("http://localhost:8000/stock/medicines", headers=headers)

data = response.json()
print(f"Total medicines in database: {data['total']}")
print("\nAll medicines:")
for m in data['items']:
    print(f"  - {m['code']}: {m['name']}")

# Test search
print("\n" + "="*60)
print("Testing search for 'paracetamol'...")
response = requests.get(
    "http://localhost:8000/stock/medicines?search=paracetamol",
    headers=headers
)
data = response.json()
print(f"Results found: {data['total']}")
for m in data['items']:
    print(f"  - {m['name']}")
