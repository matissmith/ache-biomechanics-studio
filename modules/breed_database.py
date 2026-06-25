"""
Ache Innovation — Base de Datos Morfológica por Raza
Datos basados en estándares de raza (FCI, AKC, KC).

Campos por raza:
  peso_min / peso_max        → kg
  altura_min / altura_max    → cm (altura a la cruz)
  miembro_delantero_cm       → longitud estimada miembro anterior (cm)
  miembro_trasero_cm         → longitud estimada miembro posterior (cm)
  circunf_miembro_cm         → circunferencia promedio del miembro (cm)
  talla                      → 'toy' | 'pequeño' | 'mediano' | 'grande' | 'gigante'
"""

from typing import Optional, Dict

# ─────────────────────────────────────────────────────────────────────────────
# BASE DE DATOS (extensible — agregar razas a medida que se acumulan casos)
# ─────────────────────────────────────────────────────────────────────────────
BREED_DATABASE: Dict[str, Dict] = {

    # ── GIGANTES ──────────────────────────────────────────────────────────────
    "Great Dane": {
        "peso_min": 50, "peso_max": 90,
        "altura_min": 71, "altura_max": 86,
        "miembro_delantero_cm": 40, "miembro_trasero_cm": 45,
        "circunf_miembro_cm": 18, "talla": "gigante"
    },
    "Saint Bernard": {
        "peso_min": 64, "peso_max": 120,
        "altura_min": 65, "altura_max": 90,
        "miembro_delantero_cm": 42, "miembro_trasero_cm": 46,
        "circunf_miembro_cm": 20, "talla": "gigante"
    },
    "Mastiff": {
        "peso_min": 54, "peso_max": 100,
        "altura_min": 68, "altura_max": 78,
        "miembro_delantero_cm": 38, "miembro_trasero_cm": 43,
        "circunf_miembro_cm": 19, "talla": "gigante"
    },
    "Rottweiler": {
        "peso_min": 35, "peso_max": 60,
        "altura_min": 56, "altura_max": 69,
        "miembro_delantero_cm": 33, "miembro_trasero_cm": 37,
        "circunf_miembro_cm": 17, "talla": "gigante"
    },
    "Bernese Mountain Dog": {
        "peso_min": 36, "peso_max": 50,
        "altura_min": 58, "altura_max": 70,
        "miembro_delantero_cm": 34, "miembro_trasero_cm": 38,
        "circunf_miembro_cm": 16, "talla": "gigante"
    },

    # ── GRANDES ───────────────────────────────────────────────────────────────
    "Labrador Retriever": {
        "peso_min": 25, "peso_max": 36,
        "altura_min": 54, "altura_max": 62,
        "miembro_delantero_cm": 30, "miembro_trasero_cm": 34,
        "circunf_miembro_cm": 14, "talla": "grande"
    },
    "Golden Retriever": {
        "peso_min": 25, "peso_max": 34,
        "altura_min": 54, "altura_max": 61,
        "miembro_delantero_cm": 29, "miembro_trasero_cm": 33,
        "circunf_miembro_cm": 14, "talla": "grande"
    },
    "German Shepherd": {
        "peso_min": 22, "peso_max": 40,
        "altura_min": 55, "altura_max": 65,
        "miembro_delantero_cm": 31, "miembro_trasero_cm": 35,
        "circunf_miembro_cm": 14, "talla": "grande"
    },
    "Siberian Husky": {
        "peso_min": 16, "peso_max": 27,
        "altura_min": 50, "altura_max": 60,
        "miembro_delantero_cm": 28, "miembro_trasero_cm": 32,
        "circunf_miembro_cm": 13, "talla": "grande"
    },
    "Alaskan Malamute": {
        "peso_min": 34, "peso_max": 43,
        "altura_min": 58, "altura_max": 64,
        "miembro_delantero_cm": 32, "miembro_trasero_cm": 36,
        "circunf_miembro_cm": 15, "talla": "grande"
    },
    "Boxer": {
        "peso_min": 25, "peso_max": 35,
        "altura_min": 53, "altura_max": 63,
        "miembro_delantero_cm": 28, "miembro_trasero_cm": 32,
        "circunf_miembro_cm": 14, "talla": "grande"
    },
    "Doberman": {
        "peso_min": 30, "peso_max": 45,
        "altura_min": 61, "altura_max": 72,
        "miembro_delantero_cm": 35, "miembro_trasero_cm": 39,
        "circunf_miembro_cm": 14, "talla": "grande"
    },
    "Weimaraner": {
        "peso_min": 23, "peso_max": 36,
        "altura_min": 56, "altura_max": 69,
        "miembro_delantero_cm": 32, "miembro_trasero_cm": 36,
        "circunf_miembro_cm": 14, "talla": "grande"
    },
    "Border Collie": {
        "peso_min": 14, "peso_max": 20,
        "altura_min": 46, "altura_max": 56,
        "miembro_delantero_cm": 26, "miembro_trasero_cm": 29,
        "circunf_miembro_cm": 11, "talla": "grande"
    },
    "Australian Shepherd": {
        "peso_min": 16, "peso_max": 32,
        "altura_min": 46, "altura_max": 58,
        "miembro_delantero_cm": 27, "miembro_trasero_cm": 30,
        "circunf_miembro_cm": 12, "talla": "grande"
    },
    "Standard Poodle": {
        "peso_min": 18, "peso_max": 32,
        "altura_min": 45, "altura_max": 60,
        "miembro_delantero_cm": 28, "miembro_trasero_cm": 31,
        "circunf_miembro_cm": 11, "talla": "grande"
    },
    "Belgian Malinois": {
        "peso_min": 18, "peso_max": 30,
        "altura_min": 56, "altura_max": 66,
        "miembro_delantero_cm": 30, "miembro_trasero_cm": 34,
        "circunf_miembro_cm": 12, "talla": "grande"
    },
    "Dalmatian": {
        "peso_min": 20, "peso_max": 32,
        "altura_min": 48, "altura_max": 61,
        "miembro_delantero_cm": 28, "miembro_trasero_cm": 32,
        "circunf_miembro_cm": 12, "talla": "grande"
    },
    "Irish Setter": {
        "peso_min": 25, "peso_max": 32,
        "altura_min": 60, "altura_max": 67,
        "miembro_delantero_cm": 32, "miembro_trasero_cm": 36,
        "circunf_miembro_cm": 12, "talla": "grande"
    },

    # ── MEDIANOS ──────────────────────────────────────────────────────────────
    "Bulldog": {
        "peso_min": 18, "peso_max": 25,
        "altura_min": 30, "altura_max": 40,
        "miembro_delantero_cm": 17, "miembro_trasero_cm": 20,
        "circunf_miembro_cm": 13, "talla": "mediano"
    },
    "Cocker Spaniel": {
        "peso_min": 7, "peso_max": 14,
        "altura_min": 35, "altura_max": 43,
        "miembro_delantero_cm": 19, "miembro_trasero_cm": 22,
        "circunf_miembro_cm": 9, "talla": "mediano"
    },
    "Beagle": {
        "peso_min": 9, "peso_max": 14,
        "altura_min": 33, "altura_max": 38,
        "miembro_delantero_cm": 18, "miembro_trasero_cm": 21,
        "circunf_miembro_cm": 9, "talla": "mediano"
    },
    "Shiba Inu": {
        "peso_min": 7, "peso_max": 11,
        "altura_min": 34, "altura_max": 41,
        "miembro_delantero_cm": 19, "miembro_trasero_cm": 22,
        "circunf_miembro_cm": 9, "talla": "mediano"
    },
    "Shar Pei": {
        "peso_min": 18, "peso_max": 25,
        "altura_min": 44, "altura_max": 51,
        "miembro_delantero_cm": 23, "miembro_trasero_cm": 26,
        "circunf_miembro_cm": 12, "talla": "mediano"
    },
    "Basenji": {
        "peso_min": 9, "peso_max": 12,
        "altura_min": 40, "altura_max": 43,
        "miembro_delantero_cm": 21, "miembro_trasero_cm": 24,
        "circunf_miembro_cm": 9, "talla": "mediano"
    },
    "Whippet": {
        "peso_min": 9, "peso_max": 14,
        "altura_min": 44, "altura_max": 56,
        "miembro_delantero_cm": 25, "miembro_trasero_cm": 28,
        "circunf_miembro_cm": 9, "talla": "mediano"
    },
    "Staffordshire Bull Terrier": {
        "peso_min": 11, "peso_max": 17,
        "altura_min": 36, "altura_max": 41,
        "miembro_delantero_cm": 19, "miembro_trasero_cm": 22,
        "circunf_miembro_cm": 11, "talla": "mediano"
    },
    "American Pit Bull Terrier": {
        "peso_min": 14, "peso_max": 27,
        "altura_min": 43, "altura_max": 53,
        "miembro_delantero_cm": 24, "miembro_trasero_cm": 27,
        "circunf_miembro_cm": 13, "talla": "mediano"
    },
    "Vizsla": {
        "peso_min": 18, "peso_max": 29,
        "altura_min": 53, "altura_max": 64,
        "miembro_delantero_cm": 30, "miembro_trasero_cm": 34,
        "circunf_miembro_cm": 12, "talla": "mediano"
    },

    # ── PEQUEÑOS ──────────────────────────────────────────────────────────────
    "French Bulldog": {
        "peso_min": 8, "peso_max": 14,
        "altura_min": 28, "altura_max": 33,
        "miembro_delantero_cm": 14, "miembro_trasero_cm": 16,
        "circunf_miembro_cm": 9, "talla": "pequeño"
    },
    "Pug": {
        "peso_min": 6, "peso_max": 9,
        "altura_min": 25, "altura_max": 30,
        "miembro_delantero_cm": 13, "miembro_trasero_cm": 15,
        "circunf_miembro_cm": 8, "talla": "pequeño"
    },
    "Shih Tzu": {
        "peso_min": 4, "peso_max": 8,
        "altura_min": 20, "altura_max": 28,
        "miembro_delantero_cm": 12, "miembro_trasero_cm": 13,
        "circunf_miembro_cm": 7, "talla": "pequeño"
    },
    "Miniature Schnauzer": {
        "peso_min": 5, "peso_max": 8,
        "altura_min": 30, "altura_max": 36,
        "miembro_delantero_cm": 16, "miembro_trasero_cm": 18,
        "circunf_miembro_cm": 7, "talla": "pequeño"
    },
    "Cavalier King Charles Spaniel": {
        "peso_min": 5, "peso_max": 8,
        "altura_min": 30, "altura_max": 33,
        "miembro_delantero_cm": 15, "miembro_trasero_cm": 17,
        "circunf_miembro_cm": 7, "talla": "pequeño"
    },
    "Dachshund": {
        "peso_min": 4, "peso_max": 9,
        "altura_min": 20, "altura_max": 27,
        "miembro_delantero_cm": 9, "miembro_trasero_cm": 10,
        "circunf_miembro_cm": 6, "talla": "pequeño"
    },
    "Bichon Frise": {
        "peso_min": 3, "peso_max": 7,
        "altura_min": 23, "altura_max": 30,
        "miembro_delantero_cm": 13, "miembro_trasero_cm": 14,
        "circunf_miembro_cm": 6, "talla": "pequeño"
    },
    "Jack Russell Terrier": {
        "peso_min": 5, "peso_max": 8,
        "altura_min": 25, "altura_max": 38,
        "miembro_delantero_cm": 16, "miembro_trasero_cm": 18,
        "circunf_miembro_cm": 7, "talla": "pequeño"
    },
    "Miniature Poodle": {
        "peso_min": 4, "peso_max": 7,
        "altura_min": 28, "altura_max": 35,
        "miembro_delantero_cm": 15, "miembro_trasero_cm": 17,
        "circunf_miembro_cm": 7, "talla": "pequeño"
    },
    "Corgi": {
        "peso_min": 10, "peso_max": 14,
        "altura_min": 25, "altura_max": 30,
        "miembro_delantero_cm": 11, "miembro_trasero_cm": 12,
        "circunf_miembro_cm": 8, "talla": "pequeño"
    },

    # ── TOY ───────────────────────────────────────────────────────────────────
    "Chihuahua": {
        "peso_min": 1.5, "peso_max": 3,
        "altura_min": 15, "altura_max": 23,
        "miembro_delantero_cm": 9, "miembro_trasero_cm": 10,
        "circunf_miembro_cm": 4, "talla": "toy"
    },
    "Yorkshire Terrier": {
        "peso_min": 1.5, "peso_max": 3.2,
        "altura_min": 17, "altura_max": 23,
        "miembro_delantero_cm": 10, "miembro_trasero_cm": 11,
        "circunf_miembro_cm": 4, "talla": "toy"
    },
    "Toy Poodle": {
        "peso_min": 2, "peso_max": 4,
        "altura_min": 20, "altura_max": 28,
        "miembro_delantero_cm": 12, "miembro_trasero_cm": 13,
        "circunf_miembro_cm": 5, "talla": "toy"
    },
    "Maltese": {
        "peso_min": 1.5, "peso_max": 3,
        "altura_min": 20, "altura_max": 25,
        "miembro_delantero_cm": 10, "miembro_trasero_cm": 11,
        "circunf_miembro_cm": 4, "talla": "toy"
    },
    "Pomeranian": {
        "peso_min": 1.4, "peso_max": 3.2,
        "altura_min": 18, "altura_max": 24,
        "miembro_delantero_cm": 10, "miembro_trasero_cm": 11,
        "circunf_miembro_cm": 4, "talla": "toy"
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Funciones de consulta
# ─────────────────────────────────────────────────────────────────────────────

def get_breed_info(breed_name: str) -> Optional[Dict]:
    """
    Busca la info morfológica de una raza.
    Acepta nombres con variantes de mayúsculas/minúsculas y espacios.
    Retorna None si no está en la base de datos.
    """
    # Búsqueda exacta
    if breed_name in BREED_DATABASE:
        return BREED_DATABASE[breed_name]

    # Búsqueda case-insensitive
    lower = breed_name.lower().strip()
    for key, val in BREED_DATABASE.items():
        if key.lower() == lower:
            return val

    # Búsqueda parcial (la raza detectada puede tener nombre con variante)
    for key, val in BREED_DATABASE.items():
        key_words = set(key.lower().split())
        input_words = set(lower.split())
        if key_words & input_words:  # hay palabras en común
            return val

    return None


def get_all_breed_names() -> list:
    """Lista de todas las razas en la base de datos."""
    return sorted(BREED_DATABASE.keys())


def estimate_limb_from_weight(weight_kg: float, limb: str = "delantera") -> float:
    """
    Estimación genérica de longitud del miembro a partir del peso,
    para cuando la raza no está en la base de datos.
    Basado en regresión aproximada de datos FCI.
    """
    # Relación empírica aproximada: longitud_cm ≈ 7.5 * peso_kg^0.38
    import math
    base = 7.5 * (weight_kg ** 0.38)
    if "trasera" in limb.lower() or "posterior" in limb.lower():
        return round(base * 1.12, 1)
    return round(base, 1)
