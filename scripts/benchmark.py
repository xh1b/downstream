"""Reproducible local microbenchmarks for the public numerical paths."""
from __future__ import annotations

import json
import platform
from statistics import median
from time import perf_counter

from downstream.children import child_line
from downstream.mc import simulate
from downstream.params import load_all
from downstream.scenario import ScenarioInput, compute_counts, sample_counts
from downstream.sensitivity import sobol_indices


def measure(name, fn, repeats=5):
    samples = []
    for _ in range(repeats):
        started = perf_counter()
        fn()
        samples.append((perf_counter() - started) * 1000)
    return {"name": name, "repeats": repeats, "median_ms": round(median(samples), 3),
            "min_ms": round(min(samples), 3), "max_ms": round(max(samples), 3)}


def main():
    parts = load_all()
    params, baselines, nodes = parts["params"], parts["baselines"], parts["nodes"]
    scenario = ScenarioInput(displaced_workers=1_000)
    def child(ps):
        return child_line(ps)["grandchild"].point
    rows = [
        measure("scenario_deterministic", lambda: compute_counts(params, baselines, scenario), repeats=20),
        measure("scenario_parameter_interval_1000", lambda: sample_counts(
            params, baselines, scenario, draws=1_000, nodes=nodes), repeats=3),
        measure("child_mc_1000", lambda: simulate(params, child, draws=1_000, nodes=nodes), repeats=3),
        measure("sobol_child_base_32", lambda: sobol_indices(params, child, nodes, base=32), repeats=1),
    ]
    print(json.dumps({"schema": "downstream-benchmark/1",
                      "environment": {
                          "python": platform.python_version(),
                          "platform": platform.platform(),
                          "machine": platform.machine(),
                      },
                      "results": rows,
                      "note": "Local microbenchmark; compare like-for-like hardware and Python versions."}, indent=2))


if __name__ == "__main__":
    main()
