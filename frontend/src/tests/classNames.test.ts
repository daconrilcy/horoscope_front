import { describe, expect, it } from "vitest"
import { classNames } from "../utils/classNames"

describe("classNames", () => {
  it("joins multiple class names with spaces", () => {
    expect(classNames("a", "b", "c")).toBe("a b c")
  })

  it("filters out false values", () => {
    expect(classNames("a", false, "b")).toBe("a b")
  })

  it("filters out null values", () => {
    expect(classNames("a", null, "b")).toBe("a b")
  })

  it("filters out undefined values", () => {
    expect(classNames("a", undefined, "b")).toBe("a b")
  })

  it("handles conditional class names", () => {
    const isActive = true
    const isDisabled = false
    expect(classNames("btn", isActive && "btn--active", isDisabled && "btn--disabled")).toBe(
      "btn btn--active"
    )
  })

  it("returns empty string for no arguments", () => {
    expect(classNames()).toBe("")
  })

  it("returns empty string for all falsy arguments", () => {
    expect(classNames(false, null, undefined)).toBe("")
  })

  it("handles single class name", () => {
    expect(classNames("single")).toBe("single")
  })

  it("filters out empty strings", () => {
    expect(classNames("a", "", "b")).toBe("a b")
  })

  it("returns empty string when only empty strings provided", () => {
    expect(classNames("", "", "")).toBe("")
  })
})
