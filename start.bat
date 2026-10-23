@echo off
echo ========================================
echo VISIÓN Y PUBLICIDAD - Sistema de Gestión & Diseño
echo ========================================
echo.
echo Activando entorno virtual...
call venv\Scripts\activate
echo.
echo Instalando dependencias...
pip install -r requirements.txt
echo.
echo Iniciando aplicación...
echo La aplicación se abrirá en su navegador.
echo Presione Ctrl+C para detener.
echo.
streamlit run app.py
pause
