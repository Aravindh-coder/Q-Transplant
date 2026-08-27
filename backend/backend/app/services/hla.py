"""
HLA compatibility scoring.
Structured, documented, and configurable — never a black-box single number
with no way to see what drove it. This is a decision-support score, not an
independent clinical decision.
"""

HLA_FIELDS = ["hla_a", "hla_b", "hla_c", "hla_dr", "hla_dq"]

# Relative clinical weight per locus for the overall score. Configurable —
# adjust per your medical advisor's guidance; document any change here.
LOCUS_WEIGHTS = {
    "hla_a": 1.0,
    "hla_b": 1.0,
    "hla_c": 0.8,
    "hla_dr": 1.4,   # HLA-DR mismatches carry the strongest rejection signal
    "hla_dq": 1.0,
}


def calculate_hla_match(donor: dict, recipient: dict) -> dict:
    """
    calculate_hla_match(donor, recipient) -> structured result, e.g.:
    {
      "score": 82,
      "matched_markers": 10,
      "total_markers": 12,
      "details": {"hla_a": {"donor": "...", "recipient": "...", "match": true}, ...}
    }
    donor/recipient are dicts with keys from HLA_FIELDS (each value can hold
    up to two alleles, comma-separated, e.g. "A2,A24" — unset fields are
    skipped rather than counted as a mismatch, since not every lab panel
    types every locus).
    """
    details = {}
    weighted_matched = 0.0
    weighted_total = 0.0
    matched_markers = 0
    total_markers = 0

    for field in HLA_FIELDS:
        d_val = (donor.get(field) or "").strip()
        r_val = (recipient.get(field) or "").strip()
        if not d_val or not r_val:
            continue  # locus not typed on one side — excluded, not penalized

        d_alleles = {a.strip().upper() for a in d_val.split(",") if a.strip()}
        r_alleles = {a.strip().upper() for a in r_val.split(",") if a.strip()}
        overlap = d_alleles & r_alleles
        locus_total = max(len(d_alleles), len(r_alleles), 1)
        locus_matched = len(overlap)

        weight = LOCUS_WEIGHTS.get(field, 1.0)
        weighted_matched += locus_matched * weight
        weighted_total += locus_total * weight
        matched_markers += locus_matched
        total_markers += locus_total

        details[field] = {
            "donor": sorted(d_alleles), "recipient": sorted(r_alleles),
            "matched": sorted(overlap), "match": locus_matched == locus_total,
        }

    if weighted_total == 0:
        return {"score": 0, "matched_markers": 0, "total_markers": 0, "details": details,
                "note": "No HLA data typed on both sides — score not computable."}

    score = round((weighted_matched / weighted_total) * 100)
    return {"score": score, "matched_markers": matched_markers, "total_markers": total_markers, "details": details}
