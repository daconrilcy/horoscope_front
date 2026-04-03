import { describe, expect, it, vi } from "vitest"
import { render, screen, fireEvent } from "@testing-library/react"
import { FaqSection } from "../pages/landing/sections/FaqSection"
import { MemoryRouter } from "react-router-dom"

// Mock translations
vi.mock("../i18n", () => ({
  useTranslation: () => ({
    faq: {
      title: "Frequently Asked Questions",
      items: [
        { q: "Question 1", a: "Answer 1" },
        { q: "Question 2", a: "Answer 2" },
      ]
    },
    finalCta: {
      title: "Final CTA",
      subtitle: "Subtitle",
      button: "Start",
      micro1: "Micro 1",
      micro2: "Micro 2",
    }
  })
}))

describe("FaqSection", () => {
  it("renders all FAQ items with correct ARIA attributes", () => {
    render(
      <MemoryRouter>
        <FaqSection />
      </MemoryRouter>
    )

    const q1 = screen.getByText("Question 1")
    const q2 = screen.getByText("Question 2")

    expect(q1.closest('summary')).toHaveAttribute("aria-expanded", "false")
    expect(q2.closest('summary')).toHaveAttribute("aria-expanded", "false")
  })

  it("updates aria-expanded when an item is toggled", async () => {
    render(
      <MemoryRouter>
        <FaqSection />
      </MemoryRouter>
    )

    const q1 = screen.getByText("Question 1")
    const summary1 = q1.closest('summary')!

    // In our implementation, we use onToggle on <details>
    const details1 = summary1.closest('details')!
    
    // Simulate opening the details element
    // Manually set 'open' then fire 'toggle' event
    details1.open = true
    fireEvent(details1, new Event('toggle'))
    
    expect(summary1).toHaveAttribute("aria-expanded", "true")
    
    // Toggle again to close
    details1.open = false
    fireEvent(details1, new Event('toggle'))
    expect(summary1).toHaveAttribute("aria-expanded", "false")
  })

  it("maintains exclusive accordion behavior (one open at a time)", () => {
    render(
      <MemoryRouter>
        <FaqSection />
      </MemoryRouter>
    )

    const q1 = screen.getByText("Question 1").closest('summary')!
    const details1 = q1.closest('details')!
    const q2 = screen.getByText("Question 2").closest('summary')!
    const details2 = q2.closest('details')!

    details1.open = true
    fireEvent(details1, new Event('toggle'))
    expect(q1).toHaveAttribute("aria-expanded", "true")
    expect(q2).toHaveAttribute("aria-expanded", "false")

    details2.open = true
    fireEvent(details2, new Event('toggle'))
    expect(q1).toHaveAttribute("aria-expanded", "false")
    expect(q2).toHaveAttribute("aria-expanded", "true")
  })
})
