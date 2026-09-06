import re


class PassportMRZValidator:
    """Validate TD3 passport MRZ data."""

    WEIGHTS = [7, 3, 1]

    def _char_value(self, char: str) -> int:
        if char == "<":
            return 0

        if char.isdigit():
            return int(char)

        if "A" <= char <= "Z":
            return ord(char) - ord("A") + 10

        raise ValueError(f"Invalid MRZ character: {char}")

    def _check_digit(self, value: str) -> int:
        total = 0

        for index, char in enumerate(value):
            total += (
                self._char_value(char)
                * self.WEIGHTS[index % 3]
            )

        return total % 10

    def validate(self, mrz_lines: list[str]) -> dict:
        if len(mrz_lines) != 2:
            return {
                "status": "incomplete",
                "valid": False,
                "error": "Could not extract two MRZ lines.",
            }

        line1 = mrz_lines[0].strip().upper()
        line2 = mrz_lines[1].strip().upper()

        lengths = [len(line1), len(line2)]

        if lengths != [44, 44]:
            return {
                "status": "incomplete",
                "valid": False,
                "error": "MRZ OCR output is incomplete.",
                "line_lengths": lengths,
                "expected_lengths": [44, 44],
                "mrz_lines": [line1, line2],
            }

        if not re.fullmatch(r"[A-Z0-9<]{44}", line1):
            return {
                "status": "invalid",
                "valid": False,
                "error": "Invalid characters in MRZ line 1.",
            }

        if not re.fullmatch(r"[A-Z0-9<]{44}", line2):
            return {
                "status": "invalid",
                "valid": False,
                "error": "Invalid characters in MRZ line 2.",
            }

        document_code = line1[:2]
        names = line1[5:44]

        passport_number = line2[0:9]
        passport_number_check = line2[9]

        nationality = line2[10:13]

        date_of_birth = line2[13:19]
        date_of_birth_check = line2[19]

        sex = line2[20]

        expiry_date = line2[21:27]
        expiry_date_check = line2[27]

        optional_data = line2[28:42]

        final_check_digit = line2[43]

        passport_number_valid = (
            passport_number_check.isdigit()
            and self._check_digit(passport_number)
            == int(passport_number_check)
        )

        dob_valid = (
            date_of_birth_check.isdigit()
            and self._check_digit(date_of_birth)
            == int(date_of_birth_check)
        )

        expiry_valid = (
            expiry_date_check.isdigit()
            and self._check_digit(expiry_date)
            == int(expiry_date_check)
        )

        final_data = (
            passport_number
            + passport_number_check
            + date_of_birth
            + date_of_birth_check
            + expiry_date
            + expiry_date_check
            + optional_data
        )

        final_valid = (
            final_check_digit.isdigit()
            and self._check_digit(final_data)
            == int(final_check_digit)
        )

        overall_valid = (
            passport_number_valid
            and dob_valid
            and expiry_valid
            and final_valid
        )

        return {
            "status": "valid" if overall_valid else "invalid",
            "valid": overall_valid,
            "document_code": document_code,
            "nationality": nationality,
            "sex": sex,
            "passport_number": passport_number,
            "date_of_birth": date_of_birth,
            "expiry_date": expiry_date,
            "name_raw": names,
            "checks": {
                "passport_number": passport_number_valid,
                "date_of_birth": dob_valid,
                "expiry_date": expiry_valid,
                "final": final_valid,
            },
            "mrz_lines": [line1, line2],
        }