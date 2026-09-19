; Inno Setup 6 Script for Local Backup Vault
#define MyAppName "Local Backup Vault"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Wachira"
#define MyAppExeName "LocalBackupVault.exe"

[Setup]
; App Metadata
AppId={{8A12B487-23A1-423D-93E1-BC90334812AB}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; Output Configuration
OutputDir=C:\Users\wachi\OneDrive\Documents\Output
OutputBaseFilename=LocalBackupVault_Setup
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern

; Execution Permissions
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "autostart"; Description: "Automatically start {#MyAppName} when Windows starts"; GroupDescription: "Startup Options:"

[Files]
; Source binary from PyInstaller dist directory
Source: "C:\Users\wachi\OneDrive\Documents\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start Menu and Desktop Shortcuts
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

; Windows Startup Shortcut (if task selected)
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: autostart

[Run]
; Option to launch app after installation completes
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent