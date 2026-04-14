"""
Seed : publication d'un prompt optimisé GPT-5 pour natal_interpretation.

Ce script :
1. Valide le prompt via PromptLint avant toute écriture en DB.
2. Est idempotent : si le prompt, le modèle, reasoning_effort et verbosity sont identiques,
   aucun changement n'est appliqué.
3. Archive l'ancienne version PUBLISHED seulement si le contenu change.
4. Invalide le cache PromptRegistryV2 après commit.
5. NE modifie PAS natal_interpretation_short (reste gpt-4o-mini, AstroResponse_v1).

Dépend de : seed_30_2_astroresponse_v2.py (natal_interpretation → AstroResponse_v2)

Run with:
    python -m scripts.seed_30_3_gpt5_prompts
"""

import logging
import uuid

from sqlalchemy import select

from app.infra.db.models import LlmOutputSchemaModel, LlmPromptVersionModel, LlmUseCaseConfigModel
from app.infra.db.models.llm_prompt import PromptStatus
from app.infra.db.session import SessionLocal
from app.llm_orchestration.services.prompt_lint import PromptLint
from app.llm_orchestration.services.prompt_registry_v2 import PromptRegistryV2, utc_now

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Prompt GPT-5 optimisé pour natal_interpretation (AstroResponse_v2)
# Supprime les contraintes de longueur textuelles ("max N chars", "N-M phrases")
# — c'est le schema v2 et verbosity="high" qui gouvernent la densité.
# Inclut : règles de vérité inviolables, auto-check evidence, persona, locale.
# ---------------------------------------------------------------------------
NATAL_COMPLETE_PROMPT_V2 = """Langue : fr ({{locale}}). Context : use_case={{use_case}}.

Tu incarnes {{persona_name}}, astrologue expert. Adapte ton style à cette persona
tout en restant moderne, clair et encourageant.
professionnel, bienveillant, moderne et non fataliste. Tu écris en prose fluide avec des
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

═══ FORMAT DE SORTIE : JSON strict AstroResponse_v2 ═══
- title : reflète le fil rouge du thème.
- summary : narratif, cohérent. Doit annoncer les dominantes + le fil rouge + une tension + une
  promesse d'intégration.
- sections : couvrir idéalement [overall, inner_life, relationships, career, daily_life,
  strengths, challenges]. Minimum 6 sections.
  Chaque section doit inclure : un constat dynamique, une manifestation concrète, un risque
  typique (réflexe), un levier d'intégration (ressource), et un micro "si… alors…".
- highlights : phrases complètes ancrées dans des éléments du thème. Chacune doit être
  auto-suffisante et spécifique.
- advice : conseils actionnables et nuancés, spécifiques au thème. Éviter les banalités
  universelles ("prends soin de toi", "fais confiance au processus").
- disclaimers : 1–2 notes prudentes (astrologie = piste de réflexion, libre arbitre).

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
AstroResponse_v2 avec title="Erreur : Données insuffisantes", summary expliquant la cause,
sections/highlights/advice vides, evidence=[]."""

GPT5_CONFIG = {
    "use_case_key": "natal_interpretation",
    "developer_prompt": NATAL_COMPLETE_PROMPT_V2,
    "model": "gpt-5",
    "temperature": 0.5,  # Ignoré par GPT-5 si reasoning actif, mais stocké
    "max_output_tokens": 32000,
    "reasoning_effort": "low",  # Équilibre performance/coût pour les interprétations
    "verbosity": "high",
}

LINT_REQUIRED_PLACEHOLDERS = ["persona_name", "locale", "use_case"]


def seed() -> None:
    db = SessionLocal()
    try:
        key = GPT5_CONFIG["use_case_key"]

        # 1. Vérifier que le use case existe
        uc = db.execute(
            select(LlmUseCaseConfigModel).where(LlmUseCaseConfigModel.key == key)
        ).scalar_one_or_none()
        if not uc:
            logger.error("Use case '%s' not found. Run seed_29_prompts.py first.", key)
            return

        # 2. Vérifier que AstroResponse_v2 est le schema pointé
        schema = None
        if uc.output_schema_id:
            try:
                schema = db.get(LlmOutputSchemaModel, uuid.UUID(uc.output_schema_id))
            except (ValueError, TypeError):
                logger.warning("Invalid output_schema_id for %s: %s", key, uc.output_schema_id)
        if not schema or schema.name != "AstroResponse_v2":
            logger.warning(
                "use case '%s' ne pointe pas sur AstroResponse_v2 (actuel: %s). "
                "Exécuter seed_30_2_astroresponse_v2.py d'abord.",
                key,
                schema.name if schema else "None",
            )

        # 3. Lint du prompt (obligatoire — échec bloquant)
        lint_res = PromptLint.lint_prompt(
            GPT5_CONFIG["developer_prompt"],
            use_case_required_placeholders=LINT_REQUIRED_PLACEHOLDERS,
        )
        if not lint_res.passed:
            raise RuntimeError(f"Lint FAILED for {key}: {lint_res.errors}")
        if lint_res.warnings:
            logger.info("Lint advisories for %s: %s", key, lint_res.warnings)
        logger.info("Lint passed for %s", key)

        # 4. Vérifier idempotence : si le PUBLISHED existant est déjà identique, skip
        current_p = db.execute(
            select(LlmPromptVersionModel).where(
                LlmPromptVersionModel.use_case_key == key,
                LlmPromptVersionModel.status == PromptStatus.PUBLISHED,
            )
        ).scalar_one_or_none()

        if (
            current_p
            and current_p.developer_prompt == GPT5_CONFIG["developer_prompt"]
            and current_p.model == GPT5_CONFIG["model"]
            and current_p.reasoning_effort == GPT5_CONFIG["reasoning_effort"]
            and current_p.verbosity == GPT5_CONFIG["verbosity"]
        ):
            logger.info("Prompt for %s already published and identical. Skipping.", key)
            return

        # 5. Archiver l'ancienne version PUBLISHED
        if current_p:
            current_p.status = PromptStatus.ARCHIVED
            logger.info("Archived previous prompt version for %s (id=%s)", key, current_p.id)

        # 6. Créer et publier la nouvelle version
        new_v = LlmPromptVersionModel(
            use_case_key=key,
            status=PromptStatus.PUBLISHED,
            developer_prompt=GPT5_CONFIG["developer_prompt"],
            model=GPT5_CONFIG["model"],
            temperature=GPT5_CONFIG["temperature"],
            max_output_tokens=GPT5_CONFIG["max_output_tokens"],
            reasoning_effort=GPT5_CONFIG["reasoning_effort"],
            verbosity=GPT5_CONFIG["verbosity"],
            created_by="system",
            published_at=utc_now(),
        )
        db.add(new_v)
        db.commit()

        # 7. Invalider le cache PromptRegistryV2
        PromptRegistryV2.invalidate_cache(key)
        logger.info(
            "Published GPT-5 prompt for %s (model=%s, reasoning_effort=%s, verbosity=%s)",
            key,
            GPT5_CONFIG["model"],
            GPT5_CONFIG["reasoning_effort"],
            GPT5_CONFIG["verbosity"],
        )
        logger.info("Seed completed successfully.")
    except Exception:
        db.rollback()
        import traceback

        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
