from pathlib import Path

import cv2
import numpy as np


class ImageQualityAnalyzer:
    """
    Calculate basic image-quality features.

    Current signals:
        - resolution
        - brightness
        - contrast
        - blur/sharpness using Laplacian variance

    These are supporting signals only.
    """

    def _load_image(self, image):
        if isinstance(image, (str, Path)):
            image = cv2.imread(str(image))

            if image is None:
                raise ValueError(
                    "Could not read image."
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

        height, width = image.shape[:2]

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY,
        )

        brightness = float(
            np.mean(gray)
        )

        contrast = float(
            np.std(gray)
        )

        sharpness = float(
            cv2.Laplacian(
                gray,
                cv2.CV_64F,
            ).var()
        )

        # Very low Laplacian variance generally indicates
        # a blurry/low-detail image.
        if sharpness < 50:
            quality_status = "low_sharpness"
        elif sharpness < 150:
            quality_status = "moderate_sharpness"
        else:
            quality_status = "good_sharpness"

        return {
            "status": "completed",
            "width": width,
            "height": height,
            "brightness": round(
                brightness,
                4,
            ),
            "contrast": round(
                contrast,
                4,
            ),
            "sharpness": round(
                sharpness,
                4,
            ),
            "quality_status": quality_status,
        }


def run_check(image):
    """Compatibility helper."""
    return ImageQualityAnalyzer().analyze(image)
