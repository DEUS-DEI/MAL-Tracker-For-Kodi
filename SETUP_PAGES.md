# 🌐 Configurar GitHub Pages

## 📋 Pasos para habilitar GitHub Pages:

### 1. Configurar repositorio
1. Ve a **Settings** del repositorio
2. **Pages** (menú izquierdo)
3. **Source**: GitHub Actions
4. **Save**

### 2. Ejecutar workflow
1. **Actions** → **Deploy to GitHub Pages**
2. **Run workflow**
3. Esperar que complete

### 3. Verificar deployment
- URL: `https://username.github.io/MAL-Tracker-For-Kodi/`
- Archivos disponibles:
  - `addons.xml`
  - `addons.xml.md5`
  - `plugin.video.maltracker.zip`
  - `repository.maltracker.zip`

## 🔧 Configuración en addon.xml del repositorio

Actualizar URLs en `repository.maltracker/addon.xml`:

```xml
<info compressed="false">https://username.github.io/MAL-Tracker-For-Kodi/addons.xml</info>
<checksum>https://username.github.io/MAL-Tracker-For-Kodi/addons.xml.md5</checksum>
<datadir zip="true">https://username.github.io/MAL-Tracker-For-Kodi/</datadir>
```

## 🚀 Instalación para usuarios

### URL del repositorio:
```
https://username.github.io/MAL-Tracker-For-Kodi/repository.maltracker.zip
```

### En Kodi:
1. **Configuración** → **Addons** → **Gestionar fuentes**
2. **Agregar fuente**: `https://username.github.io/MAL-Tracker-For-Kodi/`
3. **Instalar desde ZIP** → Seleccionar fuente → `repository.maltracker.zip`