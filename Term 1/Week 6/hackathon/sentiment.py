import re
import config

def clean(text):
    return re.sub(r"\s+", " ", re.sub(r"@[A-Za-z0-9_.-]+", "@user", text)).strip()

class Analyzer:
    def __init__(self):
        from transformers import pipeline
        self.pipe = pipeline("text-classification", model=config.MODEL_NAME, top_k=None,
                             truncation=True, max_length=512, device=-1)

    def analyze(self, text):
        text = re.sub(r"https?://\S+", "http", clean(text))
        result = self.pipe(text)
        if result and isinstance(result[0], list):
            result = result[0]
        probs = {r["label"].lower(): float(r["score"]) for r in result}
        if not {"negative", "neutral", "positive"}.issubset(probs):
            raise ValueError("Unexpected model labels: " + str(probs))
        return dict(label=max(probs, key=probs.get), p_neg=probs["negative"],
                    p_neu=probs["neutral"], p_pos=probs["positive"],
                    score=probs["positive"] - probs["negative"])
