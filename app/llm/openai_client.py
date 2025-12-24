from openai import OpenAI
import os

client = OpenAI("")

def openai_chat(system: str, user: str, temperature: float = 0.3) -> str:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        temperature=temperature
    )
    return resp.choices[0].message.content
