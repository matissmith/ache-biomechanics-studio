#!/bin/bash
cd "$(dirname "$0")"
rm -f .git/index.lock 2>/dev/null
git add docs/index.html
git commit -m "feat: conectar web con Streamlit Cloud URL"
git push origin main
echo ""
echo "✅ Web actualizada y publicada."
echo ""
echo "🌐 Link de la web: https://matissmith.github.io/ache-biomechanics-studio/"
echo ""
read -p "Presioná Enter para salir..."
