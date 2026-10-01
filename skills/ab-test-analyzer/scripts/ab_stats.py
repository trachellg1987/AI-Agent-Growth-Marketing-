"""A/B test statistics for offer tests. Single source of truth: never reimplement.

Standard library only. Used by agent 08, the case studies, and the unit tests.

Run directly:
    python skills/ab-test-analyzer/scripts/ab_stats.py --csv 08-ab-test-analyzer/sample-ab-results.csv
"""

from __future__ import annotations

import argparse
import csv
import math
from dataclasses import dataclass
from pathlib import Path

REQUIRED_COLUMNS = ("segment", "variant", "visitors", "conversions")


def normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def normal_ppf(p: float) -> float:
    """Inverse of normal_cdf, by bisection (accurate to ~1e-10)."""
    if not 0.0 < p < 1.0:
        raise ValueError("p must be between 0 and 1")
    lo, hi = -10.0, 10.0
    for _ in range(100):
        mid = (lo + hi) / 2.0
        if normal_cdf(mid) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def wilson_interval(conversions: int, n: int, confidence: float = 0.95) -> tuple[float, float]:
    """Wilson score interval for one conversion rate."""
    if n <= 0:
        raise ValueError("n must be positive")
    z = normal_ppf(1 - (1 - confidence) / 2)
    p = conversions / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return max(0.0, centre - half), min(1.0, centre + half)


@dataclass
class ZTest:
    n_a: int
    conv_a: int
    n_b: int
    conv_b: int
    rate_a: float
    rate_b: float
    abs_diff: float          # rate_b - rate_a, in proportion units
    rel_lift: float | None   # (rate_b - rate_a) / rate_a; None if rate_a == 0
    z: float
    p_value: float           # two-sided
    ci_low: float            # 95% CI for rate_b - rate_a (unpooled SE)
    ci_high: float


def two_proportion_ztest(conv_a: int, n_a: int, conv_b: int, n_b: int,
                         confidence: float = 0.95) -> ZTest:
    """Two-sided pooled z-test for a difference in conversion rates (B minus A)."""
    for name, value in (("n_a", n_a), ("n_b", n_b)):
        if value <= 0:
            raise ValueError(f"{name} must be positive")
    for conv, n in ((conv_a, n_a), (conv_b, n_b)):
        if conv < 0 or conv > n:
            raise ValueError("conversions must be between 0 and the number exposed")
    rate_a, rate_b = conv_a / n_a, conv_b / n_b
    diff = rate_b - rate_a
    pooled = (conv_a + conv_b) / (n_a + n_b)
    se_pooled = math.sqrt(pooled * (1 - pooled) * (1 / n_a + 1 / n_b))
    if se_pooled == 0:
        z, p_value = 0.0, 1.0
    else:
        z = diff / se_pooled
        p_value = 2 * (1 - normal_cdf(abs(z)))
    se_unpooled = math.sqrt(rate_a * (1 - rate_a) / n_a + rate_b * (1 - rate_b) / n_b)
    z_crit = normal_ppf(1 - (1 - confidence) / 2)
    return ZTest(
        n_a=n_a, conv_a=conv_a, n_b=n_b, conv_b=conv_b,
        rate_a=rate_a, rate_b=rate_b, abs_diff=diff,
        rel_lift=(diff / rate_a) if rate_a > 0 else None,
        z=z, p_value=p_value,
        ci_low=diff - z_crit * se_unpooled, ci_high=diff + z_crit * se_unpooled,
    )


def holm_adjust(p_values: list[float]) -> list[float]:
    """Holm-Bonferroni adjusted p-values, returned in the input order."""
    m = len(p_values)
    order = sorted(range(m), key=lambda i: p_values[i])
    adjusted = [0.0] * m
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (m - rank) * p_values[i]))
        adjusted[i] = running
    return adjusted


def sample_size_per_variant(baseline: float, mde_abs: float, alpha: float = 0.05,
                            power: float = 0.8) -> int:
    """Contacts needed per variant to detect an absolute lift of mde_abs."""
    if not 0 < baseline < 1:
        raise ValueError("baseline must be between 0 and 1")
    if mde_abs <= 0 or baseline + mde_abs >= 1:
        raise ValueError("mde_abs must be positive and keep the rate below 1")
    p1, p2 = baseline, baseline + mde_abs
    z_a = normal_ppf(1 - alpha / 2)
    z_b = normal_ppf(power)
    p_bar = (p1 + p2) / 2
    num = (z_a * math.sqrt(2 * p_bar * (1 - p_bar))
           + z_b * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
    return math.ceil(num / (mde_abs ** 2))


def verdict(test: ZTest, adjusted_p: float, alpha: float = 0.05) -> str:
    if adjusted_p >= alpha:
        return "no evidence of a difference"
    return "B better" if test.abs_diff > 0 else "A better"


def load_rows(path: str | Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"{path}: missing column(s): {', '.join(missing)}")
        rows = []
        for line, row in enumerate(reader, start=2):
            variant = row["variant"].strip().upper()
            if variant not in ("A", "B"):
                raise ValueError(f"{path} line {line}: variant must be A or B")
            try:
                visitors, conversions = int(row["visitors"]), int(row["conversions"])
            except ValueError as exc:
                raise ValueError(f"{path} line {line}: visitors and conversions must be integers") from exc
            rows.append({"segment": row["segment"].strip(), "variant": variant,
                         "visitors": visitors, "conversions": conversions})
    if not rows:
        raise ValueError(f"{path}: no data rows")
    return rows


def analyze(rows: list[dict], alpha: float = 0.05) -> dict:
    """Per-segment tests (Holm-adjusted across segments) plus the pooled total."""
    cells: dict[str, dict[str, list[int]]] = {}
    for row in rows:
        cell = cells.setdefault(row["segment"], {}).setdefault(row["variant"], [0, 0])
        cell[0] += row["visitors"]
        cell[1] += row["conversions"]
    segments = []
    for name, variants in cells.items():
        if set(variants) != {"A", "B"}:
            raise ValueError(f"segment {name!r} needs both an A row and a B row")
        (n_a, c_a), (n_b, c_b) = variants["A"], variants["B"]
        segments.append((name, two_proportion_ztest(c_a, n_a, c_b, n_b)))
    adjusted = holm_adjust([t.p_value for _, t in segments])
    tot = {v: [sum(cells[s][v][i] for s in cells) for i in (0, 1)] for v in ("A", "B")}
    overall = two_proportion_ztest(tot["A"][1], tot["A"][0], tot["B"][1], tot["B"][0])
    seg_results = [
        {"segment": name, "test": t, "p_holm": p, "verdict": verdict(t, p, alpha)}
        for (name, t), p in zip(segments, adjusted)
    ]
    directions = {r["verdict"] for r in seg_results} - {"no evidence of a difference"}
    return {
        "alpha": alpha,
        "segments": seg_results,
        "overall": overall,
        "overall_verdict": verdict(overall, overall.p_value, alpha),
        "segments_disagree": directions == {"A better", "B better"},
    }


def _pct(x: float) -> str:
    return f"{x * 100:.2f}%"


def format_report(result: dict, label_a: str = "A", label_b: str = "B",
                  metric: str = "conversions") -> str:
    lines = [
        f"Metric: {metric} | A = {label_a} | B = {label_b} | alpha = {result['alpha']}",
        "Per-segment p-values are Holm-adjusted across segments.",
        "",
        f"{'segment':<20}{'A rate':>16}{'B rate':>16}{'B-A (pts)':>11}"
        f"{'95% CI (pts)':>18}{'p':>8}{'p_holm':>8}  verdict",
    ]

    def row(name: str, t: ZTest, p_adj: float | None, v: str) -> str:
        a = f"{t.conv_a}/{t.n_a} {_pct(t.rate_a)}"
        b = f"{t.conv_b}/{t.n_b} {_pct(t.rate_b)}"
        ci = f"[{t.ci_low * 100:+.2f}, {t.ci_high * 100:+.2f}]"
        p_holm = f"{p_adj:.4f}" if p_adj is not None else "-"
        return (f"{name:<20}{a:>16}{b:>16}{t.abs_diff * 100:>+11.2f}{ci:>18}"
                f"{t.p_value:>8.4f}{p_holm:>8}  {v}")

    for r in result["segments"]:
        lines.append(row(r["segment"], r["test"], r["p_holm"], r["verdict"]))
    lines.append(row("ALL (pooled)", result["overall"], None, result["overall_verdict"]))
    lines.append("")
    if result["segments_disagree"]:
        lines.append("WARNING: segments disagree (B wins in at least one segment and loses in "
                     "another). Do not roll out on the pooled result alone.")
    else:
        lines.append("Segments do not point in opposite directions.")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="A/B statistics for an offer test CSV.")
    parser.add_argument("--csv", required=True, help="CSV with segment,variant,visitors,conversions")
    parser.add_argument("--alpha", type=float, default=0.05, help="significance level (default 0.05)")
    args = parser.parse_args()
    print(format_report(analyze(load_rows(args.csv), args.alpha)))


if __name__ == "__main__":
    main()
