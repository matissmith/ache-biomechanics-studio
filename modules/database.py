"""
Ache Innovation — Módulo de Base de Datos SQLite
Guarda y recupera casos de pacientes localmente.
"""

import sqlite3
import json
from pathlib import Path
from typing import Optional, List, Dict


def init_db(db_path: Path) -> None:
    """Crea las tablas si no existen."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS cases (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_perro    TEXT NOT NULL,
            nombre_dueno    TEXT NOT NULL,
            peso_actual     REAL,
            sexo            TEXT,
            edad            TEXT,
            extremidad      TEXT,
            estado          TEXT,
            raza_manual     TEXT,
            raza_detectada  TEXT,
            notas           TEXT,
            vet_nombre      TEXT,
            fecha           TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS measurements (
            id                      INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id                 INTEGER REFERENCES cases(id),
            munon_largo_cm          REAL,
            munon_circunf_base_cm   REAL,
            munon_circunf_distal_cm REAL,
            scale_mm_per_px         REAL,
            breed_info_json         TEXT,
            fecha                   TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS prosthetic_specs (
            id                      INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id                 INTEGER REFERENCES cases(id),
            specs_json              TEXT,
            scad_code               TEXT,
            fecha                   TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_case(db_path: Path, case_data: Dict) -> int:
    """Guarda un nuevo caso y retorna el ID generado."""
    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()
    c.execute("""
        INSERT INTO cases
            (nombre_perro, nombre_dueno, peso_actual, sexo, edad,
             extremidad, estado, raza_manual, notas, vet_nombre, fecha)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        case_data.get("nombre_perro"),
        case_data.get("nombre_dueno"),
        case_data.get("peso_actual"),
        case_data.get("sexo"),
        case_data.get("edad"),
        case_data.get("extremidad"),
        case_data.get("estado"),
        case_data.get("raza_manual"),
        case_data.get("notas"),
        case_data.get("vet_nombre"),
        case_data.get("fecha"),
    ))
    case_id = c.lastrowid
    conn.commit()
    conn.close()
    return case_id


def update_case_breed(db_path: Path, case_id: int, raza_detectada: str) -> None:
    """Actualiza la raza detectada automáticamente en un caso."""
    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()
    c.execute(
        "UPDATE cases SET raza_detectada = ? WHERE id = ?",
        (raza_detectada, case_id)
    )
    conn.commit()
    conn.close()


def save_measurements(db_path: Path, case_id: int, meas: Dict, breed_info: Optional[Dict] = None) -> None:
    """Guarda las medidas del muñón para un caso."""
    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()
    c.execute("""
        INSERT INTO measurements
            (case_id, munon_largo_cm, munon_circunf_base_cm,
             munon_circunf_distal_cm, scale_mm_per_px, breed_info_json, fecha)
        VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
    """, (
        case_id,
        meas.get("munon_largo_cm"),
        meas.get("munon_circunf_base_cm"),
        meas.get("munon_circunf_distal_cm"),
        meas.get("scale_mm_per_px"),
        json.dumps(breed_info) if breed_info else None,
    ))
    conn.commit()
    conn.close()


def save_prosthetic_specs(db_path: Path, case_id: int, specs: Dict, scad_code: str = "") -> None:
    """Guarda las especificaciones de la prótesis y el código OpenSCAD."""
    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()
    c.execute("""
        INSERT INTO prosthetic_specs (case_id, specs_json, scad_code, fecha)
        VALUES (?, ?, ?, datetime('now'))
    """, (case_id, json.dumps(specs), scad_code))
    conn.commit()
    conn.close()


def get_cases(db_path: Path) -> List[tuple]:
    """Retorna todos los casos ordenados por fecha descendente."""
    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()
    c.execute("""
        SELECT id, nombre_perro, nombre_dueno, extremidad,
               COALESCE(raza_detectada, raza_manual, 'No detectada'),
               estado, fecha
        FROM cases
        ORDER BY fecha DESC
    """)
    rows = c.fetchall()
    conn.close()
    return rows


def get_case(db_path: Path, case_id: int) -> Optional[Dict]:
    """Retorna todos los datos de un caso por ID."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM cases WHERE id = ?", (case_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def get_case_measurements(db_path: Path, case_id: int) -> Optional[Dict]:
    """Retorna las medidas más recientes de un caso."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("""
        SELECT * FROM measurements WHERE case_id = ?
        ORDER BY fecha DESC LIMIT 1
    """, (case_id,))
    row = c.fetchone()
    conn.close()
    if row:
        result = dict(row)
        if result.get("breed_info_json"):
            result["breed_info"] = json.loads(result["breed_info_json"])
        return result
    return None
