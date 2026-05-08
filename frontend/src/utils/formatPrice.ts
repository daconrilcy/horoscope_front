// Centralise le formatage monetaire partage entre pages et panneaux admin.
export function formatCurrencyCents(
  amountCents: number,
  currency: string,
  locale: string,
  options: Intl.NumberFormatOptions = {},
): string {
  return new Intl.NumberFormat(locale, {
    style: "currency",
    currency,
    ...options,
  }).format(amountCents / 100)
}
