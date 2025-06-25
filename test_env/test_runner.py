#!/usr/bin/env python3
import sys
import os

# Agregar mocks al path
sys.path.insert(0, os.path.dirname(__file__))

# Importar mocks
from xbmc_mocks import xbmc, xbmcgui, xbmcaddon, xbmcvfs, xbmcplugin

# Inyectar mocks en sys.modules
sys.modules['xbmc'] = xbmc
sys.modules['xbmcgui'] = xbmcgui
sys.modules['xbmcaddon'] = xbmcaddon
sys.modules['xbmcvfs'] = xbmcvfs
sys.modules['xbmcplugin'] = xbmcplugin

# Agregar addon al path
addon_path = os.path.join(os.path.dirname(__file__), '..', 'plugin.video.maltracker')
sys.path.insert(0, addon_path)

def test_auth():
    print("=== TESTING AUTH ===")
    
    # Configurar credenciales de prueba
    addon = xbmcaddon.Addon()
    addon.setSetting('client_id', 'test_client_id')
    addon.setSetting('client_secret', 'test_client_secret')
    
    # Importar módulos del addon
    from resources import auth, config
    
    print(f"Client ID: {config.CLIENT_ID}")
    print(f"Redirect URI: {config.REDIRECT_URI}")
    
    # Probar generación PKCE
    verifier, challenge = auth.generate_pkce_pair()
    print(f"PKCE Verifier: {verifier[:20]}...")
    print(f"PKCE Challenge: {challenge[:20]}...")

def test_config_import():
    print("\n=== TESTING CONFIG IMPORT ===")
    
    from resources import config_importer
    
    # Simular texto de configuración
    test_config = """
    MyAnimeList:
    ClientId
    193940c0c1b8fbfe241038e97a1903c4
    ClientSecret
    6e7dec7dc528519b839e7aead9540b4bea66b6689f9f934faa938883b20e088e
    
    AniList:
    ID
    27906
    Secret
    TVOKgDSgf3ga2chdI2pxJ2M6mjrOcsNOjdubwyNw
    """
    
    # Mock del input dialog
    original_input = xbmcgui.Dialog.input
    xbmcgui.Dialog.input = lambda self, prompt, type=0: test_config
    
    config_importer.import_config_from_text()
    
    # Restaurar
    xbmcgui.Dialog.input = original_input

if __name__ == "__main__":
    test_auth()
    test_config_import()
    print("\n=== TESTS COMPLETED ===")