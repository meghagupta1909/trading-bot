from fastapi import APIRouter
from app.api.orders import router as orders_router
from app.api.health import router as health_router

api_router = APIRouter(prefix="/api")
api_router.include_router(orders_router)
api_router.include_router(health_router)

__all__ = ["api_router"]