export interface FocusMomentTag {
  code: string;
  label: string;
}

export interface FocusMomentCardModel {
  timeRange: string;
  title: string;
  tags: FocusMomentTag[];
  description: string;
  ctaLabel: string;
}

export interface DailyDomainScore {
  code: string;
  label: string;
  score: number; // 0-20
  percentage: number; // 0-100
}

export interface DailyDomainsCardModel {
  title: string;
  primaryDomains: DailyDomainScore[];
  secondaryDomains: DailyDomainScore[];
}

export interface DailyAdviceCardModel {
  title: string;
  advice: string;
  emphasis: string;
}
