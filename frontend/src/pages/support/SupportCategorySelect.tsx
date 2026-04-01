import React from "react"
import { useTranslation, useAstrologyLabels } from "@i18n"
import { useHelpCategories } from "@api/help"
import { EmptyState } from "@ui/EmptyState/EmptyState"
import { ErrorState } from "@ui/ErrorState/ErrorState"
import { Skeleton } from "@ui/Skeleton/Skeleton"
import { 
  CreditCard, 
  Settings, 
  Bug, 
  User, 
  HelpCircle, 
  ShieldCheck, 
  MessageCircle 
} from "lucide-react"

interface SupportCategorySelectProps {
  onSelect: (code: string, label: string) => void
}

const CATEGORY_ICONS: Record<string, React.ElementType> = {
  subscription_problem: CreditCard,
  billing_issue: Settings,
  bug: Bug,
  account_access: User,
  feature_question: HelpCircle,
  data_privacy: ShieldCheck,
  other: MessageCircle,
}

export function SupportCategorySelect({ onSelect }: SupportCategorySelectProps) {
  const { lang } = useAstrologyLabels()
  const { help } = useTranslation("support")
  const { data: categories, isLoading, isError } = useHelpCategories(lang)

  if (isLoading) {
    return (
      <div className="category-grid">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="category-card category-card--skeleton">
            <Skeleton variant="rect" height={32} width={32} className="mb-2" />
            <Skeleton variant="text" width="60%" height={20} />
          </div>
        ))}
      </div>
    )
  }

  if (isError) {
    return <ErrorState message={help.categories.error} />
  }

  if (!categories || categories.length === 0) {
    return (
      <EmptyState
        icon={<HelpCircle size={40} />}
        title={help.categories.emptyTitle}
        description={help.categories.emptyDescription}
      />
    )
  }

  return (
    <div className="category-grid">
      {categories?.map((cat) => {
        const Icon = CATEGORY_ICONS[cat.code] || HelpCircle
        return (
          <button
            type="button"
            key={cat.code} 
            className="category-card"
            onClick={() => onSelect(cat.code, cat.label)}
          >
            <div className="category-card__icon">
              <Icon size={32} />
            </div>
            <span className="category-card__label">{cat.label}</span>
          </button>
        )
      })}
    </div>
  )
}
