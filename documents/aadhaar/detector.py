from pathlib import Path

from ultralytics import YOLO


ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = ROOT / "runs" / "aadhaar_fields" / "weights" / "best.pt"

CLASS_NAMES = {
    0: "aadhaar_number",
    1: "dob",
    2: "gender",
    3: "name",
    4: "address",
}


class AadhaarFieldDetector:
    def __init__(self, model_path: Path = MODEL_PATH):
        if not model_path.exists():
            raise FileNotFoundError(
                f"Aadhaar detector weights not found: {model_path}"
            )

        self.model = YOLO(str(model_path))

    def detect(self, image_path: str, confidence: float = 0.25):
        results = self.model.predict(
            source=image_path,
            imgsz=640,
            conf=confidence,
            verbose=False,
        )

        result = results[0]

        detections = []

        if result.boxes is None:
            return detections

        boxes = result.boxes.xyxy.cpu().numpy()
        classes = result.boxes.cls.cpu().numpy().astype(int)
        confidences = result.boxes.conf.cpu().numpy()

        for box, class_id, score in zip(
            boxes, classes, confidences
        ):
            detections.append(
                {
                    "field": CLASS_NAMES.get(
                        int(class_id),
                        f"class_{class_id}",
                    ),
                    "confidence": round(float(score), 4),
                    "bbox": [round(float(x), 2) for x in box],
                }
            )

        return detections