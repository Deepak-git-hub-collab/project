from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class AlertActionRequest(BaseModel):
    action: str
    notes: Optional[str] = ""
    analyst_id: Optional[str] = "analyst_sec_ops"

class AlertItem(BaseModel):
    id: str
    transaction_id: str
    timestamp: float
    user_id: str
    amount: float
    currency: str
    merchant: str
    risk_score: float
    risk_level: str
    status: str
    triggered_rules: List[str] = []
    reason_summary: str
    analyst_notes: Optional[str] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[float] = None

Alert = AlertItem

