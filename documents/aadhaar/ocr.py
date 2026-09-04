import cv2
import pytesseract


class AadhaarOCR:
    """Extract text from detected Aadhaar field crops."""

    def __init__(self):
        self.tesseract_cmd = "tesseract"

    def extract_text(self, image_path: str, bbox, field: str) -> str:
        """
        Crop a detected Aadhaar field and extract text using Tesseract.

        bbox format:
            [x1, y1, x2, y2]
        """

        image = cv2.imread(str(image_path))

        if image is None:
            raise FileNotFoundError(
                f"Could not read image: {image_path}"
            )

        x1, y1, x2, y2 = map(int, bbox)

        # Keep coordinates inside the image.
        height, width = image.shape[:2]

        x1 = max(0, min(x1, width - 1))
        x2 = max(0, min(x2, width))
        y1 = max(0, min(y1, height - 1))
        y2 = max(0, min(y2, height))

        if x2 <= x1 or y2 <= y1:
            return ""

        # Crop the detected field.
        crop = image[y1:y2, x1:x2]

        # Enlarge the crop to help OCR.
        crop = cv2.resize(
            crop,
            None,
            fx=3,
            fy=3,
            interpolation=cv2.INTER_CUBIC,
        )

        # Convert to grayscale.
        gray = cv2.cvtColor(
            crop,
            cv2.COLOR_BGR2GRAY,
        )

        # Light denoising.
        gray = cv2.GaussianBlur(
            gray,
            (3, 3),
            0,
        )

        # Different OCR configuration depending on the field.
        if field == "aadhaar_number":
            config = (
                "--psm 7 "
                "-c tessedit_char_whitelist=0123456789"
            )

            text = pytesseract.image_to_string(
                gray,
                config=config,
            )

            return text.strip()

        elif field == "dob":
            config = (
                "--psm 7 "
                "-c tessedit_char_whitelist=0123456789/-"
            )

            # OCR attempt 1: grayscale image.
            text1 = pytesseract.image_to_string(
                gray,
                config=config,
            ).strip()

            # OCR attempt 2: thresholded image.
            _, threshold = cv2.threshold(
                gray,
                0,
                255,
                cv2.THRESH_BINARY + cv2.THRESH_OTSU,
            )

            text2 = pytesseract.image_to_string(
                threshold,
                config=config,
            ).strip()

            # Prefer the result that looks like a date.
            import re

            date_pattern = r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}"

            if re.fullmatch(date_pattern, text2):
                return text2

            if re.fullmatch(date_pattern, text1):
                return text1

            # If neither result matches the expected date
            # format, return the first result for debugging.
            return text1

        else:
            config = "--psm 7"

            text = pytesseract.image_to_string(
                gray,
                config=config,
            )

            return text.strip()