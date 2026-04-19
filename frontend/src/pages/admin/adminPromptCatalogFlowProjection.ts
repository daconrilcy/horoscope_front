import type {
  AdminResolvedAssemblyView,
  AdminRuntimeArtifactView,
  AdminSelectedComponentView,
} from "@api"

import type { LogicGraphProjection, LogicGraphNodeTone } from "./adminPromptsLogicGraphProjection"

type PromptFlowNodeKind = "activation" | "selected_component" | "runtime_artifact"

export type AdminPromptCatalogFlowNode = {
  id: string
  kind: PromptFlowNodeKind
  title: string
  detail: string
  tone: LogicGraphNodeTone
  badge?: string
  position: { x: number; y: number }
  promptContent: string | null
  summary: string
  contentLabel: string
  meta: Array<{ label: string; value: string }>
  editableUseCaseKey: string | null
}

export type AdminPromptCatalogFlowProjection = LogicGraphProjection & {
  flowNodes: AdminPromptCatalogFlowNode[]
}

function toSingleLinePreview(value: string, limit = 72): string {
  const normalized = value.replace(/\s+/g, " ").trim()
  if (!normalized) {
    return "Texte disponible"
  }
  if (normalized.length <= limit) {
    return normalized
  }
  return `${normalized.slice(0, Math.max(limit - 1, 1)).trimEnd()}…`
}

function toMetaEntries(meta: Record<string, unknown>): Array<{ label: string; value: string }> {
  return Object.entries(meta)
    .filter(([, value]) => value !== null && value !== undefined && value !== "")
    .map(([label, value]) => ({
      label: label.replace(/_/g, " "),
      value: typeof value === "string" ? value : JSON.stringify(value),
    }))
}

function makeNode(
  id: string,
  kind: PromptFlowNodeKind,
  title: string,
  detail: string,
  tone: LogicGraphNodeTone,
  position: { x: number; y: number },
  promptContent: string | null,
  summary: string,
  contentLabel: string,
  meta: Array<{ label: string; value: string }>,
  editableUseCaseKey: string | null = null,
  badge?: string,
): AdminPromptCatalogFlowNode {
  return {
    id,
    kind,
    title,
    detail,
    tone,
    badge,
    position,
    promptContent,
    summary,
    contentLabel,
    meta,
    editableUseCaseKey,
  }
}

function getComponentTone(component: AdminSelectedComponentView): LogicGraphNodeTone {
  if (component.component_type === "hard_policy") {
    return "system"
  }
  if (component.component_type === "persona_overlay") {
    return "neutral"
  }
  if (component.impact_status === "reference_only") {
    return "layer"
  }
  return "layer"
}

function getArtifactTone(artifact: AdminRuntimeArtifactView): LogicGraphNodeTone {
  if (artifact.artifact_type === "system_prompt" || artifact.artifact_type === "final_provider_payload") {
    return "system"
  }
  return "neutral"
}

export function buildAdminPromptCatalogFlowProjection(
  resolvedView: AdminResolvedAssemblyView,
): AdminPromptCatalogFlowProjection {
  const flowNodes: AdminPromptCatalogFlowNode[] = []
  const flowEdges: AdminPromptCatalogFlowProjection["edges"] = []

  flowNodes.push(
    makeNode(
      "activation",
      "activation",
      "Activation",
      `${resolvedView.activation.feature} / ${resolvedView.activation.plan ?? "—"} / ${resolvedView.activation.locale ?? "—"}`,
      "layer",
      { x: 0, y: 210 },
      null,
      "Sélection canonique active pour ce contexte runtime.",
      "Détails d'activation",
      [
        { label: "Manifest", value: resolvedView.activation.manifest_entry_id },
        { label: "Feature", value: resolvedView.activation.feature },
        { label: "Subfeature", value: resolvedView.activation.subfeature ?? "—" },
        { label: "Plan", value: resolvedView.activation.plan ?? "—" },
        { label: "Locale", value: resolvedView.activation.locale ?? "—" },
        { label: "Execution profile", value: resolvedView.activation.execution_profile ?? "—" },
        { label: "Provider", value: resolvedView.activation.provider_target },
        { label: "Policy family", value: resolvedView.activation.policy_family },
        { label: "Output schema", value: resolvedView.activation.output_schema ?? "—" },
        { label: "Persona policy", value: resolvedView.activation.persona_policy ?? "—" },
      ],
    ),
  )

  resolvedView.selected_components.forEach((component, index) => {
    const nodeId = `component-${component.key}`
    const meta = [
      ...(component.ref ? [{ label: "Reference", value: component.ref }] : []),
      ...(component.source_label ? [{ label: "Source", value: component.source_label }] : []),
      ...(component.version_label ? [{ label: "Version", value: component.version_label }] : []),
      ...(component.merge_mode ? [{ label: "Merge mode", value: component.merge_mode }] : []),
      ...toMetaEntries(component.meta),
    ]
    flowNodes.push(
      makeNode(
        nodeId,
        "selected_component",
        component.title,
        component.content ? toSingleLinePreview(component.content) : component.impact_status,
        getComponentTone(component),
        { x: 360, y: 40 + index * 130 },
        component.content,
        component.summary,
        "Composant sélectionné",
        meta,
        component.editable_use_case_key,
        component.impact_status === "reference_only"
          ? "Reference"
          : component.impact_status === "absent"
            ? "Absent"
            : undefined,
      ),
    )
    flowEdges.push({ from: "activation", to: nodeId, label: "sélectionne" })
  })

  resolvedView.runtime_artifacts.forEach((artifact, index) => {
    const nodeId = `artifact-${artifact.key}`
    const meta = [
      ...(artifact.injection_point ? [{ label: "Injection", value: artifact.injection_point }] : []),
      ...toMetaEntries(artifact.meta),
    ]
    flowNodes.push(
      makeNode(
        nodeId,
        "runtime_artifact",
        artifact.title,
        artifact.content ? toSingleLinePreview(artifact.content) : artifact.change_status,
        getArtifactTone(artifact),
        { x: 760 + index * 320, y: 210 },
        artifact.content,
        artifact.summary,
        "Artefact runtime",
        meta,
        null,
        artifact.change_status === "unchanged" ? "No delta" : undefined,
      ),
    )
  })

  const assembledNode = "artifact-developer_prompt_assembled"
  const afterPersonaNode = "artifact-developer_prompt_after_persona"
  const afterInjectorsNode = "artifact-developer_prompt_after_injectors"
  const systemNode = "artifact-system_prompt"
  const payloadNode = "artifact-final_provider_payload"

  resolvedView.selected_components.forEach((component) => {
    const nodeId = `component-${component.key}`
    if (component.component_type === "persona_overlay") {
      if (flowNodes.some((node) => node.id === afterPersonaNode)) {
        flowEdges.push({ from: nodeId, to: afterPersonaNode, label: "ajoute persona" })
      }
      return
    }
    if (component.component_type === "hard_policy") {
      if (flowNodes.some((node) => node.id === systemNode)) {
        flowEdges.push({ from: nodeId, to: systemNode, label: "injecté en system" })
      }
      return
    }
    if (flowNodes.some((node) => node.id === assembledNode)) {
      flowEdges.push({ from: nodeId, to: assembledNode, label: "alimente" })
    }
  })

  if (flowNodes.some((node) => node.id === assembledNode) && flowNodes.some((node) => node.id === afterPersonaNode)) {
    flowEdges.push({ from: assembledNode, to: afterPersonaNode, label: "after persona" })
  }
  flowEdges.push({
    from: flowNodes.some((node) => node.id === afterPersonaNode) ? afterPersonaNode : assembledNode,
    to: afterInjectorsNode,
    label: "after injectors",
  })
  flowEdges.push({ from: afterInjectorsNode, to: payloadNode, label: "developer payload" })
  flowEdges.push({ from: systemNode, to: payloadNode, label: "system payload" })

  return {
    nodes: flowNodes.map((node) => ({
      id: node.id,
      title: node.title,
      detail: node.detail,
      tone: node.tone,
      badge: node.badge,
      position: node.position,
      interactive: true,
    })),
    flowNodes,
    edges: flowEdges,
    dense: false,
    boundaryRemountKey: [
      resolvedView.manifest_entry_id,
      resolvedView.active_snapshot_id ?? "",
      resolvedView.active_snapshot_version ?? "",
      resolvedView.use_case_key,
      resolvedView.runtime_artifacts.length,
    ].join("::"),
    fallbackSummary: [
      `Activation: ${resolvedView.activation.feature}/${resolvedView.activation.plan ?? "-"}/${resolvedView.activation.locale ?? "-"}`,
      ...resolvedView.selected_components.map((component) => `component:${component.key}`),
      ...resolvedView.runtime_artifacts.map((artifact) => `artifact:${artifact.key}`),
    ],
  }
}
