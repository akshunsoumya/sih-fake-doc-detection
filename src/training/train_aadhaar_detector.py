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
RUNS = ROOT / "runs"


def main():
    if not DATA.exists():
        raise FileNotFoundError(
            f"{DATA} not found. "
            "Prepare the Aadhaar dataset first."
        )

    # Read the portable YAML.
    data_cfg = yaml.safe_load(DATA.read_text())

    # Resolve the dataset path locally.
    data_cfg["path"] = str(DATA.parent.resolve())

    # Create a temporary local YAML for Ultralytics.
    resolved_data = DATA.parent / "_data_local.yaml"
    resolved_data.write_text(yaml.safe_dump(data_cfg, sort_keys=False))

    try:
        model = YOLO("yolov8n.pt")

        model.train(
            data=str(resolved_data),
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

    finally:
        # Never leave the machine-specific YAML in the repository.
        if resolved_data.exists():
            resolved_data.unlink()

    best = RUNS / "aadhaar_fields" / "weights" / "best.pt"

    print(f"Best weights: {best}")


if __name__ == "__main__":
    main()