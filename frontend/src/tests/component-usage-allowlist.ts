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
]
