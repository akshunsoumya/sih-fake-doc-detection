from forgery_detection.ela import ELAAnalyzer


IMAGE = (
    "datasets/aadhaar_entities/valid/images/"
    "116508899_159713039053118_8698401500526480570_n_"
    "jpg.rf.5163023ced02b8c13d67e816f091cef4.jpg"
)


def main():
    analyzer = ELAAnalyzer()

    result = analyzer.analyze(IMAGE)

    print("\nELA Result")
    print("----------")

    print(
        f"Max block error: "
        f"{result['max_block_error']}"
    )

    print(
        f"Spike ratio: "
        f"{result['spike_ratio']}"
    )

    print(
        f"Forgery score: "
        f"{result['forgery_score']}"
    )

    print(
        f"Status: "
        f"{result['status']}"
    )


if __name__ == "__main__":
    main()