import { beforeEach, describe, expect, it, vi } from "vitest"
import { render, screen } from "@testing-library/react"

const reactFlowState = vi.hoisted(() => ({
  mountCount: 0,
  unmountCount: 0,
}))

vi.mock("@xyflow/react", async () => {
  const React = await import("react")

  return {
    Background: () => null,
    Controls: () => null,
    MarkerType: { ArrowClosed: "arrow-closed" },
    ReactFlowProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
    useNodesState: (initialNodes: unknown[]) => [initialNodes, vi.fn(), vi.fn()],
    useEdgesState: (initialEdges: unknown[]) => [initialEdges, vi.fn(), vi.fn()],
    ReactFlow: () => {
      React.useEffect(() => {
        reactFlowState.mountCount += 1
        return () => {
          reactFlowState.unmountCount += 1
        }
      }, [])
      return <div data-testid="mock-react-flow-engine">mock react flow</div>
    },
  }
})

import type { LogicGraphProjection } from "../pages/admin/adminPromptsLogicGraphProjection"
import { AdminPromptsLogicGraph } from "../pages/admin/AdminPromptsLogicGraph"

function makeProjection(boundaryRemountKey: string): LogicGraphProjection {
  return {
    dense: false,
    boundaryRemountKey,
    fallbackSummary: [
      "manifest_entry_id: chat:chat_default:premium:fr-FR",
      "composition_sources -> transformation_pipeline -> provider_messages -> résultat opérateur",
    ],
    nodes: [
      {
        id: "manifest",
        title: "manifest_entry_id",
        detail: "chat:chat_default:premium:fr-FR",
        tone: "neutral",
      },
      {
        id: "providerMessages",
        title: "provider_messages",
        detail: "context_quality: not_needed",
        tone: "system",
      },
      {
        id: "operatorResult",
        title: "résultat opérateur",
        detail: "Sortie structurée après fournisseur",
        tone: "neutral",
      },
    ],
    edges: [{ from: "providerMessages", to: "operatorResult", label: "validation / restitution" }],
  }
}

describe("AdminPromptsLogicGraph", () => {
  beforeEach(() => {
    reactFlowState.mountCount = 0
    reactFlowState.unmountCount = 0
    vi.spyOn(console, "error").mockImplementation(() => {})
  })

  it("remonte le sous-arbre React Flow quand la clé change pour le même manifest", () => {
    const projection = makeProjection("chat:chat_default:premium:fr-FR::assembly_preview")

    const { rerender } = render(<AdminPromptsLogicGraph projection={projection} />)

    expect(screen.getByTestId("admin-prompts-logic-graph-visual")).toBeInTheDocument()
    expect(screen.getByTestId("mock-react-flow-engine")).toBeInTheDocument()
    expect(reactFlowState.mountCount).toBe(1)
    expect(reactFlowState.unmountCount).toBe(0)

    rerender(
      <AdminPromptsLogicGraph
        projection={makeProjection("chat:chat_default:premium:fr-FR::runtime_preview::sample-1")}
      />,
    )

    expect(screen.getByTestId("admin-prompts-logic-graph-visual")).toBeInTheDocument()
    expect(screen.getByTestId("mock-react-flow-engine")).toBeInTheDocument()
    expect(reactFlowState.mountCount).toBe(2)
    expect(reactFlowState.unmountCount).toBe(1)
  })
})
