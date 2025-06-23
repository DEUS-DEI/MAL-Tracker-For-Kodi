@echo off
echo Building MAL Tracker Addon for Kodi...

set ADDON_NAME=plugin.video.maltracker
set BUILD_DIR=build
set ZIP_NAME=%ADDON_NAME%-1.0.0.zip

if exist %BUILD_DIR% rmdir /s /q %BUILD_DIR%
mkdir %BUILD_DIR%
mkdir %BUILD_DIR%\%ADDON_NAME%

echo Copying addon files...
xcopy /s /e /q %ADDON_NAME%\*.* %BUILD_DIR%\%ADDON_NAME%\

echo Excluding unnecessary files...
del /q %BUILD_DIR%\%ADDON_NAME%\*.pyc 2>nul
del /q %BUILD_DIR%\%ADDON_NAME%\resources\*.pyc 2>nul
rmdir /s /q %BUILD_DIR%\%ADDON_NAME%\__pycache__ 2>nul
rmdir /s /q %BUILD_DIR%\%ADDON_NAME%\resources\__pycache__ 2>nul

echo Creating ZIP package...
cd %BUILD_DIR%
powershell -command "Compress-Archive -Path '%ADDON_NAME%' -DestinationPath '../%ZIP_NAME%' -Force"
cd ..

echo Cleaning up...
rmdir /s /q %BUILD_DIR%

echo.
echo Addon package created: %ZIP_NAME%
echo Ready for installation in Kodi!
pause