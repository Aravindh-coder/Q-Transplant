import math
from typing import Dict, List, Any, Optional
from backend.app.models.domain import Organ, Patient


class QuantumMatchingEngine:
    """
    Quantum-inspired multi-dimensional optimization for organ-recipient compatibility.
    """

    ABO_COMPATIBILITY: Dict[str, List[str]] = {
        "O-": ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"],
        "O+": ["O+", "A+", "B+", "AB+"],
        "A-": ["A-", "A+", "AB-", "AB+"],
        "A+": ["A+", "AB+"],
        "B-": ["B-", "B+", "AB-", "AB+"],
        "B+": ["B+", "AB+"],
        "AB-": ["AB-", "AB+"],
        "AB+": ["AB+"]
    }

    @classmethod
    def evaluate_abo_gate(cls, donor_blood: str, patient_blood: str) -> bool:
        allowed = cls.ABO_COMPATIBILITY.get(donor_blood, [])
        return patient_blood in allowed

    @classmethod
    def compute_hla_quantum_similarity(cls, hla_d: str, hla_p: str) -> float:
        d_loci = set([x.strip().upper() for x in hla_d.split(",") if x.strip()])
        p_loci = set([x.strip().upper() for x in hla_p.split(",") if x.strip()])

        if not d_loci or not p_loci:
            return 50.0

        intersection = d_loci.intersection(p_loci)
        union = d_loci.union(p_loci)
        similarity = (len(intersection) / len(union)) * 100.0
        return round(similarity, 2)

    @classmethod
    def compute_quantum_match(
        cls,
        organ: Organ,
        patient: Patient,
        distance_km: float = 15.0,
        icu_capacity_percent: float = 80.0
    ) -> Dict[str, Any]:
        """
        Computes Quantum-Inspired Match Vector with confidence score and rationale.
        Returns confidence_score=0 if organ type or ABO is incompatible.
        """
        # Organ type gate
        organ_type = getattr(organ, 'organ_type', '') or ''
        target_organ = getattr(patient, 'target_organ', '') or ''
        if organ_type.lower() != target_organ.lower():
            return {
                "confidence_score": 0.0,
                "is_viable": False,
                "rationale": f"Organ type mismatch: {organ_type} vs target {target_organ}"
            }

        # ABO gate
        if not cls.evaluate_abo_gate(organ.blood_type, patient.blood_type):
            return {
                "confidence_score": 0.0,
                "is_viable": False,
                "rationale": f"ABO Incompatible: Donor ({organ.blood_type}) vs Patient ({patient.blood_type})"
            }

        # HLA similarity (35%)
        hla_score = cls.compute_hla_quantum_similarity(organ.hla_type, patient.hla_type)

        # Urgency (25%)
        urgency_score = min(100.0, (getattr(patient, 'urgency_score', 5) or 5) * 10.0)

        # Ischemia preservation window decay (15%)
        max_hrs = getattr(organ, 'max_ischemia_hours', None) or 6.0
        estimated_transit_hrs = (distance_km / 50.0) + 0.5
        ischemia_decay = max(0.0, (1.0 - (estimated_transit_hrs / max_hrs))) * 100.0

        # Distance decay (15%)
        distance_score = max(0.0, 100.0 - (distance_km * 0.8))

        # ICU readiness (10%)
        icu_readiness_score = min(100.0, icu_capacity_percent)

        overall = (
            (hla_score * 0.35) +
            (urgency_score * 0.25) +
            (ischemia_decay * 0.15) +
            (distance_score * 0.15) +
            (icu_readiness_score * 0.10)
        )
        overall = round(min(100.0, max(0.0, overall)), 2)

        rationale = (
            f"Quantum Score {overall}% | HLA: {hla_score:.1f}% | "
            f"Urgency: {getattr(patient, 'urgency_score', 5)}/10 | "
            f"Transit: {estimated_transit_hrs:.1f}h/{max_hrs}h | "
            f"Distance: {distance_km}km | ICU: {icu_capacity_percent:.0f}%"
        )

        return {
            "confidence_score": overall,
            "is_viable": overall >= 40.0,
            "components": {
                "hla_score": hla_score,
                "urgency_score": urgency_score,
                "ischemia_decay": round(ischemia_decay, 2),
                "distance_score": round(distance_score, 2),
                "icu_readiness": round(icu_readiness_score, 2)
            },
            "rationale": rationale
        }
