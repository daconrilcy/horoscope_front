# Plan d'implementation CS-340

<!-- Commentaire global: ce plan garde le fil de validation de la frontiere prompt/audit sans elargir le perimetre applicatif. -->

## Approche

1. Verifier que `CS-339` est `done` dans `_condamad/stories/story-status.md`.
2. Capturer un scan baseline des termes `provenance`, `projection_hash`, `llm_input_hash`, `audit_only` et `prompt_visible`.
3. Executer les tests backend ciblant le contrat, le gateway, les hashes, l'audit persistant et les guards legacy.
4. Executer les scans negatifs sur les placeholders modernes natals.
5. Produire le rapport timestampé sous `_condamad/reports/frontiere-provenance-prompt-audit-llm-natal/`.
6. Synchroniser traceabilite AC, evidence finale et statut de story.

## Frontiere No Legacy

- Aucun fichier frontend, API publique, migration ou dependance ne doit changer.
- Aucun shim, fallback silencieux ou chemin `chart_json` / `natal_data` ne doit etre ajoute.
- Les occurrences restantes des termes d'audit doivent etre classees par ownership plutot que supprimees aveuglement.
