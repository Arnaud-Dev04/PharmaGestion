# Guide de Création de l'Installateur Windows

Ce guide explique comment créer un installateur Windows unique (`.exe`) pour distribuer l'application Pharmac+.

## Prérequis

1. **Python 3.10+** avec PyInstaller installé
2. **Flutter** configuré pour Windows
3. **Inno Setup** (télécharger depuis https://jrsoftware.org/isdl.php)
4. **Connexion Internet** (pour télécharger les Visual C++ Redistributables)

## Solution au Problème MSVCP140.dll

L'application utilise une **double protection** pour garantir la compatibilité sur tous les systèmes Windows :

### ✅ Solution 1 : DLLs Intégrées dans le Backend

Le backend Python est compilé avec PyInstaller en mode `--collect-binaries=*`, ce qui inclut automatiquement toutes les DLLs Visual C++ Runtime nécessaires (MSVCP140.dll, VCRUNTIME140.dll, etc.) directement dans l'exécutable.

### ✅ Solution 2 : Installation Automatique des Redistributables

L'installateur inclut les **Visual C++ 2015-2022 Redistributables** (x86 et x64) et les installe automatiquement si nécessaire. L'installation est :

- **Silencieuse** (pas d'interaction utilisateur)
- **Intelligente** (détecte si déjà installé)
- **Rapide** (quelques secondes seulement)


Cette approche garantit que l'application fonctionnera sur **n'importe quel ordinateur Windows**, même sans Visual C++ préinstallé.

## Étape 1 : Build du Frontend Flutter

```powershell
cd frontend1
flutter build windows --release
```

Cela crée l'application dans `frontend1\build\windows\x64\runner\Release\`

## Étape 2 : Build du Backend Python

```powershell
cd backend
python build_exe.py
```

Cela crée `backend\dist\PharmaBackend.exe` avec toutes les DLLs nécessaires intégrées.

## Étape 3 : Création de l'Installateur

### Option A : Script Automatique (Recommandé)

Exécutez le script de build complet :

```powershell
.\build_installer.bat
```

Ce script effectue automatiquement :
1. **Téléchargement** des Visual C++ Redistributables (si nécessaire)
2. **Création** du launcher invisible
3. **Build** de l'application Flutter
4. **Build** du backend Python avec DLLs intégrées
5. **Préparation** du dossier de release
6. **Création** de l'installateur avec Inno Setup

### Option B : Manuelle avec Inno Setup

1. Téléchargez d'abord les Visual C++ Redistributables :

   ```powershell
   .\download_vcredist.bat
   ```

2. Ouvrez `installer_script.iss` avec Inno Setup Compiler
3. Cliquez sur **Build > Compile**
4. L'installateur sera créé dans `Output\PharmaGestion_Setup.exe`

## Structure de l'Installateur

L'installateur inclut :

- ✅ Application Flutter (frontend)
- ✅ Backend Python compilé **avec DLLs intégrées**
- ✅ Visual C++ Redistributables (x86 + x64)
- ✅ Base de données SQLite vide
- ✅ Icônes et ressources
- ✅ Raccourci Bureau
- ✅ Raccourci Menu Démarrer
- ✅ Désinstalleur automatique

## Distribution

Envoyez simplement le fichier `PharmaGestion_Setup.exe` à vos utilisateurs.

**Taille approximative :** 100-140 MB (incluant les redistributables)

## Installation pour l'Utilisateur

1. Double-cliquer sur `PharmaGestion_Setup.exe`
2. Suivre l'assistant d'installation
3. Les Visual C++ Redistributables seront installés automatiquement si nécessaire
4. Lancer l'application depuis le raccourci Bureau ou Menu Démarrer

## Identifiants par Défaut

- **Username:** admin
- **Password:** pharma123

## Notes Importantes

- L'application fonctionne **100% hors ligne**
- Les données sont stockées localement dans `%APPDATA%\PharmaGestion\`
- La licence est configurée dans le backend (fichier `config.py`)
- **Aucune fenêtre de console n'apparaît** lors de l'exécution (backend et launcher invisibles)
- **Compatibilité garantie** sur tous les systèmes Windows grâce à la double solution DLLs

## Nouvelles Fonctionnalités

### 🔒 Instance Unique
L'application est maintenant configurée pour ne s'ouvrir qu'une seule fois.
- Si l'utilisateur essaie de la lancer alors qu'elle est déjà ouverte, la fenêtre existante est mise au premier plan.
- Empêche les conflits de base de données et de ressources.
- Titre de fenêtre amélioré : "Pharmac+ - Gestion de Pharmacie"

## Architecture du Launcher

L'application utilise un système de launcher en 3 couches pour garantir une exécution invisible et robuste :

1. **PharmaGestion.exe** - Wrapper exécutable invisible
2. **launcher.vbs** - Script VBScript de gestion
3. **Backend** - Python invisible avec DLLs intégrées
4. **Frontend** - Flutter avec Mutex d'instance unique

Cette architecture garantit :
- Pas de console visible
- Une seule fenêtre à l'écran
- Compatibilité système maximale

## Dépannage

### Problème : "MSVCP140.dll was not found"

Si cette erreur apparaît malgré l'installateur :

1. **Vérifier que les redistributables sont inclus** :
   - Le dossier `vcredist\` doit contenir `vc_redist.x64.exe` et `vc_redist.x86.exe`
   - Si absent, exécutez `.\download_vcredist.bat`

2. **Rebuild le backend** avec les nouvelles options :

   ```powershell
   cd backend
   python build_exe.py
   ```

3. **Rebuild l'installateur** :

   ```powershell
   .\build_installer.bat
   ```

### Installation Manuelle des Redistributables

Si nécessaire, téléchargez et installez manuellement :

- **x64** : <https://aka.ms/vs/17/release/vc_redist.x64.exe>
- **x86** : <https://aka.ms/vs/17/release/vc_redist.x86.exe>

