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


def seed_66_15_convergence():
    with Session(engine) as db:
        # 1. Create Execution Profiles
        profiles = {
            "standard": LlmExecutionProfileModel(
                id=uuid.uuid4(),
                name="OpenAI Standard (gpt-4o-mini)",
                provider="openai",
                model="gpt-4o-mini",
                reasoning_profile="off",
                verbosity_profile="balanced",
                output_mode="structured_json",
                tool_mode="none",
                timeout_seconds=30,
                status=PromptStatus.PUBLISHED,
                created_by="system_66_15",
            ),
            "premium": LlmExecutionProfileModel(
                id=uuid.uuid4(),
                name="OpenAI Premium (gpt-4o)",
                provider="openai",
                model="gpt-4o",
                reasoning_profile="off",
                verbosity_profile="detailed",
                output_mode="structured_json",
                tool_mode="none",
                timeout_seconds=60,
                status=PromptStatus.PUBLISHED,
                created_by="system_66_15",
            ),
            "reasoning": LlmExecutionProfileModel(
                id=uuid.uuid4(),
                name="OpenAI Reasoning (o1-preview)",
                provider="openai",
                model="o1-preview",
                reasoning_profile="medium",
                verbosity_profile="detailed",
                output_mode="structured_json",
                tool_mode="none",
                timeout_seconds=120,
                status=PromptStatus.PUBLISHED,
                created_by="system_66_15",
            ),
        }

        for key, p in profiles.items():
            # Avoid duplicates if script re-run
            existing = db.execute(
                select(LlmExecutionProfileModel).where(LlmExecutionProfileModel.name == p.name)
            ).scalar_one_or_none()
            if not existing:
                db.add(p)
            else:
                profiles[key] = existing  # Use the existing one from DB

        db.commit()
        print("Execution profiles seeded.")

        # 2. Get or create use case configs and prompt versions for templates
        def get_or_create_v(key):
            # Ensure UseCaseConfig exists (for foreign key)
            stmt_uc = select(LlmUseCaseConfigModel).where(LlmUseCaseConfigModel.key == key)
            db_uc = db.execute(stmt_uc).scalar_one_or_none()

            if not db_uc:
                from app.domain.llm.prompting.catalog import PROMPT_CATALOG

                entry = PROMPT_CATALOG.get(key)
                if not entry:
                    print(f"No catalog entry for {key}, cannot create UC config.")
                    return None

                db_uc = LlmUseCaseConfigModel(
                    key=key,
                    display_name=key.replace("_", " ").title(),
                    description=entry.description,
                    safety_profile="astrology",
                )
                db.add(db_uc)
                db.commit()
                print(f"Created UC config for {key}")

            stmt = (
                select(LlmPromptVersionModel)
                .where(
                    LlmPromptVersionModel.use_case_key == key,
                    LlmPromptVersionModel.status == PromptStatus.PUBLISHED,
                )
                .order_by(LlmPromptVersionModel.created_at.desc())
            )
            v = db.execute(stmt).scalars().first()
            if v:
                return v

            # Create stub version
            from app.domain.llm.prompting.catalog import PROMPT_CATALOG

            entry = PROMPT_CATALOG.get(key)
            if not entry:
                print(f"No catalog entry for {key}, cannot create stub.")
                return None

            v = LlmPromptVersionModel(
                id=uuid.uuid4(),
                use_case_key=key,
                developer_prompt=entry.description,  # Just a placeholder
                model="gpt-4o-mini",
                max_output_tokens=entry.max_tokens,
                temperature=entry.temperature,
                status=PromptStatus.PUBLISHED,
                created_by="system_66_15",
            )
            db.add(v)
            db.commit()
            print(f"Created stub prompt version for {key}")
            return v

        # 3. Create Assembly Configs
        # Combinations: feature / subfeature / plan
        assemblies = [
            # NATAL
            (
                "natal",
                "interpretation",
                "premium",
                "natal_interpretation",
                profiles["premium"].id,
            ),
            ("natal", "interpretation", "free", "natal_long_free", profiles["standard"].id),
            ("natal", "short", "free", "natal_interpretation_short", profiles["standard"].id),
            # GUIDANCE
            ("guidance", "daily", "free", "guidance_daily", profiles["standard"].id),
            ("guidance", "daily", "premium", "guidance_daily", profiles["premium"].id),
            ("guidance", "weekly", "free", "guidance_weekly", profiles["standard"].id),
            ("guidance", "weekly", "premium", "guidance_weekly", profiles["premium"].id),
            ("guidance", "contextual", "premium", "guidance_contextual", profiles["premium"].id),
            ("guidance", "event", "premium", "event_guidance", profiles["premium"].id),
            # CHAT
            ("chat", "astrologer", "free", "chat", profiles["standard"].id),
            ("chat", "astrologer", "premium", "chat_astrologer", profiles["premium"].id),
        ]

        for f, sf, p, uc_key, prof_id in assemblies:
            v = get_or_create_v(uc_key)
            if not v:
                continue

            # Avoid duplicates
            existing = db.execute(
                select(PromptAssemblyConfigModel).where(
                    PromptAssemblyConfigModel.feature == f,
                    PromptAssemblyConfigModel.subfeature == sf,
                    PromptAssemblyConfigModel.plan == p,
                    PromptAssemblyConfigModel.status == PromptStatus.PUBLISHED,
                )
            ).scalar_one_or_none()

            if not existing:
                config = PromptAssemblyConfigModel(
                    id=uuid.uuid4(),
                    feature=f,
                    subfeature=sf,
                    plan=p,
                    locale="fr-FR",
                    feature_template_ref=v.id,
                    execution_profile_ref=prof_id,
                    execution_config={
                        "model": v.model,
                        "max_output_tokens": v.max_output_tokens,
                    },  # compatibility
                    status=PromptStatus.PUBLISHED,
                    created_by="system_66_15",
                )
                db.add(config)
                print(f"Created assembly config: {f}/{sf}/{p}")

        db.commit()
        print("Assembly configs seeded.")


if __name__ == "__main__":
    seed_66_15_convergence()
