#!/bin/bash
# ============================================================
# Ache Innovation — Script de Instalación para Mac
# Ejecutar UNA SOLA VEZ desde la carpeta del proyecto:
#   bash instalar_mac.sh
# ============================================================

set -e  # Detener si hay error

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║       Ache Innovation — Instalación          ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# ── 1. Verificar Python ─────────────────────────────────────
echo "→ Verificando Python 3..."
if ! command -v python3 &> /dev/null; then
    echo ""
    echo "❌ Python 3 no está instalado."
    echo "   Instalalo desde: https://www.python.org/downloads/"
    echo "   Descargá la versión más reciente para Mac y seguí el instalador."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "   ✅ Python $PYTHON_VERSION encontrado"

# ── 2. Crear entorno virtual ────────────────────────────────
echo ""
echo "→ Creando entorno virtual (ache_env)..."
python3 -m venv ache_env
echo "   ✅ Entorno creado"

# ── 3. Activar entorno ──────────────────────────────────────
echo ""
echo "→ Activando entorno virtual..."
source ache_env/bin/activate
echo "   ✅ Entorno activado"

# ── 4. Actualizar pip ───────────────────────────────────────
echo ""
echo "→ Actualizando pip..."
pip install --upgrade pip --quiet

# ── 5. Instalar dependencias ────────────────────────────────
echo ""
echo "→ Instalando librerías (puede tardar 5-10 minutos la primera vez)..."
echo "   Se va a descargar PyTorch (~500 MB) — necesitás internet."
echo ""
pip install -r requirements.txt

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║     ✅  INSTALACIÓN COMPLETADA               ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
echo "Para iniciar el software, ejecutá:"
echo ""
echo "   source ache_env/bin/activate && streamlit run app.py"
echo ""
echo "O simplemente ejecutá el archivo 'iniciar.sh':"
echo "   bash iniciar.sh"
echo ""

# ── 6. Crear script de inicio ───────────────────────────────
cat > iniciar.sh << 'EOF'
#!/bin/bash
# Ache Innovation — Iniciar el software
cd "$(dirname "$0")"
source ache_env/bin/activate
echo "Iniciando Ache Innovation..."
echo "Abrí http://localhost:8501 en tu navegador si no se abre solo."
streamlit run app.py
EOF

chmod +x iniciar.sh
echo "✅ Archivo 'iniciar.sh' creado — usalo para iniciar el software en el futuro."
echo ""
