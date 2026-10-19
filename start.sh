#!/bin/bash

echo "========================================"
echo "Visión Publicidad - Sistema de Gestión"
echo "========================================"
echo ""
echo "Activando entorno virtual..."
source venv/bin/activate
echo ""
echo "Instalando dependencias..."
pip install -r requirements.txt
echo ""
echo "Iniciando aplicación..."
echo "La aplicación se abrirá en su navegador."
echo "Presione Ctrl+C para detener."
echo ""
streamlit run app.py
