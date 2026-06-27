#!/bin/bash
echo "=== Setup Ache Innovation ==="
echo ""

# Detectar brew
BREW=""
if command -v brew &>/dev/null; then
  BREW="brew"
elif [ -f /opt/homebrew/bin/brew ]; then
  BREW="/opt/homebrew/bin/brew"
elif [ -f /usr/local/bin/brew ]; then
  BREW="/usr/local/bin/brew"
fi

if [ -z "$BREW" ]; then
  echo "Instalando Homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  [ -f /opt/homebrew/bin/brew ] && BREW="/opt/homebrew/bin/brew" || BREW="/usr/local/bin/brew"
else
  echo "Homebrew: OK"
fi

# Instalar gh
if ! command -v gh &>/dev/null; then
  echo "Instalando GitHub CLI..."
  $BREW install gh
else
  echo "GitHub CLI: OK"
fi

# Instalar huggingface_hub
if ! python3 -c "import huggingface_hub" &>/dev/null 2>&1; then
  echo "Instalando huggingface_hub..."
  pip3 install huggingface_hub 2>/dev/null || pip3 install --user huggingface_hub
else
  echo "huggingface_hub: OK"
fi

# Login GitHub (abre navegador)
if ! command -v gh &>/dev/null; then
  export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
fi
echo ""
echo "Autenticando GitHub (se abre el navegador)..."
gh auth login --web --git-protocol ssh

echo ""
echo "=== ✅ Todo listo. Avisale a Claude que terminó. ==="
read -p "Presioná Enter para salir..."
