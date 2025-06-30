@echo off
echo Building MAL Tracker Repository...

python create_repo.py

if exist addons.xml (
    echo ✓ Repository built successfully!
    echo.
    echo Generated files:
    echo - addons.xml
    echo - addons.xml.md5
    echo - plugin.video.maltracker.zip
    echo - repository.maltracker.zip
    echo.
    echo Ready for distribution!
) else (
    echo ✗ Failed to build repository
)

pause