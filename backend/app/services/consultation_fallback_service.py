from typing import Dict, Literal, Optional
from app.api.v1.schemas.consultation import (
    SafeguardIssue, 
    ConsultationPrecheckData, 
    ConsultationStatus, 
    PrecisionLevel, 
    FallbackMode
)

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

    @staticmethod
    def resolve_route_key(data: ConsultationPrecheckData) -> Optional[str]:
        if data.status == ConsultationStatus.blocked:
            return None
            
        t = data.consultation_type
        p = data.precision_level
        f = data.fallback_mode
        
        if t in ["period", "work", "orientation"]:
            if p == PrecisionLevel.high:
                return f"{t}_full"
            else:
                return f"{t}_no_birth_time"
                
        if t == "relation":
            if f == FallbackMode.other_no_birth_time:
                return "relation_full_other_no_time"
            if f == FallbackMode.relation_user_only:
                return "relation_user_only"
            if p == PrecisionLevel.high:
                return "relation_full_full"
            return "relation_user_only" # Default fallback
            
        if t == "timing":
            if p == PrecisionLevel.high:
                return "timing_full"
            return "timing_degraded"
            
        return None
