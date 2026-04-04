# Story 63.16: Instrumentation analytics du funnel [Priorité haute — implémenter tôt]

Status: done

## Mise en oeuvre réelle

- Le hook `useAnalytics()` est en place et couvre les événements du funnel principal.
- `noop` reste le provider par défaut en dev/test.
- Plausible est maintenant traité comme provider privacy-first sans blocage par un cookie de consentement applicatif local.
- Un test frontend dédié couvre ce comportement.

## Story

As a product manager et équipe produit,
I want des événements analytics normalisés sur toutes les étapes du funnel landing → inscription,
so que je puisse mesurer les taux de conversion à chaque étape et optimiser la landing après mise en ligne.

## Note de priorité

**Cette story doit être implémentée dès la mise en ligne de la landing, idéalement en parallèle des premières stories UI.** Sans instrumentation, il est impossible d'optimiser le funnel après lancement. Ne pas la reporter comme "nice-to-have".

## Acceptance Criteria

### AC1 — Consentement

1. **Aucun événement n'est envoyé sans consentement utilisateur** si la jurisdiction requiert un consentement cookie (RGPD en Europe).
2. Un mécanisme de consentement minimal est en place avant le tracking : soit une bannière cookie (si analytics tiers), soit un tracking first-party privacy-first configuré de manière compatible avec le cadre légal retenu.
3. **Recommandation MVP** : utiliser Plausible Analytics ou Matomo self-hosted configuré sans cookies, sous validation du cadre légal et cookie du produit.
4. Le provider analytics est configurable via `VITE_ANALYTICS_PROVIDER` (`plausible` | `matomo` | `noop`). Par défaut : `noop` en dev/test.

### AC2 — Événements normalisés (payload stable)

5. Les événements suivants sont trackés avec leur payload minimal :

| Événement | Déclencheur | Propriétés |
|-----------|-------------|------------|
| `landing_view` | Chargement de `LandingPage` | `{ referrer, utm_source, utm_medium, utm_campaign }` |
| `hero_cta_click` | Clic CTA primaire hero | `{ cta_label }` |
| `secondary_cta_click` | Clic "Voir un exemple" | — |
| `pricing_view` | Section #pricing dans viewport | — |
| `pricing_plan_select` | Clic CTA sur un plan | `{ plan_id }` |
| `register_view` | Chargement de `/register` | `{ from_plan: PlanCode | null }` |
| `register_start` | Premier focus sur le formulaire | — |
| `register_success` | Création de compte réussie | `{ method: 'email' | 'google', plan: PlanCode | null }` |
| `register_error` | Échec de la soumission | `{ error_type }` |

6. Tous les payloads sont des objets sérialisables simples — pas d'identifiants personnels (pas d'email, pas de nom).
7. Les propriétés UTM (`utm_source`, `utm_medium`, `utm_campaign`) sont lues depuis `window.location.search` au chargement de la landing.

### AC3 — Implémentation frontend

8. Un hook `useAnalytics()` est créé dans `frontend/src/hooks/useAnalytics.ts` exposant `track(eventName, properties)`.
9. En mode `noop`, `track()` loggue l'événement à `console.debug` uniquement — aucun appel réseau.
10. L'instrumentation est ajoutée dans les composants concernés sans modifier leur logique métier (séparation des préoccupations).
11. Les événements de section (ex. `pricing_view`) utilisent `IntersectionObserver` ou un équivalent — implémentation laissée au dev.

### AC4 — Dashboard minimal

12. Un dashboard ou une vue analytics simple doit être consultable par le PO pour visualiser les conversions par étape. Si Plausible est utilisé, son dashboard natif suffit. Si Matomo, configurer un objectif de conversion basique.

### Definition of Done QA

- [ ] `landing_view` déclenché au chargement de `/` (vérifiable en `console.debug` avec `noop`)
- [ ] `register_success` déclenché uniquement après création de compte réussie
- [ ] Aucun payload contient un email ou identifiant personnel
- [ ] En dev (`VITE_ANALYTICS_PROVIDER=noop`), aucun appel réseau vers un provider
- [ ] UTM params capturés correctement depuis l'URL

## Tasks / Subtasks

- [ ] T1 — Choix et config provider (AC: 1–4)
  - [ ] Décider Plausible vs Matomo vs custom (avec PO)
  - [ ] `VITE_ANALYTICS_PROVIDER` env var
  - [ ] Provider `noop` pour dev/CI
- [ ] T2 — Hook `useAnalytics` (AC: 8, 9, 10)
  - [ ] `frontend/src/hooks/useAnalytics.ts`
  - [ ] Abstraction provider (noop | plausible | matomo)
- [ ] T3 — Instrumentation composants (AC: 5–7)
  - [ ] `landing_view` dans LandingPage
  - [ ] `hero_cta_click`, `pricing_plan_select` etc. dans les sections concernées
  - [ ] `register_view`, `register_start`, `register_success` dans SignUpForm
- [ ] T4 — Dashboard (AC: 12)
  - [ ] Config objectif de conversion dans le provider choisi

## Dev Notes

- **Plausible** est la recommandation MVP pour sa simplicité. La configuration finale doit néanmoins être validée avec le cadre légal et cookie du produit avant mise en production.
- **Ne pas utiliser Google Analytics** : GA4 requiert un consentement RGPD et ajoute de la complexité.
- Le hook `useAnalytics` suit le même pattern que `useTranslation` — simple, injectable, mockable.
- Cette story dépend logiquement de 63.1 (LandingPage) et 63.11 (SignUpForm) mais peut être implémentée en parallèle.

### Project Structure Notes

```
frontend/src/
├── hooks/
│   └── useAnalytics.ts    # nouveau
└── config/
    └── analytics.ts       # nouveau — config provider
```

### References

- Document funnel — Métriques : [docs/funnel/landing_funnel.md](docs/funnel/landing_funnel.md#métriques-clés-pilotage)

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
