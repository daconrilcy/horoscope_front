from __future__ import annotations

import logging
import time
from dataclasses import dataclass

import stripe
from sqlalchemy.orm import Session

from app.core.config import settings
from app.infra.db.models.stripe_billing import StripeBillingProfileModel
from app.integrations.stripe_client import get_stripe_client
from app.services.stripe_billing_profile_service import StripeBillingProfileService

logger = logging.getLogger(__name__)


class StripeCustomerPortalServiceError(Exception):
    def __init__(self, code: str, message: str, details: dict | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}


@dataclass
class StripeSubscriptionUpgradeResult:
    checkout_url: str | None
    invoice_status: str | None
    amount_due_cents: int
    currency: str | None


class StripeCustomerPortalService:
    _PLAN_RANK = {"free": 0, "basic": 1, "premium": 2}

    @staticmethod
    def _resolve_target_price_id(plan: str) -> str | None:
        if plan == "basic":
            return settings.stripe_price_basic
        if plan == "premium":
            return settings.stripe_price_premium
        return None

    @staticmethod
    def _extract_subscription_items(subscription: object) -> list[object]:
        items = getattr(subscription, "items", None)
        if items is not None:
            data = getattr(items, "data", None)
            if data:
                return list(data)

        if isinstance(subscription, dict):
            data = subscription.get("items", {}).get("data", [])
            if isinstance(data, list):
                return data

        to_dict_recursive = getattr(subscription, "to_dict_recursive", None)
        if callable(to_dict_recursive):
            serialized = to_dict_recursive()
            if isinstance(serialized, dict):
                data = serialized.get("items", {}).get("data", [])
                if isinstance(data, list):
                    return data

        return []

    @staticmethod
    def _extract_subscription_item_price_id(subscription_item: object) -> str | None:
        if isinstance(subscription_item, dict):
            price = subscription_item.get("price")
            if isinstance(price, dict):
                return price.get("id")
            return None

        price = getattr(subscription_item, "price", None)
        if price is None:
            return None
        return getattr(price, "id", None)

    @staticmethod
    def _resolve_current_subscription_item(
        profile: StripeBillingProfileModel,
        subscription_items: list[object],
    ) -> object:
        if not subscription_items:
            raise StripeCustomerPortalServiceError(
                code="stripe_subscription_not_found",
                message="No active Stripe subscription item found for this user",
            )

        expected_price_ids = [
            price_id
            for price_id in (
                profile.stripe_price_id,
                StripeCustomerPortalService._resolve_target_price_id(
                    profile.entitlement_plan or "free"
                ),
            )
            if price_id
        ]

        for expected_price_id in expected_price_ids:
            for item in subscription_items:
                if (
                    StripeCustomerPortalService._extract_subscription_item_price_id(item)
                    == expected_price_id
                ):
                    return item

        if len(subscription_items) == 1:
            return subscription_items[0]

        for item in subscription_items:
            if StripeCustomerPortalService._extract_subscription_item_price_id(item):
                return item

        raise StripeCustomerPortalServiceError(
            code="stripe_subscription_not_found",
            message="No active Stripe subscription item found for this user",
        )

    @staticmethod
    def _serialize_stripe_object(stripe_object: object) -> dict:
        if isinstance(stripe_object, dict):
            return stripe_object
        to_dict_recursive = getattr(stripe_object, "to_dict_recursive", None)
        if callable(to_dict_recursive):
            serialized = to_dict_recursive()
            if isinstance(serialized, dict):
                return serialized
        return {}

    @staticmethod
    def _extract_invoice_lines(invoice: object) -> list[dict]:
        serialized_invoice = StripeCustomerPortalService._serialize_stripe_object(invoice)
        lines = serialized_invoice.get("lines", {})
        if isinstance(lines, dict):
            data = lines.get("data", [])
            if isinstance(data, list):
                return [line for line in data if isinstance(line, dict)]
        return []

    @staticmethod
    def _extract_invoice_amount_due(invoice: object) -> int:
        serialized_invoice = StripeCustomerPortalService._serialize_stripe_object(invoice)
        return int(
            serialized_invoice.get("amount_due", 0)
            or serialized_invoice.get("total", 0)
            or 0
        )

    @staticmethod
    def _extract_invoice_currency(invoice: object) -> str | None:
        serialized_invoice = StripeCustomerPortalService._serialize_stripe_object(invoice)
        currency = serialized_invoice.get("currency")
        return currency if isinstance(currency, str) else None

    @staticmethod
    def _extract_proration_delta_amount(invoice: object) -> int:
        total = 0
        for line in StripeCustomerPortalService._extract_invoice_lines(invoice):
            if not bool(line.get("proration")):
                continue
            total += int(line.get("amount", 0) or 0)
        return total

    @staticmethod
    def _validate_upgrade_proration_preview(
        preview_invoice: object,
        *,
        current_price_id: str | None,
        target_price_id: str,
    ) -> tuple[int, str | None]:
        preview_lines = StripeCustomerPortalService._extract_invoice_lines(preview_invoice)
        has_credit_line = False
        has_target_debit_line = False

        for line in preview_lines:
            price = line.get("price")
            price_id = price.get("id") if isinstance(price, dict) else None
            amount = int(line.get("amount", 0) or 0)
            is_proration = bool(line.get("proration"))
            if not is_proration:
                continue
            if current_price_id and price_id == current_price_id and amount < 0:
                has_credit_line = True
            if price_id == target_price_id and amount > 0:
                has_target_debit_line = True

        if not has_credit_line or not has_target_debit_line:
            raise StripeCustomerPortalServiceError(
                code="stripe_subscription_upgrade_invalid_proration_preview",
                message="Stripe proration preview did not produce the expected upgrade delta",
                details={
                    "current_price_id": current_price_id,
                    "target_price_id": target_price_id,
                },
            )

        amount_due_cents = StripeCustomerPortalService._extract_proration_delta_amount(
            preview_invoice
        )
        if amount_due_cents <= 0:
            amount_due_cents = StripeCustomerPortalService._extract_invoice_amount_due(
                preview_invoice
            )
        currency = StripeCustomerPortalService._extract_invoice_currency(preview_invoice)
        return amount_due_cents, currency

    @staticmethod
    def _build_upgrade_checkout_metadata(
        *,
        user_id: int,
        subscription_id: str,
        subscription_item_id: str,
        target_plan: str,
        target_price_id: str,
        quantity: int,
        proration_date: int,
    ) -> dict[str, str]:
        return {
            "app_user_id": str(user_id),
            "billing_operation": "subscription_upgrade",
            "stripe_subscription_id": subscription_id,
            "stripe_subscription_item_id": subscription_item_id,
            "target_plan": target_plan,
            "target_price_id": target_price_id,
            "quantity": str(quantity),
            "proration_date": str(proration_date),
        }

    @staticmethod
    def _extract_checkout_session_value(session: object, field: str) -> str | None:
        if isinstance(session, dict):
            value = session.get(field)
            return value if isinstance(value, str) else None
        value = getattr(session, field, None)
        return value if isinstance(value, str) else None

    @staticmethod
    def _extract_checkout_session_metadata(session: object) -> dict[str, str]:
        if isinstance(session, dict):
            metadata = session.get("metadata")
            return metadata if isinstance(metadata, dict) else {}
        metadata = getattr(session, "metadata", None)
        return metadata if isinstance(metadata, dict) else {}

    @staticmethod
    def is_subscription_upgrade_checkout_session(session: object) -> bool:
        metadata = StripeCustomerPortalService._extract_checkout_session_metadata(session)
        return metadata.get("billing_operation") == "subscription_upgrade"

    @staticmethod
    def apply_paid_subscription_upgrade_checkout_session(
        db: Session,
        *,
        session: object,
    ) -> StripeBillingProfileModel:
        metadata = StripeCustomerPortalService._extract_checkout_session_metadata(session)
        user_id_raw = metadata.get("app_user_id")
        subscription_id = metadata.get("stripe_subscription_id")
        subscription_item_id = metadata.get("stripe_subscription_item_id")
        target_price_id = metadata.get("target_price_id")
        quantity_raw = metadata.get("quantity", "1")
        payment_status = StripeCustomerPortalService._extract_checkout_session_value(
            session,
            "payment_status",
        )
        customer_id = StripeCustomerPortalService._extract_checkout_session_value(
            session,
            "customer",
        )

        if payment_status != "paid":
            raise StripeCustomerPortalServiceError(
                code="stripe_subscription_upgrade_payment_not_completed",
                message="Stripe Checkout session is not fully paid yet",
            )

        if (
            not user_id_raw
            or not subscription_id
            or not subscription_item_id
            or not target_price_id
        ):
            raise StripeCustomerPortalServiceError(
                code="stripe_subscription_upgrade_checkout_metadata_missing",
                message="Stripe Checkout session metadata is incomplete for subscription upgrade",
            )

        user_id = int(user_id_raw)
        quantity = int(quantity_raw)
        profile = StripeCustomerPortalService._get_customer_subscription_profile(
            db,
            user_id=user_id,
        )
        if customer_id and profile.stripe_customer_id and customer_id != profile.stripe_customer_id:
            raise StripeCustomerPortalServiceError(
                code="stripe_subscription_upgrade_checkout_customer_mismatch",
                message="Stripe Checkout session customer does not match the billing profile",
            )

        client = get_stripe_client()
        if client is None:
            raise StripeCustomerPortalServiceError(
                code="stripe_unavailable",
                message="Stripe client is not configured",
            )

        if profile.stripe_price_id == target_price_id and profile.subscription_status == "active":
            return profile

        subscription = client.subscriptions.update(
            subscription_id,
            params={
                "items": [
                    {
                        "id": subscription_item_id,
                        "price": target_price_id,
                        "quantity": quantity,
                    }
                ],
                "billing_cycle_anchor": "unchanged",
                "proration_behavior": "none",
            },
        )
        updated_profile = StripeBillingProfileService.update_from_event_payload(
            db,
            user_id,
            {
                "id": f"manual_upgrade_checkout_{subscription_id}",
                "type": "customer.subscription.updated",
                "data": {"object": subscription.to_dict()},
            },
        )
        logger.info(
            (
                "Stripe subscription upgrade applied after Checkout payment "
                "for user=%s subscription=%s"
            ),
            user_id,
            subscription_id,
        )
        return updated_profile

    @staticmethod
    def _ensure_subscription_update_is_allowed(
        profile: StripeBillingProfileModel,
    ) -> None:
        if profile.subscription_status == "trialing":
            raise StripeCustomerPortalServiceError(
                code="stripe_portal_subscription_update_not_allowed_for_trial",
                message="Subscription updates are not allowed during the Stripe trial period",
            )

    @staticmethod
    def _ensure_subscription_cancel_is_allowed(
        profile: StripeBillingProfileModel,
    ) -> None:
        if profile.cancel_at_period_end:
            raise StripeCustomerPortalServiceError(
                code="stripe_portal_subscription_cancel_already_scheduled",
                message="Subscription is already set to cancel at period end",
            )

    @staticmethod
    def _ensure_subscription_reactivation_is_allowed(
        profile: StripeBillingProfileModel,
    ) -> None:
        if not profile.cancel_at_period_end:
            raise StripeCustomerPortalServiceError(
                code="stripe_subscription_reactivation_not_needed",
                message="Subscription is not scheduled for cancellation",
            )

    @staticmethod
    def _ensure_immediate_upgrade_is_allowed(
        profile: StripeBillingProfileModel,
        *,
        target_plan: str,
    ) -> str:
        StripeCustomerPortalService._ensure_subscription_update_is_allowed(profile)
        current_plan = profile.entitlement_plan or "free"
        current_rank = StripeCustomerPortalService._PLAN_RANK.get(current_plan, 0)
        target_rank = StripeCustomerPortalService._PLAN_RANK.get(target_plan, 0)
        if target_rank <= current_rank:
            raise StripeCustomerPortalServiceError(
                code="stripe_subscription_upgrade_not_allowed",
                message="Immediate upgrade is only allowed for paid plan upgrades",
            )
        price_id = StripeCustomerPortalService._resolve_target_price_id(target_plan)
        if not price_id:
            raise StripeCustomerPortalServiceError(
                code="plan_price_not_configured",
                message=f"Plan '{target_plan}' is not configured in Stripe mapping",
            )
        return price_id

    @staticmethod
    def _map_stripe_portal_error_code(error: stripe.StripeError, *, flow_type: str) -> str:
        if isinstance(error, stripe.InvalidRequestError):
            message = (str(error) or "").lower()
            if (
                flow_type == "subscription_update"
                and "subscription update feature" in message
                and "disabled" in message
            ):
                return "stripe_portal_subscription_update_disabled"
            if (
                flow_type == "subscription_update"
                and "no price in the portal configuration available to change to" in message
            ):
                return "stripe_portal_subscription_update_no_change_options"
            if (
                flow_type == "subscription_cancel"
                and "subscription cancel feature" in message
                and "disabled" in message
            ):
                return "stripe_portal_subscription_cancel_disabled"
            if (
                flow_type == "subscription_cancel"
                and "already set to be canceled at period end" in message
            ):
                return "stripe_portal_subscription_cancel_already_scheduled"
        return "stripe_api_error"

    @staticmethod
    def _get_customer_subscription_profile(
        db: Session,
        *,
        user_id: int,
    ) -> StripeBillingProfileModel:
        profile = StripeBillingProfileService.get_by_user_id(db, user_id)
        if profile is None or not profile.stripe_customer_id:
            raise StripeCustomerPortalServiceError(
                code="stripe_subscription_not_found",
                message="No Stripe customer found for this user",
            )
        if not profile.stripe_subscription_id:
            raise StripeCustomerPortalServiceError(
                code="stripe_subscription_not_found",
                message="No active Stripe subscription found for this user",
            )
        return profile

    @staticmethod
    def _create_subscription_flow_session(
        db: Session,
        *,
        user_id: int,
        return_url: str,
        flow_type: str,
        configuration_id: str | None = None,
    ) -> str:
        if not configuration_id:
            raise StripeCustomerPortalServiceError(
                code="stripe_portal_configuration_missing",
                message="Stripe Customer Portal configuration ID is missing",
            )

        profile = StripeCustomerPortalService._get_customer_subscription_profile(
            db,
            user_id=user_id,
        )
        if flow_type == "subscription_update":
            StripeCustomerPortalService._ensure_subscription_update_is_allowed(profile)
        if flow_type == "subscription_cancel":
            StripeCustomerPortalService._ensure_subscription_cancel_is_allowed(profile)

        client = get_stripe_client()
        if client is None:
            raise StripeCustomerPortalServiceError(
                code="stripe_unavailable",
                message="Stripe client is not configured",
            )

        try:
            flow_payload = {
                "subscription": profile.stripe_subscription_id,
            }
            params: dict[str, object] = {
                "customer": profile.stripe_customer_id,
                "return_url": return_url,
                "flow_data": {
                    "type": flow_type,
                    flow_type: flow_payload,
                    "after_completion": {
                        "type": "redirect",
                        "redirect": {"return_url": return_url},
                    },
                },
                "configuration": configuration_id,
            }

            session = client.billing_portal.sessions.create(params=params)
            logger.info(
                "Stripe portal %s session created for user=%s configuration=%s",
                flow_type,
                user_id,
                configuration_id,
            )
            return session.url
        except stripe.StripeError as error:
            logger.exception("Stripe API error during portal %s session creation", flow_type)
            raise StripeCustomerPortalServiceError(
                code=StripeCustomerPortalService._map_stripe_portal_error_code(
                    error, flow_type=flow_type
                ),
                message="Stripe API error",
                details={"error_message": str(error)},
            ) from error

    @staticmethod
    def create_portal_session(
        db: Session,
        *,
        user_id: int,
        return_url: str,
        configuration_id: str | None = None,
    ) -> str:
        """
        Crée une session Stripe Customer Portal pour un utilisateur.
        """
        if not configuration_id:
            raise StripeCustomerPortalServiceError(
                code="stripe_portal_configuration_missing",
                message="Stripe Customer Portal configuration ID is missing",
            )

        # Lecture seule — NE PAS utiliser get_or_create_profile ici
        profile = StripeBillingProfileService.get_by_user_id(db, user_id)
        if profile is None or not profile.stripe_customer_id:
            raise StripeCustomerPortalServiceError(
                code="stripe_billing_profile_not_found",
                message="No Stripe customer ID found for this user",
            )

        client = get_stripe_client()
        if client is None:
            raise StripeCustomerPortalServiceError(
                code="stripe_unavailable",
                message="Stripe client is not configured",
            )

        try:
            # Création de la session via le SDK Stripe
            session = client.billing_portal.sessions.create(
                params={
                    "customer": profile.stripe_customer_id,
                    "return_url": return_url,
                    "configuration": configuration_id,
                }
            )
            logger.info(
                "Stripe portal session created for user=%s configuration=%s",
                user_id,
                configuration_id,
            )
            return session.url
        except stripe.StripeError as error:
            logger.exception("Stripe API error during portal session creation")
            raise StripeCustomerPortalServiceError(
                code="stripe_api_error",
                message="Stripe API error",
                details={"error_message": str(error)},
            ) from error

    @staticmethod
    def create_subscription_update_session(
        db: Session,
        *,
        user_id: int,
        return_url: str,
        configuration_id: str | None = None,
    ) -> str:
        """Crée une session Stripe Customer Portal avec flow subscription_update."""
        return StripeCustomerPortalService._create_subscription_flow_session(
            db,
            user_id=user_id,
            return_url=return_url,
            flow_type="subscription_update",
            configuration_id=configuration_id,
        )

    @staticmethod
    def create_subscription_cancel_session(
        db: Session,
        *,
        user_id: int,
        return_url: str,
        configuration_id: str | None = None,
    ) -> str:
        """Crée une session Stripe Customer Portal avec flow subscription_cancel."""
        return StripeCustomerPortalService._create_subscription_flow_session(
            db,
            user_id=user_id,
            return_url=return_url,
            flow_type="subscription_cancel",
            configuration_id=configuration_id,
        )

    @staticmethod
    def reactivate_subscription(
        db: Session,
        *,
        user_id: int,
    ) -> StripeBillingProfileModel:
        profile = StripeCustomerPortalService._get_customer_subscription_profile(
            db,
            user_id=user_id,
        )
        StripeCustomerPortalService._ensure_subscription_reactivation_is_allowed(profile)

        client = get_stripe_client()
        if client is None:
            raise StripeCustomerPortalServiceError(
                code="stripe_unavailable",
                message="Stripe client is not configured",
            )

        try:
            subscription = client.subscriptions.update(
                profile.stripe_subscription_id,
                params={
                    "cancel_at_period_end": False,
                    "proration_behavior": "none",
                },
            )
            updated_profile = StripeBillingProfileService.update_from_event_payload(
                db,
                user_id,
                {
                    "id": f"manual_subscription_reactivation_{profile.stripe_subscription_id}",
                    "type": "customer.subscription.updated",
                    "data": {"object": subscription.to_dict()},
                },
            )
            logger.info(
                "Stripe subscription reactivated for user=%s subscription=%s",
                user_id,
                profile.stripe_subscription_id,
            )
            return updated_profile
        except stripe.StripeError as error:
            logger.exception("Stripe API error during subscription reactivation")
            raise StripeCustomerPortalServiceError(
                code="stripe_api_error",
                message="Stripe API error",
                details={"error_message": str(error)},
            ) from error

    @staticmethod
    def create_subscription_upgrade_payment(
        db: Session,
        *,
        user_id: int,
        target_plan: str,
    ) -> StripeSubscriptionUpgradeResult:
        profile = StripeCustomerPortalService._get_customer_subscription_profile(
            db,
            user_id=user_id,
        )
        target_price_id = StripeCustomerPortalService._ensure_immediate_upgrade_is_allowed(
            profile,
            target_plan=target_plan,
        )

        client = get_stripe_client()
        if client is None:
            raise StripeCustomerPortalServiceError(
                code="stripe_unavailable",
                message="Stripe client is not configured",
            )

        try:
            current_subscription = client.subscriptions.retrieve(
                profile.stripe_subscription_id
            )
            subscription_items = StripeCustomerPortalService._extract_subscription_items(
                current_subscription
            )
            current_item = StripeCustomerPortalService._resolve_current_subscription_item(
                profile,
                subscription_items,
            )
            current_item_id = (
                current_item.get("id")
                if isinstance(current_item, dict)
                else getattr(current_item, "id", None)
            )
            current_item_quantity = (
                current_item.get("quantity", 1)
                if isinstance(current_item, dict)
                else getattr(current_item, "quantity", None) or 1
            )
            if not current_item_id:
                raise StripeCustomerPortalServiceError(
                    code="stripe_subscription_not_found",
                    message="No active Stripe subscription item found for this user",
                )

            current_price_id = StripeCustomerPortalService._extract_subscription_item_price_id(
                current_item
            )
            proration_date = int(time.time())
            preview_invoice = client.invoices.create_preview(
                params={
                    "customer": profile.stripe_customer_id,
                    "subscription": profile.stripe_subscription_id,
                    "subscription_details": {
                        "items": [
                            {
                                "id": current_item_id,
                                "price": target_price_id,
                                "quantity": current_item_quantity,
                            }
                        ],
                        "proration_date": proration_date,
                    },
                }
            )
            amount_due_cents, currency = (
                StripeCustomerPortalService._validate_upgrade_proration_preview(
                    preview_invoice,
                    current_price_id=current_price_id,
                    target_price_id=target_price_id,
                )
            )

            if amount_due_cents <= 0:
                subscription = client.subscriptions.update(
                    profile.stripe_subscription_id,
                    params={
                        "items": [
                            {
                                "id": current_item_id,
                                "price": target_price_id,
                                "quantity": current_item_quantity,
                            }
                        ],
                        "billing_cycle_anchor": "unchanged",
                        "proration_behavior": "none",
                    },
                )
                StripeBillingProfileService.update_from_event_payload(
                    db,
                    user_id,
                    {
                        "id": f"manual_zero_amount_upgrade_{profile.stripe_subscription_id}",
                        "type": "customer.subscription.updated",
                        "data": {"object": subscription.to_dict()},
                    },
                )
                return StripeSubscriptionUpgradeResult(
                    checkout_url=None,
                    invoice_status="paid",
                    amount_due_cents=0,
                    currency=currency,
                )

            checkout_metadata = StripeCustomerPortalService._build_upgrade_checkout_metadata(
                user_id=user_id,
                subscription_id=profile.stripe_subscription_id,
                subscription_item_id=current_item_id,
                target_plan=target_plan,
                target_price_id=target_price_id,
                quantity=current_item_quantity,
                proration_date=proration_date,
            )
            checkout_session = client.checkout.sessions.create(
                params={
                    "mode": "payment",
                    "customer": profile.stripe_customer_id,
                    "success_url": settings.stripe_portal_return_url,
                    "cancel_url": settings.stripe_portal_return_url,
                    "client_reference_id": str(user_id),
                    "line_items": [
                        {
                            "price_data": {
                                "currency": currency or "eur",
                                "product_data": {
                                    "name": f"Upgrade vers {target_plan.title()}",
                                    "description": (
                                        "Paiement additionnel de prorata pour changement "
                                        "d'abonnement en cours de période"
                                    ),
                                },
                                "unit_amount": amount_due_cents,
                            },
                            "quantity": 1,
                        }
                    ],
                    "metadata": checkout_metadata,
                    "payment_intent_data": {
                        "metadata": checkout_metadata,
                    },
                },
            )

            logger.info(
                (
                    "Stripe upgrade Checkout session created for user=%s subscription=%s "
                    "target_plan=%s amount_due=%s"
                ),
                user_id,
                profile.stripe_subscription_id,
                target_plan,
                amount_due_cents,
            )
            return StripeSubscriptionUpgradeResult(
                checkout_url=checkout_session.url,
                invoice_status="requires_payment",
                amount_due_cents=amount_due_cents,
                currency=currency,
            )
        except StripeCustomerPortalServiceError:
            raise
        except stripe.StripeError as error:
            logger.exception("Stripe API error during subscription upgrade payment creation")
            raise StripeCustomerPortalServiceError(
                code="stripe_api_error",
                message="Stripe API error",
                details={"error_message": str(error)},
            ) from error
