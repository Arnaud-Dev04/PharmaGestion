
## Étape 10 : Maintenance & Debugging
**Prompt 11 (Debugging) :**
```text
Je rencontre des problèmes avec l'application Flutter. Peux-tu effectuer un diagnostic complet ?
Voici les étapes à suivre :

1. **Analyse des Logs Running** :
   - Regarde les exceptions dans la console (ex: `type 'double' is not a subtype of type 'int'`, `RenderFlex overflow`, `LocaleDataException`).
   - Identifie le fichier et la ligne exacts.

2. **Vérification API & Modèles** :
   - Compare la réponse JSON brute de l'API (logs `[API] *** Response ***`) avec les classes `.fromJson` dans `lib/models/`.
   - Vérifie si un champ `int` reçoit un `double` (ex: `1000.0`), ou si un champ optionnel est nul.
   - Si erreur de typage : Modifie le modèle pour utiliser `(json['champ'] as num).toDouble()` (pour les double) ou `toInt()` (pour les int).

3. **Vérification UI & State** :
   - Si écran blanc ou "chargement infini" : Vérifie si un `FutureBuilder` a crashé silencieusement (ajout de logs dans `catchError`).
   - Si "RenderFlex overflow" : Vérifie les `Column`/`Row` et ajuste avec `Expanded`, `Flexible` ou `SingleChildScrollView`.

4. **Action** :
   - Propose la correction du code (fichier complet ou diff).
   - Indique si un redémarrage complet (`R` ou stop/start) est nécessaire.
```
