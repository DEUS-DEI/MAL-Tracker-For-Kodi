# MAL-Tracker-For-Kodi

Addon para Kodi que permite consultar, buscar y actualizar tu lista de anime en MyAnimeList usando la API oficial.

## Instalación manual

1. Renombra la carpeta raíz a `plugin.video.maltracker` si es necesario.
2. Comprime la carpeta en un archivo ZIP:
   - **Linux/macOS:**
     ```bash
     zip -r plugin.video.maltracker.zip plugin.video.maltracker
     ```
   - **Windows:**
     - Haz clic derecho sobre la carpeta y selecciona "Enviar a > Carpeta comprimida (zip)".
3. Copia el ZIP a tu dispositivo con Kodi.
4. En Kodi, ve a **Add-ons > Instalar desde archivo ZIP** y selecciona el archivo.

## Scripts de empaquetado

### Linux/macOS
```bash
#!/bin/bash
set -e
DIR="plugin.video.maltracker"
ZIP="plugin.video.maltracker.zip"
rm -f $ZIP
cd ..
zip -r $ZIP $DIR
echo "Addon empaquetado en $ZIP"
```

### Windows (PowerShell)
```powershell
$dir = "plugin.video.maltracker"
$zip = "plugin.video.maltracker.zip"
if (Test-Path $zip) { Remove-Item $zip }
Compress-Archive -Path $dir -DestinationPath $zip
Write-Host "Addon empaquetado en $zip"
```

## Configuración de GitHub Actions para releases automáticos

Agrega este archivo como `.github/workflows/release.yml`:

```yaml
name: Build and Release Addon
on:
  push:
    tags:
      - 'v*'
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Empaquetar addon
        run: |
          zip -r plugin.video.maltracker.zip . -x '*.git*' '.github/*'
      - name: Crear release
        uses: softprops/action-gh-release@v2
        with:
          files: plugin.video.maltracker.zip
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

Esto generará un archivo ZIP listo para instalar en Kodi cada vez que crees un tag como `v1.0.0` en GitHub.

## Notas
- Recuerda registrar tu app en MyAnimeList y poner tu CLIENT_ID y CLIENT_SECRET en `resources/config.py`.
- El addon funciona en cualquier sistema donde Kodi soporte addons en Python (Windows, Linux, macOS, Android, etc.).