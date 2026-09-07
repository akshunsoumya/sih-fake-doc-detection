"""Prepare a leakage-safe Indian passport dataset for document classification.

Source:
    /tmp/indian_passport_hf

The source contains 600 images with strong perceptual duplicate pairs.
This script:
1. Finds near-duplicate groups using perceptual similarity.
2. Keeps each duplicate group entirely inside one split.
3. Selects one representative image per group.
4. Creates:
       datasets/document_types/
           train/passport/
           valid/passport/
           test/passport/
5. Leaves the Aadhaar dataset untouched.

This prevents the same passport/document from appearing in multiple splits.
"""

from pathlib import Path
import random
import shutil

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]

SOURCE_DIR = Path("/tmp/indian_passport_hf")
OUTPUT_ROOT = ROOT / "datasets" / "document_types"

TRAIN_DIR = OUTPUT_ROOT / "train" / "passport"
VALID_DIR = OUTPUT_ROOT / "valid" / "passport"
TEST_DIR = OUTPUT_ROOT / "test" / "passport"

SIMILARITY_THRESHOLD = 0.98
SEED = 42

TRAIN_RATIO = 0.70
VALID_RATIO = 0.15
TEST_RATIO = 0.15


class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, a, b):
        ra = self.find(a)
        rb = self.find(b)

        if ra == rb:
            return

        if self.rank[ra] < self.rank[rb]:
            self.parent[ra] = rb
        elif self.rank[ra] > self.rank[rb]:
            self.parent[rb] = ra
        else:
            self.parent[rb] = ra
            self.rank[ra] += 1


def load_image(path):
    image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)

    if image is None:
        return None

    image = cv2.resize(image, (256, 256))

    image = image.astype(np.float32)

    mean = image.mean()
    std = image.std()

    image = (image - mean) / (std + 1e-6)

    return image


def similarity(a, b):
    return float(np.mean(a * b))


def find_duplicate_groups(files, images):
    union_find = UnionFind(len(files))

    pairs = 0

    for i in range(len(files)):
        for j in range(i + 1, len(files)):
            score = similarity(images[i], images[j])

            if score >= SIMILARITY_THRESHOLD:
                union_find.union(i, j)
                pairs += 1

    groups = {}

    for i in range(len(files)):
        root = union_find.find(i)
        groups.setdefault(root, []).append(files[i])

    return list(groups.values()), pairs


def choose_representative(group):
    """Choose the largest image in the group as representative."""

    def image_area(path):
        image = cv2.imread(str(path))

        if image is None:
            return 0

        height, width = image.shape[:2]

        return width * height

    return max(group, key=image_area)


def prepare_output_dirs():
    for directory in [TRAIN_DIR, VALID_DIR, TEST_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

        for old_file in directory.iterdir():
            if old_file.is_file():
                old_file.unlink()


def copy_group_representatives(groups):
    random.seed(SEED)

    representatives = [
        choose_representative(group)
        for group in groups
    ]

    random.shuffle(representatives)

    total = len(representatives)

    train_count = int(total * TRAIN_RATIO)
    valid_count = int(total * VALID_RATIO)

    train_files = representatives[:train_count]

    valid_files = representatives[
        train_count:train_count + valid_count
    ]

    test_files = representatives[
        train_count + valid_count:
    ]

    splits = {
        "train": (train_files, TRAIN_DIR),
        "valid": (valid_files, VALID_DIR),
        "test": (test_files, TEST_DIR),
    }

    for split_name, (files, output_dir) in splits.items():
        for index, source in enumerate(files, start=1):
            destination = output_dir / f"indian_passport_{index:04d}.jpg"
            shutil.copy2(source, destination)

    return train_files, valid_files, test_files


def main():
    print("=" * 70)
    print("INDIAN PASSPORT CLASSIFIER DATASET PREPARATION")
    print("=" * 70)

    if not SOURCE_DIR.exists():
        raise FileNotFoundError(
            f"Source dataset not found:\n{SOURCE_DIR}"
        )

    files = sorted(
        path
        for path in SOURCE_DIR.glob("*.jpg")
        if path.is_file()
    )

    print(f"\nSource images: {len(files)}")

    if len(files) == 0:
        raise RuntimeError("No JPG images found in source dataset.")

    print("\nLoading images...")

    images = []
    valid_files = []

    for path in files:
        image = load_image(path)

        if image is not None:
            valid_files.append(path)
            images.append(image)

    print(f"Loaded images: {len(images)}")

    print(
        f"\nFinding duplicate groups "
        f"(threshold >= {SIMILARITY_THRESHOLD})..."
    )

    groups, pair_count = find_duplicate_groups(
        valid_files,
        images,
    )

    print(f"Near-duplicate pairs: {pair_count}")
    print(f"Underlying image groups: {len(groups)}")

    group_sizes = [len(group) for group in groups]

    print(
        "Group sizes:",
        {
            size: group_sizes.count(size)
            for size in sorted(set(group_sizes))
        },
    )

    print("\nPreparing classifier directories...")

    prepare_output_dirs()

    train_files, valid_files, test_files = copy_group_representatives(
        groups
    )

    print("\n" + "=" * 70)
    print("FINAL SPLIT")
    print("=" * 70)

    print(f"Train passport images: {len(train_files)}")
    print(f"Valid passport images: {len(valid_files)}")
    print(f"Test passport images : {len(test_files)}")

    print("\nOutput:")

    print(f"  {TRAIN_DIR}")
    print(f"  {VALID_DIR}")
    print(f"  {TEST_DIR}")

    print("\nAadhaar directories were NOT modified.")

    print("\n" + "=" * 70)
    print("DONE")
    print("=" * 70)

    print(
        """
Important:
- Only one representative is selected from each duplicate group.
- A duplicate group cannot cross train/valid/test.
- Existing Greek passport images in the classifier dataset are removed.
- The source dataset in /tmp is not modified.
"""
    )


if __name__ == "__main__":
    main()