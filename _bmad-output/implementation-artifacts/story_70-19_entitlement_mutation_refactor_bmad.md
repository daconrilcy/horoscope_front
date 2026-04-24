# Story 70-19: Refactoriser et durcir les modèles SQLAlchemy des mutations d’entitlements dans un sous-domaine dédié

Status: ready-for-dev

## Story

As a Platform Architect,  
I want refactoriser et durcir les modèles SQLAlchemy liés aux audits, reviews, alertes, tentatives de delivery, handling et suppression des mutations d’entitlements, en les regroupant dans un sous-domaine dédié et en factorisant strictement les champs communs,  
so that le modèle de persistance soit robuste, explicite, DRY, extensible, aligné sur une séparation nette entre état courant, historique, référentiel et application de règles, tout en imposant une gestion centralisée et homogène des dates via `datetime_provider`.

## Context

Le modèle actuel couvre déjà les capacités fonctionnelles principales autour des mutations d’entitlements :

- review courante d’un audit ;
- historique des reviews ;
- création d’alertes ;
- journalisation des tentatives de delivery ;
- état courant de handling ;
- historique de handling ;
- règles de suppression.

Cependant, le périmètre présente plusieurs défauts structurels qui empêchent de considérer ce sous-domaine comme durci et maintenable à long terme :

- les modèles sont dispersés à plat dans `backend\app\infra\db\models` avec l’ensemble des autres modèles, sans sous-domaine dédié ;
- plusieurs tables mélangent ou rendent peu lisible la frontière entre current state et historique ;
- les champs techniques sont dupliqués dans plusieurs fichiers ;
- la gestion des dates est répétée avec des helpers locaux alors qu’un provider backend central existe déjà ;
- l’alerte centrale mélange partiellement cycle de vie métier et état technique de delivery ;
- aucune table dédiée ne trace relationnellement l’application effective d’une règle de suppression ;
- la structure actuelle n’impose pas de garde-fous suffisants pour éviter de futures dérives de modélisation.

Le backend dispose déjà d’un provider centralisé pour l’horloge système via `backend\app\core\datetime_provider.py`. Ce provider expose `datetime_provider.utcnow()`, `datetime_provider.now()`, `datetime_provider.today()` ainsi que les helpers legacy `utc_now()`, `current_datetime()` et `current_date()`. La story doit imposer que toute gestion de datetime dans ce sous-domaine repose sur ce point d’entrée unique, sans redéclaration locale d’un helper concurrent. fileciteturn1file0

La cible attendue est une version durcie avec :

- séparation explicite current state / history ;
- enrichissement maîtrisé du cycle de vie d’alerte ;
- introduction d’une table de suppression appliquée ;
- factorisation DRY via bases et mixins dédiés au sous-domaine ;
- centralisation stricte des dates et heures via `datetime_provider` ;
- arborescence dédiée sous `backend\app\infra\db\models\entitlement_mutation` ;
- un fichier par responsabilité métier imposée.

## Scope

Cette story couvre exclusivement :

- les modèles SQLAlchemy du sous-domaine entitlement mutation ;
- leur réorganisation physique en sous-domaine dédié ;
- les classes de base et mixins strictement nécessaires à ce sous-domaine ;
- les colonnes, FKs, index et contraintes associées ;
- les migrations DB requises ;
- les adaptations minimales des imports et usages applicatifs pour supporter le nouveau schéma ;
- les tests structurels et d’intégration DB liés à ce refactoring.

Cette story ne couvre pas :

- une refonte fonctionnelle large des services métier ;
- une refonte UI ;
- une refonte d’API ;
- l’ajout de nouveaux comportements métier hors ce qui est strictement nécessaire pour supporter la cible de persistance ;
- la création d’un framework générique transverse pour tous les modèles du projet au-delà de ce sous-domaine.

## Target Design

### Current state
- `CanonicalEntitlementMutationAuditReviewModel`
- `CanonicalEntitlementMutationAlertEventModel`
- `CanonicalEntitlementMutationAlertHandlingModel`
- `CanonicalEntitlementMutationAlertSuppressionRuleModel`

### History / event log
- `CanonicalEntitlementMutationAuditReviewEventModel`
- `CanonicalEntitlementMutationAlertHandlingEventModel`
- `CanonicalEntitlementMutationAlertDeliveryAttemptModel`
- `CanonicalEntitlementMutationAlertSuppressionApplicationModel`

### Shared base / mixins
- mixins de timestamps utilisant exclusivement `datetime_provider`
- mixin de `request_id`
- mixin d’ops comment si réellement partagé
- mixin d’utilisateur d’action si réellement partagé
- base(s) / mixins de snapshot ou de contexte si réellement réutilisés par plusieurs modèles du sous-domaine

## Expected file organization

La structure cible est imposée et doit être exactement la suivante :

```text
backend/
  app/
    infra/
      db/
        models/
          entitlement_mutation/
            __init__.py
            shared/
              __init__.py
              base_mixins.py
              timestamps.py
            audit/
              __init__.py
              review.py
              review_event.py
            alert/
              __init__.py
              alert_event.py
              delivery_attempt.py
              handling.py
              handling_event.py
            suppression/
              __init__.py
              suppression_rule.py
              suppression_application.py
```

Contraintes associées :

- aucun modèle de ce sous-domaine ne doit rester à plat dans `backend\app\infra\db\models` ;
- aucun fichier “fourre-tout” de type `audit.py`, `alert.py` ou `shared.py` ne doit être créé au niveau `entitlement_mutation/` ;
- aucun découpage alternatif ne doit être introduit ;
- chaque fichier métier imposé contient uniquement le modèle correspondant ;
- les `__init__.py` doivent réexporter explicitement les symboles publics utiles ;
- les imports applicatifs, ORM et de tests doivent pointer uniquement vers cette nouvelle arborescence.

## Acceptance Criteria

### AC1 — Les modèles entitlement mutation sont isolés dans un sous-domaine dédié
Tous les modèles du périmètre “canonical entitlement mutation” sont déplacés dans le sous-dossier :

`backend\app\infra\db\models\entitlement_mutation`

Aucun modèle de ce sous-domaine ne reste à la racine de `backend\app\infra\db\models` après finalisation du refactoring.

### AC2 — L’arborescence cible est implémentée exactement comme spécifiée
La structure physique des fichiers et sous-dossiers correspond exactement à la section “Expected file organization”.

Aucun sous-dossier supplémentaire, aucun regroupement alternatif et aucun fichier métier supplémentaire non prévu ne doivent être introduits dans cette story.

### AC3 — La séparation current state / history / référentiel / application est explicite
Le code final permet d’identifier sans ambiguïté :
- les tables de current state ;
- les tables d’historique append-only ;
- les tables de référentiel ;
- les tables traçant l’application effective d’une règle.

Aucune table historique n’est utilisée comme source de vérité courante.

### AC4 — Une table dédiée trace l’application effective des suppressions
Le modèle `CanonicalEntitlementMutationAlertSuppressionApplicationModel` est introduit avec une table dédiée.

Cette table contient au minimum :
- `id`
- `alert_event_id`
- `suppression_rule_id`
- `suppression_key`
- `application_mode`
- `application_reason`
- `applied_by_user_id`
- `request_id`
- `applied_at`

Elle possède une FK vers l’alerte et une FK vers la règle de suppression.

### AC5 — Le modèle d’alerte central porte explicitement son cycle de vie métier et technique
`CanonicalEntitlementMutationAlertEventModel` contient distinctement :
- `alert_status`
- `last_delivery_status`
- `last_delivery_error`
- `delivery_attempt_count`
- `first_delivered_at`
- `last_delivered_at`
- `is_suppressed`
- `suppressed_at`
- `suppression_reason`
- `updated_at`
- `closed_at`

Le modèle ne confond plus le statut global métier de l’alerte avec le dernier état technique de delivery.

### AC6 — Les snapshots métier restent figés au niveau de l’alerte
`CanonicalEntitlementMutationAlertEventModel` conserve les snapshots de contexte d’émission, incluant au minimum :
- `risk_level_snapshot`
- `review_status_snapshot` ou équivalent final validé
- `feature_code_snapshot`
- `plan_id_snapshot`
- `plan_code_snapshot`
- `actor_type_snapshot`
- `actor_identifier_snapshot`
- `sla_target_seconds_snapshot`
- `due_at_snapshot`
- `age_seconds_snapshot`

Ces champs restent stockés sur l’alerte et ne sont pas recalculés dynamiquement depuis les entités amont.

### AC7 — Le current handling d’alerte devient un vrai current state durci
`CanonicalEntitlementMutationAlertHandlingModel` contient au minimum :
- `id`
- `alert_event_id`
- `handling_status`
- `resolution_code`
- `handled_by_user_id`
- `handled_at`
- `ops_comment`
- `incident_key`
- `requires_followup`
- `followup_due_at`
- `suppression_application_key` ou référence équivalente retenue
- `handling_version`
- `request_id`
- `created_at`
- `updated_at`

Une contrainte d’unicité garantit un seul current handling par alerte.

### AC8 — Le handling history est complet et append-only
`CanonicalEntitlementMutationAlertHandlingEventModel` contient au minimum :
- `id`
- `alert_event_id`
- `event_type`
- `handling_status`
- `resolution_code`
- `handled_by_user_id`
- `handled_at` ou `occurred_at`
- `ops_comment`
- `incident_key`
- `requires_followup`
- `followup_due_at`
- `suppression_application_key`
- `request_id`

Cette table ne porte aucune responsabilité de current state.

### AC9 — La review courante est versionnée et tracée
`CanonicalEntitlementMutationAuditReviewModel` contient au minimum :
- `id`
- `audit_id`
- `review_status`
- `reviewed_by_user_id`
- `reviewed_at`
- `review_comment`
- `incident_key`
- `review_version`
- `request_id`
- `created_at`
- `updated_at`

Une contrainte d’unicité garantit une seule review courante par audit.

### AC10 — L’historique de review est explicitement typé
`CanonicalEntitlementMutationAuditReviewEventModel` contient un champ `event_type` et conserve les transitions de review, incluant :
- ancien statut
- nouveau statut
- ancien commentaire
- nouveau commentaire
- ancienne incident key
- nouvelle incident key
- utilisateur
- date d’occurrence
- `request_id`

### AC11 — Les tentatives de delivery sont enrichies pour l’exploitation prod
`CanonicalEntitlementMutationAlertDeliveryAttemptModel` contient au minimum :
- `delivery_provider`
- `response_code`
- `is_retryable`

La contrainte d’unicité `(alert_event_id, attempt_number)` est conservée.

### AC12 — Les règles de suppression restent un référentiel courant durci
`CanonicalEntitlementMutationAlertSuppressionRuleModel` contient au minimum :
- `alert_kind`
- `feature_code`
- `plan_code`
- `actor_type`
- `suppression_key`
- `rule_status` si retenu dans le design final
- `ops_comment`
- `is_active`
- `created_by_user_id`
- `created_at`
- `updated_by_user_id`
- `updated_at`

Une contrainte d’unicité logique empêche les doublons fonctionnels.

### AC13 — Le DRY est appliqué via bases et mixins dédiés au sous-domaine
Les champs techniques et transverses réellement partagés sont factorisés dans `shared/base_mixins.py`.

La story mutualise au minimum, là où pertinent :
- les timestamps ;
- `request_id` ;
- `ops_comment` ;
- les utilisateurs d’action quand la factorisation reste lisible.

Aucune duplication évitable de colonnes identiques ne subsiste dans les modèles refactorés.

### AC14 — Toute gestion de datetime utilise exclusivement le provider backend central
Toute gestion de date ou datetime dans les modèles refactorés, dans leurs valeurs par défaut et dans les mixins associés, utilise exclusivement le provider central défini dans `backend\app\core\datetime_provider.py`. fileciteturn1file0

Sont autorisés :
- `datetime_provider.utcnow()`
- `datetime_provider.now(...)`
- `datetime_provider.today(...)`
- ou, si nécessaire pour compatibilité locale, les wrappers du même module (`utc_now`, `current_datetime`, `current_date`)

Sont interdits dans ce sous-domaine :
- tout appel direct à `datetime.now(...)` ;
- tout appel direct à `date.today()` ;
- toute redéclaration locale d’un helper `_utc_now()` ;
- toute source de temps concurrente à `datetime_provider`.

### AC15 — Le helper datetime partagé du sous-domaine s’appuie sur `datetime_provider`
Si un helper de timestamp est introduit dans `entitlement_mutation/shared/timestamps.py`, il doit être un simple point de réutilisation local du sous-domaine s’appuyant exclusivement sur le provider central backend, sans logique concurrente ni comportement divergent. fileciteturn1file0

### AC16 — Les noms des modèles et fichiers reflètent explicitement leur responsabilité
Le code final adopte un naming non ambigu :
- `AlertEvent` pour l’entité centrale d’alerte ;
- `AlertDeliveryAttempt` pour le journal technique ;
- `AlertHandling` pour le current state ;
- `AlertHandlingEvent` pour l’historique ;
- `AlertSuppressionRule` pour le référentiel ;
- `AlertSuppressionApplication` pour la trace d’application ;
- `AuditReview` pour le current state ;
- `AuditReviewEvent` pour l’historique.

Le suffixe `Event` n’est plus utilisé pour désigner un current state.

### AC17 — Les relations, FKs, index et contraintes sont strictement alignés sur la cible
Le schéma final garantit explicitement :
- une review courante unique par audit ;
- un handling courant unique par alerte ;
- une tentative unique par numéro d’essai et alerte ;
- une règle de suppression logiquement unique selon ses critères ;
- une suppression appliquée traçable relationnellement.

### AC18 — Les anciens chemins et fichiers obsolètes sont supprimés
Une fois les imports migrés et les tests validés, les anciens fichiers de modèles devenus obsolètes à la racine de `backend\app\infra\db\models` sont supprimés.

Aucune double déclaration ORM de la même table ou du même modèle ne doit subsister.

### AC19 — Les migrations DB sont cohérentes et sans perte de données utiles
Les migrations permettent :
- l’ajout des nouvelles tables ;
- l’ajout des nouvelles colonnes ;
- les renommages nécessaires ;
- le backfill des champs calculables ;
- la conservation des données existantes utiles ;
- la recréation explicite des contraintes et index.

### AC20 — Les tests valident schéma, DRY, imports et discipline datetime
Les tests couvrent :
- la structure des modèles ;
- les contraintes d’unicité ;
- les FKs ;
- les flux de current state et history ;
- la création d’une suppression appliquée ;
- la matérialisation des champs hérités ;
- l’usage de l’arborescence cible ;
- l’absence de helper `_utc_now()` local ;
- l’usage exclusif de `datetime_provider` comme source de temps.

## Tasks / Subtasks

### Task 1 — Créer l’arborescence cible du sous-domaine entitlement mutation
#### Subtasks
1. Créer le dossier `backend\app\infra\db\models\entitlement_mutation`.
2. Créer les sous-dossiers obligatoires :
   - `shared`
   - `audit`
   - `alert`
   - `suppression`
3. Créer un `__init__.py` dans :
   - `entitlement_mutation`
   - `entitlement_mutation\shared`
   - `entitlement_mutation\audit`
   - `entitlement_mutation\alert`
   - `entitlement_mutation\suppression`
4. Créer les fichiers imposés :
   - `shared\base_mixins.py`
   - `shared\timestamps.py`
   - `audit\review.py`
   - `audit\review_event.py`
   - `alert\alert_event.py`
   - `alert\delivery_attempt.py`
   - `alert\handling.py`
   - `alert\handling_event.py`
   - `suppression\suppression_rule.py`
   - `suppression\suppression_application.py`
5. Ne créer aucun autre fichier métier dans cette story.
6. Ne laisser aucun modèle du sous-domaine à la racine de `backend\app\infra\db\models`.

#### Exit criteria
- l’arborescence cible existe exactement comme spécifiée ;
- aucun découpage alternatif n’a été introduit.

### Task 2 — Mettre en place la gestion partagée des datetime et mixins de base
#### Subtasks
1. Importer `datetime_provider` depuis `backend\app\core\datetime_provider.py` comme source unique de temps pour ce sous-domaine. fileciteturn1file0
2. Créer dans `shared\timestamps.py` un point de réutilisation local s’appuyant exclusivement sur `datetime_provider`.
3. Interdire toute redéclaration locale de `_utc_now()` dans les fichiers métiers.
4. Créer dans `shared\base_mixins.py` les mixins réellement nécessaires pour :
   - `created_at`
   - `updated_at`
   - `request_id`
   - `ops_comment` si partagé
   - utilisateur d’action si partagé sans perte de clarté
5. Vérifier que chaque mixin introduit est utilisé par au moins deux modèles du sous-domaine.
6. Ne pas créer de mixin spéculatif non utilisé dans cette story.
7. Vérifier que tous les defaults datetime reposent sur `datetime_provider` et non sur `datetime.now()` ou `date.today()`. fileciteturn1file0

#### Exit criteria
- aucune source de temps concurrente ;
- aucun helper local dupliqué ;
- mixins partagés créés et réellement utilisés.

### Task 3 — Refactoriser le current review d’audit
#### Subtasks
1. Créer ou déplacer `CanonicalEntitlementMutationAuditReviewModel` dans `audit\review.py`.
2. Conserver la table métier correspondante.
3. Ajouter les colonnes :
   - `review_version`
   - `request_id`
   - `created_at`
   - `updated_at`
4. Conserver les colonnes métier existantes de review.
5. Appliquer les mixins communs pertinents.
6. Conserver ou recréer explicitement la contrainte d’unicité sur `audit_id`.
7. Vérifier que ce modèle représente uniquement le current state.

#### Exit criteria
- review current state versionnée ;
- unicité par audit garantie ;
- aucun champ d’historique parasite.

### Task 4 — Refactoriser l’historique de review d’audit
#### Subtasks
1. Créer ou déplacer `CanonicalEntitlementMutationAuditReviewEventModel` dans `audit\review_event.py`.
2. Ajouter `event_type`.
3. Conserver les colonnes de transition :
   - ancien statut
   - nouveau statut
   - ancien commentaire
   - nouveau commentaire
   - ancienne incident key
   - nouvelle incident key
4. Ajouter `request_id` via mixin si retenu.
5. Conserver l’utilisateur et la date d’occurrence.
6. Vérifier que cette table reste strictement historique et append-only.

#### Exit criteria
- review history typée ;
- aucun rôle de current state.

### Task 5 — Refactoriser le modèle central d’alerte
#### Subtasks
1. Créer ou déplacer `CanonicalEntitlementMutationAlertEventModel` dans `alert\alert_event.py`.
2. Renommer `effective_review_status_snapshot` en `review_status_snapshot` si ce renommage est retenu.
3. Ajouter :
   - `alert_status`
   - `last_delivery_status`
   - `last_delivery_error`
   - `delivery_attempt_count`
   - `first_delivered_at`
   - `last_delivered_at`
   - `is_suppressed`
   - `suppressed_at`
   - `suppression_reason`
   - `updated_at`
   - `closed_at`
4. Conserver les snapshots métier existants.
5. Vérifier qu’aucune donnée de current handling n’est portée par ce modèle.
6. Vérifier que tous les defaults datetime utilisent `datetime_provider`.

#### Exit criteria
- alerte centrale durcie ;
- distinction claire entre cycle de vie métier et delivery technique.

### Task 6 — Refactoriser les tentatives de delivery
#### Subtasks
1. Créer ou déplacer `CanonicalEntitlementMutationAlertDeliveryAttemptModel` dans `alert\delivery_attempt.py`.
2. Ajouter :
   - `delivery_provider`
   - `response_code`
   - `is_retryable`
3. Conserver :
   - `alert_event_id`
   - `attempt_number`
   - le lien FK vers l’alerte
4. Conserver ou recréer explicitement l’unicité `(alert_event_id, attempt_number)`.
5. Appliquer les mixins partagés pertinents.
6. Vérifier que cette table reste un journal technique append-only.
7. Vérifier que tous les defaults datetime utilisent `datetime_provider`.

#### Exit criteria
- delivery attempts enrichies ;
- contrainte d’unicité conservée ;
- table strictement historique.

### Task 7 — Refactoriser le current handling d’alerte
#### Subtasks
1. Créer ou déplacer `CanonicalEntitlementMutationAlertHandlingModel` dans `alert\handling.py`.
2. Si nécessaire, renommer l’ancien modèle `...AlertEventHandlingModel` vers le nom cible.
3. Ajouter :
   - `resolution_code`
   - `incident_key`
   - `requires_followup`
   - `followup_due_at`
   - `handling_version`
   - `request_id`
   - `created_at`
   - `updated_at`
4. Conserver :
   - `handling_status`
   - `handled_by_user_id`
   - `handled_at`
   - `ops_comment`
5. Clarifier le rôle du champ de suppression dans ce modèle ; ne conserver qu’un pointeur de référence si nécessaire.
6. Conserver ou recréer explicitement l’unicité sur `alert_event_id`.
7. Appliquer les mixins partagés pertinents.
8. Vérifier que tous les defaults datetime utilisent `datetime_provider`.

#### Exit criteria
- current handling unique par alerte ;
- modèle suffisamment riche pour le pilotage ops ;
- aucun glissement de responsabilité avec la suppression appliquée.

### Task 8 — Refactoriser l’historique de handling
#### Subtasks
1. Créer ou déplacer `CanonicalEntitlementMutationAlertHandlingEventModel` dans `alert\handling_event.py`.
2. Si nécessaire, renommer l’ancien modèle `...AlertEventHandlingEventModel` vers le nom cible.
3. Ajouter :
   - `event_type`
   - `resolution_code`
   - `incident_key`
   - `requires_followup`
   - `followup_due_at`
4. Conserver :
   - `handling_status`
   - `handled_by_user_id`
   - `handled_at` ou harmoniser vers `occurred_at`
   - `ops_comment`
   - la référence de suppression si retenue
   - `request_id`
5. Conserver le lien FK vers l’alerte.
6. Vérifier qu’aucune contrainte ne transforme cette table en current state.
7. Vérifier que tous les defaults datetime utilisent `datetime_provider`.

#### Exit criteria
- handling history complète ;
- `event_type` présent ;
- table append-only.

### Task 9 — Refactoriser le référentiel de règles de suppression
#### Subtasks
1. Créer ou déplacer `CanonicalEntitlementMutationAlertSuppressionRuleModel` dans `suppression\suppression_rule.py`.
2. Conserver :
   - `alert_kind`
   - `feature_code`
   - `plan_code`
   - `actor_type`
   - `suppression_key`
   - `is_active`
   - `ops_comment`
   - `created_by_user_id`
   - `created_at`
   - `updated_by_user_id`
   - `updated_at`
3. Ajouter `rule_status` uniquement si retenu dans le design final.
4. Appliquer les mixins partagés pertinents.
5. Conserver ou recréer explicitement l’unicité logique basée sur les critères normalisés.
6. Vérifier que cette table reste un référentiel courant et non un historique.
7. Vérifier que tous les defaults datetime utilisent `datetime_provider`.

#### Exit criteria
- référentiel de règles stabilisé ;
- unicité logique préservée ;
- source de temps unifiée.

### Task 10 — Introduire le modèle de suppression appliquée
#### Subtasks
1. Créer `CanonicalEntitlementMutationAlertSuppressionApplicationModel` dans `suppression\suppression_application.py`.
2. Déclarer la table `canonical_entitlement_mutation_alert_suppression_applications`.
3. Ajouter :
   - `id`
   - `alert_event_id`
   - `suppression_rule_id`
   - `suppression_key`
   - `application_mode`
   - `application_reason`
   - `applied_by_user_id`
   - `request_id`
   - `applied_at`
4. Ajouter la FK vers l’alerte.
5. Ajouter la FK vers la règle de suppression.
6. Ajouter les index nécessaires sur :
   - `alert_event_id`
   - `suppression_rule_id`
   - `applied_at`
7. Vérifier que cette table porte exclusivement la traçabilité relationnelle de l’application effective d’une suppression.
8. Vérifier que tous les defaults datetime utilisent `datetime_provider`.

#### Exit criteria
- table créée ;
- double rattachement alerte + règle ;
- traçabilité complète et relationnelle.

### Task 11 — Mettre à jour les `__init__.py` et les imports
#### Subtasks
1. Mettre à jour chaque `__init__.py` de sous-dossier pour réexporter explicitement les symboles publics utiles.
2. Mettre à jour `entitlement_mutation\__init__.py` pour réexporter l’ensemble des modèles publics du sous-domaine.
3. Mettre à jour tous les imports applicatifs.
4. Mettre à jour tous les imports ORM.
5. Mettre à jour tous les imports de tests.
6. Vérifier qu’un seul chemin d’import canonique subsiste pour chaque modèle refactoré.
7. Supprimer les anciens imports devenus obsolètes.

#### Exit criteria
- imports réalignés ;
- plus de double chemin d’import durable.

### Task 12 — Écrire les migrations DB
#### Subtasks
1. Générer ou écrire une migration pour les nouvelles colonnes des tables existantes.
2. Générer ou écrire une migration pour la nouvelle table de suppression appliquée.
3. Gérer explicitement les renommages de colonnes retenus.
4. Recréer explicitement les FKs impactées.
5. Recréer explicitement les contraintes d’unicité impactées.
6. Recréer explicitement les index impactés.
7. Backfiller `delivery_attempt_count` depuis les tentatives existantes si des données sont présentes.
8. Backfiller `first_delivered_at`, `last_delivered_at`, `last_delivery_status`, `last_delivery_error` lorsque calculable.
9. Backfiller `created_at` / `updated_at` des nouveaux current states lorsque calculable.
10. Documenter explicitement toute donnée non backfillable.
11. Vérifier que la migration est réversible ou documenter clairement la part non réversible.

#### Exit criteria
- migration exécutable ;
- schéma cible atteignable sans perte de données utiles.

### Task 13 — Adapter les usages applicatifs minimaux
#### Subtasks
1. Identifier tous les services et modules qui écrivent dans les modèles refactorés.
2. Mettre à jour les écritures du current review.
3. Mettre à jour les écritures du review history.
4. Mettre à jour les écritures de l’alerte centrale.
5. Mettre à jour les écritures des delivery attempts si de nouvelles colonnes deviennent obligatoires.
6. Mettre à jour les écritures du current handling.
7. Mettre à jour les écritures du handling history.
8. Ajouter l’écriture dans `AlertSuppressionApplicationModel` lors de toute suppression effective.
9. Vérifier qu’aucun service ne lit une table d’historique comme current state.
10. Limiter les changements applicatifs au strict minimum nécessaire à la compatibilité du nouveau schéma.

#### Exit criteria
- flux d’écriture compatibles ;
- aucune dépendance illégitime à l’historique comme source de vérité.

### Task 14 — Supprimer les anciens fichiers obsolètes et éliminer les doubles déclarations ORM
#### Subtasks
1. Identifier les anciens fichiers de modèles du sous-domaine restés à la racine.
2. Vérifier que tous les imports ont été migrés.
3. Vérifier que les tests passent avec la nouvelle arborescence.
4. Supprimer les anciens fichiers obsolètes.
5. Vérifier qu’aucune table n’est déclarée deux fois via deux modèles différents.
6. Vérifier que le chargement SQLAlchemy reste correct.
7. Vérifier que la découverte Alembic n’est pas cassée.

#### Exit criteria
- aucun reliquat de modèle obsolète ;
- aucune double déclaration ORM ;
- chargement ORM et Alembic fonctionnels.

### Task 15 — Écrire les tests structurels et d’intégration DB
#### Subtasks
1. Ajouter un test vérifiant qu’une seule review courante peut exister par audit.
2. Ajouter un test vérifiant qu’un seul current handling peut exister par alerte.
3. Ajouter un test vérifiant l’unicité `(alert_event_id, attempt_number)`.
4. Ajouter un test vérifiant la FK `alert_event_id` de la suppression appliquée.
5. Ajouter un test vérifiant la FK `suppression_rule_id` de la suppression appliquée.
6. Ajouter un test vérifiant la présence des colonnes durcies sur `AlertEvent`.
7. Ajouter un test vérifiant la présence de `event_type` sur `AuditReviewEvent`.
8. Ajouter un test vérifiant la présence de `event_type` sur `AlertHandlingEvent`.
9. Ajouter un test vérifiant que les modèles refactorés n’embarquent plus de helper `_utc_now()` local.
10. Ajouter un test vérifiant que les defaults datetime de ce sous-domaine s’appuient sur `datetime_provider`.
11. Ajouter un test vérifiant que les colonnes héritées via mixins sont bien matérialisées.
12. Ajouter un test vérifiant que les imports canoniques passent par `entitlement_mutation`.
13. Ajouter au moins un test de flux complet :
    `audit review -> alert event -> delivery attempt -> alert handling -> suppression application`

#### Exit criteria
- couverture structurelle et DB en place ;
- discipline datetime testée ;
- flux principal couvert.

### Task 16 — Effectuer le contrôle final anti-dérive
#### Subtasks
1. Vérifier qu’aucun modèle refactoré ne redéclare `_utc_now()`.
2. Vérifier qu’aucun modèle refactoré n’utilise `datetime.now()` ou `date.today()` directement.
3. Vérifier que toute source de temps provient de `datetime_provider`. fileciteturn1file0
4. Vérifier que chaque modèle appartient clairement à une catégorie :
   - current state
   - history
   - référentiel
   - application
5. Vérifier que chaque fichier contient uniquement le modèle imposé.
6. Vérifier que les snapshots restent sur l’alerte.
7. Vérifier que les suppressions appliquées sont traçables relationnellement.
8. Vérifier qu’aucun ancien chemin d’import ambigu ne subsiste.
9. Vérifier que la structure finale correspond exactement à la structure cible.

#### Exit criteria
- aucun reliquat structurel ambigu ;
- discipline datetime respectée ;
- design final conforme à la cible.

### Review Findings

- [ ] [Review][Patch] Le sous-domaine `entitlement_mutation/` imposé par la story n’existe pas et les modèles restent à plat sous `backend\app\infra\db\models`, ce qui viole directement AC1, AC2 et AC18. [backend/app/infra/db/models/__init__.py:18]
- [ ] [Review][Patch] `CanonicalEntitlementMutationAlertEventModel` conserve un modèle d’alerte centré sur `delivery_status`/`delivery_error`/`delivered_at` et n’introduit pas les champs de cycle de vie courant exigés (`alert_status`, `last_delivery_status`, `delivery_attempt_count`, suppression, `updated_at`, `closed_at`). L’implémentation actuelle ne sépare donc toujours pas statut métier et état technique de delivery comme demandé par AC5. [backend/app/infra/db/models/canonical_entitlement_mutation_alert_event.py:39]
- [ ] [Review][Patch] La traçabilité relationnelle d’application de suppression n’est pas implémentée: aucun modèle `CanonicalEntitlementMutationAlertSuppressionApplicationModel` n’existe et le current/history handling ne stocke qu’un `suppression_key` libre. Cela bloque AC4, AC7, AC8 et AC17. [backend/app/infra/db/models/canonical_entitlement_mutation_alert_event_handling.py:32]
- [ ] [Review][Patch] Le current review d’audit n’est ni versionné ni complètement tracé: `review_version`, `request_id`, `created_at` et `updated_at` manquent encore, ce qui ne satisfait pas AC9. [backend/app/infra/db/models/canonical_entitlement_mutation_audit_review.py:27]
- [ ] [Review][Patch] Les tables d’historique ne sont pas encore des event logs explicitement typés conformes à la story: `CanonicalEntitlementMutationAuditReviewEventModel` n’a pas de `event_type`, et le handling history ne porte ni `event_type`, ni `resolution_code`, ni `incident_key`, ni suivi de follow-up. AC8 et AC10 restent donc non couverts. [backend/app/infra/db/models/canonical_entitlement_mutation_audit_review_event.py:26]

## Dev Notes

### Non-negotiable implementation rules
- Ne pas laisser de modèles du sous-domaine entitlement mutation à plat dans `backend\app\infra\db\models`.
- Ne pas créer de fichier agrégateur métier au niveau `entitlement_mutation/` en dehors de `__init__.py`.
- Ne pas fusionner plusieurs modèles métier distincts dans un même fichier lorsque la structure cible impose un fichier dédié.
- Ne pas introduire de découpage alternatif à `shared / audit / alert / suppression`.
- Ne pas conserver les anciens fichiers racine une fois les imports migrés et les tests passés.
- Ne pas conserver deux chemins d’import durables pour une même source de vérité.
- Ne pas introduire de mixin non utilisé dans cette story.
- Ne pas déplacer la responsabilité des snapshots hors de l’alerte.
- Ne pas utiliser une table d’historique comme source de vérité courante.
- Ne pas redéclarer `_utc_now()` localement.
- Ne pas utiliser `datetime.now(...)`, `date.today()` ou toute autre source de temps concurrente.
- Toute gestion de datetime doit provenir exclusivement du provider central `backend\app\core\datetime_provider.py`. fileciteturn1file0

## Testing

Les tests doivent démontrer :
- l’intégrité du schéma ;
- la présence des colonnes attendues ;
- la bonne matérialisation des champs issus de mixins ;
- la validité des FKs ;
- la validité des contraintes d’unicité ;
- le respect de la structure de modules imposée ;
- le respect de la discipline datetime centralisée ;
- la compatibilité du flux principal de bout en bout.

## Definition of Done

La story est Done uniquement si :

- l’arborescence `backend\app\infra\db\models\entitlement_mutation` existe exactement selon la cible ;
- chaque modèle concerné vit dans le fichier imposé ;
- les `__init__.py` réexportent explicitement les symboles utiles ;
- aucun modèle du sous-domaine ne reste à la racine de `backend\app\infra\db\models` ;
- les bases/mixins partagés sont introduits et réellement utilisés ;
- toute gestion de datetime passe exclusivement par `datetime_provider` ;
- aucun helper `_utc_now()` local ne subsiste ;
- la table de suppression appliquée existe ;
- current states, histories, référentiels et applications sont clairement séparés ;
- les migrations passent ;
- les tests passent ;
- aucun reliquat structurel ambigu ne subsiste.
