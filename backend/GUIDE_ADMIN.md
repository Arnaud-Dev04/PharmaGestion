# 👨‍💼 Guide Administrateur - Gestion des Utilisateurs

## 📋 Table des Matières

1. [Accès au Système](#accès-au-système)
2. [Créer des Utilisateurs](#créer-des-utilisateurs)
3. [Les Différents Rôles](#les-différents-rôles)
4. [Gérer les Comptes](#gérer-les-comptes)
5. [Exemples Pratiques](#exemples-pratiques)
6. [Sécurité](#sécurité)

---

## 🔐 Accès au Système

### Première Connexion Admin

**Identifiants par défaut** (créés lors de l'installation):
- **Username**: `admin`
- **Password**: `admin123`

> [!WARNING]
> **Important**: Changez le mot de passe admin après la première connexion en production!

### Se Connecter à l'Interface API

1. **Démarrer le serveur**:
   ```bash
   uvicorn main:app --reload
   ```

2. **Ouvrir l'interface Swagger**:
   - Dans votre navigateur: http://localhost:8000/docs
   - Vous verrez toutes les routes API disponibles

3. **Se connecter**:
   - Trouvez la section **"Authentication"**
   - Cliquez sur `POST /auth/login`
   - Cliquez le bouton **"Try it out"**
   - Remplissez le formulaire:
     ```
     username: admin
     password: admin123
     ```
   - Cliquez **"Execute"**

4. **Récupérer le token**:
   - Dans la réponse, vous verrez:
     ```json
     {
       "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
       "token_type": "bearer"
     }
     ```
   - **Copiez** le `access_token` (tout le texte long)

5. **Authoriser toutes les requêtes**:
   - Cliquez le bouton **"Authorize"** 🔓 (en haut à droite de la page)
   - Dans la popup qui s'ouvre, collez: `Bearer <votre_token>`
   - Exemple: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
   - Cliquez **"Authorize"**
   - Cliquez **"Close"**

✅ Vous êtes maintenant authentifié! Toutes les routes protégées sont accessibles.

---

## 👥 Créer des Utilisateurs

### Créer un Pharmacien

**Étape par étape**:

1. **Assurez-vous d'être connecté** (voir section précédente)

2. **Allez sur** `POST /auth/register`

3. **Cliquez** "Try it out"

4. **Remplissez le formulaire**:
   ```json
   {
     "username": "pharmacien1",
     "password": "pharma123",
     "role": "pharmacist",
     "is_active": true
   }
   ```

5. **Cliquez** "Execute"

6. **Résultat attendu** (200 OK):
   ```json
   {
     "id": 2,
     "username": "pharmacien1",
     "role": "pharmacist",
     "is_active": true,
     "created_at": "2025-12-11T09:30:00Z",
     "updated_at": "2025-12-11T09:30:00Z"
   }
   ```

✅ **Le pharmacien peut maintenant se connecter** avec `pharmacien1` / `pharma123`

### Créer un Autre Administrateur

```json
{
  "username": "admin2",
  "password": "AdminSecure456",
  "role": "admin",
  "is_active": true
}
```

### Créer un Compte Désactivé

Pour créer un compte mais le désactiver temporairement:

```json
{
  "username": "stagiaire1",
  "password": "temp123",
  "role": "pharmacist",
  "is_active": false
}
```

⚠️ Cet utilisateur **ne pourra pas se connecter** tant que `is_active` est `false`.

---

## 🎭 Les Différents Rôles

### Tableau des Permissions

| Fonctionnalité | Admin | Pharmacist |
|----------------|-------|------------|
| **Authentification** |
| Se connecter | ✅ | ✅ |
| Voir son profil (`/auth/me`) | ✅ | ✅ |
| **Gestion Utilisateurs** |
| Créer des utilisateurs | ✅ | ❌ |
| Modifier des utilisateurs | ✅ | ❌ |
| Désactiver des comptes | ✅ | ❌ |
| **Stock** (Module 3+) |
| Consulter le stock | ✅ | ✅ |
| Ajouter des produits | ✅ | ✅ |
| Modifier des produits | ✅ | ❌ |
| Supprimer des produits | ✅ | ❌ |
| **Ventes** (Module 4+) |
| Faire des ventes | ✅ | ✅ |
| Voir l'historique | ✅ | ✅ |
| Annuler des ventes | ✅ | ❌ |
| **Rapports** (Module 7+) |
| Générer des rapports | ✅ | ✅ |
| Exporter en Excel/PDF | ✅ | ❌ |

### Rôle: Admin

**Permissions complètes**:
- Gestion totale des utilisateurs
- Accès à toutes les fonctionnalités
- Configuration du système
- Génération de rapports avancés

**Utilisation recommandée**:
- Propriétaire de la pharmacie
- Responsable principal
- Maximum 2-3 comptes admin

### Rôle: Pharmacist

**Permissions limitées**:
- Opérations quotidiennes (ventes, consultation stock)
- Pas d'accès aux fonctions administratives
- Pas de création/suppression d'utilisateurs

**Utilisation recommandée**:
- Employés de la pharmacie
- Vendeurs
- Personnel de terrain

---

## 🛠️ Gérer les Comptes

### Voir les Informations d'un Utilisateur

Pour voir votre propre profil:

1. Connectez-vous
2. Allez sur `GET /auth/me`
3. Cliquez "Try it out"
4. Cliquez "Execute"

**Résultat**:
```json
{
  "id": 1,
  "username": "admin",
  "role": "admin",
  "is_active": true,
  "created_at": "2025-12-11T08:00:00Z",
  "updated_at": "2025-12-11T08:00:00Z"
}
```

### Désactiver un Compte

> [!NOTE]
> Cette fonctionnalité nécessite l'ajout d'une route dans les modules futurs. Pour l'instant, vous pouvez le faire via script Python.

**Via script Python** (`deactivate_user.py`):

```python
from app.database import SessionLocal
from app.models.user import User

db = SessionLocal()
username = input("Username à désactiver: ")

user = db.query(User).filter(User.username == username).first()
if user:
    user.is_active = False
    db.commit()
    print(f"✅ Utilisateur {username} désactivé")
else:
    print(f"❌ Utilisateur {username} introuvable")
    
db.close()
```

---

## 📖 Exemples Pratiques

### Exemple 1: Configuration Initiale d'une Pharmacie

**Contexte**: Nouvelle pharmacie avec 1 propriétaire et 3 employés

**Étapes**:

1. **Créer l'admin principal** (déjà fait):
   ```
   admin / admin123
   ```

2. **Créer le gérant** (aussi admin):
   ```json
   {
     "username": "gerant",
     "password": "Gerant2025!",
     "role": "admin",
     "is_active": true
   }
   ```

3. **Créer les 3 pharmaciens**:
   
   **Pharmacien matin**:
   ```json
   {
     "username": "pharma_matin",
     "password": "Matin123",
     "role": "pharmacist",
     "is_active": true
   }
   ```
   
   **Pharmacien après-midi**:
   ```json
   {
     "username": "pharma_soir",
     "password": "Soir123",
     "role": "pharmacist",
     "is_active": true
   }
   ```
   
   **Pharmacien weekend**:
   ```json
   {
     "username": "pharma_weekend",
     "password": "Weekend123",
     "role": "pharmacist",
     "is_active": true
   }
   ```

**Résultat**: 2 admins + 3 pharmaciens = 5 utilisateurs

### Exemple 2: Gérer un Stagiaire

**Contexte**: Un stagiaire rejoint la pharmacie pour 3 mois

**Créer le compte**:
```json
{
  "username": "stagiaire_jean",
  "password": "Stage2025",
  "role": "pharmacist",
  "is_active": true
}
```

**Après le stage**: Désactiver le compte au lieu de le supprimer (pour garder l'historique)

### Exemple 3: Tester les Permissions

**Test 1**: Pharmacien essaie de créer un utilisateur

1. Créez un pharmacien (`pharmacien_test`)
2. Logout de l'admin
3. Login avec `pharmacien_test`
4. Essayez `POST /auth/register`
5. **Résultat**: ❌ 403 Forbidden - "Access forbidden: Admin privileges required"

✅ **C'est normal!** Seuls les admins peuvent créer des utilisateurs.

**Test 2**: Admin peut tout faire

1. Login avec `admin`
2. Testez `POST /auth/register` → ✅ Succès
3. Testez `GET /auth/me` → ✅ Succès
4. Testez `GET /metrics` → ✅ Succès

---

## 🔒 Sécurité

### Bonnes Pratiques

1. **Mots de passe forts**:
   - Minimum 8 caractères
   - Mélanger majuscules, minuscules, chiffres
   - Exemple: `Pharma2025!` au lieu de `admin123`

2. **Limiter les admins**:
   - Maximum 2-3 comptes admin
   - La plupart des employés = pharmacist

3. **Changer le mot de passe par défaut**:
   - Après installation, créez un nouvel admin
   - Désactivez le compte `admin` par défaut

4. **Tokens expirés**:
   - Les tokens expirent après **30 minutes**
   - Reconnectez-vous si vous voyez "401 Unauthorized"

5. **Désactiver au lieu de supprimer**:
   - Gardez l'historique des ventes
   - Utilisez `is_active: false` pour désactiver

### Vérifier la Sécurité

**Checklist**:
- [ ] Mot de passe admin changé
- [ ] Pas plus de 3 comptes admin
- [ ] Mots de passe forts (8+ caractères)
- [ ] Les anciens employés ont des comptes désactivés
- [ ] Les pharmaciens ne peuvent PAS créer d'utilisateurs

---

## 📝 Récapitulatif des Commandes

### Créer un Admin
```json
{
  "username": "nouvel_admin",
  "password": "MotDePasseSecure123",
  "role": "admin",
  "is_active": true
}
```

### Créer un Pharmacien
```json
{
  "username": "nouveau_pharmacien",
  "password": "MotDePasse123",
  "role": "pharmacist",
  "is_active": true
}
```

### Créer un Compte Désactivé
```json
{
  "username": "compte_desactive",
  "password": "TempPass123",
  "role": "pharmacist",
  "is_active": false
}
```

---

## 🆘 Problèmes Courants

### "401 Unauthorized"
**Problème**: Token expiré ou invalide
**Solution**: Reconnectez-vous et récupérez un nouveau token

### "403 Forbidden"
**Problème**: Pas les permissions nécessaires
**Solution**: Cette opération nécessite le rôle admin

### "400 Bad Request - Username already exists"
**Problème**: Le username existe déjà
**Solution**: Choisissez un autre username

### Token ne fonctionne pas
**Problème**: Mal copié ou mal formaté
**Solution**: 
- Vérifiez que vous avez ajouté `Bearer ` avant le token
- Exemple correct: `Bearer eyJhbGc...`
- Exemple incorrect: `eyJhbGc...` (manque "Bearer ")

---

## 📞 Support

Pour toute question sur la gestion des utilisateurs:
1. Vérifiez cette documentation
2. Testez dans Swagger UI: http://localhost:8000/docs
3. Consultez les logs du serveur si erreur

---

**Version**: Module 2 - Authentification
**Dernière mise à jour**: Décembre 2025
