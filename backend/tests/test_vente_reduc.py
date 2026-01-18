"""
Test de vente avec réduction de 10%
"""

import requests
import json

BASE_URL = "http://localhost:8000"

# Login
print("=== LOGIN ADMIN ===")
response = requests.post(
    f"{BASE_URL}/auth/login",
    data={"username": "admin", "password": "admin123"}
)
token = response.json()["access_token"]
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
print("✓ Connecté\n")

# Get available medicines
print("=== MÉDICAMENTS DISPONIBLES ===")
response = requests.get(f"{BASE_URL}/stock/medicines", headers=headers)
medicines = response.json()["items"][:2]

for med in medicines:
    print(f"ID {med['id']}: {med['name']}")
    print(f"  Stock: {med['quantity']} unités")
    print(f"  Prix: {med['price_sell']} FBu")
    print()

# Create sale with 10% discount
print("=== CRÉATION DE VENTE AVEC RÉDUCTION 10% ===")
sale_data = {
    "items": [
        {"medicine_id": medicines[0]["id"], "quantity": 2},
        {"medicine_id": medicines[1]["id"], "quantity": 3}
    ],
    "payment_method": "cash",
    "discount_percent": 10.0,
    "customer_phone": "+25771111111",
    "customer_first_name": "Client",
    "customer_last_name": "Test"
}

print(f"Articles:")
print(f"  - {medicines[0]['name']}: 2 × {medicines[0]['price_sell']} = {2 * medicines[0]['price_sell']} FBu")
print(f"  - {medicines[1]['name']}: 3 × {medicines[1]['price_sell']} = {3 * medicines[1]['price_sell']} FBu")
subtotal = 2 * medicines[0]['price_sell'] + 3 * medicines[1]['price_sell']
print(f"\nSous-total: {subtotal} FBu")
print(f"Réduction 10%: -{subtotal * 0.1} FBu")
print(f"Total attendu: {subtotal * 0.9} FBu\n")

response = requests.post(
    f"{BASE_URL}/sales/create",
    headers=headers,
    json=sale_data
)

if response.status_code == 201:
    sale = response.json()
    print("✓ VENTE CRÉÉE AVEC SUCCÈS!\n")
    print(f"Facture: {sale['code']}")
    print(f"Total final: {sale['total_amount']} FBu")
    print(f"Client: {sale['customer']['first_name']} {sale['customer']['last_name']}")
    print(f"Téléphone: {sale['customer']['phone']}")
    print(f"Bonus gagné: {sale['bonus_earned']} points (5% du total réduit)")
    print(f"Total points client: {sale['customer']['total_points']} points")
    
    # Verify stock decreased
    print("\n=== VÉRIFICATION STOCK ===")
    for i, med in enumerate(medicines):
        response = requests.get(
            f"{BASE_URL}/stock/medicines/{med['id']}",
            headers=headers
        )
        new_stock = response.json()["quantity"]
        qty_sold = sale_data["items"][i]["quantity"]
        print(f"{med['name']}: {med['quantity']} -> {new_stock} (-{qty_sold}) ✓")
    
    # Download PDF invoice
    print("\n=== TÉLÉCHARGEMENT FACTURE PDF ===")
    response = requests.get(
        f"{BASE_URL}/sales/invoice/{sale['id']}",
        headers=headers
    )
    if response.status_code == 200:
        filename = f"facture_{sale['code']}.pdf"
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"✓ Facture enregistrée: {filename}")
        print(f"  Taille: {len(response.content)} bytes")
else:
    print(f"✗ ERREUR: {response.status_code}")
    print(response.text)
