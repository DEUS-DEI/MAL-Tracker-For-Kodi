#!/usr/bin/env python3
"""
Script para crear repositorio de Kodi
Genera addons.xml y addons.xml.md5
"""

import os
import xml.etree.ElementTree as ET
import hashlib
import zipfile
import shutil

def create_addon_zip(addon_path, output_dir):
    """Crear ZIP del addon"""
    addon_name = os.path.basename(addon_path)
    zip_path = os.path.join(output_dir, f"{addon_name}.zip")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(addon_path):
            # Excluir archivos innecesarios
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git']]
            
            for file in files:
                if not file.endswith(('.pyc', '.log', '.tmp', '.bak')):
                    file_path = os.path.join(root, file)
                    arc_path = os.path.relpath(file_path, addon_path)
                    zipf.write(file_path, arc_path)
    
    return zip_path

def extract_addon_info(addon_xml_path):
    """Extraer información del addon.xml"""
    tree = ET.parse(addon_xml_path)
    root = tree.getroot()
    
    return {
        'id': root.get('id'),
        'version': root.get('version'),
        'xml': ET.tostring(root, encoding='unicode')
    }

def create_addons_xml(repo_dir):
    """Crear addons.xml"""
    addons_root = ET.Element('addons')
    
    # Buscar todos los addons
    for item in os.listdir(repo_dir):
        item_path = os.path.join(repo_dir, item)
        addon_xml = os.path.join(item_path, 'addon.xml')
        
        if os.path.isdir(item_path) and os.path.exists(addon_xml):
            # Leer addon.xml
            tree = ET.parse(addon_xml)
            addon_element = tree.getroot()
            addons_root.append(addon_element)
            
            # Crear ZIP del addon
            create_addon_zip(item_path, repo_dir)
    
    # Escribir addons.xml
    addons_xml_path = os.path.join(repo_dir, 'addons.xml')
    tree = ET.ElementTree(addons_root)
    tree.write(addons_xml_path, encoding='utf-8', xml_declaration=True)
    
    return addons_xml_path

def create_md5(file_path):
    """Crear archivo MD5"""
    with open(file_path, 'rb') as f:
        content = f.read()
    
    md5_hash = hashlib.md5(content).hexdigest()
    
    md5_path = file_path + '.md5'
    with open(md5_path, 'w') as f:
        f.write(md5_hash)
    
    return md5_path

def main():
    """Función principal"""
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("Creando repositorio de Kodi...")
    
    # Crear addons.xml
    addons_xml = create_addons_xml(repo_dir)
    print(f"✓ Creado: {addons_xml}")
    
    # Crear MD5
    md5_file = create_md5(addons_xml)
    print(f"✓ Creado: {md5_file}")
    
    # Crear ZIP del repositorio
    repo_zip = create_addon_zip('repository.maltracker', repo_dir)
    print(f"✓ Creado: {repo_zip}")
    
    print("\n🎉 Repositorio creado exitosamente!")
    print("\nArchivos generados:")
    print("- addons.xml")
    print("- addons.xml.md5") 
    print("- plugin.video.maltracker.zip")
    print("- repository.maltracker.zip")

if __name__ == '__main__':
    main()