from pathlib import Path

import torch
import torch.nn as nn
from PIL import Image
from torchvision import models, transforms


ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "document_classifier" / "best_model.pth"

DEVICE = torch.device(
    "mps"
    if torch.backends.mps.is_available()
    else "cuda"
    if torch.cuda.is_available()
    else "cpu"
)


class DocumentClassifier:
    def __init__(self, model_path: Path = MODEL_PATH):
        if not model_path.exists():
            raise FileNotFoundError(
                f"Model not found: {model_path}"
            )

        checkpoint = torch.load(
            model_path,
            map_location=DEVICE,
            weights_only=False,
        )

        self.class_names = checkpoint["class_names"]
        self.image_size = checkpoint["image_size"]

        self.model = models.resnet18(weights=None)

        num_features = self.model.fc.in_features

        self.model.fc = nn.Sequential(
            nn.Dropout(p=0.3),
            nn.Linear(num_features, len(self.class_names)),
        )

        self.model.load_state_dict(
            checkpoint["model_state_dict"]
        )

        self.model = self.model.to(DEVICE)
        self.model.eval()

        self.transform = transforms.Compose([
            transforms.Resize(
                (self.image_size, self.image_size)
            ),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225],
            ),
        ])

    def predict(self, image_path: str):
        image = Image.open(image_path).convert("RGB")
        image_tensor = self.transform(image).unsqueeze(0)
        image_tensor = image_tensor.to(DEVICE)

        with torch.no_grad():
            outputs = self.model(image_tensor)
            probabilities = torch.softmax(outputs, dim=1)

        confidence, predicted_idx = torch.max(
            probabilities, dim=1
        )

        predicted_idx = int(predicted_idx.item())
        confidence = float(confidence.item())

        return {
            "document_type": self.class_names[predicted_idx],
            "confidence": round(confidence, 4),
        }