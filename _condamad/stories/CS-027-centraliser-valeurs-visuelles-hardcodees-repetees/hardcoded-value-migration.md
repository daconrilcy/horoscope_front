<!-- Preuve de migration du premier lot de valeurs visuelles hardcodees. -->

# Hardcoded Value Migration

| Literal | Token | Files migrated | Decision |
|---|---|---|---|
| `border-radius: 999px` | `border-radius: var(--radius-full)` | `App.css`, `AdminPromptsPage.css`, `HelpPage.css`, `Settings.css`, `AstrologerProfilePage.css` | exact migration |
| `gap: 12px` | `gap: var(--space-3)` | same batch | exact migration |
| `gap: 8px` | `gap: var(--space-2)` | same batch | exact migration |

Approximate colors and expressive gradients remain blocked for product/design
decision; they are not normalized by this story.
