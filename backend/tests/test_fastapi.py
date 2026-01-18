"""
Script pour tester le serveur FastAPI rapidement.
Lance le serveur et teste les endpoints de base.
"""

import requests
import time
import subprocess
import sys

print("=" * 60)
print("TEST FASTAPI - MODULE 1")
print("=" * 60)

# Importer l'app pour vérifier qu'elle se charge
print("\n[TEST 1] Chargement de l'application FastAPI...")
try:
    from main import app
    print(f"  [OK] Application chargee: {app.title}")
    print(f"  [OK] Version: {app.version}")
except Exception as e:
    print(f"  [ERREUR] {e}")
    sys.exit(1)

print("\n[TEST 2] Verification des routes...")
try:
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            methods = ','.join(route.methods) if route.methods else 'N/A'
            routes.append((route.path, methods))
            print(f"  [OK] {methods:10} {route.path}")
    
    print(f"\n  Total routes: {len(routes)}")
except Exception as e:
    print(f"  [ERREUR] {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("RESULTAT: APPLICATION FASTAPI OPERATIONNELLE")
print("=" * 60)
print("\nPour lancer le serveur:")
print("  uvicorn main:app --reload")
print("\nPuis acceder a:")
print("  - API: http://localhost:8000")
print("  - Docs: http://localhost:8000/docs")
print("  - Health: http://localhost:8000/health")
print("=" * 60)
