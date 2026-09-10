"""
Generic phone-photo preprocessing for identity documents.

Supports:
    - Aadhaar
    - Passport
    - PAN
    - Other rectangular identity documents

Goal:
    Detect the document inside a phone photograph, correct perspective,
    and return a clean document crop for classification/OCR/forensics.

The detector is conservative:
    - It tries multiple edge/threshold methods.
    - It accepts both true 4-point contours and strong rectangular contours.
    - It rejects obviously invalid shapes.
    - If no reliable document is found, the original image is returned.
"""

from pathlib import Path

import cv2
import numpy as np


def order_points(pts):
    """Return points in top-left, top-right, bottom-right, bottom-left order."""

    pts = np.asarray(
        pts,
        dtype=np.float32,
    )

    s = pts.sum(axis=1)
    d = np.diff(
        pts,
        axis=1,
    ).ravel()

    return np.array(
        [
            pts[np.argmin(s)],
            pts[np.argmin(d)],
            pts[np.argmax(s)],
            pts[np.argmax(d)],
        ],
        dtype=np.float32,
    )


def four_point_warp(
    img,
    quad,
):
    """
    Apply perspective correction using four document corners.

    Output size is derived from the detected document geometry.
    """

    rect = order_points(quad)

    top_left, top_right, bottom_right, bottom_left = rect

    width_top = np.linalg.norm(
        top_right - top_left
    )

    width_bottom = np.linalg.norm(
        bottom_right - bottom_left
    )

    height_left = np.linalg.norm(
        bottom_left - top_left
    )

    height_right = np.linalg.norm(
        bottom_right - top_right
    )

    output_width = max(
        int(round(max(width_top, width_bottom))),
        1,
    )

    output_height = max(
        int(round(max(height_left, height_right))),
        1,
    )

    # Prevent extremely large outputs.
    max_dimension = 1800

    scale = min(
        1.0,
        max_dimension / max(
            output_width,
            output_height,
        ),
    )

    output_width = max(
        int(round(output_width * scale)),
        1,
    )

    output_height = max(
        int(round(output_height * scale)),
        1,
    )

    dst = np.array(
        [
            [0, 0],
            [output_width - 1, 0],
            [output_width - 1, output_height - 1],
            [0, output_height - 1],
        ],
        dtype=np.float32,
    )

    matrix = cv2.getPerspectiveTransform(
        rect,
        dst,
    )

    warped = cv2.warpPerspective(
        img,
        matrix,
        (
            output_width,
            output_height,
        ),
    )

    return warped


def _contour_quad(
    contour,
    scale,
):
    """
    Try to approximate a contour as a four-point polygon.
    """

    perimeter = cv2.arcLength(
        contour,
        True,
    )

    if perimeter <= 0:
        return None

    for epsilon_factor in (
        0.015,
        0.02,
        0.025,
        0.03,
        0.04,
    ):
        approximation = cv2.approxPolyDP(
            contour,
            epsilon_factor * perimeter,
            True,
        )

        if len(approximation) == 4:
            if not cv2.isContourConvex(
                approximation
            ):
                continue

            points = (
                approximation
                .reshape(4, 2)
                .astype(np.float32)
            )

            points = points / scale

            return points

    return None


def _quad_quality(
    quad,
    image_shape,
):
    """
    Calculate geometric quality of a quadrilateral.

    Returns:
        score, width, height, aspect_ratio, area_ratio
    """

    height, width = image_shape[:2]

    rect = order_points(
        quad
    )

    top_left, top_right, bottom_right, bottom_left = rect

    top_width = np.linalg.norm(
        top_right - top_left
    )

    bottom_width = np.linalg.norm(
        bottom_right - bottom_left
    )

    left_height = np.linalg.norm(
        bottom_left - top_left
    )

    right_height = np.linalg.norm(
        bottom_right - top_right
    )

    average_width = (
        top_width + bottom_width
    ) / 2.0

    average_height = (
        left_height + right_height
    ) / 2.0

    if average_width <= 0 or average_height <= 0:
        return (
            -1.0,
            average_width,
            average_height,
            0.0,
            0.0,
        )

    aspect_ratio = (
        average_width / average_height
    )

    contour_area = abs(
        cv2.contourArea(
            rect.astype(np.float32)
        )
    )

    image_area = float(
        width * height
    )

    area_ratio = (
        contour_area / image_area
        if image_area > 0
        else 0.0
    )

    # Identity documents are normally rectangular and
    # reasonably wide/tall rather than extremely elongated.
    if not (
        0.45
        <= aspect_ratio
        <= 2.6
    ):
        return (
            -1.0,
            average_width,
            average_height,
            aspect_ratio,
            area_ratio,
        )

    # Reject tiny regions.
    if area_ratio < 0.15:
        return (
            -1.0,
            average_width,
            average_height,
            aspect_ratio,
            area_ratio,
        )

    # Reject almost the complete image.
    if area_ratio > 0.97:
        return (
            -1.0,
            average_width,
            average_height,
            aspect_ratio,
            area_ratio,
        )

    # Similar opposite-side lengths indicate a reasonable rectangle.
    width_consistency = min(
        top_width,
        bottom_width,
    ) / max(
        top_width,
        bottom_width,
    )

    height_consistency = min(
        left_height,
        right_height,
    ) / max(
        left_height,
        right_height,
    )

    rectangularity = (
        width_consistency
        + height_consistency
    ) / 2.0

    score = (
        area_ratio * 0.65
        + rectangularity * 0.35
    )

    return (
        score,
        average_width,
        average_height,
        aspect_ratio,
        area_ratio,
    )


def find_document_quad(
    img,
):
    """
    Detect the most likely document quadrilateral.

    Multiple preprocessing strategies are attempted because phone
    photographs may contain:
        - shadows
        - reflections
        - uneven illumination
        - weak borders
        - textured backgrounds
        - perspective distortion
    """

    if img is None or img.size == 0:
        return None

    original_height, original_width = img.shape[:2]

    # Work on a smaller image for faster contour detection.
    scale = min(
        1.0,
        1400.0 / max(
            original_height,
            original_width,
        ),
    )

    if scale < 1.0:
        small = cv2.resize(
            img,
            None,
            fx=scale,
            fy=scale,
            interpolation=cv2.INTER_AREA,
        )
    else:
        small = img.copy()

    gray = cv2.cvtColor(
        small,
        cv2.COLOR_BGR2GRAY,
    )

    # Light smoothing reduces tiny background edges.
    blurred = cv2.GaussianBlur(
        gray,
        (5, 5),
        0,
    )

    # -------------------------------------------------------------
    # Build several edge/threshold variants.
    # -------------------------------------------------------------

    variants = []

    # Standard Canny.
    variants.append(
        cv2.Canny(
            blurred,
            30,
            100,
        )
    )

    # Stronger Canny.
    variants.append(
        cv2.Canny(
            blurred,
            60,
            150,
        )
    )

    # Otsu threshold.
    _, otsu = cv2.threshold(
        blurred,
        0,
        255,
        cv2.THRESH_BINARY
        + cv2.THRESH_OTSU,
    )

    variants.append(
        cv2.Canny(
            otsu,
            30,
            100,
        )
    )

    # Adaptive threshold.
    adaptive = cv2.adaptiveThreshold(
        blurred,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        41,
        9,
    )

    variants.append(
        cv2.Canny(
            adaptive,
            30,
            100,
        )
    )

    # -------------------------------------------------------------
    # Find candidates.
    # -------------------------------------------------------------

    image_area = float(
        small.shape[0]
        * small.shape[1]
    )

    candidates = []

    for edges in variants:

        # Connect broken document borders.
        close_kernel = np.ones(
            (9, 9),
            dtype=np.uint8,
        )

        closed = cv2.morphologyEx(
            edges,
            cv2.MORPH_CLOSE,
            close_kernel,
            iterations=2,
        )

        # Small dilation connects nearby border segments.
        dilated = cv2.dilate(
            closed,
            np.ones(
                (3, 3),
                dtype=np.uint8,
            ),
            iterations=1,
        )

        contours, _ = cv2.findContours(
            dilated,
            cv2.RETR_LIST,
            cv2.CHAIN_APPROX_SIMPLE,
        )

        for contour in contours:

            area = cv2.contourArea(
                contour
            )

            if area < image_area * 0.15:
                continue

            if area > image_area * 0.97:
                continue

            quad = _contour_quad(
                contour,
                scale,
            )

            if quad is None:
                continue

            quality = _quad_quality(
                quad,
                img.shape,
            )

            score = quality[0]

            if score <= 0:
                continue

            candidates.append(
                (
                    score,
                    area,
                    quad,
                )
            )

    if not candidates:
        return None

    # Largest/highest-quality candidate wins.
    candidates.sort(
        key=lambda item: (
            item[0],
            item[1],
        ),
        reverse=True,
    )

    return candidates[0][2]


def preprocess_photo(
    img,
):
    """
    Preprocess a photographed identity document.

    Returns:
        processed_image, metadata
    """

    if img is None or img.size == 0:
        raise ValueError(
            "Input image is empty."
        )

    quad = find_document_quad(
        img
    )

    if quad is None:
        return (
            img.copy(),
            {
                "perspective_corrected": False,
                "reason": (
                    "no reliable quadrilateral"
                ),
                "original_shape": list(
                    img.shape
                ),
                "processed_shape": list(
                    img.shape
                ),
            },
        )

    warped = four_point_warp(
        img,
        quad,
    )

    return (
        warped,
        {
            "perspective_corrected": True,
            "quad": quad.round(
                1
            ).tolist(),
            "original_shape": list(
                img.shape
            ),
            "processed_shape": list(
                warped.shape
            ),
        },
    )


def preprocess_path(
    path: str,
    output_path: str | None = None,
):
    """Load, preprocess, and optionally save a document image."""

    image = cv2.imread(
        path
    )

    if image is None:
        raise ValueError(
            f"Could not read image: {path}"
        )

    processed, metadata = preprocess_photo(
        image
    )

    if output_path:
        success = cv2.imwrite(
            output_path,
            processed,
        )

        if not success:
            raise ValueError(
                f"Could not save preprocessed image: {output_path}"
            )

    return processed, metadata