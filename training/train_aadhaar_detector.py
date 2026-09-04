"""Train the Aadhaar field detector.

This model performs Aadhaar FIELD LOCALIZATION, not forgery classification.

Expected dataset:
    datasets/aadhaar_entities/data.yaml

Training outputs:
    runs/aadhaar_fields/
"""

from pathlib import Path

import yaml
from ultralytics import YOLO


ROOT = Path(__file__).resolve().parents[1]

DATA = ROOT / "datasets" / "aadhaar_entities" / "data.yaml"
DATASET_DIR = DATA.parent
RUNS = ROOT / "runs"


def main():
    if not DATA.exists():
        raise FileNotFoundError(
            f"{DATA} not found. "
            "Prepare the Aadhaar dataset first."
        )

    # Keep data.yaml portable.
    # Resolve its dataset path from this repository at runtime.
    data_cfg = yaml.safe_load(DATA.read_text())
    data_cfg["path"] = str(DATASET_DIR)

    model = YOLO("yolov8n.pt")

    model.train(
        data=data_cfg,
        epochs=50,
        imgsz=640,
        batch=8,
        workers=2,
        patience=10,
        project=str(RUNS),
        name="aadhaar_fields",
        exist_ok=True,
        pretrained=True,
        device="mps",
    )

    best = RUNS / "aadhaar_fields" / "weights" / "best.pt"

    print(f"Best weights: {best}")


if __name__ == "__main__":
    main()