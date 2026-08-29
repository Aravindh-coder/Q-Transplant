"""AI-assisted identity verification for doctor onboarding.

Compares a live selfie against the photo on a submitted license/medical
certificate and returns a structured, human-readable verdict. This is
assistive only: the result is surfaced to the organizer alongside the raw
images, never used to auto-approve or auto-reject a doctor. Matches the
platform's clinical-safety principle that AI supports human decisions and
never substitutes for one (see clinical_safety.py for the equivalent
pattern applied to transplant matching).

Two interchangeable providers are supported:
- Groq (GROQ_API_KEY) -- qwen/qwen3.6-27b, Groq's current vision-capable
  model. Groq itself flags this as a preview model, not their
  production-recommended tier, as of when this was written -- swap
  MODEL_GROQ below if that changes.
- Anthropic (ANTHROPIC_API_KEY) -- claude-sonnet-5

If GROQ_API_KEY is set, Groq is used (faster/cheaper for most accounts).
Otherwise ANTHROPIC_API_KEY is used if present. If neither is set, the
check is skipped and the organizer is told to review manually.
"""
import base64
import json
import logging
import os

logger = logging.getLogger("qtransplant.identity_verification")

MODEL_ANTHROPIC = "claude-sonnet-5"
MODEL_GROQ = "qwen/qwen3.6-27b"

_SYSTEM_PROMPT = (
    "You are assisting a human reviewer (never replacing them) who is "
    "verifying a doctor's identity during account registration. You will "
    "be shown two images: a live selfie and a photo from a submitted "
    "medical license/certificate. Judge only whether the two photos "
    "plausibly depict the same person -- image quality, angle, lighting, "
    "and age of the license photo can all cause honest mismatches, so "
    "stay calibrated and avoid false confidence in either direction. "
    "Respond with ONLY a JSON object, no other text, in exactly this "
    "shape: {\"same_person_likely\": true|false|null, \"confidence\": "
    "\"high\"|\"medium\"|\"low\", \"reasoning\": \"<one or two sentences>\"}. "
    "Use null for same_person_likely only if a face isn't clearly "
    "visible in one of the images."
)
_NOT_RUN = {
    "status": "not_run",
    "same_person_likely": None,
    "confidence": "unknown",
    "reasoning": "Automated identity verification is not configured (set GROQ_API_KEY or ANTHROPIC_API_KEY). An organizer must compare the two images manually.",
}
_ERROR = {
    "status": "error",
    "same_person_likely": None,
    "confidence": "unknown",
    "reasoning": "The automated check failed to run. An organizer must compare the two images manually.",
}


def _parse_verdict(text: str) -> dict:
    text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    parsed = json.loads(text)
    return {
        "status": "completed",
        "same_person_likely": parsed.get("same_person_likely"),
        "confidence": parsed.get("confidence", "unknown"),
        "reasoning": parsed.get("reasoning", ""),
    }


def _call_anthropic(api_key, live_bytes, live_media_type, id_bytes, id_media_type) -> dict:
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=MODEL_ANTHROPIC,
        max_tokens=400,
        system=_SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": "Live selfie:"},
                {"type": "image", "source": {"type": "base64", "media_type": live_media_type, "data": base64.b64encode(live_bytes).decode()}},
                {"type": "text", "text": "License/certificate photo:"},
                {"type": "image", "source": {"type": "base64", "media_type": id_media_type, "data": base64.b64encode(id_bytes).decode()}},
            ],
        }],
    )
    text = "".join(block.text for block in response.content if getattr(block, "type", None) == "text")
    return _parse_verdict(text)


def _call_groq(api_key, live_bytes, live_media_type, id_bytes, id_media_type) -> dict:
    from groq import Groq
    client = Groq(api_key=api_key)
    live_url = f"data:{live_media_type};base64,{base64.b64encode(live_bytes).decode()}"
    id_url = f"data:{id_media_type};base64,{base64.b64encode(id_bytes).decode()}"
    response = client.chat.completions.create(
        model=MODEL_GROQ,
        max_tokens=400,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": [
                {"type": "text", "text": "Live selfie:"},
                {"type": "image_url", "image_url": {"url": live_url}},
                {"type": "text", "text": "License/certificate photo:"},
                {"type": "image_url", "image_url": {"url": id_url}},
            ]},
        ],
    )
    return _parse_verdict(response.choices[0].message.content)


def verify_identity_photos(live_photo_bytes: bytes, live_photo_media_type: str,
                            id_photo_bytes: bytes, id_photo_media_type: str) -> dict:
    """Returns a dict with status/same_person_likely/confidence/reasoning.
    Never raises -- a failure here should never block document upload or
    registration; it just means the organizer sees 'not_run'/'error' and
    reviews the two images manually instead."""
    groq_key = os.environ.get("GROQ_API_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    if not (groq_key or anthropic_key):
        return dict(_NOT_RUN)
    try:
        if groq_key:
            return _call_groq(groq_key, live_photo_bytes, live_photo_media_type, id_photo_bytes, id_photo_media_type)
        return _call_anthropic(anthropic_key, live_photo_bytes, live_photo_media_type, id_photo_bytes, id_photo_media_type)
    except Exception:
        logger.exception("Identity verification call failed.")
        return dict(_ERROR)
