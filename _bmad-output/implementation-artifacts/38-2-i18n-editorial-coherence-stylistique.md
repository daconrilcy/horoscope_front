# Story 38.2 : Internationalisation et cohérence stylistique éditoriale

Status: ready-for-dev

## Story

As a développeur de l'application horoscope,
I want des templates éditoriaux disponibles en FR et EN avec une charte rédactionnelle stable,
so that la même structure de template est réutilisée dans les deux langues sans dupliquer de logique, et que les labels UI s'affichent correctement quelle que soit la langue de l'utilisateur.

## Acceptance Criteria

### AC1 — Structure identique entre FR et EN

Les templates EN dans `backend/app/prediction/editorial_templates/en/` sont des miroirs structurels exacts des templates FR : mêmes noms de fichiers, mêmes placeholders, mêmes sections.

### AC2 — Seules les chaînes changent entre les langues

Aucune logique conditionnelle ou calculatoire n'est dupliquée entre les dossiers `fr/` et `en/`. Un diff structurel entre les deux dossiers ne révèle que des différences de libellés.

### AC3 — Aucune logique calculatoire dans la couche i18n

Le fichier `frontend/src/i18n/predictions.ts` ne contient que des dictionnaires de traduction (Record). Toute logique de sélection de label reste dans le composant appelant.

### AC4 — Charte rédactionnelle documentée

Le fichier `docs/editorial/charte-redactionnelle.md` documente le ton, le registre, la longueur cible des textes, et les niveaux de certitude attendus pour chaque type de template.

### AC5 — Labels catégories et bandes disponibles en FR et EN dans le frontend

`frontend/src/i18n/predictions.ts` exporte `CATEGORY_LABELS`, `NOTE_BAND_LABELS`, `TONE_LABELS` et `PIVOT_LABELS` utilisables directement par les composants React avec un paramètre `lang: 'fr' | 'en'`.

## Tasks / Subtasks

### T1 — Créer les templates EN miroirs du FR (AC1, AC2) — ARCHITECTURE UNIFIÉE

**CRITIQUE** : les templates EN doivent suivre **exactement la même architecture que les templates FR** définie en story 38-1. Les templates FR sont des fichiers `.txt` nommés par **fonction** (pas par catégorie) : `intro_du_jour.txt`, `resume_categorie.txt`, `phrase_pivot.txt`, `meilleure_fenetre.txt`, `prudence_sante.txt`, `prudence_argent.txt`. Ne pas créer de fichiers `.md` nommés par catégorie (`amour.md`, `travail.md`...) — ce serait une architecture différente incompatible.

- [ ] Créer le dossier `backend/app/prediction/editorial_templates/en/`
- [ ] Créer les 6 templates EN en miroir des templates FR (mêmes noms, même extension `.txt`) :
  - [ ] `intro_du_jour.txt` — même placeholders que FR : `{date_local}`, `{overall_tone_label}`, `{top3_labels}`
  - [ ] `resume_categorie.txt` — mêmes placeholders : `{category_label}`, `{note_20}`, `{band}`
  - [ ] `phrase_pivot.txt` — mêmes placeholders : `{pivot_time}`, `{pivot_severity_label}`
  - [ ] `meilleure_fenetre.txt` — mêmes placeholders : `{window_start}`, `{window_end}`, `{dominant_category_label}`
  - [ ] `prudence_sante.txt` — "Pay particular attention to your health today." (prudent, sans diagnostic)
  - [ ] `prudence_argent.txt` — "Exercise caution in financial matters; consider postponing major commitments." (prudent)
- [ ] Vérifier que chaque template EN contient exactement les mêmes placeholders que son équivalent FR

### T2 — Créer la charte rédactionnelle (AC4)

- [ ] Créer `docs/editorial/charte-redactionnelle.md` avec les sections :
  - Ton général (bienveillant, non alarmiste, ancré dans le quotidien)
  - Registre (vouvoiement en FR, "you" direct en EN)
  - Longueur cible par section (titre : 1 ligne, corps : 2-4 phrases, pivot : 1 phrase action)
  - Niveaux de certitude (éviter absolus type "vous allez", préférer "il est probable que")
  - Règles de prudence (catégories `sante` et `argent` : ton plus mesuré)
  - Exemples de formulations acceptées et refusées

### T3 — Créer `frontend/src/i18n/predictions.ts` (AC3, AC5)

- [ ] Créer `frontend/src/i18n/predictions.ts` avec les exports suivants :
  - [ ] `type Lang = 'fr' | 'en'`
  - [ ] `CATEGORY_LABELS: Record<string, Record<Lang, string>>` — couvrir **tous les codes de catégories renvoyés par l'API** (ne pas coder en dur une liste fixe de 6 — le référentiel est dynamique). Utiliser les codes connus du référentiel actif comme base, mais prévoir un fallback générique pour les codes inconnus (`(code) => code`)
  - [ ] `NOTE_BAND_LABELS: Record<string, Record<Lang, string>>` pour `fragile`, `tendu`, `neutre`, `porteur`, `très favorable`
  - [ ] `TONE_LABELS: Record<string, Record<Lang, string>>` pour `steady`, `push`, `careful`, `open`, `mixed`
  - [ ] `PIVOT_LABELS: Record<string, Record<Lang, string>>` pour les codes de pivots définis dans `EditorialTemplateEngine`
- [ ] Vérifier que le fichier ne contient aucune logique conditionnelle (pure data)

### T4 — Tests unitaires backend i18n (AC1, AC2, AC5)

- [ ] Créer `backend/app/tests/unit/test_editorial_i18n.py` :
  - [ ] `test_fr_en_same_placeholders` — pour chaque paire de templates (fr/X.txt, en/X.txt), extraire les `{placeholder}` et vérifier que les ensembles sont identiques
  - [ ] `test_no_calculatory_logic_in_templates` — vérification textuelle : aucun template ne contient `if`, `else`, `for`, `=`, `def`, ni de code Python
  - [ ] `test_engine_selects_correct_lang` — instancier `EditorialTemplateEngine` avec `lang='en'`, vérifier que le texte produit (`EditorialTextOutput`) est en anglais (contient des mots EN, pas FR)

## Dev Notes

### Pattern fichier i18n frontend

Reproduire le style de `frontend/src/i18n/astrology.ts` :

```typescript
// frontend/src/i18n/predictions.ts
type Lang = 'fr' | 'en'

export const CATEGORY_LABELS: Record<string, Record<Lang, string>> = {
  amour: { fr: 'Amour', en: 'Love' },
  travail: { fr: 'Travail', en: 'Work' },
  sante: { fr: 'Santé', en: 'Health' },
  argent: { fr: 'Argent', en: 'Money' },
  vitalite: { fr: 'Vitalité', en: 'Vitality' },
  social: { fr: 'Social', en: 'Social' },
}

export const NOTE_BAND_LABELS: Record<string, Record<Lang, string>> = {
  fragile: { fr: 'Fragile', en: 'Fragile' },
  tendu: { fr: 'Tendu', en: 'Tense' },
  neutre: { fr: 'Neutre', en: 'Neutral' },
  porteur: { fr: 'Porteur', en: 'Favorable' },
  'très favorable': { fr: 'Très favorable', en: 'Very favorable' },
}

export const TONE_LABELS: Record<string, Record<Lang, string>> = {
  steady: { fr: 'Stable', en: 'Steady' },
  push: { fr: 'Dynamique', en: 'Push' },
  careful: { fr: 'Prudent', en: 'Careful' },
  open: { fr: 'Ouvert', en: 'Open' },
  mixed: { fr: 'Mixte', en: 'Mixed' },
}
```

### Sélection de langue dans EditorialTemplateEngine

`EditorialTemplateEngine` supporte déjà un paramètre `lang` qui sélectionne le dossier (`fr/` ou `en/`). La story ne modifie pas cette logique — elle crée uniquement le contenu manquant des templates EN.

### Structure de dossier attendue

Architecture unifiée avec 38-1 : fichiers `.txt` nommés par **fonction** (pas par catégorie).

```
backend/app/prediction/editorial_templates/
├── fr/
│   ├── intro_du_jour.txt
│   ├── resume_categorie.txt
│   ├── phrase_pivot.txt
│   ├── meilleure_fenetre.txt
│   ├── prudence_sante.txt
│   └── prudence_argent.txt
└── en/
    ├── intro_du_jour.txt      ← à créer (même placeholders que FR)
    ├── resume_categorie.txt   ← à créer
    ├── phrase_pivot.txt       ← à créer
    ├── meilleure_fenetre.txt  ← à créer
    ├── prudence_sante.txt     ← à créer ("Pay particular attention to your health today.")
    └── prudence_argent.txt    ← à créer ("Exercise caution in financial matters; consider postponing major commitments.")
```

### Test placeholder extraction (exemple)

```python
import re
from pathlib import Path

def extract_placeholders(text: str) -> set[str]:
    return set(re.findall(r'\{(\w+)\}', text))

def test_fr_en_same_placeholders():
    base = Path("backend/app/prediction/editorial_templates")
    for fr_file in (base / "fr").glob("*.txt"):
        en_file = base / "en" / fr_file.name
        assert en_file.exists(), f"Missing EN template: {fr_file.name}"
        fr_ph = extract_placeholders(fr_file.read_text())
        en_ph = extract_placeholders(en_file.read_text())
        assert fr_ph == en_ph, f"{fr_file.name}: FR placeholders {fr_ph} != EN {en_ph}"
```

### Project Structure Notes

- Dossier templates FR existant : `backend/app/prediction/editorial_templates/fr/`
- Fichier i18n astrology de référence : `frontend/src/i18n/astrology.ts`
- `EditorialTemplateEngine` : `backend/app/prediction/editorial_template_engine.py`
- `EditorialTextOutput` : défini dans `backend/app/prediction/schemas.py`

## References

- [Source: backend/app/prediction/editorial_template_engine.py — EditorialTemplateEngine, paramètre lang]
- [Source: backend/app/prediction/schemas.py — EditorialTextOutput]
- [Source: backend/app/prediction/editorial_templates/fr/ — templates FR de référence]
- [Source: frontend/src/i18n/astrology.ts — pattern i18n frontend]
- [Story: 38-1 — EditorialTemplateEngine produit EditorialTextOutput avec textes par langue]

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List

## Change Log

- 2026-03-08: Story créée pour Epic 38.
