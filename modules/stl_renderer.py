"""Render y lectura de STL para preview real en la app.

Usa OpenSCAD CLI si está instalado en macOS. Genera STL desde SCAD y lo
parsea para visualizar exactamente el modelo CAD exportable.
"""

from __future__ import annotations

import struct
import subprocess
import tempfile
from pathlib import Path
from typing import Tuple

import numpy as np

OPENSCAD_MAC = Path("/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD")


def openscad_available() -> bool:
    return OPENSCAD_MAC.exists() and OPENSCAD_MAC.is_file()


def render_scad_to_stl(scad_code: str, timeout: int = 90) -> bytes:
    """Renderiza código SCAD a STL usando OpenSCAD CLI y devuelve bytes STL."""
    if not openscad_available():
        raise RuntimeError("OpenSCAD no está instalado en /Applications/OpenSCAD.app")

    with tempfile.TemporaryDirectory(prefix="ache_scad_") as td:
        td = Path(td)
        scad_path = td / "model.scad"
        stl_path = td / "model.stl"
        scad_path.write_text(scad_code, encoding="utf-8")

        cmd = [str(OPENSCAD_MAC), "-o", str(stl_path), str(scad_path)]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if proc.returncode != 0:
            raise RuntimeError((proc.stderr or proc.stdout or "OpenSCAD falló").strip())
        if not stl_path.exists() or stl_path.stat().st_size == 0:
            raise RuntimeError("OpenSCAD no generó el STL")
        return stl_path.read_bytes()


def parse_stl(stl_bytes: bytes) -> Tuple[np.ndarray, np.ndarray]:
    """Parsea STL ASCII o binario. Devuelve vertices únicos y faces."""
    if stl_bytes[:5].lower() == b"solid" and b"facet" in stl_bytes[:500].lower():
        return _parse_ascii_stl(stl_bytes)
    return _parse_binary_stl(stl_bytes)


def _parse_ascii_stl(data: bytes) -> Tuple[np.ndarray, np.ndarray]:
    text = data.decode("utf-8", errors="ignore")
    verts = []
    faces = []
    current = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("vertex"):
            parts = line.split()
            if len(parts) >= 4:
                current.append((float(parts[1]), float(parts[2]), float(parts[3])))
                if len(current) == 3:
                    idx = []
                    for v in current:
                        idx.append(len(verts))
                        verts.append(v)
                    faces.append(tuple(idx))
                    current = []
    return _dedupe(np.array(verts, dtype=float), np.array(faces, dtype=int))


def _parse_binary_stl(data: bytes) -> Tuple[np.ndarray, np.ndarray]:
    if len(data) < 84:
        raise RuntimeError("STL binario inválido")
    n_tri = struct.unpack_from("<I", data, 80)[0]
    expected = 84 + n_tri * 50
    if len(data) < expected:
        raise RuntimeError("STL binario incompleto")

    verts = []
    faces = []
    offset = 84
    for _ in range(n_tri):
        # normal 12 bytes, then 3 vertices
        offset += 12
        idx = []
        for _v in range(3):
            x, y, z = struct.unpack_from("<fff", data, offset)
            offset += 12
            idx.append(len(verts))
            verts.append((x, y, z))
        faces.append(tuple(idx))
        offset += 2  # attr byte count
    return _dedupe(np.array(verts, dtype=float), np.array(faces, dtype=int))


def _dedupe(vertices: np.ndarray, faces: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    if len(vertices) == 0:
        return vertices, faces
    # STL está en mm. Convertimos a cm para que coincida con los ejes de la app.
    vertices = vertices / 10.0
    rounded = np.round(vertices, 5)
    unique, inverse = np.unique(rounded, axis=0, return_inverse=True)
    return unique.astype(float), inverse[faces].astype(int)
