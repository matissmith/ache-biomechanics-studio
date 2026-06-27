#!/bin/bash
set -e
echo "========================================"
echo "  Ache Innovation — Deploy Automático"
echo "========================================"
echo ""

REPO_DIR="$(dirname "$0")"
cd "$REPO_DIR"

# ── 1. Verificar Homebrew ──────────────────────────────────────────
echo "[ 1/5 ] Verificando Homebrew..."
if ! command -v brew &>/dev/null; then
  echo "  Instalando Homebrew (puede tardar 2-3 min)..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  # Agregar al PATH para la sesión actual
  eval "$(/opt/homebrew/bin/brew shellenv)" 2>/dev/null || eval "$(/usr/local/bin/brew shellenv)" 2>/dev/null || true
else
  echo "  Homebrew: OK"
fi

# ── 2. Instalar gh CLI ─────────────────────────────────────────────
echo ""
echo "[ 2/5 ] Verificando GitHub CLI (gh)..."
if ! command -v gh &>/dev/null; then
  echo "  Instalando gh..."
  brew install gh
else
  echo "  gh: OK ($(gh --version | head -1))"
fi

# ── 3. Instalar huggingface_hub ────────────────────────────────────
echo ""
echo "[ 3/5 ] Verificando huggingface_hub..."
if ! python3 -c "import huggingface_hub" &>/dev/null; then
  echo "  Instalando huggingface_hub..."
  pip3 install huggingface_hub --break-system-packages 2>/dev/null || pip3 install huggingface_hub
else
  echo "  huggingface_hub: OK"
fi

# ── 4. Login GitHub ────────────────────────────────────────────────
echo ""
echo "[ 4/5 ] Verificando autenticación GitHub..."
if ! gh auth status &>/dev/null; then
  echo "  Se abrirá el navegador para autenticarte en GitHub."
  echo "  Iniciá sesión con tu cuenta de GitHub (matissmith)."
  gh auth login --web --git-protocol ssh
else
  echo "  GitHub: ya autenticado"
  gh auth status 2>&1 | head -2
fi

# ── 5. Resultado ───────────────────────────────────────────────────
echo ""
echo "========================================"
echo "  ✅ Herramientas listas"
echo "========================================"
echo ""
echo "Herramientas instaladas:"
command -v gh &>/dev/null && echo "  gh: $(gh --version | head -1)"
command -v brew &>/dev/null && echo "  brew: OK"
python3 -c "import huggingface_hub; print('  huggingface_hub: OK')" 2>/dev/null
echo ""
echo "Avisale a Claude que este script terminó. ✓"
echo ""
read -p "Presioná Enter para salir..."
