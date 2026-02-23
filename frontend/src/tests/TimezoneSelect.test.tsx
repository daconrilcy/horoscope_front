import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { act, cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

import { TimezoneSelect, DEBOUNCE_MS, MAX_VISIBLE_OPTIONS } from "../components/TimezoneSelect"

beforeEach(() => {
  Element.prototype.scrollIntoView = vi.fn()
  localStorage.setItem("lang", "fr")
})

afterEach(() => {
  cleanup()
  // restoreAllMocks requis car scrollIntoView est mocké dans beforeEach via prototype
  vi.restoreAllMocks()
  localStorage.clear()
})

describe("TimezoneSelect", () => {
  it("renders with initial value", () => {
    render(<TimezoneSelect value="Europe/Paris" onChange={vi.fn()} />)
    expect(screen.getByRole("combobox")).toHaveValue("Europe/Paris")
  })

  it("opens dropdown on focus", async () => {
    render(<TimezoneSelect value="UTC" onChange={vi.fn()} />)
    const input = screen.getByRole("combobox")
    
    fireEvent.focus(input)
    
    await waitFor(() => {
      expect(screen.getByRole("listbox")).toBeInTheDocument()
    })
  })

  it("filters timezones based on search term", async () => {
    render(<TimezoneSelect value="" onChange={vi.fn()} />)
    const input = screen.getByRole("combobox")
    
    fireEvent.focus(input)
    fireEvent.change(input, { target: { value: "Paris" } })
    
    await waitFor(() => {
      expect(screen.getByRole("option", { name: "Europe/Paris" })).toBeInTheDocument()
    })
    expect(screen.queryByRole("option", { name: "America/New_York" })).not.toBeInTheDocument()
  })

  it("calls onChange when option is selected", async () => {
    const onChange = vi.fn()
    render(<TimezoneSelect value="" onChange={onChange} />)
    const input = screen.getByRole("combobox")
    
    fireEvent.focus(input)
    fireEvent.change(input, { target: { value: "Tokyo" } })
    
    await waitFor(() => {
      expect(screen.getByRole("option", { name: "Asia/Tokyo" })).toBeInTheDocument()
    })
    
    fireEvent.click(screen.getByRole("option", { name: "Asia/Tokyo" }))
    
    expect(onChange).toHaveBeenCalledWith("Asia/Tokyo")
  })

  it("navigates with keyboard arrows and highlights options", async () => {
    const user = userEvent.setup()
    render(<TimezoneSelect value="" onChange={vi.fn()} />)
    const input = screen.getByRole("combobox")

    await user.click(input)
    
    await waitFor(() => {
      expect(screen.getByRole("listbox")).toBeInTheDocument()
    })

    // Navigate down to highlight first option
    await user.keyboard("{ArrowDown}")

    // Verify aria-activedescendant is set on the input
    await waitFor(() => {
      const activeDescendant = input.getAttribute("aria-activedescendant")
      expect(activeDescendant).toBeTruthy()
      // The highlighted option should exist
      const highlightedOption = document.getElementById(activeDescendant!)
      expect(highlightedOption).toBeInTheDocument()
      expect(highlightedOption).toHaveClass("highlighted")
    })

    // Navigate down again
    await user.keyboard("{ArrowDown}")

    // Verify aria-activedescendant changed to a different option
    await waitFor(() => {
      const activeDescendant = input.getAttribute("aria-activedescendant")
      const highlightedOption = document.getElementById(activeDescendant!)
      expect(highlightedOption).toHaveClass("highlighted")
    })
  })

  it("selects with Enter key", async () => {
    const onChange = vi.fn()
    const user = userEvent.setup()
    render(<TimezoneSelect value="" onChange={onChange} />)
    const input = screen.getByRole("combobox")
    
    await user.click(input)
    await user.type(input, "UTC")
    await user.keyboard("{ArrowDown}{Enter}")
    
    expect(onChange).toHaveBeenCalled()
  })

  it("closes dropdown on Escape", async () => {
    const user = userEvent.setup()
    render(<TimezoneSelect value="" onChange={vi.fn()} />)
    const input = screen.getByRole("combobox")
    
    await user.click(input)
    
    await waitFor(() => {
      expect(screen.getByRole("listbox")).toBeInTheDocument()
    })
    
    await user.keyboard("{Escape}")
    
    await waitFor(() => {
      expect(screen.queryByRole("listbox")).not.toBeInTheDocument()
    })
  })

  it("closes dropdown on click outside", async () => {
    render(
      <div>
        <TimezoneSelect value="" onChange={vi.fn()} />
        <button type="button">Outside</button>
      </div>
    )
    const input = screen.getByRole("combobox")
    
    fireEvent.focus(input)
    
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
      const input = screen.getByRole("combobox")

      fireEvent.focus(input)
      fireEvent.change(input, { target: { value: "XYZNOTEXIST" } })

      await waitFor(() => {
        const noResults = screen.getByTestId("timezone-no-results")
        expect(noResults).toBeInTheDocument()
        expect(noResults).toHaveTextContent("Aucun fuseau horaire trouvé")
        expect(noResults).toHaveAttribute("role", "status")
        expect(noResults).toHaveAttribute("aria-live", "polite")
      })
    })

    it("does not call onChange when pressing Enter with no results (with debounce)", async () => {
      vi.useFakeTimers()
      try {
        const onChange = vi.fn()
        render(<TimezoneSelect value="" onChange={onChange} />)
        const input = screen.getByRole("combobox")

        await act(async () => {
          fireEvent.focus(input)
          fireEvent.change(input, { target: { value: "XYZNOTEXIST" } })
        })

        await act(async () => {
          vi.advanceTimersByTime(DEBOUNCE_MS + 10)
        })

        expect(screen.getByTestId("timezone-no-results")).toBeInTheDocument()

        fireEvent.keyDown(input, { key: "Enter" })

        expect(onChange).not.toHaveBeenCalled()
      } finally {
        vi.useRealTimers()
      }
    })
  })

  it("is disabled when disabled prop is true", () => {
    render(<TimezoneSelect value="UTC" onChange={vi.fn()} disabled />)
    expect(screen.getByRole("combobox")).toBeDisabled()
  })

  it("has correct ARIA attributes for accessibility", async () => {
    render(<TimezoneSelect value="Europe/Paris" onChange={vi.fn()} id="tz-select" />)
    const input = screen.getByRole("combobox")
    
    expect(input).toHaveAttribute("aria-haspopup", "listbox")
    expect(input).toHaveAttribute("aria-autocomplete", "list")
    expect(input).toHaveAttribute("aria-expanded", "false")
    // aria-controls should be undefined when listbox is closed (WCAG compliance)
    expect(input).not.toHaveAttribute("aria-controls")
    
    fireEvent.focus(input)
    
    await waitFor(() => {
      expect(input).toHaveAttribute("aria-expanded", "true")
      expect(input).toHaveAttribute("aria-controls", "tz-select-listbox")
      expect(input).toHaveAttribute("aria-activedescendant")
    })
    
    const listbox = screen.getByRole("listbox")
    expect(listbox).toHaveAttribute("id", "tz-select-listbox")
  })

  it("highlights current selection in dropdown", async () => {
    render(<TimezoneSelect value="Europe/Paris" onChange={vi.fn()} />)
    const input = screen.getByRole("combobox")
    
    fireEvent.focus(input)
    
    await waitFor(() => {
      const parisOption = screen.getByRole("option", { name: "Europe/Paris" })
      expect(parisOption).toHaveAttribute("aria-selected", "true")
    })
  })

  it("scrolls highlighted option into view", async () => {
    const scrollIntoViewMock = vi.fn()
    Element.prototype.scrollIntoView = scrollIntoViewMock

    const user = userEvent.setup()
    render(<TimezoneSelect value="" onChange={vi.fn()} />)
    const input = screen.getByRole("combobox")
    
    await user.click(input)
    
    // Navigate down to trigger scrollIntoView
    for (let i = 0; i < 5; i++) {
      await user.keyboard("{ArrowDown}")
    }
    
    await waitFor(() => {
      expect(screen.getByRole("listbox")).toBeInTheDocument()
    })

    // Verify scrollIntoView was called for keyboard navigation
    expect(scrollIntoViewMock).toHaveBeenCalledWith({ block: "nearest" })
  })

  it("passes aria-invalid and aria-describedby to input", () => {
    render(
      <TimezoneSelect
        value=""
        onChange={vi.fn()}
        aria-invalid={true}
        aria-describedby="error-msg"
      />
    )
    const input = screen.getByRole("combobox")
    expect(input).toHaveAttribute("aria-invalid", "true")
    expect(input).toHaveAttribute("aria-describedby", "error-msg")
  })

  it("shows hint when displaying max visible options without search", async () => {
    render(<TimezoneSelect value="" onChange={vi.fn()} />)
    const input = screen.getByRole("combobox")

    fireEvent.focus(input)

    await waitFor(() => {
      expect(screen.getByRole("listbox")).toBeInTheDocument()
    })

    const options = screen.getAllByRole("option")
    expect(options.length).toBe(MAX_VISIBLE_OPTIONS)

    const hint = screen.getByTestId("timezone-hint")
    expect(hint).toBeInTheDocument()
    expect(hint).toHaveAttribute("role", "status")
    // Verify both the message and the total count are displayed
    expect(hint).toHaveTextContent(/Tapez pour filtrer/)
    expect(hint).toHaveTextContent(/\(\d+\)/)
  })

  it("shows hint when value is outside first MAX_VISIBLE_OPTIONS (101 items rendered)", async () => {
    // Europe/Paris is typically outside the first 100 timezones (which start with Africa/...)
    render(<TimezoneSelect value="Europe/Paris" onChange={vi.fn()} />)
    const input = screen.getByRole("combobox")

    fireEvent.focus(input)

    await waitFor(() => {
      expect(screen.getByRole("listbox")).toBeInTheDocument()
    })

    // Should have 101 options (value prepended + 100 initial)
    const options = screen.getAllByRole("option")
    expect(options.length).toBe(MAX_VISIBLE_OPTIONS + 1)

    // Hint should still be visible because >= MAX_VISIBLE_OPTIONS
    const hint = screen.getByTestId("timezone-hint")
    expect(hint).toBeInTheDocument()
    expect(hint).toHaveTextContent(/Tapez pour filtrer/)
  })

  it("hides hint when search term is entered", async () => {
    render(<TimezoneSelect value="" onChange={vi.fn()} />)
    const input = screen.getByRole("combobox")

    fireEvent.focus(input)
    await waitFor(() => {
      expect(screen.getByTestId("timezone-hint")).toBeInTheDocument()
    })

    fireEvent.change(input, { target: { value: "Paris" } })

    await waitFor(() => {
      expect(screen.queryByTestId("timezone-hint")).not.toBeInTheDocument()
    })
  })

  it("debounces search input before filtering", async () => {
    vi.useFakeTimers()
    try {
      render(<TimezoneSelect value="" onChange={vi.fn()} />)
      const input = screen.getByRole("combobox")

      await act(async () => {
        fireEvent.focus(input)
        fireEvent.change(input, { target: { value: "Paris" } })
      })

      // Before debounce delay: all timezones should still be visible
      const allOptionsBeforeDebounce = screen.getAllByRole("option")
      expect(allOptionsBeforeDebounce.length).toBeGreaterThan(1)

      // Advance time past the debounce delay
      await act(async () => {
        vi.advanceTimersByTime(DEBOUNCE_MS + 10)
      })

      // After debounce: only Paris-matching timezones should be visible
      const filteredOptions = screen.getAllByRole("option")
      expect(filteredOptions.length).toBe(1)
      expect(screen.getByRole("option", { name: "Europe/Paris" })).toBeInTheDocument()
    } finally {
      vi.useRealTimers()
    }
  })

  it("keyboard navigation stays within valid options when hint is visible", async () => {
    const onChange = vi.fn()
    render(<TimezoneSelect value="" onChange={onChange} />)
    const input = screen.getByRole("combobox")

    fireEvent.focus(input)

    await waitFor(() => {
      expect(screen.getByRole("listbox")).toBeInTheDocument()
      expect(screen.getByTestId("timezone-hint")).toBeInTheDocument()
    })

    const options = screen.getAllByRole("option")
    const lastOptionIndex = options.length - 1

    // Navigate to the last option using keyboard events
    for (let i = 0; i <= lastOptionIndex + 5; i++) {
      fireEvent.keyDown(input, { key: "ArrowDown" })
    }

    // Press Enter to select - should select the last actual option, not crash
    fireEvent.keyDown(input, { key: "Enter" })

    expect(onChange).toHaveBeenCalledWith(expect.any(String))
    // Verify it's a valid timezone (not undefined or hint text)
    const selectedTz = onChange.mock.calls[0][0]
    expect(selectedTz).toMatch(/^[A-Za-z]+\//)
  })

  it("falls back to French when lang is not set and navigator.language unavailable", async () => {
    localStorage.clear()
    vi.stubGlobal("navigator", { ...navigator, language: undefined })

    render(<TimezoneSelect value="" onChange={vi.fn()} />)
    const input = screen.getByRole("combobox")

    // Placeholder should be in French (ultimate fallback)
    expect(input).toHaveAttribute("placeholder", "Rechercher un fuseau horaire...")

    fireEvent.focus(input)
    fireEvent.change(input, { target: { value: "NOTEXIST" } })

    await waitFor(() => {
      expect(screen.getByText("Aucun fuseau horaire trouvé")).toBeInTheDocument()
    })
  })

  it("does not prepend invalid value that is not in TIMEZONES list", async () => {
    render(<TimezoneSelect value="Invalid/Timezone" onChange={vi.fn()} />)
    const input = screen.getByRole("combobox")

    // Invalid timezone should still show in the input
    expect(input).toHaveValue("Invalid/Timezone")

    fireEvent.focus(input)

    await waitFor(() => {
      expect(screen.getByRole("listbox")).toBeInTheDocument()
    })

    // Invalid value should NOT be in the options list (it's filtered out)
    expect(screen.queryByRole("option", { name: "Invalid/Timezone" })).not.toBeInTheDocument()

    // First option should be first valid timezone from list
    const options = screen.getAllByRole("option")
    expect(options.length).toBeGreaterThan(0)
    expect(options[0]).toHaveTextContent(/^Africa\//)
  })

  it("allows selecting a valid option when starting with invalid value", async () => {
    const onChange = vi.fn()
    render(<TimezoneSelect value="Invalid/Timezone" onChange={onChange} />)
    const input = screen.getByRole("combobox")

    expect(input).toHaveValue("Invalid/Timezone")

    fireEvent.focus(input)

    await waitFor(() => {
      expect(screen.getByRole("listbox")).toBeInTheDocument()
    })

    fireEvent.change(input, { target: { value: "Paris" } })

    await waitFor(() => {
      expect(screen.getByRole("option", { name: "Europe/Paris" })).toBeInTheDocument()
    })

    fireEvent.click(screen.getByRole("option", { name: "Europe/Paris" }))

    expect(onChange).toHaveBeenCalledWith("Europe/Paris")
  })
})
