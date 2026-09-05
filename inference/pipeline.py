from pathlib import Path

from document_detection.classifier import DocumentClassifier


class DocumentPipeline:
    """Main pipeline for document classification and routing."""

    def __init__(self):
        self.classifier = DocumentClassifier()

    def process(self, image_path: str) -> dict:
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(
                f"Input image not found: {image_path}"
            )

        # Stage 1: document classification
        classification = self.classifier.predict(str(image_path))

        document_type = classification["document_type"]
        confidence = classification["confidence"]

        # Stage 2: document-specific routing
        if document_type == "aadhaar":
            result = self._run_aadhaar(image_path)

        elif document_type == "passport":
            result = self._run_passport(image_path)

        else:
            raise ValueError(
                f"Unsupported document type: {document_type}"
            )

        return {
            "document_type": document_type,
            "document_classifier_confidence": confidence,
            "analysis": result,
        }

    def _run_aadhaar(self, image_path: Path) -> dict:
        from documents.aadhaar.pipeline import AadhaarPipeline

        pipeline = AadhaarPipeline()
        return pipeline.process(str(image_path))

    def _run_passport(self, image_path: Path) -> dict:
        from documents.passport.pipeline import PassportPipeline

        pipeline = PassportPipeline()

        return pipeline.process(str(image_path))