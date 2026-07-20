// Vérifie la règle globale de retour à la ligne des contenus éditoriaux.
import { render } from "@testing-library/react"
import { describe, expect, it } from "vitest"

import { EditorialText } from "./EditorialText"

describe("EditorialText", () => {
  it("ne rend rien lorsque le texte est vide", () => {
    const { container } = render(<EditorialText text="" />)

    expect(container).toBeEmptyDOMElement()
  })

  it("conserve un texte sans deux-points", () => {
    const { container } = render(
      <p>
        <EditorialText text="Une phrase sans rupture." />
      </p>,
    )

    expect(container.querySelectorAll("br")).toHaveLength(0)
    expect(container.textContent).toBe("Une phrase sans rupture.")
  })

  it("ajoute un retour après un deux-points sans modifier le texte", () => {
    const text = "Repère : une explication."
    const { container } = render(
      <p>
        <EditorialText text={text} />
      </p>,
    )

    expect(container.querySelectorAll("br")).toHaveLength(1)
    expect(container.textContent).toBe(text)
  })

  it("ajoute un retour après chacun des deux-points", () => {
    const text = "Premier : détail : conclusion."
    const { container } = render(
      <p>
        <EditorialText text={text} />
      </p>,
    )

    expect(container.querySelectorAll("br")).toHaveLength(2)
    expect(container.textContent).toBe(text)
  })
})
