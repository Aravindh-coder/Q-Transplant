"""Structured HLA matching adapter."""
from app.services.hla import calculate_hla_match

def check_hla(donor: dict, recipient: dict) -> dict:
    return calculate_hla_match(donor, recipient)
