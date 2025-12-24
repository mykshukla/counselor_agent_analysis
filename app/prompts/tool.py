# TOOLS = [
#     {
#         "type": "function",
#         "name": "get_campaign_overview",
#         "description": "Campaign performance list between dates (supports pagination).",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "start_date": {"type": "string"},
#                 "end_date": {"type": "string"},
#                 "country": {"type": "string"},
#                 "page": {"type": "integer", "default": 1},
#                 "page_size": {"type": "integer", "default": 100}
#             },
#             "required": ["start_date", "end_date"]
#         }
#     },
#     {
#         "type": "function",
#         "name": "get_campaign_counselor_performance",
#         "description": "Campaign → counselor performance between dates.",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "campaign": {"type": "string"},
#                 "country": {"type": "string"},
#                 "start_date": {"type": "string"},
#                 "end_date": {"type": "string"},
#                 "page": {"type": "integer", "default": 1},
#                 "page_size": {"type": "integer", "default": 20}
#             },
#             "required": ["start_date", "end_date"]
#         }
#     },
#     {
#         "type": "function",
#         "name": "get_campaign_waste_report",
#         "description": "Find campaigns wasting spend.",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "start_date": {"type": "string"},
#                 "end_date": {"type": "string"},
#                 "min_spend": {"type": "number", "default": 500}
#             },
#             "required": ["start_date", "end_date"]
#         }
#     }
# ]

TOOLS = {
    "get_campaign_overview": {
        "description": "Campaign performance list between dates",
        "required": ["start_date", "end_date"],
        "optional": [ "country"],
        "defaults": {
            "page": 1,
            "page_size": 100
        }
    },

    "get_campaign_counselor_performance": {
        "description": "Campaign → counselor performance",
        "required": ["start_date", "end_date"],
        "optional": ["campaign", "country"],
        "defaults": {
            "page": 1,
            "page_size": 100
        }
    },

    "get_campaign_waste_report": {
        "description": "Find campaigns wasting spend",
        "required": ["start_date", "end_date"],
        "defaults": {
            "min_spend": 500
        }
    }
}


INTENT_TOOL_MAP = {
    "campaign_performance": "get_campaign_metrics",
    "counselor_performance": "get_counselor_metrics",
    "campaign_counselor_breakdown": "get_campaign_counselor_metrics",
    "interaction_analysis": "get_interaction_summaries",
    "future_campaign_recommendation": "recommend_campaigns"
}