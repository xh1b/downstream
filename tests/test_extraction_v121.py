"""v1.21 pins: the Collinson et al. 2024 eviction stream (queue #17,
read via NBER w30382; QJE 139(1):57-120 is the version of record).

What this file hunts:
- the queue's original target creeping back: #17 named the Collinson &
  Reed 2018 WP, which the QJE paper SUBSUMES - a future re-landing
  from the 2018 WP would regress the version of record and mix two
  designs (NYC-only application vs two-city shelter use)
- the desmond2016 +11-22pp job-loss number sneaking in as a point or
  an eviction->worker_earnings edge appearing: matching on
  observables is not a CITING §1 class, and collinson2024's employment
  nulls refute the size; the refusal must stay encoded
- the shelter rate ratio losing its base: 4.778 is (0.009+0.034)/0.009
  with BOTH the base and the SE named; a silent base swap changes it
- the earnings response being read in dollars instead of the stored
  gap multiplier, or the year-1 null (-$323, ns) getting promoted to
  the point (the stevens2011 timing pattern runs the other way)
- the new nodes composing into the worker_earnings displacement
  multiplier - PARALLEL stream, boundary-applied
- the bib evidence tier regressing below fulltext-table
"""
import pytest

from downstream.audit import audit
from downstream.citations import parse_bib
from downstream.params import default_dir, load, load_nodes

PARAMS_DIR = default_dir()
PARAMS = load(PARAMS_DIR / "parameters.csv")

BIB = parse_bib(PARAMS_DIR / "references.bib")
SHELTER = "eviction_order->emergency_shelter_use"
EARNINGS = "eviction_order->eviction_earnings_response"


def test_version_is_v121():
    assert (PARAMS_DIR / "VERSION").read_text().strip() == "v1.30"


def test_shelter_row_matches_table_v_col3():
    # Table V col 3: IV +3.4pp (SE 1.7) on the 0.009 non-evicted base
    delta, se, base = 0.034, 0.017, 0.009
    p = PARAMS.by_link(SHELTER)
    assert p.point == pytest.approx((base + delta) / base, abs=1e-3)
    assert p.low == pytest.approx((base + delta - 1.96 * se) / base, abs=1e-3)
    assert p.high == pytest.approx((base + delta + 1.96 * se) / base, abs=1e-3)
    assert p.tier == "EXACT" and p.citation == "collinson2024"


def test_shelter_band_state_pinned():
    p = PARAMS.by_link(SHELTER)
    assert p.point == pytest.approx(4.778, abs=1e-3)
    assert p.low == pytest.approx(1.076, abs=1e-3)
    assert p.high == pytest.approx(8.480, abs=1e-3)


def test_shelter_timing_declared():
    # year-2 shelter null; services persist (+3.6pp, SE 1.5) - the
    # acute-spike-then-persistent-contact structure must survive edits
    p = PARAMS.by_link(SHELTER)
    assert "year-2 emergency-shelter IV is null" in p.notes
    assert "+3.6pp" in p.notes
    # the superseded NYC-only application estimate stays a cross-check,
    # never a second row
    assert "+12.7pp" in p.notes


def test_earnings_row_is_gap_multiplier_on_4300_base():
    # Table VI: Q5-8 IV -$613 (SE 248) on the $4,300 non-evicted mean
    delta, se, base = 613, 248, 4300
    p = PARAMS.by_link(EARNINGS)
    assert p.point == pytest.approx(1 - delta / base, abs=1e-4)
    assert p.low == pytest.approx(1 - (delta + 1.96 * se) / base, abs=1e-4)
    assert p.high == pytest.approx(1 - (delta - 1.96 * se) / base, abs=1e-4)
    assert p.tier == "EXACT" and p.citation == "collinson2024"
    assert p.low < p.point < p.high


def test_earnings_year1_null_not_promoted():
    # the year-1 estimate is -$323 (SE 175) and NOT significant; the
    # point is the sustained year-2 window (stevens2011 timing pattern)
    p = PARAMS.by_link(EARNINGS)
    assert "-$323" in p.notes
    assert "NOT significant" in p.notes
    assert p.point == pytest.approx(0.8574, abs=1e-3)


def test_desmond_refusal_encoded():
    # the matched +11-22pp job-loss estimate must NEVER become a point:
    # (a) no eviction->worker_earnings edge exists
    assert "eviction_order->worker_earnings" not in {q.link for q in PARAMS.parameters}
    # (b) the refusal is documented on the earnings row and cites the
    #     refuting employment nulls
    p = PARAMS.by_link(EARNINGS)
    assert "desmond2016" in p.notes and "NOT encoded" in p.notes
    assert "-1.5pp" in p.notes and "-1.8pp" in p.notes
    # (c) desmond2016 is a bib entry but cites NO parameter row
    assert "desmond2016" in BIB
    cited = {k for q in PARAMS.parameters for k in q.citation_keys}
    assert "desmond2016" not in cited


def test_version_of_record_correction_recorded():
    # the 2018 WP the queue named is subsumed; the row must say so
    p = PARAMS.by_link(SHELTER)
    assert "version of record is collinson2024" in p.notes
    assert "w30382" in p.notes
    assert BIB["collinson2024"].evidence == "fulltext-table"
    assert BIB["collinson2024"].fields["doi"] == "10.1093/qje/qjad042"
    assert BIB["desmond2016"].evidence == "fulltext-table"


def test_new_nodes_are_parallel_stream():
    # hazard-space + level-response nodes never chain into the
    # displacement earnings multiplier or the child streams
    nodes = load_nodes(PARAMS_DIR / "nodes.csv")
    for node in ("emergency_shelter_use", "eviction_earnings_response"):
        assert node in nodes
        ups = [q.from_node for q in PARAMS.parameters if q.to_node == node]
        assert ups == ["eviction_order"]
    assert nodes["eviction_order"].unit == "persons"
    assert nodes["emergency_shelter_use"].unit == "rate_ratio"
    assert nodes["eviction_earnings_response"].unit == "gap_multiplier"


def test_audit_clean():
    findings = audit()
    errors = [f for f in findings if f.severity == "ERROR"]
    assert errors == []
