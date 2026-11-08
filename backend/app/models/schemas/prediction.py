from pydantic import BaseModel
from typing import List, Dict, Any

class AnomalyPrediction(BaseModel):
    anomaly_score: float
    is_anomaly: bool
    factors: List[Dict[str, Any]] = []

