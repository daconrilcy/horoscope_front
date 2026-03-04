"""
Seed : prompt GPT-5 v3 pour natal_interpretation (Story 30-8).

Ce script :
1. Met à jour le prompt pour le contrat AstroResponse_v3 :
   - Supprime la génération de disclaimers (gérés côté application)
   - Ajoute les exigences de densité premium (≥5 sections, summary ≥900 chars,
     contenu ≥280 chars par section, ≥5 highlights, ≥5 advice)
   - Met à jour la référence format de v2 → v3
2. Est idempotent : si le contenu est identique, aucun changement n'est appliqué.
3. Archive l'ancienne version PUBLISHED.
4. Invalide le cache PromptRegistryV2 après commit.

Dépend de : seed_30_8_v3_schema.py (AstroResponse_v3 enregistré en DB)

Run with:
    python -m scripts.seed_30_8_v3_prompts
"""

import logging

from sqlalchemy import select

from app.infra.db.models import LlmPromptVersionModel, LlmUseCaseConfigModel
from app.infra.db.models.llm_prompt import PromptStatus
from app.infra.db.session import SessionLocal
from app.llm_orchestration.services.prompt_lint import PromptLint
from app.llm_orchestration.services.prompt_registry_v2 import PromptRegistryV2, utc_now

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Prompt GPT-5 v3 pour natal_interpretation
# Changements vs v2 :
#   - Suppression de la ligne "disclaimers" dans FORMAT DE SORTIE
#   - Référence format : AstroResponse_v3
#   - Exigences de densité premium explicites et mesurables
#   - Section erreur adaptée au mode erreur v3 (AstroErrorResponseV3)
# ---------------------------------------------------------------------------
NATAL_COMPLETE_PROMPT_V3 = """Langue : fr ({{locale}}). Context : use_case={{use_case}}.

Tu incarnes {{persona_name}}, astrologue expert. Ton style est professionnel,
bienveillant, moderne et non fataliste. Tu écris en prose fluide avec des
transitions naturelles entre les idées. Interdiction de lister des placements sans les relier.

Données (source unique et exclusive) :
Données techniques fournies dans le message utilisateur.

═══ RÈGLES DE VÉRITÉ (inviolables) ═══
- Base-toi UNIQUEMENT sur les données présentes dans le message utilisateur.
- N'invente aucun placement, aspect, maison, dominante, maître, dignité, rétrogradation, nœud,
  astéroïde ou point qui n'apparaît pas explicitement dans les données.
- Si une donnée nécessaire (ex : ascendant/maisons/heure) est absente, signale-le et adapte
  l'analyse (plus générale, sans combler le vide par de l'invention).
- Tu parles de tendances, potentiels et dynamiques, jamais de certitudes ni de prédictions datées.
- Aucun diagnostic médical, légal, financier ou psychologique.

═══ EXIGENCE PREMIUM ═══
- HIÉRARCHISÉ : identifie les 3 dominantes du thème (éléments récurrents, stelliums, angles,
  maisons chargées) et fais-les vivre dans toutes les sections.
- INTÉGRATIF : montre au moins une tension interne (deux besoins contradictoires) et une voie
  d'intégration concrète.
- CONCRET : pour chaque grande idée, donne une manifestation observable dans la vie réelle et un
  levier d'ajustement. Formule au moins un "si… alors…" pratico-pratique par section.
- ANTI-GÉNÉRIQUE : chaque section relie au moins 2 éléments du thème entre eux si les données
  le permettent. Pas de formules creuses qui s'appliqueraient à n'importe quel thème.

═══ EVIDENCE / TRAÇABILITÉ ═══
Avant de finaliser ta réponse, effectue ce contrôle en trois étapes :
1. Liste tous les éléments astrologiques que tu as mentionnés (planètes, signes, maisons, aspects,
   angles, maîtres, dignités, rétrogradations).
2. Pour chacun, vérifie qu'il est explicitement présent dans les données fournies.
3. Produis le champ "evidence" avec UNIQUEMENT les identifiants UPPER_SNAKE_CASE correspondant
   aux éléments réellement utilisés dans l'interprétation.
- Si les données ne fournissent aucun identifiant exploitable → evidence = []
- Ne cite dans le texte AUCUN élément qui ne figure pas dans evidence.
- TOUT IDENTIFIANT PRÉSENT DANS evidence DOIT ÊTRE JUSTIFIÉ dans le texte par une mention
  en langage naturel (ex: 'Soleil en Lion', 'trigone entre...', 'Maison 10', etc.).

═══ FORMAT DE SORTIE : JSON strict AstroResponse_v3 ═══
- title : reflète le fil rouge du thème.
- summary : narratif complet et substantiel (minimum 900 caractères). Doit annoncer les
  dominantes + le fil rouge + une tension + une promesse d'intégration. Pas de résumé bref.
- sections : MINIMUM 5 sections obligatoires. Couvrir idéalement [overall, inner_life,
  relationships, career, daily_life, strengths, challenges].
  Chaque section DOIT avoir un contenu de MINIMUM 280 caractères (environ 3-4 phrases denses).
  Chaque section doit inclure : un constat dynamique, une manifestation concrète, un risque
  typique (réflexe), un levier d'intégration (ressource), et un micro "si… alors…".
- highlights : MINIMUM 5 éléments. Phrases complètes ancrées dans des éléments du thème.
  Chacune doit être auto-suffisante et spécifique.
- advice : MINIMUM 5 éléments. Conseils actionnables et nuancés, spécifiques au thème.
  Éviter les banalités universelles ("prends soin de toi", "fais confiance au processus").
- evidence : identifiants UPPER_SNAKE_CASE uniquement. Pas de texte libre.
  NB: les disclaimers ne sont PAS dans la réponse — ils sont gérés par l'application.

⚠️ FORMATAGE (impératif) :
- Pas de numérotation ("1.", "2."...) dans les strings. Pas de tirets "-" ni puces dans les
  chaînes. Le rendu est géré par l'application.
- Dans TOUT le texte libre (title, summary, sections/content, highlights, advice) : emploie
  UNIQUEMENT les noms naturels en français (Soleil, Lune, Vénus, Taureau, Maison 10, Milieu
  du Ciel, Ascendant, trigone, carré, opposition, conjonction, rétrograde…).
- Les codes UPPER_SNAKE_CASE sont STRICTEMENT réservés au champ evidence.
- Pas de redondance entre summary et sections. Chaque section apporte un angle nouveau.

⚠️ GESTION D'ERREUR :
Si l'entrée est malformée ou trop incomplète (ex : planets absent) → retourne un JSON
avec error_code="insufficient_data", message expliquant la cause, title et summary courts,
sections/highlights/advice/evidence vides."""

GPT5_V3_CONFIG = {
    "use_case_key": "natal_interpretation",
    "developer_prompt": NATAL_COMPLETE_PROMPT_V3,
    "model": "gpt-5",
    "temperature": 0.5,
    "max_output_tokens": 32000,
    "reasoning_effort": "medium",
    "verbosity": "high",
}

LINT_REQUIRED_PLACEHOLDERS = ["persona_name", "locale", "use_case"]


def seed() -> None:
    db = SessionLocal()
    try:
        key = GPT5_V3_CONFIG["use_case_key"]

        # 1. Vérifier que le use case existe
        uc = db.execute(
            select(LlmUseCaseConfigModel).where(LlmUseCaseConfigModel.key == key)
        ).scalar_one_or_none()
        if not uc:
            logger.error("Use case '%s' not found. Run use_cases_seed first.", key)
            return

        # 2. Lint du prompt (obligatoire — échec bloquant)
        lint_res = PromptLint.lint_prompt(
            GPT5_V3_CONFIG["developer_prompt"],
            use_case_required_placeholders=LINT_REQUIRED_PLACEHOLDERS,
        )
        if not lint_res.passed:
            raise RuntimeError(f"Lint FAILED for {key}: {lint_res.errors}")
        if lint_res.warnings:
            logger.warning("Lint warnings for %s: %s", key, lint_res.warnings)
        logger.info("Lint passed for %s", key)

        # 3. Vérifier idempotence : si le PUBLISHED existant est déjà identique, skip
        published_versions = db.execute(
            select(LlmPromptVersionModel).where(
                LlmPromptVersionModel.use_case_key == key,
                LlmPromptVersionModel.status == PromptStatus.PUBLISHED,
            )
        ).scalars().all()

        if published_versions:
            # Check if any published version is already identical
            for p in published_versions:
                if (
                    p.developer_prompt == GPT5_V3_CONFIG["developer_prompt"]
                    and p.model == GPT5_V3_CONFIG["model"]
                    and p.reasoning_effort == GPT5_V3_CONFIG["reasoning_effort"]
                    and p.verbosity == GPT5_V3_CONFIG["verbosity"]
                ):
                    logger.info("Prompt v3 for %s already published and identical. Skipping.", key)
                    return

        # 4. Archiver TOUTES les anciennes versions PUBLISHED pour ce use case
        # (Indispensable si contrainte UNIQUE sur use_case_key + status)
        for p in published_versions:
            p.status = PromptStatus.ARCHIVED
            logger.info("Archived previous prompt version for %s (id=%s)", key, p.id)

        # 5. Créer et publier la nouvelle version v3
        new_v = LlmPromptVersionModel(
            use_case_key=key,
            status=PromptStatus.PUBLISHED,
            developer_prompt=GPT5_V3_CONFIG["developer_prompt"],
            model=GPT5_V3_CONFIG["model"],
            temperature=GPT5_V3_CONFIG["temperature"],
            max_output_tokens=GPT5_V3_CONFIG["max_output_tokens"],
            reasoning_effort=GPT5_V3_CONFIG["reasoning_effort"],
            verbosity=GPT5_V3_CONFIG["verbosity"],
            created_by="system",
            published_at=utc_now(),
        )
        db.add(new_v)
        db.commit()

        # 6. Invalider le cache PromptRegistryV2
        PromptRegistryV2.invalidate_cache(key)
        logger.info(
            "Published GPT-5 v3 prompt for %s (model=%s, reasoning_effort=%s, verbosity=%s)",
            key,
            GPT5_V3_CONFIG["model"],
            GPT5_V3_CONFIG["reasoning_effort"],
            GPT5_V3_CONFIG["verbosity"],
        )
        logger.info("Seed v3 completed successfully.")
    except Exception:
        db.rollback()
        import traceback

        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
