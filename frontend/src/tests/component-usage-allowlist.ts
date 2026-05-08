// Registre exact des composants conserves malgre un usage runtime ambigu.

export type ComponentUsageClassification =
  | "public-library-export"
  | "runtime-used"
  | "test-only"
  | "remove"
  | "needs-user-decision"

export type ComponentUsageException = {
  file: string
  exports: string[]
  classification: ComponentUsageClassification
  owner: string
  evidence: string
  exitCondition: string
}

export const COMPONENT_USAGE_EXCEPTIONS: ComponentUsageException[] = [
  {
    file: "components/B2BAstrologyPanel.tsx",
    exports: ["B2BAstrologyPanel"],
    classification: "test-only",
    owner: "enterprise dashboard",
    evidence: "F-005 no-runtime-reference; imports only in B2BAstrologyPanel.test.tsx and architecture registers.",
    exitCondition: "Deplacer sous feature enterprise ou supprimer apres decision produit.",
  },
  {
    file: "components/B2BBillingPanel.tsx",
    exports: ["B2BBillingPanel"],
    classification: "test-only",
    owner: "enterprise dashboard",
    evidence: "F-005 no-runtime-reference; imports only in B2BBillingPanel.test.tsx and architecture registers.",
    exitCondition: "Deplacer sous feature enterprise ou supprimer apres decision produit.",
  },
  {
    file: "components/B2BEditorialPanel.tsx",
    exports: ["B2BEditorialPanel"],
    classification: "test-only",
    owner: "enterprise dashboard",
    evidence: "F-005 no-runtime-reference; imports only in B2BEditorialPanel.test.tsx and architecture registers.",
    exitCondition: "Deplacer sous feature enterprise ou supprimer apres decision produit.",
  },
  {
    file: "components/B2BUsagePanel.tsx",
    exports: ["B2BUsagePanel"],
    classification: "test-only",
    owner: "enterprise dashboard",
    evidence: "F-005 no-runtime-reference; imports only in B2BUsagePanel.test.tsx and architecture registers.",
    exitCondition: "Deplacer sous feature enterprise ou supprimer apres decision produit.",
  },
  {
    file: "components/DailyInsightsSection.tsx",
    exports: ["DailyInsightsSection", "DailyInsightsSectionPresenter"],
    classification: "test-only",
    owner: "daily horoscope",
    evidence: "F-005 no-runtime-reference; imports only in MiniInsightCard.test.tsx and design-system guard.",
    exitCondition: "Rattacher au runtime daily ou supprimer apres inventaire route.",
  },
  {
    file: "components/MiniInsightCard.tsx",
    exports: ["MiniInsightCard"],
    classification: "test-only",
    owner: "daily horoscope",
    evidence: "Runtime reachability guard found only type-only hook import and import from test-only DailyInsightsSection.",
    exitCondition: "Rattacher avec DailyInsightsSection au runtime daily ou supprimer apres inventaire route.",
  },
  {
    file: "components/ConstellationSVG.tsx",
    exports: ["ConstellationSVG"],
    classification: "test-only",
    owner: "daily/dashboard UI",
    evidence: "Runtime reachability guard found only import from test-only HeroHoroscopeCard.",
    exitCondition: "Rattacher avec HeroHoroscopeCard au runtime owner ou supprimer apres decision produit.",
  },
  {
    file: "components/HeroHoroscopeCard.tsx",
    exports: ["HeroHoroscopeCard"],
    classification: "test-only",
    owner: "daily/dashboard UI",
    evidence: "F-005 no-runtime-reference; imports only in HeroHoroscopeCard.test.tsx and visual/design guards.",
    exitCondition: "Rattacher au runtime owner ou supprimer apres decision produit.",
  },
  {
    file: "components/OpsMonitoringPanel.tsx",
    exports: ["OpsMonitoringPanel"],
    classification: "test-only",
    owner: "admin operations",
    evidence: "F-005 no-runtime-reference; imports only in OpsMonitoringPanel.test.tsx and architecture registers.",
    exitCondition: "Deplacer sous feature admin-ops ou supprimer apres decision produit.",
  },
  {
    file: "components/OpsPersonaPanel.tsx",
    exports: ["OpsPersonaPanel"],
    classification: "test-only",
    owner: "admin operations",
    evidence: "F-005 no-runtime-reference; imports only in OpsPersonaPanel.test.tsx and architecture registers.",
    exitCondition: "Deplacer sous feature admin-ops ou supprimer apres decision produit.",
  },
  {
    file: "components/PrivacyPanel.tsx",
    exports: ["PrivacyPanel"],
    classification: "test-only",
    owner: "settings privacy",
    evidence: "F-005 no-runtime-reference; imports only in PrivacyPanel.test.tsx and architecture registers.",
    exitCondition: "Deplacer sous settings ou feature privacy.",
  },
  {
    file: "components/TodayHeader.tsx",
    exports: ["TodayHeader"],
    classification: "test-only",
    owner: "daily/dashboard UI",
    evidence: "F-005 no-runtime-reference; imports only in TodayHeader.test.tsx and architecture registers.",
    exitCondition: "Rattacher au runtime owner ou supprimer apres decision produit.",
  },
  {
    file: "components/dashboard/DashboardCard.tsx",
    exports: ["DashboardCard"],
    classification: "public-library-export",
    owner: "dashboard UI",
    evidence: "Import-aware whole-components guard found only dashboard barrel export, without runtime consumer.",
    exitCondition: "Rattacher a une route dashboard ou supprimer apres decision produit.",
  },
  {
    file: "components/icons/DashboardIcons.tsx",
    exports: [
      "ChatIcon",
      "CrystalBallIcon",
      "SettingsIcon",
      "StarIcon",
      "UserIcon",
    ],
    classification: "public-library-export",
    owner: "dashboard icons",
    evidence: "F-005 manual-review-required; named icon public surface exported by components/icons/index.ts.",
    exitCondition: "Remplacer par lucide-react ou prouver un consommateur runtime exact.",
  },
  {
    file: "components/prediction/TurningPointsList.tsx",
    exports: ["TurningPointsList"],
    classification: "test-only",
    owner: "prediction UI",
    evidence: "Runtime reachability guard found no runtime import; retained only for TurningPointsEnriched.test.tsx.",
    exitCondition: "Rattacher au runtime prediction ou supprimer avec TurningPointsEnriched.test.tsx apres decision produit.",
  },
  {
    file: "components/ui/Form/FormField.tsx",
    exports: ["FormField"],
    classification: "public-library-export",
    owner: "ui form primitive",
    evidence: "F-005 barrel-only via components/ui/Form/index.ts; primitive publique testee.",
    exitCondition: "Supprimer seulement si le barrel public Form cesse d'exposer FormField.",
  },
  {
    file: "components/ui/Card/Card.tsx",
    exports: ["Card"],
    classification: "public-library-export",
    owner: "ui card primitive",
    evidence: "Import-aware whole-components guard found only ui barrel export, without runtime consumer.",
    exitCondition: "Supprimer seulement si le barrel public UI cesse d'exposer Card.",
  },
  {
    file: "components/prediction/DayPredictionCard.tsx",
    exports: ["DayPredictionCard"],
    classification: "test-only",
    owner: "prediction UI",
    evidence: "Runtime reachability guard found no runtime import; retained only for day-prediction-card-tone.test.ts.",
    exitCondition: "Extraire getDayPredictionToneClassKey ou supprimer apres retrait du test direct.",
  },
]
