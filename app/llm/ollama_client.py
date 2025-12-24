import requests
import time

OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "qwen2.5:3b-instruct"

DEFAULT_TIMEOUT = 180  # 🔥 3 minutes (safe for 7B model)

# def ollama_chat(system: str, user: str, temperature: float = 0.2) -> str:
#     payload = {
#         "model": OLLAMA_MODEL,
#         "stream": False,
#         "messages": [
#             {"role": "system", "content": system},
#             {"role": "user", "content": user}
#         ],
#         "options": {
#             "temperature": temperature,
#             "num_ctx": 4096,     # 🔥 limit context
#             "num_predict": 512  # 🔥 limit output tokens
#         }
#     }

#     try:
#         start = time.time()
#         res = requests.post(
#             OLLAMA_URL,
#             json=payload,
#             timeout=DEFAULT_TIMEOUT
#         )
#         res.raise_for_status()
#         data = res.json()
#         return data["message"]["content"]

#     except requests.exceptions.Timeout:
#         raise RuntimeError("Ollama timeout: model took too long to respond")

#     except Exception as e:
#         raise RuntimeError(f"Ollama error: {str(e)}")

def ollama_chat(system: str, user: str, temperature: float = 0.2) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "stream": False,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        "options": {
            "temperature": temperature,
            "num_ctx": 2048,
            "num_predict": 300
        }
    }

    try:
        res = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=60   # ⬅️ LOWER timeout, not higher
        )
        res.raise_for_status()
        return res.json()["message"]["content"]

    except Exception:
        # 🔥 FALLBACK (NO LLM)
        return (
            "### 📌 Key Insights\n"
            "- Data fetched successfully but AI analysis timed out.\n\n"
            "### 🏆 Best & Worst Performers\n"
            "- Please refer to top rows in data.\n\n"
            "### 🔄 Funnel Metrics\n"
            "- Leads → Demo → Enrollment ratios available in data.\n\n"
            "### 🚀 Action Plan (Next 7–14 Days)\n"
            "- Use high-conversion campaigns and coach low performers."
        )

