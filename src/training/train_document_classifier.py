import copy
import random
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import (
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

ROOT = Path(__file__).resolve().parents[1]

DATASET_ROOT = ROOT / "datasets" / "document_types"
MODEL_DIR = ROOT / "models" / "document_classifier"

MODEL_DIR.mkdir(parents=True, exist_ok=True)

BATCH_SIZE = 16

# Stage 1: train classifier head
HEAD_EPOCHS = 5

# Stage 2: fine-tune last ResNet block + classifier
FINETUNE_EPOCHS = 10

LEARNING_RATE_HEAD = 1e-4
LEARNING_RATE_FINETUNE = 1e-5

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

if torch.backends.mps.is_available():
    DEVICE = torch.device("mps")
elif torch.cuda.is_available():
    DEVICE = torch.device("cuda")
else:
    DEVICE = torch.device("cpu")


print("=" * 60)
print("Document Type Classifier")
print("=" * 60)
print(f"Device: {DEVICE}")
print(f"Dataset: {DATASET_ROOT}")
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
# Dataset loading
# ============================================================

train_dir = DATASET_ROOT / "train"
valid_dir = DATASET_ROOT / "valid"
test_dir = DATASET_ROOT / "test"


if not train_dir.exists():
    raise FileNotFoundError(f"Training directory not found: {train_dir}")

if not valid_dir.exists():
    raise FileNotFoundError(f"Validation directory not found: {valid_dir}")

if not test_dir.exists():
    raise FileNotFoundError(f"Test directory not found: {test_dir}")


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


# ============================================================
# Safety checks
# ============================================================

expected_classes = {
    "aadhaar",
    "passport",
}

if set(train_dataset.classes) != expected_classes:
    raise RuntimeError(
        f"Unexpected classes: {train_dataset.classes}. "
        f"Expected: {sorted(expected_classes)}"
    )

if train_dataset.class_to_idx != valid_dataset.class_to_idx:
    raise RuntimeError(
        "Train/valid class mappings do not match."
    )

if train_dataset.class_to_idx != test_dataset.class_to_idx:
    raise RuntimeError(
        "Train/test class mappings do not match."
    )


# ============================================================
# Print class distribution
# ============================================================

def print_class_distribution(dataset, name):
    counts = np.bincount(
        dataset.targets,
        minlength=len(dataset.classes),
    )

    print(f"{name} class distribution:")

    for index, class_name in enumerate(dataset.classes):
        print(
            f"  {class_name}: {int(counts[index])}"
        )

    print()


print_class_distribution(
    train_dataset,
    "Train",
)

print_class_distribution(
    valid_dataset,
    "Valid",
)

print_class_distribution(
    test_dataset,
    "Test",
)


# ============================================================
# Class weights
# ============================================================

train_targets = np.array(train_dataset.targets)

class_counts = np.bincount(
    train_targets,
    minlength=len(CLASS_NAMES),
)

total_samples = class_counts.sum()

class_weights = total_samples / (
    len(CLASS_NAMES) * class_counts
)

class_weights = torch.tensor(
    class_weights,
    dtype=torch.float32,
    device=DEVICE,
)

print("Class weights:")

for index, class_name in enumerate(train_dataset.classes):
    print(
        f"  {class_name}: "
        f"{class_weights[index].item():.4f}"
    )

print()


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

num_features = model.fc.in_features

model.fc = nn.Sequential(
    nn.Dropout(p=0.3),
    nn.Linear(num_features, len(CLASS_NAMES)),
)

model = model.to(DEVICE)


# ============================================================
# Training / evaluation functions
# ============================================================

def train_one_epoch(
    model,
    loader,
    criterion,
    optimizer,
):
    model.train()

    running_loss = 0.0
    correct = 0
    total = 0

    progress = tqdm(
        loader,
        desc="Training",
        leave=False,
    )

    for images, labels in progress:

        images = images.to(DEVICE)
        labels = labels.to(DEVICE)

        optimizer.zero_grad()

        outputs = model(images)

        loss = criterion(
            outputs,
            labels,
        )

        loss.backward()

        optimizer.step()

        running_loss += (
            loss.item() * images.size(0)
        )

        predictions = outputs.argmax(
            dim=1
        )

        correct += (
            predictions == labels
        ).sum().item()

        total += labels.size(0)

        progress.set_postfix(
            loss=f"{loss.item():.4f}",
            acc=f"{correct / total:.4f}",
        )

    epoch_loss = running_loss / total
    epoch_accuracy = correct / total

    return epoch_loss, epoch_accuracy


def evaluate(
    model,
    loader,
    criterion,
):
    model.eval()

    running_loss = 0.0
    correct = 0
    total = 0

    all_labels = []
    all_predictions = []

    with torch.no_grad():

        progress = tqdm(
            loader,
            desc="Validation",
            leave=False,
        )

        for images, labels in progress:

            images = images.to(DEVICE)
            labels = labels.to(DEVICE)

            outputs = model(images)

            loss = criterion(
                outputs,
                labels,
            )

            running_loss += (
                loss.item() * images.size(0)
            )

            predictions = outputs.argmax(
                dim=1
            )

            correct += (
                predictions == labels
            ).sum().item()

            total += labels.size(0)

            all_labels.extend(
                labels.cpu().numpy()
            )

            all_predictions.extend(
                predictions.cpu().numpy()
            )

    epoch_loss = running_loss / total
    epoch_accuracy = correct / total

    return (
        epoch_loss,
        epoch_accuracy,
        np.array(all_labels),
        np.array(all_predictions),
    )


# ============================================================
# Loss function
# ============================================================

criterion = nn.CrossEntropyLoss(
    weight=class_weights
)


# ============================================================
# Training history
# ============================================================

train_losses = []
valid_losses = []

train_accuracies = []
valid_accuracies = []

best_accuracy = 0.0
best_model_state = None


# ============================================================
# Stage 1
# ============================================================

print()
print("=" * 60)
print("STAGE 1: Training classifier head")
print("=" * 60)


for parameter in model.parameters():
    parameter.requires_grad = False


for parameter in model.fc.parameters():
    parameter.requires_grad = True


optimizer = torch.optim.Adam(
    model.fc.parameters(),
    lr=LEARNING_RATE_HEAD,
)


for epoch in range(HEAD_EPOCHS):

    print()
    print(
        f"Head Epoch "
        f"{epoch + 1}/{HEAD_EPOCHS}"
    )

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

    if valid_accuracy > best_accuracy:

        best_accuracy = valid_accuracy

        best_model_state = copy.deepcopy(
            model.state_dict()
        )

        checkpoint_path = (
            MODEL_DIR / "best_model.pth"
        )

        torch.save(
            {
                "model_state_dict": best_model_state,
                "class_names": CLASS_NAMES,
                "class_to_idx": train_dataset.class_to_idx,
                "image_size": IMAGE_SIZE,
            },
            checkpoint_path,
        )

        print(
            f"✓ Best model saved: "
            f"{checkpoint_path}"
        )


# ============================================================
# Stage 2: Fine-tune last ResNet block + classifier
# ============================================================

print()
print("=" * 60)
print("STAGE 2: Fine-tuning last ResNet block")
print("=" * 60)


for parameter in model.parameters():
    parameter.requires_grad = False


for parameter in model.layer4.parameters():
    parameter.requires_grad = True


for parameter in model.fc.parameters():
    parameter.requires_grad = True


optimizer = torch.optim.Adam(
    [
        {
            "params": model.layer4.parameters(),
            "lr": LEARNING_RATE_FINETUNE,
        },
        {
            "params": model.fc.parameters(),
            "lr": LEARNING_RATE_FINETUNE,
        },
    ]
)


for epoch in range(FINETUNE_EPOCHS):

    print()
    print(
        f"Fine-tune Epoch "
        f"{epoch + 1}/{FINETUNE_EPOCHS}"
    )

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

    if valid_accuracy > best_accuracy:

        best_accuracy = valid_accuracy

        best_model_state = copy.deepcopy(
            model.state_dict()
        )

        checkpoint_path = (
            MODEL_DIR / "best_model.pth"
        )

        torch.save(
            {
                "model_state_dict": best_model_state,
                "class_names": CLASS_NAMES,
                "class_to_idx": train_dataset.class_to_idx,
                "image_size": IMAGE_SIZE,
            },
            checkpoint_path,
        )

        print(
            f"✓ Best model saved: "
            f"{checkpoint_path}"
        )


# ============================================================
# Load best model
# ============================================================

print()
print("=" * 60)
print("Loading best model")
print("=" * 60)


checkpoint_path = (
    MODEL_DIR / "best_model.pth"
)


checkpoint = torch.load(
    checkpoint_path,
    map_location=DEVICE,
    weights_only=False,
)

model.load_state_dict(
    checkpoint["model_state_dict"]
)


# ============================================================
# Final test evaluation
# ============================================================

print()
print("=" * 60)
print("FINAL TEST EVALUATION")
print("=" * 60)


test_loss, test_accuracy, test_labels, test_predictions = evaluate(
    model,
    test_loader,
    criterion,
)


print(
    f"Test Loss: {test_loss:.4f}"
)

print(
    f"Test Accuracy: {test_accuracy:.4f}"
)

print()


# ============================================================
# Classification report
# ============================================================

print("Classification Report:")

print(
    classification_report(
        test_labels,
        test_predictions,
        target_names=CLASS_NAMES,
        digits=4,
        zero_division=0,
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

plt.title(
    "Aadhaar vs Passport - Document Classifier"
)

confusion_path = (
    MODEL_DIR / "confusion_matrix.png"
)

plt.savefig(
    confusion_path,
    dpi=200,
    bbox_inches="tight",
)

plt.close()

print(
    f"Confusion matrix saved: "
    f"{confusion_path}"
)


# ============================================================
# Training curves
# ============================================================

epochs = range(
    1,
    len(train_losses) + 1,
)


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

plt.title(
    "Training vs Validation Accuracy"
)

plt.legend()

accuracy_path = (
    MODEL_DIR / "accuracy_curve.png"
)

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

plt.title(
    "Training vs Validation Loss"
)

plt.legend()

loss_path = (
    MODEL_DIR / "loss_curve.png"
)

plt.savefig(
    loss_path,
    dpi=200,
    bbox_inches="tight",
)

plt.close()


# ============================================================
# Final summary
# ============================================================

print(
    f"Accuracy curve saved: "
    f"{accuracy_path}"
)

print(
    f"Loss curve saved: "
    f"{loss_path}"
)

print()
print("=" * 60)
print("TRAINING COMPLETE")
print("=" * 60)

print(
    f"Best validation accuracy: "
    f"{best_accuracy:.4f}"
)

print(
    f"Final test accuracy:      "
    f"{test_accuracy:.4f}"
)

print()
print("Model saved at:")
print(checkpoint_path)