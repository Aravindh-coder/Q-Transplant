import pytest
from app.services.compatibility import check_blood_compatibility, check_organ_compatibility
from app.services.hla import calculate_hla_match
from app.services.matching.engine import evaluate, run_matching
from app.services.urgency import calculate_recipient_priority
from app.services.emergency_state import transition


def test_blood_rules_are_deterministic():
    assert check_blood_compatibility("O-", "AB+")["compatible"] is True
    assert check_blood_compatibility("A+", "B+")["compatible"] is False


def test_organ_compatibility_requires_all_gates():
    assert check_organ_compatibility("kidney", "kidney", True, True)["compatible"] is True
    assert check_organ_compatibility("kidney", "liver", True, True)["compatible"] is False
    assert check_organ_compatibility("kidney", "kidney", False, True)["compatible"] is False


def test_hla_returns_structured_result():
    d = {"hla_a":"A1,A2", "hla_b":"B7,B8", "hla_dr":"DR1,DR2"}
    r = {"hla_a":"A1,A2", "hla_b":"B7,B9", "hla_dr":"DR1,DR3"}
    result = calculate_hla_match(d, r)
    assert 0 <= result["score"] <= 100
    assert "matched_markers" in result and "total_markers" in result
    assert "details" in result


def test_matching_never_returns_blood_incompatible_candidate():
    donor = {"id": 1, "blood_group":"A+", "organ":"kidney", "availability_status":"ACTIVE"}
    recipient = {"id": 2, "blood_group":"B+", "required_organ":"kidney", "urgency":"CRITICAL", "medical_eligible":True}
    assert evaluate(donor, recipient) is None


def test_matching_returns_ranked_multiple_candidates():
    recipient = {"id": 9, "blood_group":"O+", "required_organ":"kidney", "urgency":"HIGH", "medical_eligible":True}
    donors = [
        {"id":1,"blood_group":"O+","organ":"kidney","availability_status":"ACTIVE","hla_a":"A1"},
        {"id":2,"blood_group":"O+","organ":"kidney","availability_status":"ACTIVE","hla_a":"A2"},
    ]
    result = run_matching(donors, recipient, top_n=2)
    assert result["candidates_evaluated"] == 2
    assert len(result["matches"]) <= 2
    assert all("explanation" in x for x in result["matches"])


def test_urgency_is_transparent():
    result = calculate_recipient_priority({"urgency":"EMERGENCY"}, True)
    assert result["score"] >= 0
    assert result["factors"]


def test_emergency_lifecycle():
    state = "CREATED"
    for new in ("NOTIFIED", "ACKNOWLEDGED", "PROCESSING", "RESOLVED"):
        state = transition(state, new)
    assert state == "RESOLVED"


def test_invalid_emergency_transition_rejected():
    with pytest.raises(ValueError):
        transition("CREATED", "RESOLVED")
