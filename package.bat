@echo off
echo Creating MAL Tracker addon package...

if exist plugin.video.maltracker.zip del plugin.video.maltracker.zip

powershell Compress-Archive -Path plugin.video.maltracker -DestinationPath plugin.video.maltracker.zip -Force

if exist plugin.video.maltracker.zip (
    echo Success! Created plugin.video.maltracker.zip
) else (
    echo Failed to create zip file
)

pause