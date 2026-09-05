import os
import random
import subprocess
from pathlib import Path

ZIP_PATH = Path(r"C:\Users\Admin\Desktop\idnet_temp\GRC.zip")

OUTPUT_ROOT = Path("datasets/document_types")

TRAIN_COUNT = 1700
VALID_COUNT = 400
TEST_COUNT = 400

SEED = 42

random.seed(SEED)


def get_positive_images():
    """Get all image paths inside GRC/positive from the ZIP."""
    command = [
        r"C:\Program Files\7-Zip\7z.exe",
        "l",
        "-slt",
        str(ZIP_PATH),
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )

    images = []

    for line in result.stdout.splitlines():
        if not line.startswith("Path = GRC\\positive\\"):
            continue

        path = line[len("Path = "):]

        ext = Path(path).suffix.lower()

        if ext in {".jpg", ".jpeg", ".png", ".webp"}:
            images.append(path)

    return images


def extract_files(files, output_dir):
    """Extract selected files from the ZIP."""
    output_dir.mkdir(parents=True, exist_ok=True)

    file_list = output_dir / "extract_list.txt"

    with open(file_list, "w", encoding="utf-8") as f:
        for file in files:
            f.write(file + "\n")

    command = [
        r"C:\Program Files\7-Zip\7z.exe",
        "e",
        str(ZIP_PATH),
        f"@{file_list}",
        f"-o{output_dir}",
        "-y",
    ]

    subprocess.run(command, check=True)

    file_list.unlink()


def main():
    print("Reading GRC.zip...")
    images = get_positive_images()

    print(f"Positive images found: {len(images)}")

    required = TRAIN_COUNT + VALID_COUNT + TEST_COUNT

    if len(images) < required:
        raise RuntimeError(
            f"Not enough images. Required {required}, found {len(images)}."
        )

    random.shuffle(images)

    train = images[:TRAIN_COUNT]
    valid = images[TRAIN_COUNT:TRAIN_COUNT + VALID_COUNT]
    test = images[TRAIN_COUNT + VALID_COUNT:required]

    print("\nSelected:")
    print(f"Train: {len(train)}")
    print(f"Valid: {len(valid)}")
    print(f"Test : {len(test)}")

    print("\nExtracting train...")
    extract_files(
        train,
        OUTPUT_ROOT / "train" / "passport"
    )

    print("Extracting valid...")
    extract_files(
        valid,
        OUTPUT_ROOT / "valid" / "passport"
    )

    print("Extracting test...")
    extract_files(
        test,
        OUTPUT_ROOT / "test" / "passport"
    )

    print("\nPassport dataset preparation complete.")


if __name__ == "__main__":
    main()