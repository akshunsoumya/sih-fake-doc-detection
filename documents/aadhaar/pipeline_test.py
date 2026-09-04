from documents.aadhaar.pipeline import AadhaarPipeline


IMAGE = (
    "datasets/aadhaar_entities/valid/images/"
    "116508899_159713039053118_8698401500526480570_n_"
    "jpg.rf.5163023ced02b8c13d67e816f091cef4.jpg"
)


def main():
    pipeline = AadhaarPipeline()

    result = pipeline.process(IMAGE)

    print("\nDocument type:")
    print(result["document_type"])

    print("\nFields:")

    for field, data in result["fields"].items():
        print(f"\n{field}")
        print(f"  OCR: {data['text']}")
        print(f"  Confidence: {data['confidence']}")
        print(f"  Bounding box: {data['bbox']}")

        validation = data.get("validation")

        if validation:
            print(f"  Valid: {validation['valid']}")


if __name__ == "__main__":
    main()