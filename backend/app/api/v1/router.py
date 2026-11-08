from fastapi import APIRouter
from backend.app.api.v1.endpoints.transactions import router as transactions_router
from backend.app.api.v1.endpoints.rules import router as rules_router
from backend.app.api.v1.endpoints.analytics import router as analytics_router
from backend.app.api.v1.endpoints.simulator import router as simulator_router
from backend.app.api.v1.endpoints.fraud_alerts import router as alerts_router
from backend.app.api.v1.endpoints.health import router as health_router
from backend.app.api.v1.endpoints.auth import router as auth_router
from backend.app.api.v1.endpoints.actions import router as actions_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router)
api_v1_router.include_router(actions_router)
api_v1_router.include_router(transactions_router)
api_v1_router.include_router(rules_router)
api_v1_router.include_router(analytics_router)
api_v1_router.include_router(simulator_router)
api_v1_router.include_router(alerts_router)
api_v1_router.include_router(health_router)
