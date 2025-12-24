import json
from app.llm.ollama_client import ollama_chat

NORMALIZER_SYSTEM = """
You convert user questions into a STANDARD ANALYSIS_REQUEST format.

Rules:
- Infer reasonable defaults if missing
- Use ALL when unsure
- If no date is given, use last 60 days
- Return STRICT JSON only (no explanation)
"""

NORMALIZER_USER_TEMPLATE = """
User question:
"{question}"

Return JSON in this format:
{{
  "intent": "campaign_performance | counselor_performance | campaign_counselor_breakdown | future_campaign_recommendation | counselor_coaching",
  "from": "YYYY-MM-DD",
  "to": "YYYY-MM-DD",
  "country": "ALL",
  "campaign": "ALL",
  "counselor": "ALL",
  "include_call": false,
  "include_video": false,
  "question": "<rewritten clear question>"
}}
"""

def normalize_free_text(question: str) -> dict:
    response = ollama_chat(
        system=NORMALIZER_SYSTEM,
        user=NORMALIZER_USER_TEMPLATE.format(question=question),
        temperature=0
    )

    return json.loads(response)
