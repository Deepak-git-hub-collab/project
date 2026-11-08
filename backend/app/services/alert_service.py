from typing import List, Dict, Any, Optional
from backend.app.core.database import db

class AlertService:
    def get_alerts(self, limit: int = 50, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        return db.get_alerts(limit=limit, status_filter=status_filter)

    def resolve_alert(self, alert_id: str, action: str, notes: str = "", analyst_id: str = "analyst_sec_ops") -> bool:
        return db.resolve_alert(alert_id=alert_id, action=action, notes=notes, analyst_id=analyst_id)

alert_service = AlertService()

