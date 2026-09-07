from pathlib import Path

import cv2
import numpy as np


class CopyMoveDetector:
    """
    Copy-move forgery detector.

    A copy-move forgery happens when a region from an image
    is copied and pasted somewhere else in the SAME image.

    Accepts:
        - image file path
        - OpenCV / NumPy image

    This produces a forensic signal, not a final forgery decision.
    """

    def __init__(
        self,
        min_matches: int = 8,
        distance_ratio: float = 0.75,
        min_spatial_distance: float = 40.0,
    ):
        self.min_matches = min_matches
        self.distance_ratio = distance_ratio
        self.min_spatial_distance = min_spatial_distance

        self.sift = cv2.SIFT_create()

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
        """Accept either a file path or NumPy/OpenCV image."""

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
        """Run copy-move analysis."""

        image = self._load_image(image)

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY,
        )

        keypoints, descriptors = self.sift.detectAndCompute(
            gray,
            None,
        )

        if descriptors is None or len(keypoints) < 2:
            return {
                "keypoints": len(keypoints),
                "candidate_matches": 0,
                "geometric_matches": 0,
                "match_ratio": 0.0,
                "copy_move_score": 0.0,
                "suspicious": False,
                "status": "insufficient_features",
            }

        # Compare every feature with features from the same image.
        matches = self.matcher.knnMatch(
            descriptors,
            descriptors,
            k=2,
        )

        candidate_matches = []

        for pair in matches:
            if len(pair) < 2:
                continue

            first, second = pair

            # Never match a feature with itself.
            if first.queryIdx == first.trainIdx:
                continue

            # Lowe ratio test.
            if first.distance < (
                self.distance_ratio * second.distance
            ):
                candidate_matches.append(first)

        # ---------------------------------------------------------
        # Remove matches that are spatially too close.
        #
        # A genuine copy-move should appear in two different
        # locations in the same image.
        # ---------------------------------------------------------

        spatial_matches = []

        for match in candidate_matches:
            source = np.array(
                keypoints[match.queryIdx].pt,
                dtype=np.float32,
            )

            target = np.array(
                keypoints[match.trainIdx].pt,
                dtype=np.float32,
            )

            distance = float(
                np.linalg.norm(source - target)
            )

            if distance >= self.min_spatial_distance:
                spatial_matches.append(match)

        # ---------------------------------------------------------
        # Geometric consistency.
        #
        # If several matched points follow a similar transformation,
        # they are stronger evidence of a copied region.
        # ---------------------------------------------------------

        geometric_matches = []

        if len(spatial_matches) >= 4:
            source_points = np.float32(
                [
                    keypoints[m.queryIdx].pt
                    for m in spatial_matches
                ]
            ).reshape(-1, 1, 2)

            target_points = np.float32(
                [
                    keypoints[m.trainIdx].pt
                    for m in spatial_matches
                ]
            ).reshape(-1, 1, 2)

            matrix, mask = cv2.findHomography(
                source_points,
                target_points,
                cv2.RANSAC,
                5.0,
            )

            if matrix is not None and mask is not None:
                inlier_mask = mask.ravel().astype(bool)

                geometric_matches = [
                    match
                    for match, is_inlier
                    in zip(
                        spatial_matches,
                        inlier_mask,
                    )
                    if is_inlier
                ]

        geometric_count = len(geometric_matches)

        match_ratio = (
            geometric_count / len(keypoints)
            if keypoints
            else 0.0
        )

        # ---------------------------------------------------------
        # Simple MVP score.
        #
        # More geometrically consistent matches → higher score.
        # This is NOT a probability of forgery.
        # ---------------------------------------------------------

        normalized_matches = min(
            geometric_count / 30.0,
            1.0,
        )

        normalized_ratio = min(
            match_ratio / 0.05,
            1.0,
        )

        copy_move_score = (
            0.7 * normalized_matches
            + 0.3 * normalized_ratio
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
            geometric_count >= self.min_matches
        )

        return {
            "keypoints": len(keypoints),
            "candidate_matches": len(candidate_matches),
            "geometric_matches": geometric_count,
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
        - file path
        - OpenCV / NumPy image
    """

    detector = CopyMoveDetector()

    return detector.detect(image)