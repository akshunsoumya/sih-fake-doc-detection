import copy
import random
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
)
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms
from tqdm import tqdm


# ============================================================
# Configuration
# ============================================================

DATASET_ROOT = Path("datasets/document_types")
MODEL_DIR = Path("models/document_classifier")

MODEL_DIR.mkdir(parents=True, exist_ok=True)

BATCH_SIZE = 16
NUM_EPOCHS = 15
LEARNING_RATE = 1e-4
NUM_WORKERS = 0
IMAGE_SIZE = 224

SEED = 42

CLASS_NAMES = ["aadhaar", "passport"]


# ============================================================
# Reproducibility
# ============================================================

random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)


# ============================================================
# Device
# ============================================================

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print("=" * 60)
print("Document Type Classifier")
print("=" * 60)
print(f"Device: {DEVICE}")
print(f"Dataset: {DATASET_ROOT.resolve()}")
print()


# ============================================================
# Data transforms
# ============================================================

train_transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.RandomHorizontalFlip(p=0.3),
    transforms.RandomRotation(5),
    transforms.ColorJitter(
        brightness=0.15,
        contrast=0.15,
        saturation=0.05,
    ),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
    ),
])


eval_transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
    ),
])


# ============================================================
# Load datasets
# ============================================================

train_dir = DATASET_ROOT / "train"
valid_dir = DATASET_ROOT / "valid"
test_dir = DATASET_ROOT / "test"

train_dataset = datasets.ImageFolder(
    train_dir,
    transform=train_transform,
)

valid_dataset = datasets.ImageFolder(
    valid_dir,
    transform=eval_transform,
)

test_dataset = datasets.ImageFolder(
    test_dir,
    transform=eval_transform,
)


print("Dataset sizes:")
print(f"Train: {len(train_dataset)}")
print(f"Valid: {len(valid_dataset)}")
print(f"Test : {len(test_dataset)}")
print()

print("Class mapping:")
print(train_dataset.class_to_idx)
print()

# Safety check
if train_dataset.class_to_idx != valid_dataset.class_to_idx:
    raise RuntimeError("Train/valid class mappings do not match.")

if train_dataset.class_to_idx != test_dataset.class_to_idx:
    raise RuntimeError("Train/test class mappings do not match.")


# ============================================================
# Data loaders
# ============================================================

train_loader = DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True,
    num_workers=NUM_WORKERS,
)

valid_loader = DataLoader(
    valid_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=NUM_WORKERS,
)

test_loader = DataLoader(
    test_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=NUM_WORKERS,
)


# ============================================================
# Model
# ============================================================

print("Loading pretrained ResNet18...")

weights = models.ResNet18_Weights.DEFAULT

model = models.resnet18(weights=weights)

# Freeze the pretrained backbone initially
for parameter in model.parameters():
    parameter.requires_grad = False

# Replace final classifier
num_features = model.fc.in_features

model.fc = nn.Sequential(
    nn.Dropout(p=0.3),
    nn.Linear(num_features, 2),
)

model = model.to(DEVICE)


# ============================================================
# Loss and optimizer
# ============================================================

criterion = nn.CrossEntropyLoss()

optimizer = torch.optim.Adam(
    model.fc.parameters(),
    lr=LEARNING_RATE,
)


# ============================================================
# Training functions
# ============================================================

def train_one_epoch(model, loader, criterion, optimizer):
    model.train()

    running_loss = 0.0
    correct = 0
    total = 0

    progress = tqdm(loader, desc="Training", leave=False)

    for images, labels in progress:
        images = images.to(DEVICE)
        labels = labels.to(DEVICE)

        optimizer.zero_grad()

        outputs = model(images)
        loss = criterion(outputs, labels)

        loss.backward()
        optimizer.step()

        running_loss += loss.item() * images.size(0)

        predictions = outputs.argmax(dim=1)

        correct += (predictions == labels).sum().item()
        total += labels.size(0)

        progress.set_postfix(
            loss=f"{loss.item():.4f}",
            acc=f"{correct / total:.4f}",
        )

    epoch_loss = running_loss / total
    epoch_accuracy = correct / total

    return epoch_loss, epoch_accuracy


def evaluate(model, loader, criterion):
    model.eval()

    running_loss = 0.0
    correct = 0
    total = 0

    all_labels = []
    all_predictions = []

    with torch.no_grad():

        progress = tqdm(loader, desc="Validation", leave=False)

        for images, labels in progress:
            images = images.to(DEVICE)
            labels = labels.to(DEVICE)

            outputs = model(images)

            loss = criterion(outputs, labels)

            running_loss += loss.item() * images.size(0)

            predictions = outputs.argmax(dim=1)

            correct += (predictions == labels).sum().item()
            total += labels.size(0)

            all_labels.extend(labels.cpu().numpy())
            all_predictions.extend(predictions.cpu().numpy())

    epoch_loss = running_loss / total
    epoch_accuracy = correct / total

    return (
        epoch_loss,
        epoch_accuracy,
        np.array(all_labels),
        np.array(all_predictions),
    )


# ============================================================
# Training loop
# ============================================================

best_accuracy = 0.0
best_model_state = None

train_losses = []
valid_losses = []

train_accuracies = []
valid_accuracies = []

print()
print("=" * 60)
print("Starting training")
print("=" * 60)

for epoch in range(NUM_EPOCHS):

    print()
    print(f"Epoch {epoch + 1}/{NUM_EPOCHS}")

    train_loss, train_accuracy = train_one_epoch(
        model,
        train_loader,
        criterion,
        optimizer,
    )

    valid_loss, valid_accuracy, _, _ = evaluate(
        model,
        valid_loader,
        criterion,
    )

    train_losses.append(train_loss)
    valid_losses.append(valid_loss)

    train_accuracies.append(train_accuracy)
    valid_accuracies.append(valid_accuracy)

    print(
        f"Train Loss: {train_loss:.4f} | "
        f"Train Acc: {train_accuracy:.4f}"
    )

    print(
        f"Valid Loss: {valid_loss:.4f} | "
        f"Valid Acc: {valid_accuracy:.4f}"
    )

    # Save best model
    if valid_accuracy > best_accuracy:

        best_accuracy = valid_accuracy
        best_model_state = copy.deepcopy(model.state_dict())

        checkpoint_path = MODEL_DIR / "best_model.pth"

        torch.save(
            {
                "model_state_dict": best_model_state,
                "class_names": CLASS_NAMES,
                "class_to_idx": train_dataset.class_to_idx,
                "image_size": IMAGE_SIZE,
            },
            checkpoint_path,
        )

        print(f"✓ Best model saved: {checkpoint_path}")


# ============================================================
# Load best model
# ============================================================

print()
print("=" * 60)
print("Loading best model")
print("=" * 60)

checkpoint_path = MODEL_DIR / "best_model.pth"

checkpoint = torch.load(
    checkpoint_path,
    map_location=DEVICE,
)

model.load_state_dict(checkpoint["model_state_dict"])


# ============================================================
# Test evaluation
# ============================================================

print()
print("=" * 60)
print("Final Test Evaluation")
print("=" * 60)

test_loss, test_accuracy, test_labels, test_predictions = evaluate(
    model,
    test_loader,
    criterion,
)

print(f"Test Loss: {test_loss:.4f}")
print(f"Test Accuracy: {test_accuracy:.4f}")
print()

print("Classification Report:")
print(
    classification_report(
        test_labels,
        test_predictions,
        target_names=CLASS_NAMES,
        digits=4,
    )
)


# ============================================================
# Confusion matrix
# ============================================================

cm = confusion_matrix(
    test_labels,
    test_predictions,
)

print("Confusion Matrix:")
print(cm)

disp = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=CLASS_NAMES,
)

disp.plot()

plt.title("Aadhaar vs Passport - Document Classifier")

confusion_path = MODEL_DIR / "confusion_matrix.png"

plt.savefig(
    confusion_path,
    dpi=200,
    bbox_inches="tight",
)

plt.close()

print(f"Confusion matrix saved: {confusion_path}")


# ============================================================
# Training curves
# ============================================================

epochs = range(1, NUM_EPOCHS + 1)

plt.figure()

plt.plot(
    epochs,
    train_accuracies,
    label="Train Accuracy",
)

plt.plot(
    epochs,
    valid_accuracies,
    label="Validation Accuracy",
)

plt.xlabel("Epoch")
plt.ylabel("Accuracy")
plt.title("Training vs Validation Accuracy")
plt.legend()

accuracy_path = MODEL_DIR / "accuracy_curve.png"

plt.savefig(
    accuracy_path,
    dpi=200,
    bbox_inches="tight",
)

plt.close()


plt.figure()

plt.plot(
    epochs,
    train_losses,
    label="Train Loss",
)

plt.plot(
    epochs,
    valid_losses,
    label="Validation Loss",
)

plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.title("Training vs Validation Loss")
plt.legend()

loss_path = MODEL_DIR / "loss_curve.png"

plt.savefig(
    loss_path,
    dpi=200,
    bbox_inches="tight",
)

plt.close()


print(f"Accuracy curve saved: {accuracy_path}")
print(f"Loss curve saved: {loss_path}")

print()
print("=" * 60)
print("Training complete")
print("=" * 60)
print(f"Best validation accuracy: {best_accuracy:.4f}")
print(f"Final test accuracy:      {test_accuracy:.4f}")
print(f"Model: {checkpoint_path}")