"""
Ache Innovation — Módulo de Detección de Raza

Usa modelos públicos de clasificación de imágenes de Hugging Face.
El modelo anterior del MVP dejó de estar disponible, por eso este módulo
prueba modelos estables y normaliza las etiquetas a nombres de raza.
"""

from typing import List, Dict

import streamlit as st
from PIL import Image


MODEL_CANDIDATES = [
    # ImageNet: incluye muchas razas caninas comunes, incluyendo Golden Retriever y Labrador.
    "google/vit-base-patch16-224",
    "microsoft/resnet-50",
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
    # Algunos modelos devuelven labels tipo "golden retriever, Golden Retriever".
    label = label.split(",")[0].strip()
    label = label.replace("_", " " ).replace("-", " ")
    return " ".join(label.split())


def _looks_like_dog_breed(label: str) -> bool:
    low = _clean_label(label).lower()
    return any(k in low for k in DOG_KEYWORDS)


@st.cache_resource(show_spinner="Cargando modelo de detección de raza...")
def _load_model():
    """Carga un clasificador público. Prueba varios por si uno falla."""
    from transformers import pipeline

    errors = []
    for model_name in MODEL_CANDIDATES:
        try:
            clf = pipeline(
                "image-classification",
                model=model_name,
                top_k=10,
            )
            return clf, model_name
        except Exception as exc:  # pragma: no cover - depende de red/cache local
            errors.append(f"{model_name}: {exc}")

    raise RuntimeError(
        "No se pudo cargar ningún modelo público de detección de raza. "
        + " | ".join(errors)
    )


def detect_breed(image: Image.Image) -> List[Dict]:
    """
    Detecta la raza del perro en una imagen.

    Returns:
        Lista de dicts con label y score.
    """
    classifier, _model_name = _load_model()
    img = image.convert("RGB")
    results = classifier(img)

    # Transformers a veces devuelve [[...]] dependiendo de versión/top_k.
    if results and isinstance(results[0], list):
        results = results[0]

    normalized = []
    for r in results:
        label = _clean_label(str(r.get("label", "")))
        score = float(r.get("score", 0.0))
        if label:
            normalized.append({"label": label, "score": score})

    dog_results = [r for r in normalized if _looks_like_dog_breed(r["label"])]

    # Si el modelo devuelve mezcla de objetos/animales, priorizamos razas de perro.
    # Si no encontró keywords caninas, devolvemos lo mejor que haya para que la UI no explote.
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
