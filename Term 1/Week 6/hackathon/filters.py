import re
import config

def matches(text, words):
    return [w for w in words if re.search(r"(?<!\w)" + re.escape(w) + r"(?!\w)", text, re.I)]

def relevant(record):
    langs = record.get("langs") or []
    if not any(x.lower().split("-")[0] == "en" for x in langs):
        return False
    text = record.get("text", "")
    return (len(text) >= 20 and bool(matches(text, config.TRANSPORT_WORDS))
            and bool(matches(text, config.SAFETY_WORDS))
            and not any(x in text.lower() for x in config.EXCLUSIONS))
