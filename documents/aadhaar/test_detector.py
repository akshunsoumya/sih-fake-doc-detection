from documents.aadhaar.detector import AadhaarFieldDetector


IMAGE = (
    "datasets/aadhaar_entities/valid/images/"
    "116508899_159713039053118_8698401500526480570_n_"
    "jpg.rf.5163023ced02b8c13d67e816f091cef4.jpg"
)


detector = AadhaarFieldDetector()

detections = detector.detect(IMAGE)

for detection in detections:
    print(detection)