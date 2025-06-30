# 🔧 Habilitar GitHub Pages

## ⚠️ Error: Pages no habilitado

Si ves este error:
```
Get Pages site failed. Please verify that the repository has Pages enabled
```

## 📋 Solución manual:

### 1. Ir a Settings del repositorio
- **Settings** → **Pages** (menú izquierdo)

### 2. Configurar Source
- **Source**: Deploy from a branch
- **Branch**: gh-pages (o main)
- **Folder**: / (root)
- **Save**

### 3. Cambiar a GitHub Actions
- **Source**: GitHub Actions
- **Save**

### 4. Ejecutar workflow
- **Actions** → **Deploy to GitHub Pages**
- **Run workflow**

## 🔄 Alternativa: Workflow simplificado

Si persiste el error, usar este workflow:

```yaml
name: Simple Pages Deploy

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.x'
    - name: Build
      run: python create_repo.py
    - name: Deploy
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./
```

## ✅ Verificar funcionamiento

URL final: `https://DEUS-DEI.github.io/MAL-Tracker-For-Kodi/`