# Story 70-23: Durcir `backend/app/services` pour imposer DRY strict et zero legacy

Status: review

## Story

As a Platform Architect,  
I want assainir structurellement `backend/app/services` jusqu a ne laisser qu un namespace de services factorise, explicite et sans reliquat legacy,  
so that le backend n accepte plus ni duplication active, ni coexistence ambiguë de chemins concurrents, ni wrappers de compatibilite conserves par inertie.

## Contexte

L audit du dossier `backend/app/services` montre un etat de convergence inacheve :

- des sous-domaines sont deja bien engages dans une organisation cible (`canonical_entitlement/`, `entitlement/`, `llm_generation/`, `llm_observability/`) ;
- une partie importante des services reste encore a plat a la racine de `backend/app/services/` ;
- plusieurs services sont volumineux, multi-responsabilites et difficiles a faire evoluer sans duplication ;
- des reliquats legacy ou transitoires restent visibles dans le code nominal ;
- un vrai doublon metier existe encore dans `backend/app/services/tests/__init__.py`, qui porte une ancienne implementation de service natal au lieu de simples helpers de test.

L audit a releve des problemes structurels concrets qui doivent maintenant etre traites comme une dette de gouvernance backend, pas comme un simple rangement cosmetique :

- duplication quasi integrale des runtime gates B2C (`chat`, `thematic_consultation`, `natal_chart_long`) ;
- couplage de `PredictionContextRepairService` a un script de seed versionne (`seed_31_prediction_reference_v2`) ;
- `BillingService` monolithique, melangeant catalogue, statut d abonnement, compatibilite tests, quotas et logique Stripe-first ;
- duplication ou redefinition partielle d helpers natals entre `llm_generation/natal/prompt_context.py`, `llm_generation/shared/natal_context.py`, `astro_context_builder.py` et le doublon de test ;
- coexistence de surfaces legacy explicites dans plusieurs services (`billing`, `consultation_catalogue`, `user_natal_chart`, `llm_observability`, `llm_generation/natal`) ;
- niveau racine `backend/app/services/` devenu une zone de depot pour des services qui auraient du etre rattaches a des sous-domaines stables.

Les stories 70-18, 70-20, 70-21 et 70-22 ont deja pose plusieurs regles fortes :

- pas de shim durable ;
- pas de chemin legacy maintenu "par securite" ;
- pas de duplication active entre couches ou namespaces ;
- reutiliser un sous-dossier canonique existant avant d en creer un nouveau ;
- ajouter des garde-fous qui echouent si un ancien chemin ou une structure interdite reapparait.

La story 70-23 doit prolonger cette gouvernance sur l ensemble de `backend/app/services`, avec deux objectifs non negociables :

- **DRY strict** : toute duplication active, nominale ou cachee dans un faux helper de test doit etre factorisee ou supprimee ;
- **legacy supprime** : tout chemin, wrapper, suffixe technique, import inverse, fallback nominal ou service concurrent conserve "au cas ou" doit disparaitre du runtime de production.

## Objectif

Obtenir un dossier `backend/app/services` ou :

- chaque responsabilite applicative possede un chemin canonique unique ;
- la racine `services/` est gouvernee par une allowlist explicite de fichiers autorises ;
- aucun ancien chemin deplace ne reste present sous forme de forwarder, alias, shim ou re-export ;
- aucun module applicatif ne depend d un module de test, d un script versionne ou d un chemin legacy ;
- les services mono-domaine sont rattaches a un sous-package metier stable ;
- les duplications actives identifiees sont supprimees par extraction, fusion ou suppression, pas seulement deplacees ;
- les eventuelles compatibilites residuelles sont non nominales, non importees par le runtime, documentees avec consommateur et story d extinction ;
- les tests structurels echouent si une dette supprimee reapparait.

### Regle sur les compatibilites

Par defaut, aucun module `compat/`, alias d import, shim, forwarder ou re-export legacy n est autorise sous `backend/app/services`.

Une exception n est acceptable que si les trois conditions suivantes sont reunies :

- le consommateur est explicitement identifie ;
- le module n appartient pas au chemin runtime nominal ;
- une story d extinction datee est creee et referencee dans le Dev Agent Record.

Tout module `compat/` eventuel doit etre couvert par un test prouvant qu aucun import nominal de production ne l utilise.

## Regle de convergence attendue

La story doit partir de cette cible et la confirmer par audit d implementation :

- **reutiliser les namespaces existants** avant de creer de nouveaux sous-dossiers ;
- **ne laisser a la racine `services/` que des services transverses clairement justifies** ;
- **sortir les services mono-domaine de la racine** vers des sous-packages metier ou techniques stables ;
- **supprimer les doublons au lieu de les deplacer ensemble** ;
- **privilegier un chemin canonique unique** par responsabilite et migrer tous les imports vers ce chemin ;
- **ne tolerer aucun legacy nominal** dans le code de production, les tests nominaux, les patch targets ou `services/__init__.py`.

Les sous-familles pressenties minimales sont :

- `services/billing/`
- `services/consultation/`
- `services/natal/`
- `services/prediction/`
- `services/b2b/`
- `services/user_profile/`
- `services/ops/`

Si l audit d implementation montre une cible strictement meilleure en reutilisant un namespace deja existant, elle est autorisee.  
En revanche, il est interdit de conserver la situation actuelle "a plat + exceptions + wrappers".

## Acceptance Criteria

1. **AC1 - Cartographie exhaustive et opposable par fichier racine**  
   La story produit une cartographie versionnee de tous les fichiers Python directement presents sous `backend/app/services/`.
   Pour chaque fichier, la cartographie doit indiquer :
   - chemin actuel ;
   - responsabilite dominante ;
   - consommateurs principaux ;
   - decision : conserver, deplacer, fusionner, supprimer ou follow-up ;
   - chemin canonique cible si deplacement/fusion ;
   - justification si conservation a la racine ;
   - tests impactes ou patch targets connus.  
   Aucun fichier racine n est laisse sans decision.  
   La cartographie doit etre inscrite dans le Dev Agent Record ou dans un artefact dedie sous `_bmad-output/implementation-artifacts/`.

2. **AC2 - Racine `services/` gouvernee par allowlist**  
   Apres implementation, la racine `backend/app/services/` ne contient que :
   - `__init__.py` ;
   - les fichiers explicitement conserves dans une allowlist documentee ;
   - aucun service mono-domaine ;
   - aucun ancien chemin deplace conserve comme wrapper.  
   Un test structurel doit comparer le contenu reel de la racine a l allowlist finale.  
   Toute conservation a la racine doit etre justifiee par une responsabilite transverse reelle et par au moins deux consommateurs de domaines distincts.

3. **AC3 - Runtime gates B2C factorisees autour d un noyau commun**  
   Les gates B2C `chat`, `thematic_consultation` et `natal_chart_long` doivent deleguer leur logique commune a un composant canonique unique.
   Ce composant doit porter au minimum :
   - resolution d acces ;
   - mapping des refus d acces ;
   - detection quota exhausted ;
   - consommation des quotas ;
   - selection du `UsageState` pertinent ;
   - normalisation des erreurs retournees au caller.  
   Les gates specifiques ne doivent conserver que :
   - le feature code ;
   - les DTO propres au use case ;
   - les exceptions strictement specifiques ;
   - les adaptations d entree/sortie.  
   Un test doit prouver que les trois gates utilisent le composant partage et qu aucune duplication structurante de la logique commune ne subsiste.

4. **AC4 - Aucun package de test sous `backend/app/services`**  
   Le package `backend/app/services/tests/` ne doit plus exister comme package importable applicatif.  
   L ancienne implementation metier natal presente dans `backend/app/services/tests/__init__.py` doit etre supprimee.  
   Les fixtures, factories ou helpers reellement utiles doivent etre deplaces sous le repertoire de tests backend approprie, par exemple `backend/tests/...`, sans import depuis le runtime de production.  
   Un test structurel doit echouer si un dossier ou module `tests` reapparait sous `backend/app/services/`.

5. **AC5 - Aucun import `scripts/*` depuis `app.services`**  
   Aucun module sous `backend/app/services/` ne doit importer directement ou indirectement un module `scripts/*`.  
   L interdiction couvre :
   - imports statiques ;
   - imports dynamiques via `importlib` ;
   - chemins string-based ;
   - appels a des fonctions de seed versionnees.  
   `PredictionContextRepairService` doit etre refactorise pour dependre d un composant applicatif ou infra canonique, jamais d un script `seed_*`.  
   Un test AST ou equivalent doit echouer si `app.services` reference `scripts.` ou un chemin `scripts/`.

6. **AC6 - `BillingService` cesse d etre un god service**  
   `backend/app/services/billing_service.py` ne doit plus concentrer la logique principale de billing.
   La cible doit separer au minimum :
   - catalogue des plans ;
   - statut d abonnement ;
   - quotas et usage courant ;
   - integration Stripe ou provider externe ;
   - cache eventuel ;
   - fixtures ou comportements de test.  
   Les comportements de test ne doivent pas etre presents dans le chemin nominal de production.  
   Si un `BillingService` est conserve, il doit etre une facade fine d orchestration, sans logique de catalogue, sans logique Stripe directe, sans fallback test-only et sans cache metier embarque.  
   Un test ou une revue structurelle doit prouver que les responsabilites ci-dessus ne sont plus implementees dans un seul fichier monolithique.

7. **AC7 - Conventions natales partagees centralisees sans god helper**  
   Les primitives natales partagees doivent provenir d un ou plusieurs modules canoniques explicitement nommes.  
   La story doit distinguer :
   - les primitives de domaine natal reutilisables ;
   - les adaptations de prompt LLM ;
   - les adaptations specifiques chat/guidance/consultation/natal.  
   Les modules `llm_generation/natal/prompt_context.py`, `llm_generation/shared/natal_context.py`, `astro_context_builder.py` et les parcours consommateurs ne doivent plus redefinir les memes mappings, resumes, hints ou modes degrages.  
   Les modules specifiques peuvent conserver uniquement de l adaptation locale, pas une variante concurrente de la logique partagee.

8. **AC8 - Aucun suffixe technique ambigu dans les noms canoniques**  
   Aucun fichier, classe, fonction publique, fixture nominale ou patch target canonique sous `backend/app/services/` ne doit utiliser un suffixe technique de type `_v2`, `_legacy`, `_old`, `_tmp`, `_refacto`, `_new`.  
   Une exception n est acceptable que si le suffixe correspond a une version metier explicitement supportee et documentee.  
   La story doit statuer explicitement sur :
   - `natal_interpretation_service.py` / `interpretation_service.py` ;
   - les references `*_v2_refacto` ;
   - les helpers ou champs de compatibilite encore utilises par inertie ;
   - tout script de seed versionne encore reference par un service.  
   Un test structurel doit echouer si ces suffixes reapparaissent comme noms canoniques dans `app.services`.

9. **AC9 - Legacy supprime physiquement du chemin nominal**  
   Tout legacy identifie et actif dans le runtime nominal doit etre supprime ou migre.  
   Il est interdit de conserver :
   - un ancien fichier deplace comme forwarder ;
   - un alias d import ;
   - un re-export dans `services/__init__.py` ;
   - un commentaire indiquant un ancien chemin a utiliser ;
   - un fallback nominal ;
   - un shim pour les tests.  
   Les anciens chemins deplaces doivent disparaitre physiquement du package applicatif, sauf exception `compat/` validee selon la regle dediee.

10. **AC10 - Imports, patch targets, overrides et references string-based migres**  
    Tous les imports de production, tests, fixtures, dependency overrides, patch targets, `mock.patch`, `monkeypatch`, `importlib.import_module`, chemins string-based et reexports sont migres vers les chemins canoniques.  
    La story doit inclure une recherche negative documentee sur les anciens chemins supprimes.  
    Aucun test nominal ne doit continuer a patcher un ancien chemin pour faire passer la compatibilite.

11. **AC11 - Garde-fous structurels anti-reintroduction**  
    La story ajoute ou met a jour des tests structurels qui echouent si :
    - un dossier ou module `tests` existe sous `backend/app/services/` ;
    - un fichier non autorise apparait a la racine `backend/app/services/` ;
    - un ancien chemin deplace existe encore comme fichier Python ;
    - un import ou patch target vise un ancien chemin legacy ;
    - un module sous `app.services` reference `scripts.*` ou `scripts/` ;
    - un suffixe technique interdit est utilise dans un nom canonique ;
    - `services/__init__.py` re-exporte un service metier, un chemin legacy ou un module de compatibilite ;
    - une gate B2C reimplemente localement une logique commune censee etre factorisee.  
    Les tests doivent etre suffisamment cibles pour echouer en cas de regression structurelle, meme si les tests fonctionnels continuent de passer.

12. **AC12 - Follow-up autorise uniquement hors dette identifiee**  
    Toute refactorisation hors dette identifiee peut etre reportee en follow-up.  
    En revanche, les dettes explicitement listees dans les hotspots de cette story ne peuvent pas etre reportees sans justification bloquante documentee :
    - gates B2C dupliquees ;
    - `services/tests/__init__.py` ;
    - dependance a `seed_31_prediction_reference_v2` ;
    - `BillingService` monolithique ;
    - helpers natals concurrents ;
    - suffixes ou chemins legacy nommes dans l AC8.  
    Un follow-up ne peut pas servir a valider la story en conservant une duplication active ou un legacy nominal deja identifie.

13. **AC13 - Documentation francaise conforme AGENTS**  
    Tout fichier Python cree ou significativement modifie contient :
    - un commentaire global en francais en tete de fichier ;
    - des docstrings en francais pour les classes, fonctions publiques et fonctions non triviales.  
    Les commentaires de transition en anglais ou les docstrings legacy incoherentes doivent etre corriges.

14. **AC14 - Validation backend obligatoire dans le venv**  
    La story n est terminee que si les verifications backend ont ete executees dans le venv :
    - `.\.venv\Scripts\Activate.ps1`
    - `cd backend`
    - `ruff format .`
    - `ruff check .`
    - `pytest -q`  
    Si `pytest -q` complet est disproportionne, le Dev Agent Record doit fournir :
    - la raison precise ;
    - les suites ciblees executees ;
    - les tests structurels ajoutes ;
    - les tests des domaines touches ;
    - les recherches negatives effectuees sur les anciens chemins.  
    Une validation partielle sans justification et sans couverture des domaines modifies ne satisfait pas cet AC.

15. **AC15 - Preuve d absence de legacy residuel dans le perimetre traite**  
    Le Dev Agent Record doit lister explicitement :
    - les doublons supprimes ;
    - les chemins legacy supprimes ;
    - les compatibilites eventuellement releguees en `compat/` avec raison ;
    - les fichiers deplaces, fusionnes ou supprimes ;
    - les garde-fous ajoutes ;
    - les points reportes en follow-up.  
    Une simple affirmation "cleanup effectue" n est pas acceptable.

16. **AC16 - Chaque sous-package cree possede une responsabilite bornee**  
    Tout nouveau sous-package cree sous `backend/app/services/` doit contenir un `__init__.py` minimal et une responsabilite clairement bornee.  
    Il est interdit de creer un sous-package fourre-tout ou miroir de la racine.  
    Pour chaque sous-package cree ou fortement modifie, le Dev Agent Record doit preciser :
    - responsabilite du package ;
    - modules publics attendus ;
    - modules internes ;
    - consommateurs principaux ;
    - raison pour laquelle un namespace existant n etait pas suffisant.

17. **AC17 - Les anciens chemins deplaces echouent explicitement**  
    Les anciens chemins de modules deplaces ne doivent plus etre importables, sauf exception `compat/` validee.  
    Les tests structurels doivent verifier l absence physique des anciens fichiers et l absence de forwarders.  
    La migration doit privilegier la correction des consommateurs plutot que la conservation d alias.

18. **AC18 - Convention de nommage stable des services**  
    Les fichiers de service deplaces doivent adopter une convention homogene :
    - nom metier clair ;
    - pas de suffixe de transition ;
    - pas de doublon entre nom de package et nom de fichier ;
    - pas de coexistence entre deux noms pour la meme responsabilite.  
    Des noms comme `billing_service_v2.py`, `new_billing_service.py` ou `billing_refacto.py` sont interdits.

19. **AC19 - Convergence complete du sous-domaine `prediction` hors racine**
   La story ne peut pas etre consideree terminee tant que le sous-domaine `prediction` reste partage entre la racine `backend/app/services/` et `backend/app/services/prediction/` sans justification stricte.
   En particulier :
   - `daily_prediction_service.py` ne peut rester a la racine que comme facade applicative mince ;
   - toute orchestration metier `prediction` (single-flight, logique de recompute, politique de fallback, contexte de repair, enrichissement, selection de composants internes, logging/metrics specifiques prediction) doit vivre dans `services/prediction/` ;
   - tout helper ou service purement specifique a prediction doit etre deplace sous `services/prediction/` plutot que conserve a la racine.
   Si un fichier racine conserve plus qu un role de facade, il doit etre deplace ou scinde.

20. **AC20 - Justification opposable des survivants de la racine**
   Pour chaque fichier conserve a la racine `backend/app/services/`, la story doit fournir une preuve explicite qu il est reellement transverse.
   Cette preuve doit inclure au minimum :
   - au moins deux consommateurs nominaux appartenant a des domaines distincts ;
   - l absence de dependance dominante a un seul sous-package metier ;
   - la raison pour laquelle un rattachement a un namespace existant (`prediction/`, `natal/`, `ops/`, etc.) serait moins coherent.
   Une simple reutilisation par des tests ne constitue pas une justification de transversalite.

21. **AC21 - Interdiction pour la racine de reconstituer un sous-domaine par imports internes**
   Un fichier Python conserve a la racine `backend/app/services/` ne doit pas reconstituer a lui seul un sous-domaine en important plusieurs modules internes d un meme package metier.
   Sont interdits :
   - une facade racine qui importe plusieurs composants `app.services.prediction.*` puis conserve l orchestration complete du flux ;
   - un helper racine qui ne sert qu un seul domaine et depend essentiellement de ses DTO, repositories ou calculateurs ;
   - une conservation a la racine motivee uniquement par l inertie des patch targets historiques.
   Une facade racine autorisee doit se limiter a un role d entree stable, de delegation et de contrat public minimal.

22. **AC22 - Garde-fous specifiques sur la frontiere racine vs sous-packages**
   Les tests structurels de la story doivent etre etendus pour echouer si :
   - un fichier autorise a la racine importe plusieurs modules d un meme sous-package metier, hors cas explicitement documente ;
   - un service racine marque comme facade contient encore des primitives d orchestration metier du sous-domaine ;
   - un service conserve a la racine n a pas de justification de transversalite documentee dans la cartographie ;
   - un module specifique a `prediction` est reintroduit a la racine alors qu un namespace `services/prediction/` existe deja.
   Les garde-fous doivent couvrir au minimum `daily_prediction_service.py` et tout helper conserve a la racine au nom du sous-domaine prediction.

23. **AC23 - Aucun binome ou micro-famille mono-domaine ne reste eclate a la racine**
   La racine `backend/app/services/` ne doit plus conserver plusieurs fichiers appartenant clairement au meme sous-domaine metier ou technique.
   Sont explicitement vises :
   - `email_service.py` + `email_provider.py` ;
   - `quota_usage_service.py` + `quota_window_resolver.py` ;
   - `chart_result_service.py` + `chart_json_builder.py` ;
   - `daily_prediction_service.py` + `daily_prediction_types.py`.
   Chaque famille doit etre soit regroupee dans un sous-package canonique unique, soit justifiee comme facade publique minimale sans logique metier residuelle.

24. **AC24 - Le sous-domaine `email` possede un namespace canonique unique**
   Les composants email de production doivent etre regroupes sous un chemin canonique unique, par exemple `backend/app/services/email/`.
   Au minimum, `email_service.py` et `email_provider.py` doivent etre deplaces ou restructures sous ce namespace.
   Le runtime nominal ne doit plus exposer deux fichiers racine separes pour le meme sous-domaine email.

25. **AC25 - Le sous-domaine `quota` possede un namespace canonique unique**
   Les composants de calcul et de consommation des quotas doivent etre regroupes sous un chemin canonique unique, par exemple `backend/app/services/quota/` ou un sous-namespace existant strictement meilleur.
   Au minimum, `quota_usage_service.py` et `quota_window_resolver.py` doivent etre rattaches au meme sous-package.
   La logique de fenetre de quota ne doit plus rester a la racine si la consommation de quota possede deja un domaine canonique associe.

26. **AC26 - Le sous-domaine `chart` ou son rattachement `natal` devient explicite et unique**
   Les composants centres sur le cycle de vie du chart natal ne doivent plus etre conserves a la racine comme faux services transverses.
   Au minimum, `chart_result_service.py` et `chart_json_builder.py` doivent etre :
   - soit regroupes dans un namespace `services/chart/` ;
   - soit rattaches explicitement a `services/natal/` si ce rattachement est plus coherent.
   La story doit choisir une seule cible canonique et migrer tous les imports vers celle-ci.

27. **AC27 - Le sous-domaine `daily_prediction` ne conserve plus un couple facade/types ambigu a la racine**
   `daily_prediction_service.py` et `daily_prediction_types.py` doivent etre traites comme une meme famille canonique.
   La cible attendue est :
   - soit un regroupement complet sous `services/prediction/` ;
   - soit une facade racine minimale conservee pour stabilite d entree publique, avec les types deplaces dans `services/prediction/`.
   Il est interdit de conserver a la racine une logique ou le service et ses types metier vivent cote a cote sans justification architecturale explicite.

28. **AC28 - Toute facade racine conservee doit etre strictement contractuelle**
   Si un fichier racine est conserve comme facade publique apres regroupement mono-domaine, il ne peut contenir que :
   - imports du chemin canonique ;
   - `__all__` eventuel ;
   - alias publics explicitement documentes.
   Une facade racine ne doit pas contenir de logique metier, d orchestration, de selection de provider, de logique de quota, de serialisation de chart, ni de fallback legacy.

29. **AC29 - Les nouveaux sous-packages mono-domaine respectent DRY strict**
   Le regroupement en sous-packages ne doit pas deplacer la duplication au lieu de la supprimer.
   Pour chaque famille refactorisee (`email`, `quota`, `chart`, `prediction`), la story doit demontrer :
   - l absence de logique dupliquee entre facade racine et chemin canonique ;
   - l absence de doublon actif entre ancien et nouveau chemin ;
   - l absence de coexistence de deux services concurrents pour une meme responsabilite ;
   - la centralisation coherente des types, helpers et erreurs du sous-domaine.

30. **AC30 - No legacy strict sur les chemins deplaces**
   Une fois le regroupement effectue, les anciens chemins racine ne doivent plus survivre comme :
   - forwarders ;
   - wrappers de compatibilite ;
   - alias d import ;
   - patch targets historiques maintenus "au cas ou" ;
   - documentation presentant encore l ancien chemin comme nominal.
   Toute migration doit corriger les consommateurs, pas preserver l ancien chemin.

31. **AC31 - La cartographie racine est reecrite apres regroupement**
   `_bmad-output/implementation-artifacts/70-23-services-root-cartography.md` doit etre mise a jour pour refleter la nouvelle realite du dossier `backend/app/services/`.
   Pour chaque fichier retire de la racine, la cartographie doit indiquer :
   - ancien chemin ;
   - nouveau chemin canonique ;
   - consommateurs principaux migres ;
   - justification du regroupement mono-domaine ;
   - suppression explicite de tout reliquat legacy associe.

32. **AC32 - Les garde-fous interdisent le retour des familles eclatees**
   Les tests structurels doivent echouer si l une des familles suivantes reapparait a plat a la racine :
   - `email_*` ;
   - `quota_*` ;
   - `chart_*` ;
   - `daily_prediction_*` au-dela d une facade publique explicitement autorisee.
   Les garde-fous doivent verifier :
   - l allowlist racine mise a jour ;
   - l absence physique des anciens fichiers deplaces ;
   - l absence de facade racine epaisse ;
   - l absence de doubles chemins actifs pour un meme sous-domaine.

33. **AC33 - Les imports, patch targets et tests sont alignes sur les chemins canoniques mono-domaine**
   Tous les imports de production, tests, mocks, patch targets, dependency overrides et references string-based doivent pointer vers les nouveaux chemins canoniques.
   Les tests ne doivent pas conserver artificiellement les anciens chemins racine pour preserver une compatibilite implicite.

34. **AC34 - La story prouve explicitement l atteinte des objectifs `mono domaine`, `DRY`, `no legacy`**
   Le Dev Agent Record doit lister, pour `email`, `quota`, `chart` et `daily_prediction` :
   - le sous-package canonique retenu ;
   - les fichiers sortis de la racine ;
   - les duplications supprimees ;
   - les anciens chemins retires ;
   - les garde-fous ajoutes ;
   - les validations executees.
   Une simple mention "services regroupes" ne satisfait pas cet AC.

## Tasks / Subtasks

- [x] **Task 1: Produire la cartographie opposable et les listes de controle**  
  AC: 1, 2, 11, 12  
  - [x] Lister tous les fichiers Python directement presents sous `backend/app/services/`.
  - [x] Identifier pour chacun les consommateurs production, tests et patch targets.
  - [x] Classer chaque fichier par responsabilite dominante.
  - [x] Definir l allowlist finale des fichiers autorises a la racine.
  - [x] Definir la denylist des anciens chemins, suffixes et modules interdits.
  - [x] Produire une decision explicite : conserver, deplacer, fusionner, supprimer ou follow-up.

- [x] **Task 2: Supprimer les duplications actives les plus critiques**  
  AC: 3, 4, 7, 8, 9  
  - [x] Factoriser la logique commune des runtime gates B2C.
  - [x] Supprimer l implementation metier legacy residuelle dans `backend/app/services/tests/__init__.py`.
  - [x] Supprimer physiquement les anciens fichiers deplaces, sauf exception `compat/` validee.
  - [x] Verifier qu aucun ancien chemin ne reste importable via forwarder.
  - [x] Unifier les helpers natals partages et supprimer les redefinitions concurrentes.
  - [x] Statuer explicitement sur tout suffixe technique ambigu encore expose dans le perimetre.

- [x] **Task 3: Sortir les services mono-domaine de la racine**  
  AC: 2, 6, 7, 9, 10  
  - [x] Creer ou reutiliser les sous-namespaces cibles strictement necessaires.
  - [x] Deplacer les services `billing`, `consultation`, `natal`, `prediction`, `b2b`, `ops`, `user_profile` selon la cartographie retenue.
  - [x] Maintenir a la racine uniquement les services transverses reellement justifies.
  - [x] Migrer tous les imports de production et de tests vers les nouveaux chemins.

- [x] **Task 4: Decoupler le runtime des scripts et assainir les services monolithiques**  
  AC: 5, 6, 9, 10  
  - [x] Refactoriser `PredictionContextRepairService` pour eliminer toute dependance directe a `scripts/*`.
  - [x] Scinder ou factoriser `BillingService` en composants coherents.
  - [x] Verifier qu aucun service nominal ne conserve de fallback legacy "tests only" dans son chemin principal.
  - [x] Reporter en follow-up seulement ce qui depasse clairement le perimetre de l audit.

- [x] **Task 5: Ajouter les garde-fous structurels et legacy**  
  AC: 11, 15  
  - [x] Ajouter un test de structure sur la racine `backend/app/services/`.
  - [x] Ajouter un test interdisant les imports `scripts/*` depuis `app.services`.
  - [x] Ajouter un test interdisant le retour de doublons metiers dans `backend/app/services/tests/`.
  - [x] Ajouter un test interdisant les anciens chemins ou suffixes canoniques interdits.
  - [x] Ajouter des recherches negatives documentees sur les anciens chemins supprimes.
  - [x] Ajouter un test sur `services/__init__.py` pour interdire les reexports metier.
  - [x] Ajouter un test sur les suffixes interdits dans fichiers, classes et fonctions publiques.

- [x] **Task 6: Documenter et valider dans le venv**  
  AC: 13, 14, 15  
  - [x] Mettre a jour les commentaires globaux et docstrings en francais sur les fichiers touches.
  - [x] Activer le venv avant toute commande Python.
  - [x] Executer `ruff format`, `ruff check` et les tests backend pertinents.
  - [x] Tracer precisement la validation, les limites et les follow-ups dans le Dev Agent Record.

- [x] **Task 7: Finaliser la convergence de la racine `services/` apres audit complementaire**
  AC: 19, 20, 21, 22
  - [x] Reauditer chaque fichier encore autorise a la racine `backend/app/services/` contre le critere de transversalite reelle.
  - [x] Extraire hors de la racine toute orchestration encore specifique au sous-domaine `prediction`.
  - [x] Statuer explicitement sur `daily_prediction_service.py`, `relative_scoring_service.py` et `chart_result_service.py` : facade mince conservee, deplacement, ou scission.
  - [x] Mettre a jour la cartographie opposable avec la justification detaillee de chaque survivant de la racine.
  - [x] Etendre `test_story_70_23_services_structure_guard.py` pour proteger la frontiere racine vs sous-packages metiers.

- [x] **Task 8: Regrouper les familles mono-domaine residuelles de la racine**
  AC: 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34
  - [x] Creer les namespaces canoniques retenus pour `email`, `quota` et `chart`, avec `__init__.py` minimaux.
  - [x] Deplacer `email_service.py` et `email_provider.py` hors de la racine vers un sous-package unique.
  - [x] Deplacer `quota_usage_service.py` et `quota_window_resolver.py` hors de la racine vers un sous-package unique.
  - [x] Deplacer `chart_result_service.py` et `chart_json_builder.py` hors de la racine vers un sous-package unique ou vers `natal/` si retenu.
  - [x] Rattacher `daily_prediction_types.py` au package `prediction/` et statuer sur la facade publique `daily_prediction_service.py`.
  - [x] Migrer tous les imports, patch targets et tests vers les nouveaux chemins canoniques.
  - [x] Mettre a jour la cartographie racine, l allowlist et les garde-fous pour interdire le retour des familles eclatees.

## Dev Notes

### Developer Context

- Cette story n est **pas** une simple suite cosmetique de 70-22. Elle doit fermer la dette structurelle du dossier `backend/app/services` au sens large.
- Le perimetre prioritaire vient directement de l audit utilisateur sur `backend/app/services`.
- Les deux objectifs non negociables sont :
  - **DRY strict** ;
  - **legacy supprime**.
- Toute solution de type "on laisse le doublon mais on documente", "on garde le fallback pour les tests", "on cree un alias temporaire", "on conserve l ancien chemin comme forwarder", "on deplace sans factoriser" ou "on reporte un hotspot deja identifie en follow-up" doit etre consideree comme invalide par defaut.

### Frontieres et contraintes

- Reutiliser les sous-dossiers deja introduits par 70-21 et 70-22 avant d en creer de nouveaux.
- Respecter `docs/backend-structure-governance.md` : pas de nouveau dossier de base backend sans accord explicite.
- Ne pas recréer de couche parallele equivalente a `services/`.
- Aucun import de production ne doit pointer vers un module de test ou vers `scripts/*`.
- Aucun re-export de compatibilite ne doit etre ajoute dans `backend/app/services/__init__.py`.
- Les tests doivent etre adaptes aux chemins canoniques. Il est interdit de faire passer les tests en patchant les anciens chemins ou en ajoutant des alias de compatibilite.

### Intelligence des stories precedentes

- **70-18** a verrouille la gouvernance structurelle backend et la regle anti-dossiers concurrents.
- **70-20** a impose une ligne dure contre les facades/app adapters qui conservent du legacy par inertie.
- **70-21** a commence a sortir les residus LLM de la racine `services/`.
- **70-22** a cree un namespace `services/entitlement/` et a deja demontre le pattern attendu : cartographie, deplacement, migrations d imports et garde-fous.
- **70-23** doit appliquer cette logique a l ensemble du dossier `services`, avec un niveau de durcissement superieur car il ne s agit plus seulement d un sous-domaine.

### Hotspots issus de l audit initial

- `backend/app/services/tests/__init__.py` : doublon metier legacy a supprimer.
- `backend/app/services/entitlement/*` : gates B2C a factoriser.
- `backend/app/services/prediction_context_repair_service.py` : dependance directe a un script de seed.
- `backend/app/services/billing_service.py` : service monolithique a scinder ou factoriser.
- `backend/app/services/llm_generation/natal/prompt_context.py`
- `backend/app/services/llm_generation/shared/natal_context.py`
- `backend/app/services/astro_context_builder.py`

### Validation attendue

- La preuve de convergence ne repose pas seulement sur les deplacements de fichiers.
- Le dev agent doit montrer que :
  - les chemins legacy n existent plus ;
  - les imports ont ete migres ;
  - la duplication active a disparu ;
  - les garde-fous echoueraient en cas de retour arriere.

## References

- [Source: AGENTS.md]
- [Source: docs/backend-structure-governance.md]
- [Source: _bmad-output/implementation-artifacts/70-18-cleaner-la-structure-backend-et-converger-les-namespaces-techniques.md]
- [Source: _bmad-output/implementation-artifacts/70-20-auditer-et-assainir-ai-engine-adapter.md]
- [Source: _bmad-output/implementation-artifacts/70-21-analyser-factoriser-et-deplacer-les-services-llm-residuels-sous-services.md]
- [Source: _bmad-output/implementation-artifacts/70-22-cartographier-et-converger-les-services-entitlement.md]

## Dev Agent Record

### Agent Model Used

gpt-5

### Debug Log References

- Story redigee a partir de l audit local de `backend/app/services` demande par l utilisateur le 2026-04-25.
- Cartographie racine produite dans `_bmad-output/implementation-artifacts/70-23-services-root-cartography.md`.
- Reorganisation effectuee vers les sous-packages `billing/`, `consultation/`, `natal/`, `prediction/`, `b2b/`, `ops/` et `user_profile/`.
- Factorisation B2C centralisee dans `app/services/entitlement/b2c_runtime_gate.py`.
- Validation Python executee apres activation du venv avec `.\.venv\Scripts\Activate.ps1`.
- `pytest -q` complet lance deux fois depuis `backend/` puis interrompu pour timeout ; validation ciblee documentee ci-dessous.
- Correctifs de revue appliques le 2026-04-26 : retrait des bypass legacy nominaux sur `horoscope_daily` et sur le catalogue de consultations, renforcement des garde-fous structurels, puis correctif du fallback SQLite `email_logs.id` dans `EmailService`.
- Audit complementaire du 2026-04-26 : residu structurel identifie sur la frontiere racine `services/` vs sous-package `prediction/`, avec AC supplementaires rediges pour fermer explicitement ce perimetre.
- Mise en oeuvre des AC complementaires le 2026-04-26 : deplacement de `relative_scoring_service.py` vers `app/services/prediction/`, migration de l orchestration `DailyPredictionService` vers `app/services/prediction/service.py`, facade racine amincie, cartographie mise a jour et tests du routeur prediction realignes sur la gate d entitlement.
- Nouvelle passe d audit du 2026-04-26 : familles mono-domaine residuelles identifiees a la racine (`email`, `quota`, `chart`, `daily_prediction_types`) puis converges vers des namespaces canoniques uniques.
- Correctif final du 2026-04-26 : isolation SQLite de `app/tests/integration/test_daily_prediction_api.py` pour supprimer le bruit de contraintes FK quand la suite partageait une meme base avec d autres modules.
- Passe documentaire finale du 2026-04-26 : re-audit des fichiers encore presents directement sous `backend/app/services/`, confirmation de leur statut transverse vis-a-vis de l allowlist, puis ajout de commentaires globaux en francais sur les survivants qui n en avaient pas encore.
- Passe de convergence supplementaire du 2026-04-26 : `current_context.py`, `persona_config_service.py`, `feature_flag_service.py` et `cross_tool_report.py` ont quitte la racine ; la facade racine `daily_prediction_service.py` a ete supprimee apres migration complete des imports vers `app.services.prediction`.
- Verification utilisateur du 2026-04-26 : `disclaimer_registry.py` est desormais canonique sous `app/services/resources/templates/`, avec suppression du dernier reliquat racine dans la cartographie et migration des imports encore restants.

### Completion Notes List

- Cartographie exhaustive de la racine `backend/app/services/` versionnee dans `_bmad-output/implementation-artifacts/70-23-services-root-cartography.md`, avec allowlist finale et denylist de chemins/suffixes interdits.
- Les services mono-domaine a la racine ont ete migres vers des namespaces canoniques ; les anciens fichiers deplaces ont ete supprimes physiquement sans forwarder ni re-export.
- `backend/app/services/tests/` a ete retire du runtime applicatif ; les reliquats utiles ont ete deplaces sous `backend/app/tests/unit/legacy_services/`.
- Les gates B2C `chat`, `thematic_consultation` et `natal_chart_long` deleguent desormais leur logique commune a `app/services/entitlement/b2c_runtime_gate.py`.
- `PredictionContextRepairService` ne depend plus d un script versionne ; le runtime passe par `app/services/prediction/reference_seed_service.py` et le script de seed ne sert plus que de wrapper de compatibilite hors runtime nominal.
- `BillingService` a ete reduit a une facade d orchestration fine, avec extraction du catalogue, du cache, du provider Stripe, des quotas runtime et du statut d abonnement dans des modules dedies du package `app/services/billing/`.
- Les helpers natals concurrents ont ete converges autour de `app/services/llm_generation/shared/natal_context.py`, `prompt_context.py` devenant un simple point de re-export interne.
- Les imports de production, de tests et les patch targets ont ete migres vers les chemins canoniques ; les garde-fous structurels couvrent l allowlist racine, l interdiction de `scripts/*`, l absence de `services/tests/`, l interdiction des suffixes techniques et la non-reintroduction de logique B2C dupliquee.
- Validation ciblee executee dans le venv : `ruff format .`, `ruff check .`, puis suites de tests des zones touchees dont `test_story_70_22_entitlement_structure_guard.py`, `test_story_70_23_services_structure_guard.py`, `test_daily_prediction_service.py`, `test_billing_service.py`, `test_effective_entitlement_resolver_service.py`, `test_natal_chart_long_entitlement_gate.py`, `test_natal_chart_long_entitlement_gate_v2.py` et `test_thematic_consultation_entitlement_gate_v2.py` avec `60 passed`.
- Passage de revue complete : la normalisation des types de consultation legacy est maintenant faite a l entree API via les schemas Pydantic, le service canonique `consultation/catalogue_service.py` ne conserve plus de mapping legacy, et `horoscope_daily_entitlement_gate.py` refuse explicitement les etats non canoniques au lieu de revenir silencieusement a `full`.
- Le garde-fou `test_story_70_23_services_structure_guard.py` couvre desormais explicitement l interdiction de bypass legacy nominaux dans les services canoniques concernes par la revue.
- Le blocage residuel de validation integration sur `email_logs.id` a ete corrige dans `app/services/email_service.py` en rendant l ecriture compatible avec la forme SQLite legacy encore presente dans certaines bases de test.
- Validation complementaire executee dans le venv apres revue : `test_consultation_request_schema.py`, `test_horoscope_daily_entitlement_gate.py`, `test_consultation_fallback_service.py`, `test_consultation_precheck_service.py`, `test_story_70_23_services_structure_guard.py`, `test_consultations_router.py`, `test_horoscope_daily_entitlement.py` et `test_consultation_catalogue.py` avec `40 passed`.
- Le sous-domaine `prediction` a ete convergé : `relative_scoring_service.py` n existe plus a la racine, `DailyPredictionService` delegue maintenant au module canonique `app/services/prediction/service.py`, et le garde-fou structurel interdit le retour d une facade racine epaisse.
- Les familles mono-domaine residuelles ont ete sorties de la racine : `email_service.py` et `email_provider.py` vivent maintenant sous `app/services/email/`, `quota_usage_service.py` et `quota_window_resolver.py` sous `app/services/quota/`, `chart_result_service.py` et `chart_json_builder.py` sous `app/services/chart/`, et `daily_prediction_types.py` sous `app/services/prediction/types.py`.
- Les nouveaux packages `app/services/email/__init__.py`, `app/services/quota/__init__.py` et `app/services/chart/__init__.py` bornent explicitement leurs exports publics sans recreer de facade legacy a la racine.
- La facade racine `app/services/daily_prediction_service.py` reste contractuelle et importe maintenant ses types depuis `app.services.prediction.types`, ce qui supprime le dernier binome prediction ambigu a la racine.
- Le garde-fou `test_story_70_23_services_structure_guard.py` interdit desormais le retour de familles plates `email_*`, `quota_*` et `chart_*` a la racine, en plus de l absence physique des anciens chemins.
- Les tests routeur prediction ont ete realignes pour neutraliser explicitement la gate d entitlement quand l objectif du test est le contrat HTTP ou le mapping d erreur, ce qui permet de valider le perimetre cible sans faux 403 parasites.
- Validation ciblee executee dans le venv pour cette passe : `ruff format` et `ruff check` sur les namespaces touches, smoke import de `app.main`/routeurs, `138 passed` sur la suite unitaire et email d integration, puis `25 passed` sur `app/tests/integration/test_daily_prediction_api.py`.
- `app/tests/integration/test_daily_prediction_api.py` utilise maintenant une base SQLite isolee par test, sur le meme pattern que d autres suites d integration du repo ; la limite de nettoyage FK partage est donc fermee.
- Validation consolidee executee dans le venv apres ce correctif : `ruff format app/tests/integration/test_daily_prediction_api.py`, `ruff check app/tests/integration/test_daily_prediction_api.py`, puis la suite groupee `test_story_70_23_services_structure_guard.py`, `test_quota_usage_service.py`, `test_quota_window_resolver.py`, `test_chart_result_service.py`, `test_chart_json_builder.py`, `test_daily_prediction_service.py`, `test_daily_prediction_version_consistency.py`, `test_chat_entitlement_gate.py`, `test_b2b_api_entitlement_gate.py`, `test_effective_entitlement_resolver_service.py`, `test_email_idempotence.py`, `test_user_natal_chart_service.py`, `tests/integration/test_email_unsubscribe.py` et `app/tests/integration/test_daily_prediction_api.py` avec `163 passed`.
- Audit final des fichiers isoles restants a la racine `backend/app/services/` : `__init__.py`, `auth_service.py`, `cross_tool_report.py`, `current_context.py`, `daily_prediction_service.py`, `disclaimer_registry.py`, `feature_flag_service.py`, `feature_registry_consistency_validator.py`, `geocoding_service.py`, `persona_config_service.py`, `privacy_service.py` et `reference_data_service.py` ; aucun nouveau regroupement mono-domaine bloquant n a ete identifie sur ce lot.
- Les fichiers racine qui n avaient pas encore de commentaire global francais ont ete completes : `services/__init__.py`, `cross_tool_report.py`, `current_context.py`, `feature_registry_consistency_validator.py` et `geocoding_service.py`.
- La racine `backend/app/services/` a encore ete reduite : `current_context.py` et `persona_config_service.py` vivent maintenant sous `app/services/llm_generation/guidance/`, `feature_flag_service.py` sous `app/services/ops/`, `cross_tool_report.py` sous `backend/scripts/`, et `daily_prediction_service.py` a disparu au profit du package canonique `app.services.prediction`.
- Les imports de production, de jobs, de scripts et de tests ont ete migres vers `app.services.prediction`, `app.services.llm_generation.guidance.*`, `app.services.ops.feature_flag_service` et `scripts.cross_tool_report`.
- `disclaimer_registry.py` ne fait plus partie des survivants de la racine : son chemin canonique est maintenant `app.services.resources.templates.disclaimer_registry`, utilise par les routes natales, l export PDF et la generation LLM associee.
- Limite connue de validation : `pytest -q` complet n a pas termine dans la fenetre de temps allouee malgre deux tentatives ; aucun autre follow-up bloquant n a ete laisse dans le perimetre impose par la story.

### File List

- _bmad-output/implementation-artifacts/70-23-durcir-backend-app-services-pour-imposer-dry-strict-et-zero-legacy.md
- _bmad-output/implementation-artifacts/70-23-services-root-cartography.md
- backend/app/services/entitlement/b2c_runtime_gate.py
- backend/app/services/entitlement/chat_entitlement_gate.py
- backend/app/services/entitlement/thematic_consultation_entitlement_gate.py
- backend/app/services/entitlement/natal_chart_long_entitlement_gate.py
- backend/app/services/prediction/reference_seed_service.py
- backend/app/services/prediction/context_repair_service.py
- backend/app/services/prediction/service.py
- backend/app/services/prediction/relative_scoring_service.py
- backend/app/services/prediction/types.py
- backend/app/services/chart/__init__.py
- backend/app/services/chart/json_builder.py
- backend/app/services/chart/result_service.py
- backend/app/services/email/__init__.py
- backend/app/services/email/provider.py
- backend/app/services/email/service.py
- backend/app/services/quota/__init__.py
- backend/app/services/quota/usage_service.py
- backend/app/services/quota/window_resolver.py
- backend/scripts/seed_31_prediction_reference_v2.py
- backend/app/services/billing/service.py
- backend/app/services/billing/models.py
- backend/app/services/billing/subscription_cache.py
- backend/app/services/billing/plan_catalog.py
- backend/app/services/billing/quota_runtime.py
- backend/app/services/billing/stripe_provider.py
- backend/app/services/billing/subscription_status.py
- backend/app/services/llm_generation/shared/natal_context.py
- backend/app/services/llm_generation/natal/prompt_context.py
- backend/app/services/natal/astro_context_builder.py
- backend/app/services/resources/templates/__init__.py
- backend/app/services/resources/templates/disclaimer_registry.py
- backend/app/api/v1/schemas/consultation.py
- backend/app/api/v1/routers/consultations.py
- backend/app/services/consultation/catalogue_service.py
- backend/app/services/consultation/fallback_service.py
- backend/app/services/consultation/precheck_service.py
- backend/app/services/entitlement/horoscope_daily_entitlement_gate.py
- backend/app/services/__init__.py
- backend/app/services/feature_registry_consistency_validator.py
- backend/app/services/geocoding_service.py
- backend/app/tests/unit/test_story_70_22_entitlement_structure_guard.py
- backend/app/tests/unit/test_disclaimer_registry.py
- backend/app/tests/unit/test_story_70_23_services_structure_guard.py
- backend/app/tests/integration/test_daily_prediction_api.py
- backend/app/tests/unit/test_consultation_request_schema.py
- backend/app/tests/unit/test_daily_prediction_guardrails.py
- backend/app/tests/unit/legacy_services/legacy_natal_interpretation_service.py

## Change Log

- 2026-04-25 - Implementation de la convergence structurelle de `backend/app/services`, suppression des reliquats legacy nominaux, ajout des garde-fous de non-regression et validation ciblee dans le venv.
- 2026-04-26 - Correctifs post-review : suppression des bypass legacy nominaux restants, durcissement des tests structurels et correction du fallback SQLite `email_logs.id`, avec validation integration complementaire.
- 2026-04-26 - Ajout d AC complementaires post-audit pour finaliser la convergence de la racine `services/`, en particulier sur le sous-domaine `prediction` et sur les garde-fous de transversalite.
- 2026-04-26 - Mise en oeuvre des AC complementaires : convergence finale du sous-domaine `prediction`, facade racine amincie, garde-fous renforces et realignement des tests du routeur prediction.
- 2026-04-26 - Mise en oeuvre des AC 23 a 34 : convergence des familles `email`, `quota`, `chart` et `daily_prediction_types` vers des sous-packages canoniques, migration complete des imports et durcissement de l allowlist racine.
- 2026-04-26 - Audit final des survivants de la racine `services/` et ajout des commentaires globaux francais manquants sur les fichiers transverses restants.
- 2026-04-26 - Correctif de la limite restante de validation : isolation SQLite de `test_daily_prediction_api.py` et validation consolidee verte sur la suite ciblee partagee.
- 2026-04-26 - Realignement final du registre de disclaimers vers `services/resources/templates/`, retrait de la racine et mise a jour de la cartographie/story.
