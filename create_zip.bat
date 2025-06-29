@echo off
echo Creating MAL Tracker addon package...

if exist plugin.video.maltracker.zip del plugin.video.maltracker.zip

powershell -command "Compress-Archive -Path '.\plugin.video.maltracker\*' -DestinationPath '.\plugin.video.maltracker.zip' -Force"

if exist plugin.video.maltracker.zip (
    echo ✅ Successfully created plugin.video.maltracker.zip
    echo.
    echo 📋 INSTALLATION INSTRUCTIONS:
    echo 1. Copy plugin.video.maltracker.zip to your Kodi device
    echo 2. In Kodi: Settings → Add-ons → Install from zip file
    echo 3. Select the plugin.video.maltracker.zip file
    echo 4. Configure your MAL API credentials in addon settings
    echo.
    echo 🎯 QUICK START:
    echo - Use 'Buscar anime (básico)' to search without authentication
    echo - Use 'Top anime' and 'Anime de temporada' for browsing
    echo - Get API credentials at: https://myanimelist.net/apiconfig
) else (
    echo ❌ Failed to create zip file
)

pause