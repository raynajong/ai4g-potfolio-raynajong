"""Pure Roboflow prediction parsing and correction logic for NatureClean AI."""
from __future__ import annotations

import math
from collections import Counter
from typing import Any

CLASSES = (
    "plastic_bottle",
    "plastic_bag",
    "plastic_packaging",
    "beverage_can",
    "paper_cardboard",
    "glass_bottle",
    "pen",
    "other_litter",
)

LABELS = {
    "plastic_bottle": "Plastic bottle",
    "plastic_bag": "Plastic bag",
    "plastic_packaging": "Plastic packaging",
    "beverage_can": "Beverage can",
    "paper_cardboard": "Paper & cardboard",
    "glass_bottle": "Glass bottle",
    "pen": "Discarded pen",
    "other_litter": "Other litter",
}
POINTS_PER_ITEM = 10


def find_predictions(payload: Any) -> tuple[list[dict], dict]:
    """Locate the prediction list in a (possibly nested) Roboflow Workflow output.

    Roboflow Workflows often return [{"predictions": {"image": ..., "predictions": [...]}}].
    We deliberately accept empty prediction lists and preserve any image metadata.
    """
    def walk(node: Any, inherited_meta: dict | None = None):
        if isinstance(node, dict):
            meta = node.get("image") if isinstance(node.get("image"), dict) else inherited_meta
            value = node.get("predictions")
            if isinstance(value, list) and all(isinstance(x, dict) for x in value):
                # Do not mistake an outer list of workflow-output dictionaries for detections.
                if not value or all("class" in x or all(k in x for k in ("x", "y", "width", "height")) for x in value):
                    return value, meta or {}
            if value is not None:
                result = walk(value, meta)
                if result is not None:
                    return result
            for key, child in node.items():
                if key in ("predictions", "image"):
                    continue
                result = walk(child, meta)
                if result is not None:
                    return result
        elif isinstance(node, list):
            for child in node:
                result = walk(child, inherited_meta)
                if result is not None:
                    return result
        return None

    located = walk(payload)
    if located is None:
        raise ValueError("Roboflow returned no recognizable predictions output.")
    return located


def clean_predictions(predictions: list[dict]) -> list[dict]:
    """Only retain usable bounding-box detections, sorted by confidence."""
    output: list[dict] = []
    for raw in predictions:
        try:
            x, y, w, h = (float(raw[k]) for k in ("x", "y", "width", "height"))
            confidence = float(raw.get("confidence", 0))
            if not all(math.isfinite(n) for n in (x, y, w, h, confidence)):
                continue
            if w <= 0 or h <= 0:
                continue
            label = str(raw.get("class", "other_litter"))
            if label not in CLASSES:
                label = "other_litter"
            output.append({
                "x": x, "y": y, "width": w, "height": h,
                "confidence": max(0.0, min(1.0, confidence)),
                "class": label,
            })
        except (ValueError, TypeError, KeyError):
            continue
    return sorted(output, key=lambda item: item["confidence"], reverse=True)


def confirmed_counts(rows: list[dict], missed: dict[str, int]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in rows:
        if bool(row.get("Keep", False)):
            label = str(row.get("Category", "other_litter"))
            counts[label if label in CLASSES else "other_litter"] += 1
    for label in CLASSES:
        counts[label] += max(0, int(missed.get(label, 0)))
    return {label: counts[label] for label in CLASSES if counts[label] > 0}


