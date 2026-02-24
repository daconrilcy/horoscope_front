import { describe, it, expect } from "vitest"
import {
  CalendarDays,
  MessageCircle,
  Star,
  Layers,
  User,
  ChevronRight,
  navItems,
  type NavItem,
  type LucideIcon,
} from "../ui"

describe("ui/ barrel export (index.ts)", () => {
  it("exports icons from icons.tsx", () => {
    expect(CalendarDays).toBeDefined()
    expect(MessageCircle).toBeDefined()
    expect(Star).toBeDefined()
    expect(Layers).toBeDefined()
    expect(User).toBeDefined()
    expect(ChevronRight).toBeDefined()
  })

  it("exports navItems from nav.ts", () => {
    expect(navItems).toBeDefined()
    expect(Array.isArray(navItems)).toBe(true)
    expect(navItems).toHaveLength(15)
  })

  it("exports NavItem type", () => {
    const item: NavItem = navItems[0]
    expect(item.key).toBe("today")
  })

  it("exports LucideIcon type", () => {
    const icon: LucideIcon = CalendarDays
    expect(icon).toBeDefined()
  })
})
