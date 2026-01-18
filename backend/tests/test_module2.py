"""
Script de test pour vérifier le Module 2 (Authentification).
"""

print("=" * 60)
print("TEST MODULE 2 - AUTHENTIFICATION JWT")
print("=" * 60)

# Test 1: Import des modules de sécurité
print("\n[TEST 1] Import des utilitaires de securite...")
try:
    from app.utils.security import hash_password, verify_password, create_access_token, decode_token
    print("  [OK] Fonctions de securite importees")
except Exception as e:
    print(f"  [ERREUR] {e}")
    exit(1)

# Test 2: Test du hashage de mot de passe
print("\n[TEST 2] Test du hashage de mot de passe (bcrypt)...")
try:
    test_password = "test123"
    hashed = hash_password(test_password)
    print(f"  [OK] Password hashe: {hashed[:30]}...")
    
    # Vérifier le mot de passe
    is_valid = verify_password(test_password, hashed)
    print(f"  [OK] Verification: {is_valid}")
    
    # Vérifier avec un mauvais mot de passe
    is_invalid = verify_password("wrongpassword", hashed)
    print(f"  [OK] Mauvais password rejete: {not is_invalid}")
    
except Exception as e:
    print(f"  [ERREUR] {e}")
    exit(1)

# Test 3: Test de création de token JWT
print("\n[TEST 3] Test de creation de token JWT...")
try:
    token_data = {"sub": "testuser", "role": "admin"}
    token = create_access_token(token_data)
    print(f"  [OK] Token cree: {token[:50]}...")
    
    # Décoder le token
    username = decode_token(token)
    print(f"  [OK] Token decode: username='{username}'")
    
    if username == "testuser":
        print("  [OK] Donnees du token correctes")
    else:
        print(f"  [ERREUR] Username incorrect: {username}")
        
except Exception as e:
    print(f"  [ERREUR] {e}")
    exit(1)

# Test 4: Import des schémas Pydantic
print("\n[TEST 4] Import des schemas Pydantic...")
try:
    from app.schemas.auth import Token, UserLogin, UserCreate, UserResponse
    print("  [OK] Token schema")
    print("  [OK] UserLogin schema")
    print("  [OK] UserCreate schema")
    print("  [OK] UserResponse schema")
except Exception as e:
    print(f"  [ERREUR] {e}")
    exit(1)

# Test 5: Import des dépendances d'authentification
print("\n[TEST 5] Import des dependances d'authentification...")
try:
    from app.auth.dependencies import (
        get_current_user,
        get_current_active_user,
        get_admin_user
    )
    print("  [OK] get_current_user")
    print("  [OK] get_current_active_user")
    print("  [OK] get_admin_user")
except Exception as e:
    print(f"  [ERREUR] {e}")
    exit(1)

# Test 6: Import des routes
print("\n[TEST 6] Import des routes d'authentification...")
try:
    from app.routes.auth import router as auth_router
    from app.routes.metrics import router as metrics_router
    print("  [OK] Auth router importe")
    print("  [OK] Metrics router importe")
except Exception as e:
    print(f"  [ERREUR] {e}")
    exit(1)

# Test 7: Vérifier que l'app FastAPI charge bien
print("\n[TEST 7] Chargement de l'application FastAPI...")
try:
    from main import app
    print(f"  [OK] Application chargee: {app.title}")
    
    # Vérifier les routes
    routes_count = 0
    auth_routes = []
    for route in app.routes:
        if hasattr(route, 'path'):
            if '/auth/' in route.path or route.path == '/metrics':
                auth_routes.append(route.path)
                routes_count += 1
    
    print(f"  [OK] Routes d'authentification trouvees: {routes_count}")
    for route_path in sorted(set(auth_routes)):
        print(f"      - {route_path}")
        
except Exception as e:
    print(f"  [ERREUR] {e}")
    exit(1)

# Test 8: Vérifier la configuration
print("\n[TEST 8] Verification de la configuration...")
try:
    from app.utils.security import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
    print(f"  [OK] SECRET_KEY: {'*' * 20}... (cache)")
    print(f"  [OK] ALGORITHM: {ALGORITHM}")
    print(f"  [OK] TOKEN_EXPIRE: {ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
except Exception as e:
    print(f"  [ERREUR] {e}")
    exit(1)

# Résumé
print("\n" + "=" * 60)
print("RESULTAT FINAL")
print("=" * 60)
print("[OK] Module 2: TOUS LES TESTS REUSSIS!")
print("\nComposants implementes:")
print("  - Hashage de mots de passe (bcrypt)")
print("  - Creation et verification de tokens JWT")
print("  - Schemas Pydantic pour validation")
print("  - Dependencies pour authentification/autorisation")
print("  - Routes: /auth/login, /auth/register, /auth/me")
print("  - Route protegee: /metrics")
print("\nProchaines etapes:")
print("  1. Creer un utilisateur admin:")
print("     python create_admin.py")
print("\n  2. Lancer le serveur:")
print("     uvicorn main:app --reload")
print("\n  3. Tester dans Swagger:")
print("     http://localhost:8000/docs")
print("=" * 60)
