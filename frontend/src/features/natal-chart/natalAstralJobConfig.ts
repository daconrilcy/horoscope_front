// Configuration temporaire du job Astral natal, en attendant une normalisation backend.
import {
  type AstralJobRequest,
  type AstralPlan,
  buildAstralClientRequestId,
} from "../../api/astral"

// Compatibilité avec le catalogue d'entitlements existant.
// Le code "horoscope_daily" couvre actuellement aussi l'accès au thème natal.
// Ne pas renommer sans décision produit et migration backend.
export const NATAL_ENTITLEMENT_FEATURE_CODE = "horoscope_daily"

/** Dérive le plan Astral natal depuis la variante d'entitlement actuelle. */
export function resolveNatalAstralPlan(variantCode?: string | null): AstralPlan {
  if (variantCode?.includes("premium")) return "premium"
  if (variantCode?.includes("basic") || variantCode === "single_astrologer") return "basic"
  return "free"
}

type BuildNatalAstralJobRequestParams = {
  plan: AstralPlan
}

/** Construit le payload inchangé attendu par la façade backend Astral. */
export function buildNatalAstralJobRequest({
  plan,
}: BuildNatalAstralJobRequestParams): AstralJobRequest {
  return {
    product: "natal_full",
    plan,
    client_request_id: buildAstralClientRequestId("natal"),
    // Dette produit : la page connaît déjà `lang`, mais le job Astral est encore forcé en français.
    // Ne pas remplacer par `lang` sans vérifier les langues réellement supportées par le backend Astral.
    target_language_code: "fr",
    audience_level: plan === "premium" ? "expert" : "beginner",
  }
}
