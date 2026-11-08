from pydantic import BaseModel
from typing import Optional, Dict, Any

class SystemMetrics(BaseModel):
    total_transactions: int
    flagged_transactions: int
    blocked_transactions: int
    approved_transactions: int
    prevented_loss_usd: float
    current_tps: float
    avg_latency_ms: float

