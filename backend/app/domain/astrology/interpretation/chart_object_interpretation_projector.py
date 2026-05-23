# Projection des payloads chart-object vers l'input interpretatif.
"""Projector sans recalcul pour les faits runtime deja attaches aux objets."""

from __future__ import annotations

from app.domain.astrology.interpretation.chart_interpretation_input_contracts import (
    ChartObjectInterpretationRuntimeData,
    DignityBreakdownInterpretationRuntimeData,
    DignityInterpretationRuntimeData,
    DominanceBreakdownInterpretationRuntimeData,
    DominanceInterpretationRuntimeData,
    FixedStarContactInterpretationRuntimeData,
    HousePositionInterpretationRuntimeData,
    MotionInterpretationRuntimeData,
    RulershipInterpretationRuntimeData,
    VisibilityInterpretationRuntimeData,
    ZodiacInterpretationRuntimeData,
)
from app.domain.astrology.runtime.chart_object_runtime_data import (
    ChartObjectRuntimeData,
    DignityRuntimePayload,
    DominanceRuntimePayload,
)


class ChartObjectInterpretationProjector:
    """Convertit un objet runtime en contrat interpretable."""

    def project(self, chart_object: ChartObjectRuntimeData) -> ChartObjectInterpretationRuntimeData:
        """Projette les payloads existants et refuse une position zodiacale absente."""
        if chart_object.zodiac_position is None:
            raise ValueError(
                f"interpretable chart object requires zodiac position: {chart_object.code}"
            )
        house_position = self.project_house_position(chart_object)
        return ChartObjectInterpretationRuntimeData(
            code=chart_object.code,
            display_name=chart_object.display_name,
            object_type=chart_object.object_type,
            classifications=chart_object.classifications,
            source_type=chart_object.source.source_type,
            source_key=chart_object.source.source_key,
            longitude=chart_object.longitude,
            latitude=chart_object.latitude,
            zodiac_position=ZodiacInterpretationRuntimeData(
                sign_code=chart_object.zodiac_position.sign_code,
                degree_in_sign=chart_object.zodiac_position.degree_in_sign,
            ),
            house_number=house_position.house_number if house_position is not None else None,
            house_modality=house_position.house_modality if house_position is not None else None,
            dignity=self.project_dignity(chart_object),
            motion=self.project_motion(chart_object),
            visibility=self.project_visibility(chart_object),
            dominance=self.project_dominance(chart_object),
            rulership=self.project_rulership(chart_object),
            fixed_star_contacts=self.project_fixed_star_contacts(chart_object),
            source_codes=self._source_codes(chart_object),
        )

    def project_dignity(
        self, chart_object: ChartObjectRuntimeData
    ) -> DignityInterpretationRuntimeData | None:
        """Projette le payload dignity rattache a l'objet."""
        payload = chart_object.payloads.dignity
        if payload is None:
            return None
        return _dignity_from_payload(chart_object.code, payload)

    def project_dominance(
        self, chart_object: ChartObjectRuntimeData
    ) -> DominanceInterpretationRuntimeData | None:
        """Projette le payload dominance rattache a l'objet."""
        payload = chart_object.payloads.dominance
        if payload is None:
            return None
        return _dominance_from_payload(chart_object.code, payload)

    def project_house_position(
        self, chart_object: ChartObjectRuntimeData
    ) -> HousePositionInterpretationRuntimeData | None:
        """Projette la position en maison rattachee a l'objet."""
        payload = chart_object.payloads.house_position
        if payload is None:
            return None
        return HousePositionInterpretationRuntimeData(
            code=chart_object.code,
            house_number=payload.house_number,
            house_modality=payload.house_modality,
            source=payload.source,
            house_cusp_code=payload.house_cusp_code,
            house_cusp_longitude=payload.house_cusp_longitude,
        )

    def project_rulership(
        self, chart_object: ChartObjectRuntimeData
    ) -> RulershipInterpretationRuntimeData | None:
        """Projette les maitrises rattachees a l'objet."""
        payload = chart_object.payloads.rulership
        if payload is None:
            return None
        return RulershipInterpretationRuntimeData(
            code=chart_object.code,
            rules_houses=payload.rules_houses,
            is_house_ruler=payload.is_house_ruler,
            is_ascendant_ruler=payload.is_ascendant_ruler,
            is_midheaven_ruler=payload.is_midheaven_ruler,
            source=payload.source,
            dispositor_code=payload.dispositor_code,
            rules_signs=payload.rules_signs,
            rulership_sources=payload.rulership_sources,
        )

    def project_motion(
        self, chart_object: ChartObjectRuntimeData
    ) -> MotionInterpretationRuntimeData | None:
        """Projette les faits de mouvement rattaches a l'objet."""
        payload = chart_object.payloads.motion
        if payload is None:
            return None
        return MotionInterpretationRuntimeData(
            speed_longitude=payload.speed_longitude,
            is_retrograde=payload.is_retrograde,
            direction=payload.direction,
            is_direct=payload.is_direct,
            is_stationary=payload.is_stationary,
            speed_state=payload.speed_state,
            absolute_speed_longitude=payload.absolute_speed_longitude,
            normalized_speed_ratio=payload.normalized_speed_ratio,
            source=payload.source,
        )

    def project_visibility(
        self, chart_object: ChartObjectRuntimeData
    ) -> VisibilityInterpretationRuntimeData | None:
        """Projette les faits de visibilite rattaches a l'objet."""
        payload = chart_object.payloads.visibility
        if payload is None:
            return None
        return VisibilityInterpretationRuntimeData(
            visibility_key=payload.visibility_key,
            is_visible=payload.is_visible,
            confidence=payload.confidence,
            reason=payload.reason,
            solar_separation_deg=payload.solar_separation_deg,
            solar_proximity_key=payload.solar_proximity_key,
            solar_phase_relation_key=payload.solar_phase_relation_key,
            is_cazimi=payload.is_cazimi,
            is_combust=payload.is_combust,
            is_under_beams=payload.is_under_beams,
            is_oriental=payload.is_oriental,
            is_occidental=payload.is_occidental,
            source=payload.source,
        )

    def project_fixed_star_contacts(
        self, chart_object: ChartObjectRuntimeData
    ) -> tuple[FixedStarContactInterpretationRuntimeData, ...]:
        """Projette les contacts etoile fixe rattaches a l'objet."""
        return tuple(
            FixedStarContactInterpretationRuntimeData(
                fixed_star_code=payload.fixed_star_code,
                fixed_star_display_name=payload.fixed_star_display_name,
                target_code=payload.target_code,
                target_display_name=payload.target_display_name,
                fixed_star_longitude_deg=payload.fixed_star_longitude_deg,
                target_longitude_deg=payload.target_longitude_deg,
                orb_deg=payload.orb_deg,
                max_orb_deg=payload.max_orb_deg,
                rule_code=payload.rule_code,
                source=payload.source,
            )
            for payload in chart_object.payloads.fixed_star_conjunctions
        )

    def _source_codes(self, chart_object: ChartObjectRuntimeData) -> tuple[str, ...]:
        """Expose les sources techniques presentes sur les payloads projetes."""
        codes = [chart_object.source.source_key]
        for payload in (
            chart_object.payloads.motion,
            chart_object.payloads.visibility,
            chart_object.payloads.dignity,
            chart_object.payloads.dominance,
            chart_object.payloads.house_position,
            chart_object.payloads.rulership,
        ):
            source = getattr(payload, "source", None)
            if isinstance(source, str) and source.strip():
                codes.append(source)
        codes.extend(payload.source for payload in chart_object.payloads.fixed_star_conjunctions)
        return tuple(dict.fromkeys(codes))


def _dignity_from_payload(
    code: str, payload: DignityRuntimePayload
) -> DignityInterpretationRuntimeData:
    """Copie un payload dignity vers le contrat d'entree."""
    return DignityInterpretationRuntimeData(
        code=code,
        essential_score=payload.essential_score,
        accidental_score=payload.accidental_score,
        total_score=payload.total_score,
        source=payload.source,
        functional_strength_score=payload.functional_strength_score,
        expression_quality_score=payload.expression_quality_score,
        intensity_score=payload.intensity_score,
        essential_breakdown=tuple(
            DignityBreakdownInterpretationRuntimeData(
                dignity_type_code=item.dignity_type_code,
                score_value=item.score_value,
                source=item.source,
            )
            for item in payload.essential_breakdown
        ),
        accidental_breakdown=tuple(
            DignityBreakdownInterpretationRuntimeData(
                dignity_type_code=item.dignity_type_code,
                score_value=item.score_value,
                source=item.source,
            )
            for item in payload.accidental_breakdown
        ),
        condition_codes=payload.condition_codes,
    )


def _dominance_from_payload(
    code: str, payload: DominanceRuntimePayload
) -> DominanceInterpretationRuntimeData:
    """Copie un payload dominance vers le contrat d'entree."""
    return DominanceInterpretationRuntimeData(
        code=code,
        score=payload.contribution_score,
        source=payload.source,
        rank=payload.rank,
        factors=payload.factors,
        breakdown=tuple(
            DominanceBreakdownInterpretationRuntimeData(
                factor_code=item.factor_code,
                raw_value=item.raw_value,
                normalized_value=item.normalized_value,
                weight=item.weight,
                weighted_score=item.weighted_score,
            )
            for item in payload.contribution_breakdown
        ),
    )
