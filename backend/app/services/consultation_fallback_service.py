from typing import Dict, Literal
from app.api.v1.schemas.consultation import SafeguardIssue

SafeguardResolution = Literal["fallback", "refusal", "reframing"]

SAFEGUARD_MATRIX: Dict[SafeguardIssue, SafeguardResolution] = {
    SafeguardIssue.health: "refusal",
    SafeguardIssue.emotional_distress: "reframing",
    SafeguardIssue.obsessive_relation: "reframing",
    SafeguardIssue.pregnancy: "refusal",
    SafeguardIssue.death: "refusal",
    SafeguardIssue.legal_finance: "reframing",
    SafeguardIssue.third_party_manipulation: "refusal",
}

class ConsultationFallbackService:
    @staticmethod
    def resolve_safeguard(issue: SafeguardIssue) -> SafeguardResolution:
        return SAFEGUARD_MATRIX.get(issue, "refusal")
