from fastapi import APIRouter, HTTPException
from typing import List, Optional
from backend.app.core.database import db
from backend.app.models.schemas.rule import DetectionRule, RuleUpdateRequest
from backend.app.services.rule_engine import rule_engine

router = APIRouter(prefix="/rules", tags=["Rules Engine"])

@router.get("", response_model=List[DetectionRule])
def list_rules():
    return db.get_all_rules()

@router.patch("/{rule_id}")
def update_rule(rule_id: str, req: RuleUpdateRequest):
    success = db.update_rule(
        rule_id=rule_id,
        enabled=req.enabled,
        threshold=req.threshold,
        weight=req.weight,
        action=req.action
    )
    if not success:
        raise HTTPException(status_code=404, detail="Rule not found or no changes applied")
    
    # Reload in-memory rule engine cache
    rule_engine.reload_rules()
    return {"status": "success", "message": f"Rule {rule_id} updated successfully"}
