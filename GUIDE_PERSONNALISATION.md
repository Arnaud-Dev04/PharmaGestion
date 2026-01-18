# Guide de Personnalisation : Nom et Icône

Ce fichier liste toutes les modifications à faire pour changer le nom de "Pharmac+" et l'icône de l'application.

## 1. Changer l'Icône de l'application

C'est l'image qui apparait dans la barre des tâches et sur le bureau.

*   **Fichier cible :** `c:\Pharma_logiciels_version_01\frontend1\windows\runner\resources\app_icon.ico`
*   **Action :**
    1.  Préparez votre logo au format **.ico**.
    2.  Renommez-le exactement `app_icon.ico`.
    3.  **Remplacez** le fichier existant dans le dossier ci-dessus par le vôtre.

---

## 2. Changer le Nom de la Fenêtre

C'est le texte affiché dans la barre de titre de l'application.

*   **Fichier cible :** `c:\Pharma_logiciels_version_01\frontend1\windows\runner\main.cpp`
*   **Lignes à modifier :** Ligne 16 et Ligne 54.
*   **Action :** Remplacez `"Pharmac+ - Gestion de Pharmacie"` par votre nouveau titre.

```cpp
// Avant
HWND hwnd = FindWindow(NULL, L"Pharmac+ - Gestion de Pharmacie");
// ...
if (!window.Create(L"Pharmac+ - Gestion de Pharmacie", origin, size)) {

// Après
HWND hwnd = FindWindow(NULL, L"Mon Nouveau Nom");
// ...
if (!window.Create(L"Mon Nouveau Nom", origin, size)) {
```

---

## 3. Changer le Nom "Interne" (Gestionnaire des tâches)

C'est le nom qui s'affiche quand vous faites Clic Droit > Propriétés sur le fichier .exe.

*   **Fichier cible :** `c:\Pharma_logiciels_version_01\frontend1\windows\runner\Runner.rc`
*   **Lignes à modifier :** Lignes 92, 93, 95, 98 (cherchez "frontend1" ou "com.pharma").
*   **Action :** Remplacez les valeurs par les vôtres.

```cpp
VALUE "CompanyName", "Votre Entreprise" "\0"
VALUE "FileDescription", "Nom de l'App" "\0"
VALUE "InternalName", "Nom de l'App" "\0"
VALUE "ProductName", "Nom de l'App" "\0"
```

---

## 4. Changer le Nom de l'Installateur et de l'Exécutable

Pour que le fichier final s'appelle `MonLogiciel.exe` et non `PharmaGestion.exe`.

*   **Fichier cible :** `c:\Pharma_logiciels_version_01\installer_script.iss`
*   **Lignes à modifier :** Début du fichier (lignes 4 à 7).

```ini
#define MyAppName "Mon Nouveau Nom"
#define MyAppPublisher "Ma Pharmacie"
#define MyAppExeName "MonLogiciel.exe"
```

*   **Fichier cible :** `c:\Pharma_logiciels_version_01\PharmaGestion.spec`
*   **Ligne à modifier :** Ligne `name='PharmaGestion'`.

```python
exe = EXE(
    # ...
    name='MonLogiciel',  <-- Modifiez ici
    # ...
)
```

---

## 5. Appliquer les changements

Une fois tous ces fichiers modifiés, lancez simplement la recompilation complète :

Double-cliquez sur `build_installer.bat` ou lancez dans le terminal :

```powershell
.\build_installer.bat
```
