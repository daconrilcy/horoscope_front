# Story CS-174 localiser-libelles-astrologiques-backend: Localiser les libellés de signes astrologiques backend depuis `astral_sign_translations`

Status: ready-to-dev

## 1. Objectif

Faire de `users.default_language_id`, d'une langue explicitement demandée et de la table
`astral_sign_translations` la source de vérité des libellés de signes astrologiques restitués par le backend.
Les DTO publics et les contextes LLM conservent les codes canoniques stables, tout en
exposant ou consommant un libellé résolu selon la langue effective.

## 2. Déclencheur / Source

- Type de source: brief
- Référence source: demande utilisateur du 2026-05-16 sur la suppression de `SIGN_NAMES_FR` et l'usage de `astral_sign_translations`.
- Raison du changement: plusieurs services backend reconstruisent encore les noms français des
  signes via des constantes locales alors que les référentiels canoniques et leurs traductions
  existent déjà en base.

## 3. Frontière de domaine

Cette story appartient à un seul domaine:

- Domaine: `backend/app/services` - restitution localisée des libellés de signes astrologiques.
- Dans le périmètre:
  - Créer ou réutiliser un resolver service/infra pour résoudre les libellés de signes depuis `languages` et `astral_sign_translations`.
  - Brancher les builders chart, natal et LLM ciblés sur ce resolver ou sur un objet
    `AstrologyLabels` déjà résolu.
  - Conserver dans les payloads les codes canoniques et ajouter les libellés localisés nécessaires sans renommer les champs code historiques; utiliser `*_code` + `*_label` seulement quand aucun champ code historique explicite n'existe.
  - Appliquer l'ordre de résolution: langue API explicite, langue utilisateur, langue système `fr`, puis code canonique.
- Hors périmètre:
  - Traduire tous les contenus éditoriaux des profils astrologiques.
  - Localiser les libellés de planètes, maisons, aspects et angles, même si leurs tables de traduction existent déjà.
  - Migrer `PLANET_NAMES_FR`, `ASPECT_NAMES_FR` ou les libellés français non liés aux signes.
  - Migrer `NatalPdfExportService.SIGN_LABELS`; ce mapping PDF existant reste hors périmètre de cette story et devra faire l'objet d'une story dédiée si la localisation PDF doit devenir DB-backed.
  - Modifier les algorithmes de calcul zodiacal ou l'ordre des signes.
  - Changer la table canonique `astral_signs` ou les seeds de référence hors tests nécessaires.
  - Déplacer la localisation vers `backend/app/domain/astrology`.
- Non-objectifs explicites:
  - Ne pas modifier `backend/app/domain/astrology/zodiac.py` sauf si un test révèle une rupture indépendante du périmètre.
  - Ne pas modifier `backend/app/domain/astrology/natal_calculation.py` pour ajouter des libellés affichables.
  - Ne pas changer `sign_from_longitude(longitude)`: il continue à retourner uniquement un code canonique comme `"aries"`.
  - Ne pas introduire de nouvelle constante backend concurrente du type `SIGN_NAMES_FR`.
  - Ne pas modifier les invariants `RG-091` à `RG-108` des référentiels astrologiques DB-backed.
  - Ne pas créer de fallback legacy silencieux: chaque fallback autorisé doit suivre l'ordre explicite du contrat et être couvert par test.

## 4. Contrat d'opération

- Type d'opération: replace-runtime-source
- Archétype principal: contract-enrichment + dead-code-removal
- Raison de l'archétype: la story remplace les constantes et exports de libellés de signes codés en dur par un propriétaire runtime canonique, puis enrichit les surfaces ciblées avec des libellés localisés sans supprimer les codes existants.
- Changement de comportement autorisé: contraint
- Contraintes de changement de comportement:
  - Les codes techniques existants restent stables pour les règles métier, tests et prompts structurés.
  - Les libellés affichables peuvent changer selon la langue effective.
  - Les payloads publics enrichis doivent conserver les champs historiques requis et ajouter les champs de libellé sans supprimer les codes.
  - Le fallback technique final `sign.code` est autorisé uniquement après échec des langues demandée, utilisateur et système.
- Suppression autorisée: oui
- Remplacement autorisé: oui
- Décision utilisateur requise si: une surface publique existante doit supprimer un champ historique au lieu d'ajouter un champ `*_label`.

## 4a. Contrats requis

| Contrat | Requis | Raison |
|---|---:|---|
| Source de vérité runtime | oui | Les libellés de signes doivent venir des tables runtime `languages` et `astral_sign_translations`. |
| Snapshot baseline | oui | Les constantes actuelles et la forme des payloads doivent être capturées avant/après. |
| Routage d'ownership | oui | La localisation appartient au resolver service/infra, pas aux builders ni au domaine pur. |
| Exception d'allowlist | non | Aucune exception durable de constante codée en dur n'est autorisée dans les surfaces ciblées. |
| Forme du contrat | oui | Les DTO/payloads ciblés doivent préciser les champs de code conservés et les champs de libellé ajoutés par surface. |
| Migration batch | non | Aucune migration de données n'est attendue. |
| Guard anti-réintroduction | oui | Un guard doit empêcher le retour de mappings `SIGN_NAMES_FR` dans le backend applicatif. |
| Preuve persistante | oui | Story, registre et tests ciblés constituent la preuve durable. |

## 4b. Source de vérité runtime

- Source de vérité principale: schéma DB / métadonnées SQLAlchemy reflétées des tables `languages`, `astral_signs` et `astral_sign_translations`, plus guard AST sur les imports de domaine.
- Preuve secondaire: tests unitaires/intégration du resolver, snapshot ciblé du JSON chart et scans négatifs des constantes codées en dur.
- Les scans statiques seuls ne suffisent pas: ils prouvent l'absence de constante, mais pas que la résolution respecte la langue utilisateur et les fallbacks runtime.
- Source runtime: session SQLAlchemy active du service appelant, avec préférence `users.default_language_id` si aucun `language_code` API n'est fourni.
- Fallback de langue système: `fr`. Le resolver doit chercher une ligne `languages.code == "fr"` et utiliser ses traductions avant de tomber sur `sign.code`.
- Implémentation requise: un propriétaire unique de résolution expose des libellés de signes par
  code canonique, en appliquant l'ordre langue explicite, langue utilisateur, langue système `fr`,
  puis `sign.code`.
- Source interdite: `SIGN_NAMES_FR`, mapping local de signes, JSON applicatif autonome pour les libellés runtime.

## 4c. Règle baseline / avant-après

- Baseline requis: oui.
- Artefact baseline avant implémentation: `_condamad/stories/CS-174-localiser-libelles-astrologiques-backend/generated/01-baseline-sign-localization.md`.
- Contenu du baseline: scan ciblé de `SIGN_NAMES_FR`, `_longitude_to_sign`, `SIGN_LABELS`,
  `sign_label` et `sign_code` dans `backend/app/services`, `backend/app/domain/astrology` et
  `backend/app/tests`, avec mention explicite que `NatalPdfExportService.SIGN_LABELS` est hors périmètre.
- Comparaison après implémentation: mêmes scans ciblés plus tests du resolver et tests des consommateurs migrés.
- Invariant attendu: `sign_from_longitude(longitude)` et les calculateurs astrology continuent de retourner des codes.
- Preuve avant: `json_builder.py`, `astro_context_builder.py` et `natal_context.py` contiennent ou importent `SIGN_NAMES_FR`.
- Preuve après: les surfaces ciblées ne contiennent plus de mapping de signes codé en dur et consomment un resolver ou un objet `AstrologyLabels`.
- Différences autorisées: ajout de champs `*_label` dans les DTO/payloads publics et variation localisée des textes LLM.

## 4d. Règle de routage d'ownership

| Type de responsabilité | Propriétaire canonique | Destination interdite |
|---|---|---|
| Résolution des libellés de signes | `backend/app/services/reference_data/astrology_translation_resolver.py` | `backend/app/domain/astrology/**`, builders JSON, prompts LLM |
| Préférence langue utilisateur | `users.default_language_id` via `UserModel.default_language` | constante locale ou paramètre global non relié à l'utilisateur |
| Projection chart JSON | `backend/app/services/chart/json_builder.py` | lookup SQL direct dispersé dans chaque boucle |
| Contexte natal LLM | `backend/app/services/llm_generation/shared/natal_context.py` | constante `SIGN_NAMES_FR` exportée |
| Contexte astro daily/weekly | `backend/app/services/natal/astro_context_builder.py` | import de constantes de traduction |

- Propriétaire canonique: resolver service/infra injecté depuis les services orchestrateurs qui disposent d'une session DB ou d'un `AstrologyLabels` déjà résolu.
- Règle de routage: les consommateurs ne doivent pas importer les modèles SQLAlchemy directement s'ils peuvent recevoir un objet `AstrologyLabels` déjà résolu.

## 4e. Allowlist / registre d'exceptions

- Exception d'allowlist: non applicable.
- Raison: aucune constante de libellés de signes DB-backed ne doit rester dans les surfaces applicatives ciblées. Les mappings PDF existants sont exclus de cette story et doivent être documentés comme hors périmètre dans le baseline.

## 4f. Forme du contrat

- Type de contrat:
  - Payload JSON backend et contrats internes de contexte LLM.
- Champs:
  - `sign_code: str` - code canonique stable issu de `astral_signs.code`.
  - `sign_label: str` - libellé localisé issu de `astral_sign_translations.translated_name`, puis fallback explicite.
  - `language_code: str | None` - langue demandée explicitement quand la surface API l'accepte.
  - `effective_language_code: str` - langue effectivement utilisée par le resolver quand exposée en méta ou testée.
- Champs requis:
  - Tout nouveau champ exposant un libellé doit conserver le code associé.
  - Les champs de code existants restent requis quand ils l'étaient déjà.
- Champs optionnels:
  - `language_code` côté entrée API/service si la surface n'a pas de langue explicite.
  - `effective_language_code` seulement si la surface possède déjà un bloc meta adapté.
- Codes de statut:
  - Aucun nouveau code de statut HTTP: cette story ne crée pas de route HTTP.
- Noms de sérialisation:
  - `sign_code` et `sign_label` pour les nouveaux couples de signes quand aucun champ code historique explicite n'existe.
  - Les champs historiques `sign`, `cusp_sign`, `ruler_planet_sign` restent en code pour compatibilité.
  - Tout affichage ajouté doit avoir son champ de libellé explicite.
- Mapping requis par surface:

| Surface | Champ code existant conservé | Champ libellé à ajouter ou consommer | Notes |
|---|---|---|---|
| `chart_json.planets[]` | `sign` | `sign_label` | `sign` reste le code canonique historique. |
| `chart_json.houses[]` | `cusp_sign` et champ historique `sign` | `cusp_sign_label` | `sign` continue à refléter `cusp_sign`; aucun `sign_code` séparé requis. |
| `chart_json.house_rulers[]` | `cusp_sign`, `ruler_planet_sign` | `cusp_sign_label`, `ruler_planet_sign_label` | Les champs historiques ne sont pas renommés. |
| `chart_json.angles.*` | `sign` | `sign_label` | Les entrées `None` restent inchangées. |
| Libellés du catalogue d'évidence | IDs d'évidence existants | libellés de signes résolus depuis `AstrologyLabels` | Les IDs restent construits depuis les codes. |
| Résumés et indications de `natal_context.py` | codes de signes existants dans les objets source | libellés lus depuis `AstrologyLabels.sign_label(code)` | Le texte humain utilise la langue effective. |
| Texte de phase lunaire dans `astro_context_builder.py` | code du signe lunaire | libellé lu depuis `AstrologyLabels.sign_label(code)` | Aucun import de constante de traduction. |
- Impact sur les types frontend:
  - Aucun changement front obligatoire, sauf si un contrat généré expose les nouveaux champs.
- Impact sur le contrat généré:
  - Si une route publique de thème natal expose les payloads enrichis, l'OpenAPI doit refléter les champs ajoutés.
- Contrats API affectés:
  - Payloads de thème natal et de contexte natal seulement si déjà exposés par routes existantes.
- Contrat d'erreur:
  - Les erreurs API existantes ne changent pas.

## 4g. Plan de migration batch

- Migration batch: non applicable.
- Raison: les tables de traduction et `users.default_language_id` existent déjà.

## 4h. Artefacts de preuve persistante

- Preuves persistantes requises:
  - `_condamad/stories/story-status.md`
  - `_condamad/stories/regression-guardrails.md`
  - tests backend ciblés ajoutés ou mis à jour

| Artefact | Chemin | Objectif |
|---|---|---|
| Contrat de story | `_condamad/stories/CS-174-localiser-libelles-astrologiques-backend/00-story.md` | Cadrage exécutable de la migration des libellés. |
| Registre des stories | `_condamad/stories/story-status.md` | Numéro, statut et source de la story. |
| Registre des guardrails | `_condamad/stories/regression-guardrails.md` | Invariant empêchant le retour des libellés DB-backed codés en dur. |
| Scan baseline de localisation | `_condamad/stories/CS-174-localiser-libelles-astrologiques-backend/generated/01-baseline-sign-localization.md` | Preuve avant/après des constantes, champs et exclusions hors périmètre. |
| Tests du resolver | `backend/app/tests/unit/test_astrology_translation_resolver.py` | Preuve de résolution langue utilisateur, langue explicite et fallbacks. |
| Tests des consommateurs | Tests chart JSON et localisation natale | Preuve de consommation sans constantes locales. |

## 4i. Guard anti-réintroduction

- Guard requis: oui.
- Forme du guard: guard d'architecture sur symboles interdits et scan ciblé échouant si `SIGN_NAMES_FR`
  est réintroduit dans les surfaces ciblées de `backend/app/services` ou si `app.domain.astrology` importe le resolver.
- Périmètre du guard: `backend/app/services/chart`, `backend/app/services/natal/astro_context_builder.py`,
  `backend/app/services/llm_generation/shared/natal_context.py` et
  `backend/app/services/llm_generation/natal/prompt_context.py`.
- Exception explicite du guard: `backend/app/services/natal/pdf_export_service.py::SIGN_LABELS` est hors périmètre pour cette story et doit être ignoré uniquement avec une assertion/documentation explicite du test de garde.
- Preuves exécutables:
  - Depuis `backend/`: `pytest -q app/tests/unit/test_astrology_translation_resolver.py app/tests/unit/test_chart_json_builder.py app/tests/unit/test_natal_context_localization.py`
  - Depuis `backend/`: `rg -n "SIGN_NAMES_FR|\\bSIGNS\\s*=\\s*\\[" app/services/chart app/services/natal/astro_context_builder.py app/services/llm_generation/shared/natal_context.py app/services/llm_generation/natal/prompt_context.py app/domain/astrology`
  - Depuis `backend/`: `rg -n "AstrologyTranslationResolver|astrology_translation_resolver" app/domain/astrology`
- Attente négative:
  - Premier scan: aucun hit nominal dans `app/services` hors tests de garde explicitement nommés.
  - Second scan: aucun hit dans `app/domain/astrology`.

## 4j. Clôture du finding source

- Statut de clôture: non applicable.
- Raison: cette story ne provient pas d'un finding d'audit.

## 5. État actuel / preuves

Le code ou l'audit courant indique:

- Preuve 1: `backend/app/services/chart/json_builder.py` - contient `SIGN_NAMES_FR` pour les
  libellés d'évidence des planètes, angles, maisons et maîtres de maisons.
- Preuve 2: `backend/app/services/natal/astro_context_builder.py` - importe `SIGN_NAMES_FR` depuis le contexte natal LLM pour libeller la phase lunaire.
- Preuve 3: `backend/app/services/llm_generation/shared/natal_context.py` - déclare `SIGNS` et `SIGN_NAMES_FR`, puis formate les résumés LLM en français codé en dur.
- Preuve 4: `backend/app/infra/db/models/translation_reference.py` - `AstralSignTranslationModel` existe avec `astral_sign_id`, `language_id` et `translated_name`.
- Preuve 5: `backend/app/infra/db/models/user.py` - `UserModel.default_language_id` référence `languages.id` et expose la relation `default_language`.
- Preuve 6: `backend/app/domain/astrology/zodiac.py` - `sign_from_longitude(longitude)`
  retourne un code canonique depuis l'ordre des signes, sans libellé affichable.
- Preuve 7: `backend/app/services/natal/pdf_export_service.py` - contient `SIGN_LABELS` pour le PDF, explicitement hors périmètre de cette story.
- Preuve N: `_condamad/stories/regression-guardrails.md` - invariants de régression consultés avant la finalisation du périmètre.

## 6. État cible

Après implémentation:

- Les services ciblés ne connaissent plus `SIGN_NAMES_FR`.
- Un resolver ou objet `AstrologyLabels` fournit les libellés à partir de `astral_sign_translations`.
- Les appels API/services peuvent fournir une langue explicite; sinon la préférence `users.default_language_id` est utilisée; sinon la langue système `fr`; sinon le code canonique.
- Les payloads ou contextes qui affichent un signe gardent le code stable et ajoutent un libellé localisé.
- Le domaine `backend/app/domain/astrology` reste pur et ne dépend pas de la localisation.

## 6a. Regression Guardrails

- Source des guardrails: `_condamad/stories/regression-guardrails.md`
- Invariants applicables:
  - `RG-095` - la localisation ne doit pas introduire de dépendance prediction ou service dans le domaine astrology.
  - `RG-106` - les calculateurs astrology ne doivent pas revenir à des constantes/fallbacks dispersés.
  - `RG-107` - les contrats runtime astrology restent typés et les JSON/DB libres ne traversent pas les frontières.
  - `RG-108` - un vocabulaire métier DB-backed ne doit pas être recréé en mapping local.
  - `RG-109` - les libellés de signes affichables doivent provenir des traductions DB ou du fallback technique explicite.
- Invariants non applicables:
  - `RG-083` à `RG-090` - la story ne modifie pas le frontend ni le design system.
  - `RG-091` à `RG-094` - la story ne recrée pas les anciens référentiels ni ne change les maîtres de maisons.
- Preuves de régression requises:
  - Tests du resolver et des consommateurs.
  - Scans négatifs `SIGN_NAMES_FR` et imports du resolver depuis `domain/astrology`.
  - Snapshot ciblé ou assertions JSON prouvant que chaque libellé ajouté conserve le champ code associé.
- Différences autorisées:
  - Ajout de libellés localisés dans les payloads/contexte.
  - Changement des textes LLM selon la langue effective.

## 7. Critères d'acceptation

| AC | Exigence | Preuve de validation requise |
|---|---|---|
| AC1 | Un propriétaire résout les libellés DB selon l'ordre langue explicite, langue utilisateur, langue système `fr`, puis code canonique. | `pytest -q app/tests/unit/test_astrology_translation_resolver.py` |
| AC2 | `json_builder.py` conserve les champs code historiques et ajoute les libellés définis dans le tableau Mapping requis par surface. | `pytest -q app/tests/unit/test_chart_json_builder.py` |
| AC3 | Les contextes LLM consomment le contrat localisé `AstrologyLabels`. | `pytest -q app/tests/unit/test_natal_context_localization.py` |
| AC4 | Le domaine astrology pur reste indépendant de la localisation. | `pytest -q tests/unit/domain/astrology/test_zodiac.py` + scan imports |
| AC5 | Aucun mapping backend de libellés de signes DB-backed n'est réintroduit dans les surfaces ciblées, hors exception PDF documentée. | `pytest -q app/tests/unit/test_astrology_localization_guardrails.py` |

## 8. Tâches d'implémentation

- [ ] Tâche 1 - Construire le propriétaire de résolution localisée (AC: AC1, AC4)
  - [ ] Créer `AstrologyTranslationResolver` ou un propriétaire équivalent sous `backend/app/services/reference_data/`.
  - [ ] Définir un DTO `AstrologyLabels` ou contrat équivalent avec `sign_label(sign_code)`.
  - [ ] Tester langue explicite, langue utilisateur, langue système `fr` et fallback code.

- [ ] Tâche 2 - Migrer le JSON chart vers les libellés injectés (AC: AC2)
  - [ ] Adapter `build_chart_json` et le catalogue d'évidence pour recevoir `language_code`, `AstrologyLabels` ou un resolver injecté.
  - [ ] Ajouter les champs de libellé du tableau Mapping requis par surface sans supprimer ni renommer les codes historiques.
  - [ ] Mettre à jour les tests de chart JSON.

- [ ] Tâche 3 - Migrer les contextes LLM natals (AC: AC3)
  - [ ] Supprimer l'export nominal `SIGN_NAMES_FR` de `natal_context.py`.
  - [ ] Adapter `astro_context_builder.py` pour résoudre le libellé lunaire depuis le propriétaire canonique.
  - [ ] Couvrir le résumé natal et l'indication de chat dans la langue effective.

- [ ] Tâche 4 - Ajouter les gardes anti-régression (AC: AC4, AC5)
  - [ ] Ajouter ou étendre un test d'architecture contre les mappings de signes dans `app/services`.
  - [ ] Vérifier que `domain/astrology` ne dépend pas du resolver ni des modèles de traduction.
  - [ ] Documenter toute exception test historique si un hit hors runtime existe.

- [ ] Tâche 5 - Valider et documenter l'évidence (AC: AC1, AC2, AC3, AC4, AC5)
  - [ ] Exécuter lint, tests ciblés et scans négatifs depuis le venv.
  - [ ] Capturer le résultat dans le compte rendu d'implémentation.

## 9. Réutilisation obligatoire / contraintes DRY

- Réutiliser:
  - `LanguageModel` et `UserModel.default_language` pour la préférence utilisateur.
  - `AstralSignTranslationModel` pour les libellés de signes.
  - `sign_from_longitude(longitude)` uniquement pour calculer les codes depuis les longitudes.
  - Le client/session DB existant du service appelant; ne pas ouvrir de nouvelle session globale.
- Ne pas recréer:
  - `SIGN_NAMES_FR`, `SIGNS` local ou autre mapping de noms de signes.
  - Un JSON applicatif autonome pour les libellés.
  - Une logique de fallback différente par consommateur.
  - Un mapping concurrent de `NatalPdfExportService.SIGN_LABELS` dans les surfaces ciblées.
- Abstraction partagée autorisée seulement si:
  - Elle centralise la résolution de libellés pour au moins les trois consommateurs ciblés ou expose clairement un contrat réutilisable par eux.

## 10. Pas de legacy / chemins interdits

Interdit sauf approbation explicite:

- wrappers de compatibilité
- alias transitoires
- imports legacy
- implémentations actives dupliquées
- fallback silencieux
- service au niveau racine quand un namespace canonique existe
- conservation de l'ancien chemin par re-export

Symboles / chemins spécifiquement interdits:

- `SIGN_NAMES_FR` dans `backend/app/services/**`.
- `SIGNS = [hardcoded_sign_codes]` dans `backend/app/services/llm_generation/shared/natal_context.py`.
- Nouveau `SIGN_LABELS` ou mapping équivalent de signes dans les surfaces ciblées par cette story.
- Import de `AstrologyTranslationResolver` ou de modèles SQLAlchemy de traduction depuis `backend/app/domain/astrology/**`.
- Nouveau fichier de constante de signes sous `backend/app/core`, `backend/app/domain` ou `backend/app/services`.
- Re-export de `SIGN_NAMES_FR` depuis `backend/app/services/llm_generation/natal/prompt_context.py`.

## 11. Règles de classification de suppression

La classification de suppression s'applique uniquement aux surfaces de localisation codées en dur.

- `canonical-active`: `sign_from_longitude(longitude)` et les codes de signes canoniques sont actifs et doivent être conservés.
- `external-active`: aucun usage externe de `SIGN_NAMES_FR` n'est identifié; si un import depuis un package externe est trouvé, l'implémentation doit s'arrêter pour décision utilisateur.
- `historical-facade`: le re-export de `SIGN_NAMES_FR` par `prompt_context.py`, s'il existe encore,
  est une façade sur la constante partagée codée en dur et doit être supprimé.
- `dead`: les mappings locaux `SIGN_NAMES_FR` et les listes `SIGNS` de niveau service utilisées uniquement pour les libellés
  sont morts après introduction du resolver et migration des consommateurs.
- `needs-user-decision`: toute suppression de champ d'API publique au-delà des constantes codées en dur.

Matrice de décision de classification:

| Classification | Décisions autorisées | Règle |
|---|---|---|
| `canonical-active` | `keep` | Ne doit pas être supprimé. |
| `external-active` | `keep`, `needs-user-decision` | Ne doit pas être supprimé sans décision utilisateur explicite. |
| `historical-facade` | `delete`, `needs-user-decision` | Doit être supprimé quand aucun blocage externe ne reste. Ne doit pas être redirigé. |
| `dead` | `delete` | Doit être supprimé. |
| `needs-user-decision` | `needs-user-decision` | Doit bloquer l'implémentation jusqu'à décision. |

## 12. Format d'audit de suppression

| Élément | Type | Classification | Consommateurs | Remplacement canonique | Décision | Preuve | Risque |
|---|---|---|---|---|---|---|---|
| `json_builder.py::SIGN_NAMES_FR` | constante | `dead` | libellés d'évidence chart | resolver / DTO `AstrologyLabels` | delete | tests chart JSON | libellés français résiduels |
| `natal_context.py::SIGN_NAMES_FR` | constante | `dead` | résumés et indications | resolver / DTO `AstrologyLabels` | delete | tests de localisation natal | prompts uniquement français résiduels |
| `natal_context.py::SIGNS` | constante | `dead` pour les libellés | helper local | `sign_from_longitude` | replace-consumer | tests natal + zodiac | ordre dupliqué |
| `prompt_context.py::SIGN_NAMES_FR` | re-export | `historical-facade` | imports de prompt | aucun re-export | delete | scan de la chaîne d'import | alias restant |
| `pdf_export_service.py::SIGN_LABELS` | constante | `out-of-scope` | libellés PDF | story future de localisation PDF | keep | exclusion dans le baseline | PDF toujours codé en dur |

Vocabulaire de classification autorisé: `out-of-scope` est autorisé uniquement pour une preuve exclue qui ne doit pas être modifiée par CS-174.
Vocabulaire de décision autorisé pour cet audit: `keep`, `replace-consumer`, `delete`, `needs-user-decision`.

Chemin de sortie de l'audit quand applicable:

- La section `## 12. Removal Audit Format` de la story constitue l'audit persistant pour ce périmètre borné de suppression de constantes.

## 13. Ownership canonique

| Responsabilité | Propriétaire canonique | Surfaces non canoniques |
|---|---|---|
| Codes zodiacaux et ordre géométrique | `backend/app/domain/astrology/zodiac.py` | resolver de traduction, services LLM |
| Libellés localisés de signes | `backend/app/services/reference_data/astrology_translation_resolver.py` | builders chart, natal et astro context |
| Préférence langue utilisateur | `backend/app/infra/db/models/user.py` + services user profile | paramètre global ou constante |
| Payload chart public | `backend/app/services/chart/json_builder.py` | domaine astrology pur |
| Résumé natal LLM | `backend/app/services/llm_generation/shared/natal_context.py` | constante importée par plusieurs modules |

## 14. Règle delete-only

Les éléments classés `dead` ou `historical-facade` doivent être supprimés, pas redirigés.

Interdit:

- rediriger vers un autre mapping français codé en dur
- conserver un wrapper
- ajouter un alias de compatibilité
- garder un import déprécié actif
- conserver l'ancien chemin par re-export
- remplacer la suppression par un comportement de désactivation souple

## 15. Blocage d'usage externe

Si `SIGN_NAMES_FR` a un usage `external-active`, il ne doit pas être supprimé sans décision utilisateur explicite.
Les imports internes doivent être migrés vers le resolver ou `AstrologyLabels`.

## 16. Notes de compatibilité

- Impact compatibilité: les codes existants restent disponibles; les libellés sont ajoutés ou consommés comme information affichable.
- Impact migration: aucune migration DB prévue.
- Compatibilité frontend: le front peut continuer à lire les codes existants; il peut adopter `sign_label` quand disponible.
- Compatibilité LLM: les prompts structurés gardent les codes; les textes humains utilisent la langue effective.
- Compatibilité PDF: l'export PDF conserve son mapping existant, car sa migration DB-backed est hors périmètre.

## 17. Vérification du contrat généré

- Vérification du contrat généré: applicable si une route FastAPI expose le chart JSON enrichi.
- Preuve de contrat généré requise:
  - Test ou snapshot OpenAPI ciblé si le schéma public est modifié.
  - Assertion JSON sur au moins un payload contenant `sign_code` et `sign_label`.

## 18. Fichiers à inspecter d'abord

Codex doit inspecter avant modification:

- `backend/app/services/chart/json_builder.py`
- `backend/app/services/natal/astro_context_builder.py`
- `backend/app/services/llm_generation/shared/natal_context.py`
- `backend/app/services/llm_generation/natal/prompt_context.py`
- `backend/app/infra/db/models/translation_reference.py`
- `backend/app/infra/db/models/user.py`
- `backend/app/domain/astrology/zodiac.py`
- `backend/app/tests/unit/test_chart_json_builder.py`

## 19. Fichiers attendus à modifier

Fichiers probables:

- `backend/app/services/reference_data/astrology_translation_resolver.py` - propriétaire de résolution localisée.
- `backend/app/services/chart/json_builder.py` - injection/consommation des libellés et suppression du mapping de signes.
- `backend/app/services/natal/astro_context_builder.py` - résolution de libellé lunaire sans constante.
- `backend/app/services/llm_generation/shared/natal_context.py` - contrat `AstrologyLabels` pour résumé/indication natale.
- `backend/app/services/llm_generation/natal/prompt_context.py` - suppression du re-export `SIGN_NAMES_FR`.
- `_condamad/stories/CS-174-localiser-libelles-astrologiques-backend/generated/01-baseline-sign-localization.md` - baseline avant/après des scans.

Tests probables:

- `backend/app/tests/unit/test_astrology_translation_resolver.py`
- `backend/app/tests/unit/test_chart_json_builder.py`
- `backend/app/tests/unit/test_natal_context_localization.py`
- `backend/app/tests/unit/test_astrology_localization_guardrails.py`

Fichiers non attendus à modifier:

- `backend/app/domain/astrology/zodiac.py` - le calcul reste en code canonique.
- `backend/app/domain/astrology/**` - aucune localisation affichable dans le domaine pur.
- `frontend/**` - la story ne demande pas de changement UI.
- `backend/app/services/natal/pdf_export_service.py` - mapping PDF hors périmètre de cette story.
- `backend/requirements.txt` - interdit; les dépendances restent dans `backend/pyproject.toml`.

## 20. Politique de dépendances

- Nouvelles dépendances: aucune.
- Changements de dépendances autorisés uniquement s'ils sont listés ici avec justification.

## 21. Plan de validation

Exécuter ou justifier l'omission:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q app/tests/unit/test_astrology_translation_resolver.py app/tests/unit/test_chart_json_builder.py
pytest -q app/tests/unit/test_natal_context_localization.py tests/unit/domain/astrology/test_zodiac.py
pytest -q app/tests/unit/test_astrology_localization_guardrails.py
rg -n "SIGN_NAMES_FR|\bSIGNS\s*=\s*\[" app/services/chart app/services/natal/astro_context_builder.py app/services/llm_generation/shared/natal_context.py app/services/llm_generation/natal/prompt_context.py app/domain/astrology
rg -n "AstrologyTranslationResolver|astrology_translation_resolver|translated_name|LanguageModel" app/domain/astrology
```

Si les schémas API générés changent, exécuter aussi:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
pytest -q app/tests/integration/test_natal_calculate_api.py
```

## 22. Risques de régression

- Risque: la localisation se retrouve dans le domaine astrologique pur.
  - Guardrail: scan négatif des imports resolver/modèles traduction dans `app/domain/astrology`.
- Risque: un service garde un mapping français local tout en ajoutant un resolver.
  - Guardrail: scan négatif `SIGN_NAMES_FR` sur les surfaces ciblées + test d'architecture documentant l'exception PDF hors périmètre.
- Risque: le fallback code masque une traduction manquante.
  - Guardrail: tests du resolver couvrant la langue explicite, la langue utilisateur, la langue système `fr` et le fallback final.
- Risque: le front ou les prompts perdent les codes stables.
  - Guardrail: assertions code + libellé par surface et conservation des champs historiques.

## 23. Instructions pour l'agent de développement

- Implémenter uniquement cette story.
- Ne pas élargir le domaine.
- Ne pas introduire de nouvelles dépendances sauf si elles sont explicitement listées.
- Ne pas marquer une tâche comme complète sans preuve de validation.
- Si un AC ne peut pas être satisfait, arrêter et consigner le blocage.
- Ne pas préserver un comportement legacy par facilité.
- Ne pas contourner la suppression par redirection, soft-disable, wrapper, alias, fallback ou re-export.
- Ne pas accepter `PASS with limitation`, allowlist large, exception wildcard,
  fallback non classifié, compatibilité, legacy, migration-only, shim, alias,
  TODO ou travail résiduel caché dans le domaine quand cette story est marquée
  `full-closure`.

## 24. References

- User brief 2026-05-16 - source de vérité et ordre de résolution demandé.
- `backend/app/infra/db/models/translation_reference.py` - modèles de traductions astrologiques.
- `backend/app/infra/db/models/user.py` - préférence de langue utilisateur.
- `backend/app/domain/astrology/zodiac.py` - propriétaire des codes zodiacaux.
- `_condamad/stories/regression-guardrails.md` - invariants consultés et enrichis.
