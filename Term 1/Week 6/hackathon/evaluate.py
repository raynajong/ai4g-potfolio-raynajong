"""Blind labels: python evaluate.py sample. Then edit human_label, then score."""
import argparse
import json
from pathlib import Path
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import config
import db

LABELS = ["negative", "neutral", "positive"]
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["sample", "score"])
    args = parser.parse_args()
    con = db.connect()
    data = pd.read_sql_query("SELECT * FROM posts", con); con.close()
    folder = config.ROOT / "evaluation"; folder.mkdir(exist_ok=True)
    path = folder / "labels.csv"
    if args.action == "sample":
        if path.exists():
            raise SystemExit("labels.csv already exists. Keep your labels; rename it deliberately before drawing another sample.")
        if len(data) < 50:
            raise SystemExit("Need at least 50 real saved posts; currently %d." % len(data))
        sample = data.sample(50, random_state=42)[["uri", "text"]].copy()
        sample["human_label"] = ""
        sample.to_csv(path, index=False)
        print("Created", path, "— fill human_label with negative, neutral or positive without viewing predictions.")
        return
    if not path.exists():
        raise SystemExit("Run sample first.")
    labels = pd.read_csv(path, keep_default_na=False)
    labels.human_label = labels.human_label.str.strip().str.lower()
    if len(labels) != 50 or labels.uri.duplicated().any() or not labels.human_label.isin(LABELS).all():
        raise SystemExit("Provide 50 unique items, all labeled negative, neutral or positive.")
    test = labels.merge(data[["uri", "text", "label"]].rename(columns={"text":"current_text"}), on="uri", how="left", validate="one_to_one")
    if test.label.isna().any() or not test.text.eq(test.current_text).all():
        raise SystemExit("Some sampled posts were deleted or changed. Review the sample before evaluating; do not score stale text.")
    vader = SentimentIntensityAnalyzer()
    def predict(text):
        s = vader.polarity_scores(text)["compound"]
        return "positive" if s >= .05 else "negative" if s <= -.05 else "neutral"
    test["vader"] = test.text.map(predict)
    report = {}
    for name,col in [("RoBERTa","label"),("VADER","vader")]:
        report[name] = dict(accuracy=accuracy_score(test.human_label,test[col]),
                            macro_f1=f1_score(test.human_label,test[col],labels=LABELS,average="macro",zero_division=0),
                            confusion_matrix=confusion_matrix(test.human_label,test[col],labels=LABELS).tolist())
    test["roberta_wrong"] = test.human_label.ne(test.label)
    test["vader_wrong"] = test.human_label.ne(test.vader)
    test.to_csv(folder / "test_table.csv",index=False)
    (folder / "metrics.json").write_text(json.dumps({"label_order":LABELS,"results":report},indent=2))
    print(json.dumps(report,indent=2))
    print("Saved test_table.csv and metrics.json. Choose real failure cases; never invent errors.")
if __name__ == "__main__":
    main()
