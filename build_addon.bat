@echo off
echo Building MAL Tracker Addon for Kodi...

set ADDON_NAME=plugin.video.maltracker
set ZIP_NAME=%ADDON_NAME%-1.0.0.zip

echo Excluding unnecessary files...
if exist %ADDON_NAME%\*.pyc del /q %ADDON_NAME%\*.pyc
if exist %ADDON_NAME%\resources\*.pyc del /q %ADDON_NAME%\resources\*.pyc
if exist %ADDON_NAME%\__pycache__ rmdir /s /q %ADDON_NAME%\__pycache__
if exist %ADDON_NAME%\resources\__pycache__ rmdir /s /q %ADDON_NAME%\resources\__pycache__

echo Creating ZIP package...
powershell -command "Compress-Archive -Path '%ADDON_NAME%' -DestinationPath '%ZIP_NAME%' -Force"

echo.
echo Addon package created: %ZIP_NAME%
echo Ready for installation in Kodi!
pause