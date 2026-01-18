# 🚀 Guide Complet - Application Desktop Pharmac+

Ce guide vous permet de créer une **application desktop autonome** qui s'ouvre dans sa propre fenêtre (pas de navigateur).

---

## 📋 Prérequis (Pour la création uniquement)

Ces outils sont nécessaires **uniquement sur le PC où vous créez l'application** :

1. **Python 3.10+** 
2. **Node.js 18+**
3. **Un terminal** (PowerShell ou CMD)

---

## 🎯 Méthode Recommandée : Application Desktop

### Étape 1 : Build du Frontend

```bash
cd c:\Pharma_logiciels_version_01\frontend
npm install
npm run build
```

### Étape 2 : Installation des Dépendances

```bash
cd c:\Pharma_logiciels_version_01\backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install pyinstaller
```

### Étape 3 : Test de l'Application Desktop

Avant de créer l'exécutable, testez que tout fonctionne :

```bash
python desktop_app.py
```

Une fenêtre devrait s'ouvrir avec votre application ! ✅

### Étape 4 : Création de l'Exécutable Desktop

Utilisez le fichier spec spécial pour desktop :

```bash
python -m PyInstaller desktop_app.spec
```

---

## 📦 Résultat Final

Après la compilation, vous obtiendrez :

**Emplacement** : `c:\Pharma_logiciels_version_01\backend\dist\PharmacPlus\`

**Contenu du dossier** :
- `PharmacPlus.exe` - L'exécutable principal
- Plusieurs DLL et fichiers de support
- Dossier `_internal` avec les dépendances

**Taille totale** : ~200-300 Mo

---

## 💻 Utilisation

### Sur votre PC

1. Allez dans `backend\dist\PharmacPlus\`
2. Double-cliquez sur `PharmacPlus.exe`
3. ✨ L'application s'ouvre dans sa propre fenêtre !

### Sur un Autre PC

1. **Copiez** tout le dossier `PharmacPlus`
2. **Collez** où vous voulez (ex: `C:\Program Files\PharmacPlus\`)
3. **Lancez** `PharmacPlus.exe`

**Aucune installation requise !** Python, Node.js, etc. ne sont pas nécessaires.

---

## 📤 Distribution

### Option A : Fichier ZIP

```powershell
# Compresser le dossier
Compress-Archive -Path "backend\dist\PharmacPlus" -DestinationPath "PharmacPlus-v1.0.zip"
```

Partagez le fichier ZIP. Les utilisateurs décompressent et lancent l'exe.

### Option B : Installateur (Avancé)

Utilisez **Inno Setup** ou **NSIS** pour créer un vrai installateur .exe qui :
- Copie les fichiers dans Program Files
- Crée un raccourci sur le bureau
- Ajoute au menu Démarrer

---

## ⚙️ Configuration

### Modifier la Date de Licence

Avant de compiler :

1. Ouvrez `backend/app/core/config.py`
2. Modifiez :
   ```python
   LICENSE_EXPIRATION_DATE = "2025-12-31"  # YYYY-MM-DD
   ```
3. Recompilez

### Personnaliser la Fenêtre

Dans `backend/desktop_app.py`, modifiez :

```python
window = webview.create_window(
    title='Pharmac+ - Gestion de Pharmacie',  # Titre
    width=1400,  # Largeur
    height=900,  # Hauteur
    # ...
)
```

---

## 🛠️ Dépannage

### L'application ne démarre pas

1. Vérifiez que le dossier complet est copié (pas juste l'exe)
2. Désactivez l'antivirus temporairement (faux positif possible)
3. Exécutez en tant qu'administrateur

### Écran blanc au démarrage

Le serveur prend quelques secondes à démarrer. Attendez 5-10 secondes.

### Port 8000 déjà utilisé

Une autre application utilise le port. Fermez les autres instances de Pharmac+.

---

## 📊 Avantages de cette Méthode

✅ **Vrai application desktop** - Fenêtre native, pas de navigateur
✅ **Portable** - Fonctionne sur n'importe quel PC Windows
✅ **Professionnel** - Apparaît comme une vraie application
✅ **Facile à distribuer** - Un seul dossier à zipper
✅ **Auto-contenu** - Tout est inclus

---

## 🎯 Résumé Rapide

```bash
# 1. Build
cd frontend && npm run build

# 2. Installer
cd ../backend
venv\Scripts\activate
pip install -r requirements.txt
pip install pyinstaller

# 3. Compiler
python -m PyInstaller desktop_app.spec

# 4. Distribuer
# Fichier : backend/dist/PharmacPlus/ (tout le dossier)
```

**Utilisation** : Double-clic sur `PharmacPlus.exe` dans le dossier
