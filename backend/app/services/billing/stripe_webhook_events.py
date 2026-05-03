# Registre canonique unique pour garder runtime, scripts et documentation alignés.
"""Registre canonique des événements webhook Stripe supportés."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

UserResolution = Literal[
    "checkout_client_reference",
    "customer_lookup",
    "customer_object_id_lookup",
]
HandlerGroup = Literal["checkout_upgrade", "billing_profile_update"]


@dataclass(frozen=True, slots=True)
class StripeWebhookEventDefinition:
    """Décrit un événement Stripe supporté et ses routes internes."""

    event_type: str
    user_resolution: UserResolution
    handler_group: HandlerGroup
    local_listener: bool
    documentation_note: str | None = None


SUPPORTED_WEBHOOK_EVENTS: tuple[StripeWebhookEventDefinition, ...] = (
    StripeWebhookEventDefinition(
        event_type="checkout.session.completed",
        user_resolution="checkout_client_reference",
        handler_group="checkout_upgrade",
        local_listener=True,
        documentation_note="Point d'entrée checkout principal.",
    ),
    StripeWebhookEventDefinition(
        event_type="checkout.session.async_payment_succeeded",
        user_resolution="customer_lookup",
        handler_group="checkout_upgrade",
        local_listener=True,
        documentation_note="Checkout asynchrone accepté explicitement.",
    ),
    StripeWebhookEventDefinition(
        event_type="customer.subscription.created",
        user_resolution="customer_lookup",
        handler_group="billing_profile_update",
        local_listener=True,
    ),
    StripeWebhookEventDefinition(
        event_type="customer.subscription.updated",
        user_resolution="customer_lookup",
        handler_group="billing_profile_update",
        local_listener=True,
    ),
    StripeWebhookEventDefinition(
        event_type="customer.subscription.deleted",
        user_resolution="customer_lookup",
        handler_group="billing_profile_update",
        local_listener=True,
    ),
    StripeWebhookEventDefinition(
        event_type="customer.subscription.paused",
        user_resolution="customer_lookup",
        handler_group="billing_profile_update",
        local_listener=True,
    ),
    StripeWebhookEventDefinition(
        event_type="customer.subscription.resumed",
        user_resolution="customer_lookup",
        handler_group="billing_profile_update",
        local_listener=True,
    ),
    StripeWebhookEventDefinition(
        event_type="customer.subscription.trial_will_end",
        user_resolution="customer_lookup",
        handler_group="billing_profile_update",
        local_listener=True,
    ),
    StripeWebhookEventDefinition(
        event_type="subscription_schedule.created",
        user_resolution="customer_lookup",
        handler_group="billing_profile_update",
        local_listener=True,
        documentation_note="Périmètre schedule supporté par le service de profil billing.",
    ),
    StripeWebhookEventDefinition(
        event_type="subscription_schedule.updated",
        user_resolution="customer_lookup",
        handler_group="billing_profile_update",
        local_listener=True,
        documentation_note="Périmètre schedule supporté par le service de profil billing.",
    ),
    StripeWebhookEventDefinition(
        event_type="subscription_schedule.canceled",
        user_resolution="customer_lookup",
        handler_group="billing_profile_update",
        local_listener=True,
        documentation_note="Périmètre schedule supporté par le service de profil billing.",
    ),
    StripeWebhookEventDefinition(
        event_type="subscription_schedule.completed",
        user_resolution="customer_lookup",
        handler_group="billing_profile_update",
        local_listener=True,
        documentation_note="Périmètre schedule supporté par le service de profil billing.",
    ),
    StripeWebhookEventDefinition(
        event_type="customer.updated",
        user_resolution="customer_object_id_lookup",
        handler_group="billing_profile_update",
        local_listener=True,
    ),
    StripeWebhookEventDefinition(
        event_type="invoice.paid",
        user_resolution="customer_lookup",
        handler_group="billing_profile_update",
        local_listener=True,
    ),
    StripeWebhookEventDefinition(
        event_type="invoice.payment_failed",
        user_resolution="customer_lookup",
        handler_group="billing_profile_update",
        local_listener=True,
    ),
    StripeWebhookEventDefinition(
        event_type="invoice.payment_action_required",
        user_resolution="customer_lookup",
        handler_group="billing_profile_update",
        local_listener=True,
    ),
)

SUPPORTED_WEBHOOK_EVENT_TYPES = tuple(event.event_type for event in SUPPORTED_WEBHOOK_EVENTS)
LOCAL_LISTENER_EVENT_TYPES = tuple(
    event.event_type for event in SUPPORTED_WEBHOOK_EVENTS if event.local_listener
)
CHECKOUT_UPGRADE_EVENT_TYPES = tuple(
    event.event_type
    for event in SUPPORTED_WEBHOOK_EVENTS
    if event.handler_group == "checkout_upgrade"
)
CHECKOUT_CLIENT_REFERENCE_EVENT_TYPES = tuple(
    event.event_type
    for event in SUPPORTED_WEBHOOK_EVENTS
    if event.user_resolution == "checkout_client_reference"
)
CUSTOMER_LOOKUP_EVENT_TYPES = tuple(
    event.event_type
    for event in SUPPORTED_WEBHOOK_EVENTS
    if event.user_resolution == "customer_lookup"
)
CUSTOMER_OBJECT_ID_LOOKUP_EVENT_TYPES = tuple(
    event.event_type
    for event in SUPPORTED_WEBHOOK_EVENTS
    if event.user_resolution == "customer_object_id_lookup"
)


def is_supported_webhook_event(event_type: str) -> bool:
    """Indique si un type d'événement Stripe est supporté par le backend billing."""
    return event_type in SUPPORTED_WEBHOOK_EVENT_TYPES
