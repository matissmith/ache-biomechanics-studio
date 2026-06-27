#!/bin/bash
echo "=== Verificando herramientas ==="
echo ""
echo "gh CLI: $(which gh 2>/dev/null || echo 'NO')"
echo "HF CLI: $(which huggingface-cli 2>/dev/null || echo 'NO')"
echo "netlify: $(which netlify 2>/dev/null || echo 'NO')"
echo ""
echo "=== Python ==="
echo "$(python3 --version 2>/dev/null)"
python3 -c "import huggingface_hub; print('huggingface_hub: OK')" 2>/dev/null || echo "huggingface_hub: NO"
echo ""
echo "=== GitHub CLI autenticado ==="
gh auth status 2>&1 | head -3
echo ""
echo "=== HF Token ==="
cat ~/.huggingface/token 2>/dev/null || echo "No encontrado"
echo ""
echo "Presioná Enter para salir..."
read
