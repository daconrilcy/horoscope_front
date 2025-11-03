# Guide de publication GitHub - FE-5 Horoscope

## Étapes pour publier l'issue et la PR

### 1. Préparer la branche

```bash
# Vérifier la branche courante
git branch --show-current

# Si pas sur feat/FE-5-horoscope, la créer
git checkout -b feat/FE-5-horoscope

# Ajouter tous les fichiers
git add -A

# Vérifier les fichiers à commiter
git status

# Commit avec message descriptif
git commit -m "feat: implement FE-5 horoscope feature

- Add HoroscopeService with strict Zod schemas
- Add horoscopeStore with LRU and FIFO cap 10
- Add React Query hooks (useCreateNatal, useToday, useTodayPremium, useDownloadPdf)
- Add UI components (NatalForm, TodayCard, TodayPremiumCard)
- Add horoscope page with lazy loading
- Add tests: 13 service tests, 10 store tests
- Total: 207/207 tests passing

Closes #[issue_number]"

# Push vers origin
git push -u origin feat/FE-5-horoscope
```

### 2. Créer l'issue GitHub

Aller sur : https://github.com/daconrilcy/horoscope_front/issues/new

**Titre** : `FE-5 — Horoscope Feature`

**Description** : Copier le contenu de `FE-5-horoscope-issue.md`

**Labels** :

- `feature`
- `horoscope`
- `milestone-fe-5`

**Assigné** : [assigner à soi-même si nécessaire]

**Créer l'issue** et noter le numéro (ex: #15)

### 3. Créer la Pull Request

Aller sur : https://github.com/daconrilcy/horoscope_front/compare/feat/FE-5-horoscope

**Base** : `main` (ou `feat/FE-0-bootstrap-qualite` selon la branche de base)

**Compare** : `feat/FE-5-horoscope`

**Titre** : `FE-5 — Horoscope Feature`

**Description** : Copier le contenu de `FE-5-horoscope-pr.md`

Ajouter à la fin :

```
Closes #[issue_number]
```

**Reviewers** : [assigner si nécessaire]

**Labels** :

- `feature`
- `horoscope`
- `milestone-fe-5`

**Create pull request**

### 4. Vérifications post-creation

- [ ] Les checks CI/CD passent
- [ ] Les reviewers sont assignés
- [ ] Les labels sont corrects
- [ ] L'issue est liée à la PR
- [ ] La description PR est complète

## Commandes utiles

```bash
# Vérifier le statut
git status

# Voir les différences
git diff

# Voir les fichiers modifiés
git diff --name-only

# Voir l'historique des commits
git log --oneline -5

# Rollback si nécessaire
git reset --soft HEAD~1
```

## Rollback en cas de problème

```bash
# Si le commit n'a pas été pushé
git reset --soft HEAD~1

# Si le commit a été pushé
git reset --hard origin/[branch-name]
```

## Checklist finale

- [x] Tous les fichiers sont créés/modifiés
- [x] Tests 207/207 passants
- [x] Lint OK (0 erreurs)
- [x] Typecheck OK
- [x] Build OK
- [ ] Branche créée
- [ ] Commit créé
- [ ] Push vers origin
- [ ] Issue GitHub créée
- [ ] PR GitHub créée
- [ ] PR liée à l'issue
- [ ] CI/CD checks passent

## Résumé

**Fichiers** : 18 créés + 1 modifié = 19 fichiers
**Tests** : 23 nouveaux tests (13 service + 10 store)
**Total tests projet** : 207/207 ✅
**Qualité** : lint OK, typecheck OK, build OK
