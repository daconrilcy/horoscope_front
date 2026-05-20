// Panneau expert affichant uniquement les faits natals avances fournis par l'API publique.
import type { ReactNode } from "react"

import type {
  AdvancedCondition,
  DignitiesPayload,
  DignityBreakdownItem,
  DignityPlanetPayload,
  DominantPlanet,
  DominantPlanetsResult,
  InterpretationAdapterResult,
  LatestNatalChart,
  PlanetConditionProfile,
  PlanetConditionSignal,
  PlanetSectCondition,
  TraditionalConditionsPayload,
} from "../../api/natalChart"
import { classNames } from "../../utils/classNames"
import "./NatalExpertPanel.css"

type SectGroupKey = "in" | "out" | "neutral"

type SectGroup = {
  key: SectGroupKey
  title: string
  items: PlanetSectCondition[]
}

type NatalExpertPanelProps = {
  chart?: LatestNatalChart | null
  isLoading?: boolean
  errorMessage?: string | null
}

const EMPTY_MARK = "-"

function formatValue(value: string | number | boolean | null | undefined): string {
  if (value === null || value === undefined || value === "") return EMPTY_MARK
  if (typeof value === "boolean") return value ? "true" : "false"
  if (typeof value === "number") return Number.isInteger(value) ? String(value) : value.toFixed(2)
  return value
}

function hasItems<T>(items: T[] | undefined): items is T[] {
  return Array.isArray(items) && items.length > 0
}

function groupSectConditions(planets: Record<string, DignityPlanetPayload> | undefined): SectGroup[] {
  const groups: Record<SectGroupKey, PlanetSectCondition[]> = {
    in: [],
    out: [],
    neutral: [],
  }

  Object.values(planets ?? {}).forEach((planet) => {
    const condition = planet.sect_condition
    if (!condition) return

    if (condition.is_in_sect) {
      groups.in.push(condition)
      return
    }

    if (condition.is_out_of_sect) {
      groups.out.push(condition)
      return
    }

    groups.neutral.push(condition)
  })

  return [
    { key: "in", title: "Dans la secte", items: groups.in },
    { key: "out", title: "Hors secte", items: groups.out },
    { key: "neutral", title: "Neutre / variable / inconnu", items: groups.neutral },
  ]
}

function entriesByPlanet<T>(items: Record<string, T> | undefined): Array<[string, T]> {
  return Object.entries(items ?? {}).sort(([current], [next]) => current.localeCompare(next))
}

function getAdvancedFacts(conditions: AdvancedCondition[] | undefined): AdvancedCondition[] {
  return [...(conditions ?? [])].sort((current, next) => {
    const currentPlanet = current.planet_code ?? ""
    const nextPlanet = next.planet_code ?? ""
    const planetOrder = currentPlanet.localeCompare(nextPlanet)
    if (planetOrder !== 0) return planetOrder
    return (current.condition_code ?? "").localeCompare(next.condition_code ?? "")
  })
}

function isExpertPayloadMissing(result: LatestNatalChart["result"] | undefined): boolean {
  if (!result) return true
  return (
    result.dignities === undefined &&
    result.planet_condition_profiles === undefined &&
    result.planet_condition_signals === undefined &&
    result.advanced_conditions === undefined &&
    result.traditional_conditions === undefined &&
    result.dominant_planets === undefined &&
    result.interpretation_adapter === undefined
  )
}

function isNoTimePayload(chart: LatestNatalChart): boolean {
  const degradedMode = chart.metadata.degraded_mode
  if (degradedMode === "no_time") return true
  if (degradedMode === "no_location_no_time") return true
  return chart.astro_profile?.missing_birth_time === true
}

function FactRow({
  label,
  value,
}: {
  label: string
  value: string | number | boolean | null | undefined
}) {
  return (
    <div className="natal-expert-fact">
      <dt>{label}</dt>
      <dd>{formatValue(value)}</dd>
    </div>
  )
}

function SectionShell({
  title,
  children,
  isEmpty,
  emptyLabel = "Bloc absent ou vide dans le payload public.",
}: {
  title: string
  children: ReactNode
  isEmpty?: boolean
  emptyLabel?: string
}) {
  return (
    <section className="natal-expert-section" aria-label={title}>
      <div className="natal-expert-section__header">
        <h3>{title}</h3>
      </div>
      {isEmpty ? <p className="natal-expert-empty">{emptyLabel}</p> : children}
    </section>
  )
}

function ChartSectBlock({ dignities }: { dignities?: DignitiesPayload }) {
  const sect = dignities?.sect
  return (
    <SectionShell title="Secte du theme" isEmpty={!sect}>
      {sect ? (
        <dl className="natal-expert-facts">
          <FactRow label="chart_sect" value={sect.chart_sect} />
          <FactRow label="sun_horizon_position" value={sect.sun_horizon_position} />
          <FactRow label="sun_above_horizon" value={sect.sun_above_horizon} />
          <FactRow label="calculation_basis" value={sect.calculation_basis} />
          <FactRow label="reference_system" value={sect.reference_system} />
        </dl>
      ) : null}
    </SectionShell>
  )
}

function PlanetSectBlock({ dignities }: { dignities?: DignitiesPayload }) {
  const groups = groupSectConditions(dignities?.planets)
  const isEmpty = groups.every((group) => group.items.length === 0)

  return (
    <SectionShell title="Condition de secte par planete" isEmpty={isEmpty}>
      <div className="natal-expert-sect-groups">
        {groups.map((group) => (
          <article key={group.key} className={classNames("natal-expert-sect-group", `is-${group.key}`)}>
            <h4>{group.title}</h4>
            {group.items.length === 0 ? (
              <p className="natal-expert-empty natal-expert-empty--compact">Aucune entree.</p>
            ) : (
              <ul className="natal-expert-list">
                {group.items.map((condition) => (
                  <li key={condition.planet_code} className="natal-expert-item">
                    <strong>{condition.planet_code}</strong>
                    <span>{condition.planet_sect_condition}</span>
                    <span>{condition.intrinsic_sect}</span>
                    <span>{condition.chart_sect}</span>
                  </li>
                ))}
              </ul>
            )}
          </article>
        ))}
      </div>
    </SectionShell>
  )
}

function BreakdownList({ title, items }: { title: string; items?: DignityBreakdownItem[] }) {
  if (!hasItems(items)) return null
  return (
    <div className="natal-expert-breakdown">
      <h5>{title}</h5>
      <ul className="natal-expert-list">
        {items.map((item, index) => (
          <li key={`${title}-${index}`} className="natal-expert-item natal-expert-item--stacked">
            <strong>{item.type ?? item.dignity_type ?? item.dignity_type_code ?? "fact"}</strong>
            <span>{formatValue(item.score_value ?? item.score)}</span>
            {item.reason ? <span>{item.reason}</span> : null}
          </li>
        ))}
      </ul>
    </div>
  )
}

function DignityScoresBlock({ dignities }: { dignities?: DignitiesPayload }) {
  const planets = entriesByPlanet(dignities?.planets)
  return (
    <SectionShell title="Scores de dignite" isEmpty={planets.length === 0}>
      <div className="natal-expert-card-grid">
        {planets.map(([planetCode, planet]) => (
          <article key={planetCode} className="natal-expert-data-card">
            <h4>{planetCode}</h4>
            <dl className="natal-expert-facts natal-expert-facts--compact">
              <FactRow label="essential_score" value={planet.essential_score} />
              <FactRow label="accidental_score" value={planet.accidental_score} />
              <FactRow label="total_score" value={planet.total_score} />
              <FactRow label="functional_strength_score" value={planet.functional_strength_score} />
              <FactRow label="expression_quality_score" value={planet.expression_quality_score} />
              <FactRow label="intensity_score" value={planet.intensity_score} />
            </dl>
            <BreakdownList title="essential_breakdown" items={planet.essential_breakdown} />
            <BreakdownList title="accidental_breakdown" items={planet.accidental_breakdown} />
          </article>
        ))}
      </div>
    </SectionShell>
  )
}

function AdvancedConditionsBlock({ conditions }: { conditions?: AdvancedCondition[] }) {
  const facts = getAdvancedFacts(conditions)
  return (
    <SectionShell title="Conditions avancees" isEmpty={facts.length === 0}>
      <ul className="natal-expert-list natal-expert-list--grid">
        {facts.map((condition, index) => (
          <li
            key={`${condition.planet_code ?? "planet"}-${condition.condition_code ?? index}`}
            className="natal-expert-item natal-expert-item--stacked"
          >
            <strong>
              {formatValue(condition.planet_code)} / {formatValue(condition.condition_code)}
            </strong>
            <span>condition_type: {formatValue(condition.condition_type)}</span>
            <span>score_effect: {formatValue(condition.score_effect)}</span>
            {condition.axis_weights ? (
              <span>axis_weights: {formatAxisWeights(condition.axis_weights)}</span>
            ) : null}
            {hasItems(condition.evidence) ? <span>evidence: {condition.evidence.join(" | ")}</span> : null}
          </li>
        ))}
      </ul>
    </SectionShell>
  )
}

function TraditionalConditionsBlock({
  conditions,
}: {
  conditions?: TraditionalConditionsPayload | null
}) {
  const planets = entriesByPlanet(conditions?.planets)
  return (
    <SectionShell title="Contrats traditionnels" isEmpty={planets.length === 0}>
      <div className="natal-expert-card-grid">
        {planets.map(([planetCode, condition]) => (
          <article key={planetCode} className="natal-expert-data-card">
            <h4>{planetCode}</h4>
            <dl className="natal-expert-facts natal-expert-facts--compact">
              <FactRow label="hayz.is_hayz" value={condition.hayz.is_hayz} />
              <FactRow label="hayz.sect_match" value={condition.hayz.sect_match} />
              <FactRow label="hayz.hemisphere_match" value={condition.hayz.hemisphere_match} />
              <FactRow label="hayz.sign_gender_match" value={condition.hayz.sign_gender_match} />
              <FactRow label="rejoicing.is_rejoicing" value={condition.rejoicing.is_rejoicing} />
              <FactRow label="rejoicing.current_house" value={condition.rejoicing.current_house} />
              <FactRow label="rejoicing.rejoicing_house" value={condition.rejoicing.rejoicing_house} />
            </dl>
          </article>
        ))}
      </div>
    </SectionShell>
  )
}

function formatAxisWeights(axisWeights: Record<string, number>): string {
  return Object.entries(axisWeights)
    .map(([axis, value]) => `${axis} ${formatValue(value)}`)
    .join(", ")
}

function ProfilesBlock({ profiles }: { profiles?: Record<string, PlanetConditionProfile> }) {
  const entries = entriesByPlanet(profiles)
  return (
    <SectionShell title="Profils conditionnels" isEmpty={entries.length === 0}>
      <div className="natal-expert-card-grid">
        {entries.map(([planetCode, profile]) => (
          <article key={planetCode} className="natal-expert-data-card">
            <h4>{profile.planet_code ?? planetCode}</h4>
            <dl className="natal-expert-facts natal-expert-facts--compact">
              <FactRow label="condition_level" value={profile.condition_level} />
              <FactRow label="ranking_score" value={profile.ranking_score} />
              <FactRow label="functional_strength" value={profile.functional_strength} />
              <FactRow label="visibility" value={profile.visibility} />
              <FactRow label="stability" value={profile.stability} />
              <FactRow label="intensity" value={profile.intensity} />
              <FactRow label="coherence" value={profile.coherence} />
              <FactRow label="support" value={profile.support} />
              <FactRow label="constraint" value={profile.constraint} />
            </dl>
          </article>
        ))}
      </div>
    </SectionShell>
  )
}

function SignalsBlock({ signals }: { signals?: Record<string, PlanetConditionSignal[]> }) {
  const entries = entriesByPlanet(signals).filter(([, planetSignals]) => planetSignals.length > 0)
  return (
    <SectionShell title="Signaux conditionnels" isEmpty={entries.length === 0}>
      <div className="natal-expert-card-grid">
        {entries.map(([planetCode, planetSignals]) => (
          <article key={planetCode} className="natal-expert-data-card">
            <h4>{planetCode}</h4>
            <ul className="natal-expert-list">
              {planetSignals.map((signal, index) => (
                <li key={`${signal.code ?? "signal"}-${index}`} className="natal-expert-item natal-expert-item--stacked">
                  <strong>{signal.code ?? "signal"}</strong>
                  <span>{signal.label ?? EMPTY_MARK}</span>
                  <span>
                    axis: {formatValue(signal.axis)} / level: {formatValue(signal.level)}
                  </span>
                  <span>
                    axis_value: {formatValue(signal.axis_value)} / priority_weight:{" "}
                    {formatValue(signal.priority_weight)}
                  </span>
                  <span>interpretation_use: {formatValue(signal.interpretation_use)}</span>
                </li>
              ))}
            </ul>
          </article>
        ))}
      </div>
    </SectionShell>
  )
}

function DominantPlanetItem({ planet }: { planet: DominantPlanet }) {
  return (
    <article className="natal-expert-data-card">
      <h4>
        #{formatValue(planet.rank)} {formatValue(planet.planet_code)}
      </h4>
      <dl className="natal-expert-facts natal-expert-facts--compact">
        <FactRow label="score" value={planet.score} />
      </dl>
      {hasItems(planet.factors) ? (
        <ul className="natal-expert-list">
          {planet.factors.map((factor, index) => (
            <li key={`${factor.factor_code ?? "factor"}-${index}`} className="natal-expert-item natal-expert-item--stacked">
              <strong>{factor.factor_code ?? "factor"}</strong>
              <span>
                raw: {formatValue(factor.raw_value)} / normalized: {formatValue(factor.normalized_value)}
              </span>
              <span>
                weight: {formatValue(factor.weight)} / weighted_score: {formatValue(factor.weighted_score)}
              </span>
              {factor.reason ? <span>{factor.reason}</span> : null}
            </li>
          ))}
        </ul>
      ) : null}
    </article>
  )
}

function DominantPlanetsBlock({ dominantPlanets }: { dominantPlanets?: DominantPlanetsResult | null }) {
  const planets = dominantPlanets?.planets ?? []
  return (
    <SectionShell
      title="Planetes dominantes"
      isEmpty={!dominantPlanets}
      emptyLabel="Dominantes indisponibles dans ce payload."
    >
      <dl className="natal-expert-facts">
        <FactRow label="top_planet_code" value={dominantPlanets?.top_planet_code} />
        <FactRow label="chart_ruler_code" value={dominantPlanets?.chart_ruler_code} />
        <FactRow label="most_elevated_planet_code" value={dominantPlanets?.most_elevated_planet_code} />
      </dl>
      {planets.length === 0 ? (
        <p className="natal-expert-empty">Aucun classement planetaire dans le payload.</p>
      ) : (
        <div className="natal-expert-card-grid">
          {planets.map((planet, index) => (
            <DominantPlanetItem key={`${planet.planet_code ?? "planet"}-${index}`} planet={planet} />
          ))}
        </div>
      )}
    </SectionShell>
  )
}

function StringList({ title, items }: { title: string; items?: string[] }) {
  return (
    <div className="natal-expert-string-list">
      <h4>{title}</h4>
      {hasItems(items) ? (
        <ul className="natal-expert-list">
          {items.map((item) => (
            <li key={item} className="natal-expert-item">
              <span>{item}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="natal-expert-empty natal-expert-empty--compact">Aucune entree.</p>
      )}
    </div>
  )
}

function InterpretationAdapterBlock({ adapter }: { adapter?: InterpretationAdapterResult | null }) {
  return (
    <SectionShell
      title="Adaptateur interpretatif factuel"
      isEmpty={!adapter}
      emptyLabel="Adaptateur indisponible dans ce payload."
    >
      {adapter ? (
        <>
          <div className="natal-expert-card-grid">
            <article className="natal-expert-data-card">
              <h4>signals</h4>
              {hasItems(adapter.signals) ? (
                <ul className="natal-expert-list">
                  {adapter.signals.map((signal, index) => (
                    <li key={`${signal.signal ?? "signal"}-${index}`} className="natal-expert-item natal-expert-item--stacked">
                      <strong>{signal.signal ?? "signal"}</strong>
                      <span>theme: {formatValue(signal.theme)}</span>
                      <span>source: {formatValue(signal.source_type)} / {formatValue(signal.source_code)}</span>
                      <span>priority: {formatValue(signal.priority)} / rank: {formatValue(signal.priority_rank)}</span>
                      <span>weight: {formatValue(signal.weight)}</span>
                      <span>semantic_category: {formatValue(signal.semantic_category)}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="natal-expert-empty natal-expert-empty--compact">Aucun signal.</p>
              )}
            </article>
            <article className="natal-expert-data-card">
              <h4>activated_themes</h4>
              {hasItems(adapter.activated_themes) ? (
                <ul className="natal-expert-list">
                  {adapter.activated_themes.map((theme, index) => (
                    <li key={`${theme.theme ?? "theme"}-${index}`} className="natal-expert-item natal-expert-item--stacked">
                      <strong>{theme.theme ?? "theme"}</strong>
                      <span>theme_category: {formatValue(theme.theme_category)}</span>
                      <span>activation_score: {formatValue(theme.activation_score)}</span>
                      <span>priority: {formatValue(theme.priority)} / rank: {formatValue(theme.priority_rank)}</span>
                      {hasItems(theme.contributing_signals) ? (
                        <span>contributing_signals: {theme.contributing_signals.join(", ")}</span>
                      ) : null}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="natal-expert-empty natal-expert-empty--compact">Aucun theme active.</p>
              )}
            </article>
          </div>
          <div className="natal-expert-string-grid">
            <StringList title="dominant_topics" items={adapter.dominant_topics} />
            <StringList title="dominant_axes" items={adapter.dominant_axes} />
            <StringList title="tension_patterns" items={adapter.tension_patterns} />
            <StringList title="support_patterns" items={adapter.support_patterns} />
            <StringList title="critical_patterns" items={adapter.critical_patterns} />
            <StringList title="narrative_priorities" items={adapter.narrative_priorities} />
          </div>
        </>
      ) : null}
    </SectionShell>
  )
}

/** Rend les faits experts natals publics fournis par l'API sans calculer l'astrologie dans React. */
export function NatalExpertPanel({ chart, isLoading = false, errorMessage = null }: NatalExpertPanelProps) {
  if (isLoading) {
    return (
      <article className="natal-card natal-expert-panel" aria-busy="true">
        <h2>Panneau expert natal</h2>
        <p className="natal-expert-empty">Chargement des faits techniques...</p>
      </article>
    )
  }

  if (errorMessage) {
    return (
      <article className="natal-card natal-expert-panel" role="alert">
        <h2>Panneau expert natal</h2>
        <p className="natal-expert-empty">{errorMessage}</p>
      </article>
    )
  }

  if (!chart) {
    return (
      <article className="natal-card natal-expert-panel">
        <h2>Panneau expert natal</h2>
        <p className="natal-expert-empty">Aucun theme natal charge.</p>
      </article>
    )
  }

  const result = chart.result
  const noTime = isNoTimePayload(chart)
  const expertPayloadMissing = isExpertPayloadMissing(result)

  return (
    <article className="natal-card natal-expert-panel">
      <div className="natal-expert-panel__header">
        <span className="natal-expert-panel__eyebrow">JSON public</span>
        <h2>Panneau expert natal</h2>
        <p>
          Faits techniques fournis par l'API publique du theme natal. Les blocs absents restent
          indiques comme indisponibles.
        </p>
      </div>

      {noTime ? (
        <p className="natal-expert-warning" role="note">
          Mode sans heure fiable: certains blocs avances peuvent etre neutralises par le payload.
        </p>
      ) : null}

      {expertPayloadMissing ? (
        <p className="natal-expert-warning" role="note">
          Ancien payload ou projection partielle: aucun bloc expert avance n'est present.
        </p>
      ) : null}

      <div className="natal-expert-panel__content">
        <ChartSectBlock dignities={result.dignities} />
        <PlanetSectBlock dignities={result.dignities} />
        <TraditionalConditionsBlock conditions={result.traditional_conditions} />
        <AdvancedConditionsBlock conditions={result.advanced_conditions} />
        <DignityScoresBlock dignities={result.dignities} />
        <ProfilesBlock profiles={result.planet_condition_profiles} />
        <SignalsBlock signals={result.planet_condition_signals} />
        <DominantPlanetsBlock dominantPlanets={result.dominant_planets} />
        <InterpretationAdapterBlock adapter={result.interpretation_adapter} />
      </div>
    </article>
  )
}
