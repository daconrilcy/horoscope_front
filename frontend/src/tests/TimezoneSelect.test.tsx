import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react"

import { TimezoneSelect } from "../components/TimezoneSelect"

beforeEach(() => {
  Element.prototype.scrollIntoView = vi.fn()
  localStorage.setItem("lang", "fr")
})

afterEach(() => {
  cleanup()
  vi.restoreAllMocks()
  localStorage.clear()
})

describe("TimezoneSelect", () => {
  it("renders with initial value", () => {
    render(<TimezoneSelect value="Europe/Paris" onChange={vi.fn()} />)
    const trigger = screen.getByRole("button")
    expect(trigger).toHaveTextContent("Europe/Paris")
  })

  it("opens dropdown on click", async () => {
    render(<TimezoneSelect value="UTC" onChange={vi.fn()} />)
    const trigger = screen.getByRole("button")

    fireEvent.click(trigger)

    await waitFor(() => {
      expect(screen.getByRole("listbox")).toBeInTheDocument()
    })
  })

  it("filters timezones based on search term", async () => {
    render(<TimezoneSelect value="" onChange={vi.fn()} />)

    fireEvent.click(screen.getByRole("button"))

    await waitFor(() => {
      expect(screen.getByRole("listbox")).toBeInTheDocument()
    })

    const searchInput = screen.getByPlaceholderText(/rechercher/i)
    fireEvent.change(searchInput, { target: { value: "Paris" } })

    await waitFor(() => {
      expect(screen.getByRole("option", { name: "Europe/Paris" })).toBeInTheDocument()
    })
    expect(screen.queryByRole("option", { name: "America/New_York" })).not.toBeInTheDocument()
  })

  it("calls onChange when option is selected", async () => {
    const onChange = vi.fn()
    render(<TimezoneSelect value="" onChange={onChange} />)

    fireEvent.click(screen.getByRole("button"))

    const searchInput = await screen.findByPlaceholderText(/rechercher/i)
    fireEvent.change(searchInput, { target: { value: "Tokyo" } })

    await waitFor(() => {
      expect(screen.getByRole("option", { name: "Asia/Tokyo" })).toBeInTheDocument()
    })

    fireEvent.click(screen.getByRole("option", { name: "Asia/Tokyo" }))

    expect(onChange).toHaveBeenCalledWith("Asia/Tokyo")
  })

  it("navigates with keyboard arrows and highlights options", async () => {
    const { container } = render(<TimezoneSelect value="" onChange={vi.fn()} />)

    fireEvent.click(screen.getByRole("button"))

    await waitFor(() => {
      expect(screen.getByRole("listbox")).toBeInTheDocument()
    })

    const selectContainer = container.firstChild as HTMLElement
    fireEvent.keyDown(selectContainer, { key: "ArrowDown" })

    await waitFor(() => {
      const options = screen.getAllByRole("option")
      expect(options.length).toBeGreaterThan(0)
    })
  })

  it("selects with Enter key", async () => {
    const onChange = vi.fn()
    const { container } = render(<TimezoneSelect value="" onChange={onChange} />)

    fireEvent.click(screen.getByRole("button"))

    await waitFor(() => {
      expect(screen.getByRole("listbox")).toBeInTheDocument()
    })

    const searchInput = screen.getByPlaceholderText(/rechercher/i)
    fireEvent.change(searchInput, { target: { value: "UTC" } })

    await waitFor(() => {
      const options = screen.getAllByRole("option")
      expect(options.length).toBeGreaterThan(0)
    })

    const selectContainer = container.firstChild as HTMLElement
    fireEvent.keyDown(selectContainer, { key: "ArrowDown" })
    fireEvent.keyDown(selectContainer, { key: "Enter" })

    expect(onChange).toHaveBeenCalled()
  })

  it("closes dropdown on Escape", async () => {
    const { container } = render(<TimezoneSelect value="" onChange={vi.fn()} />)

    fireEvent.click(screen.getByRole("button"))

    await waitFor(() => {
      expect(screen.getByRole("listbox")).toBeInTheDocument()
    })

    const selectContainer = container.firstChild as HTMLElement
    fireEvent.keyDown(selectContainer, { key: "Escape" })

    await waitFor(() => {
      expect(screen.queryByRole("listbox")).not.toBeInTheDocument()
    })
  })

  it("closes dropdown on click outside", async () => {
    render(
      <div>
        <TimezoneSelect value="" onChange={vi.fn()} />
        <button type="button">Outside</button>
      </div>,
    )

    const trigger = screen.getAllByRole("button")[0]
    fireEvent.click(trigger)

    await waitFor(() => {
      expect(screen.getByRole("listbox")).toBeInTheDocument()
    })

    fireEvent.mouseDown(screen.getByRole("button", { name: "Outside" }))

    await waitFor(() => {
      expect(screen.queryByRole("listbox")).not.toBeInTheDocument()
    })
  })

  describe("no results behavior", () => {
    it("shows 'no results' message when search finds nothing", async () => {
      render(<TimezoneSelect value="" onChange={vi.fn()} />)

      fireEvent.click(screen.getByRole("button"))

      await waitFor(() => {
        expect(screen.getByRole("listbox")).toBeInTheDocument()
      })

      const searchInput = screen.getByPlaceholderText(/rechercher/i)
      fireEvent.change(searchInput, { target: { value: "XYZNOTEXIST" } })

      await waitFor(() => {
        expect(screen.getByText(/aucun résultat trouvé/i)).toBeInTheDocument()
      })
    })

    it("does not call onChange when pressing Enter with no results", async () => {
      const onChange = vi.fn()
      const { container } = render(<TimezoneSelect value="" onChange={onChange} />)

      fireEvent.click(screen.getByRole("button"))

      await waitFor(() => {
        expect(screen.getByRole("listbox")).toBeInTheDocument()
      })

      const searchInput = screen.getByPlaceholderText(/rechercher/i)
      fireEvent.change(searchInput, { target: { value: "XYZNOTEXIST" } })

      await waitFor(() => {
        expect(screen.getByText(/aucun résultat trouvé/i)).toBeInTheDocument()
      })

      const selectContainer = container.firstChild as HTMLElement
      fireEvent.keyDown(selectContainer, { key: "Enter" })

      expect(onChange).not.toHaveBeenCalled()
    })
  })

  it("is disabled when disabled prop is true", () => {
    render(<TimezoneSelect value="UTC" onChange={vi.fn()} disabled />)
    expect(screen.getByRole("button")).toBeDisabled()
  })

  it("has correct ARIA attributes for accessibility", async () => {
    render(<TimezoneSelect value="Europe/Paris" onChange={vi.fn()} id="tz-select" />)
    const trigger = screen.getByRole("button")

    expect(trigger).toHaveAttribute("aria-haspopup", "listbox")
    expect(trigger).toHaveAttribute("aria-expanded", "false")

    fireEvent.click(trigger)

    await waitFor(() => {
      expect(trigger).toHaveAttribute("aria-expanded", "true")
    })

    const listbox = screen.getByRole("listbox")
    expect(listbox).toBeInTheDocument()
  })

  it("highlights current selection in dropdown", async () => {
    render(<TimezoneSelect value="Europe/Paris" onChange={vi.fn()} />)

    fireEvent.click(screen.getByRole("button"))

    await waitFor(() => {
      expect(screen.getByPlaceholderText(/rechercher/i)).toBeInTheDocument()
    })

    const searchInput = screen.getByPlaceholderText(/rechercher/i)
    fireEvent.change(searchInput, { target: { value: "Paris" } })

    await waitFor(() => {
      const parisOption = screen.getByRole("option", { name: "Europe/Paris" })
      expect(parisOption).toHaveAttribute("aria-selected", "true")
    })
  })

  it("scrolls highlighted option into view", async () => {
    const scrollIntoViewMock = vi.fn()
    Element.prototype.scrollIntoView = scrollIntoViewMock

    const { container } = render(<TimezoneSelect value="" onChange={vi.fn()} />)

    fireEvent.click(screen.getByRole("button"))

    await waitFor(() => {
      expect(screen.getByRole("listbox")).toBeInTheDocument()
    })

    const selectContainer = container.firstChild as HTMLElement
    for (let i = 0; i < 5; i++) {
      fireEvent.keyDown(selectContainer, { key: "ArrowDown" })
    }

    await waitFor(() => {
      expect(scrollIntoViewMock).toHaveBeenCalledWith({ block: "nearest" })
    })
  })

  it("passes aria-invalid to trigger when provided", () => {
    render(
      <TimezoneSelect
        value=""
        onChange={vi.fn()}
        aria-invalid={true}
      />,
    )
    const trigger = screen.getByRole("button")
    expect(trigger).toHaveAttribute("aria-invalid", "true")
  })

  it("allows selecting a valid option", async () => {
    const onChange = vi.fn()
    render(<TimezoneSelect value="Europe/Paris" onChange={onChange} />)

    const trigger = screen.getByRole("button")
    expect(trigger).toHaveTextContent("Europe/Paris")

    fireEvent.click(trigger)

    await waitFor(() => {
      expect(screen.getByRole("listbox")).toBeInTheDocument()
    })

    const searchInput = screen.getByPlaceholderText(/rechercher/i)
    fireEvent.change(searchInput, { target: { value: "Tokyo" } })

    await waitFor(() => {
      expect(screen.getByRole("option", { name: "Asia/Tokyo" })).toBeInTheDocument()
    })

    fireEvent.click(screen.getByRole("option", { name: "Asia/Tokyo" }))
    expect(onChange).toHaveBeenCalledWith("Asia/Tokyo")
  })
})
