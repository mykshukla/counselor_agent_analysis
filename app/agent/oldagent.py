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

from app.store.memory_store import create_task_id


def run_agent(user_prompt: str):
    # 1️⃣ Parse structured prompt
    ctx = parse_user_prompt(user_prompt)
    

    # 2️⃣ Normalize free-text
    if ctx.get("intent_hint") is None:
        normalized = normalize_free_text(user_prompt)
        ctx.update(normalized)
    else:
        ctx["intent"] = ctx["intent_hint"]

    intent = ctx.get("intent")
    print(ctx)
    if not intent:
        return {"error": "Intent not detected"}

    # 3️⃣ Fast data (NO AI)
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

    task_id = create_task_id()

    return {
        "task_id": task_id,
        "status": "processing",
        "intent": intent,
        "context": {
            "from": ctx["from"],
            "to": ctx["to"],
            "country": ctx["country"],
            "campaign": ctx["campaign"],
            "counselor": ctx["counselor"],
        },
        "data_preview": json.loads(
            json.dumps(data[:5] if isinstance(data, list) else data, default=json_safe)
        )
    }
