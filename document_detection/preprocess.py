"""Phone-photo preprocessing for Aadhaar images.

Goal: turn a tilted/rotated card photo into a stable top-down crop before
running OCR/forensic checks. This is deliberately conservative: if a reliable
quadrilateral cannot be found, the original image is returned instead of
inventing a crop.
"""
from pathlib import Path
import cv2
import numpy as np


def order_points(pts):
    pts = np.asarray(pts, dtype=np.float32)
    s = pts.sum(axis=1)
    d = np.diff(pts, axis=1).ravel()
    return np.array([pts[np.argmin(s)], pts[np.argmin(d)],
                     pts[np.argmax(s)], pts[np.argmax(d)]], dtype=np.float32)


def four_point_warp(img, quad, width=1280, height=800):
    rect = order_points(quad)
    dst = np.array([[0, 0], [width - 1, 0],
                    [width - 1, height - 1], [0, height - 1]], dtype=np.float32)
    M = cv2.getPerspectiveTransform(rect, dst)
    return cv2.warpPerspective(img, M, (width, height))


def find_document_quad(img):
    h, w = img.shape[:2]
    scale = min(1.0, 1000.0 / max(h, w))
    small = cv2.resize(img, None, fx=scale, fy=scale) if scale < 1 else img.copy()
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)
    kernel = np.ones((5, 5), np.uint8)
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=2)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    image_area = small.shape[0] * small.shape[1]
    candidates = []
    for c in contours:
        area = cv2.contourArea(c)
        if area < image_area * 0.20:
            continue
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4 and cv2.isContourConvex(approx):
            pts = approx.reshape(4, 2).astype(np.float32) / scale
            candidates.append((area, pts))
    if not candidates:
        return None
    return max(candidates, key=lambda x: x[0])[1]


def preprocess_photo(img):
    quad = find_document_quad(img)
    if quad is None:
        return img.copy(), {"perspective_corrected": False, "reason": "no reliable quadrilateral"}
    warped = four_point_warp(img, quad)
    return warped, {"perspective_corrected": True, "quad": quad.round(1).tolist()}


def preprocess_path(path: str, output_path: str | None = None):
    img = cv2.imread(path)
    if img is None:
        raise ValueError(f"Could not read image: {path}")
    out, meta = preprocess_photo(img)
    if output_path:
        cv2.imwrite(output_path, out)
    return out, meta
