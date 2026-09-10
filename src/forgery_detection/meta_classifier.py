from pathlib import Path

import joblib
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

MODEL_PATH = (
    ROOT
    / "models"
    / "forgery"
    / "forgery_classifier.joblib"
)


class ForgeryClassifier:
    """
    Inference wrapper for the trained forensic Random Forest.

    Input:
        forensic feature dictionary

    Output:
        predicted forgery class and class probabilities
    """

    def __init__(self, model_path: Path = MODEL_PATH):
        if not model_path.exists():
            raise FileNotFoundError(
                f"Forgery classifier model not found: {model_path}"
            )

        artifact = joblib.load(model_path)

        self.model = artifact["model"]
        self.label_encoder = artifact["label_encoder"]
        self.feature_columns = artifact["feature_columns"]

    def predict(self, forensic_result: dict):
        """
        Predict forgery class from ForensicAnalyzer output.
        """

        signals = forensic_result["signals"]

        ela = signals["ela"]
        copy_move = signals["copy_move"]
        image_quality = signals["image_quality"]
        compression = signals["compression"]

        features = {
            "ela_score": ela.get(
                "forgery_score",
                0.0,
            ),
            "ela_max_error": ela.get(
                "max_block_error",
                0.0,
            ),
            "ela_spike_ratio": ela.get(
                "spike_ratio",
                0.0,
            ),

            "copy_move_score": copy_move.get(
                "copy_move_score",
                0.0,
            ),
            "keypoints": copy_move.get(
                "keypoints",
                0,
            ),
            "candidate_matches": copy_move.get(
                "candidate_matches",
                0,
            ),
            "geometric_matches": copy_move.get(
                "geometric_matches",
                0,
            ),
            "copy_move_match_ratio": copy_move.get(
                "match_ratio",
                0.0,
            ),

            "brightness": image_quality.get(
                "brightness",
                0.0,
            ),
            "contrast": image_quality.get(
                "contrast",
                0.0,
            ),
            "sharpness": image_quality.get(
                "sharpness",
                0.0,
            ),

            "jpeg_to_raw_ratio": compression.get(
                "jpeg_to_raw_ratio",
                0.0,
            ),
        }

        feature_vector = pd.DataFrame(
            [
                [
                    features[column]
                    for column in self.feature_columns
                ]
            ],
            columns=self.feature_columns,
        )

        predicted_encoded = self.model.predict(
            feature_vector
        )[0]

        probabilities = self.model.predict_proba(
            feature_vector
        )[0]

        predicted_class = (
            self.label_encoder.inverse_transform(
                [predicted_encoded]
            )[0]
        )

        class_probabilities = {}

        for encoded_class, probability in zip(
            self.model.classes_,
            probabilities,
        ):
            class_name = (
                self.label_encoder.inverse_transform(
                    [encoded_class]
                )[0]
            )

            class_probabilities[class_name] = round(
                float(probability),
                4,
            )

        confidence = float(
            max(probabilities)
        )

        return {
            "predicted_class": predicted_class,
            "confidence": round(
                confidence,
                4,
            ),
            "class_probabilities": class_probabilities,
            "status": "completed",
        }


def run_forgery_prediction(forensic_result: dict):
    """
    Convenience helper for forgery prediction.
    """

    classifier = ForgeryClassifier()

    return classifier.predict(
        forensic_result
    )
