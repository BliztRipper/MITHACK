import importlib.util
import pathlib

import pytest

_p = pathlib.Path(__file__).resolve().parents[2] / "ml" / "prepare_data.py"
_spec = importlib.util.spec_from_file_location("prepare_data", _p)
pd = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pd)

COLS = ["ID", "Disease_Risk", "DR", "BRVO", "CRVO", "ODE", "AION", "OTHER"]


def rows(*specs):  # spec = (id, {col: 1})
    return [dict.fromkeys(COLS, "0") | {"ID": i} | {k: str(v) for k, v in on.items()} for i, on in specs]


def test_filter_keeps_normal_and_mimics_drops_rest_and_rao():
    r = rows(("1", {}),                          # normal
             ("2", {"Disease_Risk": 1, "CRVO": 1}),  # mimic
             ("3", {"Disease_Risk": 1, "DR": 1}),    # other disease, dropped
             ("4", {"Disease_Risk": 1, "AION": 1}),  # mimic but RAO -> dropped
             ("5", {"Disease_Risk": 1, "OTHER": 1}))
    assert pd.select_other(r, {"4"}) == {"1", "2"}


def test_missing_rao_id_fails():
    with pytest.raises(SystemExit, match="leakage"):
        pd.select_other(rows(("1", {})), {"999"})


def test_missing_column_fails():
    with pytest.raises(SystemExit, match="columns"):
        pd.select_other([{"ID": "1", "Disease_Risk": "0"}], set())


def test_rfmid_id():
    assert pd.rfmid_id("217.png") == "217" and pd.rfmid_id("91_0.png") == "91"
