from __future__ import annotations

from typing import TYPE_CHECKING

from .editorial_builder import EditorialOutputBuilder
from .editorial_template_engine import EditorialTemplateEngine
from .schemas import EditorialOutputBundle

if TYPE_CHECKING:
    from .schemas import CoreEngineOutput, V3EvidencePack


class PredictionEditorialService:
    """
    Service responsible for transforming raw engine output into human-readable 
    editorial content.
    """

    def __init__(
        self,
        builder: EditorialOutputBuilder | None = None,
        engine: EditorialTemplateEngine | None = None,
    ) -> None:
        self._builder = builder or EditorialOutputBuilder()
        self._engine = engine or EditorialTemplateEngine()

    def generate_bundle(
        self,
        core_output: CoreEngineOutput,
        lang: str = "fr",
        evidence_pack: V3EvidencePack | None = None,
    ) -> EditorialOutputBundle:
        """
        Builds the editorial data and renders the associated texts.
        AC1 Story 42.16: Use evidence_pack if available.
        """
        # 1. Build structured editorial data
        if evidence_pack:
            editorial_data = self._builder.build_from_evidence(evidence_pack)
        else:
            editorial_data = self._builder.build(
                core_output,  # type: ignore
                core_output.explainability,  # type: ignore
            )

        # 2. Render templates into final texts
        editorial_text = self._engine.render(
            editorial_data,
            lang=lang,
            time_blocks=core_output.time_blocks,
            turning_points=core_output.turning_points,
        )

        return EditorialOutputBundle(
            data=editorial_data,
            text=editorial_text,
        )
