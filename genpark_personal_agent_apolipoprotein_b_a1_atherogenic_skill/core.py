# -*- coding: utf-8 -*-
"""Apolipoprotein B/A1 Atherogenic Sentinel for GenPark Personal Agent."""
import json
from typing import Dict, Any

class ApolipoproteinAtherogenicSentinel:
    @staticmethod
    def calculate_apob_apoa1_ratio(apob_mg_dl: float, apoa1_mg_dl: float, gender: str = "male") -> Dict[str, Any]:
        ratio = round(apob_mg_dl / max(1.0, apoa1_mg_dl), 2)
        # AMORIS & INTERHEART study thresholds:
        cutoff_high = 0.90 if gender.lower() == "male" else 0.80
        cutoff_opt = 0.60 if gender.lower() == "male" else 0.50
        
        if ratio >= cutoff_high:
            tier = "VERY_HIGH_ATHEROGENIC_PARTICLE_BURDEN"
            risk_desc = "Excess of atherogenic ApoB particles (LDL, VLDL, IDL) over protective HDL particles."
        elif ratio > cutoff_opt:
            tier = "MODERATE_CARDIOVASCULAR_RISK"
            risk_desc = "Acceptable but suboptimal balance; plaque progression possible."
        else:
            tier = "LOWEST_RISK_OPTIMAL_LONGEVITY"
            risk_desc = "Elite protective profile: minimal atherogenic arterial retention risk."

        return {
            "apob_mg_dl": apob_mg_dl,
            "apoa1_mg_dl": apoa1_mg_dl,
            "apob_apoa1_ratio": ratio,
            "gender": gender,
            "atherogenic_risk_tier": tier,
            "clinical_assessment": risk_desc
        }

    @staticmethod
    def audit_ldl_apob_discordance(ldl_c_mg_dl: float, apob_mg_dl: float, triglycerides_mg_dl: float = 120.0) -> Dict[str, Any]:
        # Discordance: Low/normal LDL-C (< 100) with High ApoB (> 90) implies small, dense, particle-dense LDL
        is_discordant = (ldl_c_mg_dl < 110.0 and apob_mg_dl > 90.0) or (triglycerides_mg_dl > 150.0 and apob_mg_dl > 85.0)
        return {
            "ldl_c_mg_dl": ldl_c_mg_dl,
            "apob_mg_dl": apob_mg_dl,
            "triglycerides_mg_dl": triglycerides_mg_dl,
            "discordance_detected": is_discordant,
            "phenotype": "SMALL_DENSE_LDL_PARTICLE_SURPLUS (Pattern B)" if is_discordant else "CONCORDANT_LIPID_PROFILE",
            "clinical_advisory": "Treat ApoB target directly (< 70 mg/dL for primary prevention, < 55 mg/dL for high risk) rather than relying on LDL-C."
        }
