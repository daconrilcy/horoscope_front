# Story 16.5: Consultations Thématiques — Pages et Wizard (REFONDU / EPIC 46)

> [!IMPORTANT]
> Le périmètre de cette story a été refondu dans l'Epic 46 (mars 2026).
> Les consultations n'incluent plus de tirage (tarot/runes) et le wizard comporte désormais 3 étapes au lieu de 4.

Status: done (refactored)

## Story

As a utilisateur,
I want créer des consultations thématiques (dating, pro, événement) sans tirage,
So that je puisse obtenir des guidances spécialisées structurées et les partager dans le chat.

## Contexte

Cette story crée des pages dédiées pour les consultations thématiques avec un wizard de création structuré. Elle a été simplifiée dans l'Epic 46 pour se concentrer sur la guidance astrologique ciblée.

## Scope (Post-Epic 46)

### In-Scope
- Page `/consultations` avec liste des types et historique
- Page `/consultations/new` avec wizard multi-step (3 étapes)
- Page `/consultations/result` pour résultat structuré
- Wizard steps : type → astrologue → validation (demande)
- CTAs résultat : "Ouvrir dans le chat", "Sauvegarder"
- Types : Dating, Pro, Événement, Question libre
- Modèle de données structuré : summary, keyPoints, actionableAdvice

### Out-of-Scope (Retiré dans Epic 46)
- Notions de tirage (cartes, runes)
- Étape `DrawingOptionStep`
- Rendu des cartes ou runes dans le résultat

## Acceptance Criteria (Actualisés)

### AC1: Liste consultations
**Given** un utilisateur sur `/consultations`
**When** la page se charge
**Then** il voit les types de consultation disponibles
**And** son historique de consultations (si disponible)

### AC2: Wizard step 1 - Type
**Given** un utilisateur sur `/consultations/new`
**When** il choisit un type (Dating, Pro, Événement, Libre)
**Then** il passe au step 2

### AC3: Wizard step 2 - Astrologue
**Given** le step 2 du wizard
**When** l'utilisateur sélectionne un astrologue (ou "auto")
**Then** il passe au step 3 (Validation)

### AC4: Wizard step 3 - Validation (Demande)
**Given** le step 3 du wizard
**When** l'utilisateur saisit son contexte et valide
**Then** la guidance est générée
**And** il est redirigé vers la page résultat

### AC5: Page résultat structuré
**Given** un utilisateur sur la page résultat
**When** la page se charge
**Then** il voit : type, astrologue, contexte, et la guidance structurée (interprétation, points clés, conseils)
**And** deux CTAs : "Ouvrir dans le chat", "Sauvegarder"

## Tasks (Actualisées)

- [x] Task 1: Créer state wizard (AC: #2-4)
- [x] Task 2: Créer composants wizard (AC: #2-4)
- [x] Task 3: Créer pages (AC: #1, #5)
- [x] Task 4: Intégration API (AC: #4, #5)
- [x] Task 5: Tests (AC: tous)

## Dev Agent Record

### Agent Model Used
Claude Opus 4.5 / Gemini 2.0 Flash (Refonte Epic 46)

### completion Notes List
- Implémentation initiale du wizard 4 steps (Février 2026).
- Refonte complète vers 3 étapes sans tirage (Mars 2026 - Epic 46).
- Passage à un modèle de données structuré (points clés, conseils).
- Migration de l'historique localStorage assurée.
