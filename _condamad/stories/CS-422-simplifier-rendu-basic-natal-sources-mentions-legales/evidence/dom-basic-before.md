# Baseline avant implementation - CS-422

<!-- Commentaire global: ce fichier conserve la baseline pre-implementation reconstituee depuis la story et le diff Git. -->

Capture DOM executable non prise avant edition. Baseline compensee par:

- `00-story.md` Current State Evidence 7: `PublicEvidenceList` etait rendu dans chaque theme Basic V2.
- `git show HEAD:frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` montrait `PublicEvidenceList embedded evidence={theme.public_evidence}` dans `.ni-basic-theme`.
- Le meme fichier rendait ensuite `PublicEvidenceList evidence={publicEvidence}`, puis limitations, `PublicDisclaimers`, puis le footer global `Mentions legales`.

Etat attendu avant correction: repetition des sources theme + annexe, et deux zones/titres legaux possibles.
