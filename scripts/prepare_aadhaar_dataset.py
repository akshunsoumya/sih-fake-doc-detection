"""Prepare the archived Aadhaar entity-detection dataset for Ultralytics YOLO.

Usage:
    python prepare_archived_dataset.py archive.zip

Creates:
    datasets/aadhaar_entities/{train,valid,test}/{images,labels}
    datasets/aadhaar_entities/data.yaml

The archived labels are YOLO format. The five observed classes are mapped to:
0=aadhaar_number, 1=dob, 2=gender, 3=name, 4=address.
"""
from pathlib import Path
import shutil
import sys
import zipfile

CLASS_NAMES = ["aadhaar_number", "dob", "gender", "name", "address"]


def main(zip_path: str):
    zip_path = Path(zip_path).resolve()
    root = Path(__file__).resolve().parent
    out = root / "datasets" / "aadhaar_entities"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    with zipfile.ZipFile(zip_path) as z:
        for split in ("train", "valid", "test"):
            for kind in ("images", "labels"):
                target = out / split / kind
                target.mkdir(parents=True, exist_ok=True)
                prefix = f"{split}/{kind}/"
                for name in z.namelist():
                    if name.startswith(prefix) and not name.endswith("/"):
                        # Keep only basename; the archive has no duplicate basenames
                        # within a split in normal Roboflow exports.
                        (target / Path(name).name).write_bytes(z.read(name))

    yaml = out / "data.yaml"
    yaml.write_text(
        "path: " + out.as_posix() + "\n"
        "train: train/images\n"
        "val: valid/images\n"
        "test: test/images\n"
        f"nc: {len(CLASS_NAMES)}\n"
        "names:\n" + "".join(f"  {i}: {name}\n" for i, name in enumerate(CLASS_NAMES)),
        encoding="utf-8",
    )
    print(f"Prepared dataset: {out}")
    print(yaml.read_text())


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python prepare_archived_dataset.py path/to/archive.zip")
        raise SystemExit(1)
    main(sys.argv[1])
