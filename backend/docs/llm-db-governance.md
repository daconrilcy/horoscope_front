# Gouvernance DB LLM post-cleanup

## Source de verite canonique

Les decisions runtime nominales doivent venir des familles d objets suivantes :

- `llm_assembly_configs`
- `llm_execution_profiles`
- `llm_release_snapshots`
- `llm_active_releases`
- `llm_call_logs`
- `llm_canonical_consumption_aggregates`
- `llm_sample_payloads`
- `llm_personas`
- `llm_output_schemas`

`llm_prompt_versions` reste canonique pour le contenu des templates publies et leur historique, mais les champs de parametrage runtime qu il transporte encore ne doivent plus redevenir une source de verite implicite.

## Compatibilites legacy

Le perimetre canonique ne doit plus reintroduire de lecture ou d ecriture legacy
sur les objets LLM assainis. Les suppressions physiques sont portees par les
migrations Alembic et les traces historiques restent documentees dans
[llm-db-cleanup-registry.json](./llm-db-cleanup-registry.json).

## Regles de changement

Tout futur changement DB LLM doit respecter cet ordre :

1. converger la lecture et l ecriture metier vers les objets canoniques ;
2. geler les compatibilites legacy restantes ;
3. archiver les donnees utiles si un drop est vise ;
4. seulement ensuite introduire une migration physique de suppression.

Un `DROP` ne doit jamais preceder la convergence logique ni l archivage utile.

## Discipline de registre

Avant toute nouvelle migration ou tout nouvel acces a un objet LLM legacy :

1. mettre a jour `backend/docs/llm-db-cleanup-registry.json` ;
2. documenter la justification et la decision (`keep`, `migrate`, `freeze`, `archive`, `drop`) ;
3. mettre a jour les garde-fous si un nouveau chemin compat est temporairement autorise.

Le validateur `backend/scripts/check_llm_db_cleanup.py` et les tests associes doivent echouer si :

- un objet LLM n est pas classe dans le registre ;
- une migration LLM n est pas referencee ;
- une lecture ou ecriture legacy apparait hors des fichiers explicitement autorises.

## Contrat du harness SQLite de tests

L allowlist `allowed_secondary_missing_tables_at_head` utilisee par `backend/app/tests/integration/conftest.py`
est un contrat de harness d integration uniquement.

Elle ne definit pas une regle generale du bootstrap applicatif, ni une permission generique du garde SQLite
pour accepter des bases secondaires incompletes.

Son seul but est de tolerer, sur la SQLite secondaire de `backend/app/tests`, un petit ensemble borne de
tables ORM-only creees immediatement apres l alignement Alembic par `Base.metadata.create_all(bind=engine)`.

Toute extension de cette allowlist doit etre revue comme un changement de harness de test, avec justification
explicite des tables ajoutees et verification qu aucune table attendue par les migrations ne devient
silencieusement optionnelle.
