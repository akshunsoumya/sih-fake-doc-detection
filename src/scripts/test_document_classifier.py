from pathlib import Path
import sys

from document_detection.classifier import DocumentClassifier


def main():
    if len(sys.argv) != 2:
        print(
            "Usage:\n"
            "python scripts/test_document_classifier.py "
            "/path/to/image.jpg"
        )
        sys.exit(1)

    image_path = Path(sys.argv[1]).expanduser().resolve()

    if not image_path.exists():
        print(f"ERROR: Image not found: {image_path}")
        sys.exit(1)

    print("=" * 60)
    print("DOCUMENT CLASSIFIER TEST")
    print("=" * 60)
    print(f"Input: {image_path}")
    print()

    classifier = DocumentClassifier()

    result = classifier.predict(str(image_path))

    print("Prediction:")
    print(f"  Document type: {result['document_type']}")
    print(f"  Confidence:    {result['confidence']:.4f}")

    print()
    print("=" * 60)
    print("DONE")
    print("=" * 60)


if __name__ == "__main__":
    main()