import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend', 'backend')))

from app.database import SessionLocal
from app.models import DonorProfile, User
from app.services.quantum.grover_sim import simulate_grover_steps
from app.services.hla import calculate_hla_match

def test_donor_count():
    db = SessionLocal()
    count = db.query(DonorProfile).count()
    db.close()
    assert count >= 1000, f"Expected at least 1000 donors in DB, found {count}"
    print(f"✅ PASS: Donor count in database = {count}")

def test_hla_match():
    donor_hla = {"hla_a": "*02", "hla_b": "*07", "hla_c": "*01", "hla_dr": "*01", "hla_dq": "*02"}
    patient_hla = {"hla_a": "*02", "hla_b": "*07", "hla_c": "*01", "hla_dr": "*04", "hla_dq": "*02"}
    res = calculate_hla_match(donor_hla, patient_hla)
    assert res["score"] > 50.0
    print(f"✅ PASS: HLA Match score calculated = {res['score']}% (Matched {res['matched_markers']} markers)")

def test_grover_simulation():
    steps = simulate_grover_steps(n_candidates=64, target_index=5)
    assert len(steps) > 1
    # Check that amplitude of target increases after diffusion
    initial_prob = steps[0]["target_probability"]
    final_prob = steps[-1]["target_probability"]
    assert final_prob > initial_prob, f"Target probability should increase: {initial_prob} -> {final_prob}"
    print(f"✅ PASS: Grover simulation amplified target state probability from {initial_prob:.4f} to {final_prob:.4f}")

if __name__ == "__main__":
    print("Running Q-Transplant System Tests...")
    test_donor_count()
    test_hla_match()
    test_grover_simulation()
    print("🎉 ALL TESTS PASSED SUCCESSFULLY!")
