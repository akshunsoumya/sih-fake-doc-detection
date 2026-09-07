from pathlib import Path
from typing import Any, Dict

from document_detection.classifier import DocumentClassifier
from forgery_detection.forensic_features import ForensicAnalyzer
from forgery_detection.meta_classifier import ForgeryClassifier
from forgery_detection.decision_engine import ForgeryDecisionEngine


class DocumentForgeryPipeline:
    """
    End-to-end document forgery detection pipeline.

    Flow:
        Image
          ↓
        Document Classification
          ↓
        Document-specific OCR / Validation
          ↓
        Forensic Analysis
          ↓
        Forgery Classification
          ↓
        Decision Engine
          ↓
        Final JSON
    """

    def __init__(self):
        self.document_classifier = DocumentClassifier()
        self.forensic_analyzer = ForensicAnalyzer()
        self.forgery_classifier = ForgeryClassifier()
        self.decision_engine = ForgeryDecisionEngine()

    def _analyze_aadhaar(self, image_path: str) -> Dict[str, Any]:
        """
        Run Aadhaar-specific field detection, OCR and validation.
        """

        try:
            from documents.aadhaar.detector import AadhaarFieldDetector

            detector = AadhaarFieldDetector()

            result = detector.detect(image_path)

            return result

        except Exception as exc:
            return {
                "status": "error",
                "fields": [],
                "error": str(exc),
            }

    def _analyze_passport(self, image_path: str) -> Dict[str, Any]:
        """
        Run Passport-specific OCR and validation.
        """

        try:
            from documents.passport.ocr import PassportOCR

            ocr = PassportOCR()

            result = ocr.extract(image_path)

            return result

        except Exception as exc:
            return {
                "status": "error",
                "error": str(exc),
            }

    def _analyze_document(
        self,
        image_path: str,
        document_type: str,
    ) -> Dict[str, Any]:

        if document_type == "aadhaar":
            return self._analyze_aadhaar(image_path)

        if document_type == "passport":
            return self._analyze_passport(image_path)

        return {
            "status": "unsupported",
            "error": (
                f"No document-specific pipeline available "
                f"for document type: {document_type}"
            ),
        }

    def run(self, image_path: str) -> Dict[str, Any]:
        """
        Run the complete document forgery detection pipeline.
        """

        image_path = str(Path(image_path).resolve())

        # ====================================================
        # STEP 1: DOCUMENT CLASSIFICATION
        # ====================================================

        try:
            classification = self.document_classifier.predict(
                image_path
            )

        except Exception as exc:
            return {
                "status": "error",
                "error": f"Document classification failed: {exc}",
            }

        document_type = classification.get(
            "document_type",
            "unknown",
        )

        document_confidence = float(
            classification.get(
                "confidence",
                0.0,
            )
        )

        # ====================================================
        # STEP 2: DOCUMENT-SPECIFIC ANALYSIS
        # ====================================================

        document_analysis = self._analyze_document(
            image_path=image_path,
            document_type=document_type,
        )

        # ====================================================
        # STEP 3: FORENSIC ANALYSIS
        # ====================================================

        try:
            forensic_analysis = self.forensic_analyzer.analyze(
                image_path
            )

        except Exception as exc:
            forensic_analysis = {
                "status": "error",
                "signals": {},
                "combined_anomaly_score": 0.0,
                "error": str(exc),
            }

        # ====================================================
        # STEP 4: FORGERY CLASSIFICATION
        # ====================================================

        try:
            forgery_raw = self.forgery_classifier.predict(
                forensic_analysis
            )

            # Convert current classifier output to API format.
            forgery_assessment = {
                "predictedClass": forgery_raw.get(
                    "predicted_class",
                    "unknown",
                ),
                "confidence": forgery_raw.get(
                    "confidence",
                    0.0,
                ),
                "classProbabilities": forgery_raw.get(
                    "class_probabilities",
                    {},
                ),
                "status": forgery_raw.get(
                    "status",
                    "completed",
                ),
            }

        except Exception as exc:
            forgery_assessment = {
                "predictedClass": "unknown",
                "confidence": 0.0,
                "classProbabilities": {},
                "status": "error",
                "error": str(exc),
            }

        # ====================================================
        # STEP 5: DECISION ENGINE
        # ====================================================

        try:
            decision = self.decision_engine.evaluate(
                forensic_analysis=forensic_analysis,
                forgery_assessment=forgery_assessment,
                document_analysis=document_analysis,
            )

        except Exception as exc:
            decision = {
                "overallStatus": "unknown",
                "decision": "manual_review",
                "reviewRequired": True,
                "predictedForgeryType": forgery_assessment.get(
                    "predictedClass",
                    "unknown",
                ),
                "modelConfidence": forgery_assessment.get(
                    "confidence",
                    0.0,
                ),
                "combinedAnomalyScore": forensic_analysis.get(
                    "combinedAnomalyScore",
                    0.0,
                ),
                "classProbabilities": forgery_assessment.get(
                    "classProbabilities",
                    {},
                ),
                "validationSummary": {
                    "totalFields": 0,
                    "invalidFields": 0,
                },
                "reasons": [
                    f"Decision engine failed: {exc}"
                ],
                "recommendation": (
                    "Manual review required because "
                    "automated decision could not be completed."
                ),
                "status": "error",
            }

        # ====================================================
        # STEP 6: FINAL RESPONSE
        # ====================================================

        return {
            "document": {
                "documentType": document_type,
                "classifierConfidence": document_confidence,
            },

            "documentAnalysis": document_analysis,

            "forensicAnalysis": forensic_analysis,

            "forgeryAssessment": forgery_assessment,

            "decision": decision,

            "status": "completed",

            "error": None,
        }


def run_pipeline(image_path: str) -> Dict[str, Any]:
    """
    Convenience function for running the complete pipeline.
    """

    pipeline = DocumentForgeryPipeline()

    return pipeline.run(image_path)