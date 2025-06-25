import os
import json

# Mock xbmc
class xbmc:
    LOGINFO = 1
    LOGERROR = 3
    
    @staticmethod
    def log(msg, level=1):
        print(f"[KODI LOG] {msg}")
    
    @staticmethod
    def executebuiltin(cmd):
        print(f"[KODI CMD] {cmd}")

# Mock xbmcgui
class Dialog:
    def notification(self, title, message):
        print(f"[NOTIFICATION] {title}: {message}")
    
    def ok(self, title, message):
        print(f"[DIALOG OK] {title}\n{message}")
        return True
    
    def input(self, prompt, type=0):
        return input(f"[INPUT] {prompt}: ")

class ListItem:
    def __init__(self, label=""):
        self.label = label
        self.art = {}
        self.info = {}
    
    def setArt(self, art):
        self.art = art
    
    def setInfo(self, type, info):
        self.info = info

class xbmcgui:
    Dialog = Dialog
    ListItem = ListItem
    INPUT_ALPHANUM = 1

# Mock xbmcaddon
class Addon:
    def __init__(self):
        self.settings = {}
        self.info = {
            'name': 'MAL Tracker Test',
            'version': '1.0.0',
            'icon': 'icon.png',
            'fanart': 'fanart.jpg',
            'profile': './test_profile'
        }
    
    def getSetting(self, key):
        return self.settings.get(key, '')
    
    def setSetting(self, key, value):
        self.settings[key] = value
        print(f"[SETTING] {key} = {value}")
    
    def getAddonInfo(self, key):
        return self.info.get(key, '')

class xbmcaddon:
    Addon = Addon

# Mock xbmcvfs
class xbmcvfs:
    @staticmethod
    def translatePath(path):
        return path.replace('special://', './test_')
    
    @staticmethod
    def exists(path):
        return os.path.exists(path)
    
    @staticmethod
    def mkdirs(path):
        os.makedirs(path, exist_ok=True)

# Mock xbmcplugin
class xbmcplugin:
    SORT_METHOD_TITLE = 1
    SORT_METHOD_VIDEO_RATING = 2
    SORT_METHOD_PLAYCOUNT = 3
    
    @staticmethod
    def setPluginCategory(handle, category):
        print(f"[CATEGORY] {category}")
    
    @staticmethod
    def setContent(handle, content):
        print(f"[CONTENT] {content}")
    
    @staticmethod
    def addDirectoryItem(handle, url, listitem, isFolder):
        print(f"[ITEM] {listitem.label} -> {url}")
        return True
    
    @staticmethod
    def endOfDirectory(handle):
        print("[END DIRECTORY]")
    
    @staticmethod
    def addSortMethod(handle, method):
        pass