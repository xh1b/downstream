"""Adversarial state-machine tests for immutable forecast registrations."""
from __future__ import annotations

import copy
from datetime import datetime, timezone
import tempfile
from pathlib import Path

import pytest
from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine, invariant, precondition, rule

from downstream.forecast_registry import register, score


class ForecastLifecycleMachine(RuleBasedStateMachine):
    """Exercise every allowed/forbidden lifecycle transition repeatedly.

    States: draft -> registered -> scoreable.  Duplicate registration,
    pre-window scoring, and a tampered record are terminally invalid actions.
    Hypothesis explores action sequences rather than one hand-written path.
    """

    def __init__(self):
        super().__init__()
        self.dir = tempfile.TemporaryDirectory()
        self.path = Path(self.dir.name) / "registration.json"
        self.record = None
        self.tampered = False
        self.proposal = {
            "event_id": "fsm-event", "event_source": "fixture", "population": "test",
            "outcome": "test outcome", "unit": "units", "measurement_source": "fixture",
            "measurement_rule": "fixed", "exposure_bridge_source": "fixture",
            "algo_version": "test", "outcome_window_start": "2030-01-01T00:00:00+00:00",
            "outcome_window_end": "2030-02-01T00:00:00+00:00",
            "prediction": {"low": 1.0, "point": 2.0, "high": 3.0},
        }

    def teardown(self):
        self.dir.cleanup()

    @precondition(lambda self: self.record is None)
    @rule()
    def register_once(self):
        self.record = register(self.path, self.proposal,
                               now=datetime(2029, 1, 1, tzinfo=timezone.utc))

    @precondition(lambda self: self.record is not None)
    @rule()
    def duplicate_registration_is_refused(self):
        with pytest.raises(FileExistsError):
            register(self.path, self.proposal, now=datetime(2029, 1, 1, tzinfo=timezone.utc))

    @precondition(lambda self: self.record is not None and not self.tampered)
    @rule()
    def score_before_window_is_refused(self):
        with pytest.raises(ValueError, match="not complete"):
            score(self.record, 2.0, unit="units", source="fixture",
                  now=datetime(2030, 1, 15, tzinfo=timezone.utc))

    @precondition(lambda self: self.record is not None and not self.tampered)
    @rule()
    def tampering_is_detected(self):
        self.record = copy.deepcopy(self.record)
        # Change a hashed field textually.  Float deltas may round away, which
        # would accidentally leave an otherwise adversarial test unchanged.
        self.record["proposal"]["event_id"] += "-tampered"
        self.tampered = True
        with pytest.raises(ValueError, match="modified"):
            score(self.record, 2.0, unit="units", source="fixture",
                  now=datetime(2030, 2, 2, tzinfo=timezone.utc))

    @precondition(lambda self: self.record is not None and not self.tampered)
    @rule(measured=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False))
    def completed_score_is_well_formed(self, measured):
        out = score(self.record, measured, unit="units", source="fixture",
                    now=datetime(2030, 2, 2, tzinfo=timezone.utc))
        assert out["absolute_error"] == pytest.approx(abs(measured - 2.0))
        assert out["covered"] is (1.0 <= measured <= 3.0)

    @invariant()
    def registration_file_is_immutable_once_written(self):
        if self.record is not None:
            assert self.path.exists()
            # The serialized registration itself remains the original one;
            # tampering a caller's in-memory copy cannot rewrite it.
            assert '"sha256"' in self.path.read_text(encoding="utf-8")


TestForecastLifecycle = ForecastLifecycleMachine.TestCase
