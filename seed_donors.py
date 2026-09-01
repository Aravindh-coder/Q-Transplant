import sys
import os
import random

# Ensure app path is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend', 'backend')))

from app.database import engine, Base, SessionLocal
from app.models import User, DonorProfile, DoctorProfile, HospitalProfile, Patient, uid
from app.security import hash_password

FIRST_NAMES = [
    "Aravindh", "Priya", "Rahul", "Ananya", "Rajesh", "Lakshmi", "Suresh", "Fatima",
    "Vikram", "Kavita", "Arjun", "Deepika", "Karthik", "Sneha", "Aditya", "Meera",
    "Rohan", "Pooja", "Sanjay", "Ritu", "Amit", "Nisha", "Vijay", "Divya",
    "Manish", "Swati", "Alok", "Aarti", "Gautam", "Neha", "Tarun", "Shweta",
    "Bhavya", "Dev", "Isha", "Karan", "Kirti", "Nikhil", "Payal", "Rishi",
    "Shalini", "Varun", "Vasundhara", "Yash", "Zoya", "Aakash", "Bhakti", "Chirag"
]

LAST_NAMES = [
    "Kumar", "Sharma", "Verma", "Patel", "Gupta", "Nair", "Reddy", "Sheikh",
    "Malhotra", "Joshi", "Singhal", "Iyer", "Rao", "Deshmukh", "Chowdhury", "Das",
    "Bhat", "Mehta", "Shah", "Kulkarni", "Banerjee", "Chatterjee", "Pillai", "Menon",
    "Trivedi", "Jha", "Mishra", "Pandey", "Saxena", "Srivastava", "Agarwal", "Bhasin"
]

BLOOD_GROUPS = ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"]
ORGANS = ["kidney", "liver", "heart", "lung", "pancreas", "intestine"]

HLA_A_ALLELES = ["*01", "*02", "*03", "*11", "*24", "*33", "*68"]
HLA_B_ALLELES = ["*07", "*08", "*15", "*27", "*35", "*40", "*44", "*51"]
HLA_C_ALLELES = ["*01", "*03", "*04", "*06", "*07", "*12", "*15"]
HLA_DR_ALLELES = ["*01", "*03", "*04", "*07", "*11", "*13", "*15"]
HLA_DQ_ALLELES = ["*02", "*03", "*05", "*06"]

CITIES = [
    ("Chennai", 13.0827, 80.2707),
    ("Mumbai", 19.0760, 72.8777),
    ("Delhi", 28.6139, 77.2090),
    ("Bengaluru", 12.9716, 77.5946),
    ("Hyderabad", 17.3850, 78.4867),
    ("Kolkata", 22.5726, 88.3639),
    ("Pune", 18.5204, 73.8567),
    ("Kochi", 9.9312, 76.2673)
]

def seed_database():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Check existing donor count
    existing_count = db.query(DonorProfile).count()
    if existing_count >= 1000:
        print(f"Database already contains {existing_count} donors. Skipping seed.")
        db.close()
        return

    print("Seeding organizer, hospital, doctor accounts...")
    
    # Organizer
    organizer_user = db.query(User).filter_by(email="admin@qtransplant.org").first()
    if not organizer_user:
        organizer_user = User(
            email="admin@qtransplant.org",
            hashed_password=hash_password("AdminPass123!"),
            role="organizer",
            full_name="Central Organizer Admin",
            status="active",
            email_verified=True
        )
        db.add(organizer_user)
        db.commit()

    # Hospital
    hosp_user = db.query(User).filter_by(email="apollo@qtransplant.org").first()
    if not hosp_user:
        hosp_user = User(
            email="apollo@qtransplant.org",
            hashed_password=hash_password("ApolloPass123!"),
            role="hospital",
            full_name="Apollo Central Hospital",
            status="active",
            email_verified=True
        )
        db.add(hosp_user)
        db.commit()

        hosp_profile = HospitalProfile(
            id="h1",
            user_id=hosp_user.id,
            hospital_name="Apollo Central Hospital",
            hospital_code="HOSP-CHN-001",
            phone="+91 44 2829 0200",
            address="Greams Road, Chennai, Tamil Nadu",
            location="Chennai, Tamil Nadu",
            registration_number="TN-HOSP-2024-0001",
            authorized_contact="Dr. Ramesh Iyer, Chief Administrator",
            verification_status="verified"
        )
        db.add(hosp_profile)
        db.commit()
    else:
        hosp_profile = db.query(HospitalProfile).filter_by(user_id=hosp_user.id).first()

    # Doctor
    doc_user = db.query(User).filter_by(email="dr.aravindh@qtransplant.org").first()
    if not doc_user:
        doc_user = User(
            email="dr.aravindh@qtransplant.org",
            hashed_password=hash_password("DoctorPass123!"),
            role="doctor",
            full_name="Dr. Aravindh S.",
            status="active",
            email_verified=True
        )
        db.add(doc_user)
        db.commit()

        doc_profile = DoctorProfile(
            user_id=doc_user.id,
            license_number="MCI-2024-88992",
            specialty="Transplant Surgery",
            hospital_id=hosp_profile.id if hosp_profile else "h1",
            approval_status="APPROVED",
            phone="+91 98765 43210",
            address="Greams Road, Chennai, Tamil Nadu",
            professional_information="15 years in solid-organ transplant surgery; fellowship-trained, MCI-registered."
        )
        db.add(doc_profile)
        db.commit()

    doc_profile = db.query(DoctorProfile).filter_by(user_id=doc_user.id).first()

    print("Generating 1,000 medical donor records...")
    random.seed(42)
    donor_password_hash = hash_password("DonorDefault123!")  # hashed once -- bcrypt is deliberately slow

    current_count = db.query(DonorProfile).count()
    target_total = 1000
    
    for i in range(current_count, target_total):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        name = f"{first} {last}"
        email = f"donor_{i + 1}_{first.lower()}.{last.lower()}@qdonor.org"
        
        u = User(
            email=email,
            hashed_password=donor_password_hash,
            role="donor",
            full_name=name,
            status="active",
            email_verified=True
        )
        db.add(u)
        db.flush()

        age = random.randint(19, 62)
        dob = f"{2026 - age}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        city, lat, lng = random.choice(CITIES)
        bg = random.choice(BLOOD_GROUPS)
        
        num_organs = random.choices([1, 2, 3], weights=[0.7, 0.2, 0.1])[0]
        assigned_organs = random.sample(ORGANS, k=num_organs)

        dp = DonorProfile(
            user_id=u.id,
            date_of_birth=dob,
            gender=random.choice(["Male", "Female"]),
            phone=f"+91 {random.randint(7000000000, 9999999999)}",
            address=f"Street {random.randint(1,100)}, {city}",
            blood_group=bg,
            organs_available=assigned_organs,
            hla_a=random.choice(HLA_A_ALLELES),
            hla_b=random.choice(HLA_B_ALLELES),
            hla_c=random.choice(HLA_C_ALLELES),
            hla_dr=random.choice(HLA_DR_ALLELES),
            hla_dq=random.choice(HLA_DQ_ALLELES),
            availability_status="active",
            hospital_id=hosp_profile.id if hosp_profile else "h1",
            verification_status="verified"
        )
        db.add(dp)

        if (i + 1) % 200 == 0:
            db.commit()

    db.commit()
    total = db.query(DonorProfile).count()
    print(f"Successfully seeded database with {total} donors!")

    print("Seeding demo patients (one per organ, for immediate matching demos)...")
    demo_patients = [
        {"full_name": "Kavya Subramaniam", "age": 41, "gender": "Female", "blood_group": "O+", "required_organ": "kidney", "urgency": "HIGH"},
        {"full_name": "Ibrahim Sheikh", "age": 55, "gender": "Male", "blood_group": "A+", "required_organ": "liver", "urgency": "CRITICAL"},
        {"full_name": "Rekha Nair", "age": 33, "gender": "Female", "blood_group": "B+", "required_organ": "heart", "urgency": "EMERGENCY"},
        {"full_name": "Sameer Khan", "age": 47, "gender": "Male", "blood_group": "AB+", "required_organ": "lung", "urgency": "HIGH"},
        {"full_name": "Devika Menon", "age": 29, "gender": "Female", "blood_group": "O-", "required_organ": "pancreas", "urgency": "MEDIUM"},
        {"full_name": "Arvind Chowdhury", "age": 38, "gender": "Male", "blood_group": "A-", "required_organ": "intestine", "urgency": "MEDIUM"},
    ]
    for p in demo_patients:
        exists = db.query(Patient).filter_by(full_name=p["full_name"], hospital_id=hosp_profile.id).first()
        if exists:
            continue
        db.add(Patient(
            hospital_id=hosp_profile.id if hosp_profile else "h1",
            doctor_id=doc_profile.id,
            full_name=p["full_name"], age=p["age"], gender=p["gender"],
            blood_group=p["blood_group"], required_organ=p["required_organ"], urgency=p["urgency"],
            hla_a=random.choice(HLA_A_ALLELES), hla_b=random.choice(HLA_B_ALLELES),
            hla_c=random.choice(HLA_C_ALLELES), hla_dr=random.choice(HLA_DR_ALLELES), hla_dq=random.choice(HLA_DQ_ALLELES),
        ))
    db.commit()
    print(f"Seeded {len(demo_patients)} demo patients -- log in as dr.aravindh@qtransplant.org / DoctorPass123! and run a match on any of them.")
    db.close()

if __name__ == "__main__":
    seed_database()
