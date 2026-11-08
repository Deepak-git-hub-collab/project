from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from backend.app.services.alert_service import alert_service
from backend.app.models.schemas.alert import AlertActionRequest

router = APIRouter(prefix="/alerts", tags=["Fraud Alerts"])

@router.get("", response_model=List[Dict[str, Any]])
def get_alerts(
    limit: int = Query(50, ge=1, le=200),
    status: Optional[str] = Query(None, description="Filter by NEW, UNDER_REVIEW, RESOLVED_FRAUD, RESOLVED_LEGIT")
):
    return alert_service.get_alerts(limit=limit, status_filter=status)

@router.post("/{alert_id}/resolve")
def resolve_alert(alert_id: str, req: AlertActionRequest):
    success = alert_service.resolve_alert(
        alert_id=alert_id,
        action=req.action,
        notes=req.notes or "",
        analyst_id=req.analyst_id or "analyst_sec_ops"
    )
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"status": "success", "message": f"Alert {alert_id} resolved with action {req.action}"}
