from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any
from backend.app.streaming.kafka_producer import streamer
from backend.app.models.schemas.transaction import AttackScenarioRequest

router = APIRouter(prefix="/simulator", tags=["Simulator Engine"])

class RateRequest(BaseModel):
    tps: float

@router.post("/start")
def start_simulator():
    streamer.start()
    return {"status": "started", "rate_tps": streamer.rate_tps}

@router.post("/stop")
def stop_simulator():
    streamer.stop()
    return {"status": "stopped"}

@router.post("/rate")
def set_simulator_rate(req: RateRequest):
    streamer.set_rate(req.tps)
    return {"status": "updated", "rate_tps": streamer.rate_tps}

@router.post("/attack")
async def trigger_attack(req: AttackScenarioRequest):
    await streamer.inject_scenario(req.scenario, req.count)
    return {
        "status": "queued",
        "scenario": req.scenario,
        "message": f"Injected cyber-financial attack scenario: {req.scenario}"
    }
