import type { Lang } from "../i18n/predictions";
import {
  getCategoryMeta as getLocalizedCategoryMeta,
  getNoteBand as getLocalizedNoteBand,
  getPredictionLang,
} from "./predictionI18n";

export function getNoteBand(note: number, lang: Lang = getPredictionLang()) {
  return getLocalizedNoteBand(note, lang);
}

export function getCategoryMeta(code: string, lang: Lang = getPredictionLang()) {
  return getLocalizedCategoryMeta(code, lang);
}
