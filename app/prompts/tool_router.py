import re
from app.utils.utils import normalize_country, normalize_param


def decide_tool(user_message: str) -> str:
    text = user_message.lower()

    if "waste" in text or "wasting" in text:
        return "get_campaign_waste_report"

    if "counselor" in text:
        return "get_campaign_counselor_performance"

    return "get_campaign_overview"



def normalize_tool_args(tool_name: str, args: dict, tools: dict):
    tool = tools[tool_name]

    # Apply defaults
    for k, v in tool.get("defaults", {}).items():
        args.setdefault(k, v)

    # Normalize optional params
    for opt in tool.get("optional", []):
        if opt in args:
            val = normalize_param(args.get(opt))
            if opt == "country" and val:
                val = normalize_country(val)
            args[opt] = val

    # Validate required params
    missing = [r for r in tool["required"] if not args.get(r)]
    if missing:
        raise ValueError(f"Missing required args for {tool_name}: {missing}")

    return args

def extract_campaign_country(text: str) -> dict:
    args = {}
    t = text.lower()

    # Country extraction (extend list anytime)
    for c in ["uae", "india", "usa", "uk", "canada"]:
        if c in t:
            args["country"] = c.upper()
            break

    # Campaign extraction
    m = re.search(r"(brochure|facebook|google|organic|referral)", t)
    if m:
        args["campaign"] = m.group(1)

    return args