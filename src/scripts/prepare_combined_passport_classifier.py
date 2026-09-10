"""Build a balanced Indian + Greek passport classifier dataset.

Indian source:
    /tmp/indian_passport_hf

Greek source:
    /Users/sahusoumya/Desktop/M.Tech/SIH/document_types

Final passport dataset:
    train: 210 Indian + 210 Greek
    valid: 45 Indian + 45 Greek
    test: 45 Indian + 45 Greek

Aadhaar data is not modified.
"""

from pathlib import Path
import random
import shutil

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]

# -----------------------------
# SOURCE DATASETS
# -----------------------------

INDIAN_SOURCE = Path("/tmp/indian_passport_hf")

GREEK_SOURCE = Path(
    "/Users/sahusoumya/Desktop/M.Tech/SIH/document_types"
)

# -----------------------------
# PROJECT OUTPUT
# -----------------------------

DATASET_ROOT = ROOT / "datasets" / "document_types"

TRAIN_PASSPORT = DATASET_ROOT / "train" / "passport"
VALID_PASSPORT = DATASET_ROOT / "valid" / "passport"
TEST_PASSPORT = DATASET_ROOT / "test" / "passport"

# -----------------------------
# SETTINGS
# -----------------------------

INDIAN_TOTAL = 300
GREEK_TOTAL = 300

DUPLICATE_THRESHOLD = 0.98

TRAIN_RATIO = 0.70
VALID_RATIO = 0.15
TEST_RATIO = 0.15

SEED = 42


class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, a, b):
        root_a = self.find(a)
        root_b = self.find(b)

        if root_a == root_b:
            return

        if self.rank[root_a] < self.rank[root_b]:
            self.parent[root_a] = root_b

        elif self.rank[root_a] > self.rank[root_b]:
            self.parent[root_b] = root_a

        else:
            self.parent[root_b] = root_a
            self.rank[root_a] += 1


def load_normalized_image(path):
    image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)

    if image is None:
        return None

    image = cv2.resize(image, (256, 256))
    image = image.astype(np.float32)

    mean = image.mean()
    std = image.std()

    return (image - mean) / (std + 1e-6)


def similarity(a, b):
    return float(np.mean(a * b))


def find_indian_groups(files):
    images = []
    valid_files = []

    for path in files:
        image = load_normalized_image(path)

        if image is not None:
            valid_files.append(path)
            images.append(image)

    union_find = UnionFind(len(valid_files))

    pairs = 0

    for i in range(len(valid_files)):
        for j in range(i + 1, len(valid_files)):
            score = similarity(images[i], images[j])

            if score >= DUPLICATE_THRESHOLD:
                union_find.union(i, j)
                pairs += 1

    groups = {}

    for i, path in enumerate(valid_files):
        root = union_find.find(i)
        groups.setdefault(root, []).append(path)

    return list(groups.values()), pairs


def image_area(path):
    image = cv2.imread(str(path))

    if image is None:
        return 0

    height, width = image.shape[:2]

    return width * height


def choose_representative(group):
    return max(group, key=image_area)


def collect_greek_images():
    """Collect Greek passport images from the ORIGINAL dataset only."""

    files = []

    for split in ["train", "valid", "test"]:
        directory = GREEK_SOURCE / split / "passport"

        if not directory.exists():
            raise FileNotFoundError(
                f"Greek passport directory not found:\n{directory}"
            )

        for path in directory.iterdir():
            if (
                path.is_file()
                and path.suffix.lower() in {
                    ".jpg",
                    ".jpeg",
                    ".png",
                }
            ):
                files.append(path)

    return sorted(files)


def clean_output_directories():
    """Clean only the project's passport output directories."""

    for directory in [
        TRAIN_PASSPORT,
        VALID_PASSPORT,
        TEST_PASSPORT,
    ]:
        directory.mkdir(parents=True, exist_ok=True)

        for path in directory.iterdir():
            if path.is_file():
                path.unlink()


def split_files(files):
    random.shuffle(files)

    total = len(files)

    train_count = int(total * TRAIN_RATIO)
    valid_count = int(total * VALID_RATIO)

    train = files[:train_count]

    valid = files[
        train_count:
        train_count + valid_count
    ]

    test = files[
        train_count + valid_count:
    ]

    return train, valid, test


def copy_files(files, output_dir, prefix):
    for index, source in enumerate(files, start=1):
        destination = (
            output_dir
            / f"{prefix}_{index:04d}{source.suffix.lower()}"
        )

        shutil.copy2(source, destination)


def main():
    random.seed(SEED)

    print("=" * 70)
    print("BALANCED INDIAN + GREEK PASSPORT DATASET")
    print("=" * 70)

    # ================================================================
    # INDIAN PASSPORTS
    # ================================================================

    if not INDIAN_SOURCE.exists():
        raise FileNotFoundError(
            f"Indian source not found:\n{INDIAN_SOURCE}"
        )

    indian_files = sorted(
        path
        for path in INDIAN_SOURCE.glob("*.jpg")
        if path.is_file()
    )

    print(f"\nIndian source images: {len(indian_files)}")

    print("\nChecking Indian duplicate groups...")

    indian_groups, pair_count = find_indian_groups(
        indian_files
    )

    print(f"Indian near-duplicate pairs: {pair_count}")
    print(f"Indian unique groups: {len(indian_groups)}")

    if len(indian_groups) < INDIAN_TOTAL:
        raise RuntimeError(
            f"Need {INDIAN_TOTAL} Indian unique groups, "
            f"but found {len(indian_groups)}."
        )

    indian_representatives = [
        choose_representative(group)
        for group in indian_groups
    ]

    random.shuffle(indian_representatives)

    indian_representatives = indian_representatives[
        :INDIAN_TOTAL
    ]

    indian_train, indian_valid, indian_test = split_files(
        indian_representatives
    )

    # ================================================================
    # GREEK PASSPORTS
    # ================================================================

    greek_files = collect_greek_images()

    print(f"\nGreek source images: {len(greek_files)}")

    if len(greek_files) < GREEK_TOTAL:
        raise RuntimeError(
            f"Need {GREEK_TOTAL} Greek images, "
            f"but found {len(greek_files)}."
        )

    random.shuffle(greek_files)

    greek_selected = greek_files[:GREEK_TOTAL]

    greek_train, greek_valid, greek_test = split_files(
        greek_selected
    )

    # ================================================================
    # REBUILD OUTPUT
    # ================================================================

    print("\nRebuilding project passport directories...")

    clean_output_directories()

    copy_files(
        indian_train,
        TRAIN_PASSPORT,
        "indian",
    )

    copy_files(
        greek_train,
        TRAIN_PASSPORT,
        "greek",
    )

    copy_files(
        indian_valid,
        VALID_PASSPORT,
        "indian",
    )

    copy_files(
        greek_valid,
        VALID_PASSPORT,
        "greek",
    )

    copy_files(
        indian_test,
        TEST_PASSPORT,
        "indian",
    )

    copy_files(
        greek_test,
        TEST_PASSPORT,
        "greek",
    )

    # ================================================================
    # FINAL SUMMARY
    # ================================================================

    print("\n" + "=" * 70)
    print("FINAL PASSPORT DATASET")
    print("=" * 70)

    print("\nTRAIN")
    print(f"  Indian: {len(indian_train)}")
    print(f"  Greek : {len(greek_train)}")
    print(f"  Total : {len(indian_train) + len(greek_train)}")

    print("\nVALID")
    print(f"  Indian: {len(indian_valid)}")
    print(f"  Greek : {len(greek_valid)}")
    print(f"  Total : {len(indian_valid) + len(greek_valid)}")

    print("\nTEST")
    print(f"  Indian: {len(indian_test)}")
    print(f"  Greek : {len(greek_test)}")
    print(f"  Total : {len(indian_test) + len(greek_test)}")

    print("\nAadhaar dataset:")
    print("  NOT MODIFIED")

    print("\nOriginal sources:")
    print(f"  Indian: {INDIAN_SOURCE}")
    print(f"  Greek : {GREEK_SOURCE}")

    print("\nProject output:")
    print(f"  {TRAIN_PASSPORT}")
    print(f"  {VALID_PASSPORT}")
    print(f"  {TEST_PASSPORT}")

    print("\n" + "=" * 70)
    print("DONE")
    print("=" * 70)


if __name__ == "__main__":
    main()