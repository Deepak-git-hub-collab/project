from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from backend.app.core.database import db
from backend.app.models.schemas.transaction import Transaction, EnrichedTransaction
from backend.app.services.fraud_detector import fraud_detector

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.get("", response_model=List[Dict[str, Any]])
def get_transactions(
    limit: int = Query(50, ge=1, le=200),
    status: Optional[str] = Query(None, description="Filter by APPROVED, FLAGGED, BLOCKED"),
    country: Optional[str] = Query(None, description="Filter by country name"),
    state: Optional[str] = Query(None, description="Filter by state / province name"),
    city: Optional[str] = Query(None, description="Filter by city name")
):
    return db.get_recent_transactions(limit=limit, status_filter=status, country_filter=country, state_filter=state, city_filter=city)

@router.get("/countries", response_model=List[str])
def get_countries():
    """Returns list of distinct countries present in recorded transactions."""
    return db.get_distinct_countries()

@router.get("/states", response_model=List[str])
def get_states(country: Optional[str] = Query(None, description="Optionally filter states by country")):
    """Returns list of distinct states/provinces recorded in transactions."""
    return db.get_distinct_states(country=country)

@router.get("/cities", response_model=List[str])
def get_cities(country: Optional[str] = Query(None, description="Optionally filter cities by country")):
    """Returns list of distinct cities recorded in transactions."""
    return db.get_distinct_cities(country=country)

@router.get("/{tx_id}", response_model=Dict[str, Any])
def get_transaction_detail(tx_id: str):
    tx = db.get_transaction_by_id(tx_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx

@router.post("/ingest", response_model=EnrichedTransaction)
def ingest_transaction(tx: Transaction):
    """Real-time REST endpoint for external payment gateways to process transactions."""
    return fraud_detector.process(tx)
