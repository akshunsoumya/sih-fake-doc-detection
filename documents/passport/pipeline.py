from documents.passport.ocr import PassportOCR
from documents.passport.validator import PassportMRZValidator


class PassportPipeline:
    """Run Passport OCR and MRZ validation."""

    def __init__(self):
        self.ocr = PassportOCR()
        self.validator = PassportMRZValidator()

    def process(self, image_path: str) -> dict:
        text = self.ocr.extract_text(image_path)

        mrz_lines = self.ocr.extract_mrz(image_path)

        validation = self.validator.validate(mrz_lines)

        return {
            "document_type": "passport",
            "ocr_text": text,
            "mrz": {
                "lines": mrz_lines,
                "validation": validation,
            },
        }