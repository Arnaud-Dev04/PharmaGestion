' Launcher invisible pour PharmaGestion
' Lance l'application sans afficher de fenêtre de console

Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Obtenir le dossier du script
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)

' Créer le dossier de données si nécessaire
appDataDir = WshShell.ExpandEnvironmentStrings("%APPDATA%") & "\PharmaGestion"
If Not fso.FolderExists(appDataDir) Then
    fso.CreateFolder(appDataDir)
End If

' Démarrer le backend en arrière-plan (fenêtre cachée)
backendPath = scriptDir & "\backend\PharmaBackend.exe"

' Tuer toute instance existante du backend pour libérer le port 8000
WshShell.Run "taskkill /F /IM PharmaBackend.exe", 0, True

' Démarrer le nouveau backend
WshShell.Run """" & backendPath & """", 0, False

' Attendre 3 secondes que le backend démarre
WScript.Sleep 3000

' Démarrer l'application Flutter (fenêtre cachée au démarrage)
appPath = scriptDir & "\app\PharmaGest.exe"
WshShell.Run """" & appPath & """", 1, True

' Tuer le backend quand l'app se ferme
WshShell.Run "taskkill /F /IM PharmaBackend.exe", 0, False
