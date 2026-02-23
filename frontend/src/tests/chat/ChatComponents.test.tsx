import { cleanup, render, screen, fireEvent } from "@testing-library/react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import { ConversationItem } from "../../features/chat/components/ConversationItem"
import { ConversationList } from "../../features/chat/components/ConversationList"
import { MessageBubble } from "../../features/chat/components/MessageBubble"
import { TypingIndicator } from "../../features/chat/components/TypingIndicator"
import { ChatComposer } from "../../features/chat/components/ChatComposer"
import { AstrologerDetailPanel } from "../../features/chat/components/AstrologerDetailPanel"
import { ChatLayout } from "../../features/chat/components/ChatLayout"
import { ChatWindow } from "../../features/chat/components/ChatWindow"

beforeEach(() => {
  localStorage.setItem("lang", "fr")
})

afterEach(() => {
  cleanup()
})

describe("ConversationItem", () => {
  const baseConversation = {
    conversation_id: 42,
    status: "active",
    updated_at: "2026-02-22T10:00:00Z",
    last_message_preview: "Dernier message",
  }

  it("renders conversation preview and date", () => {
    const onClick = vi.fn()
    render(
      <ConversationItem
        conversation={baseConversation}
        isActive={false}
        onClick={onClick}
      />
    )

    expect(screen.getByText("Dernier message")).toBeInTheDocument()
    expect(screen.getByText("22 févr.")).toBeInTheDocument()
  })

  it("calls onClick when clicked", () => {
    const onClick = vi.fn()
    render(
      <ConversationItem
        conversation={baseConversation}
        isActive={false}
        onClick={onClick}
      />
    )

    fireEvent.click(screen.getByRole("button"))
    expect(onClick).toHaveBeenCalledTimes(1)
  })

  it("applies active class when isActive is true", () => {
    const onClick = vi.fn()
    render(
      <ConversationItem
        conversation={baseConversation}
        isActive={true}
        onClick={onClick}
      />
    )

    const button = screen.getByRole("button")
    expect(button).toHaveClass("conversation-item--active")
    expect(button).toHaveAttribute("aria-pressed", "true")
  })

  it("shows placeholder text when no preview", () => {
    const onClick = vi.fn()
    render(
      <ConversationItem
        conversation={{ ...baseConversation, last_message_preview: "" }}
        isActive={false}
        onClick={onClick}
      />
    )

    expect(screen.getByText("Nouvelle conversation")).toBeInTheDocument()
  })
})

describe("ConversationList", () => {
  const conversations = [
    {
      conversation_id: 1,
      status: "active",
      updated_at: "2026-02-22T10:00:00Z",
      last_message_preview: "Message 1",
    },
    {
      conversation_id: 2,
      status: "active",
      updated_at: "2026-02-21T10:00:00Z",
      last_message_preview: "Message 2",
    },
  ]

  it("renders list of conversations", () => {
    const onSelect = vi.fn()
    render(
      <ConversationList
        conversations={conversations}
        selectedId={null}
        onSelect={onSelect}
      />
    )

    expect(screen.getByText("Message 1")).toBeInTheDocument()
    expect(screen.getByText("Message 2")).toBeInTheDocument()
  })

  it("shows loading state", () => {
    const onSelect = vi.fn()
    render(
      <ConversationList
        conversations={[]}
        selectedId={null}
        onSelect={onSelect}
        isLoading={true}
      />
    )

    expect(screen.getByText("Chargement...")).toBeInTheDocument()
  })

  it("shows error state", () => {
    const onSelect = vi.fn()
    render(
      <ConversationList
        conversations={[]}
        selectedId={null}
        onSelect={onSelect}
        error={new Error("Erreur")}
      />
    )

    expect(screen.getByText("Erreur de chargement")).toBeInTheDocument()
  })

  it("shows empty state when no conversations", () => {
    const onSelect = vi.fn()
    render(
      <ConversationList
        conversations={[]}
        selectedId={null}
        onSelect={onSelect}
      />
    )

    expect(screen.getByText("Aucune conversation")).toBeInTheDocument()
  })

  it("filters conversations by search query", () => {
    const onSelect = vi.fn()
    render(
      <ConversationList
        conversations={conversations}
        selectedId={null}
        onSelect={onSelect}
      />
    )

    const searchInput = screen.getByPlaceholderText("Rechercher...")
    fireEvent.change(searchInput, { target: { value: "Message 1" } })

    expect(screen.getByText("Message 1")).toBeInTheDocument()
    expect(screen.queryByText("Message 2")).not.toBeInTheDocument()
  })

  it("shows no results when search query matches nothing", () => {
    const onSelect = vi.fn()
    render(
      <ConversationList
        conversations={conversations}
        selectedId={null}
        onSelect={onSelect}
      />
    )

    const searchInput = screen.getByPlaceholderText("Rechercher...")
    fireEvent.change(searchInput, { target: { value: "inexistant" } })

    expect(screen.getByText("Aucun résultat")).toBeInTheDocument()
  })

  it("calls onSelect when conversation is clicked", () => {
    const onSelect = vi.fn()
    render(
      <ConversationList
        conversations={conversations}
        selectedId={null}
        onSelect={onSelect}
      />
    )

    fireEvent.click(screen.getByText("Message 1"))
    expect(onSelect).toHaveBeenCalledWith(1)
  })
})

describe("MessageBubble", () => {
  it("renders user message", () => {
    render(
      <MessageBubble role="user" content="Hello world" />
    )

    expect(screen.getByText("Vous")).toBeInTheDocument()
    expect(screen.getByText("Hello world")).toBeInTheDocument()
  })

  it("renders assistant message", () => {
    render(
      <MessageBubble role="assistant" content="Bonjour" />
    )

    expect(screen.getByText("Astrologue")).toBeInTheDocument()
    expect(screen.getByText("Bonjour")).toBeInTheDocument()
  })

  it("renders timestamp when provided", () => {
    render(
      <MessageBubble
        role="user"
        content="Hello"
        timestamp="2026-02-22T14:30:00Z"
      />
    )

    expect(screen.getByText("15:30")).toBeInTheDocument()
  })

  it("applies correct class for user message", () => {
    render(
      <MessageBubble role="user" content="Test" />
    )

    const bubble = screen.getByTestId("chat-message")
    expect(bubble).toHaveClass("message-bubble--user")
  })

  it("applies correct class for assistant message", () => {
    render(
      <MessageBubble role="assistant" content="Test" />
    )

    const bubble = screen.getByTestId("chat-message")
    expect(bubble).toHaveClass("message-bubble--assistant")
  })
})

describe("TypingIndicator", () => {
  it("renders typing indicator with correct label", () => {
    render(<TypingIndicator />)

    expect(screen.getByLabelText("L'astrologue écrit...")).toBeInTheDocument()
    expect(screen.getByText("Astrologue")).toBeInTheDocument()
  })

  it("renders three dots", () => {
    render(<TypingIndicator />)

    const dots = document.querySelectorAll(".typing-indicator-dot")
    expect(dots).toHaveLength(3)
  })
})

describe("ChatComposer", () => {
  it("renders input and send button", () => {
    const onSend = vi.fn()
    render(<ChatComposer onSend={onSend} />)

    expect(screen.getByPlaceholderText("Posez votre question aux astres...")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Envoyer" })).toBeInTheDocument()
  })

  it("calls onSend when form is submitted", () => {
    const onSend = vi.fn()
    render(<ChatComposer onSend={onSend} />)

    const input = screen.getByRole("textbox")
    fireEvent.change(input, { target: { value: "Test message" } })
    fireEvent.click(screen.getByRole("button", { name: "Envoyer" }))

    expect(onSend).toHaveBeenCalledWith("Test message")
  })

  it("clears input after send", () => {
    const onSend = vi.fn()
    render(<ChatComposer onSend={onSend} />)

    const input = screen.getByRole("textbox") as HTMLTextAreaElement
    fireEvent.change(input, { target: { value: "Test message" } })
    fireEvent.click(screen.getByRole("button", { name: "Envoyer" }))

    expect(input.value).toBe("")
  })

  it("does not send empty messages", () => {
    const onSend = vi.fn()
    render(<ChatComposer onSend={onSend} />)

    fireEvent.click(screen.getByRole("button", { name: "Envoyer" }))
    expect(onSend).not.toHaveBeenCalled()
  })

  it("does not send whitespace-only messages", () => {
    const onSend = vi.fn()
    render(<ChatComposer onSend={onSend} />)

    const input = screen.getByRole("textbox")
    fireEvent.change(input, { target: { value: "   " } })
    fireEvent.click(screen.getByRole("button", { name: "Envoyer" }))

    expect(onSend).not.toHaveBeenCalled()
  })

  it("sends on Enter key press", () => {
    const onSend = vi.fn()
    render(<ChatComposer onSend={onSend} />)

    const input = screen.getByRole("textbox")
    fireEvent.change(input, { target: { value: "Test message" } })
    fireEvent.keyDown(input, { key: "Enter", shiftKey: false })

    expect(onSend).toHaveBeenCalledWith("Test message")
  })

  it("does not send on Shift+Enter", () => {
    const onSend = vi.fn()
    render(<ChatComposer onSend={onSend} />)

    const input = screen.getByRole("textbox")
    fireEvent.change(input, { target: { value: "Test message" } })
    fireEvent.keyDown(input, { key: "Enter", shiftKey: true })

    expect(onSend).not.toHaveBeenCalled()
  })

  it("disables input and button when disabled prop is true", () => {
    const onSend = vi.fn()
    render(<ChatComposer onSend={onSend} disabled={true} />)

    expect(screen.getByRole("textbox")).toBeDisabled()
    expect(screen.getByRole("button", { name: "Envoyer" })).toBeDisabled()
  })

  it("uses custom placeholder when provided", () => {
    const onSend = vi.fn()
    render(<ChatComposer onSend={onSend} placeholder="Custom placeholder" />)

    expect(screen.getByPlaceholderText("Custom placeholder")).toBeInTheDocument()
  })
})

describe("AstrologerDetailPanel", () => {
  it("renders astrologer information", () => {
    render(<AstrologerDetailPanel conversationId={null} />)

    expect(screen.getByText("Votre Astrologue")).toBeInTheDocument()
    expect(screen.getByText("En ligne")).toBeInTheDocument()
    expect(screen.getByText("Thèmes nataux")).toBeInTheDocument()
    expect(screen.getByText("Transits planétaires")).toBeInTheDocument()
  })

  it("shows conversation id when provided", () => {
    render(<AstrologerDetailPanel conversationId={42} />)

    expect(screen.getByText("#42")).toBeInTheDocument()
    expect(screen.getByText("Cette conversation")).toBeInTheDocument()
  })

  it("does not show conversation section when no conversation id", () => {
    render(<AstrologerDetailPanel conversationId={null} />)

    expect(screen.queryByText("Cette conversation")).not.toBeInTheDocument()
  })
})

describe("ChatLayout", () => {
  it("renders 3 columns on desktop", () => {
    const onMobileViewChange = vi.fn()

    render(
      <ChatLayout
        leftPanel={<div data-testid="left">Left</div>}
        centerPanel={<div data-testid="center">Center</div>}
        rightPanel={<div data-testid="right">Right</div>}
        mobileView="list"
        onMobileViewChange={onMobileViewChange}
        hasConversation={false}
        isMobile={false}
      />
    )

    expect(screen.getByTestId("left")).toBeInTheDocument()
    expect(screen.getByTestId("center")).toBeInTheDocument()
    expect(screen.getByTestId("right")).toBeInTheDocument()
    expect(document.querySelector(".chat-layout--desktop")).toBeInTheDocument()
  })

  it("renders only left panel on mobile list view", () => {
    const onMobileViewChange = vi.fn()

    render(
      <ChatLayout
        leftPanel={<div data-testid="left">Left</div>}
        centerPanel={<div data-testid="center">Center</div>}
        rightPanel={<div data-testid="right">Right</div>}
        mobileView="list"
        onMobileViewChange={onMobileViewChange}
        hasConversation={false}
        isMobile={true}
      />
    )

    expect(screen.getByTestId("left")).toBeInTheDocument()
    expect(screen.queryByTestId("center")).not.toBeInTheDocument()
    expect(screen.queryByTestId("right")).not.toBeInTheDocument()
    expect(document.querySelector(".chat-layout--mobile")).toBeInTheDocument()
  })

  it("renders only center panel on mobile chat view", () => {
    const onMobileViewChange = vi.fn()

    render(
      <ChatLayout
        leftPanel={<div data-testid="left">Left</div>}
        centerPanel={<div data-testid="center">Center</div>}
        rightPanel={<div data-testid="right">Right</div>}
        mobileView="chat"
        onMobileViewChange={onMobileViewChange}
        hasConversation={true}
        isMobile={true}
      />
    )

    expect(screen.queryByTestId("left")).not.toBeInTheDocument()
    expect(screen.getByTestId("center")).toBeInTheDocument()
    expect(screen.queryByTestId("right")).not.toBeInTheDocument()
  })

  it("shows resume conversation button on mobile when has conversation", () => {
    const onMobileViewChange = vi.fn()

    render(
      <ChatLayout
        leftPanel={<div data-testid="left">Left</div>}
        centerPanel={<div data-testid="center">Center</div>}
        rightPanel={<div data-testid="right">Right</div>}
        mobileView="list"
        onMobileViewChange={onMobileViewChange}
        hasConversation={true}
        isMobile={true}
      />
    )

    const resumeButton = screen.getByText("Reprendre la conversation")
    expect(resumeButton).toBeInTheDocument()

    fireEvent.click(resumeButton)
    expect(onMobileViewChange).toHaveBeenCalledWith("chat")
  })

  it("does not show resume button when no conversation", () => {
    const onMobileViewChange = vi.fn()

    render(
      <ChatLayout
        leftPanel={<div data-testid="left">Left</div>}
        centerPanel={<div data-testid="center">Center</div>}
        rightPanel={<div data-testid="right">Right</div>}
        mobileView="list"
        onMobileViewChange={onMobileViewChange}
        hasConversation={false}
        isMobile={true}
      />
    )

    expect(screen.queryByText("Reprendre la conversation")).not.toBeInTheDocument()
  })
})

describe("ChatWindow", () => {
  const baseMessages = [
    { id: "1", role: "user" as const, content: "Hello" },
    { id: "2", role: "assistant" as const, content: "Bonjour" },
  ]

  it("renders messages", () => {
    const onSendMessage = vi.fn()
    render(<ChatWindow messages={baseMessages} onSendMessage={onSendMessage} />)

    expect(screen.getByText("Hello")).toBeInTheDocument()
    expect(screen.getByText("Bonjour")).toBeInTheDocument()
  })

  it("renders empty state when no messages", () => {
    const onSendMessage = vi.fn()
    render(<ChatWindow messages={[]} onSendMessage={onSendMessage} />)

    expect(screen.getByText("Commencez une conversation avec votre astrologue.")).toBeInTheDocument()
  })

  it("renders typing indicator when isTyping is true", () => {
    const onSendMessage = vi.fn()
    render(
      <ChatWindow
        messages={baseMessages}
        onSendMessage={onSendMessage}
        isTyping={true}
      />
    )

    expect(screen.getByLabelText("L'astrologue écrit...")).toBeInTheDocument()
  })

  it("renders error message with retry button", () => {
    const onSendMessage = vi.fn()
    const onRetry = vi.fn()
    render(
      <ChatWindow
        messages={baseMessages}
        onSendMessage={onSendMessage}
        error={new Error("Erreur réseau")}
        onRetry={onRetry}
      />
    )

    expect(screen.getByText("Erreur: Erreur réseau")).toBeInTheDocument()
    const retryButton = screen.getByText("Réessayer")
    expect(retryButton).toBeInTheDocument()

    fireEvent.click(retryButton)
    expect(onRetry).toHaveBeenCalledTimes(1)
  })

  it("renders quota blocked message", () => {
    const onSendMessage = vi.fn()
    render(
      <ChatWindow
        messages={baseMessages}
        onSendMessage={onSendMessage}
        quotaBlocked={true}
      />
    )

    expect(screen.getByText(/quota quotidien est épuisé/)).toBeInTheDocument()
  })

  it("renders back button when showBackButton is true", () => {
    const onSendMessage = vi.fn()
    const onBack = vi.fn()
    render(
      <ChatWindow
        messages={baseMessages}
        onSendMessage={onSendMessage}
        showBackButton={true}
        onBack={onBack}
      />
    )

    const backButton = screen.getByLabelText("Retour à la liste")
    expect(backButton).toBeInTheDocument()

    fireEvent.click(backButton)
    expect(onBack).toHaveBeenCalledTimes(1)
  })

  it("does not render back button when showBackButton is false", () => {
    const onSendMessage = vi.fn()
    render(
      <ChatWindow
        messages={baseMessages}
        onSendMessage={onSendMessage}
        showBackButton={false}
      />
    )

    expect(screen.queryByLabelText("Retour à la liste")).not.toBeInTheDocument()
  })

  it("disables composer when sending", () => {
    const onSendMessage = vi.fn()
    render(
      <ChatWindow
        messages={baseMessages}
        onSendMessage={onSendMessage}
        isSending={true}
      />
    )

    expect(screen.getByRole("textbox")).toBeDisabled()
    expect(screen.getByRole("button", { name: "Envoyer" })).toBeDisabled()
  })

  it("disables composer when quota is blocked", () => {
    const onSendMessage = vi.fn()
    render(
      <ChatWindow
        messages={baseMessages}
        onSendMessage={onSendMessage}
        quotaBlocked={true}
      />
    )

    expect(screen.getByRole("textbox")).toBeDisabled()
    expect(screen.getByRole("button", { name: "Envoyer" })).toBeDisabled()
  })

  it("calls onSendMessage when message is sent", () => {
    const onSendMessage = vi.fn()
    render(<ChatWindow messages={baseMessages} onSendMessage={onSendMessage} />)

    const input = screen.getByRole("textbox")
    fireEvent.change(input, { target: { value: "Test message" } })
    fireEvent.click(screen.getByRole("button", { name: "Envoyer" }))

    expect(onSendMessage).toHaveBeenCalledWith("Test message")
  })
})

describe("useAutoScroll", () => {
  it("returns handleScroll and resetScroll functions", async () => {
    const { useAutoScroll } = await import("../../features/chat/hooks/useAutoScroll")
    const { renderHook } = await import("@testing-library/react")
    const { createRef } = await import("react")

    const ref = createRef<HTMLDivElement>()
    const { result } = renderHook(() => useAutoScroll(ref, 0))

    expect(typeof result.current.handleScroll).toBe("function")
    expect(typeof result.current.resetScroll).toBe("function")
  })

  it("handleScroll does not throw when ref has no element", async () => {
    const { useAutoScroll } = await import("../../features/chat/hooks/useAutoScroll")
    const { renderHook } = await import("@testing-library/react")
    const { createRef } = await import("react")

    const ref = createRef<HTMLDivElement>()
    const { result } = renderHook(() => useAutoScroll(ref, 0))

    expect(() => result.current.handleScroll()).not.toThrow()
  })

  it("resetScroll does not throw", async () => {
    const { useAutoScroll } = await import("../../features/chat/hooks/useAutoScroll")
    const { renderHook } = await import("@testing-library/react")
    const { createRef } = await import("react")

    const ref = createRef<HTMLDivElement>()
    const { result } = renderHook(() => useAutoScroll(ref, 0))

    expect(() => result.current.resetScroll()).not.toThrow()
  })
})

describe("useIsMobile", () => {
  const originalInnerWidth = window.innerWidth

  afterEach(() => {
    Object.defineProperty(window, "innerWidth", {
      writable: true,
      configurable: true,
      value: originalInnerWidth,
    })
    vi.useRealTimers()
  })

  it("returns true when window width is below 768px", async () => {
    const { useIsMobile } = await import("../../features/chat/hooks/useIsMobile")
    const { renderHook } = await import("@testing-library/react")

    Object.defineProperty(window, "innerWidth", {
      writable: true,
      configurable: true,
      value: 500,
    })

    const { result } = renderHook(() => useIsMobile())
    expect(result.current).toBe(true)
  })

  it("returns false when window width is 768px or above", async () => {
    const { useIsMobile } = await import("../../features/chat/hooks/useIsMobile")
    const { renderHook } = await import("@testing-library/react")

    Object.defineProperty(window, "innerWidth", {
      writable: true,
      configurable: true,
      value: 1024,
    })

    const { result } = renderHook(() => useIsMobile())
    expect(result.current).toBe(false)
  })

  it("updates value on resize with debounce", async () => {
    vi.useFakeTimers()
    const { useIsMobile } = await import("../../features/chat/hooks/useIsMobile")
    const { renderHook, act } = await import("@testing-library/react")

    Object.defineProperty(window, "innerWidth", {
      writable: true,
      configurable: true,
      value: 1024,
    })

    const { result } = renderHook(() => useIsMobile())
    expect(result.current).toBe(false)

    act(() => {
      Object.defineProperty(window, "innerWidth", {
        writable: true,
        configurable: true,
        value: 500,
      })
      window.dispatchEvent(new Event("resize"))
    })

    expect(result.current).toBe(false)

    act(() => {
      vi.advanceTimersByTime(150)
    })

    expect(result.current).toBe(true)
  })
})
