import { describe, it, expect } from "vitest"
import { navItems, type NavItem } from "../ui/nav"

describe("ui/nav configuration", () => {
  it("exports navItems array with 15 entries", () => {
    expect(navItems).toBeDefined()
    expect(Array.isArray(navItems)).toBe(true)
    expect(navItems).toHaveLength(15)
  })

  it("each navItem has required properties", () => {
    navItems.forEach((item: NavItem) => {
      expect(item).toHaveProperty("key")
      expect(item).toHaveProperty("label")
      expect(item).toHaveProperty("icon")
      expect(item).toHaveProperty("path")
      expect(typeof item.key).toBe("string")
      expect(typeof item.label).toBe("string")
      expect(typeof item.icon === "function" || typeof item.icon === "object").toBe(true)
      expect(typeof item.path).toBe("string")
    })
  })

  it("contains the expected navigation items with correct paths", () => {
    const expectedItems = [
      { key: "today", label: "Aujourd'hui", path: "/dashboard" },
      { key: "chat", label: "Chat", path: "/chat" },
      { key: "natal", label: "Thème", path: "/natal" },
      { key: "tirages", label: "Tirages", path: "/consultations" },
      { key: "profile", label: "Profil", path: "/settings" },
    ]

    expectedItems.forEach((expected, index) => {
      expect(navItems[index].key).toBe(expected.key)
      expect(navItems[index].label).toBe(expected.label)
      expect(navItems[index].path).toBe(expected.path)
    })
  })

  it("all paths start with /", () => {
    navItems.forEach((item) => {
      expect(item.path.startsWith("/")).toBe(true)
    })
  })

  it("all keys are unique", () => {
    const keys = navItems.map((item) => item.key)
    const uniqueKeys = new Set(keys)
    expect(uniqueKeys.size).toBe(keys.length)
  })
})
