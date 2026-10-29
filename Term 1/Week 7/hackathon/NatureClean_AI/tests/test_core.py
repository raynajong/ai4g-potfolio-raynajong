import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core import find_predictions, clean_predictions, confirmed_counts


def test_nested_roboflow_response():
    result = [{"predictions": {"image": {"width": 1200, "height": 800},
                 "predictions": [{"class": "plastic_bottle", "confidence": 0.445,
                                  "x": 300, "y": 400, "width": 50, "height": 90}]}}]
    raw, meta = find_predictions(result)
    assert meta == {"width": 1200, "height": 800}
    assert clean_predictions(raw)[0]["confidence"] == 0.445


def test_empty_prediction_list():
    result = [{"predictions": {"image": {"width": 500}, "predictions": []}}]
    assert find_predictions(result)[0] == []


def test_review_corrects_wrong_class_and_adds_missed():
    rows = [{"Keep": True, "Category": "plastic_packaging"},
            {"Keep": False, "Category": "paper_cardboard"}]
    assert confirmed_counts(rows, {"plastic_bottle": 2}) == {
        "plastic_bottle": 2, "plastic_packaging": 1}


def test_invalid_predictions_are_ignored():
    preds = clean_predictions([
        {"class": "plastic_bottle", "confidence": 0.67, "x": 5, "y": 5,
         "width": -10, "height": 20},
        {"class": "unknown", "confidence": 0.35, "x": 5, "y": 5,
         "width": 10, "height": 20},
    ])
    assert len(preds) == 1
    assert preds[0]["class"] == "other_litter"
