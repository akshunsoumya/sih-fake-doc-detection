from typing import Any, Dict


class ForgeryDecisionEngine:
    """
    Combines forensic analysis, forgery classifier output,
    and document validation information into a high-level decision.

    Important:
    Model confidence is NOT treated as fraud probability.
    """

    def __init__(
        self,
        suspicious_confidence: float = 0.60,
        forged_confidence: float = 0.85,
        anomaly_suspicious_threshold: float = 0.30,
        anomaly_forged_threshold: float = 0.60,
    ):
        self.suspicious_confidence = suspicious_confidence
        self.forged_confidence = forged_confidence
        self.anomaly_suspicious_threshold = anomaly_suspicious_threshold
        self.anomaly_forged_threshold = anomaly_forged_threshold

    def _extract_fields(
        self,
        document_analysis: Any,
    ) -> list:
        """
        Supports the current document pipeline format.

        Current Aadhaar detector returns:
            [
                {
                    "field": "...",
                    "confidence": ...,
                    "bbox": [...]
                }
            ]

        Future pipelines may return:
            {
                "fields": [...]
            }
        """

        if isinstance(document_analysis, list):
            return document_analysis

        if isinstance(document_analysis, dict):
            fields = document_analysis.get("fields", [])

            if isinstance(fields, list):
                return fields

        return []

    def _get_anomaly_score(
        self,
        forensic_analysis: Dict[str, Any],
    ) -> float:
        """
        Supports both current snake_case output and API-style
        camelCase output.
        """

        if not isinstance(forensic_analysis, dict):
            return 0.0

        if "combined_anomaly_score" in forensic_analysis:
            return float(
                forensic_analysis.get(
                    "combined_anomaly_score",
                    0.0,
                )
            )

        if "combinedAnomalyScore" in forensic_analysis:
            return float(
                forensic_analysis.get(
                    "combinedAnomalyScore",
                    0.0,
                )
            )

        return 0.0

    def _get_signals(
        self,
        forensic_analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Supports the current forensic analyzer structure.
        """

        if not isinstance(forensic_analysis, dict):
            return {}

        return forensic_analysis.get(
            "signals",
            {},
        )

    def evaluate(
        self,
        forensic_analysis: Dict[str, Any],
        forgery_assessment: Dict[str, Any],
        document_analysis: Any = None,
    ) -> Dict[str, Any]:

        if document_analysis is None:
            document_analysis = []

        # ----------------------------------------------------
        # Basic inputs
        # ----------------------------------------------------

        predicted_class = forgery_assessment.get(
            "predictedClass",
            "unknown",
        )

        model_confidence = float(
            forgery_assessment.get(
                "confidence",
                0.0,
            )
        )

        anomaly_score = self._get_anomaly_score(
            forensic_analysis
        )

        class_probabilities = forgery_assessment.get(
            "classProbabilities",
            {},
        )

        # ----------------------------------------------------
        # Document fields
        # ----------------------------------------------------

        fields = self._extract_fields(
            document_analysis
        )

        total_fields = len(fields)
        invalid_fields = 0

        for field in fields:

            validation = field.get(
                "validation",
                None,
            )

            if isinstance(validation, dict):
                if validation.get("valid") is False:
                    invalid_fields += 1

        # ----------------------------------------------------
        # Copy-move signal
        # ----------------------------------------------------

        signals = self._get_signals(
            forensic_analysis
        )

        copy_move = signals.get(
            "copy_move",
            signals.get(
                "copyMove",
                {},
            ),
        )

        if not isinstance(copy_move, dict):
            copy_move = {}

        copy_move_suspicious = bool(
            copy_move.get(
                "suspicious",
                False,
            )
        )

        # ----------------------------------------------------
        # Initial decision
        # ----------------------------------------------------

        overall_status = "genuine"
        decision = "accept"
        review_required = False

        reasons = []

        # ----------------------------------------------------
        # Strong forgery classifier evidence
        # ----------------------------------------------------

        if (
            predicted_class != "genuine"
            and model_confidence >= self.forged_confidence
        ):

            overall_status = "likely_forged"
            decision = "manual_review"
            review_required = True

            reasons.append(
                f"Forgery classifier strongly predicts "
                f"{predicted_class}."
            )

        # ----------------------------------------------------
        # Strong forensic anomaly
        # ----------------------------------------------------

        elif anomaly_score >= self.anomaly_forged_threshold:

            overall_status = "likely_forged"
            decision = "manual_review"
            review_required = True

            reasons.append(
                "High combined forensic anomaly detected."
            )

        # ----------------------------------------------------
        # Moderate forgery classifier evidence
        # ----------------------------------------------------

        elif (
            predicted_class != "genuine"
            and model_confidence >= self.suspicious_confidence
        ):

            overall_status = "suspicious"
            decision = "manual_review"
            review_required = True

            reasons.append(
                f"Forgery classifier predicts "
                f"{predicted_class} with moderate confidence."
            )

        # ----------------------------------------------------
        # Moderate forensic anomaly
        # ----------------------------------------------------

        elif anomaly_score >= self.anomaly_suspicious_threshold:

            overall_status = "suspicious"
            decision = "manual_review"
            review_required = True

            reasons.append(
                "Forensic analysis detected an elevated "
                "anomaly score."
            )

        # ----------------------------------------------------
        # Copy-move evidence
        # ----------------------------------------------------

        if copy_move_suspicious:

            if overall_status == "genuine":
                overall_status = "suspicious"

            decision = "manual_review"
            review_required = True

            reasons.append(
                "Copy-move detection produced suspicious evidence."
            )

        # ----------------------------------------------------
        # Invalid document fields
        # ----------------------------------------------------

        if invalid_fields > 0:

            if overall_status == "genuine":
                overall_status = "suspicious"

            decision = "manual_review"
            review_required = True

            reasons.append(
                f"{invalid_fields} of {total_fields} "
                f"extracted fields failed validation."
            )

        # ----------------------------------------------------
        # Genuine case
        # ----------------------------------------------------

        if (
            overall_status == "genuine"
            and predicted_class == "genuine"
            and anomaly_score < self.anomaly_suspicious_threshold
        ):

            reasons.append(
                "No strong forgery evidence detected."
            )

        # ----------------------------------------------------
        # Recommendation
        # ----------------------------------------------------

        if overall_status == "likely_forged":

            recommendation = (
                "Manual review required. Strong forgery "
                "evidence was detected."
            )

        elif overall_status == "suspicious":

            recommendation = (
                "Manual review recommended. Some forgery "
                "indicators were detected."
            )

        else:

            recommendation = (
                "No strong forgery indicators detected. "
                "Automated analysis completed."
            )

        # ----------------------------------------------------
        # Final decision object
        # ----------------------------------------------------

        return {
            "overallStatus": overall_status,
            "decision": decision,
            "reviewRequired": review_required,
            "predictedForgeryType": predicted_class,
            "modelConfidence": round(
                model_confidence,
                4,
            ),
            "combinedAnomalyScore": round(
                anomaly_score,
                4,
            ),
            "classProbabilities": class_probabilities,
            "validationSummary": {
                "totalFields": total_fields,
                "invalidFields": invalid_fields,
            },
            "reasons": reasons,
            "recommendation": recommendation,
            "status": "completed",
        }


def evaluate_forgery_decision(
    forensic_analysis: Dict[str, Any],
    forgery_assessment: Dict[str, Any],
    document_analysis: Any = None,
) -> Dict[str, Any]:

    engine = ForgeryDecisionEngine()

    return engine.evaluate(
        forensic_analysis=forensic_analysis,
        forgery_assessment=forgery_assessment,
        document_analysis=document_analysis,
    )