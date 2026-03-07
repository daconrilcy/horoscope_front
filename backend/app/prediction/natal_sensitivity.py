from typing import Dict

from app.prediction.context_loader import LoadedPredictionContext
from app.prediction.schemas import NatalChart


class NatalSensitivityCalculator:
    """
    Service to calculate category sensitivity NS(c) based on natal chart.
    NS(c) = clip(1.0 + w_occ * Occ(c) + w_rul * Rul(c) + w_ang * Ang(c) + w_dom * Dom(c), 0.75, 1.25)
    """

    NS_MIN = 0.75
    NS_MAX = 1.25
    ANGULAR_HOUSES = {1, 4, 7, 10}

    def compute(self, natal: NatalChart, ctx: LoadedPredictionContext) -> Dict[str, float]:
        """
        Computes sensitivity for all enabled categories.
        """
        params = ctx.ruleset_context.parameters
        w_occ = float(params.get("ns_weight_occ", 0.15))
        w_rul = float(params.get("ns_weight_rul", 0.10))
        w_ang = float(params.get("ns_weight_ang", 0.10))
        w_dom = float(params.get("ns_weight_dom", 0.0))

        pc = ctx.prediction_context
        results: Dict[str, float] = {}

        for category in pc.categories:
            if not category.is_enabled:
                continue

            cat_code = category.code
            
            occ = self._compute_occ(natal, cat_code, pc)
            rul = self._compute_rul(natal, cat_code, pc)
            ang = self._compute_ang(natal, cat_code, pc)
            dom = self._compute_dom(natal, cat_code, pc) if w_dom != 0 else 0.0

            ns_val = 1.0 + (w_occ * occ) + (w_rul * rul) + (w_ang * ang) + (w_dom * dom)
            
            # Clip between [0.75, 1.25]
            results[cat_code] = max(self.NS_MIN, min(self.NS_MAX, ns_val))

        return results

    def _compute_occ(self, natal: NatalChart, cat_code: str, pc) -> float:
        # Trouver les maisons associées à cette catégorie
        associated_houses = {
            w.house_number for w in pc.house_category_weights
            if w.category_code == cat_code and w.weight > 0
        }
        total = 0.0
        for planet_code, house_num in natal.planet_houses.items():
            if house_num in associated_houses:
                profile = pc.planet_profiles.get(planet_code)
                if profile:
                    total += profile.weight_day_climate
        return total

    def _compute_rul(self, natal: NatalChart, cat_code: str, pc) -> float:
        # AC4: Si le maître du signe de la cuspide d'une maison associée à c est en maison angulaire
        associated_houses = {
            w.house_number for w in pc.house_category_weights
            if w.category_code == cat_code and w.weight > 0
        }
        
        total = 0.0
        for house_num in associated_houses:
            ruler_code = natal.house_sign_rulers.get(house_num)
            if ruler_code:
                # Localiser ce maître dans le thème natal
                ruler_house = natal.planet_houses.get(ruler_code)
                if ruler_house in self.ANGULAR_HOUSES:
                    total += 1.0 # Contribution unitaire au rulership
                    
        return total

    def _compute_ang(self, natal: NatalChart, cat_code: str, pc) -> float:
        # Planètes natales angulaires qui ont un poids > 0 sur la catégorie
        planet_cat_weights = {
            w.planet_code: w.weight for w in pc.planet_category_weights
            if w.category_code == cat_code
        }
        total = 0.0
        for planet_code, house_num in natal.planet_houses.items():
            if house_num in self.ANGULAR_HOUSES:
                weight = planet_cat_weights.get(planet_code, 0.0)
                total += weight
        return total

    def _compute_dom(self, natal: NatalChart, cat_code: str, pc) -> float:
        # Domination optionnelle - Non implémenté en V1
        return 0.0
