from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

FEATURES_CSV = ROOT / "datasets" / "forgery_features.csv"
MODEL_PATH = ROOT / "models" / "forgery" / "forgery_classifier.joblib"


# ============================================================
# FEATURES
# Must match the features used during training
# ============================================================

FEATURE_COLUMNS = [
    "ela_score",
    "ela_max_error",
    "ela_spike_ratio",
    "copy_move_score",
    "keypoints",
    "candidate_matches",
    "geometric_matches",
    "copy_move_match_ratio",
    "brightness",
    "contrast",
    "sharpness",
    "jpeg_to_raw_ratio",
]


RANDOM_STATE = 42
TEST_SIZE = 0.20
VALIDATION_SIZE_FROM_REMAINING = 0.20


# ============================================================
# HELPERS
# ============================================================
def decode_predictions(predictions, model):
    """
    Convert numeric model predictions back to string class labels.

    Expected mapping:
        0 -> copy_move
        1 -> double_compress
        2 -> genuine
        3 -> recompress
        4 -> retype
        5 -> splice
    """

    class_names = [
        "copy_move",
        "double_compress",
        "genuine",
        "recompress",
        "retype",
        "splice",
    ]

    decoded = []

    for prediction in predictions:
        prediction = int(prediction)

        if prediction < 0 or prediction >= len(class_names):
            raise ValueError(
                f"Unknown model class index: {prediction}"
            )

        decoded.append(class_names[prediction])

    return np.array(decoded)

def print_section(title):
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def load_data():
    if not FEATURES_CSV.exists():
        raise FileNotFoundError(
            f"Feature CSV not found:\n{FEATURES_CSV}"
        )

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Forgery classifier model not found:\n{MODEL_PATH}"
        )

    df = pd.read_csv(FEATURES_CSV)

    required_columns = FEATURE_COLUMNS + ["label"]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required columns in feature CSV:\n"
            + "\n".join(missing_columns)
        )

    return df


def load_classifier():
    """
    Load the saved forgery classifier.

    The joblib file may contain either:
    1. The classifier directly, or
    2. A dictionary/checkpoint containing the classifier.
    """

    checkpoint = joblib.load(MODEL_PATH)

    print(f"Loaded object type: {type(checkpoint).__name__}")

    # --------------------------------------------------------
    # Case 1: direct sklearn model
    # --------------------------------------------------------

    if hasattr(checkpoint, "predict"):
        print("Detected direct sklearn classifier.")
        return checkpoint

    # --------------------------------------------------------
    # Case 2: dictionary/checkpoint
    # --------------------------------------------------------

    if isinstance(checkpoint, dict):

        print("Detected dictionary/checkpoint.")

        print("Checkpoint keys:")
        for key in checkpoint.keys():
            print(f"  - {key}")

        # Most likely keys
        possible_model_keys = [
            "model",
            "classifier",
            "estimator",
            "clf",
            "random_forest",
            "random_forest_classifier",
        ]

        for key in possible_model_keys:
            if key in checkpoint:
                candidate = checkpoint[key]

                if hasattr(candidate, "predict"):
                    print(
                        f"Using classifier stored under key: '{key}'"
                    )
                    return candidate

        # ----------------------------------------------------
        # Generic fallback:
        # search every dictionary value for sklearn model
        # ----------------------------------------------------

        for key, value in checkpoint.items():
            if hasattr(value, "predict"):
                print(
                    f"Using classifier stored under key: '{key}'"
                )
                return value

        raise TypeError(
            "The joblib file contains a dictionary, but no "
            "object with a .predict() method was found.\n"
            f"Available keys: {list(checkpoint.keys())}"
        )

    raise TypeError(
        "Unsupported saved model type: "
        f"{type(checkpoint).__name__}"
    )


def create_same_split(df):
    """
    Recreate the deterministic 64/16/20 split.

    80% development + 20% test
    Development -> 80% train + 20% validation
    """

    X = df[FEATURE_COLUMNS]
    y = df["label"]

    X_development, X_test, y_development, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        stratify=y,
        random_state=RANDOM_STATE,
    )

    X_train, X_validation, y_train, y_validation = train_test_split(
        X_development,
        y_development,
        test_size=VALIDATION_SIZE_FROM_REMAINING,
        stratify=y_development,
        random_state=RANDOM_STATE,
    )

    return (
        X_train,
        X_validation,
        X_test,
        y_train,
        y_validation,
        y_test,
    )


def calculate_per_class_accuracy(y_true, y_pred, labels):
    results = {}

    y_true_array = np.array(y_true)
    y_pred_array = np.array(y_pred)

    for label in labels:

        mask = y_true_array == label

        if mask.sum() == 0:
            results[label] = None
        else:
            results[label] = float(
                np.mean(y_pred_array[mask] == label)
            )

    return results


# ============================================================
# MAIN
# ============================================================

def main():

    print_section("FORGERY CLASSIFIER EVALUATION")

    print(f"Project root : {ROOT}")
    print(f"Features CSV : {FEATURES_CSV}")
    print(f"Model        : {MODEL_PATH}")

    # --------------------------------------------------------
    # Load dataset
    # --------------------------------------------------------

    df = load_data()

    print_section("DATASET")

    print(f"Total samples: {len(df)}")

    print()
    print("Class distribution:")
    print(df["label"].value_counts().sort_index())

    # --------------------------------------------------------
    # Split dataset
    # --------------------------------------------------------

    (
        X_train,
        X_validation,
        X_test,
        y_train,
        y_validation,
        y_test,
    ) = create_same_split(df)

    print_section("DATA SPLIT")

    print(f"Training samples   : {len(X_train)}")
    print(f"Validation samples : {len(X_validation)}")
    print(f"Test samples       : {len(X_test)}")

    # --------------------------------------------------------
    # Load classifier
    # --------------------------------------------------------

    print_section("LOADING MODEL")

    model = load_classifier()

    print()
    print(f"Final classifier type: {type(model).__name__}")

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    validation_predictions = model.predict(X_validation)
    validation_predictions = decode_predictions(
    validation_predictions,
    model
)

    validation_accuracy = accuracy_score(
        y_validation,
        validation_predictions,
    )

    print_section("VALIDATION RESULT")

    print(
        f"Validation Accuracy: "
        f"{validation_accuracy:.4f} "
        f"({validation_accuracy * 100:.2f}%)"
    )

    # --------------------------------------------------------
    # Test
    # --------------------------------------------------------

    test_predictions = model.predict(X_test)
    test_predictions = decode_predictions(
    test_predictions,
    model
)

    test_accuracy = accuracy_score(
        y_test,
        test_predictions,
    )

    print_section("FINAL TEST RESULT")

    print(
        f"Test Accuracy: "
        f"{test_accuracy:.4f} "
        f"({test_accuracy * 100:.2f}%)"
    )

    # --------------------------------------------------------
    # Classification report
    # --------------------------------------------------------

    labels = sorted(
        set(y_test.unique())
        | set(np.unique(test_predictions))
    )

    print_section("CLASSIFICATION REPORT")

    print(
        classification_report(
            y_test,
            test_predictions,
            labels=labels,
            zero_division=0,
        )
    )

    # --------------------------------------------------------
    # Confusion matrix
    # --------------------------------------------------------

    matrix = confusion_matrix(
        y_test,
        test_predictions,
        labels=labels,
    )

    print_section("CONFUSION MATRIX")

    print("Rows = Actual")
    print("Columns = Predicted")
    print()

    header = "Actual \\ Predicted".ljust(22)

    for label in labels:
        header += str(label).ljust(18)

    print(header)
    print("-" * len(header))

    for label, row in zip(labels, matrix):

        line = str(label).ljust(22)

        for value in row:
            line += str(value).ljust(18)

        print(line)

    # --------------------------------------------------------
    # Per-class accuracy
    # --------------------------------------------------------

    per_class_accuracy = calculate_per_class_accuracy(
        y_test,
        test_predictions,
        labels,
    )

    print_section("PER-CLASS ACCURACY")

    for label, accuracy in per_class_accuracy.items():

        if accuracy is None:
            print(f"{label}: No test samples")

        else:
            print(
                f"{label}: "
                f"{accuracy:.4f} "
                f"({accuracy * 100:.2f}%)"
            )

    # --------------------------------------------------------
    # Genuine false-positive analysis
    # --------------------------------------------------------

    genuine_mask = np.array(y_test) == "genuine"

    if genuine_mask.sum() > 0:

        genuine_predictions = np.array(
            test_predictions
        )[genuine_mask]

        genuine_false_positives = np.sum(
            genuine_predictions != "genuine"
        )

        genuine_total = genuine_mask.sum()

        false_positive_rate = (
            genuine_false_positives / genuine_total
        )

        print_section("GENUINE FALSE-POSITIVE ANALYSIS")

        print(
            f"Actual genuine samples       : "
            f"{genuine_total}"
        )

        print(
            f"Correctly predicted genuine : "
            f"{genuine_total - genuine_false_positives}"
        )

        print(
            f"Flagged as forgery           : "
            f"{genuine_false_positives}"
        )

        print(
            f"Genuine false-positive rate  : "
            f"{false_positive_rate:.4f} "
            f"({false_positive_rate * 100:.2f}%)"
        )

    # --------------------------------------------------------
    # Confidence analysis
    # --------------------------------------------------------

    if hasattr(model, "predict_proba"):

        probabilities = model.predict_proba(X_test)

        max_confidence = probabilities.max(axis=1)

        print_section("MODEL CONFIDENCE")

        print(
            f"Average confidence : "
            f"{max_confidence.mean():.4f} "
            f"({max_confidence.mean() * 100:.2f}%)"
        )

        print(
            f"Minimum confidence : "
            f"{max_confidence.min():.4f} "
            f"({max_confidence.min() * 100:.2f}%)"
        )

        print(
            f"Maximum confidence : "
            f"{max_confidence.max():.4f} "
            f"({max_confidence.max() * 100:.2f}%)"
        )

        low = np.sum(max_confidence < 0.60)

        medium = np.sum(
            (max_confidence >= 0.60)
            & (max_confidence < 0.80)
        )

        high = np.sum(max_confidence >= 0.80)

        print()
        print(f"Low confidence (<60%)       : {low}")
        print(f"Medium confidence (60-80%)  : {medium}")
        print(f"High confidence (>=80%)     : {high}")

    # --------------------------------------------------------
    # Final summary
    # --------------------------------------------------------

    print_section("FINAL SUMMARY")

    print(
        f"Test Accuracy : "
        f"{test_accuracy * 100:.2f}%"
    )

    print(
        f"Test Samples  : "
        f"{len(X_test)}"
    )

    print(
        f"Classes       : "
        f"{len(labels)}"
    )

    print()
    print("Classes evaluated:")

    for label in labels:
        print(f"  - {label}")

    print()
    print(
        "IMPORTANT:"
    )
    print(
        "This evaluation uses the current controlled/synthetic "
        "forgery dataset."
    )
    print(
        "The result must NOT be interpreted as real-world "
        "fraud detection accuracy."
    )

    print()
    print("Evaluation completed successfully.")


if __name__ == "__main__":
    main()