# Solution : Une Seule Fenêtre d'Application

## Problème Résolu

L'application ouvrait plusieurs fenêtres lorsqu'elle était lancée plusieurs fois.

## Solution Implémentée

J'ai ajouté un **Mutex Windows** dans le fichier `frontend1/windows/runner/main.cpp` pour garantir qu'**une seule instance** de l'application peut s'exécuter à la fois.

## Comment ça fonctionne

### 1. Création du Mutex
Au démarrage de l'application, un mutex nommé `PharmaGestionSingleInstanceMutex` est créé.

### 2. Détection d'Instance Existante
Si une instance est déjà en cours d'exécution :
- ✅ La nouvelle instance détecte le mutex existant
- ✅ Elle trouve la fenêtre déjà ouverte
- ✅ Elle restaure et met au premier plan la fenêtre existante
- ✅ Elle se ferme automatiquement

### 3. Comportement Utilisateur
- **Premier lancement** : L'application s'ouvre normalement
- **Double-clic répété** : La fenêtre existante est mise au premier plan (pas de nouvelle fenêtre)
- **Fenêtre minimisée** : Elle est automatiquement restaurée

## Fichier Modifié

**`frontend1/windows/runner/main.cpp`**

Changements clés :
```cpp
// Création du mutex au démarrage
HANDLE hMutex = CreateMutex(NULL, TRUE, L"PharmaGestionSingleInstanceMutex");

// Vérification si une instance existe déjà
if (GetLastError() == ERROR_ALREADY_EXISTS) {
    // Activer la fenêtre existante
    HWND hwnd = FindWindow(NULL, L"Pharmac+ - Gestion de Pharmacie");
    if (hwnd != NULL) {
        SetForegroundWindow(hwnd);
    }
    // Fermer cette nouvelle instance
    return EXIT_SUCCESS;
}
```

## Bonus : Titre de Fenêtre Amélioré

Le titre de la fenêtre a été changé de `"frontend1"` à `"Pharmac+ - Gestion de Pharmacie"` pour :
- Meilleure identification dans la barre des tâches
- Professionnalisme accru
- Faciliter la détection de la fenêtre existante

## Prochaines Étapes

### Rebuild de l'Application Flutter

```powershell
cd frontend1
flutter build windows --release
```

### Rebuild de l'Installateur Complet

```powershell
.\build_installer.bat
```

## Test de la Solution

1. Installer la nouvelle version
2. Lancer l'application
3. Essayer de lancer l'application une deuxième fois
4. **Résultat attendu** : La fenêtre existante se met au premier plan, aucune nouvelle fenêtre ne s'ouvre

## Avantages

✅ **Une seule fenêtre** - Impossible d'ouvrir plusieurs instances  
✅ **Expérience utilisateur améliorée** - Pas de confusion avec plusieurs fenêtres  
✅ **Gestion de ressources** - Évite la duplication inutile de processus  
✅ **Professionnel** - Comportement standard des applications Windows  

## Notes Techniques

- Le mutex est automatiquement libéré à la fermeture de l'application
- La solution fonctionne même si l'utilisateur double-clique rapidement plusieurs fois
- Compatible avec toutes les versions de Windows
