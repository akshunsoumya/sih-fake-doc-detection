from documents.aadhaar.validator import AadhaarValidator


def main():
    validator = AadhaarValidator()

    fields = {
        "aadhaar_number": "881696785169",
        "dob": "1102/1909",
        "name": "Bhartiy San",
        "gender": "FEMALE",
    }

    results = validator.validate_fields(fields)

    for field, result in results.items():
        print(f"\n{field}")
        print(f"  value: {result['value']}")
        print(f"  valid: {result['valid']}")

        for key, value in result.items():
            if key != "value" and key != "valid":
                print(f"  {key}: {value}")


if __name__ == "__main__":
    main()