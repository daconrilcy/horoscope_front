import type { AdminResolvedAssemblyView } from "@api"

import type { LogicGraphProjection, LogicGraphNodeTone } from "./adminPromptsLogicGraphProjection"

type PromptFlowNodeKind =
  | "feature_template"
  | "subfeature_template"
  | "plan_rules"
  | "use_case_prompt"
  | "persona_block"
  | "hard_policy"
  | "assembled_prompt"
  | "post_injectors_prompt"
  | "rendered_prompt"

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
  meta: Array<{ label: string; value: string }>
  editableUseCaseKey: string | null
}

export type AdminPromptCatalogFlowProjection = LogicGraphProjection & {
  flowNodes: AdminPromptCatalogFlowNode[]
}

type UseCaseNodePresentation = {
  canonicalDisplayName: string
  runtimeDisplayName: string | null
}

function toSingleLinePreview(value: string, limit = 88): string {
  const normalized = value.replace(/\s+/g, " ").trim()
  if (normalized.length <= limit) {
    return normalized || "Texte disponible"
  }
  return `${normalized.slice(0, Math.max(limit - 1, 1)).trimEnd()}…`
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
    meta,
    editableUseCaseKey,
  }
}

export function buildAdminPromptCatalogFlowProjection(
  resolvedView: AdminResolvedAssemblyView,
  useCasePresentation: UseCaseNodePresentation,
): AdminPromptCatalogFlowProjection {
  const flowNodes: AdminPromptCatalogFlowNode[] = []
  const flowEdges: AdminPromptCatalogFlowProjection["edges"] = []
  const sourceTargets: string[] = []
  const pushSourceNode = (
    node: AdminPromptCatalogFlowNode | null,
    edgeLabel: string,
  ) => {
    if (!node) {
      return
    }
    flowNodes.push(node)
    sourceTargets.push(node.id)
    flowEdges.push({ from: node.id, to: "assembledPrompt", label: edgeLabel })
  }

  const { composition_sources: sources, transformation_pipeline: pipeline } = resolvedView

  pushSourceNode(
    makeNode(
      "featureTemplate",
      "feature_template",
      "Feature template",
      sources.feature_template.id,
      "layer",
      { x: 0, y: 0 },
      sources.feature_template.content,
      "Couche de base activée pour la feature.",
      [
        { label: "Feature", value: resolvedView.feature },
        { label: "Template", value: sources.feature_template.id },
      ],
    ),
    "base",
  )

  pushSourceNode(
    sources.subfeature_template
      ? makeNode(
          "subfeatureTemplate",
          "subfeature_template",
          "Subfeature template",
          sources.subfeature_template.id,
          "layer",
          { x: 0, y: 130 },
          sources.subfeature_template.content,
          "Couche active spécifique à la sous-fonction.",
          [
            { label: "Subfeature", value: resolvedView.subfeature ?? "—" },
            { label: "Template", value: sources.subfeature_template.id },
          ],
        )
      : null,
    "scope",
  )

  pushSourceNode(
    sources.plan_rules?.content
      ? makeNode(
          "planRules",
          "plan_rules",
          "Plan rules",
          sources.plan_rules.ref ?? (resolvedView.plan ?? "actif"),
          "layer",
          { x: 0, y: 260 },
          sources.plan_rules.content,
          "Règles de formule injectées dans la chaîne active.",
          [
            { label: "Plan", value: resolvedView.plan ?? "—" },
            { label: "Référence", value: sources.plan_rules.ref ?? "inline" },
          ],
        )
      : null,
    "plan",
  )

  pushSourceNode(
    makeNode(
      "useCasePrompt",
      "use_case_prompt",
      useCasePresentation.runtimeDisplayName &&
      useCasePresentation.runtimeDisplayName !== useCasePresentation.canonicalDisplayName
        ? "Prompt use case canonique / runtime"
        : "Prompt use case",
      useCasePresentation.runtimeDisplayName &&
      useCasePresentation.runtimeDisplayName !== useCasePresentation.canonicalDisplayName
        ? `${useCasePresentation.canonicalDisplayName} -> ${useCasePresentation.runtimeDisplayName}`
        : useCasePresentation.canonicalDisplayName,
      "neutral",
      { x: 0, y: 390 },
      null,
      useCasePresentation.runtimeDisplayName &&
      useCasePresentation.runtimeDisplayName !== useCasePresentation.canonicalDisplayName
        ? "Le prompt canonique éditable diffère du use case réellement appelé par le runtime pour cette cible."
        : "Prompt éditable actuellement publié pour ce contexte runtime.",
      [
        { label: "Use case canonique", value: resolvedView.use_case_key },
        ...(resolvedView.runtime_use_case_key &&
        resolvedView.runtime_use_case_key !== resolvedView.use_case_key
          ? [{ label: "Use case runtime", value: resolvedView.runtime_use_case_key }]
          : []),
        { label: "Manifest", value: resolvedView.manifest_entry_id },
      ],
      resolvedView.use_case_key,
      resolvedView.runtime_use_case_key &&
        resolvedView.runtime_use_case_key !== resolvedView.use_case_key
        ? "Runtime different"
        : undefined,
    ),
    "prompt actif",
  )

  pushSourceNode(
    sources.persona_block?.content
      ? makeNode(
          "personaBlock",
          "persona_block",
          "Persona block",
          sources.persona_block.name ?? "persona",
          "layer",
          { x: 360, y: 130 },
          sources.persona_block.content,
          "Bloc persona actif dans la chaîne courante.",
          [
            { label: "Persona", value: sources.persona_block.name ?? "—" },
            { label: "ID", value: sources.persona_block.id ?? "—" },
          ],
        )
      : null,
    "persona",
  )

  flowNodes.push(
    makeNode(
      "hardPolicy",
      "hard_policy",
      "Hard policy",
      sources.hard_policy.safety_profile,
      "system",
      { x: 360, y: 260 },
      sources.hard_policy.content,
      "Politique stricte injectée avant le rendu final.",
      [{ label: "Safety profile", value: sources.hard_policy.safety_profile }],
    ),
  )
  flowEdges.push({ from: "hardPolicy", to: "renderedPrompt", label: "contrainte système" })

  flowNodes.push(
    makeNode(
      "assembledPrompt",
      "assembled_prompt",
      "Prompt assemblé",
      toSingleLinePreview(pipeline.assembled_prompt),
      "neutral",
      { x: 760, y: 170 },
      pipeline.assembled_prompt,
      "Chaîne assemblée après composition des couches actives.",
      [
        { label: "Context quality", value: resolvedView.context_quality },
        { label: "Inspection", value: resolvedView.inspection_mode },
      ],
    ),
  )
  flowNodes.push(
    makeNode(
      "postInjectorsPrompt",
      "post_injectors_prompt",
      "Après injecteurs",
      toSingleLinePreview(pipeline.post_injectors_prompt),
      "neutral",
      { x: 1110, y: 170 },
      pipeline.post_injectors_prompt,
      "Prompt après enrichissements et injecteurs runtime.",
      [
        {
          label: "Compensation",
          value: resolvedView.resolved_result.context_compensation_status,
        },
      ],
    ),
  )
  flowNodes.push(
    makeNode(
      "renderedPrompt",
      "rendered_prompt",
      "Prompt rendu final",
      toSingleLinePreview(pipeline.rendered_prompt),
      "system",
      { x: 1460, y: 170 },
      pipeline.rendered_prompt,
      "Dernier prompt rendu avant envoi au fournisseur.",
      [
        {
          label: "Provider",
          value: `${sources.execution_profile.provider} / ${sources.execution_profile.model}`,
        },
      ],
    ),
  )

  flowEdges.push({ from: "assembledPrompt", to: "postInjectorsPrompt", label: "injecteurs" })
  flowEdges.push({ from: "postInjectorsPrompt", to: "renderedPrompt", label: "rendu final" })

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
    ].join("::"),
    fallbackSummary: [
      `Contexte: ${resolvedView.feature}/${resolvedView.subfeature ?? "-"}/${resolvedView.plan ?? "-"}/${resolvedView.locale ?? "-"}`,
      ...sourceTargets.map((nodeId) => `${nodeId} -> assembledPrompt`),
      "assembledPrompt -> postInjectorsPrompt -> renderedPrompt",
      "hardPolicy -> renderedPrompt",
    ],
  }
}
