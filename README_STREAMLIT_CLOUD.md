# Ache Biomechanics Studio — Deploy en Streamlit Community Cloud

App principal: `app.py`

## Qué subir a GitHub
Subir esta carpeta del software, pero NO subir:
- `env/`
- `ache_env/`
- `.streamlit/secrets.toml`
- `data/ache.db` si contiene casos reales
- backups `*.backup*`

El archivo `.gitignore` ya deja esto protegido.

## Archivos importantes
- `app.py`: aplicación Streamlit.
- `requirements.txt`: dependencias Python para Streamlit Cloud.
- `packages.txt`: dependencias del sistema; incluye `openscad` para generar STL.
- `assets/`: logos y guía.
- `modules/`: lógica del software.
- `cad_templates/`: templates OpenSCAD.

## Secrets en Streamlit Cloud
En Streamlit Cloud > App settings > Secrets cargar una variable:

```toml
APP_PASSWORD = "TU_PASSWORD_DE_DEMO"
```

No subir `.streamlit/secrets.toml` a GitHub.

## Deploy
1. Crear repo en GitHub, idealmente privado al principio.
2. Subir esta carpeta.
3. Entrar a Streamlit Community Cloud.
4. Create app.
5. Elegir el repo.
6. Main file path: `app.py`.
7. Agregar Secrets.
8. Deploy.

## Nota de estabilidad
Streamlit Community Cloud es ideal para demo gratuita. Puede dormir la app o tardar en despertar. Para una demo comercial/LinkedIn seria, luego conviene VPS o hosting pago.
