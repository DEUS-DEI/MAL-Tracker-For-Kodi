@echo off
set DIR=plugin.video.maltracker
set ZIP=plugin.video.maltracker.zip
if exist %ZIP% del %ZIP%
powershell -Command "Compress-Archive -Path %DIR% -DestinationPath %ZIP%"
echo Addon empaquetado en %ZIP%
