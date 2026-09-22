#define MyAppName "DirectDrop"
#define MyAppVersion "0.2.0"
#define MyAppPublisher "Shyamraj"
#define MyAppExeName "DirectDrop.exe"
#define MyAgentExeName "DirectDropAgent.exe"

[Setup]
AppId={{9F3B5A71-7F9B-4D0E-B61D-5D8D1E6A0D2A}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\DirectDrop
DefaultGroupName=DirectDrop
OutputDir=output
OutputBaseFilename=DirectDrop-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible
Uninstallable=yes
CloseApplications=no
DisableProgramGroupPage=yes

[Files]
Source: "dist\DirectDrop.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\DirectDropAgent.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\DirectDrop"; Filename: "{app}\DirectDrop.exe"
Name: "{autodesktop}\DirectDrop"; Filename: "{app}\DirectDrop.exe"
Name: "{userstartup}\DirectDrop Agent"; Filename: "{app}\DirectDropAgent.exe"; WorkingDir: "{app}"

[Run]
Filename: "netsh.exe"; Parameters: "advfirewall firewall add rule name=""DirectDrop TCP 8765"" dir=in action=allow protocol=TCP localport=8765 profile=private"; Flags: runhidden
Filename: "netsh.exe"; Parameters: "advfirewall firewall add rule name=""DirectDrop UDP 8766"" dir=in action=allow protocol=UDP localport=8766 profile=private"; Flags: runhidden
Filename: "{app}\DirectDropAgent.exe"; WorkingDir: "{app}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "netsh.exe"; Parameters: "advfirewall firewall delete rule name=""DirectDrop TCP 8765"""; Flags: runhidden
Filename: "netsh.exe"; Parameters: "advfirewall firewall delete rule name=""DirectDrop UDP 8766"""; Flags: runhidden

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
