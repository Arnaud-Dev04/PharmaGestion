# ✅ Checklist GitHub - Fichiers à exclure/inclure

## 📋 Guide : Quels fichiers DOIVENT être sur GitHub ?

### ✅ FICHIERS À INCLURE (Code source et configuration)

#### **Code Source**
- ✅ **Backend** : `backend/app/**/*.py` (tous les fichiers Python du code source)
- ✅ **Frontend Flutter** : `frontend1/lib/**/*.dart` (tous les fichiers Dart)
- ✅ **Frontend React** : `frontend/**/*.{js,jsx,ts,tsx}` (si utilisé)

#### **Configuration du Projet**
- ✅ `requirements.txt` (dépendances Python)
- ✅ `pubspec.yaml` et `pubspec.lock` (dépendances Flutter)
- ✅ `package.json` et `package-lock.json` (dépendances npm, si utilisé)
- ✅ `*.yaml`, `*.yml` (configurations)
- ✅ `*.spec` pour PyInstaller (mais on les exclut pour éviter les doublons)

#### **Documentation**
- ✅ `README.md` (documentation principale)
- ✅ `*.md` (tous les fichiers Markdown de documentation)
- ✅ `GUIDE_*.md` (guides d'utilisation)

#### **Fichiers de Configuration Git**
- ✅ `.gitignore` (ce fichier)
- ✅ `LICENSE` (si vous avez une licence)

#### **Fichiers de Build (Configuration seulement)**
- ✅ `CMakeLists.txt` (config Flutter Windows)
- ✅ `*.gradle.kts` (config Android)
- ✅ `*.xml` de configuration Android (pas les builds)
- ✅ `build_*.bat`, `build_*.py` (scripts de build)

---

## ❌ FICHIERS À EXCLURE (Ne pas mettre sur GitHub)

### ❌ **Fichiers de Build / Compilation**
- ❌ `build/` (dossiers de build)
- ❌ `dist/` (fichiers distribuables)
- ❌ `release/` (builds de release)
- ❌ `Output/` (exécutables générés)
- ❌ `__pycache__/` (cache Python)
- ❌ `*.pyc`, `*.pyo` (fichiers Python compilés)

### ❌ **Environnements Virtuels**
- ❌ `venv/` (environnement Python virtuel)
- ❌ `env/`, `ENV/` (autres environnements)
- ❌ `node_modules/` (dépendances npm - volumineux)
- ❌ `.dart_tool/` (outils Dart)
- ❌ `.flutter-plugins*` (plugins Flutter générés)

### ❌ **Bases de Données**
- ❌ `*.db` (bases de données SQLite)
- ❌ `*.sqlite`, `*.sqlite3`
- ❌ `pharmacy_local.db` (votre base de données locale)

### ❌ **Fichiers Sensibles / Secrets**
- ❌ `.env` (variables d'environnement avec secrets)
- ❌ `*.env.local`
- ❌ Fichiers contenant des mots de passe, clés API, tokens

### ❌ **Fichiers Binaires / Exécutables**
- ❌ `*.exe` (exécutables Windows)
- ❌ `*.dll` (bibliothèques)
- ❌ `*.dylib`, `*.so` (bibliothèques Unix)
- ❌ `*.pdf` générés (factures, rapports de test)
- ❌ `*.xlsx` générés (rapports de test)
- ❌ `*.jpg`, `*.jpeg`, `*.png` de test/générés (sauf assets)

### ❌ **Logs et Fichiers Temporaires**
- ❌ `*.log` (fichiers de log)
- ❌ `*.txt` de log (`output_*.txt`, `test*_output.txt`)
- ❌ `*.tmp`, `*.temp`, `*.bak`

### ❌ **Fichiers IDE / Éditeur**
- ❌ `.vscode/` (config VS Code personnelle)
- ❌ `.idea/` (config IntelliJ/Android Studio)
- ❌ `*.iml` (fichiers IntelliJ - sauf si partagé)
- ❌ `.DS_Store` (macOS)
- ❌ `Thumbs.db` (Windows)

### ❌ **Fichiers de Debug / Test générés**
- ❌ `test_*.pdf` (rapports de test générés)
- ❌ `test_*.xlsx` (rapports Excel de test)
- ❌ `facture_*.pdf` (factures générées)
- ❌ `debug.log` (logs de debug)
- ❌ `.cursor/` (dossiers d'outils de développement)

---

## 🤔 FICHIERS À CONSIDÉRER (Optionnel - Dépend de votre cas)

### ⚠️ **Scripts de Migration / Test / Debug**
Ces fichiers peuvent être utiles mais ne sont pas essentiels :

- ⚠️ `backend/test_*.py` (scripts de test manuels)
- ⚠️ `backend/debug_*.py` (scripts de debug)
- ⚠️ `backend/check_*.py` (scripts de vérification)
- ⚠️ `backend/fix_*.py` (scripts de correction ponctuels)
- ⚠️ `backend/migrate_*.py` (scripts de migration)

**Recommandation** : Les garder s'ils sont utiles pour d'autres développeurs, sinon les exclure.

### ⚠️ **Fichiers de Build Scripts**
- ⚠️ `build_*.bat`, `build_*.py` (scripts de build - utiles pour reproduire les builds)
- ⚠️ `*.spec` (spécifications PyInstaller - peuvent être utiles)

**Recommandation** : Les garder s'ils sont nécessaires pour construire le projet.

---

## 📝 Résumé Rapide

### ✅ À INCLURE (Essentiels)
```
✅ Code source (*.py, *.dart, *.js, *.jsx)
✅ Configuration (requirements.txt, pubspec.yaml, package.json)
✅ Documentation (README.md, *.md)
✅ .gitignore
✅ Assets (images, logos nécessaires)
```

### ❌ À EXCLURE (Toujours)
```
❌ Builds (build/, dist/, release/)
❌ Environnements (venv/, node_modules/)
❌ Bases de données (*.db)
❌ Secrets (.env)
❌ Binaires (*.exe, *.dll, *.pdf générés)
❌ Logs (*.log, *.txt de log)
❌ Cache (__pycache__/, .dart_tool/)
```

---

## 🚀 Vérification Avant Commit

Avant de pousser sur GitHub, vérifiez :

1. ✅ Aucun fichier `.db` dans le commit
2. ✅ Aucun fichier `.env` dans le commit
3. ✅ Aucun dossier `venv/` ou `node_modules/` dans le commit
4. ✅ Aucun fichier `*.exe` dans le commit
5. ✅ Aucun dossier `build/`, `dist/`, `release/` dans le commit
6. ✅ Le `.gitignore` est présent et correct

---

**Note** : Le `.gitignore` actuel devrait déjà exclure tous ces fichiers. Vérifiez avec `git status` avant de committer !

