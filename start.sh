#!/bin/bash

echo "========================================"
echo "VISIÓN Y PUBLICIDAD - Sistema de Gestión & Diseño"
echo "========================================"
echo ""
if [ -f "venv/bin/activate" ]; then
    echo "Activando entorno virtual..."
    source venv/bin/activate
fi
echo ""
echo "Iniciando aplicación..."
PORT="${PORT:-8501}"
streamlit run app.py --server.port $PORT --server.address 0.0.0.0

