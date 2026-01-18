# Plan de Migration React vers Flutter (Design Identique)

Ce document contient une série de "Prompts" (commandes) que tu peux exécuter une par une avec ton assistant IA pour recréer ton application en Flutter dans le dossier `frontend1`.

**Règle d'or pour l'IA** : "Analyse le code React existant dans `frontend/src` (CSS, JSX) pour reproduire *exactement* le même design visuel et la même logique métier dans `frontend1` avec Flutter."

---

## Étape 0 : Initialisation du Projet
**Prompt 1 :**
```text
Crée un nouveau projet Flutter nommé `frontend1` dans le répertoire `c:\Pharma_logiciels_version_01\`.
Configure le projet pour supporter Windows, Web et Android.
Ajoute les dépendances suivantes dans `pubspec.yaml` qui seront nécessaires pour égaler les fonctionnalités du React :
- `dio` (pour les requêtes HTTP, remplacement d'axios)
- `provider` ou `flutter_riverpod` (pour la gestion d'état)
- `google_fonts` (pour la typographie)
- `fl_chart` (pour les graphiques dashboard)
- `intl` (pour le formatage dates/monnaies)
- `shared_preferences` (pour le stockage local simple)
- `flutter_secure_storage` (pour stocker le token JWT)
- `data_table_2` (pour les tableaux avancés comme en React)
Ne supprime SURTOUT PAS le dossier `frontend` existant.
```

## Étape 1 : Design System & Thème
**Prompt 2 :**
```text
Analyse le fichier `frontend/src/index.css` et la configuration Tailwind (si présente) ou les styles globaux.
Crée un fichier `lib/core/theme.dart` dans `frontend1`.
Définis un `ThemeData` Flutter qui correspond exactement à la palette de couleurs (primaire, secondaire, background, surface, error) et à la typographie de l'application React actuelle.
Assure-toi que les boutons, les inputs et les cartes (Cards) ont par défaut le même style (arrondi des bordures, ombres, padding) que dans le frontend React.
```

## Étape 2 : Couche Réseau & Authentification (Auth)
**Prompt 3 :**
```text
Analyse `frontend/src/services/api.js` (ou équivalent) et `frontend/src/pages/Auth/LoginPage.jsx`.
1. Crée un service HTTP avec `Dio` dans `frontend1/lib/services/api_service.dart` qui pointe vers le même backend FastAPI (http://127.0.0.1:8000). Gère les intercepteurs pour injecter le Token JWT.
2. Crée le modèle `User` dans `lib/models/user.dart`.
3. Crée un `AuthProvider` pour gérer l'état de connexion.
4. Crée l'écran de connexion `lib/screens/auth/login_screen.dart`. Il doit être VISUELLEMENT IDENTIQUE à la page React (même image ou couleur de fond, même style de formulaire au centre).

Mais Analyse le code React existant dans `frontend/src` (CSS, JSX) pour reproduire *exactement* le même design visuel et la même logique métier dans `frontend1` avec Flutter
```

## Étape 3 : Layout Principal (Sidebar & Header)
**Prompt 4 :**
```text
Analyse `frontend/src/components/layout/Sidebar.jsx`, `Header.jsx` et `MainLayout.jsx`.
Crée le "Scaffold" principal de l'application Flutter dans `lib/screens/layout/main_layout.dart`.
1. Reproduis la Sidebar latérale (ou un Drawer responsive) avec les mêmes icônes et couleurs.
2. Reproduis le Header en haut (Barre de recherche, Infos utilisateur, Bouton déconnexion, Toggle Thème).
3. Assure la navigation entre les pages sans recharger toute l'application.

Mais Analyse le code React existant dans `frontend/src` (CSS, JSX) pour reproduire *exactement* le même design visuel et la même logique métier dans `frontend1` avec Flutter
```

## Étape 4 : Dashboard
**Prompt 5 :**
```text
Analyse `frontend/src/pages/Dashboard/Dashboard.jsx` et les composants associés.
Crée l'écran `lib/screens/dashboard/dashboard_screen.dart`.
1. Reproduis les "StatsCards" (Total Ventes, Ruptures de stock, etc.) avec le même design (icône, chiffre, couleur de fond).
2. Utilise `fl_chart` pour reproduire les graphiques de ventes (Courbes/Barres) exactement comme ils apparaissent en React.
3. Connecte les données via un `DashboardService` qui appelle les mêmes endpoints API que le code React.

Mais Analyse le code React existant dans `frontend/src` (CSS, JSX) pour reproduire *exactement* le même design visuel et la même logique métier dans `frontend1` avec Flutter
```

## Étape 5 : Gestion du Stock (Tableaux & Modales)
**Prompt 6 :**
```text
Analyse `frontend/src/pages/Stock/StockPage.jsx` et les modales d'ajout/modif.
Crée l'écran `lib/screens/stock/stock_screen.dart`.
1. Utilise `data_table_2` pour créer un tableau de stock avec pagination, tri et recherche, identique visuellement au tableau React.
2. Crée les formulaires d'ajout/modification de médicament (les dialogues) en respectant les champs (Nom, DCI, Forme, Prix, etc.) et le layout des formulaires React.

Mais Analyse le code React existant dans `frontend/src` (CSS, JSX) pour reproduire *exactement* le même design visuel et la même logique métier dans `frontend1` avec Flutter
```

## Étape 6 : Point de Vente (POS) - *Complexe*
**Prompt 7 :**
```text
Analyse `frontend/src/pages/POS/POSPage.jsx`. C'est le module le plus interactif.
Crée l'écran `lib/screens/pos/pos_screen.dart`.
1. Divise l'écran en deux : Liste des produits (à gauche ou haut) et Panier (à droite ou bas), comme dans le design actuel.
2. Implémente la recherche rapide de produits.
3. Gère le panier en local (ajout, quantité, suppression, calcul total).
4. Crée la modale de Paiement (Espèce, Carte, Rendu monnaie) identique à celle de React.
5. Une fois la vente validée, appelle l'API backend et vide le panier.

Mais Analyse le code React existant dans `frontend/src` (CSS, JSX) pour reproduire *exactement* le même design visuel et la même logique métier dans `frontend1` avec Flutter
        ```

## Étape 7 : Historique & Rapports
**Prompt 8 :**
```text
Analyse `frontend/src/pages/SalesHistory` et `frontend/src/pages/Reports`.
Implémente les écrans correspondants dans Flutter.
1. Tableau d'historique des ventes avec filtres par date.
2. Écran de rapports avec génération de PDF (utilise le package `pdf` et `printing` de Flutter si la génération PDF se fait côté client, sinon télécharge juste le PDF du backend).     

Mais Analyse le code React existant dans `frontend/src` (CSS, JSX) pour reproduire *exactement* le même design visuel et la même logique métier dans `frontend1` avec Flutter
```

## Étape 8 : Paramètres & Utilisateurs
**Prompt 9 :**
```text
Analyse `frontend/src/pages/Settings` et `Users`.
Crée les écrans de configuration.
1. Gestion des utilisateurs (Tableau CRUD).
2. Paramètres de la pharmacie (Nom, Adresse, etc.).

Mais Analyse le code React existant dans `frontend/src` (CSS, JSX) pour reproduire *exactement* le même design visuel et la même logique métier dans `frontend1` avec Flutter
```

## Étape 9 : Finalisation & Build
**Prompt 10 :**
```text
Vérifie toute l'application `frontend1`.
Teste la compilation en mode :
- Windows Desktop : `flutter run -d windows`
- Web : `flutter run -d chrome`
Corrige les éventuels bugs d'interface (overflows, tailles de polices).
Optimise les performances.

Mais Analyse le code React existant dans `frontend/src` (CSS, JSX) pour reproduire *exactement* le même design visuel et la même logique métier dans `frontend1` avec Flutter
```
