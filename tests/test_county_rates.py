import pytest

from downstream.county_rates import (
    CountyRateObservation,
    NationalRatePrior,
    beta_binomial_posterior,
    load_county_rates,
    poisson_gamma_posterior,
)


def test_beta_binomial_posterior_shrinks_sparse_county_and_is_seeded():
    row = CountyRateObservation("01001", "mortality", 2, 1_000, "prime-age men", "2015-19", "source")
    a = beta_binomial_posterior(row, .005, 2_000, draws=200, seed=4)
    b = beta_binomial_posterior(row, .005, 2_000, draws=200, seed=4)
    assert a == b
    assert .002 < a["posterior"]["mean"] < .005
    assert a["posterior"]["p05"] <= a["posterior"]["p50"] <= a["posterior"]["p95"]


def test_beta_binomial_refuses_non_probability_or_nonpositive_prior():
    row = CountyRateObservation("01001", "mortality", 2, 1_000, "prime-age men", "2015-19", "source")
    with pytest.raises(ValueError):
        beta_binomial_posterior(row, 0, 2_000)
    with pytest.raises(ValueError):
        beta_binomial_posterior(row, .005, 0)


def test_poisson_gamma_accepts_person_time_and_requires_prior_metadata():
    row = CountyRateObservation("01001", "mortality", 12, 2.5, "prime-age men", "2015-19", "source")
    prior = NationalRatePrior("mortality", .005, "prime-age men", "2015-19", "national source")
    out = poisson_gamma_posterior(row, prior, 2_000, draws=50, seed=4)
    assert out["method"].startswith("Gamma-Poisson")
    assert out["posterior"]["mean_annual_risk_constant_hazard"] < 1
    with pytest.raises(ValueError, match="identical outcome"):
        poisson_gamma_posterior(row, NationalRatePrior("mortality", .005, "other", "2015-19", "x"), 2_000)


def _write_rates_csv(tmp_path, text):
    path = tmp_path / "county_rates.csv"
    path.write_text(text, encoding="utf-8")
    return path


VALID_CSV = """# comment lines are skipped
key,outcome,events,person_years,population_scope,time_window,citation
01001,mortality,12,2.5,prime-age men,2015-19,national source
01003,mortality,0,10.0,prime-age men,2015-19,national source
"""


def test_load_county_rates_reads_counts_and_skips_comments(tmp_path):
    rows = load_county_rates(_write_rates_csv(tmp_path, VALID_CSV))
    assert len(rows) == 2
    assert rows[0] == CountyRateObservation("01001", "mortality", 12, 2.5, "prime-age men", "2015-19", "national source")
    assert rows[1].events == 0 and rows[1].person_years == 10.0


def test_load_county_rates_requires_count_columns(tmp_path):
    path = _write_rates_csv(tmp_path, "key,outcome,rate,person_years,population_scope,time_window,citation\n01001,mortality,0.005,2.5,prime-age men,2015-19,src\n")
    with pytest.raises(ValueError, match="requires columns"):
        load_county_rates(path)


def test_load_county_rates_refuses_unparseable_counts(tmp_path):
    base = "key,outcome,events,person_years,population_scope,time_window,citation\n"
    for bad in ("01001,mortality,many,2.5,prime-age men,2015-19,src\n",
                "01001,mortality,,2.5,prime-age men,2015-19,src\n",
                "01001,mortality,1,not-years,prime-age men,2015-19,src\n"):
        with pytest.raises(ValueError, match="invalid county-rate row"):
            load_county_rates(_write_rates_csv(tmp_path, base + bad))


def test_load_county_rates_refuses_empty_metadata(tmp_path):
    base = "key,outcome,events,person_years,population_scope,time_window,citation\n"
    for bad in (",mortality,1,2.5,prime-age men,2015-19,src\n",
                "01001,   ,1,2.5,prime-age men,2015-19,src\n",
                "01001,mortality,1,2.5,prime-age men,2015-19, \n"):
        with pytest.raises(ValueError, match="may not be empty"):
            load_county_rates(_write_rates_csv(tmp_path, base + bad))


def test_load_county_rates_validates_event_and_person_year_domains(tmp_path):
    base = "key,outcome,events,person_years,population_scope,time_window,citation\n"
    for bad in ("01001,mortality,-1,2.5,prime-age men,2015-19,src\n",
                "01001,mortality,1,0,prime-age men,2015-19,src\n",
                "01001,mortality,1,-3,prime-age men,2015-19,src\n"):
        with pytest.raises(ValueError, match="nonnegative events"):
            load_county_rates(_write_rates_csv(tmp_path, base + bad))


def test_load_county_rates_refuses_duplicate_observations(tmp_path):
    text = ("key,outcome,events,person_years,population_scope,time_window,citation\n"
            "01001,mortality,1,2.5,prime-age men,2015-19,src\n"
            "01001,mortality,2,3.5,prime-age men,2015-19,src\n")
    with pytest.raises(ValueError, match="duplicate"):
        load_county_rates(_write_rates_csv(tmp_path, text))


def test_load_county_rates_allows_same_key_across_windows(tmp_path):
    text = ("key,outcome,events,person_years,population_scope,time_window,citation\n"
            "01001,mortality,1,2.5,prime-age men,2015-19,src\n"
            "01001,mortality,2,3.5,prime-age men,2020-24,src\n")
    assert len(load_county_rates(_write_rates_csv(tmp_path, text))) == 2


def test_poisson_gamma_prior_checks():
    row = CountyRateObservation("01001", "mortality", 12, 2.5, "prime-age men", "2015-19", "source")
    prior = NationalRatePrior("mortality", .005, "prime-age men", "2015-19", "")
    with pytest.raises(ValueError, match="needs a citation"):
        poisson_gamma_posterior(row, prior, 2_000)
    with pytest.raises(ValueError, match="finite and positive"):
        poisson_gamma_posterior(row, NationalRatePrior("mortality", 0, "prime-age men", "2015-19", "src"), 2_000)
    with pytest.raises(ValueError, match="finite and positive"):
        poisson_gamma_posterior(row, NationalRatePrior("mortality", float("nan"), "prime-age men", "2015-19", "src"), 2_000)
    with pytest.raises(ValueError, match="prior_person_years"):
        poisson_gamma_posterior(row, NationalRatePrior("mortality", .005, "prime-age men", "2015-19", "src"), float("inf"))


def test_poisson_gamma_validates_draws():
    row = CountyRateObservation("01001", "mortality", 12, 2.5, "prime-age men", "2015-19", "source")
    prior = NationalRatePrior("mortality", .005, "prime-age men", "2015-19", "src")
    for bad in (True, 1, 0, -5, 2.5, "many"):
        with pytest.raises(ValueError, match="draws"):
            poisson_gamma_posterior(row, prior, 2_000, draws=bad)
