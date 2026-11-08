from pydantic import BaseModel
from typing import Optional

class DetectionRule(BaseModel):
    id: str
    name: str
    description: str
    category: str
    condition_code: str
    threshold: float
    weight: float
    action: str
    enabled: bool

class RuleUpdateRequest(BaseModel):
    enabled: Optional[bool] = None
    threshold: Optional[float] = None
    weight: Optional[float] = None
    action: Optional[str] = None

