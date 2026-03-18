import React from 'react'
import type { DailyPredictionResponse } from '../../types/dailyPrediction'
import type { DayPeriodKey } from '../../types/dayTimeline'
import type { DailyAgendaSlot } from '../../utils/dailyAstrology'
import type { Lang } from '../../i18n/predictions'
import { FocusMomentCard } from './FocusMomentCard'
import { DailyDomainsCard } from './DailyDomainsCard'
import { buildFocusMomentCardModel } from '../../utils/focusMomentCardMapper'
import { buildDailyDomainsCardModel } from '../../utils/dailyDomainsCardMapper'
import './DetailAndScoresSection.css'

interface DetailAndScoresSectionProps {
  selectedPeriodKey: DayPeriodKey | null
  agendaSlots: DailyAgendaSlot[]
  prediction: DailyPredictionResponse
  lang: Lang
}

export const DetailAndScoresSection: React.FC<DetailAndScoresSectionProps> = ({
  selectedPeriodKey,
  agendaSlots,
  prediction,
  lang
}) => {
  const focusModel = buildFocusMomentCardModel(selectedPeriodKey, agendaSlots, prediction, lang)
  const domainsModel = buildDailyDomainsCardModel(prediction.categories, lang)

  return (
    <section className="detail-scores-section" aria-label="Détails et scores">
      <div className="detail-scores-section__grid">
        <div className="detail-scores-section__focus">
          <FocusMomentCard model={focusModel} />
        </div>
        <div className="detail-scores-section__domains">
          <DailyDomainsCard model={domainsModel} lang={lang} />
        </div>
      </div>
    </section>
  )
}
