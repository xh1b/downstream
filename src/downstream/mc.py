"""Monte Carlo propagation over parameter uncertainty.

v1.2 methodology: Latin Hypercube Sampling over the parameter space,
log-space sampling for positive ratio parameters, and optional
declared rank correlation (Iman-Conover). Every draw rebuilds the
full module compute, so nonlinear gap composition propagates
correctly. Outputs carry the parameter-set version (marked
`-sampled`), the seed, and the draw count — published ranges are
always reproducible.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from .distributions import materialize_parameter_set, plan
from .params import ParameterSet, load_correlations, spearman_matrix


def _declared_spearman(params: ParameterSet, params_dir: Path | None) -> tuple[list[list[float]] | None, int]:
    """Load params/correlations.csv and map it onto the row order.

    Returns (matrix, n_pairs); (None, 0) when nothing is declared.
    """
    d = params_dir if params_dir is not None else _default_params_dir()
    corr_path = Path(d) / "correlations.csv"
    if not corr_path.exists():
        return None, 0
    correlations = load_correlations(corr_path)
    mat = spearman_matrix(params, correlations)
    return mat, len(correlations)


def _default_params_dir():
    from .params import default_dir

    return default_dir()


def simulate(
    params: ParameterSet,
    compute: Callable[[ParameterSet], float],
    draws: int = 10_000,
    seed: int = 1901,
    nodes: dict | None = None,
    spearman: list[list[float]] | None = None,
    use_declared_correlations: bool = True,
    params_dir=None,
) -> dict:
    """Run `compute` over draws of the parameter space.

    `compute` takes a perturbed ParameterSet and returns the scalar
    outcome to sample. Sampling is LHS by default; when `spearman` is
    None and `use_declared_correlations` is true, the declared matrix
    from params/correlations.csv is applied (Iman-Conover) and the
    sampler stamps `lhs+iman-conover`. Pass `spearman` explicitly to
    override; pass `use_declared_correlations=False` for raw LHS.
    """
    if nodes is None:
        from .params import default_dir, load_nodes

        try:
            nodes = load_nodes((Path(params_dir) if params_dir is not None else default_dir()) / "nodes.csv")
        except OSError:
            nodes = {}

    n_pairs = 0
    if spearman is None and use_declared_correlations:
        spearman, n_pairs = _declared_spearman(params, params_dir)
    if spearman is not None and n_pairs == 0:
        n_pairs = sum(
            1
            for i in range(len(spearman))
            for j in range(i + 1, len(spearman))
            if spearman[i][j] != 0
        )

    dp = plan(params, nodes, draws, seed, spearman=spearman)
    samples: list[float] = []
    for k in range(draws):
        samples.append(compute(materialize_parameter_set(params, nodes, dp.u[k], dp.dists)))
    samples.sort()

    def pct(p: float) -> float:
        return samples[min(int(p * (draws - 1)), draws - 1)]

    return {
        "draws": draws,
        "seed": seed,
        "sampler": "lhs+iman-conover" if spearman is not None else "lhs",
        "correlations_applied": n_pairs if spearman is not None else 0,
        "parameter_set_version": f"{params.version.split('-sampled')[0]}-sampled",
        "p05": round(pct(0.05), 4),
        "p50": round(pct(0.50), 4),
        "p95": round(pct(0.95), 4),
        "mean": round(sum(samples) / draws, 4),
    }


def simulate_many(
    params: ParameterSet,
    compute: Callable[[ParameterSet], dict[str, float]],
    draws: int = 10_000,
    seed: int = 1901,
    nodes: dict | None = None,
    spearman: list[list[float]] | None = None,
    use_declared_correlations: bool = True,
    params_dir=None,
    include_samples: bool = False,
) -> dict:
    """Sample several related scalar outcomes on the *same* parameter draws.

    This is deliberately separate from :func:`simulate`: scenarios need
    count intervals for mortality and dollar losses that retain their joint
    parameter dependence. Running one independent simulation per headline
    would make their intervals individually valid but destroy that useful
    dependence for downstream consumers.
    """
    if nodes is None:
        from .params import default_dir, load_nodes

        try:
            nodes = load_nodes((Path(params_dir) if params_dir is not None else default_dir()) / "nodes.csv")
        except OSError:
            nodes = {}
    n_pairs = 0
    if spearman is None and use_declared_correlations:
        spearman, n_pairs = _declared_spearman(params, params_dir)
    if spearman is not None and n_pairs == 0:
        n_pairs = sum(1 for i in range(len(spearman)) for j in range(i + 1, len(spearman))
                      if spearman[i][j] != 0)
    dp = plan(params, nodes, draws, seed, spearman=spearman)
    samples: dict[str, list[float]] = {}
    for k in range(draws):
        values = compute(materialize_parameter_set(params, nodes, dp.u[k], dp.dists))
        for name, value in values.items():
            if not isinstance(value, (int, float)):
                raise TypeError(f"sampled outcome {name!r} must be numeric")
            samples.setdefault(name, []).append(float(value))

    raw_samples = {name: values[:] for name, values in samples.items()} if include_samples else None

    def summary(values: list[float]) -> dict:
        values.sort()
        n = len(values)
        def pct(percentile):
            return values[min(int(percentile * (n - 1)), n - 1)]
        return {"p05": round(pct(.05), 4), "p50": round(pct(.50), 4),
                "p95": round(pct(.95), 4), "mean": round(sum(values) / n, 4)}

    out = {
        "draws": draws,
        "seed": seed,
        "sampler": "lhs+iman-conover" if spearman is not None else "lhs",
        "correlations_applied": n_pairs if spearman is not None else 0,
        "parameter_set_version": f"{params.version.split('-sampled')[0]}-sampled",
        "outcomes": {name: summary(values) for name, values in samples.items()},
    }
    if raw_samples is not None:
        # Internal caller hook for posterior-predictive layers.  Kept opt-in
        # so ordinary public MC responses remain compact and JSON-stable.
        out["_raw_samples"] = raw_samples
    return out


def simulate_chain(
    params: ParameterSet,
    links: list[str],
    base: float = 1.0,
    label: str = "chain",
    draws: int = 10_000,
    seed: int = 1901,
    kinds: list[str] | None = None,
    nodes: dict | None = None,
    use_declared_correlations: bool = True,
    params_dir=None,
) -> dict:
    """Convenience wrapper: sample a named chain of links.

    Kinds are required: arbitrary links have no safe default composition.
    """
    from .ledger import chain

    if kinds is None:
        raise ValueError("arbitrary chains require explicit composition kinds")
    if nodes is None:
        from .params import default_dir, load_nodes
        nodes = load_nodes((Path(params_dir) if params_dir is not None else default_dir()) / "nodes.csv")
    from .ledger import validate_chain
    validate_chain(params, links, kinds, nodes)

    def compute(ps: ParameterSet) -> float:
        return chain(ps, links, label=label, unit="gap_multiplier", kinds=kinds, nodes=nodes,
                     base=base).point

    out = simulate(
        params,
        compute,
        draws=draws,
        seed=seed,
        nodes=nodes,
        use_declared_correlations=use_declared_correlations,
        params_dir=params_dir,
    )
    out["label"] = label
    out["links"] = links
    out["kinds"] = kinds
    return out
