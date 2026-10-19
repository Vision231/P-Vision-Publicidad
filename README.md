# Visión Publicidad - Sistema de Gestión

## 📋 Archivos del Proyecto

- `app.py` - Aplicación principal (funciona correctamente)
- `requirements.txt` - Dependencias de Python
- `.streamlit/config.toml` - Configuración de Streamlit
- `.gitignore` - Archivos a ignorar en Git
- `start.bat` - Script de inicio para Windows
- `start.sh` - Script de inicio para Linux/Mac

## ☁️ CÓMO DESPLEGAR 24/7 (Paso a Paso)

### Opción 1: Streamlit Cloud (GRATIS - Recomendado)

#### Paso 1: Crear cuenta en GitHub
1. Vaya a [github.com](https://github.com) y regístrese
2. Cree un nuevo repositorio llamado `vision-publicidad`
3. Hágalo **PÚBLICO** (requerido para despliegue gratuito)

#### Paso 2: Subir archivos a GitHub
En la carpeta del proyecto, ejecute estos comandos:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/vision-publicidad.git
git push -u origin main
```

**IMPORTANTE:** Reemplace `TU_USUARIO` con su nombre de usuario de GitHub.

#### Paso 3: Desplegar en Streamlit Cloud
1. Vaya a [share.streamlit.io](https://share.streamlit.io)
2. Haga clic en "Sign up" o "Log in with GitHub"
3. Haga clic en "New app"
4. Seleccione su repositorio `vision-publicidad`
5. Configure:
   - **Repository**: `TU_USUARIO/vision-publicidad`
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **Python version**: `3.10`
6. Haga clic en "Deploy"

#### Paso 4: Esperar y usar
- Espere 2-5 minutos mientras se despliega
- Su aplicación estará disponible en: `https://vision-publicidad.streamlit.app`
- **¡Listo! Funciona 24/7 sin su computadora**

---

### Opción 2: Render (GRATIS - Alternativa)

#### Paso 1: Subir a GitHub
(Same as above - subir archivos a GitHub)

#### Paso 2: Desplegar en Render
1. Vaya a [render.com](https://render.com) y regístrese
2. Haga clic en "New +" → "Web Service"
3. Conecte su repositorio de GitHub
4. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
5. Haga clic en "Create Web Service"

---

### Opción 3: Railway (GRATIS - Alternativa)

#### Paso 1: Instalar Railway CLI
```bash
npm install -g @railway/cli
```

#### Paso 2: Desplegar
```bash
railway login
railway init
railway up
```

---

## 🚀 Ejecutar Localmente (Solo para pruebas)

### Windows:
```bash
start.bat
```

### Linux/Mac:
```bash
chmod +x start.sh
./start.sh
```

### Manual:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
streamlit run app.py
```

---

## ✅ Verificación

El archivo `app.py` ha sido verificado y **funciona correctamente** sin errores de sintaxis.

---

## 📞 Soporte

- Streamlit Cloud: [docs.streamlit.io](https://docs.streamlit.io)
- GitHub: [github.com](https://github.com)
