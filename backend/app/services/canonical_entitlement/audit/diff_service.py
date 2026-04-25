# Service de calcul du diff canonique des mutations entitlement.
"""Calcule un diff stable et un niveau de risque pour les mutations canoniques."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class QuotaChangeSummary:
    """Résume les changements de quotas détectés dans une mutation."""

    added: list[dict]
    removed: list[dict]
    updated: list[dict]  # inclut before_quota_limit et quota_limit


@dataclass
class MutationDiffResult:
    """Expose le diff canonique consommé par les services d'audit et d'alerte."""

    change_kind: str  # "binding_created" | "binding_updated"
    changed_fields: list[str]  # trié, chemins stables
    risk_level: str  # "high" | "medium" | "low"
    quota_changes: QuotaChangeSummary


class CanonicalEntitlementMutationDiffService:
    """Calcule le diff métier canonique entre deux snapshots de binding."""

    _BINDING_FIELDS = ["is_enabled", "access_mode", "variant_code", "source_origin"]

    @staticmethod
    def compute_diff(before: dict, after: dict) -> MutationDiffResult:
        if not before:
            # Création
            return CanonicalEntitlementMutationDiffService._diff_created(after)
        return CanonicalEntitlementMutationDiffService._diff_updated(before, after)

    @staticmethod
    def _quota_key(q: dict) -> tuple:
        return (
            q.get("quota_key"),
            q.get("period_unit"),
            q.get("period_value"),
            q.get("reset_mode"),
        )

    @staticmethod
    def _diff_created(after: dict) -> MutationDiffResult:
        added_quotas = [{**q} for q in after.get("quotas", [])]
        quota_changes = QuotaChangeSummary(added=added_quotas, removed=[], updated=[])
        # risk_level pour création : basé sur access_mode (valeurs enum .value, minuscules)
        access_mode = after.get("access_mode", "")
        if access_mode == "quota":
            risk = "high"
        elif access_mode == "disabled":
            risk = "low"
        else:  # "unlimited" ou absent (cas dégradé = medium selon AC 5 point 18)
            risk = "medium"
        return MutationDiffResult(
            change_kind="binding_created",
            changed_fields=[],
            risk_level=risk,
            quota_changes=quota_changes,
        )

    @staticmethod
    def _diff_updated(before: dict, after: dict) -> MutationDiffResult:
        changed_fields: list[str] = []
        # Binding fields
        for f in ["is_enabled", "access_mode", "variant_code", "source_origin"]:
            if before.get(f) != after.get(f):
                changed_fields.append(f"binding.{f}")

        # Quota diff
        before_map = {
            CanonicalEntitlementMutationDiffService._quota_key(q): q
            for q in before.get("quotas", [])
        }
        after_map = {
            CanonicalEntitlementMutationDiffService._quota_key(q): q
            for q in after.get("quotas", [])
        }

        added, removed, updated = [], [], []
        for key, q in after_map.items():
            if key not in before_map:
                added.append({**q})
            elif before_map[key].get("quota_limit") != q.get("quota_limit"):
                updated.append(
                    {
                        **q,
                        "before_quota_limit": before_map[key].get("quota_limit"),
                    }
                )
                path = f"quotas[{key[0]},{key[1]},{key[2]},{key[3]}].quota_limit"
                changed_fields.append(path)

        for key, q in before_map.items():
            if key not in after_map:
                removed.append({**q})

        changed_fields.sort()
        quota_changes = QuotaChangeSummary(added=added, removed=removed, updated=updated)

        # Risk scoring
        risk = CanonicalEntitlementMutationDiffService._score_risk(
            before=before,
            after=after,
            changed_fields=changed_fields,
            quota_changes=quota_changes,
        )
        return MutationDiffResult(
            change_kind="binding_updated",
            changed_fields=changed_fields,
            risk_level=risk,
            quota_changes=quota_changes,
        )

    @staticmethod
    def _score_risk(
        *,
        before: dict,
        after: dict,
        changed_fields: list[str],
        quota_changes: QuotaChangeSummary,
    ) -> str:
        # HIGH
        if (
            "binding.access_mode" in changed_fields
            or "binding.is_enabled" in changed_fields
            or quota_changes.removed
        ):
            return "high"
        for u in quota_changes.updated:
            before_limit = u.get("before_quota_limit")
            after_limit = u.get("quota_limit")
            if before_limit is not None and after_limit is not None and after_limit < before_limit:
                return "high"

        # MEDIUM
        if quota_changes.added or "binding.variant_code" in changed_fields:
            return "medium"
        for u in quota_changes.updated:
            before_limit = u.get("before_quota_limit")
            after_limit = u.get("quota_limit")
            if before_limit is not None and after_limit is not None and after_limit > before_limit:
                return "medium"

        # LOW
        return "low"
