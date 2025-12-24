import json
from app.utils.prompt_parser import parse_user_prompt
from app.utils.prompt_normalizer import normalize_free_text
from app.utils.utils import json_safe

from app.services.metrics_service import (
    build_campaign_report,
    build_counselor_report,
    build_campaign_counselor_report
)
from app.services.recommend_service import recommend_campaigns

from app.llm.ollama_client import ollama_chat
from app.prompts.system_prompt import SYSTEM_PROMPT


def run_agent(user_prompt: str) -> dict:
    # -------------------------------------------------
    # 1️⃣ Parse + Normalize
    # -------------------------------------------------

    ctx = parse_user_prompt(user_prompt)

    if ctx.get("intent_hint") is None:
        normalized = normalize_free_text(user_prompt)
        ctx.update(normalized)
    else:
        ctx["intent"] = ctx["intent_hint"]

    intent = ctx.get("intent")
    if not intent:
        return {"error": "Unable to determine intent"}

    # -------------------------------------------------
    # 2️⃣ Fetch Data (FAST)
    # -------------------------------------------------
    if intent == "campaign_performance":
        data = build_campaign_report(ctx["from"], ctx["to"], ctx["country"])

    elif intent == "counselor_performance":
        data = build_counselor_report(ctx["from"], ctx["to"], ctx["country"])

    elif intent == "campaign_counselor_breakdown":
        data = build_campaign_counselor_report(ctx["from"], ctx["to"], ctx["country"])

    elif intent == "future_campaign_recommendation":
        data = recommend_campaigns(ctx["from"], ctx["to"], ctx["country"])

    else:
        return {"error": f"Unsupported intent: {intent}"}

    # -------------------------------------------------
    # 3️⃣ Prepare SMALL payload for AI
    # -------------------------------------------------
    payload = data[:15] if isinstance(data, list) else data

    prompt = f"""
USER QUESTION:
{ctx.get("question")}

DATA:
{json.dumps(payload, default=json_safe)}

Respond strictly in this format:

### 📌 Key Insights
### 🏆 Best & Worst Performers
### 🔄 Funnel Metrics
### 🚀 Action Plan (Next 7–14 Days)
"""

    # -------------------------------------------------
    # 4️⃣ AI CALL (SYNC, SINGLE RESPONSE)
    # -------------------------------------------------
    analysis = ollama_chat(
        system=SYSTEM_PROMPT,
        user=prompt,
        temperature=0.3
    )

    # -------------------------------------------------
    # 5️⃣ FINAL RESPONSE
    # -------------------------------------------------
    return {
        "intent": intent,
        "context": {
            "from": ctx["from"],
            "to": ctx["to"],
            "country": ctx["country"],
            "campaign": ctx["campaign"],
            "counselor": ctx["counselor"]
        },
        "analysis": analysis
    }
