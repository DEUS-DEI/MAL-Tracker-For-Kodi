@echo off
setlocal
REM Detectar ruta absoluta del script
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

set "DIR=plugin.video.maltracker"
set "ZIP=plugin.video.maltracker.zip"
if exist %ZIP% del %ZIP%

REM Comprimir asegurando que la carpeta sea la raíz del ZIP
REM Si tienes PowerShell (Windows 10+), esto siempre funcionará:
powershell -Command "Compress-Archive -Path '%DIR%' -DestinationPath '%ZIP%' -Force"
if exist %ZIP% (
    echo Addon empaquetado en %ZIP% con la estructura correcta.
) else (
    echo Error: No se pudo crear el ZIP. Intenta comprimir manualmente la carpeta %DIR%.
)
endlocal
