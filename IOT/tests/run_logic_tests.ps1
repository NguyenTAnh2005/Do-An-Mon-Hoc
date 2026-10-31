$ErrorActionPreference = 'Stop'

# Test logic thuan tren may tinh, khong ket noi broker hay dieu khien ESP32.
if (-not (Get-Command cl.exe -ErrorAction SilentlyContinue)) {
    $vsWhere = Join-Path ([Environment]::GetFolderPath('ProgramFilesX86')) 'Microsoft Visual Studio/Installer/vswhere.exe'
    if (-not (Test-Path -LiteralPath $vsWhere)) { throw 'Can MSVC C++ Build Tools de chay test nay.' }
    $vsInstall = & $vsWhere -latest -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
    if (-not $vsInstall) { throw 'Chua cai MSVC C++ Build Tools.' }
    Import-Module (Join-Path $vsInstall 'Common7/Tools/Microsoft.VisualStudio.DevShell.dll')
    Enter-VsDevShell -VsInstallPath $vsInstall -SkipAutomaticLocation -DevCmdArguments '-arch=x64 -host_arch=x64' | Out-Null
}

$iotTestBuild = Join-Path ([IO.Path]::GetTempPath()) 'codex-smartwasteiot-logic-tests'
New-Item -ItemType Directory -Path $iotTestBuild -Force | Out-Null
$iotTestSource = Join-Path $PSScriptRoot 'iot_logic_test.cpp'
$iotTestExe = Join-Path $iotTestBuild 'iot_logic_test.exe'
$iotTestObj = Join-Path $iotTestBuild 'iot_logic_test.obj'
& cl.exe /nologo /std:c++17 /EHsc /W4 /WX "/Fe:$iotTestExe" "/Fo:$iotTestObj" $iotTestSource /link /INCREMENTAL:NO
if ($LASTEXITCODE -ne 0) { throw 'Bien dich test that bai.' }
& $iotTestExe
if ($LASTEXITCODE -ne 0) { throw 'Logic test that bai.' }
