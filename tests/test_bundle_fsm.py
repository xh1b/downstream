"""Adversarial workflow tests for the atomic bundle export lifecycle."""
from __future__ import annotations

from pathlib import Path
import tempfile

import pytest
from hypothesis import settings
from hypothesis.stateful import RuleBasedStateMachine, invariant, precondition, rule

from downstream.bundle import export_bundle, verify_bundle


class BundleLifecycleMachine(RuleBasedStateMachine):
    """Bounded lifecycle: absent -> verified bundle -> tampered bundle."""

    def __init__(self):
        super().__init__()
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / "bundle"
        self.manifest = None
        self.tampered = False

    def teardown(self):
        self.directory.cleanup()

    @precondition(lambda self: self.manifest is None)
    @rule()
    def export(self):
        self.manifest = export_bundle(self.path)

    @precondition(lambda self: self.manifest is not None)
    @rule()
    def overwrite_is_refused(self):
        with pytest.raises(FileExistsError):
            export_bundle(self.path)

    @precondition(lambda self: self.manifest is not None and not self.tampered)
    @rule()
    def verify_complete_bundle(self):
        assert verify_bundle(self.path) == self.manifest

    @precondition(lambda self: self.manifest is not None and not self.tampered)
    @rule()
    def tamper_is_detected(self):
        version = self.path / "params" / "VERSION"
        version.write_text(version.read_text(encoding="utf-8") + "tampered", encoding="utf-8")
        self.tampered = True
        with pytest.raises(ValueError, match="checksum"):
            verify_bundle(self.path)

    @precondition(lambda self: self.manifest is not None and self.tampered)
    @rule()
    def repeated_verification_still_refuses_tampering(self):
        with pytest.raises(ValueError, match="checksum"):
            verify_bundle(self.path)

    @invariant()
    def state_has_one_visible_bundle_at_most(self):
        staging = list(self.path.parent.glob(".bundle.staging-*"))
        assert staging == []
        if self.manifest is None:
            assert not self.path.exists()
        else:
            assert (self.path / "manifest.json").is_file()


TestBundleLifecycle = BundleLifecycleMachine.TestCase
TestBundleLifecycle.settings = settings(max_examples=15, stateful_step_count=6, deadline=None)
