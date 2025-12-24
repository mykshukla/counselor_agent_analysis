import json
from app.llm.ollama_client import ollama_chat
from app.prompts.system_prompt import SYSTEM_PROMPT
from app.store.memory_store import save_result
from app.utils.utils import json_safe

def run_ai_analysis(task_id: str, question: str, data):
    try:
        payload = data[:10] if isinstance(data, list) else data

        prompt = f"""
            USER QUESTION:
            {question}

            DATA (Aggregated & Ranked):
            {json.dumps(payload, default=json_safe)}

            Analyze the data and respond strictly in the following sections:

            ### 📌 Key Insights
            ### 🏆 Best & Worst Performers
            ### 🔄 Funnel Metrics
            ### 🚀 Action Plan (Next 7–14 Days)
            """

        answer = ollama_chat(
            system=SYSTEM_PROMPT,
            user=prompt,
            temperature=0.3
        )

        save_result(task_id, {
            "status": "done",
            "analysis": answer
        })

    except Exception as e:
        save_result(task_id, {
            "status": "failed",
            "error": str(e)
        })
