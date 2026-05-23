# Executive Summary - Astro Feature Coverage

The post-CS-236 astrology engine is strong for natal structure: `natal_chart_v1`, chart objects, houses, aspects, dignities, dominance, advanced planetary conditions, fixed-star conjunction payloads, chart signature and interpretation input all have runtime and test evidence.

The next product stories should not start by adding UI. The first priority is a bounded predictive-technique roadmap because transits, progressions, returns, synastry, composite, profections, symbolic directions and firdaria/time lords are not implemented in the audited backend astrology runtime. Second priority is productizing existing internal surfaces: fixed-star conjunctions and astral points need explicit public projection and capability decisions before consumers rely on them.

Decision ranking: P0 predictive runtime roadmap; P1 fixed-star public/projection decision; P1 astral-point productization; P2 non-planetary object taxonomy for parts arabes/lots, asteroids, Chiron and midpoints; P2 guard preventing implemented-status claims without runtime plus test evidence.
