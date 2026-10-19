"""Search visibility: SEO topical-map checks and GEO/AEO answer visibility.

Standard library only. No model calls. Two CSV inputs:

pages.csv (your site's topical map, plus Search Console numbers)
    url,topic,role,target_question,links_to,impressions,clicks
    - role is "pillar" (the main page for a topic) or "cluster" (a supporting page)
    - links_to is a semicolon-separated list of urls this page links to
    - impressions and clicks come from Google Search Console (or Bing Webmaster Tools)

answers.csv (a log of buyer questions asked to AI answer engines)
    checked_on,question,persona,engine,brand_mentioned,our_url_cited,competitor_mentions
    - brand_mentioned is yes/no: did the answer name your brand or product?
    - our_url_cited is the url of yours the answer cited, or blank
    - competitor_mentions is how many other vendors the answer named

SEO is about ranking and being clicked in search results. GEO (generative engine
optimization), also called AEO (answer engine optimization), is about being named and
cited inside AI answers. This script measures both and turns them into a ranked action
list. A model can then draft the page changes; a human approves them.
"""

from __future__ import annotations

import csv
import statistics
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

ROLES = ("pillar", "cluster")
YES = {"yes", "y", "true", "1"}
NO = {"no", "n", "false", "0"}
PAGE_COLUMNS = ("url", "topic", "role", "target_question", "links_to", "impressions", "clicks")
ANSWER_COLUMNS = ("checked_on", "question", "persona", "engine", "brand_mentioned",
                  "our_url_cited", "competitor_mentions")
SMALL_SAMPLE = 5  # fewer checks than this per question = directional only


@dataclass
class Page:
    url: str
    topic: str
    role: str
    target_question: str
    links_to: list[str]
    impressions: int
    clicks: int

    @property
    def ctr(self) -> float:
        return self.clicks / self.impressions if self.impressions else 0.0


@dataclass
class Check:
    checked_on: str
    question: str
    persona: str
    engine: str
    brand_mentioned: bool
    our_url_cited: str
    competitor_mentions: int


def _norm(text: str) -> str:
    """Normalize a question for matching: lowercase, single spaces, no trailing '?'."""
    return " ".join(text.lower().split()).rstrip("?").strip()


def _int(value: str, what: str, where: str) -> int:
    try:
        number = int(value)
    except ValueError as exc:
        raise ValueError(f"{where}: {what} must be a whole number, got {value!r}") from exc
    if number < 0:
        raise ValueError(f"{where}: {what} cannot be negative")
    return number


def _read(path: str | Path, columns: tuple[str, ...]) -> list[tuple[str, dict]]:
    path = Path(path)
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = [c for c in columns if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"{path.name}: missing column(s) {', '.join(missing)}")
        rows = [(f"{path.name} line {n}", {k: (v or "").strip() for k, v in row.items()})
                for n, row in enumerate(reader, start=2)]
    if not rows:
        raise ValueError(f"{path.name}: no data rows")
    return rows


def load_pages(path: str | Path) -> list[Page]:
    pages, seen = [], set()
    for where, row in _read(path, PAGE_COLUMNS):
        role = row["role"].lower()
        if role not in ROLES:
            raise ValueError(f"{where}: role must be pillar or cluster, got {row['role']!r}")
        if not row["url"] or not row["topic"] or not row["target_question"]:
            raise ValueError(f"{where}: url, topic and target_question are required")
        if row["url"] in seen:
            raise ValueError(f"{where}: duplicate url {row['url']}")
        seen.add(row["url"])
        impressions = _int(row["impressions"] or "0", "impressions", where)
        clicks = _int(row["clicks"] or "0", "clicks", where)
        if clicks > impressions:
            raise ValueError(f"{where}: clicks cannot exceed impressions")
        links = [link.strip() for link in row["links_to"].split(";") if link.strip()]
        pages.append(Page(row["url"], row["topic"], role, row["target_question"], links,
                          impressions, clicks))
    return pages


def load_checks(path: str | Path) -> list[Check]:
    checks = []
    for where, row in _read(path, ANSWER_COLUMNS):
        mentioned = row["brand_mentioned"].lower()
        if mentioned not in YES | NO:
            raise ValueError(f"{where}: brand_mentioned must be yes or no, got {row['brand_mentioned']!r}")
        if not row["question"] or not row["engine"]:
            raise ValueError(f"{where}: question and engine are required")
        checks.append(Check(row["checked_on"], row["question"], row["persona"] or "unknown",
                            row["engine"], mentioned in YES, row["our_url_cited"],
                            _int(row["competitor_mentions"] or "0", "competitor_mentions", where)))
    return checks


# ---------------------------------------------------------------- SEO: topical map

@dataclass
class MapReport:
    topics: dict[str, dict] = field(default_factory=dict)  # topic -> {"pillar": str|None, "clusters": [...]}
    issues: list[str] = field(default_factory=list)
    site_ctr: float = 0.0
    snippet_tests: list[Page] = field(default_factory=list)


def check_topical_map(pages: list[Page]) -> MapReport:
    """Check hub-and-spoke structure, internal links, competing pages and low-CTR pages."""
    report = MapReport()
    by_url = {p.url: p for p in pages}
    inbound: dict[str, int] = defaultdict(int)
    for page in pages:
        for target in page.links_to:
            if target in by_url:
                inbound[target] += 1
            else:
                report.issues.append(f"{page.url} links to {target}, which is not in the map")

    for topic in sorted({p.topic for p in pages}):
        members = [p for p in pages if p.topic == topic]
        pillars = [p for p in members if p.role == "pillar"]
        clusters = [p for p in members if p.role == "cluster"]
        pillar = pillars[0] if len(pillars) == 1 else None
        report.topics[topic] = {"pillar": pillar.url if pillar else None,
                                "clusters": [c.url for c in clusters]}
        if len(pillars) != 1:
            report.issues.append(f"topic '{topic}' has {len(pillars)} pillar pages (want exactly 1)")
        for cluster in clusters:
            if pillar and pillar.url not in cluster.links_to:
                report.issues.append(f"{cluster.url} does not link up to its pillar {pillar.url}")
            if pillar and cluster.url not in pillar.links_to:
                report.issues.append(f"pillar {pillar.url} does not link down to {cluster.url}")
            if inbound[cluster.url] == 0:
                report.issues.append(f"{cluster.url} is an orphan page (no internal links point to it)")

    owners: dict[str, list[str]] = defaultdict(list)
    for page in pages:
        owners[_norm(page.target_question)].append(page.url)
    for urls in owners.values():
        if len(urls) > 1:
            report.issues.append(f"{' and '.join(urls)} target the same question and compete with each other")

    total_impressions = sum(p.impressions for p in pages)
    report.site_ctr = sum(p.clicks for p in pages) / total_impressions if total_impressions else 0.0
    if total_impressions:
        median = statistics.median(p.impressions for p in pages)
        report.snippet_tests = sorted(
            (p for p in pages if p.impressions >= median and p.ctr < report.site_ctr / 2),
            key=lambda p: -p.impressions)
    return report


# ---------------------------------------------------------------- GEO/AEO: answer visibility

@dataclass
class Group:
    name: str
    checks: int
    mentioned: int
    cited: int

    @property
    def mention_rate(self) -> float:
        return self.mentioned / self.checks if self.checks else 0.0

    @property
    def cite_rate(self) -> float:
        return self.cited / self.checks if self.checks else 0.0


@dataclass
class QuestionStatus:
    question: str
    persona: str
    group: Group
    page: str | None
    action: str


@dataclass
class VisibilityReport:
    overall: Group
    by_engine: list[Group]
    by_persona: list[Group]
    share_of_voice: float
    questions: list[QuestionStatus]
    period: tuple[str, str]
    threshold: float


def _group(name: str, checks: list[Check]) -> Group:
    return Group(name, len(checks), sum(c.brand_mentioned for c in checks),
                 sum(bool(c.our_url_cited) for c in checks))


def _groups(checks: list[Check], key) -> list[Group]:
    buckets: dict[str, list[Check]] = defaultdict(list)
    for check in checks:
        buckets[key(check)].append(check)
    return [_group(name, items) for name, items in sorted(buckets.items())]


ACTION_ORDER = {"CREATE PAGE": 0, "IMPROVE PAGE": 1, "MAINTAIN": 2}


def answer_visibility(checks: list[Check], pages: list[Page], threshold: float = 0.5) -> VisibilityReport:
    """Mention and citation rates, share of voice, and an action per buyer question.

    Action rules:
      CREATE PAGE  - no page in the topical map targets this question
      IMPROVE PAGE - a page exists but is cited in fewer than `threshold` of answers
      MAINTAIN     - a page exists and is cited at or above `threshold`
    """
    if not 0 < threshold <= 1:
        raise ValueError("threshold must be in (0, 1]")
    page_for = {}
    for page in pages:
        page_for.setdefault(_norm(page.target_question), page.url)

    by_question: dict[str, list[Check]] = defaultdict(list)
    for check in checks:
        by_question[_norm(check.question)].append(check)

    questions = []
    for items in by_question.values():
        group = _group(items[0].question, items)
        page = page_for.get(_norm(items[0].question))
        if page is None:
            action = "CREATE PAGE"
        elif group.cite_rate < threshold:
            action = "IMPROVE PAGE"
        else:
            action = "MAINTAIN"
        personas = sorted({c.persona for c in items})
        questions.append(QuestionStatus(items[0].question, ", ".join(personas), group, page, action))
    questions.sort(key=lambda q: (ACTION_ORDER[q.action], q.group.cite_rate, q.group.mention_rate, q.question))

    mentions = sum(c.brand_mentioned for c in checks)
    competitors = sum(c.competitor_mentions for c in checks)
    share = mentions / (mentions + competitors) if mentions + competitors else 0.0
    dates = sorted(c.checked_on for c in checks if c.checked_on)
    period = (dates[0], dates[-1]) if dates else ("", "")
    return VisibilityReport(_group("ALL", checks), _groups(checks, lambda c: c.engine),
                            _groups(checks, lambda c: c.persona), share, questions, period, threshold)


# ---------------------------------------------------------------- report

def _pct(value: float) -> str:
    return f"{value * 100:.0f}%"


def format_report(map_report: MapReport, vis: VisibilityReport) -> str:
    lines = ["SEO: topical map"]
    for topic, info in map_report.topics.items():
        lines.append(f"  {topic}: pillar {info['pillar'] or '[none]'}, {len(info['clusters'])} cluster page(s)")
    if map_report.issues:
        lines.append(f"  Structure issues ({len(map_report.issues)}):")
        lines += [f"    - {issue}" for issue in map_report.issues]
    else:
        lines.append("  Structure issues: none")
    lines.append(f"  Site click-through rate from search: {map_report.site_ctr * 100:.1f}%")
    if map_report.snippet_tests:
        lines.append("  High impressions, low click-through (test a new title and description):")
        for page in map_report.snippet_tests:
            lines.append(f"    - {page.url}: {page.impressions:,} impressions, {page.clicks} clicks, "
                         f"{page.ctr * 100:.1f}% CTR")

    start, end = vis.period
    when = f" ({start} to {end})" if start else ""
    lines += ["", f"GEO/AEO: AI answer visibility{when}",
              f"  {vis.overall.checks} answer checks | brand named in {_pct(vis.overall.mention_rate)} | "
              f"our page cited in {_pct(vis.overall.cite_rate)} | share of voice {_pct(vis.share_of_voice)}"]
    for title, groups in (("By engine", vis.by_engine), ("By persona", vis.by_persona)):
        lines.append(f"  {title}:")
        width = max(len(g.name) for g in groups)
        for g in groups:
            lines.append(f"    {g.name:<{width}}  checks {g.checks:>3}  named {_pct(g.mention_rate):>4}  "
                         f"cited {_pct(g.cite_rate):>4}")

    lines += ["", f"Actions by buyer question (cited threshold {_pct(vis.threshold)}; "
                  f"under {SMALL_SAMPLE} checks = directional only):"]
    for n, q in enumerate(vis.questions, start=1):
        small = " (small sample)" if q.group.checks < SMALL_SAMPLE else ""
        lines.append(f"  {n}. {q.action}: \"{q.question}\"")
        lines.append(f"     persona {q.persona} | page {q.page or '[none]'} | named {q.group.mentioned}/"
                     f"{q.group.checks}, cited {q.group.cited}/{q.group.checks}{small}")
    lines += ["", "Note: AI answers change from day to day and by account. Treat rates as trends to track "
                  "over weeks, not as fixed scores."]
    return "\n".join(lines)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="SEO topical-map checks and GEO/AEO answer visibility.")
    parser.add_argument("--pages", required=True, help="pages.csv")
    parser.add_argument("--answers", required=True, help="answers.csv")
    parser.add_argument("--threshold", type=float, default=0.5, help="cited rate that counts as visible")
    args = parser.parse_args()
    site_pages = load_pages(args.pages)
    print(format_report(check_topical_map(site_pages),
                        answer_visibility(load_checks(args.answers), site_pages, args.threshold)))
