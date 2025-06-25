#!/usr/bin/env python3
import sys
import os

# Setup mocks
sys.path.insert(0, os.path.dirname(__file__))
from xbmc_mocks import xbmc, xbmcgui, xbmcaddon, xbmcvfs, xbmcplugin

sys.modules['xbmc'] = xbmc
sys.modules['xbmcgui'] = xbmcgui
sys.modules['xbmcaddon'] = xbmcaddon
sys.modules['xbmcvfs'] = xbmcvfs
sys.modules['xbmcplugin'] = xbmcplugin

# Setup addon path
addon_path = os.path.join(os.path.dirname(__file__), '..', 'plugin.video.maltracker')
sys.path.insert(0, addon_path)

# Mock sys.argv for plugin
sys.argv = ['plugin://plugin.video.maltracker/', '1', '']

def test_main_menu():
    print("=== TESTING MAIN MENU ===")
    from main import show_main_menu
    show_main_menu()

def test_import_config():
    print("\n=== TESTING CONFIG IMPORT ===")
    
    # Mock input with config text
    test_config = """MyAnimeList:
ClientId
193940c0c1b8fbfe241038e97a1903c4
ClientSecret
6e7dec7dc528519b839e7aead9540b4bea66b6689f9f934faa938883b20e088e

AniList:
ID
27906
Secret
TVOKgDSgf3ga2chdI2pxJ2M6mjrOcsNOjdubwyNw"""
    
    original_input = xbmcgui.Dialog.input
    xbmcgui.Dialog.input = lambda self, prompt, type=0: test_config
    
    from resources import config_importer
    config_importer.import_config_from_text()
    
    xbmcgui.Dialog.input = original_input

def test_unified_tracker():
    print("\n=== TESTING UNIFIED TRACKER ===")
    from resources import unified_tracker
    
    service = unified_tracker.get_active_service()
    print(f"Active service: {service}")
    
    is_auth = unified_tracker.is_authenticated()
    print(f"Is authenticated: {is_auth}")

def test_router():
    print("\n=== TESTING ROUTER ===")
    from main import router
    
    # Test different routes
    print("Testing main menu:")
    router('')
    
    print("\nTesting import config:")
    router('action=import_config')

if __name__ == "__main__":
    test_main_menu()
    test_import_config()
    test_unified_tracker()
    test_router()
    print("\n=== FULL ADDON TEST COMPLETED ===")