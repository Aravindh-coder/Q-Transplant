from typing import Dict, List, Tuple
from backend.app.models.domain import Organ, Patient


class MatchingService:
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
    def is_abo_compatible(cls, donor_blood: str, patient_blood: str) -> bool:
        allowed_recipients = cls.ABO_COMPATIBILITY.get(donor_blood, [])
        return patient_blood in allowed_recipients

    @classmethod
    def calculate_hla_similarity(cls, hla_donor: str, hla_patient: str) -> float:
        """Calculates HLA locus match percentage (A, B, DR loci)."""
        donor_loci = set([x.strip().upper() for x in hla_donor.split(",") if x.strip()])
        patient_loci = set([x.strip().upper() for x in hla_patient.split(",") if x.strip()])
        
        if not donor_loci or not patient_loci:
            return 50.0  # Default baseline if unmeasured
            
        intersection = donor_loci.intersection(patient_loci)
        union = donor_loci.union(patient_loci)
        
        jaccard_score = (len(intersection) / len(union)) * 100.0
        return round(jaccard_score, 2)

    @classmethod
    def compute_match_score(cls, organ: Organ, patient: Patient, distance_km: float = 15.0) -> float:
        """
        Computes organ-patient overall compatibility index (0 to 100%).
        Formulation:
        - ABO Compatible: Mandatory (0% if incompatible)
        - HLA Score Weight: 50%
        - Urgency Weight: 35% (urgency_score 1-10 -> 10-100)
        - Distance Decay Weight: 15% (deducts 1% per 10km)
        """
        if organ.organ_type.lower() != patient.target_organ.lower():
            return 0.0

        if not cls.is_abo_compatible(organ.blood_type, patient.blood_type):
            return 0.0

        hla_score = cls.calculate_hla_similarity(organ.hla_type, patient.hla_type)
        urgency_score_pct = min(100.0, patient.urgency_score * 10.0)
        
        distance_penalty = min(15.0, distance_km * 0.1)
        distance_score = max(0.0, 100.0 - distance_penalty)

        overall_score = (hla_score * 0.50) + (urgency_score_pct * 0.35) + (distance_score * 0.15)
        return round(overall_score, 2)
