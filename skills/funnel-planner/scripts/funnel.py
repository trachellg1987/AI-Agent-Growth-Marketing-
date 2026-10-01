"""Backward funnel planning for new signed clients. Standard library only.

Stage rates are sequential: each rate is the share of the previous stage that
reaches this stage. The first rate applies to the eligible client base.
Example: reached:0.70 means 70% of eligible clients are reached.

Counts are whole clients. Working backward we round UP (you cannot pilot 0.7 of
a bank); working forward from the eligible base we round DOWN.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class Stage:
    name: str
    rate: float


def parse_funnel(spec: str) -> list[Stage]:
    """Parse 'reached:0.70,engaged:0.25,...' into ordered stages."""
    stages = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        name, sep, rate = part.partition(":")
        if not sep or not name.strip():
            raise ValueError(f"funnel stage {part!r} must look like name:rate")
        try:
            value = float(rate)
        except ValueError as exc:
            raise ValueError(f"funnel stage {part!r}: rate must be a number") from exc
        if not 0 < value <= 1:
            raise ValueError(f"funnel stage {part!r}: rate must be in (0, 1]")
        stages.append(Stage(name.strip(), value))
    if not stages:
        raise ValueError("funnel needs at least one stage")
    names = [s.name for s in stages]
    if len(set(names)) != len(names):
        raise ValueError("funnel stage names must be unique")
    return stages


def backward_counts(target: int, stages: list[Stage]) -> list[tuple[str, int]]:
    """Clients needed at each stage (plus 'eligible') to hit the target."""
    needed = target
    out = [(stages[-1].name, target)]
    for i in range(len(stages) - 1, -1, -1):
        needed = math.ceil(needed / stages[i].rate - 1e-9)
        out.append((stages[i - 1].name if i > 0 else "eligible", needed))
    return list(reversed(out))


def forward_capacity(eligible: int, stages: list[Stage]) -> list[tuple[str, int]]:
    """Clients the eligible base supports at each stage, rounding down."""
    count = eligible
    out = [("eligible", eligible)]
    for stage in stages:
        count = math.floor(count * stage.rate + 1e-9)
        out.append((stage.name, count))
    return out


def plan(target: int, eligible: int, stages: list[Stage], budget: float, weeks: int) -> dict:
    if target <= 0 or eligible <= 0 or weeks <= 0:
        raise ValueError("target, eligible and weeks must be positive")
    if budget < 0:
        raise ValueError("budget cannot be negative")
    backward = backward_counts(target, stages)
    forward = forward_capacity(eligible, stages)
    overall = math.prod(s.rate for s in stages)
    eligible_needed = backward[0][1]
    max_signed = forward[-1][1]
    feasible = max_signed >= target
    # Rate the final stage would need, holding earlier stages and the base fixed.
    before_last = forward[-2][1]
    last_rate_needed = (target / before_last) if before_last else None
    first_touch = backward[1][1]
    return {
        "target": target,
        "eligible": eligible,
        "weeks": weeks,
        "budget": budget,
        "stages": stages,
        "overall_rate": overall,
        "backward": backward,
        "forward": forward,
        "eligible_needed": eligible_needed,
        "max_signed": max_signed,
        "feasible": feasible,
        "last_stage_rate_needed": last_rate_needed,
        "budget_per_signed": budget / target,
        "budget_per_first_touch": budget / first_touch,
        "weekly": [(name, count / weeks) for name, count in backward[1:]],
    }


def format_plan(p: dict) -> str:
    stages = p["stages"]
    lines = [
        f"Target: {p['target']} new signed clients in {p['weeks']} weeks | "
        f"eligible base: {p['eligible']} | budget: ${p['budget']:,.0f}",
        "Funnel: " + " -> ".join(f"{s.name} {s.rate:.0%}" for s in stages)
        + f" | overall eligible-to-{stages[-1].name}: {p['overall_rate']:.2%}",
        "",
        f"{'stage':<12}{'needed (backward)':>19}{'supported (forward)':>21}{'per week':>10}",
    ]
    weekly = dict(p["weekly"])
    for (name, need), (_, have) in zip(p["backward"], p["forward"]):
        per_week = f"{weekly[name]:.1f}" if name in weekly else "-"
        lines.append(f"{name:<12}{need:>19}{have:>21}{per_week:>10}")
    lines += [
        "",
        f"Budget per signed client: ${p['budget_per_signed']:,.0f}",
        f"Budget per client at first stage ({p['backward'][1][0]}): "
        f"${p['budget_per_first_touch']:,.2f}",
        "",
    ]
    if p["feasible"]:
        lines.append(f"FEASIBLE: the eligible base supports {p['max_signed']} signed clients "
                     f"(target {p['target']}).")
    else:
        last = stages[-1]
        lines.append(
            f"INFEASIBLE: the target needs {p['eligible_needed']} eligible clients but the base "
            f"is {p['eligible']}; at these rates the base supports about {p['max_signed']} "
            f"signed clients, not {p['target']}."
        )
        if p["last_stage_rate_needed"] is not None:
            lines.append(
                f"Options: lower the target to {p['max_signed']}, widen the eligible base to "
                f"{p['eligible_needed']}, or lift the {last.name} rate from {last.rate:.0%} to "
                f"{p['last_stage_rate_needed']:.1%} (other rates unchanged)."
            )
    return "\n".join(lines)
