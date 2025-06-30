# 📦 Instalación del Repositorio MAL Tracker

## 🎯 Método 1: Repositorio Automático (Recomendado)

### Paso 1: Descargar repositorio
```
https://github.com/username/MAL-Tracker-For-Kodi/releases/latest/download/repository.maltracker.zip
```

### Paso 2: Instalar en Kodi
1. **Kodi** → **Addons** → **Instalar desde archivo ZIP**
2. Seleccionar `repository.maltracker.zip`
3. Esperar notificación "Addon activado"

### Paso 3: Instalar MAL Tracker
1. **Addons** → **Instalar desde repositorio**
2. **MAL Tracker Repository**
3. **Addons de video** → **MAL Tracker**
4. **Instalar**

---

## 🔧 Método 2: Manual

### Descargar addon directamente
```
https://github.com/username/MAL-Tracker-For-Kodi/releases/latest/download/plugin.video.maltracker.zip
```

1. **Kodi** → **Addons** → **Instalar desde archivo ZIP**
2. Seleccionar `plugin.video.maltracker.zip`

---

## 🌐 Método 3: GitHub Pages (URL directa)

### Agregar fuente de repositorio
1. **Kodi** → **Configuración** → **Addons**
2. **Gestionar fuentes** → **Agregar fuente**
3. **URL**: `https://username.github.io/MAL-Tracker-For-Kodi/`
4. **Nombre**: `MAL Tracker Repo`
5. **OK**

### Instalar repositorio
1. **Addons** → **Instalar desde archivo ZIP**
2. **MAL Tracker Repo** → `repository.maltracker.zip`

---

## ⚙️ Configuración Post-Instalación

### 1. Configurar servicios
- **Menú principal** → **Configurar Servicios**
- **AniList** (recomendado): https://anilist.co/settings/developer
- **MAL** (opcional): https://myanimelist.net/apiconfig

### 2. Activar streaming experto (opcional)
- **Configuración** → **Addons** → **MAL Tracker**
- **Cambiar nivel a "Experto"**
- **Activar "Sitios de Streaming Experto"**

---

## 🔄 Actualizaciones

### Automáticas (con repositorio)
- Kodi actualiza automáticamente desde el repositorio

### Manuales
- Descargar nueva versión y reinstalar ZIP

---

## 🆘 Solución de Problemas

### Error "Dependencias no satisfechas"
```bash
# Instalar manualmente:
# 1. script.module.requests
# 2. script.module.html5lib (opcional)
```

### Error "Addon no se puede instalar"
1. Verificar versión de Kodi (mínimo 19.0)
2. Limpiar cache: **Configuración** → **Sistema** → **Addons** → **Limpiar cache**

### Problemas de autenticación
1. Verificar Client ID en configuración
2. Usar autenticación manual si automática falla
3. Revisar logs: **Configuración** → **Sistema** → **Logging**

---

## 📋 Estructura del Repositorio

```
repository.maltracker/
├── addon.xml              # Configuración del repositorio
├── icon.png              # Icono del repositorio  
└── fanart.jpg            # Fanart del repositorio

Archivos generados:
├── addons.xml            # Lista de addons disponibles
├── addons.xml.md5        # Checksum de seguridad
├── plugin.video.maltracker.zip    # Addon principal
└── repository.maltracker.zip      # Repositorio
```