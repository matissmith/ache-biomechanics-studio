#!/bin/bash
# Ache Innovation — Iniciar el software
cd "$(dirname "$0")"
source env/bin/activate
echo "Iniciando Ache Innovation..."
echo "Abrí http://localhost:8501 en tu navegador si no se abre solo."
streamlit run app.py
