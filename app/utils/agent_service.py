from app.utils.prompt_parser import parse_user_prompt
from app.services.metrics_service import (
    build_campaign_report,
    build_counselor_report,
    build_campaign_counselor_report
)
from app.services.recommend_service import recommend_campaigns

def oldrun_agent(user_prompt: str):
    ctx = parse_user_prompt(user_prompt)
    intent = ctx["intent"]

    if intent == "campaign_performance":
        data = build_campaign_report(ctx["from"], ctx["to"], ctx["country"])

    elif intent == "counselor_performance":
        data = build_counselor_report(ctx["from"], ctx["to"], ctx["country"])

    elif intent == "campaign_counselor_breakdown":
        data = build_campaign_counselor_report(ctx["from"], ctx["to"], ctx["country"])

    elif intent == "future_campaign_recommendation":
        data = recommend_campaigns(ctx["from"], ctx["to"], ctx["country"])

    else:
        return {"error": "Unknown intent"}

    return {
        "intent": intent,
        "filters": ctx,
        "result": data
    }
