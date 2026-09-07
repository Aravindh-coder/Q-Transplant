"""Safe application observability: never log credentials or medical payloads."""
import logging
import time

logger = logging.getLogger("qtransplant")

def configure_logging():
    if not logger.handlers:
        logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

def safe_event(event, **fields):
    forbidden_substrings = ("password", "otp", "token", "jwt", "medical", "hla", "blood_group", "address", "phone")
    clean = {k: v for k, v in fields.items() if not any(f in k.lower() for f in forbidden_substrings)}
    logger.info("event=%s %s", event, clean)

def elapsed(start):
    return round((time.perf_counter() - start) * 1000, 2)
