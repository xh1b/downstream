import pytest

from downstream.county_mortality import count_observations, parse_export


def test_suppression_and_pooled_denominator(tmp_path):
    path = tmp_path / "county.txt"
    path.write_text('"County Code"\t"Deaths"\t"Population"\n'
                    '"01001"\t"20"\t"10000"\n'
                    '"01003"\t"Suppressed"\t"1000"\n'
                    '"01005"\t"9"\t"1000"\n')
    metadata = dict(years=[2015, 2016, 2017, 2018, 2019], sex="Male", age="45-54 years",
                    group_by=["County"], population_unit="person-years", source_url="fixture", retrieved_at="fixture")
    out = parse_export(path, metadata=metadata)
    assert out['rows'] == {'01001': {'mortality_rate': 0.002, 'mortality_n': 20}}
    observation = count_observations(out)[0]
    assert (observation.key, observation.events, observation.person_years) == ("01001", 20, 10000)
    assert observation.time_window == "2015-2019"
    assert out['suppressed_count'] == 2
    with pytest.raises(ValueError, match="sex"):
        parse_export(path, metadata={**metadata, 'sex': 'All'})
    path.write_text(path.read_text() + '"01001"\t"30"\t"10000"\n')
    with pytest.raises(ValueError, match="duplicate"):
        parse_export(path, metadata=metadata)


def test_wonder_posterior_cli_uses_validated_export(tmp_path, capsys):
    export = tmp_path / "county.tsv"
    export.write_text('"County Code"\t"Deaths"\t"Population"\n"01001"\t"20"\t"10000"\n')
    metadata = tmp_path / "metadata.json"
    metadata.write_text('{"years":[2015,2016,2017,2018,2019],"sex":"Male","age":"45-54 years","group_by":["County"],"population_unit":"person-years","source_url":"fixture","retrieved_at":"fixture"}')
    from downstream.cli import main
    assert main(["county-wonder-posterior", "--export", str(export), "--metadata", str(metadata),
                 "--key", "01001", "--national-rate", ".004944", "--prior-person-years", "2000", "--draws", "8"]) == 0
    import json
    out = json.loads(capsys.readouterr().out)
    assert out["observation"]["events"] == 20
    assert out["wonder_export"]["suppressed_count"] == 0
