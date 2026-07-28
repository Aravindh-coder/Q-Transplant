from typing import Optional, List
from sqlalchemy.orm import Session
from backend.app.models.domain import Organ, Match, Patient, Donor, Transport, Ambulance, OrganStatus, MatchStatus


class OrganRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_organ(self, donor_id: int, organ_type: str, blood_type: str, hla_type: str, max_ischemia_hours: float = 6.0, cold_box_id: str = "BOX-ESP32-001") -> Organ:
        organ = Organ(
            donor_id=donor_id,
            organ_type=organ_type,
            blood_type=blood_type,
            hla_type=hla_type,
            max_ischemia_hours=max_ischemia_hours,
            cold_box_id=cold_box_id,
            status=OrganStatus.AVAILABLE.value
        )
        self.db.add(organ)
        self.db.commit()
        self.db.refresh(organ)
        return organ

    def get_organ_by_id(self, organ_id: int) -> Optional[Organ]:
        return self.db.query(Organ).filter(Organ.id == organ_id).first()

    def list_available_organs(self) -> List[Organ]:
        return self.db.query(Organ).filter(Organ.status == OrganStatus.AVAILABLE.value).all()

    def list_all_patients(self) -> List[Patient]:
        return self.db.query(Patient).filter(Patient.status == "waiting_list").all()

    def create_match(self, organ_id: int, patient_id: int, compatibility_score: float, distance_km: float = 15.0) -> Match:
        match = Match(
            organ_id=organ_id,
            patient_id=patient_id,
            compatibility_score=compatibility_score,
            distance_km=distance_km,
            status=MatchStatus.PENDING.value
        )
        self.db.add(match)
        self.db.commit()
        self.db.refresh(match)
        return match

    def list_matches(self) -> List[Match]:
        return self.db.query(Match).all()

    def update_match_status(self, match_id: int, status: str) -> Optional[Match]:
        match = self.db.query(Match).filter(Match.id == match_id).first()
        if match:
            match.status = status
            self.db.commit()
            self.db.refresh(match)
        return match
