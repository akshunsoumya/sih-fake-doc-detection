from pathlib import Path

import cv2
import numpy as np


class CompressionAnalyzer:
    """
    Estimate JPEG/compression-related image characteristics.

    This is intentionally a lightweight MVP signal.
    It does NOT claim to identify a specific compression history.
    """

    def _load_image(self, image):
        if isinstance(image, (str, Path)):
            image_path = Path(image)

            if not image_path.exists():
                raise FileNotFoundError(
                    f"Image not found: {image_path}"
                )

            image = cv2.imread(
                str(image_path),
                cv2.IMREAD_COLOR,
            )

            if image is None:
                raise ValueError(
                    f"Could not read image: {image_path}"
                )

            return image

        if isinstance(image, np.ndarray):
            if image.size == 0:
                raise ValueError(
                    "Provided image array is empty."
                )

            return image

        raise TypeError(
            "image must be a file path or NumPy array."
        )

    def analyze(self, image):
        image = self._load_image(image)

        success, encoded = cv2.imencode(
            ".jpg",
            image,
            [
                cv2.IMWRITE_JPEG_QUALITY,
                90,
            ],
        )

        if not success:
            raise ValueError(
                "Could not JPEG-encode image."
            )

        encoded_size = int(
            len(encoded)
        )

        raw_size = int(
            image.nbytes
        )

        compression_ratio = (
            encoded_size / raw_size
            if raw_size > 0
            else 0.0
        )

        return {
            "status": "completed",
            "encoded_size_bytes": encoded_size,
            "raw_size_bytes": raw_size,
            "jpeg_to_raw_ratio": round(
                compression_ratio,
                6,
            ),
        }


def run_check(image):
    """Compatibility helper."""
    return CompressionAnalyzer().analyze(image)
