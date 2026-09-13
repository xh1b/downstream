import pytest
from pathlib import Path

from downstream.county_mortality import count_observations, parse_export


def test_suppression_and_pooled_denominator(tmp_path):
    path = tmp_path / "county.txt"
    path.write_text('"County Code"\t"Deaths"\t"Population"\n'
                    '"01001"\t"20"\t"10000"\n'
                    '"01003"\t"Suppressed"\t"1000"\n'
                    '"01005"\t"9"\t"1000"\n')
    metadata = dict(years=[2015, 2016, 2017, 2018, 2019], sex="Male", age="45-54 years",
                    cause="All causes", group_by=["County"], population_unit="person-years",
                    source_url="fixture", retrieved_at="fixture")
    out = parse_export(path, metadata=metadata)
    assert out['rows'] == {'01001': {'mortality_rate': 0.002, 'mortality_n': 20}}
    observation = count_observations(out)[0]
    assert (observation.key, observation.events, observation.person_years) == ("01001", 20, 10000)
    assert observation.time_window == "2015-2019"
    assert out['suppressed_count'] == 2
    all_sex = parse_export(path, metadata={**metadata, 'sex': 'All'})
    assert all_sex["query"]["profile"]["sex"] == "All"
    with pytest.raises(ValueError, match="group_by"):
        parse_export(path, metadata={**metadata, 'group_by': ['County', 'Age']})
    path.write_text(path.read_text() + '"01001"\t"30"\t"10000"\n')
    with pytest.raises(ValueError, match="duplicate"):
        parse_export(path, metadata=metadata)


def test_wonder_posterior_cli_uses_validated_export(tmp_path, capsys):
    export = tmp_path / "county.tsv"
    export.write_text('"County Code"\t"Deaths"\t"Population"\n"01001"\t"20"\t"10000"\n')
    metadata = tmp_path / "metadata.json"
    metadata.write_text('{"years":[2015,2016,2017,2018,2019],"sex":"Male","age":"45-54 years","cause":"All causes","group_by":["County"],"population_unit":"person-years","source_url":"fixture","retrieved_at":"fixture"}')
    from downstream.cli import main
    assert main(["county-wonder-posterior", "--export", str(export), "--metadata", str(metadata),
                 "--key", "01001", "--national-rate", ".004944", "--prior-person-years", "2000", "--draws", "8"]) == 0
    import json
    out = json.loads(capsys.readouterr().out)
    assert out["observation"]["events"] == 20
    assert out["wonder_export"]["suppressed_count"] == 0


def _base_metadata(**overrides):
    metadata = dict(years=[2015, 2016, 2017, 2018, 2019], sex="Male", age="45-54 years",
                    cause="All causes", group_by=["County"], population_unit="person-years",
                    source_url="fixture", retrieved_at="fixture")
    metadata.update(overrides)
    return metadata


def test_import_accepts_declared_csv_and_tsv_exports(tmp_path):
    metadata = _base_metadata()
    tsv = tmp_path / "county.txt"
    tsv.write_text('"County Code"\t"Deaths"\t"Population"\n"01001"\t"20"\t"10000"\n')
    assert parse_export(tsv, metadata=metadata)["rows"]["01001"]["mortality_rate"] == 0.002
    csv_export = tmp_path / "county.csv"
    csv_export.write_text('"County Code","Deaths","Population"\n"01001","20","10000"\n')
    assert parse_export(csv_export, metadata=metadata)["rows"]["01001"]["mortality_n"] == 20


def test_import_refuses_ambiguous_metadata(tmp_path):
    path = tmp_path / "county.txt"
    path.write_text('"County Code"\t"Deaths"\t"Population"\n"01001"\t"20"\t"10000"\n')
    for name in ("cause", "population_unit", "source_url", "retrieved_at"):
        stripped = {k: v for k, v in _base_metadata().items() if k != name}
        with pytest.raises(ValueError, match=name):
            parse_export(path, metadata=stripped)
    with pytest.raises(ValueError, match="contiguous"):
        parse_export(path, metadata=_base_metadata(years=[2015, 2017, 2019]))
    with pytest.raises(ValueError, match="unique"):
        parse_export(path, metadata=_base_metadata(years=[2015, 2015, 2016, 2017, 2018, 2019]))
    with pytest.raises(ValueError, match="sex and metadata.age"):
        parse_export(path, metadata=_base_metadata(sex="", age=""))


def test_import_refuses_non_person_year_denominator(tmp_path):
    path = tmp_path / "county.txt"
    path.write_text('"County Code"\t"Deaths"\t"Population"\n"01001"\t"20"\t"10000"\n')
    with pytest.raises(ValueError, match="person-years"):
        parse_export(path, metadata=_base_metadata(population_unit="census mid-year population"))


def test_import_refuses_crude_rate_only_export(tmp_path):
    path = tmp_path / "county.csv"
    path.write_text('"County Code","Deaths","Crude Rate"\n"01001","20","200.0"\n')
    with pytest.raises(ValueError, match="county WONDER"):
        parse_export(path, metadata=_base_metadata())


def test_import_refuses_deaths_exceeding_person_years_and_bad_fips(tmp_path):
    with pytest.raises(ValueError, match="deaths exceed"):
        parse_export(_write_export(tmp_path / "a.txt", '"01001"\t"101"\t"100"\n'),
                     metadata=_base_metadata())
    with pytest.raises(ValueError, match="FIPS"):
        parse_export(_write_export(tmp_path / "b.txt", '"0100"\t"20"\t"10000"\n'),
                     metadata=_base_metadata())


def test_import_refuses_export_without_county_rows(tmp_path):
    path = tmp_path / "empty.txt"
    path.write_text('"County Code"\t"Deaths"\t"Population"\n""\t""\t""\n')
    with pytest.raises(ValueError, match="no county rows"):
        parse_export(path, metadata=_base_metadata())


def test_import_parses_genuine_csv_export_with_footnotes_and_total_row(tmp_path):
    """Genuine WONDER CSV exports: quoted commas in county names, a Total
    row, a '---' separator, and trailing footnotes/query-parameter lines.

    csv.Sniffer mis-handled the quoted commas and shifted footnote text
    into the County Code column (fixed: delimiter detected directly).
    """
    path = tmp_path / "county.csv"
    path.write_text(
        '"Notes","County","County Code",Deaths,Population,Crude Rate\n'
        ',"Autauga County, AL","01001",115,19096,602.2\n'
        ',"Baldwin County, AL","01003",370,68663,538.9\n'
        '"Total",,,514314,104024440,494.4\n'
        '"---"\n'
        '"Dataset: Underlying Cause of Death, 1999-2020"\n'
        '"Sex: Male"\n'
        '"Group By: County"\n'
    )
    parsed = parse_export(path, metadata=_base_metadata())
    assert parsed["rows"]["01001"]["mortality_rate"] == pytest.approx(115 / 19096)
    assert set(parsed["count_rows"]) == {"01001", "01003"}
    observations = count_observations(parsed)
    assert len(observations) == 2


def test_import_parses_the_all_ages_context_export(tmp_path):
    """The real all-ages county context export parses as county context
    (its registry row stays context_only; this pins the file format)."""
    import shutil

    src = Path(__file__).resolve().parent.parent / "validation" / "cdc_wonder_county_all_ages_1999_2020.csv"
    if not src.exists():
        pytest.skip("context export not present")
    work = tmp_path / "context.csv"
    shutil.copy(src, work)
    metadata = _base_metadata(years=list(range(1999, 2021)), sex="All", age="All ages")
    parsed = parse_export(work, metadata=metadata)
    assert len(parsed["count_rows"]) == 3147


def _write_export(path, body):
    path.write_text('"County Code"\t"Deaths"\t"Population"\n' + body)
    return path


def test_count_observations_maps_cause_specific_outcome_ids(tmp_path):
    path = _write_export(tmp_path / "county.txt", '"01001"\t"20"\t"10000"\n')
    all_cause = count_observations(parse_export(path, metadata=_base_metadata()))[0]
    assert all_cause.outcome == "all_cause_mortality_annual"
    overdose = count_observations(
        parse_export(path, metadata=_base_metadata(cause="Drug overdose")))[0]
    assert overdose.outcome == "drug_overdose_mortality_annual"
    assert "cause: Drug overdose" in overdose.population_scope
    # The prior gate then refuses a national all-cause rate for the overdose export.
    from downstream.county_rates import NationalRatePrior, poisson_gamma_posterior
    with pytest.raises(ValueError, match="identical outcome"):
        poisson_gamma_posterior(
            overdose,
            NationalRatePrior("all_cause_mortality_annual", 0.005, overdose.population_scope,
                              overdose.time_window, "fixture"),
            prior_person_years=1000)


def test_wonder_posterior_cli_refuses_undeclared_cause(tmp_path, capsys):
    export = _write_export(tmp_path / "county.tsv", '"01001"\t"20"\t"10000"\n')
    metadata = tmp_path / "metadata.json"
    metadata.write_text('{"years":[2015,2016,2017,2018,2019],"sex":"Male","age":"45-54 years",'
                        '"group_by":["County"],"population_unit":"person-years",'
                        '"source_url":"fixture","retrieved_at":"fixture"}')
    from downstream.cli import main
    with pytest.raises(SystemExit) as exc:
        main(["county-wonder-posterior", "--export", str(export), "--metadata", str(metadata),
              "--key", "01001", "--national-rate", ".004944", "--prior-person-years", "2000"])
    assert exc.value.code == 2
    assert "cause" in capsys.readouterr().err
