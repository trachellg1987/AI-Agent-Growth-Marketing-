"""Backward plan for growing live VAS client programs. Standard library only.

Model: each month, live programs = previous live programs x (1 - attrition) + new
signed programs. Attrition means clients that deactivate or do not renew.

Channels are filled cheapest cost-per-signed-client first, up to each channel's
monthly capacity (reachable contacts x conversion to signed client). Results
are expected values, so they can be fractional; treat them as planning ranges.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class Channel:
    name: str
    monthly_contacts: float      # contacts the channel can reach per month
    conversion: float            # share of contacts that become a signed client program
    cost_per_contact: float      # loaded cost of one contact (an assumption you replace)

    @property
    def monthly_capacity(self) -> float:
        return self.monthly_contacts * self.conversion

    @property
    def cost_per_client(self) -> float:
        return self.cost_per_contact / self.conversion


def parse_channels(spec: str) -> list[Channel]:
    """Parse 'name:contacts:conversion:cost,...'."""
    channels = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        fields = part.split(":")
        if len(fields) != 4 or not fields[0].strip():
            raise ValueError(f"channel {part!r} must look like name:contacts:conversion:cost")
        try:
            contacts, conversion, cost = (float(x) for x in fields[1:])
        except ValueError as exc:
            raise ValueError(f"channel {part!r}: contacts, conversion and cost must be numbers") from exc
        if contacts <= 0 or cost < 0 or not 0 < conversion <= 1:
            raise ValueError(f"channel {part!r}: need contacts > 0, 0 < conversion <= 1, cost >= 0")
        channels.append(Channel(fields[0].strip(), contacts, conversion, cost))
    if not channels:
        raise ValueError("at least one channel is required")
    return channels


def required_monthly_adds(current: float, target_net: float, months: int, attrition: float) -> float:
    """Constant monthly new client programs needed to end at current + target_net."""
    if months <= 0:
        raise ValueError("months must be positive")
    if not 0 <= attrition < 1:
        raise ValueError("monthly attrition must be in [0, 1)")
    goal = current + target_net
    keep = 1 - attrition
    carried = current * keep ** months
    annuity = months if attrition == 0 else (1 - keep ** months) / attrition
    return max(0.0, (goal - carried) / annuity)


def trajectory(current: float, adds: float, months: int, attrition: float) -> list[tuple[int, float, float]]:
    """(month, programs lost to attrition, live programs at month end)."""
    rows, live = [], current
    for month in range(1, months + 1):
        lost = live * attrition
        live = live - lost + adds
        rows.append((month, lost, live))
    return rows


def allocate(adds: float, channels: list[Channel]) -> tuple[list[dict], float]:
    """Fill the monthly need cheapest-first. Returns allocations and any shortfall."""
    remaining = adds
    allocations = []
    for ch in sorted(channels, key=lambda c: c.cost_per_client):
        take = min(remaining, ch.monthly_capacity)
        allocations.append({
            "channel": ch,
            "clients": take,
            "contacts": take / ch.conversion,
            "cost": take * ch.cost_per_client,
            "utilization": take / ch.monthly_capacity,
        })
        remaining -= take
    return allocations, max(0.0, remaining)


def plan(current: int, target_net: int, months: int, attrition: float, channels: list[Channel]) -> dict:
    if current < 0 or target_net <= 0:
        raise ValueError("current must be >= 0 and target-net must be positive")
    adds = required_monthly_adds(current, target_net, months, attrition)
    rows = trajectory(current, adds, months, attrition)
    allocations, shortfall = allocate(adds, channels)
    used = [a for a in allocations if a["clients"] > 1e-9]
    monthly_cost = sum(a["cost"] for a in allocations)
    return {
        "current": current,
        "target_net": target_net,
        "goal": current + target_net,
        "months": months,
        "attrition": attrition,
        "monthly_adds": adds,
        "total_adds": adds * months,
        "total_lost": sum(r[1] for r in rows),
        "trajectory": rows,
        "allocations": allocations,
        "capacity": sum(c.monthly_capacity for c in channels),
        "shortfall": shortfall,
        "feasible": shortfall <= 1e-9,
        "monthly_cost": monthly_cost,
        "total_cost": monthly_cost * months,
        "blended_cost_per_client": (monthly_cost / (adds - shortfall)) if adds > shortfall else 0.0,
        "marginal": used[-1] if used else None,
    }


def format_plan(p: dict) -> str:
    lines = [
        f"Live client programs: {p['current']} now -> {p['goal']} goal "
        f"(+{p['target_net']} net) in {p['months']} months",
        f"Monthly attrition (deactivate or do not renew): {p['attrition']:.1%}",
        "",
        f"New signed client programs needed per month: {p['monthly_adds']:.2f}",
        f"Total new programs over {p['months']} months: {p['total_adds']:.1f} "
        f"(of which {p['total_lost']:.1f} replace programs lost to attrition)",
        "",
        "month  lost  live at month end",
    ]
    for month, lost, live in p["trajectory"]:
        lines.append(f"{month:>5}{lost:>6.1f}{live:>19.1f}")
    lines += [
        "",
        "Channels, cheapest cost per signed client first:",
        f"{'channel':<17}{'cost/client':>12}{'capacity/mo':>13}{'planned/mo':>12}"
        f"{'contacts/mo':>13}{'cost/mo':>11}{'used':>7}",
    ]
    for a in p["allocations"]:
        ch = a["channel"]
        lines.append(
            f"{ch.name:<17}{'$' + format(ch.cost_per_client, ',.0f'):>12}{ch.monthly_capacity:>13.1f}"
            f"{a['clients']:>12.2f}{a['contacts']:>13.0f}{'$' + format(a['cost'], ',.0f'):>11}"
            f"{a['utilization']:>7.0%}"
        )
    lines += [
        "",
        f"Total channel capacity: {p['capacity']:.1f} programs/month vs {p['monthly_adds']:.2f} needed",
        f"Planned cost: ${p['monthly_cost']:,.0f}/month, ${p['total_cost']:,.0f} over "
        f"{p['months']} months, blended ${p['blended_cost_per_client']:,.0f} per new program",
    ]
    marginal = p["marginal"]
    if marginal is not None:
        ch = marginal["channel"]
        lines.append(
            f"Marginal (most costly) channel in use: {ch.name} at ${ch.cost_per_client:,.0f} "
            f"per client, {marginal['clients']:.2f} programs/month"
        )
    if p["feasible"]:
        lines.append("FEASIBLE within current channel capacity.")
    else:
        lines.append(f"INFEASIBLE: short by {p['shortfall']:.2f} programs/month at current capacity.")
    return "\n".join(lines)
