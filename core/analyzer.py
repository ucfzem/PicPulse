import torch
import torchvision.transforms as transforms
import torchvision.models as models
from PIL import Image
import numpy as np
import json
import urllib.request
import os

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
IMAGENET_URL = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
LABELS_PATH = os.path.join(MODELS_DIR, "imagenet_classes.txt")


class ImageAnalyzer:
    def __init__(self, device=None):
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)

        os.makedirs(MODELS_DIR, exist_ok=True)

        self.model = self._load_model()
        self.labels = self._load_labels()
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            ),
        ])

    def _load_model(self):
        model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.IMAGENET1K_V1)
        model.eval()
        model.to(self.device)
        return model

    def _load_labels(self):
        if not os.path.exists(LABELS_PATH):
            try:
                urllib.request.urlretrieve(IMAGENET_URL, LABELS_PATH)
            except Exception:
                return [f"class_{i}" for i in range(1000)]
        with open(LABELS_PATH) as f:
            return [line.strip() for line in f.readlines()]

    def _clean_label(self, label):
        label = label.split(",")[0].strip()
        label = label.replace(" ", "_").lower()
        label = "".join(c for c in label if c.isalnum() or c == "_")
        return label or "unknown"

    def analyze(self, image_path):
        try:
            image = Image.open(image_path).convert("RGB")
            input_tensor = self.transform(image).unsqueeze(0).to(self.device)

            with torch.no_grad():
                output = self.model(input_tensor)
                probabilities = torch.nn.functional.softmax(output[0], dim=0)

            top_prob, top_idx = torch.topk(probabilities, 3)
            top_prob = top_prob.cpu().numpy()
            top_idx = top_idx.cpu().numpy()

            results = []
            for prob, idx in zip(top_prob, top_idx):
                label_raw = self.labels[int(idx)] if int(idx) < len(self.labels) else f"class_{int(idx)}"
                label_clean = self._clean_label(label_raw)
                results.append({
                    "label_raw": label_raw,
                    "label_clean": label_clean,
                    "confidence": float(prob),
                    "class_id": int(idx),
                })

            return {
                "success": True,
                "top_label": results[0]["label_clean"],
                "top_label_raw": results[0]["label_raw"],
                "confidence": results[0]["confidence"],
                "predictions": results,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
