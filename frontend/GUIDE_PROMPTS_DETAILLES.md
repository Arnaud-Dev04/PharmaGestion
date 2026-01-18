# 🎯 Guide de Prompts Détaillés - Frontend Pharmacy Management

> **Design de Référence** : Style "Pharmac+" avec sidebar bleu foncé, cards blanches, accents verts/bleus.
> 
> **Instructions** : Copiez chaque prompt dans votre conversation avec l'IA, en respectant l'ordre.

---

## 🎨 PALETTE DE COULEURS EXACTE (Basée sur le design)

```css
/* Couleurs principales extraites du design Pharmac+ */
:root {
  /* Sidebar - Bleu nuit */
  --sidebar-bg: #1a1f37;
  --sidebar-hover: #252b48;
  --sidebar-active: #2d9cdb;
  
  /* Background principal */
  --bg-main: #f3f4f6;
  --bg-card: #ffffff;
  
  /* Textes */
  --text-primary: #1f2937;
  --text-secondary: #6b7280;
  --text-muted: #9ca3af;
  
  /* Accents */
  --accent-primary: #2d9cdb;    /* Bleu icônes */
  --accent-success: #10b981;    /* Vert montants */
  --accent-warning: #f59e0b;
  --accent-danger: #ef4444;
  
  /* Bordures */
  --border-color: #e5e7eb;
}

.dark {
  --bg-main: #0f1225;
  --bg-card: #1a1f37;
  --text-primary: #f9fafb;
  --text-secondary: #d1d5db;
  --border-color: #374151;
}
```

---

## 📦 PROMPT 1 : Initialisation avec Style Pharmac+

```
Agis en tant qu'Expert Frontend React.

CONTEXTE :
Je développe le frontend d'un système de gestion de pharmacie appelé "Pharmac+".
Le backend FastAPI tourne sur http://localhost:8000.

DESIGN À REPRODUIRE :
- Sidebar bleu foncé (#1a1f37) fixe à gauche
- Fond principal gris clair (#f3f4f6)
- Cards blanches avec border-radius 12px et shadow subtile
- Accents bleus (#2d9cdb) et verts (#10b981)
- Typographie moderne (Inter ou Poppins)
- Support Dark Mode

STACK TECHNIQUE :
- React 18 + Vite
- TailwindCSS (customisé avec les couleurs ci-dessus)
- React Router DOM v6
- Axios
- React Query
- Zustand
- Lucide React

TÂCHE 1 : SETUP INITIAL

1. Initialise le projet Vite :
   npx create-vite@latest . --template react

2. Installe les dépendances :
   npm install react-router-dom axios @tanstack/react-query zustand lucide-react
   npm install react-hook-form zod @hookform/resolvers
   npm install date-fns recharts
   npm install -D tailwindcss postcss autoprefixer
   npx tailwindcss init -p

3. Configure tailwind.config.js :
   - darkMode: 'class'
   - Étends les couleurs avec la palette Pharmac+ ci-dessus
   - Ajoute la police Inter depuis Google Fonts

4. Structure des dossiers :
   src/
   ├── components/
   │   ├── ui/           # Button, Input, Card, Badge, Modal
   │   ├── layout/       # Sidebar, Header, MainLayout
   │   └── common/       # Table, LoadingSpinner
   ├── pages/
   ├── services/
   ├── hooks/
   ├── context/
   └── utils/

5. ThemeContext (context/ThemeContext.jsx) :
   - Gère light/dark mode
   - Toggle avec icône Sun/Moon
   - Persiste dans localStorage

6. Instance Axios (services/api.js) :
   - Base URL : http://localhost:8000
   - Intercepteur : Ajoute "Authorization: Bearer {token}" automatiquement
   - Gère les erreurs 401

7. Composants UI de base :
   - Button (variants: primary, secondary, danger, ghost)
   - Input (avec label, helper text, error state)
   - Card (avec header, body, footer optionnels)
   - Badge (variants: success, warning, danger, info)

STYLE CSS GLOBAL (index.css) :
- Import Tailwind directives
- Police Inter
- Variables CSS pour les couleurs
- Smooth scrolling
- Focus rings personnalisés

LIVRABLE : Setup complet + ThemeContext + api.js + composants UI de base
```

---

## 🔐 PROMPT 2 : Authentification Style Pharmac+

```
CONTEXTE :
Projet initialisé. Créons l'authentification.

BACKEND API :
- POST /auth/login → { username, password } → { access_token, token_type, user }
- GET /auth/me → Infos utilisateur { id, username, role, full_name }

TÂCHE 2 : AUTHENTIFICATION

1. AuthContext (context/AuthContext.jsx) :
   - State: { user, token, isAuthenticated, isLoading }
   - Actions: login(), logout(), refreshUser()
   - Stockage token dans localStorage

2. authService.js :
   - login(credentials)
   - getCurrentUser()
   - logout()

3. LoginPage (pages/Auth/LoginPage.jsx) :
   
   DESIGN PRÉCIS :
   - Layout split: 
     • Gauche (50%): Panel bleu foncé (#1a1f37) avec logo "Pharmac+" centré, texte de bienvenue
     • Droite (50%): Formulaire de login sur fond blanc
   - Formulaire :
     • Titre "Connexion" (gros, bold)
     • Sous-titre "Entrez vos identifiants"
     • Input Username avec icône User
     • Input Password avec icône Lock et toggle visibility
     • Checkbox "Se souvenir de moi"
     • Bouton "Se connecter" (bleu #2d9cdb, full width)
     • Lien "Mot de passe oublié ?" (optionnel)
   - Validation avec react-hook-form + zod
   - Messages d'erreur en français
   - Animation fade-in au load

4. ProtectedRoute (components/common/ProtectedRoute.jsx) :
   - Vérifie isAuthenticated
   - Redirige vers /login si non connecté
   - Loading state pendant vérification

5. App.jsx avec Router :
   Routes publiques: /login
   Routes privées (avec ProtectedRoute): /dashboard, /stock, /suppliers, /pos, /reports, /settings, /history

LIVRABLE : AuthContext, LoginPage (split design), ProtectedRoute, Router
```

---

## 📊 PROMPT 3 : Layout Pharmac+ (Sidebar + Header + Dashboard)

```
CONTEXTE :
Authentification OK. Créons le layout principal exactement comme le design.

BACKEND API :
- GET /dashboard/stats
- GET /dashboard/recent-sales
- GET /dashboard/low-stock

TÂCHE 3 : LAYOUT & DASHBOARD

1. Sidebar (components/layout/Sidebar.jsx) - DESIGN EXACT :
   
   STYLE :
   - Largeur fixe 260px
   - Fond: #1a1f37 (bleu nuit)
   - Position fixe à gauche
   - Hauteur 100vh
   
   CONTENU :
   - En haut: Logo "Pharmac+" avec icône colorée + "Mode Admin" en dessous
   - Menu navigation avec icônes Lucide :
     • 📊 Tableau de bord (/dashboard)
     • 📦 Gestion des stocks (/stock)  
     • 🛒 Point de vente (/pos)
     • 📜 Historique des ventes (/history)
     • 🔄 Réapprovisionnement (/restock)
     • 🏢 Fournisseurs (/suppliers)
     • 📈 Rapports (/reports)
     • ⚙️ Paramètres (/settings)
     • 💊 Prescriptions (/prescriptions) - optionnel
   - Item actif: fond légèrement plus clair + bordure gauche bleue (#2d9cdb)
   - Hover: fond hover subtil
   - En bas: Bouton "Déconnexion" avec icône

2. Header (components/layout/Header.jsx) - DESIGN EXACT :
   
   STYLE :
   - Hauteur 64px
   - Fond transparent (pas de bg)
   - Flex between
   
   CONTENU GAUCHE :
   - Date en français format "mardi 9 septembre 2025"
   - Sous-titre "Mode Administrateur" (selon le rôle)
   
   CONTENU DROITE :
   - Icône notification (Bell)
   - Toggle thème (Sun/Moon icon)
   - Globe icon + "Français" dropdown
   - Avatar utilisateur (optionnel)

3. MainLayout (components/layout/MainLayout.jsx) :
   - Structure: Sidebar fixe + (Header + Content scrollable)
   - Padding content: 24px
   - Background: #f3f4f6 (gris clair)

4. DashboardPage (pages/Dashboard/DashboardPage.jsx) :
   
   SECTION 1 - Page Titre :
   - "Consultez l'historique de toutes vos ventes"
   
   SECTION 2 - KPI Cards (2 colonnes) :
   - Card "Total des ventes" :
     • Nombre (gros, bold)
     • Icône ronde bleue (#2d9cdb) à droite
   - Card "Chiffre d'affaires total" :
     • Montant en F + devise (ex: "F10400.00")
     • Couleur verte (#10b981)
     • Icône dollar verte à droite
   
   SECTION 3 - Recherche :
   - Input "Rechercher par ID de vente ou médicament..."
   - Date picker à droite (format jj/mm/aaaa)
   
   SECTION 4 - Tableau :
   - Headers: ID DE VENTE, DATE, ARTICLES, TOTAL, ACTIONS
   - ID en format "#29b65b87" (bleu)
   - Date avec heure en dessous (gris)
   - Articles: "1 article(s)" + "2 unités" en dessous
   - Total en couleur (vert pour positif, rouge si remboursé)
   - Actions: Icônes (voir, télécharger, imprimer)

5. dashboardService.js :
   - getStats()
   - getRecentSales()
   - getLowStock()

LIVRABLE : Sidebar, Header, MainLayout, DashboardPage (design identique à l'image)
```

---

## 💊 PROMPT 4 : Gestion de Stock

```
CONTEXTE :
Layout terminé. Module Stock.

BACKEND API :
- GET /stock
- POST /stock
- PUT /stock/{id}
- DELETE /stock/{id}
- GET /stock/search?q={query}

TÂCHE 4 : MODULE STOCK

1. StockListPage (pages/Stock/StockListPage.jsx) :
   
   HEADER :
   - Titre "Gestion des stocks"
   - Sous-titre "Gérez votre inventaire de médicaments"
   - Bouton "+ Ajouter un médicament" (bleu #2d9cdb)
   
   FILTRES :
   - Input recherche avec icône Search
   - Select famille (Antibiotiques, Antalgiques, etc.)
   - Filtre stock (Tous, En stock, Rupture)
   
   TABLEAU (style Pharmac+) :
   - Colonnes: Code, Nom, Famille, Prix (F), Quantité, Expiration, Actions
   - Badge "Rupture" (rouge) si quantity < threshold
   - Badge "Faible" (orange) si quantity <= threshold * 1.5
   - Badge "OK" (vert) sinon
   - Date expiration: Rouge si expirée, Orange si < 30 jours
   - Actions: Edit (icône), Delete (icône)
   
   PAGINATION :
   - Boutons Précédent/Suivant
   - "Affichage 1-10 sur 50"

2. StockFormModal (components/common/StockFormModal.jsx) :
   - Modal avec backdrop blur
   - Titre: "Ajouter un médicament" ou "Modifier le médicament"
   - Formulaire en 2 colonnes :
     • Nom (required)
     • Code (required, unique)
     • Famille (select)
     • Prix unitaire (number)
     • Quantité (number)
     • Seuil d'alerte (number)
     • Date d'expiration (date)
     • Fournisseur (select from /suppliers)
   - Boutons: Annuler (ghost), Sauvegarder (primary)

3. DeleteConfirmModal (components/common/DeleteConfirmModal.jsx) :
   - "Êtes-vous sûr de vouloir supprimer ce médicament ?"
   - Boutons: Annuler, Supprimer (danger)

4. stockService.js :
   - getAllMedicines(params)
   - getMedicineById(id)
   - createMedicine(data)
   - updateMedicine(id, data)
   - deleteMedicine(id)
   - searchMedicines(query)

5. React Query :
   - useQuery pour liste
   - useMutation pour CRUD
   - Invalidate cache après mutation
   - Toast notifications

LIVRABLE : StockListPage, StockFormModal, DeleteConfirmModal, stockService
```

---

## 🏢 PROMPT 5 : Gestion des Fournisseurs

```
CONTEXTE :
Stock terminé. Module Fournisseurs.

BACKEND API :
- GET /suppliers
- POST /suppliers
- PUT /suppliers/{id}
- DELETE /suppliers/{id}

TÂCHE 5 : MODULE FOURNISSEURS

1. SuppliersPage (pages/Suppliers/SuppliersPage.jsx) :
   
   HEADER :
   - Titre "Fournisseurs"
   - Bouton "+ Nouveau fournisseur"
   
   AFFICHAGE EN CARDS (Grid 3 colonnes) :
   - Card par fournisseur :
     • Nom (titre bold)
     • Téléphone (icône Phone)
     • Email (icône Mail)
     • Adresse (icône MapPin)
     • Bordure gauche colorée (#2d9cdb)
   - Actions: Menu dots (...) avec Edit/Delete
   
   OU AFFICHAGE TABLEAU (toggle view) :
   - Colonnes: Nom, Téléphone, Email, Adresse, Actions

2. SupplierFormModal :
   - Formulaire: Nom, Téléphone, Email, Adresse
   - Validation email format

3. supplierService.js :
   - CRUD standard

LIVRABLE : SuppliersPage, SupplierFormModal, supplierService
```

---

## 🛒 PROMPT 6 : Point de Vente (POS) - Module Critique

```
CONTEXTE :
Interface de vente - le cœur du système.

BACKEND API :
- GET /stock (produits disponibles)
- POST /sales/ (créer vente)
- GET /sales/{id}/invoice (facture PDF)

TÂCHE 6 : INTERFACE POS

1. POSPage (pages/POS/POSPage.jsx) :
   
   LAYOUT 2 COLONNES (60% / 40%) :
   
   === COLONNE GAUCHE : Catalogue ===
   - Barre recherche (auto-focus, placeholder "Scanner ou rechercher...")
   - Filtres par famille (pills horizontaux)
   - Grille produits (cards 3-4 par ligne) :
     • Nom médicament
     • Code
     • Prix (F)
     • Stock disponible
     • Clic ajoute au panier
     • Désactivé si stock = 0
   
   === COLONNE DROITE : Panier ===
   - Titre "Panier" avec nombre d'articles
   - Liste items :
     • Nom
     • Prix unitaire × Quantité
     • Boutons +/- pour quantité
     • Bouton X pour supprimer
     • Total ligne
   - Séparateur
   - Sous-total
   - Bonus/Réduction (si applicable)
   - TOTAL (gros, vert #10b981, format "F10,400.00")
   - Bouton "Valider la vente" (full width, vert)

2. PaymentModal (components/common/PaymentModal.jsx) :
   - Récapitulatif panier
   - Mode paiement (radio buttons) :
     • Espèces
     • Mobile Money
     • Carte bancaire
   - Montant payé (input)
   - Monnaie à rendre (calculé auto)
   - Client (optionnel, select)
   - Bouton "Confirmer le paiement"
   - Après succès: Télécharge facture + Toast + Vide panier

3. cartStore (Zustand) :
   - items: []
   - addItem(product)
   - removeItem(productId)
   - updateQuantity(productId, quantity)
   - clearCart()
   - getSubtotal()
   - getTotal()

4. salesService.js :
   - createSale({ items, payment_method, amount_paid, customer_id })
   - downloadInvoice(saleId)

GESTION ERREURS :
- Stock insuffisant → Toast erreur rouge
- Panier vide → Bouton désactivé
- Validation montant payé >= total

LIVRABLE : POSPage, PaymentModal, cartStore, salesService
```

---

## 📜 PROMPT 7 : Historique des Ventes (Design exact de l'image)

```
CONTEXTE :
Page d'historique - reproduire exactement le design de l'image fournie.

BACKEND API :
- GET /sales (liste des ventes)
- GET /sales/{id} (détails)
- GET /sales/{id}/invoice (télécharger facture)

TÂCHE 7 : HISTORIQUE DES VENTES

1. SalesHistoryPage (pages/History/SalesHistoryPage.jsx) :
   
   DESIGN IDENTIQUE À L'IMAGE :
   
   TITRE :
   - "Consultez l'historique de toutes vos ventes"
   
   KPI CARDS (2) :
   - "Total des ventes" : Nombre + icône bleue ronde
   - "Chiffre d'affaires total" : Montant vert + icône dollar verte
   
   ZONE RECHERCHE :
   - Input "Rechercher par ID de vente ou médicament..."
   - Date picker (jj/mm/aaaa) à droite
   
   TABLEAU :
   - Headers: ID DE VENTE | DATE | ARTICLES | TOTAL | ACTIONS
   - ID format "#29b65b87" (bleu)
   - Date: "24/08/2025" + heure "18:56:49" en dessous (gris)
   - Articles: "1 article(s)" + "2 unités" en dessous
   - Total: Montant avec devise, couleur selon statut :
     • Vert "GHC400.00" (payé)
     • Rouge "F2000.00" (remboursé)
   - Actions: 3 icônes (œil voir, télécharger, imprimer)

2. SaleDetailModal :
   - Détails complets de la vente
   - Liste des articles
   - Informations paiement
   - Bouton télécharger facture

3. salesService.js (compléter) :
   - getAllSales(filters)
   - getSaleById(id)
   - searchSales(query)

LIVRABLE : SalesHistoryPage (design exact), SaleDetailModal
```

---

## 📈 PROMPT 8 : Rapports & Exports

```
CONTEXTE :
Module exports.

BACKEND API :
- GET /reports/stock/excel
- GET /reports/sales/excel
- GET /reports/financial/pdf

TÂCHE 8 : PAGE RAPPORTS

1. ReportsPage (pages/Reports/ReportsPage.jsx) :
   
   TITRE : "Rapports & Exports"
   
   GRID 3 CARDS :
   
   Card 1 - Stock :
   - Icône FileSpreadsheet (grande, bleue)
   - Titre "Inventaire Stock"
   - Description "Liste complète des médicaments"
   - Bouton "Télécharger Excel"
   - Loading pendant téléchargement
   
   Card 2 - Ventes :
   - Icône Receipt (grande, verte)
   - Titre "Historique Ventes"
   - Description "Toutes les transactions"
   - Bouton "Télécharger Excel"
   
   Card 3 - Financier :
   - Icône FileText (grande, orange)
   - Titre "Bilan Financier"
   - Description "Rapport PDF complet"
   - Bouton "Télécharger PDF"

2. reportService.js :
   - downloadStockReport()
   - downloadSalesReport()
   - downloadFinancialReport()
   - Utilise responseType: 'blob'

3. Fonction downloadFile(blob, filename)

LIVRABLE : ReportsPage, reportService
```

---

## ⚙️ PROMPT 9 : Paramètres & Finitions

```
CONTEXTE :
Dernière page + finitions.

BACKEND API :
- GET /settings
- PUT /settings

TÂCHE 9 : PARAMÈTRES & FINITIONS

1. SettingsPage (pages/Settings/SettingsPage.jsx) :
   
   SECTIONS :
   
   === Informations Pharmacie ===
   - Nom de la pharmacie
   - Adresse complète
   
   === Configuration Ventes ===
   - Taux de bonus (%)
   - Devise (select: FBu, GHC, USD, EUR)
   
   === Préférences ===
   - Langue (Français, English)
   - Thème (toggle Dark/Light)
   
   === Sauvegarde ===
   - Bouton "Sauvegarder les modifications"
   - Toast succès

2. settingsService.js

3. Finitions globales :

   a) Toast Notifications (composant global) :
      - Succès (vert)
      - Erreur (rouge)
      - Info (bleu)
      - Position: bottom-right
   
   b) Loading States :
      - Spinner pour les chargements
      - Skeleton pour les listes
   
   c) Empty States :
      - Messages quand liste vide
      - Illustration + texte
   
   d) Error Boundary :
      - Page erreur élégante

LIVRABLE : SettingsPage, Toast system, Loading/Empty states
```

---

## 🌐 PROMPT 10 : Multilingue & Offline

```
TÂCHE 10 : I18N & OFFLINE

1. Système i18n (utils/i18n.js) :
   - Traductions FR/EN
   - Hook useTranslation()
   - t(key) retourne la traduction

2. Sélecteur langue dans Header :
   - Dropdown avec drapeaux
   - Persiste dans localStorage

3. Indicateur Offline :
   - Hook useOnlineStatus()
   - Icône dans Header (Wifi/WifiOff)
   - Toast quand connexion revient

4. Appliquer t() à tous les textes hardcodés

LIVRABLE : i18n complet, mode offline
```

---

## ✅ RÉCAPITULATIF FINAL

Après ces 10 prompts, vous aurez une application complète avec :

| Module | Fonctionnalités |
|--------|-----------------|
| Setup | Vite, Tailwind, thème Pharmac+ |
| Auth | Login, JWT, routes protégées |
| Layout | Sidebar, Header, navigation |
| Dashboard | KPIs, graphiques |
| Stock | CRUD complet, badges |
| Fournisseurs | CRUD, cards/tableau |
| POS | Vente complète, panier, paiement |
| Historique | Liste ventes, design exact |
| Rapports | Exports Excel/PDF |
| Paramètres | Configuration système |
| i18n | FR/EN |
| Offline | Détection connexion |

---

## 🚀 COMMANDES DE LANCEMENT

```bash
# Backend
cd backend
venv\Scripts\activate
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

**URLs :**
- Frontend : http://localhost:5173
- Backend : http://localhost:8000
- API Docs : http://localhost:8000/docs
