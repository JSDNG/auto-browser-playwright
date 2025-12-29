; Inno Setup Script để tạo installer .exe cho Windows
; Yêu cầu: Cài Inno Setup từ https://jrsoftware.org/isdl.php
;
; Build: 
;   1. Build PyInstaller trước: pyinstaller build.spec
;   2. Chạy Inno Setup Compiler với file này
;   3. Hoặc dùng command line: "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\windows\EtsyCrawler.iss

#define AppName "Etsy Crawler"
#define AppVersion "1.0.0"
#define AppPublisher "Your Company"
#define AppURL "https://example.com"
#define AppExeName "EtsyCrawler.exe"
#define BuildDir "dist"
#define SourceDir "installer\windows"

[Setup]
; App info
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
AllowNoIcons=yes
LicenseFile=LICENSE.txt
InfoBeforeFile=installer\windows\README.txt
OutputDir=installer\windows\output
OutputBaseFilename=EtsyCrawler-Setup-{#AppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "vietnamese"; MessagesFile: "compiler:Languages\Vietnamese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1

[Files]
; Main executable
Source: "{#BuildDir}\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; Config file (config.ini)
Source: "config.ini"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist
; README
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme
; License (if exists)
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion; Check: FileExists(ExpandConstant('{src}\LICENSE.txt'))

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{group}\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"
Name: "{autodesk}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
function FileExists(FileName: String): Boolean;
begin
  Result := FileExists(ExpandConstant(FileName));
end;

