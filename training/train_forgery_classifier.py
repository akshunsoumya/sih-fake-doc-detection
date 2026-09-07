from pathlib import Path

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder


ROOT = Path(__file__).resolve().parents[1]

DATA_FILE = ROOT / "datasets" / "forgery_features.csv"
MODEL_DIR = ROOT / "models" / "forgery"
MODEL_FILE = MODEL_DIR / "forgery_classifier.joblib"

RANDOM_STATE = 42

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


def main():
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Feature dataset not found: {DATA_FILE}"
        )

    print("=" * 70)
    print("FORGERY CLASSIFIER TRAINING")
    print("=" * 70)
    print(f"Dataset: {DATA_FILE}")
    print()

    dataframe = pd.read_csv(DATA_FILE)

    required_columns = FEATURE_COLUMNS + ["label"]

    missing_columns = [
        column
        for column in required_columns
        if column not in dataframe.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns: {missing_columns}"
        )

    dataframe = dataframe.dropna(
        subset=required_columns
    ).reset_index(drop=True)

    print(f"Total samples: {len(dataframe)}")
    print()
    print("Class distribution:")
    print(dataframe["label"].value_counts())
    print()

    X = dataframe[FEATURE_COLUMNS].copy()
    y_text = dataframe["label"].astype(str)

    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y_text)

    print("Classes:")
    for index, class_name in enumerate(
        label_encoder.classes_
    ):
        print(f"  {index}: {class_name}")

    print()

    # ---------------------------------------------------------
    # First split:
    # 80% development data
    # 20% independent test data
    # ---------------------------------------------------------

    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    # ---------------------------------------------------------
    # Second split:
    # 80% train
    # 20% validation
    #
    # Final proportions:
    # 64% train
    # 16% validation
    # 20% test
    # ---------------------------------------------------------

    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val,
        y_train_val,
        test_size=0.20,
        random_state=RANDOM_STATE,
        stratify=y_train_val,
    )

    print("Dataset split:")
    print(f"  Train      : {len(X_train)}")
    print(f"  Validation : {len(X_val)}")
    print(f"  Test       : {len(X_test)}")
    print()

    # ---------------------------------------------------------
    # Random Forest
    # ---------------------------------------------------------

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        class_weight="balanced",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    print("Training Random Forest...")
    model.fit(
        X_train,
        y_train,
    )

    print("Training complete.")
    print()

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    validation_predictions = model.predict(
        X_val
    )

    validation_accuracy = accuracy_score(
        y_val,
        validation_predictions,
    )

    print("=" * 70)
    print("VALIDATION RESULTS")
    print("=" * 70)
    print(
        f"Validation Accuracy: "
        f"{validation_accuracy:.4f}"
    )
    print()

    print(
        classification_report(
            y_val,
            validation_predictions,
            labels=list(range(len(label_encoder.classes_))),
            target_names=label_encoder.classes_,
            zero_division=0,
        )
    )

    # ---------------------------------------------------------
    # Independent test
    # ---------------------------------------------------------

    test_predictions = model.predict(
        X_test
    )

    test_accuracy = accuracy_score(
        y_test,
        test_predictions,
    )

    print("=" * 70)
    print("FINAL TEST RESULTS")
    print("=" * 70)
    print(
        f"Test Accuracy: "
        f"{test_accuracy:.4f}"
    )
    print()

    print("Classification Report:")
    print(
        classification_report(
            y_test,
            test_predictions,
            labels=list(range(len(label_encoder.classes_))),
            target_names=label_encoder.classes_,
            zero_division=0,
        )
    )

    print("Confusion Matrix:")

    matrix = confusion_matrix(
        y_test,
        test_predictions,
        labels=list(range(len(label_encoder.classes_))),
    )

    matrix_dataframe = pd.DataFrame(
        matrix,
        index=label_encoder.classes_,
        columns=label_encoder.classes_,
    )

    print(matrix_dataframe)
    print()

    # ---------------------------------------------------------
    # Feature importance
    # ---------------------------------------------------------

    print("=" * 70)
    print("FEATURE IMPORTANCE")
    print("=" * 70)

    feature_importance = pd.Series(
        model.feature_importances_,
        index=FEATURE_COLUMNS,
    ).sort_values(
        ascending=False
    )

    print(feature_importance)
    print()

    # ---------------------------------------------------------
    # Save model
    # ---------------------------------------------------------

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    artifact = {
        "model": model,
        "label_encoder": label_encoder,
        "feature_columns": FEATURE_COLUMNS,
    }

    joblib.dump(
        artifact,
        MODEL_FILE,
    )

    print("=" * 70)
    print("MODEL SAVED")
    print("=" * 70)
    print(f"Model: {MODEL_FILE}")
    print()
    print("DONE")


if __name__ == "__main__":
    main()