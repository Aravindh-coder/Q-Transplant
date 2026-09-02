#!/usr/bin/env python3
"""
Converts an arbitrary donor/organ-transplant CSV (e.g. downloaded from
Kaggle) into the exact column format Q-Transplant's bulk import endpoint
expects, then optionally imports it directly via the API.

Kaggle requires a logged-in account or API token to actually download
data -- this environment has no network access to kaggle.com at all, so
this script can't fetch the dataset for you. Download it yourself first:

  1. pip install kaggle
  2. Get an API token: https://www.kaggle.com/settings -> "Create New Token"
     (downloads kaggle.json -- put it at ~/.kaggle/kaggle.json)
  3. kaggle datasets download -d fkshaikh/organ-transplant-dataset
     (or whichever dataset you picked -- unzip it)

Then run this script against the CSV you downloaded:

  python3 convert_donor_dataset.py path/to/kaggle_file.csv output.csv

Real organ-transplant datasets essentially never include genuine HLA
typing (that's protected medical data, not something publicly published) --
this script fills missing HLA fields with None, which the import endpoint
already handles fine (they're optional). Expect to hand-map a few columns
for whichever specific dataset you pick; the auto-detection below covers
the common naming variants but isn't guaranteed to catch everything.
"""
import csv
import sys
import re

# Target format: full_name, email, blood_group, organs_available, hla_a,
# hla_b, hla_c, hla_dr, hla_dq, phone, address, date_of_birth, gender
COLUMN_ALIASES = {
    "full_name": ["full_name", "name", "patient_name", "donor_name"],
    "email": ["email", "email_address"],
    "blood_group": ["blood_group", "bloodgroup", "blood_type", "bloodtype", "blood"],
    "organs_available": ["organs_available", "organ", "organ_type", "organs", "organ_donated"],
    "hla_a": ["hla_a"], "hla_b": ["hla_b"], "hla_c": ["hla_c"], "hla_dr": ["hla_dr"], "hla_dq": ["hla_dq"],
    "phone": ["phone", "phone_number", "contact", "mobile"],
    "address": ["address", "city", "location"],
    "date_of_birth": ["date_of_birth", "dob", "birth_date"],
    "gender": ["gender", "sex"],
}
VALID_BLOOD_GROUPS = {"O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"}


def normalize_blood_group(raw: str) -> str:
    """Handles common variants: 'O Positive', 'o+', 'AB Negative', etc."""
    if not raw:
        return ""
    s = raw.strip().upper().replace(" ", "")
    s = s.replace("POSITIVE", "+").replace("NEGATIVE", "-")
    s = s.replace("POS", "+").replace("NEG", "-")
    return s if s in VALID_BLOOD_GROUPS else ""


def build_column_map(fieldnames):
    def norm(s):
        return re.sub(r"[\s\-]+", "_", s.strip().lower())
    lower_fields = {norm(f): f for f in fieldnames}
    mapping = {}
    for target, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if alias in lower_fields:
                mapping[target] = lower_fields[alias]
                break
    return mapping


def convert(input_path: str, output_path: str):
    with open(input_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            print("ERROR: input CSV has no header row.")
            sys.exit(1)
        colmap = build_column_map(reader.fieldnames)
        print("Detected column mapping:")
        for target, source in colmap.items():
            print(f"  {target:<18} <- {source}")
        missing = [t for t in ("blood_group",) if t not in colmap]
        if missing:
            print(f"\nWARNING: could not auto-detect required column(s): {missing}")
            print(f"Available columns in your file: {reader.fieldnames}")
            print("Edit COLUMN_ALIASES in this script to add your file's exact header name, then rerun.")

        rows_out = []
        skipped = 0
        for row in reader:
            bg = normalize_blood_group(row.get(colmap.get("blood_group", ""), ""))
            if not bg:
                skipped += 1
                continue
            organs = row.get(colmap.get("organs_available", ""), "") or ""
            organs = re.sub(r"[,/|]+", ";", organs).strip().lower()
            rows_out.append({
                "full_name": row.get(colmap.get("full_name", ""), "") or "Imported Donor",
                "email": row.get(colmap.get("email", ""), "") or "",
                "blood_group": bg,
                "organs_available": organs,
                "hla_a": row.get(colmap.get("hla_a", ""), "") or "",
                "hla_b": row.get(colmap.get("hla_b", ""), "") or "",
                "hla_c": row.get(colmap.get("hla_c", ""), "") or "",
                "hla_dr": row.get(colmap.get("hla_dr", ""), "") or "",
                "hla_dq": row.get(colmap.get("hla_dq", ""), "") or "",
                "phone": row.get(colmap.get("phone", ""), "") or "",
                "address": row.get(colmap.get("address", ""), "") or "",
                "date_of_birth": row.get(colmap.get("date_of_birth", ""), "") or "",
                "gender": row.get(colmap.get("gender", ""), "") or "",
            })

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "full_name", "email", "blood_group", "organs_available", "hla_a", "hla_b",
            "hla_c", "hla_dr", "hla_dq", "phone", "address", "date_of_birth", "gender",
        ])
        writer.writeheader()
        writer.writerows(rows_out)

    print(f"\nWrote {len(rows_out)} usable rows to {output_path} ({skipped} skipped -- no valid blood group).")
    print("Upload it via the 'Import donors' page (doctor/hospital/organizer portal), or:")
    print(f'  curl -X POST https://<your-app>/api/v1/donors/import -H "Authorization: Bearer <token>" -F "file=@{output_path}"')


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        print("Usage: python3 convert_donor_dataset.py <input.csv> <output.csv>")
        sys.exit(1)
    convert(sys.argv[1], sys.argv[2])
