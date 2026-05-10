<!-- Preuve finale de centralisation des erreurs API frontend CS-132. -->

# CS-132 - Centralisation erreurs after

## Changements

- `frontend/src/api/client.ts` expose `ApiErrorEnvelope`,
  `ApiResponseEnvelope`, `readApiErrorEnvelope` et `parseApiErrorDetails`.
- Les modules B2B, billing, enterprise credentials, help, ops monitoring,
  support, admin prompts et natal chart migrent leurs wrappers publics ou
  handlers d'erreurs vers le parser canonique sur les surfaces modifiees.
- Les wrappers publics sont conserves quand ils sont consommes par les tests ou
  la facade publique.

## Scan final

Commande:

```powershell
rg -l "ErrorEnvelope|ResponseEnvelope|parseError|toTransportError|extractAdminApiErrorMessage|throw new Error" src/api -g "*.ts"
```

Resultat global: des hits restent pour les wrappers publics et pour les modules
non modifies par ce lot. Ils sont classes dans `error-wrapper-map.md`.

Scan de garde des sous-domaines touches:

```powershell
rg -n 'type\s+ErrorEnvelope|type\s+ResponseEnvelope|let\s+payload\s*:' frontend/src/api/admin-prompts/index.ts frontend/src/api/natal-chart/index.ts
```

Resultat: zero hit. Les sous-domaines crees par CS-133 deleguent au helper
canonique.
