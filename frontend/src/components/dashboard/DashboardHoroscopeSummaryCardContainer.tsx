import React from "react"
import { useAccessTokenSnapshot } from "../../utils/authToken"
import { useAstrologyLabels } from "../../i18n/astrology"
import { useDashboardAstroSummary } from "./useDashboardAstroSummary"
import { DashboardHoroscopeSummaryCard } from "./DashboardHoroscopeSummaryCard"

/**
 * Container component for DashboardHoroscopeSummaryCard (Story 55.1).
 * Handles data fetching and passes props to the pure presentation component.
 */
export const DashboardHoroscopeSummaryCardContainer: React.FC = () => {
  const accessToken = useAccessTokenSnapshot()
  const { lang } = useAstrologyLabels()
  const summary = useDashboardAstroSummary(accessToken)

  return (
    <DashboardHoroscopeSummaryCard
      prediction={summary.prediction}
      isLoading={summary.isLoading}
      isError={summary.isError}
      locale={lang}
      sign={summary.sign}
      userId={summary.userId}
      dateKey={summary.dateKey}
      dayScore={summary.dayScore}
      onRetry={() => {
        summary.refetch()
      }}
    />
  )
}
