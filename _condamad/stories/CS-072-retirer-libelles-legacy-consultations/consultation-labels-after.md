<!-- Preuve after de suppression du vocabulaire legacy des libelles consultations. -->

# CS-072 Consultation Labels After

## Decisions finales

| Cle | Langue | Libelle final | Classification | Decision |
|---|---|---|---|---|
| `type_dating` | `fr` | `Dating / Rendez-vous amoureux` | `canonical-active` | `keep` |
| `type_dating` | `en` | `Dating / Romantic meetup` | `canonical-active` | `keep` |
| `type_dating` | `es` | `Cita / Encuentro romántico` | `canonical-active` | `keep` |
| `type_pro` | `fr` | `Choix professionnel` | `canonical-active` | `keep` |
| `type_pro` | `en` | `Professional choice` | `canonical-active` | `keep` |
| `type_pro` | `es` | `Elección profesional` | `canonical-active` | `keep` |
| `type_event` | `fr` | `Événement important` | `canonical-active` | `keep` |
| `type_event` | `en` | `Important event` | `canonical-active` | `keep` |
| `type_event` | `es` | `Evento importante` | `canonical-active` | `keep` |
| `type_free` | `fr` | `Question libre` | `canonical-active` | `keep` |
| `type_free` | `en` | `Free question` | `canonical-active` | `keep` |
| `type_free` | `es` | `Pregunta libre` | `canonical-active` | `keep` |

## Commandes after

| Commande | Repertoire | Resultat | Synthese |
|---|---|---|---|
| `rg -n "legacy\|Legacy" src/i18n/consultations.ts` | `frontend` | PASS, exit 1 | Zero hit dans la source i18n consultation. |
| `npm run test -- legacy-style AstrologersPage ConsultationMigration consultationStore design-system theme-tokens css-fallback visual-smoke HelpPage` | `frontend` | PASS, exit 0 | 9 fichiers, 165 tests passes, dont `ConsultationMigration` et `consultationStore`. |
| `npm run lint` | `frontend` | PASS, exit 0 | TypeScript lint configs OK. |

## No Legacy

Aucun libelle `(Legacy)` n'est conserve comme copie de compatibilite. Les cles
et identifiants metier restent inchanges.
