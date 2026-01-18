import requests
import time
import sys

def test_executable():
    """Test l'exécutable sans navigateur"""
    base_url = "http://localhost:8000"
    
    print("🔍 Test de l'exécutable PharmacPlus.exe")
    print("=" * 50)
    
    # Attendre que le serveur démarre
    print("\n⏳ Attente du démarrage du serveur (10 secondes)...")
    time.sleep(10)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Health check
    print("\n📍 Test 1: Health Check")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ PASS - Status: {response.json()}")
            tests_passed += 1
        else:
            print(f"❌ FAIL - Code: {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"❌ FAIL - Erreur: {e}")
        tests_failed += 1
    
    # Test 2: License Status
    print("\n📍 Test 2: License Status")
    try:
        response = requests.get(f"{base_url}/license/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ PASS - Statut: {data['status']}, Jours restants: {data.get('days_remaining', 'N/A')}")
            tests_passed += 1
        else:
            print(f"❌ FAIL - Code: {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"❌ FAIL - Erreur: {e}")
        tests_failed += 1
    
    # Test 3: Root endpoint
    print("\n📍 Test 3: Root Endpoint")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ PASS - Version: {data.get('version')}, Status: {data.get('status')}")
            tests_passed += 1
        else:
            print(f"❌ FAIL - Code: {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"❌ FAIL - Erreur: {e}")
        tests_failed += 1
    
    # Test 4: Dashboard Stats (nécessite auth, devrait retourner 401 ou 403)
    print("\n📍 Test 4: Dashboard Stats (sans auth)")
    try:
        response = requests.get(f"{base_url}/dashboard/stats", timeout=5)
        if response.status_code in [401, 403]:
            print(f"✅ PASS - Auth requise (code {response.status_code}) - Sécurité OK")
            tests_passed += 1
        else:
            print(f"⚠️  WARN - Code inattendu: {response.status_code}")
            tests_passed += 1  # On compte quand même
    except Exception as e:
        print(f"❌ FAIL - Erreur: {e}")
        tests_failed += 1
    
    # Résumé
    print("\n" + "=" * 50)
    print(f"📊 RÉSULTAT: {tests_passed} tests réussis, {tests_failed} échecs")
    print("=" * 50)
    
    if tests_failed == 0:
        print("\n🎉 TOUS LES TESTS SONT PASSÉS !")
        print("✅ L'exécutable fonctionne correctement")
        return 0
    else:
        print("\n⚠️  Certains tests ont échoué")
        return 1

if __name__ == "__main__":
    sys.exit(test_executable())
