from app.api.v1.routers.astrology_engine import router as astrology_engine_router
from app.api.v1.routers.audit import router as audit_router
from app.api.v1.routers.auth import router as auth_router
from app.api.v1.routers.b2b_astrology import router as b2b_astrology_router
from app.api.v1.routers.b2b_billing import router as b2b_billing_router
from app.api.v1.routers.b2b_editorial import router as b2b_editorial_router
from app.api.v1.routers.b2b_usage import router as b2b_usage_router
from app.api.v1.routers.billing import router as billing_router
from app.api.v1.routers.chat import router as chat_router
from app.api.v1.routers.enterprise_credentials import router as enterprise_credentials_router
from app.api.v1.routers.guidance import router as guidance_router
from app.api.v1.routers.ops_monitoring import router as ops_monitoring_router
from app.api.v1.routers.ops_persona import router as ops_persona_router
from app.api.v1.routers.privacy import router as privacy_router
from app.api.v1.routers.reference_data import router as reference_data_router
from app.api.v1.routers.support import router as support_router
from app.api.v1.routers.users import router as users_router

__all__ = [
    "auth_router",
    "astrology_engine_router",
    "audit_router",
    "billing_router",
    "b2b_astrology_router",
    "b2b_billing_router",
    "b2b_editorial_router",
    "b2b_usage_router",
    "chat_router",
    "enterprise_credentials_router",
    "guidance_router",
    "ops_monitoring_router",
    "ops_persona_router",
    "privacy_router",
    "reference_data_router",
    "support_router",
    "users_router",
]
