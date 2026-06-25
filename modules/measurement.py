"""
Ache Innovation — Módulo de Medición con ArUco
Detecta el marcador ArUco en la foto y calcula la escala mm/píxel.
El marcador físico debe imprimirse a exactamente 5cm × 5cm.
"""

import cv2
import numpy as np
from PIL import Image
from typing import Tuple


# Tamaño real del marcador impreso (en mm)
MARKER_SIZE_MM = 50.0  # 5cm


def detect_aruco(img_array: np.ndarray) -> Tuple[np.ndarray, float, bool]:
    """
    Detecta el marcador ArUco y calcula la escala real.

    Args:
        img_array: Imagen como array numpy en formato RGB

    Returns:
        (imagen_anotada_RGB, mm_por_pixel, marcador_encontrado)
    """
    # Convertir RGB → BGR para OpenCV
    img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    # Detector ArUco
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    params = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, params)

    def _calc_scale(corners_list):
        """Calcula mm/px a partir de las esquinas del marcador."""
        corner = corners_list[0][0]
        sides = []
        for i in range(4):
            pt1 = corner[i]
            pt2 = corner[(i + 1) % 4]
            sides.append(np.linalg.norm(pt2 - pt1))
        avg_side_px = np.mean(sides)
        return MARKER_SIZE_MM / avg_side_px

    # Intento 1: imagen original
    corners, ids, _ = detector.detectMarkers(gray)

    # Intento 2: imagen con contraste mejorado
    if ids is None:
        enhanced = cv2.equalizeHist(gray)
        corners, ids, _ = detector.detectMarkers(enhanced)

    # Intento 3: imagen con umbral adaptativo
    if ids is None:
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        corners, ids, _ = detector.detectMarkers(thresh)

    annotated = img_bgr.copy()

    if ids is not None and len(ids) > 0:
        cv2.aruco.drawDetectedMarkers(annotated, corners, ids)
        mm_per_px = _calc_scale(corners)

        # Texto de escala en la imagen
        h, w = annotated.shape[:2]
        font_scale = max(0.5, w / 1500)
        thickness = max(1, int(w / 800))
        cv2.putText(
            annotated,
            f"Marcador OK — Escala: {mm_per_px:.3f} mm/px",
            (10, 35), cv2.FONT_HERSHEY_SIMPLEX,
            font_scale, (0, 220, 0), thickness
        )

        result_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
        return result_rgb, mm_per_px, True

    else:
        # Sin marcador — devolver imagen original con aviso
        cv2.putText(
            annotated,
            "Marcador ArUco no detectado",
            (10, 35), cv2.FONT_HERSHEY_SIMPLEX,
            1.0, (0, 0, 220), 2
        )
        result_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
        return result_rgb, 0.0, False


def px_to_mm(pixels: float, mm_per_px: float) -> float:
    """Convierte una distancia en píxeles a milímetros."""
    return pixels * mm_per_px


def px_to_cm(pixels: float, mm_per_px: float) -> float:
    """Convierte una distancia en píxeles a centímetros."""
    return (pixels * mm_per_px) / 10.0


def generate_aruco_marker_png() -> bytes:
    """
    Genera el marcador ArUco (ID 0, DICT_4X4_50) como PNG en bytes.
    Imprimir a exactamente 5cm × 5cm.
    """
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    # 400px con borde de 50px a cada lado
    marker_img = cv2.aruco.generateImageMarker(aruco_dict, 0, 400)

    # Agregar borde blanco y texto instructivo
    border = 60
    canvas = np.full(
        (400 + border * 2 + 60, 400 + border * 2),
        255, dtype=np.uint8
    )
    canvas[border:border + 400, border:border + 400] = marker_img

    # Texto
    cv2.putText(
        canvas,
        "IMPRIMIR A: 5cm x 5cm exactos",
        (10, canvas.shape[0] - 35),
        cv2.FONT_HERSHEY_SIMPLEX, 0.55, 0, 1
    )
    cv2.putText(
        canvas,
        "Ache Innovation — Marcador de Escala",
        (10, canvas.shape[0] - 10),
        cv2.FONT_HERSHEY_SIMPLEX, 0.45, 100, 1
    )

    # Codificar como PNG
    success, buffer = cv2.imencode(".png", canvas)
    if success:
        return buffer.tobytes()
    raise RuntimeError("No se pudo generar el marcador ArUco")
