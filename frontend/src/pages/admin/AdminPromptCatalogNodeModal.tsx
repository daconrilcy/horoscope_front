import type {
  AdminLlmUseCase,
  AdminPromptDraftCreateInput,
  AdminPromptVersion,
} from "@api"

import type { AdminPromptsEditorStrings } from "../../i18n/adminPromptsEditor"
import { AdminPromptEditorPanel } from "./AdminPromptEditorPanel"
import type { AdminPromptCatalogFlowNode } from "./adminPromptCatalogFlowProjection"

type AdminPromptCatalogNodeModalProps = {
  node: AdminPromptCatalogFlowNode
  useCases: AdminLlmUseCase[]
  versions: AdminPromptVersion[]
  activeVersion: AdminPromptVersion | null
  useCaseDisplayName: string | null
  editorStrings: AdminPromptsEditorStrings
  saveError: string | null
  saveSuccess: string | null
  isPending: boolean
  onClose: () => void
  onSubmit: (payload: AdminPromptDraftCreateInput) => Promise<void>
}

export function AdminPromptCatalogNodeModal({
  node,
  useCases,
  versions,
  activeVersion,
  useCaseDisplayName,
  editorStrings,
  saveError,
  saveSuccess,
  isPending,
  onClose,
  onSubmit,
}: AdminPromptCatalogNodeModalProps) {
  const isEditable = Boolean(node.editableUseCaseKey)

  return (
    <div className="modal-overlay" role="presentation">
      <div
        className="modal-content admin-prompts-modal admin-prompts-modal--catalog-node"
        aria-labelledby="admin-prompt-catalog-node-title"
        role="dialog"
        aria-modal="true"
      >
        <div className="admin-prompts-modal__header">
          <div>
            <p className="admin-prompts-modal__eyebrow">
              {isEditable ? "Edition directe" : "Lecture de la chaîne active"}
            </p>
            <h3 id="admin-prompt-catalog-node-title">{node.title}</h3>
            <p className="admin-prompts-modal__copy">{node.summary}</p>
          </div>
          <button className="text-button" type="button" onClick={onClose}>
            Fermer
          </button>
        </div>

        <dl className="admin-prompts-modal__meta admin-prompts-modal__meta--catalog-node">
          {node.meta.map((item) => (
            <div key={`${node.id}-${item.label}`}>
              <dt>{item.label}</dt>
              <dd>{item.value}</dd>
            </div>
          ))}
        </dl>

        {isEditable && node.editableUseCaseKey ? (
          <AdminPromptEditorPanel
            useCaseKey={node.editableUseCaseKey}
            useCaseDisplayName={useCaseDisplayName ?? node.editableUseCaseKey}
            versions={versions}
            activeVersion={activeVersion}
            useCases={useCases}
            strings={editorStrings}
            saveError={saveError}
            saveSuccess={saveSuccess}
            isPending={isPending}
            onSubmit={onSubmit}
          />
        ) : (
          <section className="admin-prompts-catalog-node-modal__read-only">
            <h4>Prompt actif</h4>
            <pre className="admin-prompts-code">
              {node.promptContent && node.promptContent.trim().length > 0
                ? node.promptContent
                : "Aucun texte exploitable n'est exposé par cette couche."}
            </pre>
          </section>
        )}
      </div>
    </div>
  )
}
