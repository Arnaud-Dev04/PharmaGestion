PROJET : Backend Gestion Pharmacie (Sync Online/Offline)
Ce fichier sert de référence unique pour le développement du projet. Il contient le contexte global et les instructions détaillées pour chaque module.

🌍 CONTEXTE GLOBAL

1. Objectif
   Développer un backend complet en Python pour un logiciel de pharmacie moderne, capable de fonctionner en ligne et hors ligne avec synchronisation automatique. Le frontend sera en React-Vite (hors scope actuel, mais à garder en tête).

2. Stack Technique
   Langage : Python 3.10.11
   Framework : FastAPI (recommandé pour la vitesse et l'async)
   ORM : SQLAlchemy
   Base de Données :
   Locale : SQLite (pour fonctionnement hors ligne)
   Distante : MySQL (compatible XAMPP)
   Sécurité : JWT (JSON Web Tokens)
3. Exigences Clés
   Mode Hors-ligne :
   Si Internet coupé : stockage des opérations (CRUD) dans un fichier JSON local.
   Si Internet revient : synchronisation automatique vers MySQL.
   Résolution conflits : priorité à la dernière modification (timestamp).
   Utilisateurs : Admin, Pharmacien.
   Langues : Backend doit fournir messages en FR et EN.
   Devise : Franc Burundais (FBu).
   Structure Dossiers :
   /app
   /models
   /routes
   /services
   /sync
   /database
   /auth
   /utils
   📅 PLAN DE DÉVELOPPEMENT (MODULES)
   🟢 MODULE 1 : Structure de base + Database + Models
   Prompt à exécuter :

Agis comme un expert Python/FastAPI. Nous commençons le "Module 1" du projet de pharmacie.
Tâche : Mettre en place la structure du projet et la couche de données.

1.  **Structure** : Crée l'arborescence de dossiers suivante : `/app` avec les sous-dossiers `models`, `routes`, `services`, `sync`, `database`, `auth`, `utils`.
2.  **Configuration** :
    - Crée un `requirements.txt` complet (fastapi, uvicorn, sqlalchemy, pymysql, python-jose, passlib, python-multipart, reportlab, openpyxl, alembic).
    - Crée un `.env.example` (DB_URL_LOCAL, DB_URL_REMOTE, SECRET_KEY, ALGORITHM).
    - Crée un `README.md` avec instructions d'installation.
3.  **Database** :
    - Configure SQLAlchemy dans `/app/database/core.py` pour gérer DEUX connexions : une `SessionLocal` (SQLite) et une `SessionRemote` (MySQL).
    - Le système doit pouvoir switcher ou écrire intelligemment (mais la logique de sync viendra au Module 9, pour l'instant prépare juste les connexions).
4.  **Models (SQLAlchemy)** dans `/app/models/` :
    _ `User` : id, username, password_hash, role (admin/pharmacist), is_active.
    _ `Medicine` : id, code, name, family_id, type_id, quantity, price_buy, price_sell, expiry_date, min_stock_alert.
    _ `MedicineFamily` : id, name (Dynamique).
    _ `MedicineType` : id, name (Plaquette, Flacon, etc. - Dynamique).
    _ `Supplier` : id, name, phone, email, contact_name.
    _ `Customer` : id, first_name, last_name, phone, total_points (bonus).
    _ `Sale` : id, code, total_amount, payment_method, date, user_id, customer_id, sync_status (synced/pending).
    _ `SaleItem` : id, sale_id, medicine_id, quantity, unit_price, total_price.
    _ `RestockOrder` : id, supplier_id, status, date, total_amount.
    _ `RestockItem` : id, order_id, medicine_id, quantity, price_buy.
    _ `Settings` : id, key, value (pour stocker nom pharmacie, logo, % bonus, etc.).
    _ `SyncLog` : id, timestamp, status, message (pour debugger la sync). \* Ajoute `created_at` et `updated_at` sur TOUS les modèles pour la gestion des conflits.
    Livrable : Tous les fichiers nécessaires créés et structurés. Le code doit être exécutable (hors DB MySQL qui n'est pas encore connectée, mais le code doit être prêt).
    🟢 MODULE 2 : Authentification (JWT + Roles)
    Prompt à exécuter :

Nous passons au "Module 2" : Authentification. Assure-toi d'avoir le contexte du Module 1.
Tâche : Sécuriser l'API avec JWT.

1.  **Utils** : Dans `/app/utils/security.py`, implémente le hashage de mot de passe (bcrypt) et la création/vérification de token JWT.
2.  **Middleware** : Crée `/app/auth/dependencies.py` pour :
    - Extraire le token du header `Authorization`.
    - Vérifier le token et récupérer le `current_user`.
    - Créer une dépendance `get_admin_user` qui rejette si le rôle n'est pas 'admin'.
3.  **Routes** : Crée `/app/routes/auth.py` :
    - `POST /auth/login` : Retourne le token JWT.
    - `POST /auth/register` : (Admin seulement) Créer un nouvel employé.
4.  **Main** : Mets à jour `main.py` pour inclure ces routes.
    Livrable : Système d'auth fonctionnel. Je dois pouvoir récupérer un token et l'utiliser pour accéder à une route protégée (crée une route test `/metrics` protégée pour vérifier).
    🟢 MODULE 3 : Gestion Stock + Fournisseurs
    Prompt à exécuter :

Module 3 : Gestion du Stock et des Fournisseurs.
Tâche : Implémenter le CRUD complet pour les médicaments et fournisseurs.

1.  **Schemas (Pydantic)** : Crée les schemas pour validation dans `/app/schemas/`.
2.  **Routes Stock** (`/app/routes/stock.py`) :
    - CRUD : Create, Read (avec pagination et recherche par nom/code), Update, Delete.
    - Filtres : Par Famille, Par Type.
    - Alertes : Route spécifique `/stock/alerts` retournant les produits périmés ou stock faible.
3.  **Routes Configuration Stock** :
    - CRUD pour `MedicineFamily` et `MedicineType` (car demandé dynamique).
4.  **Routes Fournisseurs** (`/app/routes/suppliers.py`) : \* CRUD complet.
    Implémente la logique métier dans `/app/services/` pour garder les routes propres.
    🟢 MODULE 4 : Point de Vente (POS) + Clients + Bonus
    Prompt à exécuter :

Module 4 : Cœur du système - Le Point de Vente (POS).
Tâche : Gérer les ventes, les clients et les bonus.

1.  **Logique Client & Bonus** :
    - Inscription client automatique si nouveau numéro de téléphone lors d'une vente.
    - Calcul Bonus : X% du montant de la vente ajouté au `total_points` du client (configurable plus tard, mets 5% par défaut).
2.  **Service Vente** (`/app/services/sales_service.py`) :
    - Création d'une vente :
      - Vérifier stock disponible.
      - Décrémenter stock.
      - Calculer total.
      - Appliquer bonus si client existant.
      - Créer `Sale` et `SaleItems`.
      - Générer un ID facture auto-incrémenté lisible (ex: INV-2023-0001).
3.  **Facture** :
    - Route `/sales/invoice/{id}` : Génère un PDF simple avec ReportLab contenant les détails de la vente.
4.  **Routes** (`/app/routes/sales.py`) :
    _ `POST /sales/create`
    _ `GET /sales/invoice/{id}`
    Note : Pour l'instant on écrit tout en DB locale (SQLite) par défaut.
    🟢 MODULE 5 : Historique ventes + Dashboard
    Prompt à exécuter :

Module 5 : Dashboard et Historique.
Tâche : Fournir les données pour le tableau de bord et l'historique.

1.  **Dashboard** (`/dashboard/stats`) :
    - Total médicaments en stock.
    - Ventes de la semaine (montant).
    - Médicaments bientôt expirés (count).
    - Stock faible (count).
    - Revenus par semaine (graphique data).
2.  **Historique** (`/sales/history`) :
    _ Liste des ventes avec filtres par date, vendeur.
    _ Détail d'une vente spécifique.
    Optimise les requêtes SQL (utilise `func.count`, `func.sum`).
    🟢 MODULE 6 : Réapprovisionnement
    Prompt à exécuter :

Module 6 : Réapprovisionnement.
Tâche : Gérer les commandes fournisseurs.

1.  **Service** :
    - Créer une commande de réapprovisionnement (`RestockOrder`).
    - Lors de la réception de la commande -> Mettre à jour le stock principal (+ quantité).
2.  **Routes** (`/app/routes/restock.py`) :
    _ `POST /restock/create` (Brouillon).
    _ `POST /restock/{id}/confirm` (Valide et incrémente le stock). \* `GET /restock/low-stock` : Liste les articles sous le seuil minimum pour faciliter la commande.
    🟢 MODULE 7 : Rapports (PDF + Excel)
    Prompt à exécuter :

Module 7 : Reporting avancé.
Tâche : Exporter les données.

1.  **Service Reporting** :
    - Utilise `openpyxl` pour générer des Excels (Stock, Ventes).
    - Utilise `reportlab` pour des rapports PDF formels (Bilan journée, Bilan mois).
2.  **Routes** (`/app/routes/reports.py`) :
    _ `GET /reports/stock/excel`
    _ `GET /reports/sales/excel?start_date=...&end_date=...` \* `GET /reports/financial/pdf?period=month` (Chiffre d'affaire, Bénéfice, Top produits).
    🟢 MODULE 8 : Paramètres + Multilingue
    Prompt à exécuter :

Module 8 : Configuration et I18n.
Tâche : Rendre le système configurable.

1.  **Fichiers Langues** :
    - Crée `/app/i18n/messages_fr.json` et `messages_en.json` (clés : `error_stock_insufficient`, `success_sale_created`, etc.).
    - Helper pour récupérer le message selon la locale demandée.
2.  **Paramètres Dynamiques** :
    _ Route `/settings` pour lire/écrire dans la table `Settings`.
    _ Champs : Nom pharmacie, Taux Bonus, Devise (FBu par défaut), Logo (URL ou base64), Liste médicaments éligibles bonus (JSON).
    🟢 MODULE 9 : Système de synchronisation hors-ligne
    Prompt à exécuter :

Module 9 : Le défi technique - Sync Offline/Online.
Tâche : Implémenter la logique de synchronisation bidirectionnelle.

1.  **Detection** :
    - Utilitaire pour vérifier la connexion MySQL (`is_online()`).
2.  **Stockage Offline** :
    - Si `is_online()` est False lors d'une écriture (Vente, Stock) -> Écrire dans SQLite ET ajouter une entrée dans un fichier `offline_queue.json` (ou table dédiée SQLite `SyncQueue`) avec l'action et les données.
3.  **Processus de Sync** (`/app/sync/sync_manager.py`) :
    _ Tâche de fond (Background Task FastAPI ou script séparé) qui tourne périodiquement.
    _ Si Internet revient : 1. Lire `offline_queue`. 2. Envoyer les données vers MySQL. 3. En cas de conflit (ID existant) : Comparer `updated_at`. Si timestamp local > distant, écraser. Sinon, ignorer. 4. Vider la queue. \* Sync Descendante (MySQL -> Local) : Mettre à jour le stock local si modifications distantes (ex: admin a changé un prix depuis le bureau).
    🟢 MODULE 10 : Tests + Documentation
    Prompt à exécuter :

Module 10 : Finalisation.
Tâche : Assurer la qualité.

1.  **Tests** :
    - Installe `pytest` et `httpx`.
    - Crée des tests unitaires simples pour Auth et Calc Vente.
2.  **Documentation** :
    - Vérifie que le Swagger (/docs) est propre avec des descriptions.
    - Complète le README avec la procédure de lancement du mode Sync.
