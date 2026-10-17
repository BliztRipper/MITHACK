"""PCE reference cases: Goff DC Jr et al., 2013 ACC/AHA Guideline on the Assessment of Cardiovascular
Risk, Circulation 2014;129(suppl 2):S49-S73, online Supplement worked examples
(age 55, TC 213, HDL 50, SBP 120 untreated, non-smoker, no diabetes).
Published values: white woman 2.1%, African-American woman 3.0%, white man 5.3%, African-American man 6.1%.
"""
import pytest

from rules.risk import Inputs, pce


def ex(sex, aa):
    return Inputs(age=55, sex=sex, sbp=120, tc=213, hdl=50, african_american=aa)


@pytest.mark.parametrize("sex,aa,expected", [
    ("female", False, 2.1), ("female", True, 3.0), ("male", False, 5.3), ("male", True, 6.1)])
def test_goff_worked_examples(sex, aa, expected):
    assert pce(ex(sex, aa)).risk == pytest.approx(expected, abs=0.1)


def test_result_carries_population_caveat():
    assert "risk.caveat.pce_not_asian" in pce(ex("female", False)).notes


@pytest.mark.parametrize("field,value", [
    ("age", 39), ("age", 80), ("tc", 129), ("tc", 321), ("hdl", 19), ("hdl", 101), ("sbp", 89), ("sbp", 201)])
def test_out_of_range_is_not_valid_not_clamped(field, value):
    i = ex("female", False)
    setattr(i, field, value)
    r = pce(i)
    assert r.risk is None and r.reason == "risk.not_valid.pce_range"


@pytest.mark.parametrize("field,value", [("age", 40), ("age", 79), ("tc", 130), ("tc", 320), ("hdl", 20), ("hdl", 100), ("sbp", 90), ("sbp", 200)])
def test_range_edges_are_valid(field, value):
    i = ex("male", False)
    setattr(i, field, value)
    assert pce(i).risk is not None


def test_missing_lab_is_not_valid():
    assert pce(Inputs(age=55, sex="male", sbp=120)).risk is None
