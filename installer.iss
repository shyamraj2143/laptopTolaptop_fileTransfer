#define MyAppName "DirectDrop"
#define MyAppVersion "0.4.0"
#define MyAppPublisher "Shyamraj"

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
PrivilegesRequired=lowest
Uninstallable=yes
CloseApplications=yes
DisableProgramGroupPage=yes
ArchitecturesInstallIn64BitMode=x64compatible

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
Filename: "taskkill.exe"; Parameters: "/F /IM DirectDropAgent.exe"; Flags: runhidden
Filename: "taskkill.exe"; Parameters: "/F /IM DirectDrop.exe"; Flags: runhidden
Filename: "netsh.exe"; Parameters: "advfirewall firewall delete rule name=""DirectDrop TCP 8765"""; Flags: runhidden
Filename: "netsh.exe"; Parameters: "advfirewall firewall delete rule name=""DirectDrop UDP 8766"""; Flags: runhidden

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  ResultCode: Integer;
begin
  Result := '';
  NeedsRestart := False;

  { Stop the old DirectDrop processes before Inno Setup replaces their EXEs. }
  Exec(ExpandConstant('{sys}\taskkill.exe'),
    '/F /IM DirectDropAgent.exe',
    '', SW_HIDE, ewWaitUntilTerminated, ResultCode);

  Exec(ExpandConstant('{sys}\taskkill.exe'),
    '/F /IM DirectDrop.exe',
    '', SW_HIDE, ewWaitUntilTerminated, ResultCode);

  { Remove the old scheduled task from previous installer versions. }
  Exec(ExpandConstant('{sys}\schtasks.exe'),
    '/End /TN "DirectDrop Background Agent"',
    '', SW_HIDE, ewWaitUntilTerminated, ResultCode);

  Exec(ExpandConstant('{sys}\schtasks.exe'),
    '/Delete /TN "DirectDrop Background Agent" /F',
    '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;
