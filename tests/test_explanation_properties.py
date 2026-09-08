"""Explanation + rendering checks, and cross-cutting properties.

The properties here are the model's constitution: they must hold for
ANY parameter set and ANY seed, not just the shipped one.
"""

import random
from pathlib import Path

import pytest

from downstream.citations import parse_bib
from downstream.children import child_line
from downstream.explanation import Explanation, Step, explain_child_line
from downstream.params import default_dir, load, load_all
from downstream.render import load_citations, render_text, validate_rendered
from downstream.scenario import ScenarioInput, compute_counts
from downstream.vignette import standard_family

PARAMS_DIR = default_dir()


def test_every_step_of_the_explanation_is_cited_and_attributed():
    exp = explain_child_line(load(PARAMS_DIR / "parameters.csv"), draws=500)
    assert exp.steps
    for s in exp.steps:
        assert s.citations, f"uncited step {s.label}"
        assert s.tier
        assert 0 < abs(s.contribution) < 1.05
    total = sum(s.contribution for s in exp.steps)
    assert total == pytest.approx(1.0, abs=0.01)


def test_explanation_values_match_the_deterministic_model():
    params = load(PARAMS_DIR / "parameters.csv")
    exp = explain_child_line(params, draws=500)
    gc = child_line(params)["grandchild"]
    assert exp.value[0] == pytest.approx(gc.point, abs=1e-6)


def test_explanation_is_reproducible_by_seed():
    params = load(PARAMS_DIR / "parameters.csv")
    a = explain_child_line(params, draws=300, seed=42).as_dict()
    b = explain_child_line(params, draws=300, seed=42).as_dict()
    assert a == b


def test_drivers_are_populated_with_sentences():
    exp = explain_child_line(load(PARAMS_DIR / "parameters.csv"), draws=500)
    assert 1 <= len(exp.drivers) <= 3
    for d in exp.drivers:
        assert 0.01 <= d["share_of_uncertainty"] <= 1.2
        assert d["sentence"].endswith(".")


def test_render_layers_all_present_and_banded():
    parts = load_all(PARAMS_DIR)
    exp = explain_child_line(parts["params"], draws=500)
    load_citations(parts["bib"])
    text = render_text(exp)
    assert "Modeled result" in text
    assert "Why: the cited chain" in text
    assert "What drives the remaining range" in text
    assert "What would prove this wrong" in text
    # no naked numbers: every applied-parameter rendering carries the
    # band brackets, and every step line carries an evidence tier
    for line in text.splitlines():
        if "Applied:" in line:
            assert " to " in line, f"naked estimate: {line}"
            assert "evidence tier" in line, f"uncited step line: {line}"


def test_render_guard_rejects_unlabeled_claims():
    assert validate_rendered("Something Modeled result text") == []
    problems = validate_rendered("point estimate only")
    assert problems


def test_sobol_driver_claim_matches_bounded_share():
    exp = explain_child_line(load(PARAMS_DIR / "parameters.csv"), draws=500)
    for d in exp.drivers:
        assert d["share_of_uncertainty"] >= 0


# ---- cross-cutting properties -------------------------------------------


def _sampled_params(params, rng):
    ps = params
    for p in params.parameters:
        lo, hi = sorted((p.low, p.high))
        ps = ps.with_param(p.link, rng.uniform(lo, hi))
    return ps


def test_property_bands_never_invert_under_random_parameters():
    """For ANY draw of the parameter space, every ledger output keeps
    low <= point <= high. This is the invariant the v0 band bug broke."""
    from downstream.worker import worker_outcomes

    params = load(PARAMS_DIR / "parameters.csv")
    rng = random.Random(17)
    for _ in range(50):
        ps = _sampled_params(params, rng)
        for ledger in child_line(ps).values():
            if hasattr(ledger, "point"):
                assert ledger.low <= ledger.point <= ledger.high
        for ledger in worker_outcomes(ps).values():
            assert ledger.low <= ledger.point <= ledger.high


def test_property_worker_line_is_monotone_in_shock_depth():
    from downstream.worker import worker_earnings

    params = load(PARAMS_DIR / "parameters.csv")
    prev = None
    for m in (0.95, 0.85, 0.75, 0.65):
        v = worker_earnings(params, wage_multiplier=m).point
        if prev is not None:
            assert v < prev
        prev = v


def test_property_scenario_is_linear_in_exposure():
    parts = load_all(PARAMS_DIR)
    jobs = [
        compute_counts(parts["params"], parts["baselines"], ScenarioInput(displaced_workers=n))
        ["modeled"]["local_service_jobs_lost"]["point"]
        for n in (10, 100, 1000)
    ]
    assert jobs[1] == pytest.approx(10 * jobs[0])
    assert jobs[2] == pytest.approx(10 * jobs[1])


def test_property_all_monte_carlo_outputs_stamp_sampled_version():
    from downstream.mc import simulate

    params = load(PARAMS_DIR / "parameters.csv")
    out = simulate(params, lambda ps: ps.by_link("displacement->child_earnings").point, draws=50)
    assert out["parameter_set_version"].endswith("-sampled")
    # v1.27: declared correlations apply by default, so the sampler
    # stamps the induction on the output
    assert out["sampler"] == "lhs+iman-conover"


def test_property_vignette_never_claims_determinism():
    parts = load_all(PARAMS_DIR)
    out = standard_family(parts["params"])
    text = str(out)
    assert "never a deterministic claim" in text
