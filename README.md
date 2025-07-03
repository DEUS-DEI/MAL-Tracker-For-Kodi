# MAL Tracker for Kodi

[![Build Status](https://github.com/DEUS-DEI/MAL-Tracker-For-Kodi/workflows/Build%20Addon/badge.svg)](https://github.com/DEUS-DEI/MAL-Tracker-For-Kodi/actions)
[![Release](https://img.shields.io/github/v/release/DEUS-DEI/MAL-Tracker-For-Kodi)](https://github.com/DEUS-DEI/MAL-Tracker-For-Kodi/releases)

Addon avanzado para Kodi que integra MyAnimeList, AniList y múltiples sitios de streaming de anime.

## 🎬 Características

- **🔄 Sistema Híbrido**: AniList como principal, MAL como fallback
- **▶️ Auto-reproducción**: Avance automático de episodios
- **🔍 Scrapers Avanzados**: AnimeFLV y JKanime con técnicas profesionales
- **🔓 Streaming Experto**: 16 sitios alternativos (configuración oculta)
- **💾 Backup Completo**: Incluye tokens y configuraciones
- **🤖 OAuth Múltiple**: Automático, manual y app auxiliar

## 📦 Instalación

### Método 1: Repositorio (Recomendado)
1. Descargar [repository.maltracker.zip](https://github.com/DEUS-DEI/MAL-Tracker-For-Kodi/releases/latest/download/repository.maltracker.zip)
2. En Kodi: **Addons** → **Instalar desde archivo ZIP**
3. Seleccionar el archivo descargado
4. **Instalar desde repositorio** → **MAL Tracker Repository**

### Método 2: URL Directa
1. **Configuración** → **Administrador de archivos** → **Agregar fuente**
2. **URL**: `https://deus-dei.github.io/MAL-Tracker-For-Kodi/`
3. **Explorar** → Instalar `repository.maltracker.zip`

### Método 3: Addon Directo
1. Descargar [plugin.video.maltracker.zip](https://github.com/DEUS-DEI/MAL-Tracker-For-Kodi/releases/latest/download/plugin.video.maltracker.zip)
2. **Addons** → **Instalar desde archivo ZIP**

## ⚙️ Configuración

### 1. Configurar Servicios
- **Menú principal** → **Configurar Servicios**
- **AniList** (recomendado): https://anilist.co/settings/developer
- **MAL** (opcional): https://myanimelist.net/apiconfig

### 2. Activar Streaming Experto (Opcional)
- **Configuración** → **Addons** → **MAL Tracker**
- **Cambiar nivel a "Experto"**
- **Activar "Sitios de Streaming Experto"**

### 3. OAuth Automático
- El addon detecta automáticamente tokens existentes
- Soporte para múltiples métodos de autenticación
- Backup automático de configuraciones

## 🚀 Funcionalidades Avanzadas

### Sistema Híbrido
- **AniList** como servicio principal
- **MAL** como fallback automático
- **Sincronización** bidireccional
- **Detección inteligente** de anime

### Auto-Player
- **Reproducción continua** de episodios
- **Detección automática** de siguiente episodio
- **Control por gestos** y comandos de voz
- **Historial** de reproducción

### Scrapers Profesionales
- **AnimeFLV**: API + scraping HTML
- **JKanime**: AJAX + paginación
- **16 sitios adicionales** en modo experto
- **Extracción multi-fuente** de videos

## 🔧 Desarrollo

### Estructura del Proyecto
```
MAL-Tracker-For-Kodi/
├── plugin.video.maltracker/     # Addon principal
├── repository/                  # Repositorio Kodi
├── assets/                     # Ejemplos y referencias
└── .github/workflows/          # CI/CD automático
```

### Build Automático
- **Push a main** → Build automático
- **Releases** → Generación automática
- **GitHub Pages** → Deploy automático

### Dependencias
Solo dependencias oficiales de Kodi:
- `script.module.requests`
- `script.module.html5lib` (opcional)
- `script.module.pyaes` (opcional)

## 🌐 URLs Importantes

- **Repositorio**: https://deus-dei.github.io/MAL-Tracker-For-Kodi/
- **Releases**: https://github.com/DEUS-DEI/MAL-Tracker-For-Kodi/releases
- **Documentación**: https://deus-dei.github.io/MAL-Tracker-For-Kodi/README.md

## 🤝 Contribuir

1. Fork el proyecto
2. Crear feature branch (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push branch (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

MIT License - ver [LICENSE](LICENSE) para detalles.

## ⚠️ Disclaimer

Este addon no aloja ni distribuye contenido. Solo proporciona enlaces a sitios externos. Los usuarios son responsables del cumplimiento de las leyes locales de derechos de autor.

## 🆘 Soporte

- **Issues**: [GitHub Issues](https://github.com/DEUS-DEI/MAL-Tracker-For-Kodi/issues)
- **Documentación**: Incluida en el addon
- **Logs**: Configuración → Sistema → Logging

---

**Desarrollado con ❤️ para la comunidad de anime**