from pathlib import Path

import numpy as np
import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModel


def vendi_score(features: np.ndarray) -> float:
    """
    Compute the Vendi Score from the exponential entropy of the feature
    similarity matrix.

    Reference:
        Friedman & Dieng, "The Vendi Score: A Diversity Evaluation Metric for Machine Learning" (2023)

    Range: [1, n], where 1 means all samples are identical and n means all
    samples are maximally diverse.
    """
    # L2-normalize features before computing cosine similarity.
    features = features / np.linalg.norm(features, axis=1, keepdims=True)

    similarity = features @ features.T

    eigenvalues = np.linalg.eigvalsh(similarity)
    eigenvalues = np.clip(eigenvalues, 0, None)
    eigenvalues = eigenvalues / eigenvalues.sum()

    eigenvalues = eigenvalues[eigenvalues > 1e-10]
    entropy = -np.sum(eigenvalues * np.log(eigenvalues))

    return float(np.exp(entropy))


class SlideStyleDiversity:
    def __init__(self, model_name: str = "facebook/dinov2-base", device: str = None):
        self.device = device or (
            "mps"
            if torch.backends.mps.is_available()
            else "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )
        self.model = AutoModel.from_pretrained(model_name).to(self.device).eval()
        self.processor = AutoImageProcessor.from_pretrained(model_name)

    def _extract_all_features(self, task_slides: list[Path]) -> np.ndarray:
        """Extract one representative feature vector for each slide deck."""
        all_features = []

        for image_dir in task_slides:
            pages = sorted(image_dir.glob("*.jpg")) or sorted(image_dir.glob("*.png"))
            images = [Image.open(p).convert("RGB") for p in pages]

            inputs = self.processor(images=images, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self.model(**inputs)
                features = outputs.last_hidden_state[:, 0, :]

            avg_feature = features.mean(dim=0)
            all_features.append(avg_feature.cpu().numpy())

        return np.stack(all_features)

    def evaluate(self, task_slides: list[Path]) -> float:
        features = self._extract_all_features(task_slides)
        vs = vendi_score(features)

        # Normalize the Vendi Score on the log scale: log(VS) in [0, log(n)].
        return float(np.log(vs) / np.log(len(features)))
