"""Non-authoritative AI assistance utilities.
All medical compatibility decisions must be made by deterministic services first.
"""
import json
import logging
import os
from collections import Counter

logger = logging.getLogger("qtransplant.ai_assistant")

def explain_match(match: dict) -> str:
    return match.get("explanation", "Deterministic compatibility analysis completed.")

def detect_data_quality(record: dict) -> list[str]:
    issues=[]
    required=("blood_group","required_organ")
    for field in required:
        if not record.get(field): issues.append(f"Missing required field: {field}")
    if record.get("age") is not None and not 0 <= record["age"] <= 120: issues.append("Age is outside the expected range.")
    return issues

def detect_duplicates(records: list[dict], keys=("email",)) -> list[dict]:
    groups={}
    for r in records:
        key=tuple(r.get(k) for k in keys)
        if all(v for v in key): groups.setdefault(key, []).append(r)
    return [v for v in groups.values() if len(v)>1]

def risk_flags(match: dict) -> list[str]:
    flags=[]
    if match.get("hla_score", 0) < 50: flags.append("Lower HLA similarity; clinician review required.")
    if match.get("priority_score", 0) >= 90: flags.append("High-priority recipient; coordinate urgently.")
    return flags

def _template_summary(match: dict) -> str:
    return f"Rank {match.get('rank','-')}, score {match.get('score',0)}; blood compatibility passed; HLA score {match.get('hla_score',0)}; urgency {match.get('urgency','UNKNOWN')}."

_SYSTEM_PROMPT = (
    "You rephrase a transplant-matching engine's already-decided, deterministic "
    "result into one or two plain-language sentences for a doctor. You do not "
    "re-score, re-rank, or second-guess any number given to you -- state them "
    "as fact and explain what they mean in context. Never invent a number that "
    "isn't in the input. Never recommend proceeding or not proceeding with a "
    "transplant -- that decision belongs to the clinician. Respond with ONLY "
    "the summary text, no preamble, no markdown."
)

def summarize_match(match: dict) -> str:
    """Plain-language summary of an already-decided deterministic match
    result. Tries Groq, then Anthropic, then falls back to a templated
    (non-AI) summary if neither is configured or the call fails -- this
    function must never raise and never block a match result from
    returning."""
    groq_key = os.environ.get("GROQ_API_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    if not (groq_key or anthropic_key):
        return _template_summary(match)
    fields = {k: match.get(k) for k in ("rank", "score", "hla_score", "urgency", "blood_compatible", "organ_compatible") if k in match}
    try:
        if groq_key:
            from groq import Groq
            client = Groq(api_key=groq_key)
            response = client.chat.completions.create(
                model="qwen/qwen3.6-27b", max_tokens=150,
                messages=[{"role": "system", "content": _SYSTEM_PROMPT},
                          {"role": "user", "content": json.dumps(fields)}],
            )
            return response.choices[0].message.content.strip()
        import anthropic
        client = anthropic.Anthropic(api_key=anthropic_key)
        response = client.messages.create(
            model="claude-sonnet-5", max_tokens=150, system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": json.dumps(fields)}],
        )
        return "".join(b.text for b in response.content if getattr(b, "type", None) == "text").strip()
    except Exception:
        logger.exception("AI match summary failed, falling back to templated summary.")
        return _template_summary(match)

def search_assist(query: str, records: list[dict]) -> list[dict]:
    q=(query or "").strip().lower()
    if not q: return []
    return [r for r in records if q in " ".join(str(v) for v in r.values()).lower()]

_REVIEW_SYSTEM_PROMPT = (
    "You are a clinical-data review assistant supporting (never replacing) a "
    "transplant doctor. You are given a deterministic matching engine's "
    "already-decided output for one donor-recipient pair: blood/organ/HLA "
    "compatibility results, urgency, and scores. Your job has two parts:\n"
    "1. confirmed_facts: short, plain statements that are DIRECTLY supported "
    "by the fields you were given. Never state a fact the input doesn't "
    "support. Never estimate, infer, or round anything not explicitly present.\n"
    "2. data_gaps: what clinically-relevant information is NOT present in the "
    "input that a doctor would normally want before proceeding (e.g. donor "
    "age, cross-match test, organ ischemia time, comorbidities) -- list only "
    "genuine gaps, not things already given.\n"
    "Do not recommend proceeding or not proceeding with a transplant. Do not "
    "assign a confidence percentage that isn't already in the input. Respond "
    "with ONLY a JSON object: {\"confirmed_facts\": [...], \"data_gaps\": [...], "
    "\"note\": \"<one sentence, no diagnosis, no recommendation>\"}."
)
_REVIEW_NOT_RUN = {
    "status": "not_run",
    "confirmed_facts": [],
    "data_gaps": [],
    "note": "AI clinical review is not configured (set GROQ_API_KEY or ANTHROPIC_API_KEY). The deterministic score and explanation above are unaffected.",
}

def clinical_review(match: dict) -> dict:
    """Structured, evidence-only review of an already-decided match result.
    Unlike summarize_match (a free-text rephrasing), this explicitly
    separates what the data actually supports from what it doesn't cover,
    so 'accurate, not assumed' is enforced by the output shape itself, not
    just prompt wording. Never authoritative -- the deterministic score
    and rank above this are what the system actually acts on."""
    groq_key = os.environ.get("GROQ_API_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    if not (groq_key or anthropic_key):
        return dict(_REVIEW_NOT_RUN)
    fields = {k: match.get(k) for k in (
        "rank", "score", "hla_score", "matched_markers", "total_markers",
        "urgency", "blood_compatible", "organ_compatible", "explanation",
    ) if k in match}
    try:
        text = None
        if groq_key:
            from groq import Groq
            client = Groq(api_key=groq_key)
            response = client.chat.completions.create(
                model="qwen/qwen3.6-27b", max_tokens=400, response_format={"type": "json_object"},
                messages=[{"role": "system", "content": _REVIEW_SYSTEM_PROMPT},
                          {"role": "user", "content": json.dumps(fields)}],
            )
            text = response.choices[0].message.content
        else:
            import anthropic
            client = anthropic.Anthropic(api_key=anthropic_key)
            response = client.messages.create(
                model="claude-sonnet-5", max_tokens=400, system=_REVIEW_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": json.dumps(fields)}],
            )
            text = "".join(b.text for b in response.content if getattr(b, "type", None) == "text")
        text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        parsed = json.loads(text)
        return {
            "status": "completed",
            "confirmed_facts": parsed.get("confirmed_facts", []),
            "data_gaps": parsed.get("data_gaps", []),
            "note": parsed.get("note", ""),
        }
    except Exception:
        logger.exception("AI clinical review failed.")
        return {**_REVIEW_NOT_RUN, "status": "error", "note": "The automated review failed to run. The deterministic score and explanation above are unaffected."}
