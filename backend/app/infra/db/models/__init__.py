# Registre racine des modèles SQLAlchemy hors périmètre LLM.
"""Expose les modèles DB non-LLM conservés dans le namespace racine."""

from app.infra.db.models import house_system_resolution as _house_system_resolution  # noqa: F401
from app.infra.db.models.astrologer import (
    AstrologerProfileModel,
    AstrologerPromptProfileModel,
    AstrologerReviewModel,
)
from app.infra.db.models.audit_event import AuditEventModel
from app.infra.db.models.billing import (
    BillingPlanModel,
    PaymentAttemptModel,
    SubscriptionPlanChangeModel,
    UserDailyQuotaUsageModel,
    UserSubscriptionModel,
)
from app.infra.db.models.calibration import CalibrationRawDayModel
from app.infra.db.models.canonical_entitlement_mutation_audit import (
    CanonicalEntitlementMutationAuditModel,
)
from app.infra.db.models.chart_result import ChartResultModel
from app.infra.db.models.chat_conversation import ChatConversationModel
from app.infra.db.models.chat_message import ChatMessageModel
from app.infra.db.models.config_text import ConfigTextModel
from app.infra.db.models.consultation_template import ConsultationTemplateModel
from app.infra.db.models.consultation_third_party import (
    ConsultationThirdPartyProfileModel,
    ConsultationThirdPartyUsageModel,
)
from app.infra.db.models.daily_prediction import (
    DailyPredictionCategoryScoreModel,
    DailyPredictionRunModel,
    DailyPredictionTimeBlockModel,
    DailyPredictionTurningPointModel,
)
from app.infra.db.models.editorial_template import EditorialTemplateVersionModel
from app.infra.db.models.email_log import EmailLogModel
from app.infra.db.models.enterprise_account import EnterpriseAccountModel
from app.infra.db.models.enterprise_api_credential import EnterpriseApiCredentialModel
from app.infra.db.models.enterprise_billing import (
    EnterpriseAccountBillingPlanModel,
    EnterpriseBillingCycleModel,
    EnterpriseBillingPlanModel,
)
from app.infra.db.models.enterprise_editorial_config import EnterpriseEditorialConfigModel
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
from app.infra.db.models.geo_place_resolved import GeoPlaceResolvedModel
from app.infra.db.models.geocoding_query_cache import GeocodingQueryCacheModel
from app.infra.db.models.interpretation_reference import (
    AstralAspectInterpretationProfileModel,
    AstralHouseAxisDefinitionModel,
    AstralHouseAxisMemberModel,
    HouseInterpretationProfileModel,
)
from app.infra.db.models.pdf_template import PdfTemplateModel
from app.infra.db.models.persona_config import PersonaConfigModel
from app.infra.db.models.prediction_reference import (
    AspectProfileModel,
    AstralAspectDefinitionModel,
    AstralAspectOrbRuleModel,
    AstralDefaultValenceModel,
    AstralInterpretiveValenceModel,
    AstralPlanetSignDignityModel,
    AstroPointModel,
    HouseCategoryWeightModel,
    HouseProfileModel,
    PlanetCategoryWeightModel,
    PlanetProfileModel,
    PointCategoryWeightModel,
    PredictionCategoryModel,
)
from app.infra.db.models.prediction_ruleset import (
    CategoryCalibrationModel,
    PredictionRulesetModel,
    RulesetEventTypeModel,
    RulesetParameterModel,
)
from app.infra.db.models.privacy import (
    UserPrivacyRequestModel,
)
from app.infra.db.models.product_entitlements import (
    FeatureCatalogModel,
    FeatureUsageCounterModel,
    PlanCatalogModel,
    PlanFeatureBindingModel,
    PlanFeatureQuotaModel,
)
from app.infra.db.models.reference import (
    AspectModel,
    AstralAspectFamilyModel,
    AstralDignityTypeModel,
    AstralElementModel,
    AstralHouseSystemModel,
    AstralModalityModel,
    AstralPolarityModel,
    AstralSignModel,
    AstralSignProfileModel,
    AstralSystemModel,
    HouseModel,
    LanguageModel,
    PlanetModel,
    ReferenceVersionModel,
)
from app.infra.db.models.stripe_billing import StripeBillingProfileModel
from app.infra.db.models.stripe_webhook_event import StripeWebhookEventModel
from app.infra.db.models.support_incident import SupportIncidentModel
from app.infra.db.models.support_ticket_category import SupportTicketCategoryModel
from app.infra.db.models.token_usage_log import UserTokenUsageLogModel
from app.infra.db.models.user import UserModel
from app.infra.db.models.user_birth_profile import UserBirthProfileModel
from app.infra.db.models.user_natal_interpretation import (
    UserNatalInterpretationModel,
)
from app.infra.db.models.user_prediction_baseline import UserPredictionBaselineModel
from app.infra.db.models.user_refresh_token import UserRefreshTokenModel

__all__ = [
    "AuditEventModel",
    "AstrologerProfileModel",
    "AstrologerPromptProfileModel",
    "AstrologerReviewModel",
    "AstralAspectInterpretationProfileModel",
    "AstralHouseAxisDefinitionModel",
    "AstralHouseAxisMemberModel",
    "BillingPlanModel",
    "PaymentAttemptModel",
    "SubscriptionPlanChangeModel",
    "UserDailyQuotaUsageModel",
    "UserSubscriptionModel",
    "CalibrationRawDayModel",
    "CanonicalEntitlementMutationAuditModel",
    "CanonicalEntitlementMutationAuditReviewModel",
    "CanonicalEntitlementMutationAuditReviewEventModel",
    "CanonicalEntitlementMutationAlertDeliveryAttemptModel",
    "CanonicalEntitlementMutationAlertEventModel",
    "CanonicalEntitlementMutationAlertHandlingModel",
    "CanonicalEntitlementMutationAlertHandlingEventModel",
    "CanonicalEntitlementMutationAlertSuppressionApplicationModel",
    "CanonicalEntitlementMutationAlertSuppressionRuleModel",
    "ChartResultModel",
    "ChatConversationModel",
    "ChatMessageModel",
    "ConsultationTemplateModel",
    "ConfigTextModel",
    "ConsultationThirdPartyProfileModel",
    "ConsultationThirdPartyUsageModel",
    "DailyPredictionCategoryScoreModel",
    "DailyPredictionRunModel",
    "DailyPredictionTimeBlockModel",
    "DailyPredictionTurningPointModel",
    "EmailLogModel",
    "EditorialTemplateVersionModel",
    "EnterpriseAccountModel",
    "EnterpriseApiCredentialModel",
    "EnterpriseBillingPlanModel",
    "EnterpriseAccountBillingPlanModel",
    "EnterpriseBillingCycleModel",
    "EnterpriseEditorialConfigModel",
    "EnterpriseFeatureUsageCounterModel",
    "FeatureFlagModel",
    "GeoPlaceResolvedModel",
    "GeocodingQueryCacheModel",
    "PdfTemplateModel",
    "PersonaConfigModel",
    "PlanCatalogModel",
    "FeatureCatalogModel",
    "PlanFeatureBindingModel",
    "PlanFeatureQuotaModel",
    "FeatureUsageCounterModel",
    "PredictionCategoryModel",
    "PlanetProfileModel",
    "AstralPlanetSignDignityModel",
    "HouseProfileModel",
    "PlanetCategoryWeightModel",
    "HouseCategoryWeightModel",
    "HouseInterpretationProfileModel",
    "AstroPointModel",
    "PointCategoryWeightModel",
    "AspectProfileModel",
    "AstralAspectDefinitionModel",
    "AstralAspectOrbRuleModel",
    "AstralDefaultValenceModel",
    "AstralInterpretiveValenceModel",
    "UserPrivacyRequestModel",
    "SupportIncidentModel",
    "SupportTicketCategoryModel",
    "UserModel",
    "UserBirthProfileModel",
    "UserNatalInterpretationModel",
    "UserPredictionBaselineModel",
    "UserRefreshTokenModel",
    "AspectModel",
    "AstralAspectFamilyModel",
    "AstralDignityTypeModel",
    "AstralElementModel",
    "AstralHouseSystemModel",
    "AstralModalityModel",
    "AstralPolarityModel",
    "AstralSystemModel",
    "HouseModel",
    "LanguageModel",
    "PlanetModel",
    "ReferenceVersionModel",
    "AstralSignModel",
    "AstralSignProfileModel",
    "StripeBillingProfileModel",
    "StripeWebhookEventModel",
    "UserTokenUsageLogModel",
    "PredictionRulesetModel",
    "RulesetEventTypeModel",
    "RulesetParameterModel",
    "CategoryCalibrationModel",
]
