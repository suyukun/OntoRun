"""Output sanitization: LLM raw text redaction + PII pass-through-encrypted guard."""

import re

# Patterns for secret-shaped or prompt-leak-shaped substrings.
_REDACTIONS = [
    (re.compile(r"sk-[A-Za-z0-9_\-]{6,}"), "[REDACTED-KEY]"),
    (re.compile(r"(?i)(api[_-]?key|secret|token|password|authorization)\s*[:=]\s*\S+"), r"\1=[REDACTED]"),
    (re.compile(r"\b[0-9a-fA-F]{32,}\b"), "[REDACTED-HEX]"),
    (re.compile(r"(?i)(system\s*prompt|系统提示词)\s*[:：].*"), "[REDACTED-PROMPT]"),
]

# Encrypted-state values look like enc(aes)::phone:<hex> (see build_sample.fake_aes).
ENC_PREFIX_RE = re.compile(r"^enc\([A-Za-z0-9]+\)::")
PII_MASK = "***MASKED***"


def sanitize_llm_text(text: str) -> str:
    """Redact secret/prompt-shaped strings before raw LLM output enters any trace
    or detail panel (product doc §六 安全: 展示前脱敏)."""
    out = text
    for pattern, replacement in _REDACTIONS:
        out = pattern.sub(replacement, out)
    return out


def apply_pii_policy(rows: list, sensitive_fields: list) -> list:
    """Field-level PII hook: sensitive columns may only leave in encrypted state.
    Encrypted values pass through unchanged; anything else is masked (fail-closed).
    Mutates and returns rows (rows are freshly built per query, never shared)."""
    for row in rows:
        for field in sensitive_fields:
            val = row.get(field)
            if val is not None and not ENC_PREFIX_RE.match(str(val)):
                row[field] = PII_MASK
    return rows
