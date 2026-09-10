"""Versioned demographic mortality-baseline profiles.

Profiles are rate inputs, not causal-effect modifiers.  A scenario may use one
verified profile or a declared mixture of verified profiles; absent profiles
fall back to the historical baseline row for backward compatibility.
"""
from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class MortalityBaselineProfile:
    profile_id: str
    sex: str
    age: str
    years: str
    cause: str
    geography: str
    annual_rate: float | None
    population_scope: str
    citation: str
    status: str
    notes: str = ""


def load_profiles(path: str | Path) -> dict[str, MortalityBaselineProfile]:
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(line for line in handle if not line.lstrip().startswith("#"))
        required = {"profile_id", "sex", "age", "years", "cause", "geography", "annual_rate", "population_scope", "citation", "status"}
        if reader.fieldnames is None or not required <= set(reader.fieldnames):
            raise ValueError(f"mortality profile CSV requires {sorted(required)}")
        out = {}
        for row in reader:
            profile_id = row["profile_id"].strip()
            raw_rate = row["annual_rate"].strip()
            rate = float(raw_rate) if raw_rate else None
            profile = MortalityBaselineProfile(
                profile_id, row["sex"].strip(), row["age"].strip(), row["years"].strip(),
                row["cause"].strip(), row["geography"].strip(), rate,
                row["population_scope"].strip(), row["citation"].strip(), row["status"].strip(),
                row.get("notes", "").strip(),
            )
            if not profile_id or profile_id in out:
                raise ValueError(f"duplicate or blank mortality profile {profile_id!r}")
            if not all((getattr(profile, field) for field in ("sex", "age", "years", "cause", "geography", "population_scope", "citation", "status"))):
                raise ValueError(f"mortality profile {profile_id!r} has blank metadata")
            if rate is not None and (not math.isfinite(rate) or rate < 0):
                raise ValueError(f"mortality profile {profile_id!r} has invalid annual_rate")
            if profile.status == "verified" and rate is None:
                raise ValueError(f"verified mortality profile {profile_id!r} needs annual_rate")
            out[profile_id] = profile
    return out


def resolve_mix(profiles: dict[str, MortalityBaselineProfile], profile_id: str | None,
                mixture: dict[str, float] | None) -> list[tuple[MortalityBaselineProfile, float]]:
    if profile_id and mixture:
        raise ValueError("mortality_profile and mortality_mix are mutually exclusive")
    weights = {profile_id: 1.0} if profile_id else (mixture or {})
    if not weights:
        return []
    if not all(isinstance(k, str) and k and isinstance(v, (int, float)) and not isinstance(v, bool)
               and math.isfinite(v) and v >= 0 for k, v in weights.items()):
        raise ValueError("mortality mix needs nonempty profile ids and finite nonnegative weights")
    total = sum(weights.values())
    if total <= 0 or abs(total - 1.0) > 1e-8:
        raise ValueError("mortality mix weights must sum to 1")
    out = []
    for key, weight in weights.items():
        try:
            profile = profiles[key]
        except KeyError as exc:
            raise KeyError(f"unknown mortality profile {key!r}") from exc
        if profile.status != "verified" or profile.annual_rate is None:
            raise ValueError(f"mortality profile {key!r} is status={profile.status!r}; it cannot produce counts")
        out.append((profile, float(weight)))
    return out


def validate_sullivan_von_wachter_applicability(
    resolved: list[tuple[MortalityBaselineProfile, float]],
) -> dict:
    """Check the demographic scope of the shipped mortality response profile.

    The response coefficients were estimated for high-tenure male workers in
    the 45--54 age range. A different baseline rate is not evidence that the
    relative displacement response transports to women or another age band.
    Geography and calendar-time transport remain explicit assumptions rather
    than a false exact-match claim.
    """
    incompatible = [p.profile_id for p, _ in resolved if p.sex != "Male" or p.age != "45-54 years"]
    if incompatible:
        raise ValueError(
            "shipped mortality response applies only to Male, 45-54 years profiles; "
            f"incompatible profile(s): {', '.join(incompatible)}. Add a separately admitted effect profile before computing a causal mortality contrast."
        )
    return {
        "status": "demographic_scope_match",
        "matched": [p.profile_id for p, _ in resolved],
        "remaining_transport_assumptions": [
            "Pennsylvania early-1980s mass-layoff response transported to the selected geography",
            "historical recession severity and tenure composition transport to the target scenario",
        ],
    }
