# CS-381 - Non Regression Generation Theme Natal Et Enrichissement Prompts

<!-- Commentaire global: ce brief cadre la preuve bout en bout que la generation natale et les prompts enrichis coexistent. -->

## Resume

Ajouter une validation bout en bout, automatisee autant que possible, qui prouve que l'application peut de nouveau generer un theme natal complet sans regression de l'enrichissement recemment ajoute dans la construction des prompts `theme_astral`.

## Contexte

Les stories CS-363 a CS-378 ont restructure le contrat `theme_astral_llm_input_v1` et le payload provider. La generation de theme natal dans l'application semble maintenant casser le rendu client apres une reponse API `200 OK`. Une fois CS-379 et CS-380 traitees, il faut une preuve de non-regression qui couvre le flux utilisateur reel et pas seulement les builders isoles.

Decision produit confirmee: `traditional_conditions` doit etre absent uniquement quand les donnees de naissance ne permettent pas un calcul fiable, par exemple `no_time`. Le crash observe intervient des la creation d'un nouveau theme; le scenario de non-regression doit donc verifier en priorite la reponse `POST /v1/users/me/natal-chart`.

## Objectif

Verifier dans un meme parcours que:

- l'utilisateur connecte peut enregistrer ses donnees de naissance;
- `POST /v1/users/me/natal-chart` repond avec un theme exploitable et un contrat traditionnel complet quand l'heure de naissance est connue;
- `GET /v1/users/me/natal-chart/latest` recharge le meme contrat public;
- le panneau expert et la projection client ne crashent pas;
- le payload prompt/provider conserve les blocs enrichis attendus;
- aucun ancien carrier legacy ne redevient source de verite.

## Perimetre inclus

1. Identifier les tests E2E ou integration existants couvrant naissance, geocoding et generation natale.
2. Ajouter ou completer un scenario cible avec l'utilisateur test ou un utilisateur fixture isole.
3. Verifier les assertions reseau sur `POST /v1/users/me/natal-chart` en priorite, puis sur `GET /latest` pour confirmer que le theme relu reste coherent.
4. Verifier une assertion UI: absence d'error boundary et presence d'un contenu expert ou d'un etat degrade controle.
5. Ajouter une assertion backend ou fixture sur le payload `theme_astral_llm_input_v1` enrichi.
6. Documenter les preconditions locales: backend, frontend, base de test, geocoding/mock si necessaire.
7. Garder le test provider LLM reel optionnel et separe.

## Hors perimetre

- Appeler un provider LLM reel en CI standard.
- Modifier les plans commerciaux ou les droits d'acces.
- Changer le contenu redactionnel des prompts.
- Couvrir tous les navigateurs et toutes les villes.
- Ajouter des secrets ou commiter un fichier `.env`.

## Sources obligatoires

- `frontend/e2e/**`
- `frontend/src/pages/BirthProfilePage.tsx`
- `frontend/src/features/birth-profile/components/BirthProfileNatalGenerationSection.tsx`
- `frontend/src/features/natal-chart/NatalExpertPanel.tsx`
- `frontend/src/api/natal-chart/index.ts`
- `backend/app/api/v1/routers/**/natal*`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`
- `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py`
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/**`

## Criteres d'acceptation

1. Le scenario local genere un theme natal apres login sans erreur console React liee a `NatalExpertPanel`.
2. Le test verifie que `traditional_conditions` est complet apres creation quand l'heure de naissance est connue, ou absent uniquement en etat degrade controle `no_time`.
3. Le test backend ou une assertion de fixture verifie la presence de `birth_context` structure et des blocs enrichis prompt-visible attendus.
4. Les assertions interdisent le retour d'un prompt construit depuis `chart_json` ou `natal_data` legacy comme source principale.
5. Les tests distinguent clairement le payload public UI du payload provider LLM.
6. La validation ne depend pas d'un appel provider externe.
7. Les commandes de lancement local sont documentees dans le rapport de story ou le README concerne si elles changent.

## Commandes de validation minimales

Backend:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests --tb=short -k "natal_chart or theme_astral or llm_astrology_input"
```

Frontend:

```powershell
cd frontend
pnpm lint
pnpm test -- NatalExpertPanel BirthProfilePage natalChartApi
pnpm build
```

E2E si l'environnement local est disponible:

```powershell
cd frontend
pnpm test:e2e -- --grep "natal"
```

Si le nom de script E2E differe, utiliser le script existant du `package.json` et documenter la commande exacte.

## Donnees de test

L'utilisateur test autorise pour la validation manuelle est:

```text
daconrilcy@hotmail.com
admin123
```

Les donnees de naissance recommandees pour aligner les exemples existants:

```text
1973-04-24 11:00
Paris, France
Europe/Paris
```

## Risques

Le risque principal est de prouver separement "le front ne crash pas" et "le prompt est enrichi" sans verifier leur coexistence dans le flux reel. Cette story doit rester une validation transversale courte, executee apres CS-379 et CS-380.
