import { Component, type ErrorInfo, type ReactNode, useEffect, useMemo } from "react"
import {
  Background,
  Controls,
  Handle,
  MarkerType,
  Position,
  ReactFlow,
  ReactFlowProvider,
  useEdgesState,
  useNodesState,
  type Edge,
  type Node,
  type NodeProps,
  type NodeTypes,
} from "@xyflow/react"

import "@xyflow/react/dist/style.css"

import type { LogicGraphNodeTone, LogicGraphProjection } from "./adminPromptsLogicGraphProjection"
import { layoutLogicGraphNodesForFlow } from "./adminPromptsLogicGraphProjection"

type LogicFlowNodeData = Record<string, unknown> & {
  title: string
  detail: string
  tone: LogicGraphNodeTone
  badge?: string
  interactive: boolean
}

type LogicRfNode = Node<LogicFlowNodeData, "logic">

function LogicGraphFlowNode(props: NodeProps<LogicRfNode>) {
  const { data } = props
  const className = `admin-prompts-logic-graph__node admin-prompts-logic-graph__node--${data.tone}${data.interactive ? " admin-prompts-logic-graph__node--interactive" : ""}`
  return (
    <div className={className}>
      <Handle type="target" position={Position.Left} />
      {data.badge ? <span className="admin-prompts-logic-graph__node-badge">{data.badge}</span> : null}
      <strong>{data.title}</strong>
      <Handle type="source" position={Position.Right} />
    </div>
  )
}

const nodeTypes: NodeTypes = {
  logic: LogicGraphFlowNode,
}

function projectionToFlow(
  projection: LogicGraphProjection,
  onNodeSelect?: ((nodeId: string) => void) | undefined,
): { nodes: Node[]; edges: Edge[] } {
  const pos = layoutLogicGraphNodesForFlow(projection.nodes)
  const nodes: Node[] = projection.nodes.map((n) => ({
    id: n.id,
    type: "logic",
    position: pos[n.id] ?? { x: 0, y: 0 },
    data: {
      title: n.title,
      detail: n.detail,
      tone: n.tone,
      badge: n.badge,
      interactive: Boolean(n.interactive && onNodeSelect),
    },
    selectable: false,
  }))
  const edges: Edge[] = projection.edges.map((e, index) => ({
    id: `lg-${e.from}-${e.to}-${index}`,
    source: e.from,
    target: e.to,
    label: e.label,
    markerEnd: { type: MarkerType.ArrowClosed, width: 18, height: 18 },
  }))
  return { nodes, edges }
}

function LogicGraphFlowInner({
  projection,
  onNodeSelect,
}: {
  projection: LogicGraphProjection
  onNodeSelect?: ((nodeId: string) => void) | undefined
}) {
  const initialFlow = useMemo(
    () => projectionToFlow(projection, onNodeSelect),
    [onNodeSelect, projection],
  )
  const [nodes, setNodes, onNodesChange] = useNodesState(initialFlow.nodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialFlow.edges)

  useEffect(() => {
    setNodes(initialFlow.nodes)
  }, [initialFlow.nodes, setNodes])

  useEffect(() => {
    setEdges(initialFlow.edges)
  }, [initialFlow.edges, setEdges])

  return (
    <div
      className="admin-prompts-logic-graph__rf-canvas"
      data-testid="admin-prompts-logic-graph-visual"
      role="img"
      aria-label="Schéma logique interactif de la chaîne LLM"
    >
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        nodesConnectable={false}
        nodesDraggable
        elementsSelectable={false}
        selectionOnDrag={false}
        panOnDrag
        panOnScroll
        zoomOnScroll
        zoomOnPinch
        minZoom={0.35}
        maxZoom={1.25}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        onNodeClick={onNodeSelect ? (_event, node) => onNodeSelect(node.id) : undefined}
        // MIT @xyflow/react : masquage pastille d’attribution en UI admin (décision produit revue 70-4).
        proOptions={{ hideAttribution: true }}
      >
        <Background gap={20} />
        <Controls showInteractive={false} />
      </ReactFlow>
    </div>
  )
}

type LogicGraphErrorBoundaryProps = {
  children: ReactNode
  fallbackSummary: string[]
}

type LogicGraphErrorBoundaryState = { hasError: boolean }

class LogicGraphErrorBoundary extends Component<LogicGraphErrorBoundaryProps, LogicGraphErrorBoundaryState> {
  constructor(props: LogicGraphErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(): LogicGraphErrorBoundaryState {
    return { hasError: true }
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    if (import.meta.env.DEV) {
      console.error("AdminPromptsLogicGraph: échec rendu React Flow", error, info.componentStack)
    }
  }

  render(): ReactNode {
    if (this.state.hasError) {
      return (
        <div
          className="admin-prompts-logic-graph__fallback admin-prompts-logic-graph__fallback--error"
          role="region"
          aria-live="polite"
          aria-label="Échec du rendu du schéma visuel, vue texte de secours"
        >
          <p className="text-muted">
            Le schéma visuel n’a pas pu être affiché. Voici la chaîne en vue texte (aucune information critique
            retirée).
          </p>
          <ul>
            {this.props.fallbackSummary.map((line) => (
              <li key={line}>{line}</li>
            ))}
          </ul>
        </div>
      )
    }
    return this.props.children
  }
}

function LogicGraphTextEdgesOnly({ projection }: { projection: LogicGraphProjection }) {
  return (
    <ul className="admin-prompts-logic-graph__edges" aria-label="Connexions du graphe (vue texte)">
      {projection.edges.map((edge) => (
        <li key={`${edge.from}-${edge.to}-${edge.label}`}>
          <code>{edge.from}</code> → <code>{edge.to}</code> · {edge.label}
        </li>
      ))}
    </ul>
  )
}

/** En mode dense, reprend les libellés métier des nœuds (profils, templates, politique) — AC3, sans dupliquer la logique de projection. */
function LogicGraphDenseNodeDetails({ projection }: { projection: LogicGraphProjection }) {
  return (
    <details className="admin-prompts-logic-graph__dense-node-details" open>
      <summary>Détail des nœuds (données opérateur)</summary>
      <p className="text-muted admin-prompts-logic-graph__dense-node-details-lead">
        Résumé global ci-dessus ; chaque couche conserve ses identifiants et paramètres utiles au diagnostic.
      </p>
      <div className="admin-prompts-logic-graph__nodes" aria-label="Nœuds du graphe logique (mode dense)">
        {projection.nodes.map((node) => (
          <article
            key={node.id}
            className={`admin-prompts-logic-graph__node admin-prompts-logic-graph__node--${node.tone}`}
          >
            {node.badge ? <span className="admin-prompts-logic-graph__node-badge">{node.badge}</span> : null}
            <strong>{node.title}</strong>
          </article>
        ))}
      </div>
    </details>
  )
}

export type AdminPromptsLogicGraphProps = {
  projection: LogicGraphProjection | null
  onNodeSelect?: ((nodeId: string) => void) | undefined
}

export function AdminPromptsLogicGraph({ projection, onNodeSelect }: AdminPromptsLogicGraphProps) {
  if (!projection) {
    return null
  }

  if (projection.dense) {
    return (
      <div className="admin-prompts-logic-graph admin-prompts-logic-graph--in-zone">
        <div className="admin-prompts-logic-graph__legend" aria-label="Légende du graphe">
          <span className="admin-prompts-logic-graph__legend-chip admin-prompts-logic-graph__legend-chip--layer">
            Couches / templates
          </span>
          <span className="admin-prompts-logic-graph__legend-chip admin-prompts-logic-graph__legend-chip--system">
            Données système
          </span>
          <span className="admin-prompts-logic-graph__legend-chip admin-prompts-logic-graph__legend-chip--fallback">
            Fallback registre
          </span>
          <span className="admin-prompts-logic-graph__legend-chip admin-prompts-logic-graph__legend-chip--sample">
            Sample payload
          </span>
        </div>
        <div className="admin-prompts-logic-graph__fallback" aria-live="polite">
          <p className="text-muted">
            Graphe simplifié en vue texte : la densité des placeholders dépasse le seuil de lisibilité du schéma
            visuel.
          </p>
          <ul>
            {projection.fallbackSummary.map((line) => (
              <li key={line}>{line}</li>
            ))}
          </ul>
        </div>
        <LogicGraphDenseNodeDetails projection={projection} />
      </div>
    )
  }

  return (
    <div className="admin-prompts-logic-graph admin-prompts-logic-graph--in-zone">
      <div className="admin-prompts-logic-graph__legend" aria-label="Légende du graphe">
        <span className="admin-prompts-logic-graph__legend-chip admin-prompts-logic-graph__legend-chip--layer">
          Couches / templates
        </span>
        <span className="admin-prompts-logic-graph__legend-chip admin-prompts-logic-graph__legend-chip--system">
          Données système
        </span>
        <span className="admin-prompts-logic-graph__legend-chip admin-prompts-logic-graph__legend-chip--fallback">
          Fallback registre
        </span>
        <span className="admin-prompts-logic-graph__legend-chip admin-prompts-logic-graph__legend-chip--sample">
          Sample payload
        </span>
      </div>
      <details className="admin-prompts-logic-graph__text-fallback-details">
        <summary>Connexions en vue liste (accessibilité & secours)</summary>
        <p className="text-muted admin-prompts-logic-graph__text-fallback-lead">
          Les nœuds sont affichés dans le schéma ci-dessus ; cette liste reprend uniquement les liaisons, sans dupliquer
          les libellés.
        </p>
        <LogicGraphTextEdgesOnly projection={projection} />
      </details>
      <LogicGraphErrorBoundary key={projection.boundaryRemountKey} fallbackSummary={projection.fallbackSummary}>
        <ReactFlowProvider>
          <LogicGraphFlowInner projection={projection} onNodeSelect={onNodeSelect} />
        </ReactFlowProvider>
      </LogicGraphErrorBoundary>
    </div>
  )
}
