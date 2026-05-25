# Reproductibilite replay_snapshot_v1

Les entrees deterministes de replay sont limitees au snapshot chiffre approuve, a son `input_hash`, a `version_identity`, a `provenance`, au `request_id` de correlation et a l'identifiant stable du snapshot.

L'execution provider reste non deterministe: latence, routage provider, disponibilite amont et sortie modele peuvent varier. Le replay ne promet donc pas une reponse identique; il produit seulement une tentative controlee et un resume borne.

Surfaces interdites dans les audits et reponses admin: prompt brut, donnees de naissance brutes, secrets, payload provider brut, bytes chiffres et donnees utilisateur identifiantes.
