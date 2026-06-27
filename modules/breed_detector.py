"""
from typing import Optional
Ache Innovation — Módulo de Detección de Raza

Usa la Inference API de Hugging Face (HTTP) para clasificar razas caninas.
No carga modelos localmente — no requiere torch ni transformers.
"""

import io
import time
from typing import List, Dict

import requests
import streamlit as st
from PIL import Image


# Modelo público de clasificación ImageNet (incluye razas caninas).
MODEL_ID = "google/vit-base-patch16-224"
HF_API_URL = f"https://api-inference.huggingface.co/models/{MODEL_ID}"

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


def detect_breed(image: Image.Image) -> List[Dict]:
    """
    Detecta la raza del perro en una imagen usando la HF Inference API.
    No carga ningún modelo localmente.

    Returns:
        Lista de dicts con label y score.
    """
    # Convertir imagen a bytes JPEG para enviar por HTTP
    img = image.convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    img_bytes = buf.getvalue()

    headers = {"Content-Type": "application/octet-stream"}
    token = _get_hf_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    # Si el modelo está dormido en HF, esperamos hasta 30 seg
    for attempt in range(3):
        resp = requests.post(HF_API_URL, headers=headers, data=img_bytes, timeout=30)

        if resp.status_code == 200:
            break
        if resp.status_code == 503:
            # Modelo cargando — HF devuelve {"estimated_time": N}
            wait = min(resp.json().get("estimated_time", 10), 20)
            time.sleep(wait)
            continue
        raise RuntimeError(
            f"HF Inference API error {resp.status_code}: {resp.text[:200]}"
        )
    else:
        raise RuntimeError("El modelo de detección de raza tardó demasiado en cargar. Intente de nuevo en unos segundos.")

    raw = resp.json()

    # La API devuelve [{"label": "...", "score": 0.99}, ...]
    normalized = []
    for r in raw:
        label = _clean_label(str(r.get("label", "")))
        score = float(r.get("score", 0.0))
        if label:
            normalized.append({"label": label, "score": score})

    dog_results = [r for r in normalized if _looks_like_dog_breed(r["label"])]
    return dog_results[:5] if dog_results else normalized[:5]


def format_breed_name(raw_label: str) -> str:
    """Convierte labels del modelo a nombre legible."""
    clean = _clean_label(raw_label)

    # Normalizaciones útiles para que matchee con la base de datos morfológica.
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
