# Executive Summary

## Domain audited

`backend/app/api`, archetype `api-adapter-boundary-audit`.

## Overall assessment

La direction de dépendance descendante est saine: `domain` et `services` ne dépendent pas de `app.api`, et les types FastAPI ne fuient pas vers ces couches. Le risque principal est interne à l'API: plusieurs routeurs restent trop épais et orchestrent directement la persistance.

## Top risks

1. Les endpoints admin LLM observability ont deux implémentations, dont une extraite mais non montée.
2. Les routeurs API exécutent massivement SQLAlchemy et des commits, ce qui viole le rôle d'adapter HTTP.
3. Le montage API v1 possède des exceptions dans `main.py` qui ne sont pas formalisées comme inventaire canonique.

## Recommended actions

Prioriser la convergence `admin.llm.observability`, puis ajouter une garde AST de persistance routeur en mode allowlist. Ensuite seulement, extraire par lots les routeurs les plus denses vers des services.

## Story candidates to create first

Créer d'abord `SC-001`, puis `SC-004`. `SC-002` doit être découpée par lot métier avant implémentation.
