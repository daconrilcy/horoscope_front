import { beforeEach, describe, expect, it, vi } from "vitest"
import { render, screen } from "@testing-library/react"

const reactFlowState = vi.hoisted(() => ({
  shouldThrow: false,
}))

vi.mock("@xyflow/react", async () => {
  const React = await import("react")

  return {
    Background: () => null,
    Controls: () => null,
    MarkerType: { ArrowClosed: "arrow-closed" },
    ReactFlowProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
    ReactFlow: () => {
      if (reactFlowState.shouldThrow) {
        throw new Error("react-flow-render-failure")
      }
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
    reactFlowState.shouldThrow = false
    vi.spyOn(console, "error").mockImplementation(() => {})
  })

  it("remonte l'Error Boundary quand la clé change pour le même manifest", () => {
    const projection = makeProjection("chat:chat_default:premium:fr-FR::assembly_preview")
    reactFlowState.shouldThrow = true

    const { rerender } = render(<AdminPromptsLogicGraph projection={projection} />)

    expect(screen.getByText(/Le schéma visuel n’a pas pu être affiché/)).toBeInTheDocument()
    expect(screen.queryByTestId("admin-prompts-logic-graph-visual")).toBeNull()

    reactFlowState.shouldThrow = false
    rerender(
      <AdminPromptsLogicGraph
        projection={makeProjection("chat:chat_default:premium:fr-FR::runtime_preview::sample-1")}
      />,
    )

    expect(screen.queryByText(/Le schéma visuel n’a pas pu être affiché/)).toBeNull()
    expect(screen.getByTestId("admin-prompts-logic-graph-visual")).toBeInTheDocument()
    expect(screen.getByTestId("mock-react-flow-engine")).toBeInTheDocument()
  })
})
