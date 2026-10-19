import tempfile
import unittest
from pathlib import Path

from tests.helpers import ROOT, search_visibility as sv

SAMPLE_PAGES = ROOT / "11-search-visibility-agent" / "sample-pages.csv"
SAMPLE_ANSWERS = ROOT / "11-search-visibility-agent" / "sample-answers.csv"

PAGE_HEADER = "url,topic,role,target_question,links_to,impressions,clicks\n"
ANSWER_HEADER = "checked_on,question,persona,engine,brand_mentioned,our_url_cited,competitor_mentions\n"


def write(text: str) -> Path:
    handle = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8")
    handle.write(text)
    handle.close()
    return Path(handle.name)


def page(url, topic="t", role="cluster", question=None, links="", impressions=100, clicks=5):
    return sv.Page(url, topic, role, question or f"question for {url}?",
                   [x for x in links.split(";") if x], impressions, clicks)


def check(question, mentioned=True, cited="", competitors=0, engine="chatgpt", persona="head_of_fraud"):
    return sv.Check("2026-10-01", question, persona, engine, mentioned, cited, competitors)


class TopicalMapTests(unittest.TestCase):
    def test_clean_hub_and_spoke_has_no_issues(self):
        pages = [page("/p", role="pillar", links="/a;/b"), page("/a", links="/p"), page("/b", links="/p")]
        report = sv.check_topical_map(pages)
        self.assertEqual(report.issues, [])
        self.assertEqual(report.topics["t"], {"pillar": "/p", "clusters": ["/a", "/b"]})

    def test_missing_links_and_orphans(self):
        pages = [page("/p", role="pillar"), page("/a")]
        issues = sv.check_topical_map(pages).issues
        self.assertIn("/a does not link up to its pillar /p", issues)
        self.assertIn("pillar /p does not link down to /a", issues)
        self.assertIn("/a is an orphan page (no internal links point to it)", issues)

    def test_topic_needs_exactly_one_pillar(self):
        issues = sv.check_topical_map([page("/a"), page("/b")]).issues
        self.assertIn("topic 't' has 0 pillar pages (want exactly 1)", issues)
        issues = sv.check_topical_map([page("/a", role="pillar"), page("/b", role="pillar")]).issues
        self.assertIn("topic 't' has 2 pillar pages (want exactly 1)", issues)

    def test_competing_pages_ignore_case_and_question_mark(self):
        pages = [page("/p", role="pillar", question="What is X?", links="/a"),
                 page("/a", question="what is  x", links="/p")]
        issues = sv.check_topical_map(pages).issues
        self.assertIn("/p and /a target the same question and compete with each other", issues)

    def test_link_to_unknown_page(self):
        issues = sv.check_topical_map([page("/p", role="pillar", links="/missing")]).issues
        self.assertIn("/p links to /missing, which is not in the map", issues)

    def test_snippet_tests_flag_high_impression_low_ctr(self):
        pages = [page("/p", role="pillar", links="/a;/b;/c", impressions=1000, clicks=100),
                 page("/a", links="/p", impressions=1000, clicks=10),
                 page("/b", links="/p", impressions=100, clicks=1),
                 page("/c", links="/p", impressions=800, clicks=80)]
        report = sv.check_topical_map(pages)
        self.assertAlmostEqual(report.site_ctr, 191 / 2900)
        self.assertEqual([p.url for p in report.snippet_tests], ["/a"])

    def test_no_impressions_is_safe(self):
        report = sv.check_topical_map([page("/p", role="pillar", impressions=0, clicks=0)])
        self.assertEqual(report.site_ctr, 0.0)
        self.assertEqual(report.snippet_tests, [])


class VisibilityTests(unittest.TestCase):
    def setUp(self):
        self.pages = [page("/p", role="pillar", question="Q1?", links="/a"),
                      page("/a", question="Q2?", links="/p")]

    def test_actions(self):
        checks = ([check("Q1?", cited="/p")] * 3 + [check("Q1?", cited="")]
                  + [check("Q2?", cited="")] * 4 + [check("Q3?", mentioned=False)] * 2)
        report = sv.answer_visibility(checks, self.pages, threshold=0.5)
        actions = [(q.question, q.action) for q in report.questions]
        self.assertEqual(actions, [("Q3?", "CREATE PAGE"), ("Q2?", "IMPROVE PAGE"), ("Q1?", "MAINTAIN")])

    def test_threshold_boundary_counts_as_visible(self):
        checks = [check("Q1?", cited="/p"), check("Q1?", cited="")]
        report = sv.answer_visibility(checks, self.pages, threshold=0.5)
        self.assertEqual(report.questions[0].action, "MAINTAIN")

    def test_rates_and_share_of_voice(self):
        checks = [check("Q1?", mentioned=True, cited="/p", competitors=1),
                  check("Q1?", mentioned=False, competitors=2),
                  check("Q2?", mentioned=True, competitors=1, engine="perplexity")]
        report = sv.answer_visibility(checks, self.pages)
        self.assertEqual((report.overall.checks, report.overall.mentioned, report.overall.cited), (3, 2, 1))
        self.assertAlmostEqual(report.share_of_voice, 2 / 6)
        self.assertEqual([g.name for g in report.by_engine], ["chatgpt", "perplexity"])

    def test_rejects_bad_threshold(self):
        for value in (0, 1.5, -0.1):
            with self.assertRaises(ValueError):
                sv.answer_visibility([check("Q1?")], self.pages, threshold=value)


class LoaderTests(unittest.TestCase):
    def test_sample_files_load(self):
        self.assertEqual(len(sv.load_pages(SAMPLE_PAGES)), 7)
        self.assertEqual(len(sv.load_checks(SAMPLE_ANSWERS)), 36)

    def test_sample_report(self):
        pages = sv.load_pages(SAMPLE_PAGES)
        report = sv.answer_visibility(sv.load_checks(SAMPLE_ANSWERS), pages)
        self.assertEqual(report.questions[0].action, "CREATE PAGE")
        self.assertEqual(report.questions[-1].action, "MAINTAIN")
        self.assertEqual(len(sv.check_topical_map(pages).issues), 9)

    def test_rejects_bad_rows(self):
        bad_pages = [
            PAGE_HEADER + "/a,t,hub,Q?,,1,0\n",
            PAGE_HEADER + "/a,t,pillar,Q?,,5,6\n",
            PAGE_HEADER + "/a,t,pillar,Q?,,x,0\n",
            PAGE_HEADER + "/a,t,pillar,Q?,,1,0\n/a,t,cluster,Q2?,,1,0\n",
            "url,topic\n/a,t\n",
            PAGE_HEADER,
        ]
        for text in bad_pages:
            with self.assertRaises(ValueError, msg=text):
                sv.load_pages(write(text))
        bad_answers = [
            ANSWER_HEADER + "2026-10-01,Q?,p,chatgpt,maybe,,0\n",
            ANSWER_HEADER + "2026-10-01,Q?,p,chatgpt,yes,,-1\n",
            ANSWER_HEADER + "2026-10-01,,p,chatgpt,yes,,0\n",
        ]
        for text in bad_answers:
            with self.assertRaises(ValueError, msg=text):
                sv.load_checks(write(text))

    def test_format_report_marks_small_samples(self):
        report = sv.answer_visibility([check("Q1?", cited="/p")], [page("/p", role="pillar", question="Q1?")])
        text = sv.format_report(sv.check_topical_map([page("/p", role="pillar", question="Q1?")]), report)
        self.assertIn("(small sample)", text)
        self.assertIn("Structure issues: none", text)


if __name__ == "__main__":
    unittest.main()
