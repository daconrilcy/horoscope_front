"""Resolution typée des instructions de calcul des points astraux.

Ce module transforme les points `astral_point_*` chargés au runtime en
instructions calculables sans recréer de catalogue de points concurrent.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.domain.astrology.runtime.runtime_reference import (
    AstralPointRuntime,
    AstralPointVariantRuntime,
)


@dataclass(frozen=True, slots=True)
class AstralPointCalculationInstruction:
    """Instruction finale utilisée par le calcul natal pour positionner un point."""

    point_code: str
    variant_code: str
    calculation_mode: str
    engine_key: str | None
    derived_from_point_code: str | None = None
    derived_from_variant_code: str | None = None
    longitude_offset_deg: float = 0.0

    @property
    def is_derived(self) -> bool:
        """Indique si l'instruction depend d'un autre point déjà calculé."""
        return self.derived_from_point_code is not None


class AstralPointCalculationResolver:
    """Résout une variante de point astral vers une instruction stricte."""

    def resolve(
        self,
        point: AstralPointRuntime,
        variant_code: str | None = None,
    ) -> AstralPointCalculationInstruction:
        """Retourne l'instruction typée pour le point et la variante demandés."""
        variant = self._select_variant(point, variant_code)
        mode = variant.calculation_mode.strip().lower()
        if mode.endswith("_opposition") or mode.endswith("_perigee"):
            base_mode = self._base_mode(mode)
            base_point_code = self._base_point_code(point.code, mode)
            return AstralPointCalculationInstruction(
                point_code=point.code,
                variant_code=variant.variant_code,
                calculation_mode=mode,
                engine_key=None,
                derived_from_point_code=base_point_code,
                derived_from_variant_code=self._base_variant_code(variant.variant_code, base_mode),
                longitude_offset_deg=180.0,
            )
        if variant.engine_key is None:
            raise ValueError(
                f"astral point variant has no engine key: {point.code}/{variant.variant_code}"
            )
        return AstralPointCalculationInstruction(
            point_code=point.code,
            variant_code=variant.variant_code,
            calculation_mode=mode,
            engine_key=variant.engine_key,
        )

    def _select_variant(
        self,
        point: AstralPointRuntime,
        variant_code: str | None,
    ) -> AstralPointVariantRuntime:
        """Sélectionne la variante explicite ou celle marquée par défaut."""
        requested = variant_code or point.default_variant_code
        if requested is None:
            raise ValueError(f"astral point has no default variant: {point.code}")
        for variant in point.variants:
            if variant.variant_code == requested:
                return variant
        raise ValueError(f"unknown astral point variant: {point.code}/{requested}")

    def _base_mode(self, mode: str) -> str:
        """Déduit le mode moteur source pour une variante dérivée."""
        if mode == "true_opposition":
            return "true"
        if mode == "mean_opposition":
            return "mean"
        if mode == "osculating_perigee":
            return "osculating_apogee"
        if mode == "mean_perigee":
            return "mean_apogee"
        raise ValueError(f"unsupported derived astral point mode: {mode}")

    def _base_point_code(self, point_code: str, mode: str) -> str:
        """Déduit le point source d'une longitude dérivée."""
        if mode.endswith("_opposition"):
            return "north_node"
        if mode.endswith("_perigee"):
            return "lunar_apogee"
        raise ValueError(f"unsupported derived astral point: {point_code}/{mode}")

    def _base_variant_code(self, variant_code: str, base_mode: str) -> str:
        """Conserve la variante métier quand elle existe pour le point source."""
        if base_mode == "osculating_apogee":
            return "true"
        if base_mode == "mean_apogee":
            return "mean"
        return variant_code
