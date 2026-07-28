from backend.app.services.quantum_matching import QuantumMatchingEngine
from backend.app.models.domain import Organ, Patient


def test_abo_gate_pass():
    assert QuantumMatchingEngine.evaluate_abo_gate("O-", "AB+") is True
    assert QuantumMatchingEngine.evaluate_abo_gate("A+", "O-") is False


def test_hla_quantum_similarity_perfect():
    score = QuantumMatchingEngine.compute_hla_quantum_similarity("A2,B7,DR4", "A2,B7,DR4")
    assert score == 100.0


def test_hla_quantum_similarity_partial():
    score = QuantumMatchingEngine.compute_hla_quantum_similarity("A2,B7", "A2,B7,DR4")
    assert 0.0 < score < 100.0


def test_quantum_full_match_score():
    organ = Organ(organ_type="Heart", blood_type="O-", hla_type="A2,B7,DR4", max_ischemia_hours=4.0)
    patient = Patient(target_organ="Heart", blood_type="A+", hla_type="A2,B7,DR4", urgency_score=10)

    result = QuantumMatchingEngine.compute_quantum_match(organ, patient, distance_km=10.0, icu_capacity_percent=90.0)
    assert result["is_viable"] is True
    assert result["confidence_score"] > 75.0


def test_quantum_abo_incompatible_returns_zero():
    organ = Organ(organ_type="Kidney", blood_type="B+", hla_type="A2", max_ischemia_hours=24.0)
    patient = Patient(target_organ="Kidney", blood_type="O-", hla_type="A2", urgency_score=5)

    result = QuantumMatchingEngine.compute_quantum_match(organ, patient)
    assert result["confidence_score"] == 0.0
    assert result["is_viable"] is False


def test_quantum_organ_type_mismatch_returns_zero():
    organ = Organ(organ_type="Liver", blood_type="O+", hla_type="A2,B7", max_ischemia_hours=12.0)
    patient = Patient(target_organ="Heart", blood_type="O+", hla_type="A2,B7", urgency_score=9)

    # target_organ != organ_type means score = 0
    result = QuantumMatchingEngine.compute_quantum_match(organ, patient)
    assert result["confidence_score"] == 0.0
