#!/usr/bin/env python3
"""
MAL Tracker Setup Script
Helps configure the addon with proper settings
"""

import os
import shutil
import zipfile

def setup_addon():
    """Setup the MAL Tracker addon"""
    print("🎌 MAL Tracker for Kodi - Setup")
    print("=" * 40)
    
    # Check if we're in the right directory
    addon_dir = "plugin.video.maltracker"
    if not os.path.exists(addon_dir):
        print("❌ Error: plugin.video.maltracker directory not found!")
        print("   Make sure you're running this from the MAL-Tracker-For-Kodi directory")
        return False
    
    print("✅ Found addon directory")
    
    # Check addon structure
    required_files = [
        "addon.xml",
        "main.py", 
        "resources/settings.xml"
    ]
    
    for file_path in required_files:
        full_path = os.path.join(addon_dir, file_path)
        if os.path.exists(full_path):
            print(f"✅ Found {file_path}")
        else:
            print(f"❌ Missing {file_path}")
            return False
    
    # Create zip package
    zip_name = "plugin.video.maltracker.zip"
    print(f"\n📦 Creating {zip_name}...")
    
    if os.path.exists(zip_name):
        os.remove(zip_name)
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(addon_dir):
            # Skip __pycache__ and .pyc files
            dirs[:] = [d for d in dirs if d != '__pycache__']
            files = [f for f in files if not f.endswith('.pyc')]
            
            for file in files:
                file_path = os.path.join(root, file)
                arc_path = os.path.relpath(file_path, '.')
                zipf.write(file_path, arc_path)
                print(f"   Added: {arc_path}")
    
    print(f"✅ Created {zip_name}")
    
    # Installation instructions
    print("\n📋 INSTALLATION INSTRUCTIONS:")
    print("=" * 40)
    print("1. Copy plugin.video.maltracker.zip to your Kodi device")
    print("2. In Kodi, go to: Settings → Add-ons → Install from zip file")
    print("3. Select the plugin.video.maltracker.zip file")
    print("4. After installation, go to: Settings → Add-ons → My add-ons → Video add-ons → MAL Tracker")
    print("5. Click 'Configure' and set up your MAL API credentials:")
    print("   - Get credentials at: https://myanimelist.net/apiconfig")
    print("   - Create a new app and copy the Client ID")
    print("   - Client Secret is optional for most operations")
    
    print("\n🎯 QUICK START:")
    print("=" * 40)
    print("1. Install the addon")
    print("2. Go to Videos → Add-ons → MAL Tracker")
    print("3. Use 'Buscar anime (básico)' to search without authentication")
    print("4. Use 'Top anime' and 'Anime de temporada' for browsing")
    print("5. Configure API credentials later for personal list features")
    
    print("\n✅ Setup completed successfully!")
    return True

if __name__ == "__main__":
    setup_addon()