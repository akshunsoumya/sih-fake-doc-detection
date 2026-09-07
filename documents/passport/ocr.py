import re
from pathlib import Path

import cv2
import pytesseract

from documents.passport.validator import PassportMRZValidator


class PassportOCR:
    """OCR utilities for passport documents and MRZ extraction."""

    def _load_image(self, image_path: str):
        image = cv2.imread(image_path)

        if image is None:
            raise ValueError(
                f"Could not read image: {image_path}"
            )

        return image

    def extract_text(self, image_path: str) -> str:
        """Extract general passport text using Tesseract OCR."""

        image = self._load_image(image_path)

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY,
        )

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

    def extract_fields(self, image_path: str) -> dict:
        """
        Extract common passport fields.

        General OCR is used first. MRZ is used as a fallback
        when a complete and structurally valid MRZ is available.
        """

        text = self.extract_text(image_path)

        fields = {
            "passport_number": None,
            "surname": None,
            "given_names": None,
            "nationality": None,
            "date_of_birth": None,
            "sex": None,
            "place_of_birth": None,
            "issue_date": None,
            "expiry_date": None,
        }

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        # ---------------------------------------------------------
        # Passport number
        # ---------------------------------------------------------

        for line in lines:
            normalized = line.lower()

            if (
                "passport no" in normalized
                or "passport no." in normalized
                or "passport number" in normalized
            ):
                candidates = re.findall(
                    r"\b[A-Z0-9$]{7,10}\b",
                    line.upper(),
                )

                for candidate in candidates:
                    candidate = candidate.replace(
                        "$",
                        "S",
                    )

                    if candidate == "PASSPORT":
                        continue

                    if any(
                        char.isdigit()
                        for char in candidate
                    ):
                        fields["passport_number"] = candidate
                        break

        # ---------------------------------------------------------
        # Surname
        # ---------------------------------------------------------

        for index, line in enumerate(lines):
            normalized = line.lower()

            if "surname" in normalized:
                candidates = []

                for next_index in range(
                    index + 1,
                    min(index + 5, len(lines)),
                ):
                    candidate = self._clean_name(
                        lines[next_index]
                    )

                    if candidate:
                        candidates.append(candidate)

                for candidate in candidates:
                    if candidate.upper() == candidate:
                        fields["surname"] = candidate
                        break

                if (
                    fields["surname"] is None
                    and candidates
                ):
                    fields["surname"] = candidates[0]

        # ---------------------------------------------------------
        # Given names
        # ---------------------------------------------------------

        for index, line in enumerate(lines):
            normalized = line.lower()

            if (
                normalized.startswith("name")
                or normalized.startswith("2.")
                or "name" in normalized
            ):
                if "nationality" in normalized:
                    continue

                candidates = []

                for next_index in range(
                    index + 1,
                    min(index + 5, len(lines)),
                ):
                    candidate = self._clean_name(
                        lines[next_index]
                    )

                    if candidate:
                        candidates.append(candidate)

                candidates = [
                    candidate
                    for candidate in candidates
                    if candidate.lower()
                    not in {
                        "name",
                        "surname",
                        "nationality",
                        "passport",
                    }
                ]

                for candidate in candidates:
                    if candidate.upper() == candidate:
                        fields["given_names"] = candidate
                        break

                if (
                    fields["given_names"] is None
                    and candidates
                ):
                    fields["given_names"] = candidates[0]

                if fields["given_names"] is not None:
                    break

        # ---------------------------------------------------------
        # Nationality
        # ---------------------------------------------------------

        for line in lines:
            normalized = line.lower()

            if "nationality" in normalized:
                match = re.search(
                    r"nationality\s*[:;]?\s*(.+)",
                    line,
                    re.IGNORECASE,
                )

                if match:
                    value = match.group(1).strip()

                    value = re.sub(
                        r"[^A-Za-z /-]",
                        "",
                        value,
                    ).strip()

                    if "/" in value:
                        parts = [
                            part.strip()
                            for part in value.split("/")
                            if part.strip()
                        ]

                        if parts:
                            value = parts[-1]

                    if value:
                        fields["nationality"] = value

        # ---------------------------------------------------------
        # Sex
        # ---------------------------------------------------------

        for line in lines:
            normalized = line.lower()

            if (
                "sex" in normalized
                or "gender" in normalized
            ):
                upper_line = line.upper()

                match = re.search(
                    r"(?:SEX|GENDER)\s*[:;]?\s*.*?\b([MF])\b",
                    upper_line,
                )

                if match:
                    fields["sex"] = match.group(1)
                    break

                match = re.search(
                    r"\b([MF])\b",
                    upper_line,
                )

                if match:
                    fields["sex"] = match.group(1)
                    break

        # ---------------------------------------------------------
        # Date of birth
        # ---------------------------------------------------------

        for line in lines:
            normalized = line.lower()

            if (
                "date of birth" in normalized
                or "birth" in normalized
            ):
                match = re.search(
                    r"(\d{1,2}\s+[A-Za-z]{3}\s+\d{2,4})",
                    line,
                )

                if match:
                    fields["date_of_birth"] = match.group(1)
                    break

        # ---------------------------------------------------------
        # Place of birth
        # ---------------------------------------------------------

        for line in lines:
            normalized = line.lower()

            if "place of birth" in normalized:
                match = re.search(
                    r"place of birth\s*[:;]?\s*(.+)",
                    line,
                    re.IGNORECASE,
                )

                if match:
                    value = self._clean_text(
                        match.group(1)
                    )

                    if value:
                        fields["place_of_birth"] = value
                        break

        # ---------------------------------------------------------
        # Issue date
        # ---------------------------------------------------------

        for line in lines:
            normalized = line.lower()

            if (
                "iss. date" in normalized
                or "issue date" in normalized
                or "date of issue" in normalized
            ):
                match = re.search(
                    r"(\d{1,2}\s+[A-Za-z]{3}\s+\d{2,4})",
                    line,
                )

                if match:
                    fields["issue_date"] = match.group(1)
                    break

        # ---------------------------------------------------------
        # Expiry date
        # ---------------------------------------------------------

        for line in lines:
            normalized = line.lower()

            if (
                "date of expiry" in normalized
                or "expiry" in normalized
                or "expiration" in normalized
            ):
                match = re.search(
                    r"(\d{1,2}\s+[A-Za-z]{3}\s+\d{2,4})",
                    line,
                )

                if match:
                    fields["expiry_date"] = match.group(1)
                    break

        # ---------------------------------------------------------
        # MRZ fallback
        # ---------------------------------------------------------

        mrz_lines = self.extract_mrz(image_path)

        if len(mrz_lines) == 2:
            mrz_fields = self._parse_mrz_basic(
                mrz_lines
            )

            if fields["passport_number"] is None:
                fields["passport_number"] = (
                    mrz_fields["passport_number"]
                )

            if fields["surname"] is None:
                fields["surname"] = (
                    mrz_fields["surname"]
                )

            if fields["given_names"] is None:
                fields["given_names"] = (
                    mrz_fields["given_names"]
                )

            if fields["nationality"] is None:
                fields["nationality"] = (
                    mrz_fields["nationality"]
                )

            if fields["date_of_birth"] is None:
                fields["date_of_birth"] = (
                    mrz_fields["date_of_birth"]
                )

            if fields["sex"] is None:
                fields["sex"] = (
                    mrz_fields["sex"]
                )

            if fields["expiry_date"] is None:
                fields["expiry_date"] = (
                    mrz_fields["expiry_date"]
                )

        return fields

    def _parse_mrz_basic(
        self,
        mrz_lines: list[str],
    ) -> dict:
        """
        Extract basic fields from a complete TD3 MRZ.

        Full MRZ validation remains the responsibility of
        PassportMRZValidator.
        """

        line1, line2 = mrz_lines

        result = {
            "passport_number": None,
            "surname": None,
            "given_names": None,
            "nationality": None,
            "date_of_birth": None,
            "sex": None,
            "expiry_date": None,
        }

        # Never parse incomplete MRZ as if it were complete.
        if len(line1) != 44 or len(line2) != 44:
            return result

        # ---------------------------------------------------------
        # Line 1
        #
        # P<XXX SURNAME << GIVEN<NAMES <<<<<<<<<<<<<
        # ---------------------------------------------------------

        name_section = line1[5:44]

        name_parts = name_section.split(
            "<<",
            1,
        )

        if name_parts:
            surname = (
                name_parts[0]
                .replace("<", " ")
                .strip()
            )

            if surname:
                result["surname"] = surname

        if len(name_parts) > 1:
            given_names = (
                name_parts[1]
                .replace("<", " ")
                .strip()
            )

            if given_names:
                result["given_names"] = (
                    given_names
                )

        # ---------------------------------------------------------
        # Line 2
        #
        # 0-8   passport number
        # 9     passport number check digit
        # 10-12 nationality
        # 13-18 date of birth
        # 19    DOB check digit
        # 20    sex
        # 21-26 expiry date
        # 27    expiry check digit
        # ---------------------------------------------------------

        passport_number = line2[0:9].replace(
            "<",
            "",
        )

        nationality = line2[10:13]

        date_of_birth = line2[13:19]

        sex = line2[20]

        expiry_date = line2[21:27]

        if passport_number:
            result["passport_number"] = (
                passport_number
            )

        if nationality:
            result["nationality"] = nationality

        if date_of_birth:
            result["date_of_birth"] = (
                date_of_birth
            )

        if sex in {"M", "F", "<"}:
            result["sex"] = sex

        if expiry_date:
            result["expiry_date"] = expiry_date

        return result

    def _clean_name(
        self,
        value: str,
    ) -> str:
        """Clean common OCR noise from a name."""

        value = re.sub(
            r"[^A-Za-zÀ-ÖØ-öø-ÿ' -]",
            "",
            value,
        )

        value = re.sub(
            r"\s+",
            " ",
            value,
        ).strip()

        return value

    def _clean_text(
        self,
        value: str,
    ) -> str:
        """Clean general OCR text."""

        value = re.sub(
            r"[^A-Za-zÀ-ÖØ-öø-ÿ' /-]",
            "",
            value,
        )

        value = re.sub(
            r"\s+",
            " ",
            value,
        ).strip()

        return value

    def extract_mrz(
        self,
        image_path: str,
    ) -> list[str]:
        """
        Extract the two MRZ lines from a passport image.

        Multiple preprocessing methods are tested. Candidate pairs
        are ranked using MRZ structure and check-digit validation.
        """

        image = self._load_image(image_path)

        height, width = image.shape[:2]

        # ---------------------------------------------------------
        # Multiple bottom-region crops.
        # ---------------------------------------------------------

        crop_ratios = [
            0.70,
            0.74,
            0.77,
            0.80,
        ]

        mrz_crops = []

        for ratio in crop_ratios:
            start_y = int(
                height * ratio
            )

            crop = image[
                start_y:height,
                0:width,
            ]

            if crop.size > 0:
                mrz_crops.append(crop)

        all_candidates = []

        whitelist = (
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "0123456789<"
        )

        # ---------------------------------------------------------
        # Generate OCR candidates.
        # ---------------------------------------------------------

        for crop in mrz_crops:

            gray = cv2.cvtColor(
                crop,
                cv2.COLOR_BGR2GRAY,
            )

            gray = cv2.resize(
                gray,
                None,
                fx=5,
                fy=5,
                interpolation=cv2.INTER_CUBIC,
            )

            clahe = cv2.createCLAHE(
                clipLimit=2.0,
                tileGridSize=(8, 8),
            )

            enhanced = clahe.apply(gray)

            variants = [
                gray,
                enhanced,
            ]

            # Otsu threshold.
            _, otsu = cv2.threshold(
                enhanced,
                0,
                255,
                cv2.THRESH_BINARY + cv2.THRESH_OTSU,
            )

            variants.append(otsu)

            # Adaptive threshold.
            adaptive = cv2.adaptiveThreshold(
                enhanced,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                31,
                11,
            )

            variants.append(adaptive)

            for variant in variants:

                for psm in (
                    6,
                    7,
                    11,
                    13,
                ):

                    config = (
                        f"--psm {psm} "
                        "-c "
                        f"tessedit_char_whitelist={whitelist}"
                    )

                    text = pytesseract.image_to_string(
                        variant,
                        config=config,
                    )

                    candidates = (
                        self.extract_mrz_candidates(
                            text
                        )
                    )

                    if len(candidates) >= 2:
                        all_candidates.append(
                            candidates[:2]
                        )

        if not all_candidates:
            return []

        validator = PassportMRZValidator()

        # ---------------------------------------------------------
        # Prefer a candidate that passes all MRZ checks.
        # ---------------------------------------------------------

        valid_candidates = []

        for candidate in all_candidates:
            validation = (
                validator.validate_candidate(
                    candidate
                )
            )

            if validation.get("valid") is True:
                valid_candidates.append(
                    candidate
                )

        if valid_candidates:
            return max(
                valid_candidates,
                key=self._mrz_score,
            )

        # ---------------------------------------------------------
        # No complete valid MRZ found.
        #
        # Return the strongest OCR candidate.
        # Validator will correctly report it as
        # incomplete/invalid.
        # ---------------------------------------------------------

        return max(
            all_candidates,
            key=self._mrz_score,
        )

    def extract_mrz_candidates(
        self,
        text: str,
    ) -> list[str]:
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

            if (
                len(cleaned) >= 30
                and "<" in cleaned
            ):
                candidates.append(cleaned)

        return candidates

    def _mrz_score(
        self,
        lines: list[str],
    ) -> float:
        """Score how likely a pair of lines is to be a passport MRZ."""

        if len(lines) != 2:
            return -1

        line1, line2 = lines

        score = 0.0

        # Passport MRZ normally starts with P<.
        if line1.startswith("P<"):
            score += 15

        # Some OCR outputs produce PD<.
        if line1.startswith("PD<"):
            score += 5

        # MRZ uses many filler '<' characters.
        score += min(
            line1.count("<"),
            20,
        ) * 0.5

        score += min(
            line2.count("<"),
            20,
        ) * 0.5

        # TD3 lines should be 44 characters.
        score -= abs(
            44 - len(line1)
        )

        score -= abs(
            44 - len(line2)
        )

        # Second MRZ line contains many digits.
        digit_count = sum(
            char.isdigit()
            for char in line2
        )

        score += min(
            digit_count,
            15,
        ) * 0.5

        # Penalize very short candidates.
        if len(line1) < 30:
            score -= 20

        if len(line2) < 30:
            score -= 20

        return score