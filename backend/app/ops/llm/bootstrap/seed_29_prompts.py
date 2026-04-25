"""
Seed des prompts nataux (Chapter 29) pour le LLMGateway.
Optimise selon les recommandations GPT-5.2 pour une concision et une structure maximale.
"""

from __future__ import annotations

import logging

from sqlalchemy import select

from app.infra.db.models.llm.llm_output_schema import LlmOutputSchemaModel
from app.infra.db.models.llm.llm_prompt import (
    LlmPromptVersionModel,
    LlmUseCaseConfigModel,
    PromptStatus,
)
from app.infra.db.session import SessionLocal
from app.ops.llm.services import PromptLint, PromptRegistryV2, utc_now

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

NATAL_SHORT_PROMPT = """Langue de réponse : français ({{locale}}). Contexte : use_case={{use_case}}.

En tant qu’astrologue expérimenté, ton interprétation du thème natal fourni doit être claire, moderne et non fataliste.
Évite les phrases courtes et hachées. Privilégie un style fluide, bien écrit, avec des transitions naturelles entre les idées pour créer un portrait cohérent.

Focalise-toi STRICTEMENT sur les données du thème natal fournies dans le message utilisateur.
Données techniques (JSON du thème natal) :
{{chart_json}}

Règles impératives :
- N’invente aucun placement planétaire, aspect ou maison non présent dans les données.
- Parle exclusivement de tendances et potentiels, jamais de certitudes.
- Aucun diagnostic médical, légal ou financier définitif.
- Si incertitude ou donnée manquante, reste général.

Format de sortie : JSON strict AstroResponse_v1
- title : titre accrocheur, 5–10 mots.
- summary : portrait synthétique et fluide du profil natal, 4–6 phrases liées.
- sections : au moins 3 parmi [overall, career, relationships, inner_life, daily_life]
  - heading : titre de section percutant.
  - content : 3–5 phrases formant un paragraphe bien construit et actionnable.
- highlights : 3–5 points forts ou traits marquants.
- advice : 3–5 conseils pratiques et positifs.
- evidence : liste des identifiants UPPER_SNAKE_CASE réellement utilisés.
- disclaimers : 1 note de prudence générale (astrologie = piste de réflexion).

⚠️ IMPORTANT : Ne numérote JAMAIS les points dans les listes (highlights, advice, sections). Pas de "1.", "2." ni de tirets "-" ou puces dans les chaînes de texte. Le formatage est géré par l’application.

⚠️ Langage naturel (IMPÉRATIF) :
- Dans TOUT le texte (title, summary, sections/content, highlights, advice) : emploie UNIQUEMENT les noms naturels en français (Soleil, Lune, Vénus, Taureau, Maison 10, Milieu du Ciel, Ascendant, trigone, carré, opposition, conjonction…).
- Les codes UPPER_SNAKE_CASE (SUN, TAURUS, MAISON_10, MARS_TRINE_SATURN…) sont STRICTEMENT réservés au champ `evidence`. Ne les écris JAMAIS dans le texte.

Contraintes supplémentaires :
- Si une section ou un champ obligatoire ne peut pas être renseigné faute de données, utilise une chaîne ou un tableau vide.
- Si un champ clé d’entrée manque (ex: planets absent), retourne un message d’erreur au même format avec title="Erreur : Données insuffisantes" et résume la cause dans summary.
- Pour le champ evidence, inclure uniquement les identifiants explicitement mobilisés dans l’interprétation."""  # noqa: E501

NATAL_COMPLETE_PROMPT = """Langue de réponse : français ({{locale}}). Contexte : use_case={{use_case}}.

Tu incarnes {{persona_name}}, astrologue expert. Adapte ton style et ton ton à cette persona tout en restant professionnel, bienveillant, moderne et non fataliste.
Tu écris de façon riche et fluide, avec des transitions naturelles. Interdiction d’écrire une suite de petites phrases ou un catalogue de placements.

Données (source unique) :
Données techniques (JSON du thème natal) :
{{chart_json}}

Règles impératives de vérité :
- Base-toi UNIQUEMENT sur les données fournies. N’invente aucun placement, aspect, maison, dominance, maître, dignité, rétrogradation, nœud, astéroïde ou point qui n’apparaît pas explicitement dans les données techniques.
- Si une information nécessaire à une analyse (ex : maisons/ascendant, aspects, heure) n’est pas présente, dis-le clairement et adapte l’analyse (plus général, sans combler le vide).
- Tu parles de tendances, potentiels et dynamiques, jamais de certitudes ni de prédictions datées.
- Aucun diagnostic médical, légal, financier, ni psychologique ferme.

Exigence "premium" (différenciation) :
- Ta lecture doit être HIÉRARCHISÉE : commence par identifier les 3 dominantes du thème (ex : éléments/modèles répétitifs/angles/maisons/stelliums/planètes dominantes) uniquement si ces éléments sont calculables à partir des données présentes. Ensuite, fais vivre ces dominantes dans toutes les sections.
- Ta lecture doit être INTÉGRATIVE : montre au moins une tension interne (besoin vs impulsion, sécurité vs expansion, contrôle vs spontanéité…) et propose une manière concrète de l’intégrer.
- Ta lecture doit être CONCRÈTE : pour chaque grande idée, donne une manifestation observable dans la vie réelle (comportement, réflexe, type de situation) et un levier d’ajustement ("si… alors…"), sans moraliser.
- Anti-générique : évite les phrases vagues. Chaque section doit relier au moins 2 éléments du thème entre eux (ex : planète + signe, planète + maison, aspect + axe) si ces données existent. Sinon, reste plus général et assume la limite.

Evidence / traçabilité :
- "evidence" doit contenir UNIQUEMENT des identifiants UPPER_SNAKE_CASE effectivement présents dans les données et réellement mobilisés dans l’interprétation.
- Chaque élément astrologique mentionné (placements, maisons, aspects, angles, maîtres) dans title/summary/sections/highlights/advice doit correspondre à un identifiant listé dans evidence.
- Si les données ne fournissent aucun identifiant exploitable, retourne evidence=[].

Format de sortie : JSON strict AstroResponse_v1
- title : 5–12 mots, reflète le fil rouge.
- summary : 10–18 phrases, narratif, cohérent, max 2000 chars. Doit annoncer les dominantes + le fil rouge + une tension principale + une promesse d’intégration.
- sections : produire idéalement 7 sections couvrant [overall, inner_life, relationships, career, daily_life, strengths, challenges] (au minimum 6).
  - heading : évocateur, max 80 chars.
  - content : 7–12 phrases, max 4000 chars, structuré en paragraphe fluide. Doit inclure :
    - un constat (dynamique)
    - une manifestation concrète (exemples de situations)
    - un risque typique (version réflexe)
    - un levier d’intégration (version ressource)
    - un micro "si… alors…" pratico-pratique
- highlights : 6–10 phrases complètes, chacune ancrée dans le thème, sans numérotation, sans tirets.
- advice : 6–10 conseils actionnables, spécifiques au thème, nuancés (éviter les banalités), sans numérotation, sans tirets.
- disclaimers : 1–2 notes prudentes (astrologie = piste de réflexion, libre arbitre).

⚠️ Formatage :
- Ne numérote JAMAIS. Pas de "1.", pas de "2.", pas de tirets "-" ni puces dans les chaînes. Le rendu est géré par l’application.

⚠️ Langage naturel (IMPÉRATIF) :
- Dans TOUT le texte (title, summary, sections/content, highlights, advice) : emploie UNIQUEMENT les noms naturels en français (Soleil, Lune, Vénus, Taureau, Maison 10, Milieu du Ciel, Ascendant, trigone, carré, opposition, conjonction, rétrograde…).
- Les codes UPPER_SNAKE_CASE (SUN, TAURUS, MAISON_10, MARS_TRINE_SATURN…) sont STRICTEMENT réservés au champ `evidence`. Ne les écris JAMAIS dans le texte libre.

Contrainte de non-redondance :
- Ne répète pas les mêmes formulations entre summary et sections. Chaque section doit apporter un angle nouveau, une profondeur différente ou un domaine de vie distinct.

Gestion des erreurs :
- Si l’entrée est malformée ou trop incomplète pour produire une interprétation (ex : planets absent), retourne un JSON AstroResponse_v1 avec title="Erreur : Données insuffisantes" et summary expliquant la cause. sections/highlights/advice vides, evidence=[]."""  # noqa: E501

PROMPTS_TO_SEED = [
    {
        "use_case_key": "natal_interpretation_short",
        "display_name": "Interprétation Natale (Courte)",
        "description": "Analyse rapide du thème de naissance.",
        "persona_strategy": "optional",
        "required_prompt_placeholders": ["chart_json", "locale", "use_case"],
        "developer_prompt": NATAL_SHORT_PROMPT,
        "model": "gpt-4o-mini",
        "temperature": 0.7,
        "max_output_tokens": 4000,
        "eval_fixtures_path": "backend/app/tests/eval_fixtures/natal_interpretation_short",
        "eval_failure_threshold": 0.10,
    },
    {
        "use_case_key": "natal_interpretation",
        "display_name": "Interprétation Natale (Complète)",
        "description": "Analyse approfondie du thème de naissance avec persona.",
        "persona_strategy": "required",
        "required_prompt_placeholders": ["chart_json", "persona_name", "locale", "use_case"],
        "developer_prompt": NATAL_COMPLETE_PROMPT,
        "model": "gpt-4o-mini",
        "temperature": 0.55,
        "max_output_tokens": 16000,
        "eval_fixtures_path": "backend/app/tests/eval_fixtures/natal_interpretation",
        "eval_failure_threshold": 0.20,
    },
]


def seed_prompts() -> None:
    """Seeds the database with natal interpretation prompts."""
    db = SessionLocal()
    keys_to_invalidate = set()
    try:
        stmt_schema = select(LlmOutputSchemaModel).where(
            LlmOutputSchemaModel.name == "AstroResponse_v1"
        )
        astro_schema = db.execute(stmt_schema).scalar_one_or_none()
        if not astro_schema:
            logger.error("AstroResponse_v1 schema not found. Run seed_28_4.py first.")
            return

        for config in PROMPTS_TO_SEED:
            key = config["use_case_key"]

            stmt_uc = select(LlmUseCaseConfigModel).where(LlmUseCaseConfigModel.key == key)
            uc = db.execute(stmt_uc).scalar_one_or_none()

            if not uc:
                logger.info("Creating use case config for %s...", key)
                uc = LlmUseCaseConfigModel(
                    key=key,
                    display_name=config["display_name"],
                    description=config["description"],
                    required_prompt_placeholders=config["required_prompt_placeholders"],
                    eval_fixtures_path=config["eval_fixtures_path"],
                    eval_failure_threshold=config["eval_failure_threshold"],
                )
                db.add(uc)
            else:
                logger.info("Updating use case config for %s...", key)
                uc.display_name = config["display_name"]
                uc.description = config["description"]
                uc.required_prompt_placeholders = config["required_prompt_placeholders"]
                uc.eval_fixtures_path = config["eval_fixtures_path"]
                uc.eval_failure_threshold = config["eval_failure_threshold"]

            db.flush()

            lint_res = PromptLint.lint_prompt(
                config["developer_prompt"],
                use_case_required_placeholders=config["required_prompt_placeholders"],
            )
            if not lint_res.passed:
                raise RuntimeError(f"Lint FAILED for {key}: {lint_res.errors}")

            stmt_p = select(LlmPromptVersionModel).where(
                LlmPromptVersionModel.use_case_key == key,
                LlmPromptVersionModel.status == PromptStatus.PUBLISHED,
            )
            current_p = db.execute(stmt_p).scalar_one_or_none()

            if current_p and current_p.developer_prompt == config["developer_prompt"]:
                logger.info("Prompt for %s already published and identical. Skipping.", key)
                continue

            logger.info("Publishing new prompt version for %s...", key)
            if current_p:
                current_p.status = PromptStatus.ARCHIVED

            new_v = LlmPromptVersionModel(
                use_case_key=key,
                status=PromptStatus.PUBLISHED,
                developer_prompt=config["developer_prompt"],
                created_by="system",
                published_at=utc_now(),
            )
            db.add(new_v)
            db.flush()

            keys_to_invalidate.add(key)
            logger.info("Prompt for %s prepared for commit.", key)

        db.commit()

        for key in keys_to_invalidate:
            PromptRegistryV2.invalidate_cache(key)

        logger.info("Seed process completed successfully.")

    except Exception as exc:
        db.rollback()
        logger.exception("Seed failed: %s", exc)
    finally:
        db.close()


if __name__ == "__main__":
    seed_prompts()
