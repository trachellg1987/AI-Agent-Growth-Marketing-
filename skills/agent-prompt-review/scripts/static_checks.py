"""Static (no-model) checks for a B2B marketing agent prompt.

Each check is a plain regex rule so results are repeatable and explainable.
A check either PASSES or is FLAGGED with a reason. These checks catch common,
obvious gaps; they do not replace a human or legal/compliance review.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class Check:
    name: str
    passed: bool
    detail: str


def _has(pattern: str, text: str) -> bool:
    return re.search(pattern, text, re.IGNORECASE | re.MULTILINE) is not None


def _find(pattern: str, text: str) -> list[str]:
    return sorted({m.group(0).strip() for m in re.finditer(pattern, text, re.IGNORECASE)})


def run_checks(text: str) -> list[Check]:
    checks: list[Check] = []

    approval = _has(r"\b(human (review|approval)|approv(e|al|ed) (by|before)|"
                    r"requires? approval|must be approved|sign[- ]off)\b", text)
    checks.append(Check("human approval step", approval,
                        "names a human approval step before sending" if approval
                        else "no human review or approval step before anything is sent"))

    claims = _find(r"\b\d{1,3}(\.\d+)?\s?%\s+(less|fewer|more|lower|higher|reduction|increase|"
                   r"lift|faster|better)\b[^.\n]*|\b(reduce|cut|lower|increase|boost)s?\b[^.\n]{0,40}"
                   r"\bby\s+\d{1,3}(\.\d+)?\s?%", text)
    checks.append(Check("no hard-coded performance claims", not claims,
                        "no specific performance figures promised" if not claims
                        else "promises a specific result: " + "; ".join(claims)[:160]))

    disparage = _find(r"\b(unlike|better than|outperforms?|beats?)\s+(our\s+)?competitors?\b|"
                      r"\bcompetitors?\b[^.]{0,40}\b(outdated|inferior|weak|worse|insecure|"
                      r"slow|failing)\b", text)
    checks.append(Check("no competitor disparagement", not disparage,
                        "does not attack competitors" if not disparage
                        else "disparages competitors: " + "; ".join(disparage)[:160]))

    sensitive = _find(r"\b(incident|fraud case|breach|investigation|chargeback case)\s+notes?\b|"
                      r"\bfull (crm|contact) (export|list)\b", text)
    checks.append(Check("no sensitive client data pulled", not sensitive,
                        "does not pull incident notes or full contact exports" if not sensitive
                        else "pulls sensitive client data: " + ", ".join(sensitive)))

    confidentiality = _has(r"\bconfidential(ity)?\b|\bclient data\b|\bdo not (share|disclose)\b", text)
    checks.append(Check("confidentiality / client-data rule", confidentiality,
                        "states how client data and confidential information are handled"
                        if confidentiality else "never mentions client confidentiality or client-data handling"))

    substantiation = _has(r"\bsubstantiat\w*\b|\bclaims?\b[^.\n]{0,60}\b(approv\w*|legal|compliance)\b|"
                          r"\b(legal|compliance)\b[^.\n]{0,60}\bclaims?\b", text)
    checks.append(Check("claims need substantiation/approval", substantiation,
                        "requires claims to be substantiated or approved" if substantiation
                        else "never says claims need substantiation or legal/compliance approval"))

    blast = _find(r"\b(send|email|blast)\b[^.]{0,30}\b(to\s+)?(everyone|every contact|all contacts|"
                  r"the (whole|entire) (list|database))\b", text)
    consent = _has(r"\bconsent\b|\bopt[- ]?in\b|\bunsubscribe|\bopt[- ]?out\b|\bsuppression\b", text)
    ok = consent and not blast
    if blast:
        detail = "sends to everyone: " + "; ".join(blast)[:120]
    elif not consent:
        detail = "no regional marketing-consent or opt-out rule"
    else:
        detail = "scopes recipients and respects regional marketing consent"
    checks.append(Check("recipient scope and marketing consent", ok, detail))

    secrets = _find(r"\b(sk-[A-Za-z0-9_-]{16,}|sk-ant-[A-Za-z0-9_-]{16,}|AKIA[0-9A-Z]{16})\b|"
                    r"\b(api[_ ]?key|password|token)\s*[:=]\s*\S{8,}", text)
    checks.append(Check("no secrets in prompt", not secrets,
                        "no keys or passwords embedded" if not secrets
                        else "contains what looks like a secret (value hidden)"))

    unknowns = _has(r"\bunknown\b|\bdo not guess\b|\bif (you are )?(not sure|unsure)\b", text)
    checks.append(Check("unknowns are labeled, not guessed", unknowns,
                        "tells the agent to label unknowns" if unknowns
                        else "no instruction for missing information; the agent may guess"))

    output = _has(r"\b(output|format|return|respond)\b[^.\n]{0,40}\b(json|table|sections?|bullets?|"
                  r"fields?|template|headings?)\b", text)
    checks.append(Check("output format defined", output,
                        "defines an output format" if output else "no output format; results will vary run to run"))
    return checks


def format_checks(checks: list[Check]) -> str:
    passed = sum(c.passed for c in checks)
    lines = [f"Static checks: {passed}/{len(checks)} passed", ""]
    for c in checks:
        lines.append(f"[{'PASS' if c.passed else 'FLAG'}] {c.name}: {c.detail}")
    return "\n".join(lines)
