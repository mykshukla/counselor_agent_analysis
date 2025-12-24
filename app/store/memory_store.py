import uuid
from typing import Dict

_AI_RESULTS: Dict[str, dict] = {}

def create_task_id() -> str:
    return str(uuid.uuid4())

def save_result(task_id: str, result: dict):
    _AI_RESULTS[task_id] = result

def get_result(task_id: str):
    return _AI_RESULTS.get(task_id)
