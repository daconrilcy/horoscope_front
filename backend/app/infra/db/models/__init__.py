# Registre racine des modèles SQLAlchemy conservés après externalisation Astral.
"""Expose uniquement les modèles DB applicatifs conservés par le backend."""

from app.infra.db.models.audit_event import AuditEventModel
from app.infra.db.models.billing import (
    BillingPlanModel,
    PaymentAttemptModel,
    SubscriptionPlanChangeModel,
    UserDailyQuotaUsageModel,
    UserSubscriptionModel,
)
from app.infra.db.models.canonical_entitlement_mutation_audit import (
    CanonicalEntitlementMutationAuditModel,
)
from app.infra.db.models.config_text import ConfigTextModel
from app.infra.db.models.email_log import EmailLogModel
from app.infra.db.models.enterprise_account import EnterpriseAccountModel
from app.infra.db.models.enterprise_api_credential import EnterpriseApiCredentialModel
from app.infra.db.models.enterprise_billing import (
    EnterpriseAccountBillingPlanModel,
    EnterpriseBillingCycleModel,
    EnterpriseBillingPlanModel,
)
from app.infra.db.models.enterprise_feature_usage_counters import (
    EnterpriseFeatureUsageCounterModel,
)
from app.infra.db.models.entitlement_mutation.alert.alert_event import (
    CanonicalEntitlementMutationAlertEventModel,
)
from app.infra.db.models.entitlement_mutation.alert.delivery_attempt import (
    CanonicalEntitlementMutationAlertDeliveryAttemptModel,
)
from app.infra.db.models.entitlement_mutation.alert.handling import (
    CanonicalEntitlementMutationAlertHandlingModel,
)
from app.infra.db.models.entitlement_mutation.alert.handling_event import (
    CanonicalEntitlementMutationAlertHandlingEventModel,
)
from app.infra.db.models.entitlement_mutation.audit.review import (
    CanonicalEntitlementMutationAuditReviewModel,
)
from app.infra.db.models.entitlement_mutation.audit.review_event import (
    CanonicalEntitlementMutationAuditReviewEventModel,
)
from app.infra.db.models.entitlement_mutation.suppression.suppression_application import (
    CanonicalEntitlementMutationAlertSuppressionApplicationModel,
)
from app.infra.db.models.entitlement_mutation.suppression.suppression_rule import (
    CanonicalEntitlementMutationAlertSuppressionRuleModel,
)
from app.infra.db.models.feature_flag import FeatureFlagModel
from app.infra.db.models.flagged_content import FlaggedContentModel
from app.infra.db.models.geo_place_resolved import GeoPlaceResolvedModel
from app.infra.db.models.geocoding_query_cache import GeocodingQueryCacheModel
from app.infra.db.models.language import LanguageModel
from app.infra.db.models.privacy import UserPrivacyRequestModel
from app.infra.db.models.product_entitlements import (
    FeatureCatalogModel,
    FeatureUsageCounterModel,
    PlanCatalogModel,
    PlanFeatureBindingModel,
    PlanFeatureQuotaModel,
)
from app.infra.db.models.stripe_billing import StripeBillingProfileModel
from app.infra.db.models.stripe_webhook_event import StripeWebhookEventModel
from app.infra.db.models.support_incident import SupportIncidentModel
from app.infra.db.models.support_ticket_category import SupportTicketCategoryModel
from app.infra.db.models.token_usage_log import UserTokenUsageLogModel
from app.infra.db.models.user import UserModel
from app.infra.db.models.user_birth_profile import UserBirthProfileModel
from app.infra.db.models.user_refresh_token import UserRefreshTokenModel

__all__ = [
    "AuditEventModel",
    "BillingPlanModel",
    "CanonicalEntitlementMutationAlertDeliveryAttemptModel",
    "CanonicalEntitlementMutationAlertEventModel",
    "CanonicalEntitlementMutationAlertHandlingEventModel",
    "CanonicalEntitlementMutationAlertHandlingModel",
    "CanonicalEntitlementMutationAlertSuppressionApplicationModel",
    "CanonicalEntitlementMutationAlertSuppressionRuleModel",
    "CanonicalEntitlementMutationAuditModel",
    "CanonicalEntitlementMutationAuditReviewEventModel",
    "CanonicalEntitlementMutationAuditReviewModel",
    "ConfigTextModel",
    "EmailLogModel",
    "EnterpriseAccountBillingPlanModel",
    "EnterpriseAccountModel",
    "EnterpriseApiCredentialModel",
    "EnterpriseBillingCycleModel",
    "EnterpriseBillingPlanModel",
    "EnterpriseFeatureUsageCounterModel",
    "FeatureCatalogModel",
    "FeatureFlagModel",
    "FeatureUsageCounterModel",
    "FlaggedContentModel",
    "GeoPlaceResolvedModel",
    "GeocodingQueryCacheModel",
    "LanguageModel",
    "PaymentAttemptModel",
    "PlanCatalogModel",
    "PlanFeatureBindingModel",
    "PlanFeatureQuotaModel",
    "StripeBillingProfileModel",
    "StripeWebhookEventModel",
    "SubscriptionPlanChangeModel",
    "SupportIncidentModel",
    "SupportTicketCategoryModel",
    "UserDailyQuotaUsageModel",
    "UserModel",
    "UserPrivacyRequestModel",
    "UserRefreshTokenModel",
    "UserSubscriptionModel",
    "UserBirthProfileModel",
    "UserTokenUsageLogModel",
]
