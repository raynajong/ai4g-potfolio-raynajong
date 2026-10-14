import os
from pathlib import Path
ROOT = Path(__file__).resolve().parent
DEMO = os.environ.get("TRANSIT_DEMO") == "1"
DB_PATH = ROOT / ("demo_safety.db" if DEMO else "bluesky_safety.db")
MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"
ENDPOINTS = ["wss://jetstream2.us-east.bsky.network/subscribe", "wss://jetstream1.us-east.bsky.network/subscribe"]
TRANSPORT_WORDS = ["train", "trains", "railway", "subway", "metro", "tram", "trams", "bus stop", "bus stops", "train station", "rail station"]
SAFETY_WORDS = ["safe", "safety", "unsafe", "scared", "scary", "afraid", "dark", "lighting", "harassed", "harassment", "threatened", "threatening", "creepy", "sketchy", "security", "assault", "attacked", "dangerous", "fear", "alone"]
EXCLUSIONS = ["subway surfers", "subway sandwich", "metro boomin", "train a model", "train the model"]
