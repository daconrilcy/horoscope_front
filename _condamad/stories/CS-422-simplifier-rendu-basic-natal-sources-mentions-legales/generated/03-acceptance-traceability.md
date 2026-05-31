# Acceptance traceability - CS-422

<!-- Commentaire global: ce fichier relie chaque critere d'acceptation CS-422 aux changements et validations executables. -->

| AC | Requirement | Status | Code evidence | Validation evidence |
|---|---|---|---|---|
| AC1 | Basic V2 renders report sections in reading order. | PASS | `BasicV2Reading` rend titre, introduction, themes, conclusion, annexe sources puis zone legale. | `pnpm --dir frontend test -- natalInterpretation natalPublicDomGuard NatalChartPage natalNarrativeReading` PASS. |
| AC2 | Basic V2 themes do not render inline evidence blocks. | PASS | Suppression de l'appel `PublicEvidenceList` dans chaque `.ni-basic-theme`; collecte par `collectBasicPublicEvidence`. | Tests DOM: absence de source dans `.ni-basic-theme-list`; scan inline legacy PASS. |
| AC3 | Basic V2 renders one public source appendix. | PASS | `PublicEvidenceList` est rendu une seule fois apres la conclusion Basic V2. | Tests: un seul titre `Ce que j’ai utilise...`. |
| AC4 | Basic V2 deduplicates repeated evidence entries. | PASS | Dedupe par `source_id`, sinon `source_type + label + meaning` normalises via `getEvidenceKey`. | Tests multi-themes: sources dupliquees visibles une seule fois. |
| AC5 | Shared Basic V2 evidence keeps compact usage metadata. | PASS | `usedInSections` fusionne titre de theme, `theme` et `used_in_sections`. | Test: `Utilise dans : Axe personnel, Axe relationnel`. |
| AC6 | Basic V2 renders one final legal area. | PASS | `mergePublicLegalLines` fusionne limitations, disclaimers Basic et lignes legales globales; footer global masque pour Basic V2. | Tests: un seul titre `Mentions legales`, lignes dupliquees dedoublonnees. |
| AC7 | Basic V2 main paragraphs exclude raw source text. | PASS | Le corps `.ni-basic-theme-list` ne rend plus les sources. | Tests DOM + scan technique denylist PASS. |
| AC8 | Free short keeps its existing public rendering. | PASS | `FreePublicReading` et footer legal non Basic conserves. | Suite cible `natalInterpretation NatalChartPage` PASS. |
| AC9 | Narrative v1 keeps accessible modern accordions. | PASS | `NatalNarrativeReading` et `NatalReadingSources` non modifies. | Suite cible `natalNarrativeReading NatalChartPage` PASS. |
| AC10 | Touched TSX surfaces do not add inline styles. | PASS | Styles dans `NatalInterpretation.css`; aucun `style={` TSX. | `rg -n "style=\\{" ...` PASS no matches; `git diff --check` PASS. |
| AC11 | Public DOM excludes technical markers. | PASS | Aucun marqueur technique ajoute. | `rg` denylist PASS no matches; `natalPublicDomGuard` PASS. |

## Guardrails

- RG-048: PASS_WITH_LIMITATIONS sur scan large a cause d'un fallback preexistant dans `frontend/src/styles/app/base.css`; scan du CSS touche PASS.
- RG-073: PASS, owner conserve.
- RG-153/RG-154/RG-158/RG-168/RG-170: PASS via tests DOM, lint/build et scans.
