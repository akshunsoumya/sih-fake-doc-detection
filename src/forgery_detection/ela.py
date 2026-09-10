from pathlib import Path

import cv2
import numpy as np


class ELAAnalyzer:
    """
    Error Level Analysis (ELA).

    Accepts either:
        1. an image file path
        2. an OpenCV/NumPy image array

    ELA is a supporting forensic signal.
    It is not proof of forgery.
    """

    def __init__(self, quality: int = 90):
        self.quality = quality

    def _load_image(self, image):
        """Load an image from either a path or NumPy array."""

        if isinstance(image, (str, Path)):
            image = cv2.imread(str(image))

            if image is None:
                raise ValueError(
                    f"Could not read image: {image}"
                )

            return image

        if isinstance(image, np.ndarray):
            if image.size == 0:
                raise ValueError(
                    "Provided image array is empty."
                )

            return image

        raise TypeError(
            "image must be a file path or a NumPy array."
        )

    def analyze(self, image):
        """Run ELA analysis."""

        image = self._load_image(image)

        success, encoded = cv2.imencode(
            ".jpg",
            image,
            [
                cv2.IMWRITE_JPEG_QUALITY,
                self.quality,
            ],
        )

        if not success:
            raise ValueError(
                "Could not JPEG-compress image for ELA."
            )

        recompressed = cv2.imdecode(
            encoded,
            cv2.IMREAD_COLOR,
        )

        if recompressed is None:
            raise ValueError(
                "Could not decode recompressed image."
            )

        original_float = image.astype(np.float32)
        recompressed_float = recompressed.astype(np.float32)

        difference = np.abs(
            original_float - recompressed_float
        )

        error_map = np.mean(
            difference,
            axis=2,
        )

        max_block_error = float(
            np.max(error_map)
        )

        mean_error = float(
            np.mean(error_map)
        )

        threshold = mean_error + (
            2.0 * float(np.std(error_map))
        )

        high_error_pixels = (
            error_map > threshold
        )

        spike_ratio = float(
            np.mean(high_error_pixels)
        )

        normalized_max = min(
            max_block_error / 50.0,
            1.0,
        )

        normalized_spikes = min(
            spike_ratio / 0.10,
            1.0,
        )

        forgery_score = (
            0.6 * normalized_max
            + 0.4 * normalized_spikes
        )

        forgery_score = float(
            max(
                0.0,
                min(
                    forgery_score,
                    1.0,
                ),
            )
        )

        return {
            "max_block_error": round(
                max_block_error,
                4,
            ),
            "spike_ratio": round(
                spike_ratio,
                6,
            ),
            "forgery_score": round(
                forgery_score,
                4,
            ),
            "status": "completed",
        }


def run_check(image):
    """
    Compatibility helper matching Devanshu's
    previous `ela.run_check(...)` interface.

    Accepts either a file path or a NumPy image.
    """

    analyzer = ELAAnalyzer()

    return analyzer.analyze(image)