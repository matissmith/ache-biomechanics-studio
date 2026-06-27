#!/bin/bash
# Ache Innovation — Limpieza general del proyecto
# Ejecutar una sola vez. Después de correr, mover este script a 90_Archivo también.

BASE="$(cd "$(dirname "$0")/../../../.."; pwd)"
CLOUD="$(dirname "$0")"

echo "========================================"
echo "  Ache Innovation — Limpieza del proyecto"
echo "========================================"
echo ""

# ── 1. Eliminar scripts one-time del repo cloud ───────────────────
echo "[ 1/4 ] Eliminando scripts obsoletos del repo cloud..."
cd "$CLOUD"
rm -f FIX_Y_PUSH.command
rm -f PUSH_FIX_NAV.command
rm -f ACTIVAR_PAGES.command
rm -f HACER_PUBLICO_Y_PAGES.command
rm -f SUBIR_A_GITHUB.command
rm -f PUBLICAR_WEB.command
rm -f PUSH_FIXES_DETECTOR.command
echo "  ✅ Scripts one-time eliminados del repo cloud"

# ── 2. Eliminar backups en ache_innovation/modules ────────────────
echo ""
echo "[ 2/4 ] Eliminando archivos .backup* en ache_innovation/modules..."
LOCAL="$BASE/01_Software/ache_biomechanics_studio/ache_innovation/modules"
rm -f "$LOCAL/"*.backup*
rm -f "$LOCAL/"*_backup*
echo "  ✅ Backups eliminados"

# ── 3. Eliminar CHECK_TOOLS.command de la raíz ───────────────────
echo ""
echo "[ 3/4 ] Eliminando CHECK_TOOLS.command obsoleto de la raíz..."
rm -f "$BASE/CHECK_TOOLS.command"
echo "  ✅ CHECK_TOOLS.command raíz eliminado"

# ── 4. Commit y push en el repo cloud ────────────────────────────
echo ""
echo "[ 4/4 ] Commiteando limpieza en git..."
cd "$CLOUD"
rm -f .git/index.lock 2>/dev/null
git config user.email "matiassmith98@gmail.com"
git config user.name "matiassmith"

# Agregar LIMPIAR_PROYECTO.command también para trackearlo brevemente
git add -A
git commit -m "chore: limpieza general — eliminar scripts one-time y obsoletos

Scripts eliminados del repo (ya cumplieron su función):
- FIX_Y_PUSH.command (fix puntual packages.txt)
- PUSH_FIX_NAV.command (fix puntual nav)
- ACTIVAR_PAGES.command (GitHub Pages ya activo)
- HACER_PUBLICO_Y_PAGES.command (ya hecho)
- SUBIR_A_GITHUB.command (fix puntual torch)
- PUBLICAR_WEB.command (reemplazado por ACTUALIZAR_WEB)
- PUSH_FIXES_DETECTOR.command (fix puntual del 26/06)

Todos los scripts históricos están respaldados en 90_Archivo/Comandos_Obsoletos/."

git push origin main

echo ""
echo "========================================"
echo "  ✅ Limpieza completada y pusheada."
echo ""
echo "  Scripts activos que quedan en el repo:"
echo "  - ACTUALIZAR_WEB.command  (actualiza web en GitHub Pages)"
echo "  - CHECK_TOOLS.command     (verifica herramientas dev)"
echo "  - INSTALAR_Y_DEPLOYAR.command"
echo "  - SETUP_RAPIDO.command"
echo "  - iniciar_con_tunel.command"
echo "========================================"
echo ""
read -p "Presioná Enter para salir..."
