from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.prediction.schemas import AstroEvent


@dataclass(frozen=True)
class ContributorEntry:
    """A single contribution to a category score."""

    event_type: str
    body: str | None
    target: str | None
    aspect: str | None
    contribution: float
    local_time: datetime
    orb_deg: float | None
    phase: str | None


@dataclass(frozen=True)
class CategoryExplainability:
    """Explainability for a single category."""

    category_code: str
    top_contributors: list[ContributorEntry]


@dataclass(frozen=True)
class ExplainabilityReport:
    """Complete explainability report for a run."""

    run_input_hash: str
    categories: dict[str, CategoryExplainability]
    debug_data: dict[str, Any] | None = None


class ExplainabilityBuilder:
    """Builder for ExplainabilityReport."""

    MAX_CONTRIBUTORS = 3

    def build(
        self,
        contributions_log: list[tuple[AstroEvent, str, float]],
        run_input_hash: str,
        debug_mode: bool,
        raw_contributions_by_step: dict[str, Any] | None = None,
    ) -> ExplainabilityReport:
        """
        Build an explainability report from a log of contributions.

        Args:
            contributions_log: List of (event, category_code, contribution_value)
            run_input_hash: Hash of the engine input
            debug_mode: Whether to include raw debug data
            raw_contributions_by_step: Raw contributions per step for debugging

        Returns:
            An ExplainabilityReport
        """
        by_category: dict[str, list[tuple[float, AstroEvent, float]]] = {}
        for event, cat_code, contribution in contributions_log:
            by_category.setdefault(cat_code, []).append((abs(contribution), event, contribution))

        categories: dict[str, CategoryExplainability] = {}
        for cat_code, items in by_category.items():
            # Sort by abs(contribution) descending
            items.sort(reverse=True, key=lambda x: x[0])
            top_items = items[: self.MAX_CONTRIBUTORS]

            top_contributors = [
                ContributorEntry(
                    event_type=ev.event_type,
                    body=ev.body,
                    target=ev.target,
                    aspect=ev.aspect,
                    contribution=contrib,
                    local_time=ev.local_time,
                    orb_deg=ev.orb_deg,
                    phase=(ev.metadata or {}).get("phase"),
                )
                for _, ev, contrib in top_items
            ]
            categories[cat_code] = CategoryExplainability(
                category_code=cat_code, top_contributors=top_contributors
            )

        return ExplainabilityReport(
            run_input_hash=run_input_hash,
            categories=categories,
            debug_data=raw_contributions_by_step if debug_mode else None,
        )
