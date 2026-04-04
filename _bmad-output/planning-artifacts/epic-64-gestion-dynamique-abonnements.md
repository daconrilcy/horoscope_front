---
stepsCompleted:
  - step-01-validate-prerequisites
  - step-02-design-epics
  - step-03-create-stories
inputDocuments:
  - '_bmad-output/planning-artifacts/prd.md'
  - '_bmad-output/planning-artifacts/architecture.md'
  - '_bmad-output/planning-artifacts/ux-design-specification.md'
workflowType: 'epic'
epicNumber: 64
status: 'in-progress'
createdAt: '2026-04-04'
owner: Cyril
---

# Epic 64 — Gestion dynamique des droits d'accès, de la génération et des CTA d'upgrade par plan d'abonnement

**Status:** in-progress
**Créé le:** 2026-04-04
**Owner:** Cyril

---

## Objectif Produit

Refondre le comportement produit pour que chaque plan d'abonnement (free / basic / premium) contrôle de manière centralisée et dynamique — depuis la base de données — :

- ce que l'utilisateur peut voir et générer ;
- la profondeur de génération LLM réellement produite selon le plan ;
- les sections visibles mais verrouillées (contenu teaser fixe + flou visuel) ;
- les CTA d'upgrade contextualisés affichés sur les pages stratégiques ;
- le moteur LLM utilisé selon le plan et le use case.

**Règle structurante :** Les règles métier d'abonnement (features, quotas, variantes d'accès, droits, plan cible d'upgrade) sont issues de la base de données. La sélection technique du modèle LLM reste configurable via `.env` à ce stade.

---

## Exigences Fonctionnelles (FR64)

### Génération LLM par plan

**FR64-1 :** Le backend sélectionne le variant de génération LLM pour l'horoscope du jour selon le plan actif (free → prompt variant "summary_only" ; basic/premium → prompt variant "full"). Les sections exclues par un variant restreint ne sont pas générées côté LLM.

**FR64-2 :** Pour le thème natal en free, **tous les calculs astrologiques sont toujours réalisés** ; seule la génération textuelle est restreinte au variant "free" (summary + ni-accordion-title uniquement). Pour basic/premium, la génération complète est produite.

**FR64-3 :** La restriction de contenu est effective côté backend au niveau de la sélection du prompt — le LLM ne génère réellement que ce qui est autorisé pour le plan (pas de génération complète masquée côté UI).

### Source de vérité et configuration

**FR64-4 :** Les règles métier d'abonnement (features, quotas, variants d'accès, droits, plan cible d'upgrade) sont issues de la base de données. La sélection technique du modèle LLM reste configurable via `.env` à ce stade — ces deux périmètres sont distincts et ne se contredisent pas.

**FR64-10 :** Le moteur LLM est configurable par plan et use case via clés `.env` dédiées (ex : `OPENAI_ENGINE_HOROSCOPE_DAILY_FREE`, `OPENAI_ENGINE_HOROSCOPE_DAILY_FULL`), structure extensible depuis Epic 59.3.

### Upgrade Hints (contrat backend → frontend)

**FR64-5 :** Le backend expose des "upgrade hints" dans le snapshot entitlements avec le contrat suivant :
```
{
  feature_code: str,
  current_plan_code: str,
  target_plan_code: str,
  benefit_key: str,        # clé de message i18n côté frontend
  cta_variant: Literal["banner", "inline", "modal"],
  priority: int            # ordre d'affichage si plusieurs hints
}
```
Ces hints sont calculés dynamiquement depuis le catalog en base. Le frontend pilote les CTA sans contenir de logique métier de plan.

**FR64-13 :** L'enrichissement de `/v1/entitlements/me` avec `upgrade_hints` est **additif** (backward compatible) — les consommateurs existants de l'endpoint ne sont pas impactés.

### Frontend — Affichage par plan

**FR64-6 :** La page `/chat` affiche pour l'utilisateur free un encart dynamique (messages restants, quota total, période de rechargement) alimenté par les entitlements.

**FR64-7 :** La page `/dashboard/horoscope` affiche pour free uniquement la section résumé générée ; les autres sections affichent un contenu teaser fixe, visuellement floutées/lockées. **Les sections lockées ne sont pas générées côté LLM**.

**FR64-8 :** Le thème natal affiche pour free uniquement summary + ni-accordion-title générés, **tous les calculs astrologiques étant conservés** ; les autres sections affichent un contenu teaser fixe et sont floutées/lockées. Exceptions : `ni-evidence-tags` et disclaimer toujours visibles et inchangés.

**FR64-9 :** Les pages stratégiques affichent des CTA d'upgrade contextualisés (free→basic, basic→premium) pilotés par les upgrade hints du backend.

**FR64-11 :** Le frontend ne contient aucune logique métier de plan ; il consomme les entitlements structurés du backend pour décider quoi afficher, flouter ou masquer.

**FR64-12 :** Les contenus floutés sont des contenus fixes (teaser/marketing), jamais du contenu utilisateur généré incomplet.

---

## Exigences Non-Fonctionnelles (NFR64)

**NFR64-1 (objectif d'implémentation) :** La résolution du snapshot entitlements avec les nouvelles features ne dégrade pas les performances — indicateur de référence : p95 < 200ms additionnel sur l'endpoint existant.

**NFR64-2 :** La sélection du prompt et du moteur LLM par plan est testable unitairement et intégrativement.

**NFR64-3 :** Toute nouvelle feature est enregistrée dans `FEATURE_SCOPE_REGISTRY` avant utilisation.

**NFR64-4 :** Les upgrade hints exposent un `target_plan_code` issu du catalog en base. Les textes de bénéfice sont gérés via des `benefit_key` (clés de message) — le stockage en base est pour les métadonnées, la présentation textuelle est résolue par le frontend via i18n.

**NFR64-5 :** Implémentation incrémentale : aucune régression pour les utilisateurs basic et premium dont le comportement ne change pas.

---

## Exigences Architecture

- Respecter la séparation domain/services/infra : logique plan dans `services/`, pas dans `api/`
- `FEATURE_SCOPE_REGISTRY` = source unique de vérité pour les feature_codes
- Nommage : snake_case pour feature_codes, PascalCase pour les classes gate
- Tests unit + integration obligatoires pour tout nouveau gate et service
- Pattern `ChatEntitlementGate` / `NatalChartLongEntitlementGate` comme référence d'implémentation
- Changements additifs sur `/v1/entitlements/me` (backward compatibility garantie)

---

## Exigences UX (UX64)

**UX64-1 :** Sections lockées avec UX premium : blur CSS + overlay icône lock + CTA non intrusif (ne masque pas le contenu visible).

**UX64-2 :** CTA upgrade contextualisé : mentionner la fonctionnalité spécifique débloquée par l'upgrade (issu du `benefit_key`).

**UX64-3 :** Encart quota chat discret et informatif tant que quota non épuisé.

**UX64-4 :** Quota épuisé → message clair + CTA upgrade immédiatement visible.

**UX64-5 :** Contenus teaser dans sections lockées écrits comme marketing aspirationnel (pas message d'erreur) — définis dans les fichiers i18n.

**UX64-6 :** Sur mobile, CTA upgrade ne doit pas obstruer la navigation ou le contenu principal.

---

## FR Coverage Map

| FR | Story | Description |
|---|---|---|
| FR64-1 | 64.1 + 64.2 | Gate horoscope_daily + prompt variant LLM |
| FR64-2 | 64.3 | Variant natal free (calculs conservés, texte restreint) |
| FR64-3 | 64.2 + 64.3 | Backend génère réellement selon le plan |
| FR64-4 | 64.1 + 64.4 | Source DB pour métier, .env pour LLM engine |
| FR64-5 | 64.4 | Upgrade hints dans EntitlementsMeResponse |
| FR64-6 | 64.7 | ChatPage quota banner |
| FR64-7 | 64.8 | DailyHoroscopePage sections lockées |
| FR64-8 | 64.9 | NatalChartPage sections lockées |
| FR64-9 | 64.6 + 64.7 + 64.8 + 64.9 | CTA upgrade sur pages stratégiques |
| FR64-10 | 64.2 | Config .env engine LLM par use case + plan |
| FR64-11 | 64.5 | Hook useEntitlementSnapshot frontend |
| FR64-12 | 64.8 + 64.9 | Contenus teaser fixes dans sections lockées |
| FR64-13 | 64.4 | Backward compatibility sur /v1/entitlements/me |
| NFR64-1 | 64.1 + 64.4 | Perf snapshot resolution |
| NFR64-2 | 64.1 + 64.2 + 64.3 | Testabilité unitaire et intégrative |
| NFR64-3 | 64.1 | FEATURE_SCOPE_REGISTRY |
| NFR64-4 | 64.4 + 64.5 | benefit_key via i18n |
| NFR64-5 | toutes | Incrémental, zéro régression |
| UX64-1..6 | 64.6 + 64.7 + 64.8 + 64.9 | UX locked sections + CTA |

---

## Séquence et dépendances

```
64.1 — Backend: Feature horoscope_daily + gate + variant_code
  ↓
64.2 — Backend: Prompts variants horoscope par plan + .env engine config
  ↓
64.3 — Backend: Prompt variant thème natal free (calculs conservés, texte restreint)
  ↓
64.4 — Backend: upgrade_hints dans EntitlementsMeResponse (additif, backward compat)
  ↓
64.5 — Frontend: hook useEntitlementSnapshot + types upgrade_hints
  ↓
64.6 — Frontend: composants UpgradeCTA + LockedSection (réutilisables)
  ↓
64.7 — Frontend: ChatPage — encart quota dynamique + CTA upgrade (dépend 64.5)
64.8 — Frontend: DailyHoroscopePage — sections lockées + CTA (dépend 64.5 + 64.6)
64.9 — Frontend: NatalChartPage — sections lockées + CTA (dépend 64.5 + 64.6)
```

64.7, 64.8, 64.9 peuvent être développées en parallèle une fois 64.5 + 64.6 terminées.

---

## Avancement au 2026-04-04

Les fondations backend/frontend de l'epic sont en place et stabilisées :

- Stories terminées : `64.1`, `64.2`, `64.3`, `64.4`, `64.5`
- Hardening complémentaire effectué après intégration :
  - compatibilité legacy du gate `horoscope_daily` pour préserver les flux et tests V4 existants ;
  - compatibilité du resolver/endpoint entitlements quand le `feature_catalog` est absent, vide ou partiellement seedé ;
  - correction de la consommation canonique des quotas chat tokens ;
  - alignement des `upgrade_hints.benefit_key` sur les clés i18n frontend ;
  - isolation du cache frontend `useEntitlementSnapshot` par sujet authentifié ;
  - stabilisation des tests de charge/concurrence via reset du cache billing et neutralisation du scheduler sous `pytest`.

Conséquence : l'ensemble de la suite de tests est verte après intégration des stories fondation de l'epic.

Finalisation UX complémentaire sur `64.9` :

- correction du flux free natal pour empêcher toute relance de génération "complète" depuis les CTA verrouillés ;
- alignement du rendu sur le cahier des charges produit : summary visible, titres issus de l'interprétation complète, badge de niveau non trompeur, sections détaillées affichées comme faux contenu fixe flouté ;
- CTA d'upgrade affiché sur chaque section lockée du thème natal et routé directement vers l'abonnement Basic ;
- hardening backend du variant `free_short` pour réutiliser la version persistée existante au lieu de provoquer un doublon SQL ;
- enrichissement du contrat `free_short` avec une vraie phrase de synthèse `title` générée côté backend, utilisée comme en-tête du cadre résumé à la place du label statique `Résumé`.

Validation finale produit :

- rendu free natal validé en test manuel après ajustements visuels finaux ;
- carte résumé désormais conforme à la maquette attendue : pas de label générique, accroche synthétique générée dans le cadre ;
- comportement d'upgrade confirmé : les CTA free redirigent vers l'abonnement Basic sans relancer une génération non autorisée.
- correction complémentaire du parcours `/settings/subscription` : un utilisateur free exposé comme plan applicatif `free` mais sans profil Stripe est désormais routé vers un Checkout Stripe initial, et non plus vers le Customer Portal.
- correction complémentaire du flux Basic sur `/natal` : une fois le quota d'interprétation complète consommé, l'interface n'autorise plus de nouvelle génération et remplace le bouton inactif par un CTA explicite vers Premium pour obtenir davantage de quota.
- correction complémentaire du quota chat Basic : un premier message dont le coût réel dépasse le budget journalier en tokens ne provoque plus un rollback incohérent (`0 utilisé` mais `quota dépassé`) ; le compteur est désormais saturé à la limite puis l'échange suivant est bloqué normalement.
- correction complémentaire du comptage LLM natal : les tokens consommés par les interprétations natales restent journalisés par utilisateur pour l'observabilité, mais ne sont plus déduits du quota `astrologer_chat`.

---

## Stories de l'Epic 64

| Story | Titre | Domaine | Fichier |
|---|---|---|---|
| 64.1 | Feature `horoscope_daily` + gate backend + variants par plan | Backend | [64-1-feature-horoscope-daily-gate-variants.md](../implementation-artifacts/64-1-feature-horoscope-daily-gate-variants.md) |
| 64.2 | Prompts variants horoscope par plan + config LLM engine via .env | Backend / LLM | [64-2-prompts-variants-horoscope-config-llm-env.md](../implementation-artifacts/64-2-prompts-variants-horoscope-config-llm-env.md) |
| 64.3 | Prompt variant thème natal free — calculs conservés, texte restreint | Backend / LLM | [64-3-prompt-variant-natal-free-calculs-conserves.md](../implementation-artifacts/64-3-prompt-variant-natal-free-calculs-conserves.md) |
| 64.4 | Upgrade hints dans EntitlementsMeResponse (backward compatible) | Backend | [64-4-upgrade-hints-entitlements-me.md](../implementation-artifacts/64-4-upgrade-hints-entitlements-me.md) |
| 64.5 | Hook `useEntitlementSnapshot` + types upgrade hints côté frontend | Frontend | [64-5-hook-useEntitlementSnapshot-types-upgrade-hints.md](../implementation-artifacts/64-5-hook-useEntitlementSnapshot-types-upgrade-hints.md) |
| 64.6 | Composants `UpgradeCTA` + `LockedSection` réutilisables | Frontend | [64-6-composants-UpgradeCTA-LockedSection.md](../implementation-artifacts/64-6-composants-UpgradeCTA-LockedSection.md) |
| 64.7 | ChatPage — encart quota dynamique + CTA upgrade | Frontend | [64-7-chatpage-quota-banner-cta-upgrade.md](../implementation-artifacts/64-7-chatpage-quota-banner-cta-upgrade.md) |
| 64.8 | DailyHoroscopePage — sections lockées free + CTA upgrade | Frontend | [64-8-dailyhoroscopepage-sections-lockees-cta.md](../implementation-artifacts/64-8-dailyhoroscopepage-sections-lockees-cta.md) |
| 64.9 | NatalChartPage — sections lockées free + CTA upgrade | Frontend | [64-9-natalchartpage-sections-lockees-cta.md](../implementation-artifacts/64-9-natalchartpage-sections-lockees-cta.md) |

---

## Fichiers clés impactés

```
backend/app/services/feature_scope_registry.py     ← 64.1 : ajout horoscope_daily
backend/app/services/horoscope_daily_entitlement_gate.py  ← 64.1 : nouveau
backend/app/api/v1/routers/predictions.py         ← 64.1 : branchement gate horoscope_daily
backend/app/prompts/catalog.py                     ← 64.2 + 64.3 : nouveaux variants
backend/app/services/prediction_compute_runner.py  ← 64.2 : sélection variant
backend/app/services/natal_interpretation_service_v2.py ← 64.3 : variant free
backend/app/services/llm_token_usage_service.py ← hardening : distinction entre journalisation LLM et consommation quota
backend/app/services/quota_usage_service.py      ← hardening : consommation capée pour saturation contrôlée des quotas chat tokens
backend/app/api/v1/schemas/entitlements.py         ← 64.4 : UpgradeHint + champ additionnel
backend/app/services/effective_entitlement_resolver_service.py ← 64.4 : compute hints
backend/app/api/v1/routers/chat.py                ← 64.4 : consommation correcte des quotas canoniques
backend/app/services/auth_service.py              ← hardening : invalidation cache billing sur création user
backend/app/core/scheduler.py                     ← hardening : neutralisation scheduler sous pytest
backend/.env.example                               ← 64.2 : nouvelles clés engine
frontend/src/api/billing.ts                        ← 64.5 : types UpgradeHint
frontend/src/hooks/useEntitlementSnapshot.ts       ← 64.5 : nouveau hook
frontend/src/components/ui/UpgradeCTA/             ← 64.6 : nouveau composant
frontend/src/components/ui/LockedSection/          ← 64.6 : nouveau composant
frontend/src/pages/ChatPage.tsx                    ← 64.7 : ChatQuotaBanner
frontend/src/pages/DailyHoroscopePage.tsx          ← 64.8 : sections lockées
frontend/src/pages/NatalChartPage.tsx              ← 64.9 : sections lockées
frontend/src/i18n/billing.ts                       ← 64.5 : benefit_key labels + upgrade CTA strings
frontend/src/i18n/horoscope_copy.ts               ← 64.8 : teaser content keys sections lockées daily
frontend/src/i18n/natalChart.ts                   ← 64.9 : teaser content keys sections lockées natal
```
