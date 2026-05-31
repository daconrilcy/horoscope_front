# QA live `/natal` — CS-390 à CS-395 — écarts restants

> **Mise à jour 2026-05-30 (CS-400)** : les écarts P0 padding/quota et P1 accordéons sont traités par CS-396→399. Voir le rapport de clôture `_condamad/reports/cs-400-cloture-qa-live-lecture-natale.md`. Le constat « narrative absente » ci-dessous reste valable pour les **payloads historiques V1** tant qu'une régénération V3 n'a pas été exécutée.

Date : 2026-05-30  
Compte : `daconrilcy@hotmail.com` / `admin123`  
Environnement : stack locale (`frontend` :5173, `backend` :8001)  
Méthode : navigation MCP + appels API + préparation manuelle du profil natal (compte local fraîchement créé).

## Captures

| Fichier | Contexte |
|---|---|
| `output/playwright/cs-395-qa-natal-loaded.png` | Basic — vue par défaut (interprétation short) |
| `output/playwright/cs-395-qa-natal-scrolled.png` | Basic — zone interprétation + mode astrologue |
| `output/playwright/cs-395-qa-natal-desktop-complete.png` | Basic — interprétation complete sans narrative (`?interpretationId=2`) |
| `output/playwright/cs-395-login-result.png` | Échec login formulaire (session antérieure, backend indisponible) |

## Synthèse exécutive

L’ossature frontend des stories CS-393/394 est en place (hero, synthèse, composants `NatalNarrativeReading` / `NatalReadingSources`, mode astrologue repliable, suppression des cartes legacy). En revanche, **la lecture narrative en cinq chapitres n’apparaît jamais en live** car le backend ne persiste pas `narrative_natal_reading_v1` sur les générations réelles (sortie LLM désérialisée en schéma v1, pas V3). La QA CS-395 reste donc **incomplète côté parcours produit authentifié**.

## État observé par profil

| Profil | Observé en live | Attendu (CS-390→395) | Écart |
|---|---|---|---|
| **Free** (état initial du compte) | Page vide « No natal chart » ; après génération : erreur « Interpretation is not available » puis retry | Résumé court + upsell Basic ; pas de fuite technique | Parcours free fragile ; compte local non seedé |
| **Basic** (plan forcé en DB pour test) | Hero Soleil/Lune/Asc ; interprétation **short** par défaut (résumé legacy) ; complete affiche message « Full reading needs regeneration » | 5 chapitres narratifs + bloc « Ce que nous avons utilisé » | **Narrative absente** ; contenu central = résumé V1, pas chapitres |
| **Premium** | Non testé (quota basic épuisé, pas de seed premium) | 5 chapitres + sources + mode astrologue ouvert avec détails experts | QA premium / astrologue ouvert **à faire** |

## Ce qui fonctionne (preuves live)

- Authentification API OK (`POST /v1/auth/login`).
- Génération thème natal OK après création profil naissance (`PUT /v1/users/me/birth-data` + `POST /v1/users/me/natal-chart`).
- Hero public (`NatalProfileHero`) : Soleil / Lune / Ascendant lisibles, sans codes moteur visibles.
- Anciennes cartes factuelles (ADN, domaines, forces, défis, etc.) **absentes** de la composition principale.
- Mode astrologue repliable : panneau technique **non monté** quand fermé (`#natal-astrologer-mode-panel` absent du DOM).
- Message de compatibilité CS-395 visible sur interprétation complete sans narrative : « Full reading needs regeneration ».
- Aucun identifiant `condition_axis`, `audit_input`, `SUN_TAURUS_*` détecté dans le texte DOM public.

## Modifications restantes

### P0 — Bloquant produit (backend CS-392)

1. **Brancher réellement `narrative_natal_reading_v1` sur le runtime de génération**
   - Constat API : toutes les interprétations générées (`short`, `complete`, `natal_long_free`) retournent `narrative_natal_reading_v1: null` et `meta.schema_version: "v1"`.
   - Cause probable : la sortie LLM ne se désérialise pas en `AstroResponseV3` ; `_attach_narrative_reading_to_complete_v3` n’est jamais exécuté (condition `isinstance(interpretation, AstroResponseV3)`).
   - Action : aligner prompt + validation + parsing pour garantir une sortie V3 acceptée, ou étendre le builder narrative pour couvrir le schéma effectivement produit.
   - Preuve cible : `POST /v1/natal/interpretation` (complete, basic) → payload avec 5 chapitres + `used_astrological_elements`.

2. **Supprimer les codes planétaires bruts du JSON public d’interprétation**
   - Constat API short : `"evidence": ["VENUS", "SUN", "SATURN", "JUPITER", "MOON"]`.
   - Action : retirer ou mapper `evidence` avant exposition publique (RG-152 / denylist narrative).
   - Fichiers : `interpretation_service.py`, contrat `NatalInterpretationResponse`, validateur narrative.

3. **Vérifier la génération en mode `accurate` avec lieu résolu**
   - Constat : `POST /v1/users/me/natal-chart {"accurate":true}` → `missing_birth_place_resolved`.
   - Impact QA : impossible de reproduire le profil documenté CS-385 (Paris résolu, Placidus) sans seed geo ou `place_resolved_id`.
   - Action : documenter/seed le compte test ou assouplir le parcours dev.

### P1 — Parcours frontend (CS-393 / CS-394)

4. **Centrer la page sur la lecture narrative, pas sur le résumé legacy**
   - Constat live basic : la vue par défaut charge l’interprétation **short** (historique id=1) avec titre + paragraphe résumé, sans chapitres.
   - Attendu CS-393 : les cinq chapitres deviennent le contenu central ; le résumé ne doit pas rester la lecture principale.
   - Action : lorsque `narrative_natal_reading_v1` est présent, masquer ou subordonner la carte `ni-content-card--summary` ; prioriser l’affichage complete narrative pour basic.

5. **Afficher `NatalReadingSources` dès que la narrative est disponible**
   - Composant implémenté mais jamais alimenté en live (dépend de P0).
   - Action : valider rendu replié par défaut + i18n FR/EN/ES/DE une fois le backend alimenté.

6. **Corriger le parcours free au premier chargement**
   - Constat : avec plan free et thème existant, la page affiche « Interpretation is not available at the moment » avant retry.
   - Piste : `NatalInterpretation.tsx` force `useCaseLevel = "complete"` quand `isLockedFree` (L271-275) alors que l’historique est vide → course condition / mauvais niveau initial.
   - Action : free doit charger explicitement le flux `short` / `natal_long_free` sans erreur générique.

7. **Cohérence i18n de la lecture**
   - Constat live : contenu interprétation en français, UI et disclaimer en anglais (« Legal Notice », « Full reading needs regeneration ») malgré le drapeau FR.
   - Action : synchroniser `lang` navigateur / localStorage avec les clés `natalChartTranslations[lang]`.

### P2 — QA et gouvernance (CS-395)

8. **Compléter la matrice QA navigateur demandée par CS-395**
   - [ ] Free — desktop + mobile (résumé court, upsell, pas de mode astrologue expert)
   - [ ] Basic — desktop + mobile (5 chapitres + sources)
   - [ ] Premium — mode astrologue ouvert (données experts visibles)
   - [ ] États dégradés `no_time` / `no_location` en navigateur
   - [ ] Interprétation rejetée (RG-150) — message contrôlé

9. **Seed / documentation du compte test local**
   - Constat : compte `daconrilcy@hotmail.com` recréé aujourd’hui (id=3), plan free, sans profil naissance ni thème.
   - AGENTS.md promet un utilisateur test utilisable ; l’environnement local ne reflète pas CS-385 (basic, Paris 1973, thème persisté).
   - Action : script de seed dev ou migration de compatibilité documentée dans README / AGENTS.md.

10. **Mettre à jour le rapport CS-395 avec les captures authentifiées**
    - Remplacer la mention « compte de test invalide » par les nouvelles preuves ou documenter les prérequis de seed.
    - Fichier : `_condamad/reports/cs-395-non-regression-lecture-natale-publique.md`.

11. **Accessibilité UI mineure observée en live**
    - Lien « Complete my profile » sur l’état vide : contraste insuffisant sur fond sombre.
    - Barre de navigation mobile intercepte les clics sur certains contrôles (sélecteur d’historique, toggle astrologue) — ajuster scroll/padding ou z-index.

### P3 — Dette / alignement architecture (CS-390 / CS-391)

12. **Clarifier la stratégie de migration des interprétations pré-narrative**
    - Comportement actuel : message « Lecture complète à régénérer » + conservation du résumé legacy au-dessus.
    - Décision produit à trancher : faut-il masquer le résumé legacy quand la narrative manque, ou proposer un CTA de régénération plus visible (quota basic = 1)?

13. **Tests d’intégration bout-en-bout manquants**
    - Les tests unitaires/architecture passent, mais aucun test ne prouve qu’une génération LLM réelle (ou fixture V3 nominal) produit `narrative_natal_reading_v1` exposée au front.
    - Action : test d’intégration POST `/v1/natal/interpretation` avec fixture gateway V3 → assert chapitres + denylist.

## Commandes de reproduction QA

```powershell
# Stack
.\scripts\start-dev-stack.ps1 -WithStripe

# Login
$body = '{"email":"daconrilcy@hotmail.com","password":"admin123"}'
$token = (Invoke-RestMethod -Uri "http://127.0.0.1:8001/v1/auth/login" -Method POST -Body $body -ContentType "application/json").data.tokens.access_token

# Vérifier narrative absente
$h = @{ Authorization = "Bearer $token" }
Invoke-RestMethod -Uri "http://127.0.0.1:8001/v1/natal/interpretation" -Method POST -Headers $h -Body '{"use_case_level":"complete","locale":"fr-FR","force_refresh":true}' -ContentType "application/json" | Select-Object -ExpandProperty data | Select-Object narrative_natal_reading_v1, @{n='schema';e={$_.meta.schema_version}}
```

## Priorisation recommandée

1. **P0 item 1** — sans narrative backend, CS-392/393/394/395 ne sont pas démontrables en prod.
2. **P0 item 2** — fuite `evidence` codes dans l’API publique.
3. **P1 items 4–7** — alignement UX une fois la narrative disponible.
4. **P2** — fermeture QA CS-395 et seed compte test.

## Références

- Stories : `_story_briefs/cs-390-*.md` … `_story_briefs/cs-395-*.md`
- Rapport non-régression : `_condamad/reports/cs-395-non-regression-lecture-natale-publique.md`
- Guardrails : RG-152, RG-153, RG-154
