from backend.app.services.matching_service import MatchingService
from backend.app.models.domain import Organ, Patient


def test_abo_compatibility():
    assert MatchingService.is_abo_compatible("O-", "AB+") is True
    assert MatchingService.is_abo_compatible("A+", "O-") is False
    assert MatchingService.is_abo_compatible("B+", "AB+") is True


def test_hla_similarity():
    score = MatchingService.calculate_hla_similarity("A2,B7,DR4", "A2,B7,DR4")
    assert score == 100.0

    partial_score = MatchingService.calculate_hla_similarity("A2,B7", "A2,B7,DR4")
    assert partial_score > 0.0 and partial_score < 100.0


def test_compute_match_score():
    organ = Organ(organ_type="Heart", blood_type="O-", hla_type="A2,B7,DR4")
    patient = Patient(target_organ="Heart", blood_type="A+", hla_type="A2,B7,DR4", urgency_score=10)

    score = MatchingService.compute_match_score(organ, patient, distance_km=10.0)
    assert score > 80.0
