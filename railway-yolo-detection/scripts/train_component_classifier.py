"""
Generic ResNet50 Component Classifier Training Script
======================================================
Train a ResNet50 classifier for any railway component type.

Usage:
    python train_component_classifier.py --component liner --data_dir ./data/liner_dataset
    python train_component_classifier.py --component rubber_pad --data_dir ./data/rubber_pad_dataset

Dataset structure expected:
    data_dir/
    ├── train/
    │   ├── good/
    │   ├── worn/
    │   ├── damaged/
    │   └── ... (other condition classes)
    └── valid/
        ├── good/
        ├── worn/
        └── ...
"""

import os
import argparse
import json
from pathlib import Path
from datetime import datetime

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
from tqdm import tqdm
import matplotlib.pyplot as plt


def get_data_transforms():
    """Get training and validation transforms."""
    train_transforms = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.RandomCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    val_transforms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    return train_transforms, val_transforms


def create_model(num_classes: int, pretrained: bool = True):
    """Create ResNet50 model with custom classifier head."""
    if pretrained:
        weights = models.ResNet50_Weights.IMAGENET1K_V2
        model = models.resnet50(weights=weights)
    else:
        model = models.resnet50(weights=None)
    
    # Freeze early layers (optional - comment out for full fine-tuning)
    for param in list(model.parameters())[:-20]:
        param.requires_grad = False
    
    # Replace classifier head
    in_features = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Dropout(0.5),
        nn.Linear(in_features, 512),
        nn.ReLU(),
        nn.Dropout(0.3),
        nn.Linear(512, num_classes)
    )
    
    return model


def train_epoch(model, dataloader, criterion, optimizer, device):
    """Train for one epoch."""
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    
    for images, labels in tqdm(dataloader, desc="Training"):
        images, labels = images.to(device), labels.to(device)
        
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        
        running_loss += loss.item()
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()
    
    return running_loss / len(dataloader), correct / total


def validate(model, dataloader, criterion, device):
    """Validate the model."""
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0
    
    with torch.no_grad():
        for images, labels in tqdm(dataloader, desc="Validating"):
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)
            
            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
    
    return running_loss / len(dataloader), correct / total


def main():
    parser = argparse.ArgumentParser(description="Train ResNet50 component classifier")
    parser.add_argument("--component", type=str, required=True,
                        help="Component type: erc, sleeper, liner, rubber_pad")
    parser.add_argument("--data_dir", type=str, required=True,
                        help="Path to dataset directory")
    parser.add_argument("--epochs", type=int, default=30,
                        help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=32,
                        help="Batch size for training")
    parser.add_argument("--lr", type=float, default=0.0001,
                        help="Learning rate")
    parser.add_argument("--output_dir", type=str, default="./models",
                        help="Output directory for saved models")
    parser.add_argument("--device", type=str, default="auto",
                        help="Device: cuda, mps, cpu, or auto")
    args = parser.parse_args()
    
    # Set device
    if args.device == "auto":
        if torch.cuda.is_available():
            device = torch.device("cuda")
        elif torch.backends.mps.is_available():
            device = torch.device("mps")
        else:
            device = torch.device("cpu")
    else:
        device = torch.device(args.device)
    
    print(f"\n{'='*60}")
    print(f"🚂 Training {args.component.upper()} Condition Classifier")
    print(f"{'='*60}")
    print(f"Device: {device}")
    print(f"Data: {args.data_dir}")
    print(f"Epochs: {args.epochs}")
    print(f"Batch Size: {args.batch_size}")
    print(f"Learning Rate: {args.lr}")
    
    # Load datasets
    train_transforms, val_transforms = get_data_transforms()
    
    train_dir = Path(args.data_dir) / "train"
    val_dir = Path(args.data_dir) / "valid"
    
    if not train_dir.exists():
        print(f"❌ Error: Training directory not found: {train_dir}")
        return
    
    train_dataset = datasets.ImageFolder(train_dir, transform=train_transforms)
    
    if val_dir.exists():
        val_dataset = datasets.ImageFolder(val_dir, transform=val_transforms)
    else:
        # Split train into train/val if no val directory
        from torch.utils.data import random_split
        train_size = int(0.8 * len(train_dataset))
        val_size = len(train_dataset) - train_size
        train_dataset, val_dataset = random_split(train_dataset, [train_size, val_size])
    
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, 
                              shuffle=True, num_workers=2)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size,
                            shuffle=False, num_workers=2)
    
    # Get class names
    class_names = train_dataset.dataset.classes if hasattr(train_dataset, 'dataset') else train_dataset.classes
    num_classes = len(class_names)
    
    print(f"\nClasses ({num_classes}): {class_names}")
    print(f"Train samples: {len(train_dataset)}")
    print(f"Val samples: {len(val_dataset)}")
    
    # Create model
    model = create_model(num_classes)
    model = model.to(device)
    
    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min',
                                                      patience=5, factor=0.5)
    
    # Training history
    history = {
        'train_loss': [], 'train_acc': [],
        'val_loss': [], 'val_acc': []
    }
    best_acc = 0.0
    
    # Output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'='*60}")
    print("Starting training...")
    print(f"{'='*60}\n")
    
    for epoch in range(args.epochs):
        print(f"\nEpoch {epoch + 1}/{args.epochs}")
        
        # Train
        train_loss, train_acc = train_epoch(model, train_loader, criterion, 
                                            optimizer, device)
        
        # Validate
        val_loss, val_acc = validate(model, val_loader, criterion, device)
        
        # Update scheduler
        scheduler.step(val_loss)
        
        # Save history
        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)
        
        print(f"  Train Loss: {train_loss:.4f} | Acc: {train_acc:.4f}")
        print(f"  Val Loss:   {val_loss:.4f} | Acc: {val_acc:.4f}")
        
        # Save best model
        if val_acc > best_acc:
            best_acc = val_acc
            model_path = output_dir / f"{args.component}_classifier_best.pt"
            torch.save({
                'model_state_dict': model.state_dict(),
                'class_names': class_names,
                'num_classes': num_classes,
                'best_accuracy': best_acc,
                'component': args.component
            }, model_path)
            print(f"  ✅ Saved best model (acc={best_acc:.4f})")
    
    # Save final training info
    info = {
        'component': args.component,
        'classes': class_names,
        'num_classes': num_classes,
        'best_accuracy': best_acc,
        'epochs_trained': args.epochs,
        'model_file': f"{args.component}_classifier_best.pt",
        'trained_at': datetime.now().isoformat()
    }
    
    with open(output_dir / f"{args.component}_classifier_info.json", 'w') as f:
        json.dump(info, f, indent=2)
    
    # Plot training history
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    
    ax1.plot(history['train_loss'], label='Train')
    ax1.plot(history['val_loss'], label='Val')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Loss')
    ax1.set_title(f'{args.component.upper()} - Training Loss')
    ax1.legend()
    
    ax2.plot(history['train_acc'], label='Train')
    ax2.plot(history['val_acc'], label='Val')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Accuracy')
    ax2.set_title(f'{args.component.upper()} - Accuracy')
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig(output_dir / f"{args.component}_training_history.png")
    print(f"\n📊 Saved training plot to {output_dir / f'{args.component}_training_history.png'}")
    
    print(f"\n{'='*60}")
    print(f"🎉 Training Complete!")
    print(f"{'='*60}")
    print(f"Best Validation Accuracy: {best_acc:.4f}")
    print(f"Model saved to: {output_dir / f'{args.component}_classifier_best.pt'}")


if __name__ == "__main__":
    main()
