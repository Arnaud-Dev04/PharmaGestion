# 🧪 Guide de Tests - Module 3: Stock & Fournisseurs

## 📋 Vue d'ensemble

Ce guide vous permet de tester **toutes** les fonctionnalités du Module 3:
- ✅ Configuration (Familles et Types)
- ✅ Gestion du Stock
- ✅ Alertes Stock
- ✅ Fournisseurs
- ✅ Permissions Admin vs Pharmacien

**Durée estimée**: 20 minutes

---

## 🎯 Préparation

### 1. Serveur en Route
Le serveur doit tourner:
```bash
uvicorn main:app --reload
```

### 2. Ouvrir Swagger
http://localhost:8000/docs

### 3. Login Admin
- Route: `POST /auth/login`
- Credentials: `admin` / `admin123`
- Copier le token
- Cliquer "Authorize" → `Bearer <token>`

✅ Vous êtes prêt!

---

## Test 1: Configuration - Familles de Médicaments

### 1.1 - Créer des Familles ✅

**Route**: `POST /config/families`

**Créer 3 familles**:

**Famille 1**:
```json
{
  "name": "Antibiotiques"
}
```
→ Résultat: 200 OK, `id: 1`

**Famille 2**:
```json
{
  "name": "Antipaludiques"
}
```
→ Résultat: 200 OK, `id: 2`

**Famille 3**:
```json
{
  "name": "Antidouleurs"
}
```
→ Résultat: 200 OK, `id: 3`

**Vérifications**:
- [ ] Code 201 Created
- [ ] IDs attribués (1, 2, 3)
- [ ] Timestamps présents

### 1.2 - Lister les Familles ✅

**Route**: `GET /config/families`

**Résultat attendu**:
```json
[
  {
    "id": 1,
    "name": "Antibiotiques",
    "created_at": "...",
    "updated_at": "..."
  },
  {
    "id": 2,
    "name": "Antipaludiques",
    "created_at": "...",
    "updated_at": "..."
  },
  {
    "id": 3,
    "name": "Antidouleurs",
    "created_at": "...",
    "updated_at": "..."
  }
]
```

**Vérifications**:
- [ ] 3 familles retournées
- [ ] Ordre alphabétique

### 1.3 - Modifier une Famille ✅

**Route**: `PUT /config/families/1`

```json
{
  "name": "Antibiotiques (Beta-lactamines)"
}
```

**Résultat**: 200 OK, nom modifié

**Vérifications**:
- [ ] Nom mis à jour
- [ ] `updated_at` changé

### 1.4 - Tenter de Supprimer une Famille (Vide) ✅

**Route**: `DELETE /config/families/3`

**Résultat**: 204 No Content

**Vérifications**:
- [ ] Famille supprimée (aucun médicament lié)

---

## Test 2: Configuration - Types de Médicaments

### 2.1 - Créer des Types ✅

**Route**: `POST /config/types`

**Type 1**:
```json
{
  "name": "Plaquette"
}
```

**Type 2**:
```json
{
  "name": "Flacon"
}
```

**Type 3**:
```json
{
  "name": "Ampoule"
}
```

**Type 4**:
```json
{
  "name": "Sachet"
}
```

**Vérifications**:
- [ ] 4 types créés
- [ ] IDs 1, 2, 3, 4

### 2.2 - Lister les Types ✅

**Route**: `GET /config/types`

**Résultat**: 4 types retournés

---

## Test 3: Fournisseurs

### 3.1 - Créer des Fournisseurs ✅

**Route**: `POST /suppliers`

**Fournisseur 1**:
```json
{
  "name": "Pharma Distributeur SA",
  "phone": "+25771234567",
  "email": "contact@pharmadist.bi",
  "contact_name": "Jean Dupont"
}
```

**Fournisseur 2**:
```json
{
  "name": "Medic Import SARL",
  "phone": "+25772345678",
  "email": "info@medicimport.bi",
  "contact_name": "Marie Niyonzima"
}
```

**Vérifications**:
- [ ] 2 fournisseurs créés
- [ ] IDs attribués

### 3.2 - Lister les Fournisseurs ✅

**Route**: `GET /suppliers?page=1&page_size=10`

**Résultat attendu**:
```json
{
  "items": [...],
  "total": 2,
  "page": 1,
  "page_size": 10,
  "total_pages": 1
}
```

**Vérifications**:
- [ ] Pagination fonctionne
- [ ] 2 fournisseurs retournés

### 3.3 - Voir un Fournisseur ✅

**Route**: `GET /suppliers/1`

**Résultat**: Détails du fournisseur 1

### 3.4 - Modifier un Fournisseur ✅

**Route**: `PUT /suppliers/1`

```json
{
  "phone": "+25779999999"
}
```

**Résultat**: Téléphone mis à jour

---

## Test 4: Médicaments - CRUD

### 4.1 - Créer des Médicaments ✅

**Route**: `POST /stock/medicines`

**Médicament 1** (Stock normal):
```json
{
  "code": "MED-001",
  "name": "Paracétamol 500mg",
  "family_id": 2,
  "type_id": 1,
  "quantity": 100,
  "price_buy": 500.0,
  "price_sell": 800.0,
  "expiry_date": "2026-12-31",
  "min_stock_alert": 20
}
```

**Médicament 2** (Stock faible):
```json
{
  "code": "MED-002",
  "name": "Amoxicilline 250mg",
  "family_id": 1,
  "type_id": 1,
  "quantity": 8,
  "price_buy": 1000.0,
  "price_sell": 1500.0,
  "expiry_date": "2027-06-30",
  "min_stock_alert": 20
}
```

**Médicament 3** (Périmé):
```json
{
  "code": "MED-003",
  "name": "Vitamine C 1000mg",
  "family_id": 2,
  "type_id": 4,
  "quantity": 50,
  "price_buy": 300.0,
  "price_sell": 500.0,
  "expiry_date": "2024-11-30",
  "min_stock_alert": 10
}
```

**Médicament 4** (Stock faible ET périmé):
```json
{
  "code": "MED-004",
  "name": "Aspirine 100mg",
  "family_id": 2,
  "type_id": 1,
  "quantity": 5,
  "price_buy": 200.0,
  "price_sell": 350.0,
  "expiry_date": "2024-12-01",
  "min_stock_alert": 15
}
```

**Médicament 5** (Sans famille ni type):
```json
{
  "code": "MED-005",
  "name": "Produit générique",
  "quantity": 200,
  "price_buy": 100.0,
  "price_sell": 150.0,
  "min_stock_alert": 30
}
```

**Vérifications**:
- [ ] 5 médicaments créés
- [ ] Champs calculés: `is_low_stock`, `is_expired`, `margin`
- [ ] Relations family/type chargées

### 4.2 - Lister les Médicaments ✅

**Route**: `GET /stock/medicines?page=1&page_size=10`

**Résultat attendu**:
```json
{
  "items": [
    {
      "id": 1,
      "code": "MED-001",
      "name": "Paracétamol 500mg",
      "quantity": 100,
      "is_low_stock": false,
      "is_expired": false,
      "margin": 300.0,
      "family": {
        "id": 2,
        "name": "Antidouleurs"
      },
      "type": {
        "id": 1,
        "name": "Plaquette"
      }
    }
  ],
  "total": 5,
  "page": 1,
  "page_size": 10,
  "total_pages": 1
}
```

**Vérifications**:
- [ ] 5 médicaments retournés
- [ ] Pagination OK
- [ ] Champs calculés présents

### 4.3 - Voir un Médicament ✅

**Route**: `GET /stock/medicines/1`

**Résultat**: Détails complets du médicament 1

### 4.4 - Modifier un Médicament ✅

**Route**: `PUT /stock/medicines/1`

```json
{
  "quantity": 150,
  "price_sell": 850.0
}
```

**Résultat**: Quantité et prix modifiés

**Vérifications**:
- [ ] Mise à jour partielle fonctionne
- [ ] Autres champs inchangés

### 4.5 - Supprimer un Médicament ✅

**Route**: `DELETE /stock/medicines/5`

**Résultat**: 204 No Content

**Vérifications**:
- [ ] Médicament supprimé
- [ ] Plus dans la liste

---

## Test 5: Recherche et Filtres

### 5.1 - Recherche par Nom ✅

**Route**: `GET /stock/medicines?search=paracetamol`

**Résultat**: MED-001 retourné

### 5.2 - Recherche par Code ✅

**Route**: `GET /stock/medicines?search=MED-002`

**Résultat**: MED-002 retourné

### 5.3 - Filtrer par Famille ✅

**Route**: `GET /stock/medicines?family_id=1`

**Résultat**: Amoxicilline (famille Antibiotiques)

### 5.4 - Filtrer par Type ✅

**Route**: `GET /stock/medicines?type_id=1`

**Résultat**: Toutes les plaquettes

### 5.5 - Filtrer Stock Faible ✅

**Route**: `GET /stock/medicines?is_low_stock=true`

**Résultat**: MED-002 et MED-004 (quantity ≤ min_stock_alert)

### 5.6 - Filtrer Périmés ✅

**Route**: `GET /stock/medicines?is_expired=true`

**Résultat**: MED-003 et MED-004 (expiry_date ≤ aujourd'hui)

### 5.7 - Filtres Combinés ✅

**Route**: `GET /stock/medicines?family_id=2&is_low_stock=true`

**Résultat**: Médicaments de famille 2 avec stock faible

---

## Test 6: Alertes Stock

### 6.1 - Voir Toutes les Alertes ✅

**Route**: `GET /stock/alerts`

**Résultat attendu**:
```json
{
  "low_stock": [
    {
      "id": 2,
      "code": "MED-002",
      "name": "Amoxicilline 250mg",
      "quantity": 8,
      "min_stock_alert": 20,
      "is_low_stock": true
    },
    {
      "id": 4,
      "code": "MED-004",
      "name": "Aspirine 100mg",
      "quantity": 5,
      "min_stock_alert": 15,
      "is_low_stock": true
    }
  ],
  "expired": [
    {
      "id": 3,
      "code": "MED-003",
      "name": "Vitamine C 1000mg",
      "expiry_date": "2024-11-30",
      "is_expired": true
    },
    {
      "id": 4,
      "code": "MED-004",
      "name": "Aspirine 100mg",
      "expiry_date": "2024-12-01",
      "is_expired": true
    }
  ],
  "total_alerts": 3
}
```

**Vérifications**:
- [ ] 2-3 alertes stock faible
- [ ] 2 alertes périmés
- [ ] MED-004 dans les deux catégories (possible)
- [ ] Total correct

---

## Test 7: Pagination

### 7.1 - Page 1 (2 items) ✅

**Route**: `GET /stock/medicines?page=1&page_size=2`

**Résultat**:
```json
{
  "items": [<2 items>],
  "total": 4,
  "page": 1,
  "page_size": 2,
  "total_pages": 2
}
```

### 7.2 - Page 2 ✅

**Route**: `GET /stock/medicines?page=2&page_size=2`

**Résultat**: 2 items suivants

**Vérifications**:
- [ ] Pas de doublons entre pages
- [ ] Total cohérent

---

## Test 8: Permissions Pharmacien

### 8.1 - Logout Admin et Login Pharmacien

1. "Authorize" → "Logout"
2. `POST /auth/login` avec `pharmacist1` / `pharma123`
3. Copier le nouveau token
4. "Authorize" → `Bearer <nouveau_token>`

### 8.2 - Pharmacien Peut Voir ✅

**Routes à tester**:
- `GET /config/families` → ✅ 200 OK
- `GET /config/types` → ✅ 200 OK
- `GET /stock/medicines` → ✅ 200 OK
- `GET /stock/medicines/1` → ✅ 200 OK
- `GET /stock/alerts` → ✅ 200 OK
- `GET /suppliers` → ✅ 200 OK

### 8.3 - Pharmacien NE PEUT PAS Modifier ❌

**Routes à tester**:

**POST famille**:
```bash
POST /config/families
{"name": "Test"}
```
→ **403 Forbidden** ✅

**POST médicament**:
```bash
POST /stock/medicines
{...}
```
→ **403 Forbidden** ✅

**PUT médicament**:
```bash
PUT /stock/medicines/1
{"quantity": 999}
```
→ **403 Forbidden** ✅

**DELETE médicament**:
```bash
DELETE /stock/medicines/1
```
→ **403 Forbidden** ✅

**POST fournisseur**:
```bash
POST /suppliers
{...}
```
→ **403 Forbidden** ✅

**Vérifications**:
- [ ] Toutes les modifications bloquées (403)
- [ ] Message: "Access forbidden: Admin privileges required"

---

## Test 9: Validation et Erreurs

### 9.1 - Code Dupliqué ❌

**Login Admin → POST /stock/medicines**

```json
{
  "code": "MED-001",
  "name": "Test",
  "quantity": 10,
  "price_buy": 100,
  "price_sell": 150,
  "min_stock_alert": 5
}
```

**Résultat**: 400 Bad Request
```json
{
  "detail": "Medicine with code 'MED-001' already exists"
}
```

### 9.2 - Famille Inexistante ❌

```json
{
  "code": "TEST-999",
  "name": "Test",
  "family_id": 9999,
  "quantity": 10,
  "price_buy": 100,
  "price_sell": 150,
  "min_stock_alert": 5
}
```

**Résultat**: 404 Not Found
```json
{
  "detail": "Medicine family with ID 9999 not found"
}
```

### 9.3 - Médicament Inexistant ❌

**Route**: `GET /stock/medicines/9999`

**Résultat**: 404 Not Found

### 9.4 - Supprimer Famille Utilisée ❌

**Route**: `DELETE /config/families/1`

**Résultat**: 400 Bad Request (famille utilisée par MED-002)

---

## 📊 Tableau Récapitulatif

| Test | Endpoint | Admin | Pharmacien | Résultat |
|------|----------|-------|------------|----------|
| Créer famille | POST /config/families | ✅ 201 | ❌ 403 | - |
| Lister familles | GET /config/families | ✅ 200 | ✅ 200 | - |
| Créer type | POST /config/types | ✅ 201 | ❌ 403 | - |
| Créer médicament | POST /stock/medicines | ✅ 201 | ❌ 403 | - |
| Lister médicaments | GET /stock/medicines | ✅ 200 | ✅ 200 | - |
| Modifier médicament | PUT /stock/medicines/{id} | ✅ 200 | ❌ 403 | - |
| Supprimer médicament | DELETE /stock/medicines/{id} | ✅ 204 | ❌ 403 | - |
| Rechercher | GET /stock/medicines?search=x | ✅ 200 | ✅ 200 | - |
| Filtrer famille | GET /stock/medicines?family_id=1 | ✅ 200 | ✅ 200 | - |
| Alertes | GET /stock/alerts | ✅ 200 | ✅ 200 | - |
| Créer fournisseur | POST /suppliers | ✅ 201 | ❌ 403 | - |
| Lister fournisseurs | GET /suppliers | ✅ 200 | ✅ 200 | - |

---

## ✅ Checklist Finale

### Configuration
- [ ] 2+ familles créées
- [ ] 3+ types créés
- [ ] Modification fonctionne
- [ ] Suppression bloquée si utilisée

### Médicaments
- [ ] 4+ médicaments créés
- [ ] CRUD complet (Create, Read, Update, Delete)
- [ ] Champs calculés OK (is_low_stock, is_expired, margin)
- [ ] Relations family/type chargées

### Recherche & Filtres
- [ ] Recherche par nom fonctionne
- [ ] Recherche par code fonctionne
- [ ] Filtrer par famille
- [ ] Filtrer par type
- [ ] Filtrer stock faible
- [ ] Filtrer périmés

### Alertes
- [ ] Alertes stock faible détectées
- [ ] Alertes périmés détectées
- [ ] Total correct

### Pagination
- [ ] Pagination fonctionne
- [ ] Total_pages calculé
- [ ] Page_size respecté

### Fournisseurs
- [ ] CRUD complet fonctionne

### Permissions
- [ ] Admin: CRUD complet ✅
- [ ] Pharmacien: Lecture seule ✅
- [ ] Modifications bloquées (403) ❌

### Validation
- [ ] Codes dupliqués rejetés
- [ ] Familles/types inexistants rejetés
- [ ] Médicaments inexistants → 404

---

## 🏆 Résultat

Si **TOUS** les tests passent:

✅ **Module 3 est 100% fonctionnel!**

- Gestion complète du stock
- Recherche et filtres avancés
- Alertes automatiques
- Configuration dynamique
- Permissions RBAC
- Validation robuste

**Prêt pour le Module 4!** 🚀

---

**Temps total**: 20-25 minutes  
**Difficulté**: Intermédiaire  
**Prérequis**: Module 2 testé
