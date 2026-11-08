from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class GeoPoint(BaseModel):
    lat: float
    lon: float
    city: str
    country: str
    country_code: str
    state: str = ""

class Transaction(BaseModel):
    id: str
    timestamp: float
    user_id: str
    card_id: str
    card_type: str = "VISA_PLATINUM"
    amount: float
    currency: str = "USD"
    merchant: str
    merchant_category: str  # e.g., "RETAIL", "CRYPTO_EXCHANGE", "ELECTRONICS", "GAMBLING", "TRAVEL"
    channel: str = "ONLINE" # "ONLINE", "IN_STORE_POS", "ATM", "SWIFT_WIRE", "MOBILE_P2P"
    payment_method: str = "CARD" # "UPI", "CARD", "NET_BANKING", "WALLET", "ATM_CASH", "CRYPTO"
    payment_rail: str = "VISA"   # "UPI_VPA", "VISA", "MASTERCARD", "RUPAY", "AMEX", "SWIFT", "APPLE_PAY"
    upi_id: Optional[str] = None # e.g., "user@okhdfcbank"
    device_id: str
    ip_address: str
    is_vpn_tor: bool = False
    location: GeoPoint
    raw_metadata: Optional[Dict[str, Any]] = None

class RiskFactor(BaseModel):
    factor_name: str
    contribution: float
    description: str
    severity: str = "INFO" # "INFO", "WARNING", "CRITICAL"

class RiskBreakdown(BaseModel):
    rule_score: float
    ml_score: float
    graph_score: float
    ensemble_score: float
    factors: List[RiskFactor] = []

class FraudDecision(BaseModel):
    status: str # "APPROVED", "FLAGGED", "BLOCKED"
    risk_score: float # 0.0 to 100.0
    risk_level: str # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    triggered_rules: List[str] = []
    reason_summary: str
    latency_ms: float
    requires_2fa: bool = False

class EnrichedTransaction(BaseModel):
    transaction: Transaction
    decision: FraudDecision
    risk_breakdown: RiskBreakdown
    network_cluster_id: Optional[str] = None
    processed_at: float

class AttackScenarioRequest(BaseModel):
    scenario: str # "IMPOSSIBLE_TRAVEL", "RAPID_CARDING", "MULE_RING", "ACCOUNT_TAKEOVER", "MICRO_PROBING", "DARKNET_SPIKE"
    count: int = 5
    speed_factor: float = 1.0
