from documents.aadhaar.detector import AadhaarFieldDetector
from documents.aadhaar.ocr import AadhaarOCR
from documents.aadhaar.validator import AadhaarValidator


class AadhaarPipeline:
    """Run Aadhaar field detection, OCR, and validation."""

    def __init__(self):
        self.detector = AadhaarFieldDetector()
        self.ocr = AadhaarOCR()
        self.validator = AadhaarValidator()

    def process(self, image_path: str) -> dict:
        """
        Process an Aadhaar image.

        Steps:
            1. Detect Aadhaar fields.
            2. Extract text from each detected field.
            3. Validate extracted values.
            4. Return a structured result.
        """

        # --------------------------------------------------
        # Step 1: Detect fields
        # --------------------------------------------------
        detections = self.detector.detect(image_path)

        fields = {}

        # --------------------------------------------------
        # Step 2: OCR each detected field
        # --------------------------------------------------
        for detection in detections:
            field = detection["field"]
            confidence = detection["confidence"]
            bbox = detection["bbox"]

            text = self.ocr.extract_text(
                image_path,
                bbox,
                field,
            )

            fields[field] = {
                "text": text,
                "confidence": confidence,
                "bbox": bbox,
            }

        # --------------------------------------------------
        # Step 3: Prepare values for validation
        # --------------------------------------------------
        values = {
            field: data["text"]
            for field, data in fields.items()
        }

        # --------------------------------------------------
        # Step 4: Validate extracted values
        # --------------------------------------------------
        validation = self.validator.validate_fields(values)

        # --------------------------------------------------
        # Step 5: Combine OCR + validation results
        # --------------------------------------------------
        for field, validation_result in validation.items():

            if field in fields:
                fields[field]["validation"] = validation_result

        # --------------------------------------------------
        # Final result
        # --------------------------------------------------
        return {
            "document_type": "aadhaar",
            "fields": fields,
        }