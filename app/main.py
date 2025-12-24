from typing import Any
from fastapi import BackgroundTasks, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.agent.agent import run_agent
from app.agent.ai_tasks import run_ai_analysis
from app.services.metrics_service import (
    build_campaign_report, build_counselor_report, build_campaign_counselor_report
)
from app.services.forecasting_service import train_leads_model
from app.services.recommend_service import recommend_campaigns
from app.store.memory_store import get_result

app = FastAPI(title="Free Performance + Campaign Recommender Agent")

class RangeReq(BaseModel):
    start: str  # "2025-12-01 00:00:00"
    end: str    # "2025-12-23 23:59:59"
    country: str | None = None

class AgentRequest(BaseModel):
    message: str

class AgentResponse(BaseModel):
    reply: Any


# ---- CORS (frontend safe) ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # production me specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}    

@app.post("/ask")
def ask(req: AgentRequest):
    return run_agent(req.message)

# @app.post("/ask")
# def ask(req: AgentRequest, background_tasks: BackgroundTasks):
#     result = run_agent(req.message)

#     # 🔥 SAFE BACKGROUND TASK (NO ASYNC ISSUE)
#     background_tasks.add_task(
#         run_ai_analysis,
#             result["task_id"],
#             req.message,
#             result["data_preview"]
#     )

#     return result

@app.get("/result/{task_id}")
def get_result_api(task_id: str):
    res = get_result(task_id)
    return res if res else {"status": "processing"}

@app.post("/report/campaigns")
def report_campaigns(req: RangeReq):
    return {"items": build_campaign_report(req.start, req.end, req.country)}

@app.post("/report/counselors")
def report_counselors(req: RangeReq):
    return {"items": build_counselor_report(req.start, req.end, req.country)}

@app.post("/report/campaign-counselors")
def report_campaign_counselors(req: RangeReq):
    return {"items": build_campaign_counselor_report(req.start, req.end, req.country)}

@app.post("/ml/train-leads-model")
def train_model(req: RangeReq):
    # training uses CAMPAIGN_DAILY_AGG, country optional
    return train_leads_model(country=req.country)

@app.post("/recommend/campaigns")
def recommend(req: RangeReq):
    return {"items": recommend_campaigns(req.start, req.end, req.country, top_n=10)}
