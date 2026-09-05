import re
from pathlib import Path

import cv2
import pytesseract


class PassportOCR:
    """OCR utilities for passport documents and MRZ extraction."""

    def _load_image(self, image_path: str):
        image = cv2.imread(image_path)

        if image is None:
            raise ValueError(f"Could not read image: {image_path}")

        return image

    def extract_text(self, image_path: str) -> str:
        """Extract general passport text using Tesseract OCR."""

        image = self._load_image(image_path)

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        gray = cv2.resize(
            gray,
            None,
            fx=2,
            fy=2,
            interpolation=cv2.INTER_CUBIC,
        )

        _, threshold = cv2.threshold(
            gray,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU,
        )

        text = pytesseract.image_to_string(
            threshold,
            config="--psm 6",
        )

        return text.strip()

    def extract_mrz(self, image_path: str) -> list[str]:
        """
        Extract the two MRZ lines from a passport image.

        MRZ is normally located near the bottom of the passport page.
        Multiple preprocessing methods and Tesseract page segmentation
        modes are tried, then the most MRZ-like candidate is selected.
        """

        image = self._load_image(image_path)

        height, width = image.shape[:2]

        # Use a generous bottom region so MRZ characters are not cropped.
        mrz_region = image[int(height * 0.55):height, :]

        gray = cv2.cvtColor(
            mrz_region,
            cv2.COLOR_BGR2GRAY,
        )

        # Upscale the MRZ for better OCR.
        gray = cv2.resize(
            gray,
            None,
            fx=4,
            fy=4,
            interpolation=cv2.INTER_CUBIC,
        )

        variants = []

        # Original grayscale image.
        variants.append(gray)

        # Otsu threshold.
        _, otsu = cv2.threshold(
            gray,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU,
        )
        variants.append(otsu)

        # Adaptive threshold.
        adaptive = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            11,
        )
        variants.append(adaptive)

        all_candidates = []

        for variant in variants:
            for psm in (6, 7, 11, 13):
                text = pytesseract.image_to_string(
                    variant,
                    config=f"--psm {psm}",
                )

                candidates = self.extract_mrz_candidates(text)

                if len(candidates) >= 2:
                    all_candidates.append(candidates[:2])

        if not all_candidates:
            return []

        # Choose the candidate pair that looks most like a passport MRZ.
        best = max(
            all_candidates,
            key=self._mrz_score,
        )

        return best

    def extract_mrz_candidates(self, text: str) -> list[str]:
        """Extract MRZ-like lines from raw OCR output."""

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        candidates = []

        for line in lines:
            cleaned = re.sub(
                r"[^A-Z0-9<]",
                "",
                line.upper(),
            )

            # MRZ lines are normally long and contain '<' separators.
            if len(cleaned) >= 30 and "<" in cleaned:
                candidates.append(cleaned)

        return candidates

    def _mrz_score(self, lines: list[str]) -> float:
        """Score how likely a pair of lines is to be a passport MRZ."""

        if len(lines) != 2:
            return -1

        line1, line2 = lines

        score = 0.0

        # Passport MRZ normally starts with P<.
        if line1.startswith("P<"):
            score += 10

        # OCR may sometimes read P< as PD<.
        if line1.startswith("PD<"):
            score += 5

        # MRZ contains many '<' filler/separator characters.
        score += min(line1.count("<"), 15) * 0.5
        score += min(line2.count("<"), 15) * 0.5

        # Prefer lines close to the expected 44 characters.
        score -= abs(44 - len(line1))
        score -= abs(44 - len(line2))

        # The second MRZ line normally contains many digits.
        digit_count = sum(
            char.isdigit()
            for char in line2
        )

        score += min(digit_count, 15) * 0.5

        return score