"""Summarize a client-program export: live vs inactive programs per VAS product.

Standard library only. Only column names and aggregates leave this module;
row-level client data is never put into a model prompt.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

REQUIRED_COLUMNS = ("client_id", "client_type", "vas_product", "status", "start_date", "source")
STATUSES = ("active", "inactive")
SOURCES = ("account_manager", "webinar", "email", "workshop")


def load(path: str | Path) -> tuple[list[str], list[dict]]:
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        columns = list(reader.fieldnames or [])
        missing = [c for c in REQUIRED_COLUMNS if c not in columns]
        if missing:
            raise ValueError(f"{path}: missing column(s): {', '.join(missing)}")
        rows = []
        for line, row in enumerate(reader, start=2):
            status = row["status"].strip().lower()
            if status not in STATUSES:
                raise ValueError(f"{path} line {line}: status must be active or inactive")
            source = row["source"].strip().lower()
            if source not in SOURCES:
                raise ValueError(f"{path} line {line}: source must be one of {', '.join(SOURCES)}")
            try:
                date.fromisoformat(row["start_date"].strip())
            except ValueError as exc:
                raise ValueError(f"{path} line {line}: start_date must be YYYY-MM-DD") from exc
            rows.append({**{k: (v or "").strip() for k, v in row.items()},
                         "status": status, "source": source})
    if not rows:
        raise ValueError(f"{path}: no data rows")
    return columns, rows


def summarize(rows: list[dict]) -> dict:
    by_product: dict[str, Counter] = defaultdict(Counter)
    active_by_type: Counter = Counter()
    active_by_source: Counter = Counter()
    for row in rows:
        by_product[row["vas_product"]][row["status"]] += 1
        if row["status"] == "active":
            active_by_type[row["client_type"]] += 1
            active_by_source[row["source"]] += 1
    products = []
    for name in sorted(by_product):
        counts = by_product[name]
        total = counts["active"] + counts["inactive"]
        products.append({"product": name, "active": counts["active"],
                         "inactive": counts["inactive"], "total": total,
                         "active_share": counts["active"] / total})
    total_active = sum(p["active"] for p in products)
    return {
        "rows": len(rows),
        "clients": len({r["client_id"] for r in rows}),
        "products": products,
        "total_active": total_active,
        "total_inactive": len(rows) - total_active,
        "active_by_type": dict(sorted(active_by_type.items())),
        "active_by_source": dict(sorted(active_by_source.items())),
    }


def format_summary(s: dict) -> str:
    lines = [
        f"Client programs: {s['rows']} rows across {s['clients']} clients | "
        f"active {s['total_active']} | inactive {s['total_inactive']}",
        "",
        f"{'vas_product':<26}{'active':>7}{'inactive':>9}{'total':>7}{'active %':>10}",
    ]
    for p in s["products"]:
        lines.append(f"{p['product']:<26}{p['active']:>7}{p['inactive']:>9}{p['total']:>7}"
                     f"{p['active_share']:>10.0%}")
    lines += ["", "Active programs by client type: "
              + ", ".join(f"{k} {v}" for k, v in s["active_by_type"].items()),
              "Active programs by source: "
              + ", ".join(f"{k} {v}" for k, v in s["active_by_source"].items())]
    return "\n".join(lines)
