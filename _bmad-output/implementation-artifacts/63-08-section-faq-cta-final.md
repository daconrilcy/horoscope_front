# Story 63.8: Section FAQ & CTA Final

Status: done

## Mise en oeuvre réelle

- La FAQ conserve un accordéon natif exclusif, avec une surface plus premium et un état ouvert plus marqué.
- Le CTA final a été réécrit pour être plus décisionnel et moins redondant avec le hero.
- Le CTA final actuellement livré est aligné sur la promesse "commencer son thème natal en quelques minutes".

## Story

As a visiteur non authentifié ayant parcouru la landing page,
I want trouver des réponses aux dernières objections qui me retiennent et un dernier appel à l'action,
so que mes freins soient levés et que je passe à l'inscription sans hésitation.

## Acceptance Criteria

### AC1 — Section FAQ accordéon

1. La section est identifiée par `id="faq"`.
2. H2 : "Questions fréquentes" ou "Vous avez des questions ?".
3. 5–6 questions/réponses en accordéon, couvrant les objections clés :
   - "Est-ce vraiment personnalisé pour moi ?" → oui, basé sur votre thème natal précis
   - "Combien de temps pour voir un premier résultat ?" → dès la première session
   - "Mes données personnelles sont-elles protégées ?" → RGPD, chiffrement
   - "Puis-je annuler mon abonnement à tout moment ?" → oui, en 1 clic
   - "L'astrologie est-elle scientifiquement fondée ?" → réponse nuancée et honnête
   - "Y a-t-il un support si j'ai besoin d'aide ?" → support par email, FAQ intégrée
4. L'accordéon est implémenté avec `<details>/<summary>` HTML natif ou avec `useState` React — sans librairie externe.
5. Une seule question peut être ouverte à la fois (comportement accordéon exclusif — si HTML `<details>`, utiliser `name` attribute pour le groupe, sinon gérer en React).

### AC2 — CTA final

6. Après la FAQ, un bloc CTA final reprend la proposition de valeur résumée en 1–2 lignes.
7. Le CTA final contient :
   - Un H2 ou titre court accrocheur (ex. "Prêt à découvrir votre thème natal ?")
   - Un paragraphe de réassurance court (1–2 lignes)
   - Bouton CTA primaire "Démarrer gratuitement" → `/register`
   - Micro-réassurance inline : "Sans carte bancaire", "Annulation en 1 clic"
8. Le bloc CTA final a un fond différencié (gradient premium ou surface glass) pour se démarquer visuellement du reste de la page.

### AC3 — Style

9. Aucun style inline : CSS dans `FaqSection.css`.
10. Accordéon : chevron animé avec CSS transform rotate, `transition: transform var(--duration-normal) var(--easing-default)`.
11. Espacement : `gap: var(--space-4)` entre items, `padding: var(--space-6)` dans chaque item.
12. CTA final : `background: var(--premium-glass-surface-2); backdrop-filter: blur(18px); border-radius: var(--premium-radius-hero);`, centré, padding `var(--space-8)`.
13. Texte CTA final : `var(--premium-text-strong)` pour le titre, `var(--premium-text-main)` pour le paragraphe.
14. Bouton CTA final : `<Button variant="primary" size="lg">` — composant Button existant.

### AC4 — i18n

13. Toutes les questions, réponses et textes CTA final dans `frontend/src/i18n/landing.ts` sous clés `faq` et `finalCta`.

## Tasks / Subtasks

- [ ] T1 — Créer `FaqSection.tsx` (AC: 1, 2, 3, 4, 5)
  - [ ] 5–6 items FAQ en accordéon
  - [ ] Comportement accordéon exclusif
- [ ] T2 — CTA final (AC: 6, 7, 8)
  - [ ] Bloc CTA final avec titre, texte, bouton, micro-réassurance
  - [ ] Fond différencié
- [ ] T3 — CSS (AC: 9, 10, 11, 12)
  - [ ] Créer `FaqSection.css`
  - [ ] Animation chevron accordéon
  - [ ] Styles CTA final
- [ ] T4 — i18n (AC: 13)
  - [ ] Clés `faq` et `finalCta` dans `landing.ts`

## Dev Notes

- **i18n** : `useTranslation('landing')` — namespace à enregistrer dans `frontend/src/i18n/index.ts`.
- **Tokens** : `--duration-normal` (250ms), `--easing-default` (cubic-bezier(0.4,0,0.2,1)), `--premium-radius-hero` (28px), `--space-6/8` pour les paddings — tous définis dans `design-tokens.css` et `premium-theme.css`.
- L'attribut `name` sur `<details>` pour le comportement exclusif : supporté Chrome 120+, Firefox 130+. Utiliser `useState` comme fallback si besoin.
- **Button CTA final** : `<Button variant="primary" size="lg">` depuis `frontend/src/components/ui/Button/Button.tsx`.
- Réponses FAQ honnêtes — surtout la question sur le fondement scientifique de l'astrologie.

### Project Structure Notes

```
frontend/src/pages/landing/sections/
├── FaqSection.tsx    # nouveau
└── FaqSection.css    # nouveau
```

### References

- Button UI : [frontend/src/components/ui/Button/Button.tsx](frontend/src/components/ui/Button/Button.tsx)
- i18n landing : [frontend/src/i18n/landing.ts](frontend/src/i18n/landing.ts)
- Document funnel — FAQ & CTA : [docs/funnel/landing_funnel.md](docs/funnel/landing_funnel.md#wireframe-ascii-commenté)

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
