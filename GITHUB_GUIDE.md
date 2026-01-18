# Guide de Dépôt sur GitHub

Ce guide vous explique comment mettre à jour votre dépôt GitHub avec la nouvelle structure nettoyée.

## 0. Créer le dépôt sur GitHub (Si ce n'est pas fait)
Comme votre projet n'est pas encore lié, vous devez d'abord créer un espace sur GitHub :

1.  Connectez-vous à **[github.com](https://github.com)**.
2.  Cliquez sur le **bouton "+"** en haut à droite, puis **"New repository"**.
3.  **Repository name** : Mettez par exemple `PharmaGestion`.
4.  **Public/Private** : Choisissez "Private" si c'est un logiciel commercial.
5.  Ne cochez **RIEN** d'autre (pas de README, pas de .gitignore).
6.  Cliquez sur **"Create repository"**.
7.  Copiez l'URL qui s'affiche (ex: `https://github.com/votre-pseudo/PharmaGestion.git`).

## 1. État des lieux
J'ai effectué les actions suivantes pour nettoyer le projet :
- **Déplacement des scripts** : Tous les scripts de maintenance (`fix_*.py`, `check_*.py`, etc.) sont maintenant dans `backend/scripts/`.
- **Déplacement des tests** : Les fichiers de test (`test_*.py`) sont maintenant dans `backend/tests/`.
- **Nettoyage** : Suppression des fichiers temporaires (`.pdf`, `.xlsx`, logs) à la racine du backend.
- **Sécurité** : Mise à jour de `.gitignore` pour ignorer les bases de données et fichiers sensibles.

## 2. Procédure de mise à jour (Git)

Ouvrez un terminal dans le dossier `c:\Pharma_logiciels_version_01` et exécutez les commandes suivantes :

### Étape 1 : Vérifier les changements
```bash
git status
```
Vous devriez voir beaucoup de fichiers supprimés (ceux déplacés) et de nouveaux fichiers dans `backend/scripts/` et `backend/tests/`.

### Étape 2 : Ajouter les modifications
Ceci va prendre en compte tous les déplacements et suppressions.
```bash
git add .
```

### Étape 3 : Commit
```bash
git commit -m "Refactor: Nettoyage structure backend (scripts et tests deplacés)"
```

### Étape 4 : Lier et Pousser vers GitHub
Une fois l'URL copiée (étape 0), lancez ces commandes (remplacez l'URL par la vôtre) :

```bash
# Lier le dépôt local au dépôt distant
git remote add origin https://github.com/votre-pseudo/PharmaGestion.git

# Renommer la branche principale en 'main' (standard actuel)
git branch -M main

# Envoyer les fichiers
git push -u origin main
```

## 3. Remarques Importantes
- **Base de données** : Le fichier `pharmacy_local.db` est ignoré par `.gitignore` pour ne pas écraser vos données de production lors d'un clonage. Pensez à faire des sauvegardes manuelles.
- **Dossier Scripts** : Si vous devez lancer un script de maintenance, allez dans le dossier :
  ```bash
  cd backend/scripts
  python fix_users.py
  ```
  *(Note : Il faudra peut-être ajuster les imports dans certains scripts s'ils ne trouvent plus le module `app`. Si c'est le cas, lancez-les depuis `backend` comme ceci : `python -m scripts.fix_users`)*.

Votre projet est maintenant propre et prêt pour GitHub !
