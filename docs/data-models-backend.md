# Data Models - Backend

## ORM and Migration
- ORM: SQLAlchemy models in `backend/app/infra/db/models/`
- Migrations: Alembic versions in `backend/migrations/versions/`

## Core Domain Models
- User/account: `user.py`, `user_birth_profile.py`, `user_refresh_token.py`
- Astrology/reference: `reference.py`, `chart_result.py`
- Conversation: `chat_conversation.py`, `chat_message.py`
- Billing/subscription: `billing.py`
- Privacy/audit/support: `privacy.py`, `audit_event.py`, `support_incident.py`
- Feature governance: `feature_flag.py`, `persona_config.py`
- B2B: `enterprise_account.py`, `enterprise_api_credential.py`, `enterprise_editorial_config.py`, `enterprise_usage.py`, `enterprise_billing.py`

## Data Governance Highlights
- Audit trail for sensitive operations (`audit_events`)
- Privacy request lifecycle persistence
- Version linkage for astrology result traceability
- Enterprise usage/billing reconciliation data models

## Migration Coverage
Alembic history includes staged creation for:
- Reference tables and result traceability
- User/profile/auth token tables
- Billing and quota tables
- Privacy and audit tables
- Support incidents
- Enterprise credentials/editorial/usage/billing
- Performance indexes and feature flag/persona extensions

## Local vs Production
- Local default supports SQLite (`sqlite:///./horoscope.db`)
- Production target supports PostgreSQL via environment-configured `DATABASE_URL`
