"""AI-assisted identity verification for doctor onboarding.

Compares a live selfie against the photo on a submitted license/medical
certificate and returns a structured, human-readable verdict. This is
assistive only: the result is surfaced to the organizer alongside the raw
images, never used to auto-approve or auto-reject a doctor. Matches the
platform's clinical-safety principle that AI supports human decisions and
never substitutes for one (see clinical_safety.py for the equivalent
pattern applied to transplant matching).
"""
import base64
import json
import logging
import os

logger = logging.getLogger("qtransplant.identity_verification")

MODEL = "claude-sonnet-5"
_NOT_RUN = {
    "status": "not_run",
    "same_person_likely": None,
    "confidence": "unknown",
    "reasoning": "Automated identity verification is not configured (ANTHROPIC_API_KEY is unset). An organizer must compare the two images manually.",
}


def verify_identity_photos(live_photo_bytes: bytes, live_photo_media_type: str,
                            id_photo_bytes: bytes, id_photo_media_type: str) -> dict:
    """Returns a dict with status/same_person_likely/confidence/reasoning.
    Never raises — a failure here should never block document upload or
    registration; it just means the organizer sees 'not_run' and reviews
    the two images manually instead."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return dict(_NOT_RUN)
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=MODEL,
            max_tokens=400,
            system=(
                "You are assisting a human reviewer (never replacing them) who is "
                "verifying a doctor's identity during account registration. You will "
                "be shown two images: a live selfie and a photo from a submitted "
                "medical license/certificate. Judge only whether the two photos "
                "plausibly depict the same person — image quality, angle, lighting, "
                "and age of the license photo can all cause honest mismatches, so "
                "stay calibrated and avoid false confidence in either direction. "
                "Respond with ONLY a JSON object, no other text, in exactly this "
                "shape: {\"same_person_likely\": true|false|null, \"confidence\": "
                "\"high\"|\"medium\"|\"low\", \"reasoning\": \"<one or two sentences>\"}. "
                "Use null for same_person_likely only if a face isn't clearly "
                "visible in one of the images."
            ),
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": "Live selfie:"},
                    {"type": "image", "source": {"type": "base64", "media_type": live_photo_media_type, "data": base64.b64encode(live_photo_bytes).decode()}},
                    {"type": "text", "text": "License/certificate photo:"},
                    {"type": "image", "source": {"type": "base64", "media_type": id_photo_media_type, "data": base64.b64encode(id_photo_bytes).decode()}},
                ],
            }],
        )
        text = "".join(block.text for block in response.content if getattr(block, "type", None) == "text").strip()
        text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        parsed = json.loads(text)
        return {
            "status": "completed",
            "same_person_likely": parsed.get("same_person_likely"),
            "confidence": parsed.get("confidence", "unknown"),
            "reasoning": parsed.get("reasoning", ""),
        }
    except Exception:
        logger.exception("Identity verification call failed.")
        return {
            "status": "error",
            "same_person_likely": None,
            "confidence": "unknown",
            "reasoning": "The automated check failed to run. An organizer must compare the two images manually.",
        }
