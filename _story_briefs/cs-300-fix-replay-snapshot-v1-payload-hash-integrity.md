# CS-300 — Fix replay_snapshot_v1 Payload Hash Integrity

## Résumé

Corriger l'incohérence entre le payload réellement stocké dans `replay_snapshot_v1`, le hash d'intégrité et le chemin d'exécution `replay`, sans élargir le périmètre DPO/sécurité approuvé.

## Contexte

La revue de CS-295 à CS-299 a identifié un défaut bloquant : le service de création chiffre `snapshot_metadata["sanitized_input"]`, mais le service de replay déchiffre ce payload puis recalcule `compute_input_hash(user_input)` comme si le payload était l'entrée originale.

Le chemin réel `log_call -> create_snapshot -> replay` produit donc un hash différent et échoue en `input_hash_mismatch`. Les tests actuels ne couvrent pas ce chemin réel parce qu'ils créent un snapshot en chiffrant directement l'input brut avec `encrypt_input(user_input)`.

## Objectif

Rendre le replay snapshot v1 cohérent de bout en bout :

- le payload chiffré doit être le payload approuvé pour le replay ;
- le hash stocké doit être calculé sur ce même payload canonique ;
- l'intégrité replay doit comparer deux représentations issues du même contrat ;
- aucune donnée interdite par la décision DPO/sécurité ne doit être persistée.

## Préalable obligatoire

Relire avant modification :

- `docs/architecture/replay-snapshot-v1-storage-security-model.md`
- `docs/architecture/replay-snapshot-v1-dpo-security-approval-request.md`
- `backend/app/core/sensitive_data.py`
- `backend/app/domain/llm/runtime/observability_service.py`
- `backend/app/services/replay_snapshot_v1_service.py`
- `backend/app/ops/llm/replay_service.py`
- `backend/tests/unit/test_replay_snapshot_v1_execution_audit.py`
- `backend/tests/integration/test_replay_snapshot_v1_db_redaction.py`

## Périmètre inclus

1. Définir une représentation canonique unique du payload replay autorisé.
2. Calculer le hash d'intégrité sur cette représentation canonique, pas sur une représentation différente.
3. Corriger `create_snapshot` et `replay` pour utiliser le même contrat de payload/hash.
4. Corriger les tests qui chiffrent actuellement un payload brut non représentatif du chemin applicatif.
5. Ajouter un test bout-en-bout `log_call -> snapshot persisté -> replay` qui échoue avant correction et passe après correction.
6. Conserver les audits de succès/échec de replay sans payload brut.
7. Vérifier que les champs interdits restent absents des métadonnées inspectables, des réponses API et des audit logs.

## Hors périmètre

- Stocker des prompts bruts.
- Stocker des données de naissance brutes.
- Stocker des coordonnées exactes.
- Stocker des identifiants directs ou secrets.
- Ajouter une UI frontend.
- Ajouter une route publique ou client.
- Modifier la décision DPO/sécurité existante.
- Ajouter un second store replay.

## Critères d'acceptation

1. Un snapshot créé par `log_call` peut être rejoué par le chemin réel sans `input_hash_mismatch`.
2. Le test de replay réel n'utilise plus `encrypt_input(user_input)` sur un payload brut fabriqué uniquement pour le test.
3. Le hash stocké dans `llm_replay_snapshots.input_hash` correspond au payload replay effectivement chiffré.
4. Le replay refuse explicitement les snapshots incomplets, expirés, purgés ou dont le hash canonique ne correspond pas.
5. Aucune donnée interdite par le modèle DPO/sécurité n'est ajoutée en DB, logs, audit details, API admin ou OpenAPI.
6. Le service reste propriétaire unique du cycle de vie `replay_snapshot_v1`.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests\unit\test_replay_snapshot_v1_execution_audit.py tests\integration\test_replay_snapshot_v1_db_redaction.py tests\unit\test_replay_snapshot_v1_redaction.py --tb=short
python -B -m pytest -q tests\unit\test_replay_snapshot_v1_*.py tests\integration\test_replay_snapshot_v1_*.py tests\api\admin\test_replay_snapshot_v1_api.py tests\architecture\test_replay_snapshot_v1_execution_boundary.py tests\architecture\test_admin_replay_snapshot_v1_public_exposure.py --tb=short
```

Si PowerShell ne développe pas les wildcards pour `pytest`, lister explicitement les fichiers `test_replay_snapshot_v1_*.py`.

## Dépendances

- CS-295 stockage et redaction.
- CS-296 service retention/purge.
- CS-298 execution/audit.
- CS-299 closure evidence à réviser après correction.
- Décision DPO/sécurité `DPO-REPLAY-SNAPSHOT-V1-RETENTION-001`.

## Risques

Le risque principal est de corriger le hash en réintroduisant des données interdites. La correction doit privilégier un contrat canonique sûr et testé. Si un replay plus fidèle nécessite des données actuellement interdites, il doit rester refusé explicitement et faire l'objet d'une nouvelle décision DPO/sécurité, pas être implémenté implicitement.
