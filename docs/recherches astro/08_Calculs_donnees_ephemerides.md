# 08 – Données, éphémérides et calculs (comprendre + contrôler)

Objectif : savoir d’où sort un thème, repérer les erreurs, et comprendre les calculs clés.

## 1) Données indispensables
- Date de naissance (calendrier grégorien, attention aux pays/historiques rares).
- Heure de naissance locale (précise).
- Lieu (ville/pays, idéalement latitude/longitude).
- Fuseau horaire et heure d’été/hiver (DST).

## 2) Conversion heure locale → UT (UTC)
Principe :  
UT = heure locale - décalage de fuseau - correction DST.

Exemple (schéma) :
- Lieu : Paris.
- Heure locale : 14:30.
- Fuseau : UTC+1 (hiver) ou UTC+2 (été).
- Si UTC+2 (été) : UT = 14:30 - 2h = 12:30.

Point pro : un logiciel fait souvent ceci automatiquement, mais tu dois savoir le vérifier.

## 3) De UT au Jour Julien (Julian Day, JD)
Le JD est un compteur de jours continu utilisé en astronomie.

Formule classique (calendrier grégorien) :
Soit Y = année, M = mois, D = jour avec fraction (ex: 17,5).
Si M ≤ 2 alors Y := Y-1 et M := M+12.
A = floor(Y/100)
B = 2 - A + floor(A/4)
JD = floor(365.25*(Y+4716)) + floor(30.6001*(M+1)) + D + B - 1524.5

D avec fraction :
D = jour + (heureUT + minute/60 + seconde/3600)/24

Utilité :
- calcul du temps sidéral,
- positions planétaires via éphémérides numériques.

## 4) Temps sidéral (concept + formule)
Le temps sidéral = “heure des étoiles”, basé sur la rotation de la Terre par rapport aux étoiles.

Repère :
- GMST : temps sidéral à Greenwich
- LST : temps sidéral local = GMST + longitude (en heures)

Conversion longitude :
- 360° = 24h → 15° = 1h
- Longitude Est = on ajoute ; Ouest = on retranche.

Formule pratique (approx) pour GMST (en degrés) :
T = (JD - 2451545.0)/36525
GMST = 280.46061837 + 360.98564736629*(JD - 2451545.0) + 0.000387933*T^2 - (T^3)/38710000
Puis réduire à [0, 360).

LST (en degrés) = GMST + longitude_deg (Est +)
Puis réduire à [0, 360).

## 5) Calcul conceptuel de l’Ascendant (ASC)
L’Ascendant est l’intersection de l’écliptique avec l’horizon Est, dépendant de :
- la latitude du lieu (φ),
- le temps sidéral local (θ = LST),
- l’obliquité de l’écliptique (ε ~ 23.44°).

Formule usuelle (longitude écliptique de l’Ascendant, λ_asc) :
λ_asc = atan2( sin(θ)*cos(ε) - tan(φ)*sin(ε), cos(θ) )
Puis normaliser λ_asc dans [0, 360).

Remarques pro :
- La trigonométrie sphérique et les conventions d’angle rendent l’implémentation délicate.
- En pratique, on utilise des bibliothèques d’éphémérides (ex. Swiss Ephemeris) pour éviter les erreurs.

## 6) MC (Milieu du Ciel) – idée
Le MC est l’intersection de l’écliptique avec le méridien local.
Il dépend surtout du temps sidéral local et de l’obliquité.

## 7) Systèmes de maisons : ce qui est calculable “à la main”
- Whole Sign : facile et robuste.
  - La maison I commence à 0° du signe de l’ASC.
  - Chaque signe = une maison entière.
- Equal House : facile.
  - Cuspide de I = degré exact de l’ASC
  - Cuspide n = ASC + (n-1)*30°
- Placidus : complexe (semi-arcs diurnes), peu réaliste “à la main” en pratique.
  - Compétence attendue : comprendre que cela dépend de latitude/temps, et savoir contrôler dans un logiciel.

## 8) Aspects : calcul d’écart angulaire
Chaque planète/point a une longitude L en degrés [0,360).
Écart minimal :
d = abs(L1 - L2)
si d > 180, d = 360 - d

Un aspect A est présent si |d - angle(A)| ≤ orbe.

Exemples :
- Conjonction 0°, carré 90°, trigone 120°, opposition 180°.

## 9) Éphémérides : lecture et contrôle
Une éphéméride donne les longitudes planétaires jour par jour.
Tu dois savoir :
- qu’une planète rétrograde = longitude décroît (vitesse apparente négative),
- qu’un changement de signe = franchissement d’un multiple de 30°,
- que la Lune bouge vite (≈ 13°/jour).

## 10) Check minimal “anti-erreur”
- UT correct ?
- lieu correct (pas confondu avec homonyme) ?
- tropical / sidéral correct ?
- maisons correctes ?
- nœud vrai/moyen choisi consciemment ?
- contrôle Whole Sign (cohérence globale) ?
