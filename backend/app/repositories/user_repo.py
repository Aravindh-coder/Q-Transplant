from typing import Optional, List
from sqlalchemy.orm import Session
from backend.app.models.domain import User, Hospital, Doctor, Donor, Patient, Approval


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email.lower()).first()

    def create_user(
        self,
        email: str,
        password_hash: str,
        full_name: str,
        role: str,
        phone: Optional[str] = None,
        is_approved: bool = False
    ) -> User:
        user = User(
            email=email.lower(),
            password_hash=password_hash,
            full_name=full_name,
            role=role,
            phone=phone,
            is_active=True,
            is_approved=is_approved
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_approval(self, user_id: int, is_approved: bool) -> Optional[User]:
        user = self.get_by_id(user_id)
        if user:
            user.is_approved = is_approved
            self.db.commit()
            self.db.refresh(user)
        return user

    def list_users(self, role: Optional[str] = None, approved_only: Optional[bool] = None) -> List[User]:
        query = self.db.query(User)
        if role:
            query = query.filter(User.role == role)
        if approved_only is not None:
            query = query.filter(User.is_approved == approved_only)
        return query.all()

    def create_hospital_profile(self, user_id: int, name: str, license_number: str, city: str, state: str, address: str, contact_phone: str) -> Hospital:
        hospital = Hospital(
            user_id=user_id,
            name=name,
            license_number=license_number,
            city=city,
            state=state,
            address=address,
            contact_phone=contact_phone
        )
        self.db.add(hospital)
        self.db.commit()
        self.db.refresh(hospital)
        return hospital

    def create_doctor_profile(self, user_id: int, medical_license: str, specialization: str, department: str, phone: str, hospital_id: Optional[int] = None) -> Doctor:
        doctor = Doctor(
            user_id=user_id,
            medical_license=medical_license,
            specialization=specialization,
            department=department,
            phone=phone,
            hospital_id=hospital_id
        )
        self.db.add(doctor)
        self.db.commit()
        self.db.refresh(doctor)
        return doctor

    def create_donor_profile(self, user_id: int, blood_type: str, hla_type: str, age: int, gender: str, medical_history: Optional[str] = None) -> Donor:
        donor = Donor(
            user_id=user_id,
            blood_type=blood_type,
            hla_type=hla_type,
            age=age,
            gender=gender,
            medical_history=medical_history
        )
        self.db.add(donor)
        self.db.commit()
        self.db.refresh(donor)
        return donor

    def create_patient_profile(self, user_id: int, blood_type: str, hla_type: str, target_organ: str, urgency_score: int = 5) -> Patient:
        patient = Patient(
            user_id=user_id,
            blood_type=blood_type,
            hla_type=hla_type,
            target_organ=target_organ,
            urgency_score=urgency_score
        )
        self.db.add(patient)
        self.db.commit()
        self.db.refresh(patient)
        return patient
