#!/bin/bash
# Push de guia_quirurgica.py personalizada
cd "$(dirname "$0")"
rm -f .git/index.lock 2>/dev/null
git config user.email "matiassmith98@gmail.com"
git config user.name "matiassmith"
git add modules/guia_quirurgica.py
git commit -m "feat: guía clínica personalizada al caso activo

- Banner rico con todos los datos del caso (raza, peso, extremidad, nivel,
  causa, BCS, medidas del muñón, specs de la prótesis, peso máx. prótesis)
- Alertas automáticas inmediatas: oncológica, BCS alto, BCS 7
- Tab Biomecánica: auto-selecciona Torácico/Pelviano desde extremidad del caso;
  muestra nota personalizada para el nivel de amputación registrado (1-7)
- Tab Clasificación: auto-clasifica A/B/C/D y pre-llena checkboxes desde
  causa, BCS, nivel, medidas del muñón
- Tab Diseño protésico: recomendaciones específicas por talla (toy/pequeño/
  mediano/grande/gigante): material, pared socket, liner, pie, suspensión;
  estimación por peso si no hay breed_info; resumen del diseño paramétrico actual
- Tab Clínico: auto-selecciona causa desde el caso
- helpers _auto_clasificar(), _TALLA_SPECS, _NIVEL_NOTAS"
git push origin main
echo ""
git log --oneline -3
echo ""
echo "✅ Guía personalizada en producción."
read -p "Presioná Enter para salir..."
