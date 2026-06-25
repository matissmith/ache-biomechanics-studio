#!/bin/bash
# Ache Biomechanics Studio — Iniciar con túnel público Cloudflare
# Levanta Streamlit + expone la URL y actualiza el HTML de la web

APP_DIR="/Users/matia/Documents/Ache Innovation/01_Software/ache_biomechanics_studio/ache_innovation"
HTML_BOVINOS="/Users/matia/Documents/Ache Innovation/03_Animales_Productivos/Bovinos/Ache_Bovinos/ache-innovation.html"
HTML_SHARE="/Users/matia/Documents/Ache Innovation/03_Animales_Productivos/Bovinos/Ache_Bovinos/ache_innovation_SHARE.html"
HTML_MAIN="/Users/matia/Documents/Ache Innovation/02_Web_Institucional/ache-innovation-claude.html"
CF="/tmp/cloudflared"
PORT=8501

clear
echo ""
echo "  ╔══════════════════════════════════════════╗"
echo "  ║   Ache Biomechanics Studio — Iniciando  ║"
echo "  ╚══════════════════════════════════════════╝"
echo ""

# ── 1. Levantar Streamlit ────────────────────────────────────────
echo "  [1/3] Iniciando Streamlit app..."
cd "$APP_DIR"

# Verificar que el entorno existe
if [ ! -f "$APP_DIR/env/bin/activate" ]; then
    echo "  ⚠️  Entorno virtual no encontrado. Instalando..."
    python3 -m venv env
    source env/bin/activate
    pip install -q -r requirements.txt
else
    source env/bin/activate
fi

# Matar instancias previas en el puerto y cloudflared residual
lsof -ti:$PORT | xargs kill -9 2>/dev/null
pkill -f "cloudflared.*tunnel" 2>/dev/null
sleep 1

# Iniciar Streamlit con nohup — sobrevive al cierre del terminal
nohup streamlit run app.py \
    --server.port=$PORT \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false \
    > /tmp/ache_streamlit.log 2>&1 &
STREAMLIT_PID=$!
disown $STREAMLIT_PID

echo "  ✓ Streamlit iniciando (PID: $STREAMLIT_PID)..."
echo "    Esperando que esté listo..."

# Esperar a que Streamlit responda
for i in $(seq 1 30); do
    if curl -s "http://localhost:$PORT" > /dev/null 2>&1; then
        break
    fi
    sleep 1
done
echo "  ✓ Streamlit activo en http://localhost:$PORT"
echo ""

# ── 2. Verificar / descargar cloudflared ────────────────────────
echo "  [2/3] Configurando túnel Cloudflare..."
if [ ! -f "$CF" ] || [ ! -x "$CF" ]; then
    echo "  Descargando cloudflared..."
    ARCH=$(uname -m)
    [ "$ARCH" = "arm64" ] && BIN="cloudflared-darwin-arm64" || BIN="cloudflared-darwin-amd64"
    curl -L -s --max-time 90 \
        "https://github.com/cloudflare/cloudflared/releases/latest/download/$BIN" \
        -o "$CF"
    chmod +x "$CF"
    xattr -d com.apple.quarantine "$CF" 2>/dev/null
    echo "  ✓ cloudflared listo"
fi
echo ""

# ── 3. Crear túnel y capturar URL ───────────────────────────────
echo "  [3/3] Creando túnel público..."
echo "  (Puede tardar ~20 segundos)"
echo ""

TUNNEL_LOG="/tmp/ache_tunnel.log"
URL_FILE="/tmp/ache_tunnel_url.txt"
> "$TUNNEL_LOG"
rm -f "$URL_FILE"

# ── Función para actualizar un HTML ─────────────────────────────
update_html() {
    local FILE="$1"
    local U="$2"
    [ -f "$FILE" ] || return
    sed -i '' "s|src=\"https://[^\"]*\.trycloudflare\.com[^\"]*\"|src=\"${U}/?embed=1\"|g" "$FILE"
    sed -i '' "s|src=\"http://localhost:${PORT}[^\"]*\"|src=\"${U}/?embed=1\"|g" "$FILE"
    sed -i '' "s|href=\"https://[^\"]*\.trycloudflare\.com[^\"]*\"|href=\"${U}\"|g" "$FILE"
    sed -i '' "s|href=\"http://localhost:${PORT}[^\"]*\"|href=\"${U}\"|g" "$FILE"
    sed -i '' "s|const STUDIO_URL = 'https://[^']*\.trycloudflare\.com';|const STUDIO_URL = '${U}';|g" "$FILE"
    sed -i '' "s|const STUDIO_URL = 'http://localhost:${PORT}';|const STUDIO_URL = '${U}';|g" "$FILE"
}

# Correr cloudflared en PIPE (fuerza line-buffering).
# El while loop NO hace break — sigue leyendo para mantener cloudflared vivo.
# Cuando encuentra la URL la guarda en URL_FILE; el main loop la lee y continúa.
"$CF" tunnel --url "http://localhost:$PORT" 2>&1 | while IFS= read -r line; do
    echo "$line" >> "$TUNNEL_LOG"
    if [ ! -f "$URL_FILE" ]; then
        FOUND=$(echo "$line" | grep -oE 'https://[a-zA-Z0-9-]+\.trycloudflare\.com' | head -1)
        [ -n "$FOUND" ] && echo "$FOUND" > "$URL_FILE"
    fi
done &
PIPE_PID=$!

# Main loop: espera URL_FILE hasta 60 s
URL=""
for i in $(seq 1 60); do
    if [ -f "$URL_FILE" ]; then
        URL=$(cat "$URL_FILE")
        break
    fi
    printf "  ⏳  Esperando túnel... %d/60\r" "$i"
    sleep 1
done
echo ""

if [ -n "$URL" ]; then
    echo "  ✅  ¡STUDIO ACTIVO!"
    echo ""
    echo "      $URL"
    echo ""

    update_html "$HTML_BOVINOS" "$URL"
    update_html "$HTML_SHARE"   "$URL"
    update_html "$HTML_MAIN"    "$URL"

    echo "  ✓ URL inyectada en los 3 HTMLs"
    echo "  📋 Copiando al portapapeles..."
    echo "$URL" | pbcopy
    echo ""

    # ── 4. Auto-deploy a Netlify ──────────────────────────────────────
    echo "  [4/4] Desplegando a Netlify (browser headless)..."
    DEPLOY_PY="/tmp/ache_netlify_deploy.py"
    NETLIFY_RESULT="/tmp/ache_netlify_result.txt"
    rm -f "$NETLIFY_RESULT"

    cat > "$DEPLOY_PY" << 'PYEOF'
import asyncio, sys, re, subprocess
FILE = sys.argv[1]
OUT  = sys.argv[2]
SKIP=["screenshot-proxy","app","blog","docs","www","api","sdk","status",
      "answers","community","cli","client-network-manager","example"]

def extract(content):
    s=set()
    for sub in re.findall(r'https://([a-z0-9][a-z0-9-]+)\.netlify\.app', content):
        if not any(x==sub or sub.startswith(x+"-") for x in SKIP): s.add(sub)
    return s

async def deploy():
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        open(OUT,'w').write("NO_PLAYWRIGHT"); return
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://app.netlify.com/drop", wait_until="domcontentloaded")
        await asyncio.sleep(4)
        pre = extract(await page.content())
        try:
            fi = page.locator('input[type="file"]').first
            await fi.wait_for(state="attached", timeout=10000)
            await fi.set_input_files(FILE)
        except:
            try:
                async with page.expect_file_chooser(timeout=8000) as fc:
                    await page.get_by_text("browse to upload").click()
                f = await fc.value; await f.set_files(FILE)
            except Exception as e:
                open(OUT,'w').write(f"ERROR:{e}"); await browser.close(); return
        site_url=None
        for _ in range(60):
            await asyncio.sleep(3)
            post=extract(await page.content())
            new=post-pre
            if new: site_url=f"https://{next(iter(new))}.netlify.app"; break
            if ".netlify.app" in page.url and "app.netlify" not in page.url:
                m=re.search(r'https://([a-z0-9][a-z0-9-]+)\.netlify\.app',page.url)
                if m and m.group(1) not in SKIP: site_url=f"https://{m.group(1)}.netlify.app"; break
        await browser.close()
        open(OUT,'w').write(site_url or "TIMEOUT")
asyncio.run(deploy())
PYEOF

    python3 "$DEPLOY_PY" "$HTML_SHARE" "$NETLIFY_RESULT" 2>/dev/null
    NETLIFY_URL=$(cat "$NETLIFY_RESULT" 2>/dev/null)

    if [[ "$NETLIFY_URL" == https://* ]]; then
        echo "  ✅  Netlify actualizado:"
        echo ""
        echo "      $NETLIFY_URL"
        echo ""
        echo "$NETLIFY_URL" | pbcopy
        echo "  📋 Link Netlify copiado al portapapeles."
    elif [[ "$NETLIFY_URL" == "NO_PLAYWRIGHT" ]]; then
        echo "  ⚠️  Playwright no instalado. Deploy manual:"
        echo "      Doble clic en subir_pagina.command"
    else
        echo "  ⚠️  Deploy Netlify no completado. Usá subir_pagina.command manualmente."
    fi
    echo ""
else
    echo "  ⚠️  No se obtuvo URL en 60s. Studio local: http://localhost:$PORT"
fi

echo "  ╔══════════════════════════════════════════╗"
echo "  ║  ⚠️  No cierres esta ventana mientras    ║"
echo "  ║     el studio esté en uso.               ║"
echo "  ╚══════════════════════════════════════════╝"
echo ""

# Mantener el terminal abierto (Streamlit corre con nohup; el pipe mantiene el túnel)
wait $PIPE_PID
