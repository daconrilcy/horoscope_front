# Story 63.7: Section Offre & Tarifs

Status: done

## Mise en oeuvre réelle

- Le pricing final ajoute un sous-titre d'aide au choix au-dessus des cartes.
- `Basic` est mis en avant comme plan vedette par la hiérarchie visuelle et le CTA le plus fort.
- Chaque plan a désormais un positionnement d'usage explicite dans la carte, au-delà du simple tableau de features.
- Le plan `trial` reste aligné au modèle canonique dans `pricingConfig.ts`, mais n'est pas exposé dans la grille publique (`isAvailable: false`).

## Story

As a visiteur non authentifié ayant compris la valeur du produit,
I want voir clairement les différentes offres et leurs prix issus du catalogue réel,
so que je puisse choisir un plan adapté et passer à l'inscription sans friction ni ambiguïté.

## Acceptance Criteria

### AC1 — Source de vérité des offres (bloquant prod)

1. La landing publique **ne dépend pas** de `GET /v1/billing/plans`, car cet endpoint est actuellement authentifié et donc inutilisable avant inscription.
2. La source de vérité MVP côté frontend est `frontend/src/config/pricingConfig.ts`, synchronisée avec le catalogue produit réel et les codes de plan canoniques existants.
3. Si un endpoint public non-auth exposant les offres est livré plus tard, il pourra devenir la source primaire, avec fallback sur `pricingConfig.ts`.
4. **Aucun prix placeholder** (ex. `9,90€/mois` inventé) ne peut être affiché en production sans correspondance réelle dans le catalogue Stripe / billing.
5. La même règle vaut pour toute ancre promotionnelle ("2 mois offerts", "-17%", "essai 7 jours") : n'afficher que ce qui est supporté et vérifié.

### AC2 — Codes de plan canoniques (contrat strict)

6. Les identifiants de plans utilisés dans les CTAs et le contexte d'inscription suivent les codes canoniques du produit :
   ```ts
   export type PlanCode = 'free' | 'trial' | 'basic' | 'premium'
   ```
7. Les cartes effectivement exposées par la landing peuvent être un sous-ensemble de ces codes (par exemple `free`, `basic`, `premium`) selon l'offre publiée.
8. Toute valeur de plan inconnue dans un paramètre URL ou une logique interne est **ignorée silencieusement**.

### AC3 — Structure de la section tarifs

9. La section est identifiée par `id="pricing"` (cible du lien "Tarifs" dans la navbar).
10. Un H2 de section visible introduit les offres.
11. 2 à 3 cartes d'offres sont affichées selon les données réellement disponibles.
12. Chaque carte affiche : nom du plan, prix réel si disponible, description courte, liste de features, CTA.
13. Le plan recommandé est visuellement mis en avant : badge "Populaire" ou équivalent, sans wording trompeur.

### AC4 — Features comparées

14. Liste de 5–6 features représentatives du produit réel (pas de features inventées) :
    - Thème natal calculé précisément (Swiss Ephemeris)
    - Horoscope quotidien personnalisé
    - Chat astrologue IA (mention du quota réel si connu)
    - Consultations thématiques (mention du quota réel si connu)
    - Prédictions et moments clés
    - Support
15. Les quotas (ex. "5 chats/jour", "2000 messages/mois") ne sont affichés que s'ils correspondent aux valeurs canoniques du catalogue — sinon formulation générique ("Chat inclus", "Usage limité").

### AC5 — CTAs et continuité du funnel

16. Chaque CTA redirige vers `/register?plan={PlanCode}` où `{PlanCode}` est une valeur canonique définie en AC2.
17. Ce paramètre est lu et stocké par la page d'inscription (story 63.11) comme **intention commerciale**, sans créer d'abonnement.
18. Sous les plans : micro-réassurance factuelle du type "Sans engagement immédiat", "Support inclus", "Tarifs affichés avant paiement" selon l'offre réelle.
19. Le CTA "Découvrir gratuitement" peut omettre `plan` ou utiliser `?plan=free`.

### AC6 — Style

20. Aucun style inline : CSS dans `PricingSection.css`.
21. Toutes les cards plan : pattern glassmorphism premium :
    ```css
    background: var(--premium-glass-surface-1);
    backdrop-filter: blur(18px) saturate(140%);
    border: 1px solid var(--premium-glass-border);
    border-radius: var(--premium-radius-card); /* 24px */
    box-shadow: var(--premium-shadow-card);
    ```
22. Card plan recommandé : border renforcée `var(--premium-glass-border-strong)` + glow subtil cohérent avec le thème existant.
23. Layout : 3 colonnes desktop, plan recommandé en premier sur mobile (1 colonne).
24. `prefers-reduced-motion` est respecté pour les transitions éventuelles des cartes.

### AC7 — i18n

25. Noms de plans, labels features, CTAs, micro-réassurance dans `frontend/src/i18n/landing.ts` sous clé `pricing`.
26. Les prix numériques et les codes de plans sont dans `frontend/src/config/pricingConfig.ts`, **pas dans `landing.ts`**.

### Definition of Done QA

- [ ] Aucun prix fictif visible en prod (Niveau 3 fallback activé si données manquantes)
- [ ] Le plan recommandé est en premier sur mobile
- [ ] CTA plan payant encode `?plan=basic` ou `?plan=premium` selon l'offre cliquée
- [ ] Valeur plan inconnue dans l'URL → aucune pré-sélection, pas d'erreur
- [ ] Les quotas chiffrés ne sont affichés que s'ils correspondent au catalogue réel
- [ ] `prefers-reduced-motion` : aucune animation décorative essentielle dans la section tarifs

## Tasks / Subtasks

- [ ] T1 — Créer `frontend/src/config/pricingConfig.ts` (AC: 1, 2, 6, 8)
  - [ ] Type `PlanCode`
  - [ ] Constantes prix synchronisées avec catalogue Stripe (ou "null" si non définis)
  - [ ] Feature flags par plan
- [ ] T2 — Créer `PricingSection.tsx` (AC: 9–19)
  - [ ] 2–3 cards plan depuis pricingConfig
  - [ ] Masquer prix si données null (Niveau 3)
  - [ ] CTA avec param plan
- [ ] T3 — Source de vérité (AC: 1)
  - [ ] Vérifier s'il existe un endpoint public non-auth pour les offres
  - [ ] Sinon rester sur `pricingConfig.ts` uniquement
- [ ] T4 — CSS (AC: 20–24)
  - [ ] Créer `PricingSection.css`
  - [ ] Responsive + prefers-reduced-motion
- [ ] T5 — i18n (AC: 25, 26)

## Dev Notes

- **i18n** : `useTranslation('landing')` — namespace à enregistrer dans `frontend/src/i18n/index.ts`.
- **Tokens premium** : `frontend/src/styles/premium-theme.css` pour `--premium-glass-surface-1`, `--premium-glass-border-strong`, `--premium-shadow-card`, `--premium-radius-card`.
- **Vérifier l'epic 61** : plans canoniques dans `_bmad-output/implementation-artifacts/61-7-modele-canonique-entitlements-produit.md` et `61-49-contrat-frontend-unique-plan-commercial-droits-effectifs.md`.
- **pricingConfig.ts** : fallback frontend public canonique tant qu'aucun endpoint public non-auth n'existe.
- `--premium-glass-border-strong` = `rgba(196, 177, 235, 0.54)` en light / `rgba(156, 121, 255, 0.2)` en dark — déjà défini dans `premium-theme.css`.

### Project Structure Notes

```
frontend/src/
├── config/
│   └── pricingConfig.ts             # nouveau — source de vérité pricing frontend
└── pages/landing/sections/
    ├── PricingSection.tsx            # nouveau
    └── PricingSection.css            # nouveau
```

### References

- Plans canoniques epic 61 : `_bmad-output/implementation-artifacts/61-7-modele-canonique-entitlements-produit.md`
- Contrat frontend plans : `_bmad-output/implementation-artifacts/61-49-contrat-frontend-unique-plan-commercial-droits-effectifs.md`
- i18n landing : [frontend/src/i18n/landing.ts](frontend/src/i18n/landing.ts)
- Document funnel — Offre & Prix : [docs/funnel/landing_funnel.md](docs/funnel/landing_funnel.md#wireframe-ascii-commenté)

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
