"""Property fuzz: the analytic layer vs the MC on random chains.

The adversarial move: stop testing the chains I thought of. Generate
random parameter sets (uniform and log-uniform bands, random level/
direct/gap sequences, random seeds) and demand the exact moment
algebra agree with the sampler every time. Any red here is a real
bug in one of the two implementations — and the closure/correlation
machinery sits on top of both.

Plus the declared-normal trap: a row that declares a normal sampling
dist must be refused by the analytic layer, not silently treated as
uniform.
"""

from __future__ import annotations

import math
import random

import pytest

from downstream.inference import (
    _draw_samples,
    analytic_chain,
    param_moments,
)
from downstream.ledger import chain as ledger_chain
from downstream.params import Parameter, ParameterSet


class _N:
    def __init__(self, name: str, unit: str):
        self.name, self.unit, self.description = name, unit, ""


def _random_params(rng: random.Random, n: int) -> tuple[ParameterSet, dict, list[str], list[str]]:
    """A random DAG chain: n links in sequence, mixed units and kinds."""
    kinds_pool = ["level", "level", "gap", "direct"]
    rows, nodes, links, kinds = [], {}, [], []
    for i in range(n):
        unit = rng.choice(["gap_multiplier", "rate_ratio", "level_ratio"])
        if rng.random() < 0.5:
            unit = "gap_multiplier"
        lo = rng.uniform(0.3, 1.4)
        hi = lo + rng.uniform(0.05, 0.6)
        point = rng.uniform(lo, hi)
        kind = rng.choice(kinds_pool)
        link = f"n{i}->n{i+1}"
        rows.append(
            Parameter(link=link, from_node=f"n{i}", to_node=f"n{i+1}",
                      point=round(point, 6), low=round(lo, 6), high=round(hi, 6),
                      tier="canonical", citation="fuzz", population_scope="fuzz")
        )
        nodes[f"n{i+1}"] = _N(f"n{i+1}", unit)
        links.append(link)
        kinds.append(kind)
    return ParameterSet(version="fuzz", parameters=tuple(rows)), nodes, links, kinds


CASES = [(_random_params(random.Random(1000 + c), 1 + c % 4)) for c in range(24)]


@pytest.mark.parametrize("case", CASES, ids=range(len(CASES)))
def test_exact_moments_match_mc_on_random_chains(case):
    ps, nodes, links, kinds = case
    analytic = analytic_chain(ps, links, kinds, nodes)

    def compute(p: ParameterSet) -> float:
        return ledger_chain(p, links, label="f", unit="gap_multiplier", kinds=kinds).point

    draws = 30_000
    samples = _draw_samples(ps, compute, nodes, draws, seed=17)
    n = len(samples)
    mean_mc = sum(samples) / n
    var_mc = sum((x - mean_mc) ** 2 for x in samples) / (n - 1)
    mean_se = math.sqrt(var_mc / n)
    # mean: 4 sampling SE tolerance (any systematic drift is algebra error)
    assert abs(mean_mc - analytic["mean"]) < 4 * max(mean_se, 1e-12), (
        f"mean drift on chain {links}/{kinds}: exact {analytic['mean']}, "
        f"mc {mean_mc} ({abs(mean_mc - analytic['mean']) / max(mean_se, 1e-12):.1f} SE)"
    )
    # variance: 6% tolerance (MC var estimator noise at 30k draws ~1.2%
    # for normal, more for skewed; 6% catches wrong identities, not noise)
    assert var_mc == pytest.approx(analytic["var"], rel=0.06), (
        f"variance mismatch on chain {links}/{kinds}: "
        f"exact {analytic['var']:.6g}, mc {var_mc:.6g}"
    )


def test_skewness_sign_matches_mc_on_random_chains():
    rng = random.Random(77)
    for _ in range(8):
        ps, nodes, links, kinds = _random_params(rng, 3)
        analytic = analytic_chain(ps, links, kinds, nodes)

        def compute(p: ParameterSet) -> float:
            return ledger_chain(p, links, label="f", unit="gap_multiplier", kinds=kinds).point

        samples = _draw_samples(ps, compute, nodes, 30_000, seed=23)
        n = len(samples)
        m = sum(samples) / n
        m3 = sum((x - m) ** 3 for x in samples) / n
        m2 = sum((x - m) ** 2 for x in samples) / n
        skew_mc = m3 / m2**1.5
        if abs(skew_mc) > 0.15:  # below that, sign is estimation noise
            assert analytic["skewness"] * skew_mc > 0, (
                f"skewness sign flip on {links}/{kinds}: "
                f"exact {analytic['skewness']:.3f}, mc {skew_mc:.3f}"
            )


# --- trap: declared-normal row silently treated as uniform --------------------

def test_declared_normal_refused_by_analytic_layer():
    p = Parameter(
        link="a->b", from_node="a", to_node="b", point=1.0, low=0.9, high=1.1,
        tier="canonical", citation="x", population_scope="t", dist="normal",
    )
    with pytest.raises(NotImplementedError, match="normal"):
        param_moments(p, "gap_multiplier")


def test_distless_row_still_uniform_moments():
    p = Parameter(
        link="a->b", from_node="a", to_node="b", point=1.0, low=0.8, high=1.2,
        tier="canonical", citation="x", population_scope="t",
    )
    m1, m2, m3 = param_moments(p, "gap_multiplier")
    # U(0.8,1.2): E=1.0, E2=(b^3-a^3)/(3(b-a)), E3=(b^4-a^4)/(4(b-a))
    assert (m1, m2, m3) == pytest.approx(
        (1.0, (1.2**3 - 0.8**3) / 1.2, (1.2**4 - 0.8**4) / 1.6)
    )
