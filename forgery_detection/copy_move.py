from pathlib import Path

import cv2
import numpy as np


class CopyMoveDetector:
    """
    Copy-move forgery detector.

    Detects regions that appear to have been copied and pasted
    somewhere else within the same image.

    Accepts either:
        1. an image file path
        2. an OpenCV / NumPy image array

    This is a supporting forensic signal, not proof of forgery.
    """

    def __init__(
        self,
        min_matches: int = 10,
        distance_ratio: float = 0.75,
    ):
        self.min_matches = min_matches
        self.distance_ratio = distance_ratio

        # SIFT is useful here because it finds local visual
        # features that can be compared within the same image.
        self.sift = cv2.SIFT_create()

        # FLANN is used to efficiently match SIFT descriptors.
        index_params = dict(
            algorithm=1,
            trees=5,
        )

        search_params = dict(
            checks=50,
        )

        self.matcher = cv2.FlannBasedMatcher(
            index_params,
            search_params,
        )

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

    def detect(self, image):
        """
        Run copy-move detection.

        Returns a dictionary containing:
            - keypoints
            - good_matches
            - match_ratio
            - copy_move_score
            - suspicious
            - status
        """

        image = self._load_image(image)

        # Convert to grayscale because SIFT works on intensity
        # information rather than color.
        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY,
        )

        # Detect local features.
        keypoints, descriptors = self.sift.detectAndCompute(
            gray,
            None,
        )

        if descriptors is None or len(keypoints) < 2:
            return {
                "keypoints": 0,
                "good_matches": 0,
                "match_ratio": 0.0,
                "copy_move_score": 0.0,
                "suspicious": False,
                "status": "insufficient_features",
            }

        # Match every feature against other features in the
        # same image.
        matches = self.matcher.knnMatch(
            descriptors,
            descriptors,
            k=2,
        )

        good_matches = []

        for pair in matches:
            if len(pair) < 2:
                continue

            first, second = pair

            # Avoid matching a feature with itself.
            if first.queryIdx == first.trainIdx:
                continue

            # Lowe's ratio test.
            if first.distance < (
                self.distance_ratio * second.distance
            ):
                good_matches.append(first)

        good_match_count = len(good_matches)

        match_ratio = (
            good_match_count / len(keypoints)
            if keypoints
            else 0.0
        )

        # Normalize the number of matching features.
        #
        # This is intentionally a simple heuristic for the MVP.
        normalized_matches = min(
            good_match_count / 50.0,
            1.0,
        )

        normalized_ratio = min(
            match_ratio / 0.10,
            1.0,
        )

        copy_move_score = (
            0.6 * normalized_matches
            + 0.4 * normalized_ratio
        )

        copy_move_score = float(
            max(
                0.0,
                min(
                    copy_move_score,
                    1.0,
                ),
            )
        )

        suspicious = (
            good_match_count >= self.min_matches
        )

        return {
            "keypoints": len(keypoints),
            "good_matches": good_match_count,
            "match_ratio": round(
                match_ratio,
                6,
            ),
            "copy_move_score": round(
                copy_move_score,
                4,
            ),
            "suspicious": suspicious,
            "status": "completed",
        }


def run_check(image):
    """
    Compatibility helper.

    Accepts either:
        - image file path
        - OpenCV / NumPy image
    """

    detector = CopyMoveDetector()

    return detector.detect(image)