import re

def parse_user_prompt(text: str) -> dict:
    def get(key):
        m = re.search(rf"{key}:\s*(.+)", text)
        return m.group(1).strip() if m else None

    return {
        "intent_hint": get("INTENT"),
        "from": get("FROM"),
        "to": get("TO"),
        "country": get("COUNTRY"),
        "campaign": get("CAMPAIGN"),
        "counselor": get("COUNSELOR"),
        "include_call": get("INCLUDE_CALL_SUMMARIES") == "YES",
        "include_video": get("INCLUDE_VIDEO_SUMMARIES") == "YES",
        "question": get("QUESTION"),
        "raw_prompt": text
    }
