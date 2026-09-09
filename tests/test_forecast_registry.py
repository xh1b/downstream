from datetime import datetime, timezone

import pytest

from downstream.forecast_registry import register, score


def proposal():
    return dict(event_id="synthetic-test", event_source="fixture", population="fixture",
                outcome="service jobs", unit="jobs", measurement_source="fixture",
                measurement_rule="fixed window change", exposure_bridge_source="fixture",
                algo_version="fixture", outcome_window_start="2090-01-01T00:00:00Z",
                outcome_window_end="2091-01-01T00:00:00Z",
                prediction=dict(low=2, point=3, high=4))


def test_no_retrospective_or_mutated_forecasts(tmp_path):
    before = datetime(2089, 1, 1, tzinfo=timezone.utc)
    after = datetime(2092, 1, 1, tzinfo=timezone.utc)
    path = tmp_path / "registered.json"
    out = register(path, proposal(), now=before)
    with pytest.raises(FileExistsError):
        register(path, proposal(), now=before)
    with pytest.raises(ValueError, match="precede"):
        register(tmp_path / "late", proposal(), now=after)
    with pytest.raises(ValueError, match="not complete"):
        score(out, 7, unit="jobs", source="fixture", now=before)
    scored = score(out, 7, unit="jobs", source="fixture", now=after)
    assert scored["covered"] is False
    assert scored["absolute_error"] == 4
    out["proposal"]["prediction"]["high"] = 8
    with pytest.raises(ValueError, match="modified"):
        score(out, 7, unit="jobs", source="fixture", now=after)
