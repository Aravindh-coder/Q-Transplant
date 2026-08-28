"""Minimum-necessary access policy helpers."""
ROLE_ACCESS={
 "donor":{"own_profile","own_status","own_notifications"},
 "doctor":{"authorized_patients","authorized_donors","matching","own_cases","emergency"},
 "hospital":{"hospital_patients","hospital_donors","hospital_cases","matching","emergency"},
 "organizer":{"operational_records","approvals","audit","devices","matching","emergency"},
}
def can_access(role, resource):
 return resource in ROLE_ACCESS.get(role, set())
