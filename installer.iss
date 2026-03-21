[Setup]
AppName=antiRug Enterprise
AppVersion=1.0
DefaultDirName={pf}\antiRug
DefaultGroupName=antiRug
OutputBaseFilename=antiRugSetup

[Files]
Source: "dist\main.exe"; DestDir: "{app}"

[Icons]
Name: "{desktop}\antiRug"; Filename: "{app}\main.exe"