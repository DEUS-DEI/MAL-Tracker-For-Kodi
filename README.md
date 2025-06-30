# MAL Tracker for Kodi

[![Build Status](https://github.com/username/MAL-Tracker-For-Kodi/workflows/Build%20MAL%20Tracker%20Addon/badge.svg)](https://github.com/username/MAL-Tracker-For-Kodi/actions)
[![Release](https://img.shields.io/github/v/release/username/MAL-Tracker-For-Kodi)](https://github.com/username/MAL-Tracker-For-Kodi/releases)

Addon avanzado para Kodi que integra MyAnimeList, AniList y múltiples sitios de streaming de anime.

## 🎬 Características

- **🔄 Sistema Híbrido**: AniList como principal, MAL como fallback
- **▶️ Auto-reproducción**: Avance automático de episodios
- **🔍 Scrapers Avanzados**: AnimeFLV y JKanime con técnicas profesionales
- **🔓 Streaming Experto**: 16 sitios alternativos (configuración oculta)
- **💾 Backup Completo**: Incluye tokens y configuraciones
- **🤖 OAuth Múltiple**: Automático, manual y app auxiliar

## 📦 Instalación

### Método 1: Release Automático
1. Ve a [Releases](https://github.com/username/MAL-Tracker-For-Kodi/releases)
2. Descarga `plugin.video.maltracker-X.X.X.zip`
3. En Kodi: Addons → Instalar desde archivo ZIP

### Método 2: Build Manual
1. Haz clic en [Actions](https://github.com/username/MAL-Tracker-For-Kodi/actions)
2. Ejecuta "Manual Build"
3. Descarga el artifact generado

## ⚙️ Configuración

1. **Configurar Servicios**: Menú → Configurar Servicios
2. **AniList (Recomendado)**: https://anilist.co/settings/developer
3. **MAL (Opcional)**: https://myanimelist.net/apiconfig
4. **Streaming Experto**: Configuración → Experto → Activar

## 🚀 GitHub Actions

Este proyecto incluye 3 workflows automáticos:

### 1. Build Automático (`build-addon.yml`)
- **Trigger**: Push a main/master
- **Función**: Crea ZIP automáticamente
- **Artifact**: `plugin.video.maltracker.zip`

### 2. Release Automático (`release.yml`)
- **Trigger**: Tags `v*` (ej: `v1.0.0`)
- **Función**: Release con changelog
- **Archivo**: `plugin.video.maltracker-X.X.X.zip`

### 3. Build Manual (`manual-build.yml`)
- **Trigger**: Manual desde Actions
- **Opciones**: Con/sin assets, nombre custom
- **Función**: Build personalizado

## 🔧 Desarrollo

```bash
# Clonar repositorio
git clone https://github.com/username/MAL-Tracker-For-Kodi.git

# Crear release
git tag v1.0.0
git push origin v1.0.0

# Build local (Windows)
package.bat

# Build local (Linux/Mac)
cd plugin.video.maltracker
zip -r ../plugin.video.maltracker.zip . -x "*.pyc" "__pycache__/*"
```

## 📋 Dependencias

Solo dependencias oficiales de Kodi:
- `script.module.requests`
- `script.module.html5lib` (opcional)
- `script.module.pyaes` (opcional)

## 🤝 Contribuir

1. Fork el proyecto
2. Crea feature branch (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push branch (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

MIT License - ver [LICENSE](LICENSE) para detalles.

## ⚠️ Disclaimer

Este addon no aloja ni distribuye contenido. Solo proporciona enlaces a sitios externos. Úsalo bajo tu propia responsabilidad.