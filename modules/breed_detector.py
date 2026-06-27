"""
Ache Innovation — Módulo de Detección de Raza

Usa la Inference API de Hugging Face (HTTP) para clasificar razas caninas.
No carga modelos localmente — no requiere torch ni transformers.

Estrategia de fallback:
  1. Modelo primario: google/vit-base-patch16-224 (ImageNet, incluye 120 razas caninas)
  2. Modelo secundario: microsoft/resnet-50 (siempre activo en HF, mismo formato de respuesta)
  Si ambos fallan, lanza excepción para que el caller muestre el mensaje apropiado.
"""

import io
import time
from typing import List, Dict, Optional

import requests
import streamlit as st
from PIL import Image


# ── Modelos en cascada ────────────────────────────────────────────────────────
_HF_BASE = "https://api-inference.huggingface.co/models"
_MODELS = [
    f"{_HF_BASE}/google/vit-base-patch16-224",   # primario — 120 razas caninas en ImageNet
    f"{_HF_BASE}/microsoft/resnet-50",            # secundario — siempre activo en HF free tier
]

DOG_KEYWORDS = {
    "retriever", "labrador", "golden", "terrier", "spaniel", "poodle",
    "shepherd", "collie", "husky", "malamute", "beagle", "boxer",
    "bulldog", "mastiff", "rottweiler", "doberman", "chihuahua",
    "dachshund", "pug", "corgi", "schnauzer", "setter", "pointer",
    "hound", "whippet", "greyhound", "samoyed", "papillon", "malinois",
    "kelpie", "weimaraner", "vizsla", "newfoundland", "st bernard",
}


def _clean_label(label: str) -> str:
    label = label.split(",")[0].strip()
    label = label.replace("_", " ").replace("-", " ")
    return " ".join(label.split())


def _looks_like_dog_breed(label: str) -> bool:
    low = _clean_label(label).lower()
    return any(k in low for k in DOG_KEYWORDS)


def _get_hf_token() -> Optional[str]:
    """Lee el token de Hugging Face desde Streamlit secrets (opcional)."""
    try:
        return st.secrets.get("HF_TOKEN")
    except Exception:
        return None


def _query_model(url: str, img_bytes: bytes, headers: dict) -> Optional[List[Dict]]:
    """
    Intenta consultar un modelo HF.
    Retorna lista de resultados normalizados, o None si el modelo no responde.
    Timeout reducido a 15s para no hacer esperar al usuario.
    """
    for attempt in range(2):
        try:
            resp = requests.post(url, headers=headers, data=img_bytes, timeout=15)
        except requests.exceptions.Timeout:
            return None
        except requests.exceptions.ConnectionError:
            return None

        if resp.status_code == 200:
            raw = resp.json()
            if not isinstance(raw, list):
                return None
            normalized = []
            for r in raw:
                label = _clean_label(str(r.get("label", "")))
                score = float(r.get("score", 0.0))
                if label:
                    normalized.append({"label": label, "score": score})
            return normalized if normalized else None

        if resp.status_code == 503:
            # Modelo cargando — esperamos máximo 8 segundos antes de pasar al siguiente
            try:
                wait = min(resp.json().get("estimated_time", 5), 8)
            except Exception:
                wait = 5
            time.sleep(wait)
            continue

        # Cualquier otro error (401, 404, 429, 5xx) → no reintentar este modelo
        return None

    return None


def detect_breed(image: Image.Image) -> List[Dict]:
    """
    Detecta la raza del perro en una imagen usando la HF Inference API.
    Prueba el modelo primario y, si falla, el secundario.
    No carga ningún modelo localmente.

    Returns:
        Lista de dicts con label y score (puede estar vacía si no detecta razas).
    Raises:
        RuntimeError si ningún modelo responde.
    """
    img = image.convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    img_bytes = buf.getvalue()

    headers = {"Content-Type": "application/octet-stream"}
    token = _get_hf_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    last_error: Optional[str] = None
    for model_url in _MODELS:
        normalized = _query_model(model_url, img_bytes, headers)
        if normalized is not None:
            dog_results = [r for r in normalized if _looks_like_dog_breed(r["label"])]
            return dog_results[:5] if dog_results else normalized[:5]
        last_error = model_url

    raise RuntimeError(
        "El servicio de detección no está disponible en este momento. "
        "Podés ingresar la raza manualmente."
    )


def format_breed_name(raw_label: str) -> str:
    """Convierte labels del modelo a nombre legible."""
    clean = _clean_label(raw_label)

    aliases = {
        "labrador retriever": "Labrador Retriever",
        "golden retriever": "Golden Retriever",
        "german shepherd": "German Shepherd",
        "german shepherd dog": "German Shepherd",
        "siberian husky": "Siberian Husky",
        "border collie": "Border Collie",
        "french bulldog": "French Bulldog",
        "english bulldog": "Bulldog",
        "rottweiler": "Rottweiler",
        "beagle": "Beagle",
        "boxer": "Boxer",
        "pug": "Pug",
        "chihuahua": "Chihuahua",
        "dachshund": "Dachshund",
        "standard poodle": "Poodle",
        "toy poodle": "Poodle",
        "miniature poodle": "Poodle",
    }
    return aliases.get(clean.lower(), clean.title())
