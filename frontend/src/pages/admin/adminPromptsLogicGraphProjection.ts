import type { AdminResolvedAssemblyView, AdminResolvedPlaceholder } from "@api"

export type LogicGraphNodeTone = "neutral" | "layer" | "system" | "fallback" | "sample"

export type LogicGraphNode = {
  id: string
  title: string
  detail: string
  tone: LogicGraphNodeTone
  badge?: string
  position?: { x: number; y: number }
  interactive?: boolean
}

export type LogicGraphEdge = {
  from: string
  to: string
  label: string
}

export type LogicGraphProjection = {
  nodes: LogicGraphNode[]
  edges: LogicGraphEdge[]
  dense: boolean
  fallbackSummary: string[]
  /** Identifiant stable pour remonter l Error Boundary : même manifest mais mode, snapshot ou placeholders différents. */
  boundaryRemountKey: string
}

function classifyPlaceholderSource(item: AdminResolvedPlaceholder): LogicGraphNodeTone | "runtime" {
  const source = (item.resolution_source ?? "").toLowerCase()
  if (source.includes("sample")) return "sample"
  if (source.includes("fallback")) return "fallback"
  if (
    source.includes("runtime") ||
    source === "static_preview_gap" ||
    source === "missing_required" ||
    item.status === "expected_missing_in_preview" ||
    item.status === "blocking_missing"
  ) {
    return "runtime"
  }
  return "neutral"
}

export function buildLogicGraphProjection(resolvedView: AdminResolvedAssemblyView): LogicGraphProjection {
  const rr = resolvedView.resolved_result
  const placeholders = Array.isArray(rr?.placeholders) ? rr.placeholders : []
  const contextCompensationStatus =
    typeof rr?.context_compensation_status === "string" ? rr.context_compensation_status : "n/a"
  const cs = resolvedView.composition_sources

  const placeholderStats = placeholders.reduce(
    (acc, item) => {
      const category = classifyPlaceholderSource(item)
      if (category === "fallback") {
        acc.fallback += 1
      } else if (category === "sample") {
        acc.sample += 1
      } else if (category === "runtime") {
        acc.runtime += 1
      }
      return acc
    },
    { runtime: 0, fallback: 0, sample: 0 },
  )
  const hasSubfeatureTemplate = Boolean(cs?.subfeature_template)
  const hasPlanRules = Boolean(cs?.plan_rules?.content)
  const hasPersonaBlock = Boolean(cs?.persona_block?.content)
  const dense = placeholders.length >= 16

  const nodes: LogicGraphNode[] = [
    { id: "manifest", title: "manifest_entry_id", detail: resolvedView.manifest_entry_id, tone: "neutral" },
    {
      id: "composition",
      title: "composition_sources",
      detail: `${resolvedView.feature}/${resolvedView.subfeature ?? "-"} · plan ${resolvedView.plan ?? "-"}`,
      tone: "neutral",
    },
    { id: "feature", title: "feature template", detail: cs?.feature_template?.id ?? "n/a", tone: "layer" },
    {
      id: "subfeature",
      title: "subfeature template",
      detail: hasSubfeatureTemplate ? (cs?.subfeature_template?.id ?? "actif") : "absent",
      tone: "layer",
    },
    {
      id: "planRules",
      title: "plan rules",
      detail: hasPlanRules ? (cs?.plan_rules?.ref ?? "actif") : "absent",
      tone: "layer",
    },
    {
      id: "persona",
      title: "persona block",
      detail: hasPersonaBlock ? (cs?.persona_block?.name ?? "actif") : "absent",
      tone: "layer",
    },
    {
      id: "hardPolicy",
      title: "hard policy",
      detail: cs?.hard_policy?.safety_profile ?? "n/a",
      tone: "system",
    },
    {
      id: "executionProfile",
      title: "execution profile",
      detail: `${cs?.execution_profile?.provider ?? "n/a"}/${cs?.execution_profile?.model ?? "n/a"}`,
      tone: "system",
    },
    { id: "pipeline", title: "transformation_pipeline", detail: "assembled -> injectors -> rendered", tone: "neutral" },
    {
      id: "providerMessages",
      title: "provider_messages",
      detail: `context_quality: ${contextCompensationStatus}`,
      tone: "system",
    },
    {
      id: "operatorResult",
      title: "résultat opérateur",
      detail: "Sortie structurée après fournisseur (schéma, métadonnées)",
      tone: "neutral",
    },
    {
      id: "runtimeInputs",
      title: "runtime inputs",
      detail: `runtime:${placeholderStats.runtime} · fallback:${placeholderStats.fallback} · sample:${placeholderStats.sample}`,
      tone: "neutral",
    },
    {
      id: "fallbackRegistry",
      title: "fallbacks registre",
      detail: `${placeholderStats.fallback} placeholder(s)`,
      tone: "fallback",
    },
    {
      id: "samplePayloads",
      title: "sample payloads",
      detail: `${placeholderStats.sample} placeholder(s)`,
      tone: "sample",
    },
  ]

  const edges: LogicGraphEdge[] = [
    { from: "manifest", to: "composition", label: "résout la cible canonique" },
    { from: "composition", to: "feature", label: "couche" },
    { from: "composition", to: "subfeature", label: hasSubfeatureTemplate ? "couche" : "optionnel" },
    { from: "composition", to: "planRules", label: hasPlanRules ? "couche" : "optionnel" },
    { from: "composition", to: "persona", label: hasPersonaBlock ? "couche" : "optionnel" },
    { from: "composition", to: "hardPolicy", label: "politique système" },
    { from: "composition", to: "executionProfile", label: "paramètres provider" },
    { from: "composition", to: "pipeline", label: "assemblage prompt" },
    { from: "hardPolicy", to: "providerMessages", label: "message system" },
    { from: "persona", to: "providerMessages", label: hasPersonaBlock ? "message persona" : "optionnel" },
    { from: "executionProfile", to: "providerMessages", label: "paramètres d'exécution" },
    { from: "pipeline", to: "providerMessages", label: "messages finaux" },
    { from: "providerMessages", to: "operatorResult", label: "validation / restitution" },
    { from: "runtimeInputs", to: "pipeline", label: "substitutions variables" },
    { from: "fallbackRegistry", to: "runtimeInputs", label: "fallbacks appliqués" },
    { from: "samplePayloads", to: "runtimeInputs", label: "données de test" },
  ]

  const placeholderFingerprint = placeholders
    .map((p) => `${p.name}:${p.status}:${p.resolution_source ?? ""}`)
    .sort()
    .join("|")

  const boundaryRemountKey = [
    resolvedView.manifest_entry_id,
    resolvedView.inspection_mode,
    resolvedView.active_snapshot_version ?? "",
    String(resolvedView.active_snapshot_id ?? ""),
    String(rr?.context_compensation_status ?? ""),
    dense ? "dense" : "sparse",
    placeholderFingerprint,
  ].join("::")

  return {
    nodes,
    edges,
    dense,
    boundaryRemountKey,
    fallbackSummary: [
      `manifest_entry_id: ${resolvedView.manifest_entry_id}`,
      `composition_sources -> transformation_pipeline -> provider_messages -> résultat opérateur`,
      `runtime inputs: runtime=${placeholderStats.runtime}, fallback=${placeholderStats.fallback}, sample=${placeholderStats.sample}`,
      `couches: feature template, subfeature template, plan rules, persona block, hard policy, execution profile`,
    ],
  }
}

/** Positions statiques gauche → droite pour lecture pédagogique (React Flow). */
export function layoutLogicGraphNodesForFlow(nodes: LogicGraphNode[]): Record<string, { x: number; y: number }> {
  const positions: Record<string, { x: number; y: number }> = {
    manifest: { x: 0, y: 320 },
    composition: { x: 260, y: 320 },
    feature: { x: 520, y: 0 },
    subfeature: { x: 520, y: 100 },
    planRules: { x: 520, y: 200 },
    persona: { x: 520, y: 300 },
    hardPolicy: { x: 520, y: 420 },
    executionProfile: { x: 520, y: 520 },
    fallbackRegistry: { x: 520, y: 640 },
    samplePayloads: { x: 520, y: 740 },
    pipeline: { x: 820, y: 320 },
    runtimeInputs: { x: 820, y: 520 },
    providerMessages: { x: 1120, y: 320 },
    operatorResult: { x: 1420, y: 320 },
  }
  for (const n of nodes) {
    if (n.position) {
      positions[n.id] = n.position
    } else if (!positions[n.id]) {
      positions[n.id] = { x: 0, y: 0 }
    }
  }
  return positions
}
