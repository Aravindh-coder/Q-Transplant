"""Roadmap regression tests for deterministic engines and workflow guards.
Run with: pytest backend/backend/app/tests/test_roadmap_41.py
"""
import pytest
from app.services.compatibility import check_blood_compatibility, check_organ_compatibility
from app.services.hla import calculate_hla_match
from app.services.case_workflow import validate_transition
from app.services.emergency_state import transition
from app.services.urgency import calculate_priority

class Obj: pass

def obj(**kw):
 x=Obj()
 for k,v in kw.items(): setattr(x,k,v)
 return x

def test_blood_compatibility():
 assert check_blood_compatibility(obj(blood_group="O+"), obj(blood_group="A+")).get("compatible") is True
 assert check_blood_compatibility(obj(blood_group="A+"), obj(blood_group="O+")).get("compatible") is False

def test_hla_structured_result():
 d=obj(hla_a="A1,A2",hla_b="B7,B8",hla_c="C1,C2",hla_dr="DR1,DR2",hla_dq="DQ1,DQ2")
 r=obj(hla_a="A1,A3",hla_b="B7,B9",hla_c="C1,C3",hla_dr="DR1,DR3",hla_dq="DQ1,DQ3")
 result=calculate_hla_match(d,r)
 assert {"score","matched_markers","total_markers","details"} <= set(result)
 assert 0 <= result["score"] <= 100

def test_organ_compatibility():
 donor=obj(organs_available=["kidney"],availability_status="ACTIVE",medical_status="eligible")
 patient=obj(required_organ="kidney",medical_status="eligible")
 assert check_organ_compatibility(donor,patient)["compatible"] is True

def test_case_and_emergency_lifecycles():
 assert validate_transition("CREATED","MEDICAL_REVIEW") == "MEDICAL_REVIEW"
 assert transition("CREATED","NOTIFIED") == "NOTIFIED"
 with pytest.raises(ValueError): validate_transition("COMPLETED","CREATED")
 with pytest.raises(ValueError): transition("RESOLVED","ACKNOWLEDGED")

def test_urgency_is_transparent():
 result=calculate_priority("CRITICAL", waiting_days=30, compatibility_score=90, organ_available=True, hospital_ready=True)
 assert "score" in result and "factors" in result and "explanation" in result
 assert result["score"] >= 0
