import { describe, it, expect } from "vitest"
import { render, screen } from "@testing-library/react"
import {
  CalendarDays,
  MessageCircle,
  Star,
  Layers,
  User,
  ChevronRight,
  Heart,
  Briefcase,
  Zap,
  Settings,
  Bell,
  Shield,
  Moon,
  LogOut,
  Loader2,
  FileText,
} from "../ui/icons"
import type { LucideIcon } from "../ui/icons"

describe("ui/icons barrel export", () => {
  const icons: { name: string; Icon: LucideIcon }[] = [
    { name: "CalendarDays", Icon: CalendarDays },
    { name: "MessageCircle", Icon: MessageCircle },
    { name: "Star", Icon: Star },
    { name: "Layers", Icon: Layers },
    { name: "User", Icon: User },
    { name: "ChevronRight", Icon: ChevronRight },
    { name: "Heart", Icon: Heart },
    { name: "Briefcase", Icon: Briefcase },
    { name: "Zap", Icon: Zap },
    { name: "Settings", Icon: Settings },
    { name: "Bell", Icon: Bell },
    { name: "Shield", Icon: Shield },
    { name: "Moon", Icon: Moon },
    { name: "LogOut", Icon: LogOut },
    { name: "Loader2", Icon: Loader2 },
    { name: "FileText", Icon: FileText },
  ]

  it.each(icons)("exports $name icon", ({ Icon }) => {
    expect(Icon).toBeDefined()
    expect(typeof Icon === "function" || typeof Icon === "object").toBe(true)
  })

  it.each(icons)("$name renders without error", ({ name, Icon }) => {
    render(<Icon data-testid={`icon-${name}`} />)
    expect(screen.getByTestId(`icon-${name}`)).toBeInTheDocument()
  })

  it("exports LucideIcon type", () => {
    const iconType: LucideIcon = CalendarDays
    expect(iconType).toBeDefined()
  })
})
