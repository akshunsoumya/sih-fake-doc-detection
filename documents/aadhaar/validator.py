import re
from datetime import datetime


class AadhaarValidator:
    """Validate OCR-extracted Aadhaar field values."""

    def validate_aadhaar_number(self, value: str) -> dict:
        """
        Validate Aadhaar number format and Verhoeff checksum.

        Returns:
            {
                "value": "...",
                "valid_format": True/False,
                "valid_checksum": True/False,
                "valid": True/False,
            }
        """

        if value is None:
            value = ""

        # Keep digits only.
        digits = re.sub(r"\D", "", value)

        # Aadhaar number must contain exactly 12 digits.
        valid_format = len(digits) == 12

        # Reject obviously invalid repeated digits.
        if valid_format and len(set(digits)) == 1:
            valid_format = False

        valid_checksum = False

        if valid_format:
            valid_checksum = self._verhoeff_check(digits)

        return {
            "value": digits,
            "valid_format": valid_format,
            "valid_checksum": valid_checksum,
            "valid": valid_format and valid_checksum,
        }

    def validate_dob(self, value: str) -> dict:
        """
        Validate date-of-birth format and whether the date exists.
        """

        if value is None:
            value = ""

        value = value.strip()

        # Accept DD/MM/YYYY or DD-MM-YYYY.
        date_pattern = r"^(\d{1,2})[/-](\d{1,2})[/-](\d{4})$"

        match = re.fullmatch(date_pattern, value)

        if not match:
            return {
                "value": value,
                "valid_format": False,
                "valid_date": False,
                "valid": False,
            }

        day, month, year = match.groups()

        try:
            datetime(
                int(year),
                int(month),
                int(day),
            )

            valid_date = True

        except ValueError:
            valid_date = False

        return {
            "value": value,
            "valid_format": True,
            "valid_date": valid_date,
            "valid": valid_date,
        }

    def validate_gender(self, value: str) -> dict:
        """Validate Aadhaar gender text."""

        if value is None:
            value = ""

        normalized = value.strip().upper()

        allowed_values = {
            "MALE",
            "FEMALE",
            "TRANSGENDER",
        }

        valid = normalized in allowed_values

        return {
            "value": normalized,
            "valid": valid,
        }

    def validate_name(self, value: str) -> dict:
        """Perform basic name validation."""

        if value is None:
            value = ""

        normalized = " ".join(value.strip().split())

        # Basic sanity checks.
        has_text = bool(normalized)
        has_reasonable_length = 2 <= len(normalized) <= 100

        valid = has_text and has_reasonable_length

        return {
            "value": normalized,
            "valid": valid,
        }

    def validate_fields(self, fields: dict) -> dict:
        """
        Validate all extracted Aadhaar fields.

        Example input:

            {
                "aadhaar_number": "123456789012",
                "dob": "01/01/2000",
                "name": "Rahul Kumar",
                "gender": "MALE"
            }
        """

        results = {}

        if "aadhaar_number" in fields:
            results["aadhaar_number"] = (
                self.validate_aadhaar_number(
                    fields["aadhaar_number"]
                )
            )

        if "dob" in fields:
            results["dob"] = self.validate_dob(
                fields["dob"]
            )

        if "gender" in fields:
            results["gender"] = self.validate_gender(
                fields["gender"]
            )

        if "name" in fields:
            results["name"] = self.validate_name(
                fields["name"]
            )

        return results

    @staticmethod
    def _verhoeff_check(number: str) -> bool:
        """
        Check Aadhaar number using the Verhoeff checksum algorithm.
        """

        multiplication_table = [
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
            [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
            [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
            [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
            [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
            [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
            [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
            [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
            [9, 8, 7, 6, 5, 4, 3, 2, 1, 0],
        ]

        permutation_table = [
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
            [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
            [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
            [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
            [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
            [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
            [7, 0, 4, 6, 9, 1, 3, 2, 5, 8],
        ]

        inverse_table = [
            0, 4, 3, 2, 1, 5, 6, 7, 8, 9
        ]

        checksum = 0

        reversed_digits = list(
            map(int, reversed(number))
        )

        for position, digit in enumerate(reversed_digits):
            checksum = multiplication_table[
                checksum
            ][
                permutation_table[position % 8][digit]
            ]

        return checksum == 0