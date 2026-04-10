from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.llm_assembly import PromptAssemblyConfigModel
from app.infra.db.models.llm_execution_profile import LlmExecutionProfileModel
from app.infra.db.models.llm_prompt import (
    LlmPromptVersionModel,
    LlmUseCaseConfigModel,
    PromptStatus,
)
from app.infra.db.session import engine


def seed_66_20_convergence():
    with Session(engine) as db:
        print("Starting seed 66.20 convergence...")

        # 1. Ensure base profiles exist (standard, premium)
        # We reuse or create generic profiles that we will then "target" to specific features
        base_profiles = {
            "standard": {
                "name": "OpenAI Standard (gpt-4o-mini)",
                "model": "gpt-4o-mini",
                "verbosity": "balanced",
                "output_mode": "structured_json",
            },
            "premium": {
                "name": "OpenAI Premium (gpt-4o)",
                "model": "gpt-4o",
                "verbosity": "detailed",
                "output_mode": "structured_json",
            },
        }

        resolved_base_ids = {}
        for key, p_data in base_profiles.items():
            existing = db.execute(
                select(LlmExecutionProfileModel).where(
                    LlmExecutionProfileModel.name == p_data["name"],
                    LlmExecutionProfileModel.feature.is_(None),
                )
            ).scalar_one_or_none()

            if not existing:
                p = LlmExecutionProfileModel(
                    id=uuid.uuid4(),
                    name=p_data["name"],
                    provider="openai",
                    model=p_data["model"],
                    reasoning_profile="off",
                    verbosity_profile=p_data["verbosity"],
                    output_mode=p_data["output_mode"],
                    tool_mode="none",
                    timeout_seconds=60,
                    status=PromptStatus.PUBLISHED,
                    created_by="system_66_20",
                )
                db.add(p)
                db.flush()
                resolved_base_ids[key] = p.id
                print(f"Created base profile: {p_data['name']}")
            else:
                resolved_base_ids[key] = existing.id

        db.commit()

        # 2. Get or create use case configs and prompt versions
        def get_v_id(uc_key):
            stmt = (
                select(LlmPromptVersionModel)
                .where(
                    LlmPromptVersionModel.use_case_key == uc_key,
                    LlmPromptVersionModel.status == PromptStatus.PUBLISHED,
                )
                .order_by(LlmPromptVersionModel.created_at.desc())
            )
            v = db.execute(stmt).scalars().first()
            if v:
                return v.id

            # Create stub if missing
            from app.prompts.catalog import PROMPT_CATALOG

            entry = PROMPT_CATALOG.get(uc_key)
            if not entry:
                print(f"ERROR: No catalog entry for {uc_key}")
                return None

            # Ensure UC config
            uc_stmt = select(LlmUseCaseConfigModel).where(LlmUseCaseConfigModel.key == uc_key)
            uc = db.execute(uc_stmt).scalar_one_or_none()
            if not uc:
                uc = LlmUseCaseConfigModel(
                    key=uc_key,
                    display_name=uc_key.replace("_", " ").title(),
                    description=entry.description,
                    safety_profile="astrology",
                )
                db.add(uc)
                db.flush()

            v = LlmPromptVersionModel(
                id=uuid.uuid4(),
                use_case_key=uc_key,
                developer_prompt=entry.description,
                model="gpt-4o-mini",
                max_output_tokens=entry.max_tokens,
                temperature=entry.temperature,
                status=PromptStatus.PUBLISHED,
                created_by="system_66_20",
            )
            db.add(v)
            db.flush()
            return v.id

        # 3. Target Map: (feature, subfeature, plan) -> (use_case_key, base_profile_key)
        target_map = [
            # CHAT
            ("chat", "astrologer", "free", "chat", "standard"),
            ("chat", "astrologer", "premium", "chat_astrologer", "premium"),
            # GUIDANCE
            ("guidance", "daily", "free", "guidance_daily", "standard"),
            ("guidance", "daily", "premium", "guidance_daily", "premium"),
            ("guidance", "weekly", "free", "guidance_weekly", "standard"),
            ("guidance", "weekly", "premium", "guidance_weekly", "premium"),
            ("guidance", "contextual", "free", "guidance_contextual", "standard"),
            ("guidance", "contextual", "premium", "guidance_contextual", "premium"),
            # NATAL
            ("natal", "natal_interpretation", "free", "natal_long_free", "standard"),
            ("natal", "natal_interpretation", "premium", "natal_interpretation", "premium"),
            # Added other natal subfeatures from catalog to be safe
            ("natal", "natal_psy_profile", "premium", "natal_psy_profile", "premium"),
            ("natal", "natal_shadow_integration", "premium", "natal_shadow_integration", "premium"),
            (
                "natal",
                "natal_leadership_workstyle",
                "premium",
                "natal_leadership_workstyle",
                "premium",
            ),
            ("natal", "natal_creativity_joy", "premium", "natal_creativity_joy", "premium"),
            ("natal", "natal_relationship_style", "premium", "natal_relationship_style", "premium"),
            ("natal", "natal_community_networks", "premium", "natal_community_networks", "premium"),
            ("natal", "natal_values_security", "premium", "natal_values_security", "premium"),
            ("natal", "natal_evolution_path", "premium", "natal_evolution_path", "premium"),
        ]

        for f, sf, p, uc_key, b_prof_key in target_map:
            v_id = get_v_id(uc_key)
            if not v_id:
                continue

            # A. Create Targeted Execution Profile (for Waterfall)
            prof_name = f"Profile for {f}/{sf}/{p}"
            existing_prof = db.execute(
                select(LlmExecutionProfileModel).where(
                    LlmExecutionProfileModel.feature == f,
                    LlmExecutionProfileModel.subfeature == sf,
                    LlmExecutionProfileModel.plan == p,
                    LlmExecutionProfileModel.status == PromptStatus.PUBLISHED,
                )
            ).scalar_one_or_none()

            base_prof = db.get(LlmExecutionProfileModel, resolved_base_ids[b_prof_key])

            if not existing_prof:
                target_prof = LlmExecutionProfileModel(
                    id=uuid.uuid4(),
                    name=prof_name,
                    provider=base_prof.provider,
                    model=base_prof.model,
                    reasoning_profile=base_prof.reasoning_profile,
                    verbosity_profile=base_prof.verbosity_profile,
                    output_mode=base_prof.output_mode,
                    tool_mode=base_prof.tool_mode,
                    timeout_seconds=base_prof.timeout_seconds,
                    feature=f,
                    subfeature=sf,
                    plan=p,
                    status=PromptStatus.PUBLISHED,
                    created_by="system_66_20",
                )
                db.add(target_prof)
                db.flush()
                target_prof_id = target_prof.id
                print(f"Created targeted profile: {prof_name}")
            else:
                target_prof_id = existing_prof.id

            # B. Create/Update Assembly Config
            existing_asm = db.execute(
                select(PromptAssemblyConfigModel).where(
                    PromptAssemblyConfigModel.feature == f,
                    PromptAssemblyConfigModel.subfeature == sf,
                    PromptAssemblyConfigModel.plan == p,
                    PromptAssemblyConfigModel.status == PromptStatus.PUBLISHED,
                )
            ).scalar_one_or_none()

            if not existing_asm:
                asm = PromptAssemblyConfigModel(
                    id=uuid.uuid4(),
                    feature=f,
                    subfeature=sf,
                    plan=p,
                    locale="fr-FR",
                    feature_template_ref=v_id,
                    execution_profile_ref=target_prof_id,
                    execution_config={
                        "model": base_prof.model,
                        "temperature": 0.7,
                        "max_output_tokens": 2048,
                        "timeout_seconds": 30,
                    },
                    status=PromptStatus.PUBLISHED,
                    created_by="system_66_20",
                )
                db.add(asm)
                print(f"Created assembly: {f}/{sf}/{p}")
            else:
                existing_asm.feature_template_ref = v_id
                existing_asm.execution_profile_ref = target_prof_id
                existing_asm.execution_config = {
                    "model": base_prof.model,
                    "temperature": 0.7,
                    "max_output_tokens": 2048,
                    "timeout_seconds": 30,
                }
                print(f"Updated assembly: {f}/{sf}/{p}")

        db.commit()
        print("Seed 66.20 convergence completed.")


if __name__ == "__main__":
    seed_66_20_convergence()
