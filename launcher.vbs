Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")
ScriptPath = FSO.GetParentFolderName(WScript.ScriptFullName)
WshShell.Run chr(34) & ScriptPath & "\Lancer_PharmaGestion.bat" & chr(34), 0
Set WshShell = Nothing
