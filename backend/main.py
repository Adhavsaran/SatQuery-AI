"""FastAPI surface for controlled SatQuery analysis."""
from fastapi import FastAPI, HTTPException
from backend.config import settings
from backend.schemas import QueryRequest, QueryResponse, HealthResponse
from agent.agent import agent
from agent.tool_registry import tool_registry
from models.base import UnavailableVisionAdapter

app=FastAPI(title="SatQuery AI",version="0.2.0",description="Evidence-grounded remote-sensing analysis; optional model adapters never fabricate inference.")
@app.get("/health",response_model=HealthResponse)
async def health_check(): return HealthResponse(status="healthy",version="0.2.0",environment=settings.environment)
@app.get("/models")
async def models():
    return {"vqa":UnavailableVisionAdapter("remote-sensing-vqa","vqa","RSVQA-compatible HuggingFace model").get_metadata(),"captioning":UnavailableVisionAdapter("remote-sensing-captioner","captioning","VRSBench-compatible HuggingFace model").get_metadata()}
@app.get("/tools")
async def tools(): return tool_registry.list_tools()
@app.post("/analyze",response_model=QueryResponse)
@app.post("/agent/query",response_model=QueryResponse)
@app.post("/api/query",response_model=QueryResponse)
async def analyze(request:QueryRequest): return await agent.process_query(request)
@app.post("/vqa",response_model=QueryResponse)
@app.post("/caption",response_model=QueryResponse)
@app.post("/ground",response_model=QueryResponse)
@app.post("/detect",response_model=QueryResponse)
@app.post("/segment",response_model=QueryResponse)
@app.post("/change",response_model=QueryResponse)
@app.post("/sar",response_model=QueryResponse)
@app.post("/fusion",response_model=QueryResponse)
async def task(request:QueryRequest): return await agent.process_query(request)
@app.post("/api/validate")
async def validate(request:QueryRequest):
    response=await agent.process_query(request)
    return response.execution_trace.validation if response.execution_trace else response.findings
@app.get("/api/agent/status")
async def agent_status(): return agent.get_status()
