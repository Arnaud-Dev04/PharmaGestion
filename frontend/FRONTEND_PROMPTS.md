# PROMPTS POUR LE FRONTEND (React + Vite)

Ce fichier contient une série de prompts optimisés pour générer le frontend de l'application de gestion de pharmacie "Pharmacy Management System".
Copiez ces prompts un par un dans votre chat avec une IA pour construire le projet étape par étape.

**NOTE IMPORTANTE**: Pour chaque prompt, fournissez à l'IA la photo/capture d'écran de design que vous souhaitez utiliser comme référence visuelle. Mentionnez : *"Utilise le style visuel de cette image (couleurs, layout, typographie) pour l'interface."*

---

## PARTIE 1 : Initialisation & Authentification

**Prompt à copier :**

```text
Agis en tant qu'Expert Frontend React.
Nous allons créer le frontend pour une application de gestion de pharmacie moderne.
Le backend (FastAPI) tourne sur http://localhost:8000.

**Stack Technique :**
- React 18 + Vite
- TailwindCSS (Styling)
- Axios (Requêtes HTTP)
- React Router DOM (Navigation)
- React Query (Gestion d'état serveur)
- Lucide React (Icônes)

**Tâche 1 : Setup & Login**
1. Initialise un projet Vite nommé `pharmacy-frontend`.
2. Installe les dépendances citées.
3. Configure une instance Axios (`api.js`) avec :
   - Base URL : `http://localhost:8000`
   - Intercepteur : Ajoute automatiquement le token JWT du `localStorage` dans le header `Authorization`.
4. Crée une page de Login (`/login`) :
   - Champs : Username, Password.
   - Action : POST `/auth/login`.
   - Succès : Stocke le token et redirige vers `/dashboard`.
   - Design : Inspire-toi de l'image fournie (Moderne, Clean, Centré).

Génère le code pour `api.js`, `App.jsx`, et `LoginPage.jsx`.
```

---

## PARTIE 2 : Gestion de Stock & Fournisseurs

**Prompt à copier :**

```text
Nous continuons le frontend. Le Login fonctionne.
Passons au module "Inventaire".

**Tâche 2 : Stock & Fournisseurs**
Crée un layout Dashboard avec une Sidebar (Navigation) et un Header (User info).

1. **Page Stock (`/stock`)** :
   - Tableau listant les médicaments (GET `/stock`).
   - Colonnes: Nom, Code, Famille, Prix, Quantité, Actions.
   - Badge "Low Stock" si quantité < seuil.
   - Bouton "Ajouter" -> Ouvre une Modale (POST `/stock`).
   - Recherche en temps réel.

2. **Page Fournisseurs (`/suppliers`)** :
   - Liste des fournisseurs (GET `/suppliers`).
   - CRUD complet (Ajouter, Modifier, Supprimer).

Utilise des composants réutilisables pour le Tableau et la Modale.
Assure-toi que le design correspond à la charte graphique définie.
```

---

## PARTIE 3 : Point de Vente (POS) - Le Cœur du Système

**Prompt à copier :**

```text
Passons à la fonctionnalité critique : Le Point de Vente (POS).
C'est l'interface utilisée par les vendeurs au comptoir.

**Tâche 3 : Interface POS (`/pos`)**
Cette page doit être divisée en deux colonnes :

1. **Gauche : Catalogue Produits**
   - Barre de recherche (Scan code-barre ou nom).
   - Grille des médicaments disponibles.
   - Au clic sur un produit -> Ajoute au panier.

2. **Droite : Panier et Paiement**
   - Liste des articles sélectionnés (Nom, Qté, Prix, Total ligne).
   - Possibilité de modifier la quantité (+/-).
   - **Total Général** en bas (Devise configurée en backend).
   - Bouton "Valider la Vente" :
     - Ouvre une modale Paiement (Espèces, Mobile Money, Carte).
     - Envoie POST `/sales/` au backend.
     - Affiche la facture (PDF simple ou HTML) après succès.

N'oublie pas de gérer les erreurs (ex: Stock insuffisant retourné par le backend).
```

---

## PARTIE 4 : Dashboard & Rapports

**Prompt à copier :**

```text
Nous avons besoin de visualiser les performances.

**Tâche 4 : Dashboard & Stats**
1. **Page Accueil (`/dashboard`)** :
   - Cartes "KPI" en haut : Ventes du jour, Alertes Stock, Chiffre d'Affaire.
   - Graphique des ventes (utilise `recharts` ou `chart.js`) avec les données de `GET /dashboard/stats`.

2. **Page Rapports (`/reports`)** :
   - Section pour télécharger les fichiers générés par le backend.
   - "Télécharger Stock (Excel)" -> `GET /reports/stock/excel`.
   - "Télécharger Ventes (Excel)" -> `GET /reports/sales/excel`.
   - "Bilan Financier (PDF)" -> `GET /reports/financial/pdf`.
```

---

## PARTIE 5 : Configuration & Sync Offline

**Prompt à copier :**

```text
Dernière étape : Configuration et Robustesse.

**Tâche 5 : Paramètres & Sync**
1. **Page Paramètres (`/settings`)** :
   - Formulaire pour modifier : Nom Pharmacie, Taux Bonus, Devise.
   - GET/PUT sur `/settings`.

2. **Indicateur Offline** :
   - Dans le Header, ajoute une icône (Wifi/Cloud).
   - Si `navigator.onLine` est faux, affiche "Mode Hors Ligne".
   - (Bonus) : Utilise Service Worker (Vite PWA) pour mettre en cache l'app.
   
3. **Synchronisation** :
   - Le backend gère la queue, mais le frontend doit signaler si la connexion au serveur est perdue (Erreurs 503/Timeout).
   - Affiche un "Toast" (Notification) quand la connexion revient.
```
