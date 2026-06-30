# 🔧 Plan de Débogage — PharmaGestion v1.0

Analyse complète du projet `Pharma_logiciels_version_01` : Backend FastAPI (Python) + Frontend Flutter (Dart).

---

## 📊 Résumé des problèmes trouvés

| Catégorie | Critiques 🔴 | Importants 🟡 | Mineurs 🟢 |
|-----------|:---:|:---:|:---:|
| **Backend** | 5 | 6 | 4 |
| **Frontend** | 3 | 5 | 3 |
| **Total** | **8** | **11** | **7** |

---

# PARTIE 1 : BACKEND (FastAPI / Python)

---

## 🔴 Bugs Critiques Backend

### B1. Crash — Référence à `user.first_name` / `user.last_name` inexistants
**Fichiers** : [sales.py](file:///c:/Pharma_logiciels_version_01/backend/app/routes/sales.py#L41-L46), [dashboard_service.py](file:///c:/Pharma_logiciels_version_01/backend/app/services/dashboard_service.py#L228-L229)

Le modèle `User` ne contient que `username`, `password_hash`, `role`, `is_active`. **Pas de champs `first_name` ni `last_name`.**

Or, dans `sales.py` (ligne 44) et `dashboard_service.py` (ligne 228), le code fait :
```python
if user.first_name and user.last_name:
    return f"{user.first_name} {user.last_name}"
```
→ **`AttributeError` à chaque appel** de `enrich_sale_response()` et `get_cancelled_sales_details()`.

**Correction** : Ajouter `first_name` et `last_name` au modèle `User`, OU supprimer ces références et utiliser `username` directement.

---

### B2. Écrasement du montant total dans `create_sale()`
**Fichier** : [sales_service.py](file:///c:/Pharma_logiciels_version_01/backend/app/services/sales_service.py#L237-L269)

```python
# Ligne 237 : total calculé correctement
total_amount = calculate_sale_total(validated_items)

# Ligne 241-243 : remise globale appliquée
if sale_data.discount_percent and sale_data.discount_percent > 0:
    discount_amount = total_amount * (sale_data.discount_percent / 100)
    total_amount -= discount_amount

# ...

# Ligne 269 : ⚠️ ÉCRASÉ À ZÉRO !
total_amount = 0.0  # ← BUG
```
Le `total_amount` calculé (avec remise) est **réinitialisé à 0.0** puis recalculé dans la boucle des items, MAIS sans la remise globale. La remise globale (`discount_percent` sur la vente) est donc **ignorée**.

**Correction** : Supprimer la ligne 269 (`total_amount = 0.0`) ou restructurer la logique pour ne calculer qu'une seule fois.

---

### B3. `check_database_connection` — Requête SQL brute invalide
**Fichier** : [core.py](file:///c:/Pharma_logiciels_version_01/backend/app/database/core.py#L194)

```python
conn.execute("SELECT 1")  # ← Erreur avec SQLAlchemy 2.0+
```
SQLAlchemy 2.0 requiert `text()` :
```python
from sqlalchemy import text
conn.execute(text("SELECT 1"))
```
→ `ObjectNotExecutableError` à chaque appel.

---

### B4. Conflit de route — `/medicines/expiring-soon` masquée
**Fichier** : [stock.py](file:///c:/Pharma_logiciels_version_01/backend/app/routes/stock.py#L83-L248)

La route `/medicines/{medicine_id}` (ligne 83) est définie **AVANT** `/medicines/expiring-soon` (ligne 234). FastAPI va essayer de parser `"expiring-soon"` comme un `int` pour `medicine_id` → **erreur 422 (validation)**.

**Correction** : Déplacer `/medicines/expiring-soon` **avant** `/medicines/{medicine_id}`.

---

### B5. Clé secrète JWT en dur par défaut
**Fichier** : [security.py](file:///c:/Pharma_logiciels_version_01/backend/app/utils/security.py#L16)

```python
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-this-in-production")
```
Si `.env` est absent (ce qui est le cas — pas de `.env` dans le dossier backend), **tous les tokens JWT sont signés avec une clé publique connue**. Faille de sécurité critique.

---

## 🟡 Bugs Importants Backend

### B6. `declarative_base()` déprécié
**Fichier** : [core.py](file:///c:/Pharma_logiciels_version_01/backend/app/database/core.py#L60)

`declarative_base()` importé depuis `sqlalchemy.ext.declarative` est **déprécié** depuis SQLAlchemy 2.0. Devrait utiliser `from sqlalchemy.orm import DeclarativeBase`.

---

### B7. Import `sys` en doublon
**Fichier** : [core.py](file:///c:/Pharma_logiciels_version_01/backend/app/database/core.py#L11-L13)

```python
import sys     # Ligne 11
import sys     # Ligne 13  ← doublon
```

---

### B8. Pollution de debug logs — chemins hardcodés
**Fichiers** : [main.py](file:///c:/Pharma_logiciels_version_01/backend/main.py), [core.py](file:///c:/Pharma_logiciels_version_01/backend/app/database/core.py)

Des dizaines de blocs `#region agent log` écrivent dans `c:\Pharma_logiciels_version_01\.cursor\debug.log`. Ces blocs :
- Utilisent un **chemin absolu hardcodé** → crash sur une autre machine
- Polluent le code et réduisent la lisibilité
- `except: pass` masque toutes les exceptions

**Correction** : Supprimer tous les blocs `#region agent log` / `#endregion`.

---

### B9. `engine_remote` toujours créé — erreurs MySQL inutiles
**Fichier** : [core.py](file:///c:/Pharma_logiciels_version_01/backend/app/database/core.py#L48-L53)

Le moteur MySQL distant est **toujours instancié**, même en mode SQLite-only. Si MySQL n'est pas installé, cela peut générer des warnings ou des erreurs silencieuses au démarrage.

**Correction** : Créer `engine_remote` de manière lazy, seulement quand utilisé.

---

### B10. License middleware inutile (no-op)
**Fichier** : [main.py](file:///c:/Pharma_logiciels_version_01/backend/main.py#L114-L134)

Le middleware `check_license_middleware` fait `return await call_next(request)` dans tous les cas. Le commentaire dit "License check is now handled in dependencies.py". Ce middleware **consomme du temps sur chaque requête** sans rien faire.

---

### B11. `datetime.utcnow()` déprécié
**Fichiers** : [security.py](file:///c:/Pharma_logiciels_version_01/backend/app/utils/security.py#L84-L86), [sales_service.py](file:///c:/Pharma_logiciels_version_01/backend/app/services/sales_service.py#L257)

`datetime.utcnow()` est **déprécié** depuis Python 3.12. Utiliser `datetime.now(timezone.utc)`.

---

## 🟢 Bugs Mineurs Backend

### B12. `customer_service` lance `HTTPException` dans la couche service
**Fichier** : [customer_service.py](file:///c:/Pharma_logiciels_version_01/backend/app/services/customer_service.py#L165-L168)

La couche service ne devrait pas lever de `HTTPException` (c'est la responsabilité des routes). Ça viole la séparation des couches.

---

### B13. `SaleStatus` enum vs colonne string
Le modèle `Sale.status` est un `Column(String(20))`, mais `dashboard_service.py` filtre avec `Sale.status == SaleStatus.CANCELLED` (un Enum). SQLite ne va pas forcément matcher correctement.

---

### B14. `CORS: allow_origins=["*"]` + `allow_credentials=True`
**Fichier** : [main.py](file:///c:/Pharma_logiciels_version_01/backend/main.py#L101-L107)

Techniquement invalide selon la spec CORS. Les navigateurs modernes peuvent rejeter cette combinaison.

---

### B15. Pas de fichier `.env` dans le backend
Le `.env.example` existe mais pas de `.env`. Les valeurs par défaut sont utilisées partout (clé JWT, DB URL…).

---

# PARTIE 2 : FRONTEND (Flutter / Dart)

---

## 🔴 Bugs Critiques Frontend

### F1. Mapping JSON incorrect — `LicenseProvider`
**Fichier** : [license_provider.dart](file:///c:/Pharma_logiciels_version_01/frontend1/lib/providers/license_provider.dart#L17-L24)

Le `fromJson` attend :
```dart
isValid: json['is_valid'],    // ← N'existe PAS dans la réponse backend
isExpired: json['is_expired'], // ← N'existe PAS non plus
```
Le backend retourne :
```json
{"status": "valid", "days_remaining": 250, "expiration_date": "...", "message": "..."}
```
→ `isValid` et `isExpired` seront toujours `true`/`false` par défaut, **jamais la vraie valeur**.

**Correction** : Mapper depuis `json['status']` :
```dart
isValid: json['status'] != 'expired',
isExpired: json['status'] == 'expired',
```

---

### F2. Modèle `User` Flutter — champ `email` fantôme
**Fichier** : [user.dart](file:///c:/Pharma_logiciels_version_01/frontend1/lib/models/user.dart#L4)

Le modèle Flutter `User` contient un champ `email`, mais le modèle backend `User` + `UserResponse` **ne contient pas d'`email`**. L'API ne retourne jamais ce champ → `json['email']` sera toujours `null` → valeur par défaut `''`.

Ce n'est pas un crash, mais c'est trompeur pour le développement futur.

---

### F3. Interception d'erreurs — crash potentiel sur `data['detail']`
**Fichier** : [api_service.dart](file:///c:/Pharma_logiciels_version_01/frontend1/lib/services/api_service.dart#L173-L186)

```dart
errorMessage = err.response?.data['detail'] ?? "Requête invalide (400)";
```
Si `err.response.data` est une `String` au lieu d'un `Map` (ce qui arrive avec certaines erreurs), cela lance un `NoSuchMethodError`.

**Correction** : Vérifier le type avant d'accéder :
```dart
final data = err.response?.data;
if (data is Map) {
  errorMessage = data['detail']?.toString() ?? "...";
}
```

---

## 🟡 Bugs Importants Frontend

### F4. Bouton toggle thème non fonctionnel
**Fichier** : [login_screen.dart](file:///c:/Pharma_logiciels_version_01/frontend1/lib/screens/auth/login_screen.dart#L349-L365)

```dart
onPressed: () {
  // Toggle theme (à implémenter avec ThemeProvider)
  // Pour l'instant, pas d'action
},
```
Le bouton clair/sombre **ne fait rien**. Le `ThemeProvider` existe pourtant.

**Correction** : Appeler `Provider.of<ThemeProvider>(context, listen: false).toggleTheme()`.

---

### F5. "Se souvenir de moi" — non traduit et non fonctionnel
**Fichier** : [login_screen.dart](file:///c:/Pharma_logiciels_version_01/frontend1/lib/screens/auth/login_screen.dart#L459-L487)

1. Le texte "Se souvenir de moi" est **hardcodé en français** au lieu d'utiliser `LanguageProvider.translate()`
2. La valeur `_rememberMe` n'est **jamais utilisée** — le token est toujours sauvegardé

---

### F6. Pas de déconnexion automatique sur 401
**Fichier** : [api_service.dart](file:///c:/Pharma_logiciels_version_01/frontend1/lib/services/api_service.dart#L147-L166)

Quand le token JWT expire, l'intercepteur affiche un message mais **ne déconnecte pas** l'utilisateur. Le commentaire dit "La déconnexion sera gérée par AuthProvider qui écoute les erreurs 401" mais **aucun mécanisme d'écoute n'est implémenté**.

---

### F7. Pas de mécanisme de retry réseau
Aucun retry automatique pour les erreurs réseau transitoires (timeout, connexion perdue momentanément).

---

### F8. `language_provider.dart` — fichier très volumineux (24KB)
**Fichier** : [language_provider.dart](file:///c:/Pharma_logiciels_version_01/frontend1/lib/providers/language_provider.dart)

Ce fichier de 24KB contient probablement toutes les traductions inline. Les traductions devraient utiliser le système i18n de Flutter (`l10n/`) qui est déjà configuré (`l10n.yaml` existe).

---

## 🟢 Bugs Mineurs Frontend

### F9. `analysis_options.yaml` — utilise `flutter_lints` au lieu de `flutter_lints`
Le package `flutter_lints` (v6) est obsolète. Le package actuel est `flutter_lints` ou mieux `very_good_analysis`.

---

### F10. Footer de login — année hardcodée
```dart
'Version 1.0.0 • © 2025 Developped by ArnaudDev'
```
Faute de frappe : "Developped" → "Developed". Et l'année 2025 est hardcodée.

---

### F11. Pas de gestion de l'état offline
Aucun écran de « connexion perdue » ou de mode dégradé si le backend est injoignable.

---

## User Review Required

> [!IMPORTANT]
> **Choix à faire pour B1** : Faut-il ajouter les champs `first_name` et `last_name` au modèle `User` backend (ce qui nécessite une migration DB), ou préférer afficher juste le `username` partout ?

> [!IMPORTANT]
> **Choix à faire pour B5** : Faut-il que je génère un fichier `.env` avec une clé secrète forte aléatoire ?

> [!WARNING]
> **Choix pour B8** : Les blocs de debug log `#region agent log` doivent-ils être entièrement supprimés, ou remplacés par un système de logging Python standard (`logging` module) ?

---

## Plan d'exécution proposé

### Phase 1 — Backend (estimé ~45 min)
1. ~~Analyser~~  ✅
2. Corriger B1 (User model + références)
3. Corriger B2 (total_amount écrasé)
4. Corriger B3 (text() pour SQLAlchemy 2.0)
5. Corriger B4 (ordre des routes stock)
6. Corriger B5 (générer .env)
7. Nettoyer B8 (supprimer debug logs)
8. Corriger B6, B7, B9, B10, B11, B13, B14
9. Tester le démarrage du backend avec `uvicorn`
10. Vérifier les endpoints critiques (`/auth/login`, `/auth/me`, `/stock/medicines`, `/sales/history`)

### Phase 2 — Frontend (estimé ~30 min)
1. ~~Analyser~~  ✅ 
2. Corriger F1 (LicenseProvider mapping)
3. Corriger F2 (User model email)
4. Corriger F3 (error interceptor safe access)
5. Corriger F4 (theme toggle)
6. Corriger F5 (remember me + traduction)
7. Corriger F6 (logout sur 401)
8. Corriger F10 (footer typo)
9. Tester la compilation Flutter (`flutter build windows`)

---

## Vérification

### Tests automatisés
```bash
# Backend : Démarrer et tester les endpoints
cd backend
python -m uvicorn main:app --reload

# Frontend : Compiler sans erreurs
cd frontend1
flutter analyze
flutter build windows
```

### Vérification manuelle
- Login avec admin/admin123
- Navigation dans toutes les pages
- Création d'une vente test
- Vérification du dashboard
