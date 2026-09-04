from documents.aadhaar.detector import AadhaarFieldDetector
from documents.aadhaar.ocr import AadhaarOCR


IMAGE = (
    "datasets/aadhaar_entities/valid/images/"
    "116508899_159713039053118_8698401500526480570_n_"
    "jpg.rf.5163023ced02b8c13d67e816f091cef4.jpg"
)


def main():
    detector = AadhaarFieldDetector()
    ocr = AadhaarOCR()

    detections = detector.detect(IMAGE)

    for detection in detections:
        text = ocr.extract_text(
            IMAGE,
            detection["bbox"],
            detection["field"],
        )

        print(
            f"{detection['field']:20s} "
            f"{detection['confidence']:.2f} "
            f"→ {text}"
        )


if __name__ == "__main__":
    main()