# @ref:code-source-support
# Contract: @link:source-withdrawal-contract.
# Verification: @link:test-source-withdrawals.
# @tag:evidence
"""Source-review withdrawals apply to defaults, overrides and sampled models."""
from __future__ import annotations

from dataclasses import dataclass
from functools import cache
import hashlib
import json


@cache
def _policy_path():
    # Use the engine's reviewed policy even for custom parameter directories.
    from .params import default_dir
    return default_dir() / 'source_support.json'


@cache
def policy():
    value = json.loads(_policy_path().read_text(encoding="utf-8"))
    if value.get('schema') != 'downstream-source-support/1':
        raise ValueError('invalid source-support policy schema')
    rows = value.get('withdrawn_parameters')
    if not isinstance(rows, dict) or any(
        row.get('status') != 'withdrawn' or not row.get('reason')
        for row in rows.values()
    ):
        raise ValueError('invalid source-support withdrawal records')
    return value


def policy_sha256():
    return hashlib.sha256(_policy_path().read_bytes()).hexdigest()


class SourceUnavailable(ValueError):
    def __init__(self, link):
        self.link = link
        self.reason = policy()['withdrawn_parameters'][link]['reason']
        super().__init__(f'source withdrawn for {link}: {self.reason}')


def require_supported(link):
    if link in policy()['withdrawn_parameters']:
        raise SourceUnavailable(link)


def is_withdrawn(link):
    return link in policy()['withdrawn_parameters']


@dataclass(frozen=True)
class UnavailableLedger:
    """Explicit nonnumeric result for a withdrawn grouped-model branch."""
    label: str
    unit: str
    source_error: SourceUnavailable
    steps: tuple = ()

    @property
    def point(self):
        raise self.source_error

    @property
    def low(self):
        raise self.source_error

    @property
    def high(self):
        raise self.source_error

    def apply(self, *_args, **_kwargs):
        raise self.source_error

    def as_dict(self):
        return {'label': self.label, 'unit': self.unit, 'available': False,
                'point': None, 'low': None, 'high': None, 'steps': [],
                'blocked': str(self.source_error), 'source_status': 'withdrawn',
                'withdrawn_input': self.source_error.link}
