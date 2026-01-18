# 🧪 Guide de Tests - Module 2 Authentification

## 📋 Plan de Tests

Ce guide vous permet de tester **TOUTES** les fonctionnalités du Module 2 avec les 2 types d'utilisateurs.

**Utilisateurs de test**:
- ✅ **Admin**: `admin` / `admin123`
- ✅ **Pharmacien**: `pharmacist1` / `pharma123`

---

## 🎯 Tests à Effectuer

### ✅ Test 1: Login Admin
### ✅ Test 2: Login Pharmacien
### ✅ Test 3: Permissions Admin
### ✅ Test 4: Permissions Pharmacien
### ✅ Test 5: Routes Protégées
### ✅ Test 6: Expiration de Token
### ✅ Test 7: Sécurité

---

## Test 1: Login Admin ✅

### Objectif
Vérifier que l'admin peut se connecter et recevoir un token valide.

### Étapes

1. **Ouvrir Swagger**: http://localhost:8000/docs

2. **Login**:
   - Route: `POST /auth/login`
   - Cliquez "Try it out"
   - Entrez:
     ```
     username: admin
     password: admin123
     ```
   - Cliquez "Execute"

3. **Résultat attendu** ✅:
   ```json
   {
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "token_type": "bearer"
   }
   ```
   - Code: **200 OK**
   - Token reçu (long texte)

4. **Vérifications**:
   - [ ] Code 200 OK
   - [ ] Token présent (commence par `eyJ`)
   - [ ] token_type = "bearer"

### ❌ Résultat si échec
- **401 Unauthorized**: Mot de passe incorrect
- **400 Bad Request**: Compte inactif
- Vérifiez les identifiants

---

## Test 2: Login Pharmacien ✅

### Objectif
Vérifier que le pharmacien peut aussi se connecter.

### Étapes

1. **Si déjà connecté**: 
   - Cliquez "Authorize" 🔓
   - Cliquez "Logout"
   - Cliquez "Close"

2. **Login Pharmacien**:
   - Route: `POST /auth/login`
   - "Try it out"
   - Entrez:
     ```
     username: pharmacist1
     password: pharma123
     ```
   - "Execute"

3. **Résultat attendu** ✅:
   ```json
   {
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "token_type": "bearer"
   }
   ```
   - Code: **200 OK**
   - Token différent de celui de l'admin

4. **Vérifications**:
   - [ ] Code 200 OK
   - [ ] Token reçu
   - [ ] Token différent de l'admin (normal!)

---

## Test 3: Permissions Admin 🔐

### Objectif
Vérifier que l'admin a accès à TOUTES les fonctionnalités.

### Préparation
1. Connectez-vous comme **admin**
2. Récupérez le token
3. Cliquez "Authorize"
4. Entrez: `Bearer <token_admin>`
5. "Authorize" puis "Close"

### 3.1 - Voir son Profil ✅

**Route**: `GET /auth/me`

**Étapes**:
1. "Try it out"
2. "Execute"

**Résultat attendu**:
```json
{
  "id": 1,
  "username": "admin",
  "role": "admin",
  "is_active": true,
  "created_at": "2025-12-11T...",
  "updated_at": "2025-12-11T..."
}
```

**Vérifications**:
- [ ] Code 200 OK
- [ ] username = "admin"
- [ ] role = "admin" ✅
- [ ] is_active = true

### 3.2 - Créer un Utilisateur ✅

**Route**: `POST /auth/register`

**Étapes**:
1. "Try it out"
2. Entrez:
   ```json
   {
     "username": "test_pharmacien",
     "password": "test123",
     "role": "pharmacist",
     "is_active": true
   }
   ```
3. "Execute"

**Résultat attendu**:
```json
{
  "id": 3,
  "username": "test_pharmacien",
  "role": "pharmacist",
  "is_active": true,
  "created_at": "...",
  "updated_at": "..."
}
```

**Vérifications**:
- [ ] Code 200 OK
- [ ] Utilisateur créé
- [ ] ID attribué automatiquement
- [ ] Dates created_at et updated_at présentes

### 3.3 - Créer un Autre Admin ✅

**Route**: `POST /auth/register`

**Étapes**:
1. "Try it out"
2. Entrez:
   ```json
   {
     "username": "admin2",
     "password": "admin456",
     "role": "admin",
     "is_active": true
   }
   ```
3. "Execute"

**Résultat attendu**:
```json
{
  "id": 4,
  "username": "admin2",
  "role": "admin",
  "is_active": true,
  ...
}
```

**Vérifications**:
- [ ] Code 200 OK
- [ ] Admin peut créer d'autres admins ✅
- [ ] role = "admin"

### 3.4 - Accéder à la Route Protégée ✅

**Route**: `GET /metrics`

**Étapes**:
1. "Try it out"
2. "Execute"

**Résultat attendu**:
```json
{
  "message": "Access granted to protected route",
  "user": {
    "username": "admin",
    "role": "admin",
    "is_active": true
  },
  "timestamp": "2025-12-11T...",
  "status": "authenticated"
}
```

**Vérifications**:
- [ ] Code 200 OK
- [ ] Message "Access granted"
- [ ] user.username = "admin"
- [ ] user.role = "admin"

---

## Test 4: Permissions Pharmacien 🔒

### Objectif
Vérifier que le pharmacien a des permissions LIMITÉES.

### Préparation
1. **Logout de l'admin**:
   - "Authorize" → "Logout" → "Close"
   
2. **Login Pharmacien**:
   - `POST /auth/login`
   - username: `pharmacist1`
   - password: `pharma123`
   
3. **Authorize**:
   - Copier le token
   - "Authorize"
   - `Bearer <token_pharmacien>`

### 4.1 - Voir son Profil ✅

**Route**: `GET /auth/me`

**Résultat attendu**:
```json
{
  "id": 2,
  "username": "pharmacist1",
  "role": "pharmacist",
  "is_active": true,
  ...
}
```

**Vérifications**:
- [ ] Code 200 OK
- [ ] username = "pharmacist1"
- [ ] role = "pharmacist" ✅
- [ ] Le pharmacien peut voir son profil

### 4.2 - Essayer de Créer un Utilisateur ❌

**Route**: `POST /auth/register`

**Étapes**:
1. "Try it out"
2. Entrez:
   ```json
   {
     "username": "hacker",
     "password": "hack123",
     "role": "admin",
     "is_active": true
   }
   ```
3. "Execute"

**Résultat attendu** ❌:
```json
{
  "detail": "Access forbidden: Admin privileges required"
}
```

**Code**: **403 Forbidden**

**Vérifications**:
- [ ] Code 403 Forbidden ✅
- [ ] Message "Admin privileges required"
- [ ] Utilisateur PAS créé
- [ ] **C'EST NORMAL!** Le pharmacien ne peut PAS créer d'utilisateurs

### 4.3 - Accéder à la Route Protégée ✅

**Route**: `GET /metrics`

**Résultat attendu**:
```json
{
  "message": "Access granted to protected route",
  "user": {
    "username": "pharmacist1",
    "role": "pharmacist",
    "is_active": true
  },
  "timestamp": "...",
  "status": "authenticated"
}
```

**Vérifications**:
- [ ] Code 200 OK
- [ ] user.username = "pharmacist1"
- [ ] user.role = "pharmacist"
- [ ] Le pharmacien PEUT accéder aux routes protégées (mais pas admin-only)

---

## Test 5: Routes Sans Authentification 🔓

### Objectif
Vérifier que certaines routes sont publiques, d'autres protégées.

### Préparation
1. **Logout complet**:
   - "Authorize" → "Logout" → "Close"
   - Vous n'êtes plus authentifié

### 5.1 - Login Public ✅

**Route**: `POST /auth/login`

**Test**:
- Essayez de vous connecter (admin ou pharmacien)

**Résultat**:
- [ ] ✅ Fonctionne sans authentification
- [ ] C'est normal, le login DOIT être public

### 5.2 - Route Protégée Sans Token ❌

**Route**: `GET /auth/me`

**Résultat attendu**:
```json
{
  "detail": "Not authenticated"
}
```

**Code**: **401 Unauthorized**

**Vérifications**:
- [ ] Code 401 ✅
- [ ] "Not authenticated"
- [ ] **C'est normal!** Cette route nécessite un token

### 5.3 - Metrics Sans Token ❌

**Route**: `GET /metrics`

**Résultat attendu**:
```json
{
  "detail": "Not authenticated"
}
```

**Code**: **401 Unauthorized**

**Vérifications**:
- [ ] Code 401 ✅
- [ ] Route protégée fonctionne correctement

### 5.4 - Register Sans Token ❌

**Route**: `POST /auth/register`

**Résultat attendu**:
```json
{
  "detail": "Not authenticated"
}
```

**Code**: **401 Unauthorized**

**Vérifications**:
- [ ] Code 401 ✅
- [ ] Impossible de créer des users sans être connecté

### 5.5 - Routes Publiques ✅

**Routes à tester** (devraient fonctionner):
- `GET /` → Welcome message
- `GET /health` → Health check
- `GET /docs` → Documentation Swagger
- `GET /openapi.json` → Schéma OpenAPI

**Vérifications**:
- [ ] Toutes retournent 200 OK
- [ ] Accessibles sans authentification

---

## Test 6: Erreurs d'Authentification ❌

### 6.1 - Mauvais Mot de Passe

**Route**: `POST /auth/login`

**Étapes**:
1. username: `admin`
2. password: `MAUVAIS_PASSWORD`
3. "Execute"

**Résultat attendu**:
```json
{
  "detail": "Incorrect username or password"
}
```

**Code**: **401 Unauthorized**

**Vérifications**:
- [ ] Code 401
- [ ] Message d'erreur clair
- [ ] Pas de token généré

### 6.2 - Username Inexistant

**Route**: `POST /auth/login`

**Étapes**:
1. username: `utilisateur_inexistant`
2. password: `n_importe_quoi`
3. "Execute"

**Résultat attendu**:
```json
{
  "detail": "Incorrect username or password"
}
```

**Code**: **401 Unauthorized**

**Vérifications**:
- [ ] Code 401
- [ ] Même message (pour ne pas révéler si le user existe)

### 6.3 - Username Déjà Existant

**Préparation**: Connectez-vous comme admin

**Route**: `POST /auth/register`

**Étapes**:
1. Essayez de créer un user avec username: `admin` (existe déjà)
2. "Execute"

**Résultat attendu**:
```json
{
  "detail": "Username 'admin' already exists"
}
```

**Code**: **400 Bad Request**

**Vérifications**:
- [ ] Code 400
- [ ] Message mentionne le username
- [ ] Utilisateur PAS créé

---

## Test 7: Token JWT 🔐

### 7.1 - Token Valide ✅

**Objectif**: Vérifier qu'un token valide fonctionne

**Étapes**:
1. Login comme admin
2. Copier le token
3. Authorize avec `Bearer <token>`
4. Tester `GET /auth/me` → ✅ Devrait fonctionner

**Vérifications**:
- [ ] Code 200 OK
- [ ] Données utilisateur retournées

### 7.2 - Token Invalide ❌

**Objectif**: Vérifier qu'un faux token est rejeté

**Étapes**:
1. Logout
2. Authorize avec un faux token: `Bearer FAUX_TOKEN_123`
3. Tester `GET /auth/me`

**Résultat attendu**:
```json
{
  "detail": "Could not validate credentials"
}
```

**Code**: **401 Unauthorized**

**Vérifications**:
- [ ] Code 401
- [ ] Token invalide rejeté

### 7.3 - Token Sans "Bearer" ❌

**Étapes**:
1. Authorize avec juste le token (sans "Bearer ")
2. Exemple: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
3. Tester `GET /auth/me`

**Résultat**:
- [ ] ❌ Erreur d'authentification
- [ ] Il FAUT mettre "Bearer " avant le token

### 7.4 - Token Expiré ⏰

**Note**: Les tokens expirent après **30 minutes**

**Test** (optionnel):
1. Récupérez un token
2. Attendez 30+ minutes
3. Essayez d'utiliser le token

**Résultat attendu**:
- [ ] 401 Unauthorized
- [ ] Token expiré
- [ ] Il faut se reconnecter

---

## 📊 Tableau Récapitulatif des Tests

| # | Test | Admin | Pharmacien | Sans Auth |
|---|------|-------|------------|-----------|
| 1 | Login | ✅ 200 | ✅ 200 | ✅ 200 |
| 2 | GET `/auth/me` | ✅ 200 | ✅ 200 | ❌ 401 |
| 3 | POST `/auth/register` | ✅ 200 | ❌ 403 | ❌ 401 |
| 4 | GET `/metrics` | ✅ 200 | ✅ 200 | ❌ 401 |
| 5 | GET `/` | ✅ 200 | ✅ 200 | ✅ 200 |
| 6 | GET `/health` | ✅ 200 | ✅ 200 | ✅ 200 |

### Légende
- ✅ = Accès autorisé
- ❌ = Accès refusé (normal!)

---

## ✅ Checklist Complète

### Tests Fonctionnels
- [ ] Admin peut se connecter
- [ ] Pharmacien peut se connecter
- [ ] Admin peut créer des users
- [ ] Pharmacien NE PEUT PAS créer des users
- [ ] Les deux peuvent voir leur profil
- [ ] Les deux peuvent accéder à `/metrics`
- [ ] Routes publiques fonctionnent sans auth

### Tests de Sécurité
- [ ] Mauvais password rejeté (401)
- [ ] User inexistant rejeté (401)
- [ ] Username dupliqué rejeté (400)
- [ ] Token invalide rejeté (401)
- [ ] Routes protégées sans token → 401
- [ ] Admin-only routes sans admin → 403

### Tests de Token
- [ ] Token généré au login
- [ ] Token commence par "eyJ"
- [ ] Token type = "bearer"
- [ ] Token doit avoir "Bearer " devant
- [ ] Token contient le username
- [ ] Token expire après 30 min

---

## 🎓 Scénarios Complets

### Scénario 1: Journée d'un Admin

1. **Matin**: Login admin
2. **Créer un nouveau pharmacien** pour remplacer un employé
3. **Vérifier son profil** (GET /auth/me)
4. **Tester que le nouveau pharmacien peut se connecter**
5. **Logout**

### Scénario 2: Journée d'un Pharmacien

1. **Login** pharmacien
2. **Voir son profil**
3. **Accéder à /metrics** ✅
4. **Essayer de créer un user** ❌ 403
5. **Logout**

### Scénario 3: Attaque (Sécurité)

1. **Essayer de deviner un password** → 401
2. **Utiliser un faux token** → 401
3. **Pharmacien essaie d'être admin** → 403
4. **Créer un user sans être connecté** → 401

**Résultat**: ✅ Toutes les attaques sont bloquées!

---

## 🏆 Résultat Final

Si **TOUS** les tests passent:

✅ **Module 2 est 100% fonctionnel!**

- Authentification sécurisée
- Gestion des rôles (RBAC)
- Protection des routes
- Tokens JWT valides
- Erreurs gérées correctement

**Prêt pour le Module 3!** 🚀

---

**Temps estimé pour tous les tests**: 15-20 minutes
**Niveau de difficulté**: Débutant
**Prérequis**: Serveur lancé + Admin créé
