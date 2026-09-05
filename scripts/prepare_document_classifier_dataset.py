from pathlib import Path
import random
import shutil


# --------------------------------------------------
# Configuration
# --------------------------------------------------

SOURCE = Path(r"C:\Users\Admin\Desktop\New folder")

OUTPUT = Path(r"C:\Users\Admin\Desktop\document_classifier_dataset")

SEED = 1337

TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15


# --------------------------------------------------
# Helpers
# --------------------------------------------------

def source_id(filename: str) -> str:
    """
    Roboflow filenames look like:

        original_name.rf.random_hash.jpg

    Everything before '.rf.' is treated as the
    original source document.
    """
    return filename.split(".rf.")[0]


def collect_images():
    images = []

    for split in ["train", "valid", "test"]:
        image_dir = SOURCE / split / "images"

        for path in image_dir.iterdir():
            if path.is_file():
                images.append(path)

    return images


def group_by_source(images):
    groups = {}

    for image in images:
        key = source_id(image.name)
        groups.setdefault(key, []).append(image)

    return groups


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    if not SOURCE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {SOURCE}"
        )

    images = collect_images()

    print(f"Total images: {len(images)}")

    groups = group_by_source(images)

    print(f"Unique source documents: {len(groups)}")

    # Deterministic shuffle
    source_ids = list(groups.keys())

    random.seed(SEED)
    random.shuffle(source_ids)

    n = len(source_ids)

    train_end = int(n * TRAIN_RATIO)
    val_end = train_end + int(n * VAL_RATIO)

    train_ids = source_ids[:train_end]
    val_ids = source_ids[train_end:val_end]
    test_ids = source_ids[val_end:]

    splits = {
        "train": train_ids,
        "val": val_ids,
        "test": test_ids,
    }

    # Create directories
    for split in splits:
        (OUTPUT / split / "aadhaar").mkdir(
            parents=True,
            exist_ok=True
        )

    # Copy images
    for split, ids in splits.items():

        count = 0

        for sid in ids:

            for image in groups[sid]:

                destination = (
                    OUTPUT
                    / split
                    / "aadhaar"
                    / image.name
                )

                shutil.copy2(image, destination)

                count += 1

        print(
            f"{split}: "
            f"{len(ids)} source documents, "
            f"{count} images"
        )

    print()
    print(f"Dataset created at: {OUTPUT}")


if __name__ == "__main__":
    main()