import type { AstrologyLang } from "./astrology"
import type { AdminConsumptionGranularity } from "../api/adminPrompts"

/** Textes de la route /admin/prompts/consumption (alignés FR / EN / ES). */
export type AdminPromptsConsumptionStrings = {
  regionAriaLabel: string
  kicker: string
  surfaceTitle: string
  surfaceIntro: string
  toolbarAria: string
  groupAxis: string
  groupPeriod: string
  groupRefine: string
  viewLabel: string
  viewAria: string
  viewOptionUser: string
  viewOptionSubscription: string
  viewOptionFeature: string
  granularityLabel: string
  granularityAria: string
  granularityOptionDay: string
  granularityOptionMonth: string
  periodFromLabel: string
  periodToLabel: string
  searchLabel: string
  searchPlaceholder: string
  exportCsv: string
  exportCsvPending: string
  granularityHint: (granularity: AdminConsumptionGranularity) => string
  loadingAggregates: string
  errorAggregates: string
  emptyAggregates: string
  errorExportCsv: string
  aggregatesHeading: string
  aggregatesHint: string
  tablePeriod: string
  tableAxis: string
  tableRequests: string
  tableTokens: string
  tableCost: string
  tableLatency: string
  tableErrorRate: string
  tableActions: string
  viewLogsButton: string
  rowLines: (count: number) => string
  pageLabel: (page: number) => string
  prevPage: string
  nextPage: string
  drilldownHeading: string
  drilldownLead: string
  selectedRowSummary: (periodLabel: string, axisLabel: string) => string
  loadingDrilldown: string
  errorDrilldown: string
  drillTableTimestamp: string
  drillTableRequestId: string
  drillTableFeature: string
  drillTableProvider: string
  drillTableSnapshot: string
  drillTableValidation: string
}

export const adminPromptsConsumptionByLang: Record<AstrologyLang, AdminPromptsConsumptionStrings> = {
  fr: {
    regionAriaLabel: "Pilotage de la consommation LLM",
    kicker: "Exploitation",
    surfaceTitle: "Consommation et investigation des appels",
    surfaceIntro:
      "Cadrez d'abord l'axe d'analyse et la période, lisez les agrégats, puis ouvrez le journal corrélé pour une ligne donnée. Les filtres actifs restent appliqués au drill-down.",
    toolbarAria: "Filtres et actions de pilotage consommation",
    groupAxis: "Axe d'analyse",
    groupPeriod: "Période (fuseau navigateur → requêtes UTC)",
    groupRefine: "Affinage et export",
    viewLabel: "Vue",
    viewAria: "Vue d'agrégation : utilisateur, abonnement ou feature",
    viewOptionUser: "Utilisateur",
    viewOptionSubscription: "Abonnement",
    viewOptionFeature: "Feature / sous-fonction",
    granularityLabel: "Granularité",
    granularityAria: "Pas de temps des agrégats",
    granularityOptionDay: "Journalière",
    granularityOptionMonth: "Mensuelle",
    periodFromLabel: "Début",
    periodToLabel: "Fin",
    searchLabel: "Recherche",
    searchPlaceholder: "E-mail, plan, feature…",
    exportCsv: "Exporter CSV",
    exportCsvPending: "Export en cours…",
    granularityHint: (granularity) =>
      `Granularité par défaut: agrégé par période sélectionnée (${granularity}).`,
    loadingAggregates: "Chargement des agrégats…",
    errorAggregates: "Impossible de charger la consommation.",
    emptyAggregates:
      "Aucune ligne d'agrégat pour cette période et ces filtres. Élargissez la plage temporelle ou modifiez la recherche.",
    errorExportCsv: "L'export CSV a échoué. Réessayez ou vérifiez la session admin.",
    aggregatesHeading: "Agrégats par période",
    aggregatesHint:
      "Vue macro : volumes, jetons et coûts consolidés. Utilisez « Voir logs récents » pour descendre au niveau appel.",
    tablePeriod: "Période",
    tableAxis: "Axe",
    tableRequests: "Requêtes",
    tableTokens: "Jetons in / out / total",
    tableCost: "Coût estimé",
    tableLatency: "Latence moy.",
    tableErrorRate: "Taux erreur",
    tableActions: "Actions",
    viewLogsButton: "Voir logs récents",
    rowLines: (count) => `${count} lignes`,
    pageLabel: (page) => `Page ${page}`,
    prevPage: "Précédent",
    nextPage: "Suivant",
    drilldownHeading: "Drill-down appels récents (50 max)",
    drilldownLead:
      "Journal micro : appels récents corrélés à la ligne d'agrégat sélectionnée (distinct de la table ci-dessus).",
    selectedRowSummary: (periodLabel, axisLabel) => `Ligne suivie : ${periodLabel} · ${axisLabel}`,
    loadingDrilldown: "Chargement du journal…",
    errorDrilldown: "Impossible de charger les logs corrélés.",
    drillTableTimestamp: "Horodatage",
    drillTableRequestId: "request_id",
    drillTableFeature: "feature / subfeature",
    drillTableProvider: "Fournisseur",
    drillTableSnapshot: "snapshot / manifeste",
    drillTableValidation: "validation_status",
  },
  en: {
    regionAriaLabel: "LLM consumption operations",
    kicker: "Operations",
    surfaceTitle: "Consumption and call investigation",
    surfaceIntro:
      "Frame the analysis axis and time range first, read aggregates, then open the correlated log for a given row. Active filters stay applied to drill-down.",
    toolbarAria: "Consumption piloting filters and actions",
    groupAxis: "Analysis axis",
    groupPeriod: "Period (browser TZ → UTC queries)",
    groupRefine: "Refine and export",
    viewLabel: "View",
    viewAria: "Aggregation view: user, subscription, or feature",
    viewOptionUser: "User",
    viewOptionSubscription: "Subscription",
    viewOptionFeature: "Feature / sub-feature",
    granularityLabel: "Granularity",
    granularityAria: "Aggregate time step",
    granularityOptionDay: "Daily",
    granularityOptionMonth: "Monthly",
    periodFromLabel: "Start",
    periodToLabel: "End",
    searchLabel: "Search",
    searchPlaceholder: "Email, plan, feature…",
    exportCsv: "Export CSV",
    exportCsvPending: "Exporting…",
    granularityHint: (granularity) =>
      `Default granularity: aggregated over the selected period (${granularity}).`,
    loadingAggregates: "Loading aggregates…",
    errorAggregates: "Could not load consumption.",
    emptyAggregates:
      "No aggregate rows for this period and filters. Widen the time range or adjust your search.",
    errorExportCsv: "CSV export failed. Retry or verify your admin session.",
    aggregatesHeading: "Aggregates by period",
    aggregatesHint:
      "Macro view: volumes, tokens, and consolidated cost. Use “View recent logs” to drill down to call level.",
    tablePeriod: "Period",
    tableAxis: "Axis",
    tableRequests: "Requests",
    tableTokens: "Tokens in / out / total",
    tableCost: "Est. cost",
    tableLatency: "Avg latency",
    tableErrorRate: "Error rate",
    tableActions: "Actions",
    viewLogsButton: "View recent logs",
    rowLines: (count) => `${count} rows`,
    pageLabel: (page) => `Page ${page}`,
    prevPage: "Previous",
    nextPage: "Next",
    drilldownHeading: "Drill-down: recent calls (50 max)",
    drilldownLead:
      "Micro journal: recent calls correlated to the selected aggregate row (separate from the table above).",
    selectedRowSummary: (periodLabel, axisLabel) => `Tracked row: ${periodLabel} · ${axisLabel}`,
    loadingDrilldown: "Loading journal…",
    errorDrilldown: "Could not load correlated logs.",
    drillTableTimestamp: "Timestamp",
    drillTableRequestId: "request_id",
    drillTableFeature: "feature / subfeature",
    drillTableProvider: "Provider",
    drillTableSnapshot: "snapshot / manifest",
    drillTableValidation: "validation_status",
  },
  es: {
    regionAriaLabel: "Operaciones de consumo LLM",
    kicker: "Operaciones",
    surfaceTitle: "Consumo e investigación de llamadas",
    surfaceIntro:
      "Primero encuadre el eje y el periodo, lea los agregados y abra el registro correlacionado para una fila. Los filtros activos se mantienen en el drill-down.",
    toolbarAria: "Filtros y acciones de pilotaje de consumo",
    groupAxis: "Eje de análisis",
    groupPeriod: "Periodo (TZ navegador → consultas UTC)",
    groupRefine: "Afinar y exportar",
    viewLabel: "Vista",
    viewAria: "Vista de agregación: usuario, suscripción o feature",
    viewOptionUser: "Usuario",
    viewOptionSubscription: "Suscripción",
    viewOptionFeature: "Feature / sub-feature",
    granularityLabel: "Granularidad",
    granularityAria: "Paso temporal de los agregados",
    granularityOptionDay: "Diaria",
    granularityOptionMonth: "Mensual",
    periodFromLabel: "Inicio",
    periodToLabel: "Fin",
    searchLabel: "Búsqueda",
    searchPlaceholder: "Email, plan, feature…",
    exportCsv: "Exportar CSV",
    exportCsvPending: "Exportando…",
    granularityHint: (granularity) =>
      `Granularidad por defecto: agregado por el periodo seleccionado (${granularity}).`,
    loadingAggregates: "Cargando agregados…",
    errorAggregates: "No se pudo cargar el consumo.",
    emptyAggregates:
      "No hay filas agregadas para este periodo y filtros. Amplíe el rango temporal o ajuste la búsqueda.",
    errorExportCsv: "La exportación CSV falló. Reintente o verifique la sesión admin.",
    aggregatesHeading: "Agregados por periodo",
    aggregatesHint:
      "Vista macro: volúmenes, tokens y coste. Use « Ver registros recientes » para bajar al nivel de llamada.",
    tablePeriod: "Periodo",
    tableAxis: "Eje",
    tableRequests: "Peticiones",
    tableTokens: "Tokens in / out / total",
    tableCost: "Coste est.",
    tableLatency: "Latencia media",
    tableErrorRate: "Tasa de error",
    tableActions: "Acciones",
    viewLogsButton: "Ver registros recientes",
    rowLines: (count) => `${count} filas`,
    pageLabel: (page) => `Página ${page}`,
    prevPage: "Anterior",
    nextPage: "Siguiente",
    drilldownHeading: "Drill-down: llamadas recientes (50 máx.)",
    drilldownLead:
      "Diario micro: llamadas recientes correlacionadas con la fila seleccionada (distinto de la tabla superior).",
    selectedRowSummary: (periodLabel, axisLabel) => `Fila seguida: ${periodLabel} · ${axisLabel}`,
    loadingDrilldown: "Cargando diario…",
    errorDrilldown: "No se pudieron cargar los registros correlacionados.",
    drillTableTimestamp: "Marca de tiempo",
    drillTableRequestId: "request_id",
    drillTableFeature: "feature / subfeature",
    drillTableProvider: "Proveedor",
    drillTableSnapshot: "snapshot / manifiesto",
    drillTableValidation: "validation_status",
  },
}
