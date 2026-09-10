from pathlib import Path

import pandas as pd

from forgery_detection.forensic_features import ForensicAnalyzer


ROOT = Path(__file__).resolve().parents[1]

DATASET_ROOT = ROOT / "datasets" / "forgery"
OUTPUT_FILE = ROOT / "datasets" / "forgery_features.csv"

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
}


def get_label(image_path: Path):
    parent_name = image_path.parent.name.lower()

    if parent_name == "genuine":
        return "genuine"

    filename = image_path.stem.lower()

    if "copy_move" in filename:
        return "copy_move"

    if "double_compress" in filename:
        return "double_compress"

    if "recompress" in filename:
        return "recompress"

    if "splice" in filename:
        return "splice"

    if "retype" in filename:
        return "retype"

    return None


def extract_features(analyzer, image_path: Path):
    result = analyzer.analyze(str(image_path))

    ela = result["signals"]["ela"]
    copy_move = result["signals"]["copy_move"]
    image_quality = result["signals"]["image_quality"]
    compression = result["signals"]["compression"]

    return {
        "image_path": str(image_path.relative_to(ROOT)),
        "label": get_label(image_path),

        "ela_score": ela.get("forgery_score", 0.0),
        "ela_max_error": ela.get("max_block_error", 0.0),
        "ela_spike_ratio": ela.get("spike_ratio", 0.0),

        "copy_move_score": copy_move.get("copy_move_score", 0.0),
        "keypoints": copy_move.get("keypoints", 0),
        "candidate_matches": copy_move.get("candidate_matches", 0),
        "geometric_matches": copy_move.get("geometric_matches", 0),
        "copy_move_match_ratio": copy_move.get("match_ratio", 0.0),

        "brightness": image_quality.get("brightness", 0.0),
        "contrast": image_quality.get("contrast", 0.0),
        "sharpness": image_quality.get("sharpness", 0.0),

        "jpeg_to_raw_ratio": compression.get(
            "jpeg_to_raw_ratio",
            0.0,
        ),
    }


def main():
    if not DATASET_ROOT.exists():
        raise FileNotFoundError(
            f"Forgery dataset not found: {DATASET_ROOT}"
        )

    image_paths = sorted(
        path
        for path in DATASET_ROOT.rglob("*")
        if (
            path.is_file()
            and path.suffix.lower() in IMAGE_EXTENSIONS
        )
    )

    if not image_paths:
        raise RuntimeError(
            f"No images found in {DATASET_ROOT}"
        )

    print("=" * 70)
    print("FORENSIC FEATURE EXTRACTION")
    print("=" * 70)
    print(f"Dataset : {DATASET_ROOT}")
    print(f"Images  : {len(image_paths)}")
    print(f"Output  : {OUTPUT_FILE}")
    print()

    analyzer = ForensicAnalyzer()

    rows = []
    failed = []

    for index, image_path in enumerate(
        image_paths,
        start=1,
    ):
        label = get_label(image_path)

        if label is None:
            print(f"[SKIP] Unknown label: {image_path}")
            continue

        print(
            f"[{index}/{len(image_paths)}] "
            f"{label:16s} "
            f"{image_path.name}",
            flush=True,
        )

        try:
            row = extract_features(
                analyzer,
                image_path,
            )
            rows.append(row)

        except Exception as exc:
            print(
                f"    ERROR: {exc}",
                flush=True,
            )
            failed.append(
                {
                    "image_path": str(image_path),
                    "error": str(exc),
                }
            )

    if not rows:
        raise RuntimeError(
            "No forensic features were extracted."
        )

    dataframe = pd.DataFrame(rows)

    dataframe.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print()
    print("=" * 70)
    print("EXTRACTION COMPLETE")
    print("=" * 70)
    print(f"Successful images : {len(dataframe)}")
    print(f"Failed images     : {len(failed)}")
    print()
    print("Class distribution:")
    print(dataframe["label"].value_counts())
    print()
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
