# 🚀 Guide Complet - Création de l'Exécutable Pharmac+

Ce guide vous permet de créer **un seul fichier .exe** que vous pouvez copier sur n'importe quel PC Windows sans installer Python, Node.js ou autre dépendance.

---

## 📋 Prérequis (Pour la création uniquement)

Ces outils sont nécessaires **uniquement sur le PC où vous créez l'exécutable** :

1. **Python 3.10+** 
2. **Node.js 18+**
3. **Un terminal** (PowerShell ou CMD)

---

## 🔧 Étape 1 : Préparation du Frontend (Interface React)

L'interface doit être compilée en fichiers optimisés.

```bash
cd c:\Pharma_logiciels_version_01\frontend
npm install
npm run build
```

✅ **Vérification** : Un dossier `dist` doit être créé dans `frontend/`

---

## 🔧 Étape 2 : Installation des Dépendances Python

```bash
cd c:\Pharma_logiciels_version_01\backend
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller
```

---

## 🔧 Étape 3 : Création de l'Exécutable

### Option A : **Avec console** (Recommandé pour tester)

```bash
python -m PyInstaller pharmac_plus.spec
```

L'exécutable sera créé avec une fenêtre console qui affiche les logs.

### Option B : **Sans console** (Version finale)

1. Ouvrez `pharmac_plus.spec`
2. Changez `console=True` en `console=False`
3. Lancez : `python -m PyInstaller pharmac_plus.spec`

L'exécutable démarrera en arrière-plan sans fenêtre.

---

## 📦 Étape 4 : Récupération de l'Exécutable

Une fois la compilation terminée (plusieurs minutes) :

1. Allez dans : `c:\Pharma_logiciels_version_01\backend\dist\`
2. Vous y trouverez : **`PharmacPlus.exe`** (environ 100-150 Mo)

**Ce fichier est complètement autonome !**

---

## 💻 Utilisation sur un Autre PC

### Installation

1. **Copiez** `PharmacPlus.exe` sur le nouveau PC
2. **Placez-le** dans un dossier de votre choix (ex: `C:\PharmacPlus\`)

### Lancement

1. **Double-cliquez** sur `PharmacPlus.exe`
   - Version avec console : Une fenêtre noire apparaît
   - Version sans console : Rien de visible (normal)

2. **Ouvrez votre navigateur** (Chrome, Edge, Firefox...)

3. **Allez à l'adresse** : `http://localhost:8000`

4. **La page de connexion apparaît** ✅

### Identifiants par défaut

- **Utilisateur** : `admin`
- **Mot de passe** : (celui que vous avez configuré)

---

## ⚙️ Configuration de la Licence

Pour modifier la date d'expiration **avant** de créer l'exécutable :

1. Ouvrez : `backend/app/core/config.py`
2. Modifiez la ligne :
   ```python
   LICENSE_EXPIRATION_DATE = "2025-12-31"  # Format YYYY-MM-DD
   ```
3. Recréez l'exécutable (Étape 3)

---

## 🛠️ Dépannage

### L'exécutable ne démarre pas

**Avec console activée** : Regardez les messages d'erreur dans la fenêtre noire

**Sans console** : 
1. Ouvrez PowerShell dans le dossier de l'exe
2. Lancez : `.\PharmacPlus.exe`
3. Lisez les erreurs affichées

### "Module not found" ou erreur d'importation

Vérifiez que :
- ✅ Le frontend a bien été build (`npm run build`)
- ✅ Toutes les dépendances sont dans `requirements.txt`
- ✅ L'environnement virtuel est activé avant de lancer PyInstaller

### Le navigateur affiche "Impossible de se connecter"

Le serveur n'a pas démarré. Vérifiez :
- L'exécutable tourne bien (console visible ou processus dans le Gestionnaire des tâches)
- L'URL est exactement `http://localhost:8000` (pas http**s**)

---

## 📝 Notes Importantes

1. **Base de données** : Une base SQLite (`pharmacy_local.db`) sera créée automatiquement au premier lancement dans le dossier utilisateur

2. **Arrêt du serveur** :
   - Avec console : Fermez la fenêtre ou CTRL+C
   - Sans console : Gestionnaire des tâches → Arrêter "PharmacPlus.exe"

3. **Firewall** : Windows peut demander l'autorisation la première fois (Autoriser)

4. **Portable** : Vous pouvez copier l'exe sur une clé USB et l'utiliser sur n'importe quel PC Windows

---

## 🎯 Résumé Rapide

```bash
# 1. Build frontend
cd frontend && npm run build

# 2. Installer dépendances
cd ../backend
venv\Scripts\activate
pip install -r requirements.txt
pip install pyinstaller

# 3. Créer l'exe
python -m PyInstaller pharmac_plus.spec

# 4. Récupérer
# Fichier : backend/dist/PharmacPlus.exe
```

**Utilisation finale** : Double-clic sur exe → Navigateur → `http://localhost:8000`
