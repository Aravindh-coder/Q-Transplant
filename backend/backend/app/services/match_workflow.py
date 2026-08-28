"""Orchestration contract for match requests; expensive work can be queued by callers."""
PIPELINE=("patient","organ_filter","eligibility","blood","hla","medical_compatibility","urgency","availability","ranking","ai_assistance","quantum_comparison","doctor_review","hospital_coordination")

def workflow_plan():
 return {"pipeline":list(PIPELINE),"backend_authoritative":True,"multiple_candidates":True}
