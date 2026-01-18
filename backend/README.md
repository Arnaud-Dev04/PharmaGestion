# 🏥 Pharmacy Management System - Backend

Backend complet en Python/FastAPI pour un système de gestion de pharmacie avec support online/offline et synchronisation automatique.

## 📋 Prérequis

- Python 3.10.11
- MySQL (XAMPP recommandé pour Windows)
- pip (gestionnaire de paquets Python)

## 🚀 Installation

### 1. Cloner le projet

```bash
git clone <repository-url>
cd backend
```

### 2. Créer un environnement virtuel

```bash
python -m venv venv
```

### 3. Activer l'environnement virtuel

**Windows:**

```bash
venv\Scripts\activate
```

**Linux/Mac:**

```bash
source venv/bin/activate
```

### 4. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 5. Configuration

1. Copier le fichier `.env.example` vers `.env`:

   ```bash
   copy .env.example .env  # Windows
   cp .env.example .env    # Linux/Mac
   ```

2. Modifier `.env` avec vos configurations:

   - `DB_URL_LOCAL`: Chemin vers votre base SQLite (par défaut: `sqlite:///./pharmacy_local.db`)
   - `DB_URL_REMOTE`: URL de connexion MySQL (format: `mysql+pymysql://user:password@host:port/database`)
   - `SECRET_KEY`: Générer une clé secrète sécurisée pour JWT
   - Autres paramètres selon vos besoins

3. **Générer une clé secrète sécurisée:**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

### 6. Initialiser la base de données

```bash
# Créer les tables dans SQLite (local)
python -c "from app.database.core import init_local_db; init_local_db()"

# Pour MySQL (optionnel, nécessite XAMPP en cours d'exécution)
# Créer d'abord la base de données 'pharmacy_db' dans phpMyAdmin
# python -c "from app.database.core import init_remote_db; init_remote_db()"
```

### 7. Lancer l'application

```bash
uvicorn main:app --reload
```

L'API sera accessible sur: `http://localhost:8000`

## 📚 Documentation API

Une fois l'application lancée, accédez à:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🏗️ Structure du Projet

```
backend/
├── app/
│   ├── models/          # Modèles SQLAlchemy
│   ├── routes/          # Endpoints API
│   ├── services/        # Logique métier
│   ├── database/        # Configuration DB
│   ├── auth/            # Authentification JWT
│   ├── sync/            # Logique de synchronisation
│   └── utils/           # Utilitaires
├── alembic/             # Migrations de DB
├── main.py              # Point d'entrée FastAPI
├── requirements.txt     # Dépendances Python
└── .env                 # Configuration (à créer)
```

## 🔧 Fonctionnalités Principales

### Module 1 (Actuel) ✅

- ✅ Structure du projet
- ✅ Configuration dual-database (SQLite + MySQL)
- ✅ Modèles de données complets
- ✅ Timestamps pour gestion des conflits

### Modules à venir

- 🔜 Module 2: Authentification JWT
- 🔜 Module 3: Gestion Stock & Fournisseurs
- 🔜 Module 4: Point de Vente (POS)
- 🔜 Module 5: Dashboard & Historique
- 🔜 Module 6: Réapprovisionnement
- 🔜 Module 7: Rapports (PDF/Excel)
- 🔜 Module 8: Paramètres & I18n
- 🔜 Module 9: Synchronisation Offline/Online
- 🔜 Module 10: Tests & Documentation

## 🗄️ Base de Données

### SQLite (Local - Mode Offline)

- Stockage automatique en local
- Fichier: `pharmacy_local.db`
- Utilisé par défaut pour toutes les opérations

### MySQL (Distant - Mode Online)

- Synchronisation avec serveur
- Configuration dans XAMPP
- Résolution de conflits par timestamp

## 🔐 Sécurité

- Authentification JWT
- Hashage des mots de passe (bcrypt)
- Rôles utilisateurs (Admin, Pharmacien)
- Tokens d'accès expirables

## 💰 Devise

Le système utilise le **Franc Burundais (FBu)** comme devise par défaut.

## 🌍 Langues

Support multilingue:

- Français (FR)
- Anglais (EN)

## 🛠️ Commandes Utiles

### Migrations Alembic

```bash
# Créer une migration
alembic revision --autogenerate -m "description"

# Appliquer les migrations
alembic upgrade head

# Revenir en arrière
alembic downgrade -1
```

### Tests (Module 10)

```bash
pytest
pytest --cov=app
```

## 📝 Licence

[Spécifier la licence]

## 👥 Contributeurs

[Liste des contributeurs]

## 📞 Support

Pour toute question ou problème, contactez [email/contact].
