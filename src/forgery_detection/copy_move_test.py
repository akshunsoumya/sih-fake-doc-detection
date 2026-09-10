import cv2

from forgery_detection.copy_move import CopyMoveDetector


GENUINE_IMAGE = (
    "datasets/aadhaar_entities/valid/images/"
    "116508899_159713039053118_8698401500526480570_n_"
    "jpg.rf.5163023ced02b8c13d67e816f091cef4.jpg"
)

COPY_MOVE_IMAGE = (
    "/Users/sahusoumya/Desktop/M.Tech/"
    "doc-forgery-detector/dataset/forged/"
    "aadhaar_0005_copy_move.jpg"
)


def print_result(label, result):
    print(f"\n{label}")
    print("-" * len(label))

    for key, value in result.items():
        print(f"{key}: {value}")


def main():
    detector = CopyMoveDetector()

    # ---------------------------------------------------------
    # TEST 1: Genuine image
    # ---------------------------------------------------------

    genuine_result = detector.detect(GENUINE_IMAGE)

    print_result(
        "Genuine Image",
        genuine_result,
    )

    # ---------------------------------------------------------
    # TEST 2: Synthetic copy-move image
    # ---------------------------------------------------------

    copy_move_result = detector.detect(COPY_MOVE_IMAGE)

    print_result(
        "Copy-Move Forged Image",
        copy_move_result,
    )

    # ---------------------------------------------------------
    # TEST 3: OpenCV image input
    # ---------------------------------------------------------

    image = cv2.imread(COPY_MOVE_IMAGE)

    if image is None:
        raise ValueError(
            f"Could not read image: {COPY_MOVE_IMAGE}"
        )

    opencv_result = detector.detect(image)

    print_result(
        "Copy-Move Image - OpenCV Input",
        opencv_result,
    )


if __name__ == "__main__":
    main()