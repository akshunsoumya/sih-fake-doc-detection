from pathlib import Path

import cv2
import numpy as np

from forgery_detection.compression import CompressionAnalyzer
from forgery_detection.copy_move import CopyMoveDetector
from forgery_detection.ela import ELAAnalyzer
from forgery_detection.image_quality import ImageQualityAnalyzer
from forgery_detection.metadata import MetadataAnalyzer


class ForensicAnalyzer:
    """
    Unified forensic analysis engine.

    Current signals:
        - ELA
        - Copy-move
        - Metadata
        - Image quality
        - Compression characteristics

    These signals support a later forgery classifier.
    They are NOT direct proof of forgery.
    """

    def __init__(
        self,
        ela_quality: int = 90,
        copy_move_min_matches: int = 8,
        copy_move_distance_ratio: float = 0.75,
        copy_move_min_spatial_distance: float = 40.0,
    ):
        self.ela = ELAAnalyzer(
            quality=ela_quality,
        )

        self.copy_move = CopyMoveDetector(
            min_matches=copy_move_min_matches,
            distance_ratio=copy_move_distance_ratio,
            min_spatial_distance=copy_move_min_spatial_distance,
        )

        self.metadata = MetadataAnalyzer()
        self.image_quality = ImageQualityAnalyzer()
        self.compression = CompressionAnalyzer()

    def _load_image(self, image):
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
            "image must be a file path or NumPy array."
        )

    def analyze(self, image):
        """
        Run all forensic analyzers.

        The image is loaded once and the same image array is
        passed to the image-based analyzers.
        """

        image_array = self._load_image(image)

        ela_result = self.ela.analyze(
            image_array
        )

        copy_move_result = self.copy_move.detect(
            image_array
        )

        image_quality_result = self.image_quality.analyze(
            image_array
        )

        compression_result = self.compression.analyze(
            image_array
        )

        # Metadata requires the original file path.
        if isinstance(image, (str, Path)):
            metadata_result = self.metadata.analyze(
                image
            )
        else:
            metadata_result = {
                "status": "not_available",
                "message": (
                    "Metadata analysis requires "
                    "an image file path."
                ),
            }

        ela_score = float(
            ela_result.get(
                "forgery_score",
                0.0,
            )
        )

        copy_move_score = float(
            copy_move_result.get(
                "copy_move_score",
                0.0,
            )
        )

        combined_score = (
            0.6 * ela_score
            + 0.4 * copy_move_score
        )

        combined_score = float(
            max(
                0.0,
                min(
                    combined_score,
                    1.0,
                ),
            )
        )

        return {
            "status": "completed",
            "signals": {
                "ela": ela_result,
                "copy_move": copy_move_result,
                "metadata": metadata_result,
                "image_quality": image_quality_result,
                "compression": compression_result,
            },
            "combined_anomaly_score": round(
                combined_score,
                4,
            ),
        }


def run_forensic_analysis(image):
    """Convenience helper."""
    analyzer = ForensicAnalyzer()
    return analyzer.analyze(image)
