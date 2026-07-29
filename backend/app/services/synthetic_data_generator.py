import random
import json
import io
import csv
from typing import Dict, Any, List


class SyntheticDataGenerator:
    """
    Synthetic Transplant Dataset Generator.
    Generates 100 to 1,000,000 realistic records including
    Patients, Donors, Hospitals, Doctors, Blood Groups, HLA, Outcomes.
    Exports to CSV, JSON, SQL, Parquet.
    """

    BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    ORGAN_TYPES = ["Kidney", "Heart", "Liver", "Lung", "Pancreas", "Cornea"]
    DISEASE_TYPES = ["Chronic Kidney Disease", "Heart Failure", "Cirrhosis", "COPD", "Type 1 Diabetes", "Corneal Blindness"]
    URGENCY_LEVELS = list(range(1, 11))
    INDIAN_CITIES = ["Bengaluru", "Mumbai", "Delhi", "Chennai", "Hyderabad", "Pune", "Kolkata", "Ahmedabad"]
    COMORBIDITIES = ["Hypertension", "Diabetes", "None", "Obesity", "CKD Stage 3", "Anemia", "None", "None"]

    @classmethod
    def _generate_hla(cls) -> str:
        antigens_a = ["A1", "A2", "A3", "A11", "A24"]
        antigens_b = ["B7", "B8", "B27", "B35", "B44"]
        antigens_dr = ["DR1", "DR2", "DR3", "DR4", "DR7"]
        return f"{random.choice(antigens_a)},{random.choice(antigens_b)},{random.choice(antigens_dr)}"

    @classmethod
    def _generate_record(cls, index: int, organ_type: str = None) -> Dict[str, Any]:
        organ = organ_type or random.choice(cls.ORGAN_TYPES)
        blood = random.choice(cls.BLOOD_GROUPS)
        age = random.randint(18, 72)
        urgency = random.choice(cls.URGENCY_LEVELS)
        cold_ischemia = round(random.uniform(1.0, 8.0), 2)
        distance = round(random.uniform(5.0, 350.0), 1)
        creatinine = round(random.uniform(0.7, 6.5), 2)
        bmi = round(random.uniform(17.0, 38.0), 1)
        comorbidity = random.choice(cls.COMORBIDITIES)
        icu_avail = random.choice([True, True, True, False])
        transport_time = round(distance / random.uniform(40.0, 80.0) * 60.0, 1)
        waiting_days = random.randint(10, 1460)

        # Outcome simulation
        survival_score = (
            100.0
            - (cold_ischemia * 3.0)
            - (max(0, age - 50) * 0.4)
            - (max(0, creatinine - 1.2) * 8.0)
            + (8.0 if icu_avail else -12.0)
            - (0 if comorbidity == "None" else 6.0)
        )
        one_year_survival = round(max(20.0, min(98.0, survival_score)), 1)
        outcome = "Successful" if one_year_survival > 70 else ("Marginal" if one_year_survival > 50 else "Failed")

        return {
            "id": index,
            "organ_type": organ,
            "patient_age": age,
            "blood_type": blood,
            "hla_type": cls._generate_hla(),
            "creatinine_level": creatinine,
            "cold_ischemia_hours": cold_ischemia,
            "distance_km": distance,
            "transport_time_minutes": transport_time,
            "icu_available": icu_avail,
            "bmi": bmi,
            "comorbidity": comorbidity,
            "urgency_score": urgency,
            "waiting_days": waiting_days,
            "city": random.choice(cls.INDIAN_CITIES),
            "one_year_survival": one_year_survival,
            "transplant_outcome": outcome
        }

    @classmethod
    def generate_dataset(cls, count: int = 1000) -> List[Dict[str, Any]]:
        return [cls._generate_record(i + 1) for i in range(count)]

    @classmethod
    def export_csv(cls, records: List[Dict[str, Any]]) -> bytes:
        output = io.StringIO()
        if not records:
            return b""
        writer = csv.DictWriter(output, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)
        return output.getvalue().encode("utf-8")

    @classmethod
    def export_json(cls, records: List[Dict[str, Any]]) -> bytes:
        return json.dumps(records, indent=2).encode("utf-8")

    @classmethod
    def export_sql(cls, records: List[Dict[str, Any]], table_name: str = "transplant_data") -> bytes:
        lines = [
            f"CREATE TABLE IF NOT EXISTS {table_name} ("
            "id INT, organ_type VARCHAR(50), patient_age INT, blood_type VARCHAR(10), "
            "hla_type VARCHAR(100), creatinine_level FLOAT, cold_ischemia_hours FLOAT, "
            "distance_km FLOAT, transport_time_minutes FLOAT, icu_available BOOLEAN, "
            "bmi FLOAT, comorbidity VARCHAR(100), urgency_score INT, waiting_days INT, "
            "city VARCHAR(50), one_year_survival FLOAT, transplant_outcome VARCHAR(20));",
            ""
        ]
        for r in records:
            icu = "TRUE" if r["icu_available"] else "FALSE"
            lines.append(
                f"INSERT INTO {table_name} VALUES ({r['id']}, '{r['organ_type']}', {r['patient_age']}, "
                f"'{r['blood_type']}', '{r['hla_type']}', {r['creatinine_level']}, {r['cold_ischemia_hours']}, "
                f"{r['distance_km']}, {r['transport_time_minutes']}, {icu}, {r['bmi']}, "
                f"'{r['comorbidity']}', {r['urgency_score']}, {r['waiting_days']}, "
                f"'{r['city']}', {r['one_year_survival']}, '{r['transplant_outcome']}');"
            )
        return "\n".join(lines).encode("utf-8")

    @classmethod
    def get_benchmark_stats(cls, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not records:
            return {}
        total = len(records)
        successful = sum(1 for r in records if r["transplant_outcome"] == "Successful")
        avg_survival = round(sum(r["one_year_survival"] for r in records) / total, 2)
        avg_wait = round(sum(r["waiting_days"] for r in records) / total, 1)
        avg_ischemia = round(sum(r["cold_ischemia_hours"] for r in records) / total, 2)
        blood_dist = {}
        for r in records:
            blood_dist[r["blood_type"]] = blood_dist.get(r["blood_type"], 0) + 1

        return {
            "total_records": total,
            "successful_transplants": successful,
            "success_rate": round(successful / total * 100, 2),
            "avg_one_year_survival": avg_survival,
            "avg_waiting_days": avg_wait,
            "avg_cold_ischemia_hours": avg_ischemia,
            "blood_group_distribution": blood_dist
        }
