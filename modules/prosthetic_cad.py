"""
Ache Innovation — Generador CAD/STL paramétrico básico

Este módulo genera una prótesis canina externa como malla 3D real:
- socket superior hueco
- caña estructural curva
- pie protésico con suela y dedos
- bandas/correas del socket

No pretende reemplazar CAD clínico profesional; sirve como primera base STL
coherente y parametrizable para iterar con veterinarios/diseñadores.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Tuple
import math
import numpy as np


@dataclass
class Mesh:
    vertices: np.ndarray  # (N, 3)
    faces: np.ndarray     # (M, 3)


def _merge(meshes: Iterable[Mesh]) -> Mesh:
    verts = []
    faces = []
    offset = 0
    for m in meshes:
        if len(m.vertices) == 0 or len(m.faces) == 0:
            continue
        verts.append(m.vertices)
        faces.append(m.faces + offset)
        offset += len(m.vertices)
    if not verts:
        return Mesh(np.zeros((0, 3)), np.zeros((0, 3), dtype=int))
    return Mesh(np.vstack(verts), np.vstack(faces).astype(int))


def _ellipsoid(cx, cy, cz, rx, ry, rz, nu=40, nv=20, cut_bottom=None) -> Mesh:
    verts = []
    index = []
    for i in range(nv + 1):
        v = math.pi * i / nv
        row = []
        for j in range(nu):
            u = 2 * math.pi * j / nu
            x = cx + rx * math.cos(u) * math.sin(v)
            y = cy + ry * math.sin(u) * math.sin(v)
            z = cz + rz * math.cos(v)
            if cut_bottom is not None and z < cut_bottom:
                z = cut_bottom
            row.append(len(verts))
            verts.append((x, y, z))
        index.append(row)

    faces = []
    for i in range(nv):
        for j in range(nu):
            a = index[i][j]
            b = index[i][(j + 1) % nu]
            c = index[i + 1][(j + 1) % nu]
            d = index[i + 1][j]
            faces.append((a, b, c))
            faces.append((a, c, d))
    return Mesh(np.array(verts, dtype=float), np.array(faces, dtype=int))


def _frustum(cx0, cy0, z0, rx0, ry0, cx1, cy1, z1, rx1, ry1, n=56, nz=18, cap_bottom=True, cap_top=False) -> Mesh:
    verts = []
    rings = []
    for i in range(nz + 1):
        t = i / nz
        cx = cx0 * (1 - t) + cx1 * t
        cy = cy0 * (1 - t) + cy1 * t
        z = z0 * (1 - t) + z1 * t
        rx = rx0 * (1 - t) + rx1 * t
        ry = ry0 * (1 - t) + ry1 * t
        ring = []
        for j in range(n):
            u = 2 * math.pi * j / n
            ring.append(len(verts))
            verts.append((cx + rx * math.cos(u), cy + ry * math.sin(u), z))
        rings.append(ring)

    faces = []
    for i in range(nz):
        for j in range(n):
            a = rings[i][j]
            b = rings[i][(j + 1) % n]
            c = rings[i + 1][(j + 1) % n]
            d = rings[i + 1][j]
            faces.append((a, b, c))
            faces.append((a, c, d))

    if cap_bottom:
        center = len(verts)
        verts.append((cx0, cy0, z0))
        for j in range(n):
            faces.append((center, rings[0][(j + 1) % n], rings[0][j]))
    if cap_top:
        center = len(verts)
        verts.append((cx1, cy1, z1))
        for j in range(n):
            faces.append((center, rings[-1][j], rings[-1][(j + 1) % n]))
    return Mesh(np.array(verts, dtype=float), np.array(faces, dtype=int))


def _tube_along_path(points, radii, n=36, oval_x=0.78, oval_y=1.0) -> Mesh:
    verts = []
    rings = []
    for (cx, cy, z), r in zip(points, radii):
        ring = []
        for j in range(n):
            u = 2 * math.pi * j / n
            ring.append(len(verts))
            verts.append((cx + r * oval_x * math.cos(u), cy + r * oval_y * math.sin(u), z))
        rings.append(ring)
    faces = []
    for i in range(len(rings) - 1):
        for j in range(n):
            a = rings[i][j]
            b = rings[i][(j + 1) % n]
            c = rings[i + 1][(j + 1) % n]
            d = rings[i + 1][j]
            faces.append((a, b, c))
            faces.append((a, c, d))
    return Mesh(np.array(verts, dtype=float), np.array(faces, dtype=int))


def _elliptic_band(cx, cy, z, rx, ry, height=0.35, thickness=0.16, n=60) -> Mesh:
    # Banda superficial tipo correa alrededor del socket.
    outer = _frustum(cx, cy, z - height / 2, rx + thickness, ry + thickness,
                     cx, cy, z + height / 2, rx + thickness, ry + thickness,
                     n=n, nz=2, cap_bottom=False, cap_top=False)
    inner = _frustum(cx, cy, z - height / 2, rx, ry,
                     cx, cy, z + height / 2, rx, ry,
                     n=n, nz=2, cap_bottom=False, cap_top=False)
    # Invert inner faces visually by reversing winding.
    inner.faces = inner.faces[:, ::-1]
    return _merge([outer, inner])


def generate_prosthetic_mesh(specs: dict) -> Mesh:
    total = float(specs.get("longitud_total_cm", 18.0))
    socket_d = float(specs.get("diametro_socket_cm", 5.5))
    socket_depth = float(specs.get("profundidad_socket_cm", min(5.0, total * 0.35)))
    shaft_d = float(specs.get("diametro_pata_cm", max(socket_d * 0.55, 2.8)))
    is_front = "Delantera" in specs.get("tipo", "Delantera")

    # En centímetros. Z arriba; Y adelante; X ancho.
    shaft_r = shaft_d / 2
    socket_r = socket_d / 2
    foot_len = max(shaft_d * 1.75, 7.0)
    foot_w = max(shaft_d * 1.00, 3.6)
    foot_h = max(shaft_d * 0.34, 1.15)

    ankle_z = foot_h + 0.75
    socket_top_z = max(total, ankle_z + socket_depth + 4.0)
    socket_bottom_z = socket_top_z - socket_depth
    socket_cy = -foot_len * 0.18

    meshes = []

    # Pie: forma baja, alargada, con punta elevada.
    meshes.append(_ellipsoid(0, foot_len * 0.06, foot_h * 0.55, foot_w * 0.50, foot_len * 0.48, foot_h * 0.50, cut_bottom=0.04))
    meshes.append(_ellipsoid(0, foot_len * 0.46, foot_h * 0.80, foot_w * 0.38, foot_len * 0.20, foot_h * 0.36, cut_bottom=0.06))
    meshes.append(_ellipsoid(0, -foot_len * 0.40, foot_h * 0.56, foot_w * 0.42, foot_len * 0.18, foot_h * 0.34, cut_bottom=0.05))

    # Suela/pad inferior.
    meshes.append(_ellipsoid(0, foot_len * 0.02, 0.16, foot_w * 0.44, foot_len * 0.40, 0.16, nu=40, nv=10, cut_bottom=0.015))

    # Dedos frontales conectados.
    for i, scale in zip([-1.35, -0.45, 0.45, 1.35], [0.82, 1.0, 1.0, 0.82]):
        meshes.append(_ellipsoid(i * foot_w * 0.13, foot_len * 0.63, foot_h * 0.72,
                                 foot_w * 0.08 * scale, foot_len * 0.11, foot_h * 0.18,
                                 nu=26, nv=12, cut_bottom=0.08))

    # Transición tobillo/carpo.
    meshes.append(_ellipsoid(0, -foot_len * 0.06, ankle_z, shaft_r * 0.72, shaft_r * 0.82, shaft_r * 0.45, nu=34, nv=14))

    # Caña principal curva.
    z_vals = np.linspace(ankle_z, socket_bottom_z + 0.15, 34)
    points = []
    radii = []
    for k, z in enumerate(z_vals):
        t = k / (len(z_vals) - 1)
        x = 0.0
        curve = 0.45 if is_front else 0.65
        y = -foot_len * 0.06 - curve * t + 0.14 * math.sin(math.pi * t)
        points.append((x, y, z))
        radii.append(shaft_r * (0.44 - 0.08 * t))
    meshes.append(_tube_along_path(points, radii, n=34, oval_x=0.72, oval_y=0.96))

    # Refuerzos laterales.
    for side in [-1, 1]:
        side_points = [(side * max(shaft_r * 0.45, 0.45), y - 0.10, z) for x, y, z in points]
        side_radii = [max(shaft_r * 0.10, 0.12)] * len(side_points)
        meshes.append(_tube_along_path(side_points, side_radii, n=18, oval_x=1.0, oval_y=1.0))

    # Socket externo ovalado, abierto arriba.
    meshes.append(_frustum(0, points[-1][1], socket_bottom_z, shaft_r * 0.85, shaft_r * 0.68,
                           0, socket_cy, socket_top_z, socket_r * 1.08, socket_r * 0.78,
                           n=58, nz=18, cap_bottom=True, cap_top=False))

    # Cavidad visual interior (superficie oscura/inner wall en STL igual geometría invertida).
    inner = _frustum(0, socket_cy, socket_top_z - socket_depth * 0.88, socket_r * 0.74, socket_r * 0.50,
                     0, socket_cy, socket_top_z + 0.02, socket_r * 0.90, socket_r * 0.62,
                     n=58, nz=8, cap_bottom=False, cap_top=False)
    inner.faces = inner.faces[:, ::-1]
    meshes.append(inner)

    # Bandas/correas sobre socket.
    meshes.append(_elliptic_band(0, socket_cy, socket_bottom_z + socket_depth * 0.35, socket_r * 1.10, socket_r * 0.80, height=0.28, thickness=0.09))
    meshes.append(_elliptic_band(0, socket_cy, socket_bottom_z + socket_depth * 0.66, socket_r * 1.13, socket_r * 0.83, height=0.28, thickness=0.09))

    return _merge(meshes)


def mesh_to_ascii_stl(mesh: Mesh, name="ache_canine_prosthesis") -> str:
    verts = mesh.vertices
    faces = mesh.faces
    lines = [f"solid {name}"]
    for f in faces:
        p1, p2, p3 = verts[f[0]], verts[f[1]], verts[f[2]]
        n = np.cross(p2 - p1, p3 - p1)
        norm = np.linalg.norm(n)
        if norm > 1e-9:
            n = n / norm
        else:
            n = np.array([0.0, 0.0, 0.0])
        lines.append(f"  facet normal {n[0]:.6e} {n[1]:.6e} {n[2]:.6e}")
        lines.append("    outer loop")
        for p in (p1, p2, p3):
            # STL en milímetros: cm -> mm
            lines.append(f"      vertex {p[0]*10:.6e} {p[1]*10:.6e} {p[2]*10:.6e}")
        lines.append("    endloop")
        lines.append("  endfacet")
    lines.append(f"endsolid {name}")
    return "\n".join(lines)
