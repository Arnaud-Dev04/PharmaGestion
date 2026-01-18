; Script Inno Setup pour PharmaGestion
; Crée un installateur Windows unique avec Visual C++ Redistributables

#define MyAppName "PharmaGest"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "PharmaGest"
#define MyAppExeName "PharmaGestion.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=Output
OutputBaseFilename=PharmaGestion_Setup
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
SetupIconFile=frontend1\windows\runner\resources\app_icon.ico
UninstallDisplayIcon={app}\app\{#MyAppExeName}

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
; Launcher principal
Source: "dist\PharmaGestion.exe"; DestDir: "{app}"; Flags: ignoreversion
; Launcher VBS
Source: "launcher.vbs"; DestDir: "{app}"; Flags: ignoreversion
; Application Flutter
Source: "release\PharmaGestion\app\*"; DestDir: "{app}\app"; Flags: ignoreversion recursesubdirs createallsubdirs
; Backend Python
Source: "release\PharmaGestion\backend\*"; DestDir: "{app}\backend"; Flags: ignoreversion recursesubdirs createallsubdirs
; Visual C++ Redistributables (si disponibles)
Source: "vcredist\vc_redist.x64.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall; Check: IsVCRedistNeeded
Source: "vcredist\vc_redist.x86.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall; Check: IsVCRedistNeeded

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Désinstaller {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Installer Visual C++ Redistributables en mode silencieux
Filename: "{tmp}\vc_redist.x64.exe"; Parameters: "/install /quiet /norestart"; StatusMsg: "Installation de Visual C++ Redistributables (x64)..."; Flags: waituntilterminated; Check: IsVCRedistNeeded
Filename: "{tmp}\vc_redist.x86.exe"; Parameters: "/install /quiet /norestart"; StatusMsg: "Installation de Visual C++ Redistributables (x86)..."; Flags: waituntilterminated; Check: IsVCRedistNeeded
; Lancer l'application
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
function IsVCRedistNeeded(): Boolean;
var
  Version: String;
begin
  // Vérifier si Visual C++ 2015-2022 Redistributable est installé
  // Si non installé, retourner True pour installer
  Result := not RegQueryStringValue(HKLM64, 'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64', 'Version', Version);
  if not Result then
    Log('Visual C++ Redistributable déjà installé: ' + Version)
  else
    Log('Visual C++ Redistributable non détecté, installation requise');
end;

function InitializeSetup(): Boolean;
begin
  Result := True;
  if MsgBox('Bienvenue dans l''installation de PharmaGestion.' + #13#10 + #13#10 +
            'Cette application nécessite environ 120 MB d''espace disque.' + #13#10 +
            'Les composants Visual C++ seront installés si nécessaire.' + #13#10 + #13#10 +
            'Voulez-vous continuer ?', mbConfirmation, MB_YESNO) = IDNO then
    Result := False;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  AppDataDir: String;
begin
  if CurStep = ssPostInstall then
  begin
    // Créer le dossier de données dans AppData
    AppDataDir := ExpandConstant('{userappdata}\PharmaGestion');
    if not DirExists(AppDataDir) then
      CreateDir(AppDataDir);
    
    // Copier la base de données template si elle existe
    if FileExists(ExpandConstant('{app}\backend\pharmacy_local.db')) then
    begin
      if not FileExists(AppDataDir + '\pharmacy_local.db') then
        FileCopy(ExpandConstant('{app}\backend\pharmacy_local.db'), 
                 AppDataDir + '\pharmacy_local.db', False);
    end;
  end;
end;

