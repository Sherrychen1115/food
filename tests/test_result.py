import json

import pytest

from food_agent.analyzer.result import AnalysisError, parse_output


def wrap(payload, structured=True):
    key = "structured_output" if structured else "result"
    return json.dumps({key: payload if structured else json.dumps(payload)})


GOOD = {"kind": "food", "name": "牛肉麵", "ingredients": ["牛肉", "麵條"], "weight_g": 450, "calories_kcal": 620}


def test_good():
    a = parse_output(wrap(GOOD))
    assert (a.kind, a.name, a.weight_g, a.calories_kcal) == ("food", "牛肉麵", 450, 620)


def test_result_text_in_code_fence():
    out = json.dumps({"result": "```json\n" + json.dumps(GOOD) + "\n```"})
    assert parse_output(out).name == "牛肉麵"


@pytest.mark.parametrize(
    "bad",
    [
        {**GOOD, "calories_kcal": "約 500"},
        {**GOOD, "calories_kcal": -5},
        {**GOOD, "calories_kcal": 99999},
        {**GOOD, "weight_g": None},
        {**GOOD, "weight_g": 0},
        {**GOOD, "weight_g": True},
        {**GOOD, "kind": "maybe"},
        {**GOOD, "ingredients": "牛肉"},
        {**GOOD, "calories_kcal": 5000, "weight_g": 10},
        {k: v for k, v in GOOD.items() if k != "name"},
    ],
)
def test_bad_payloads_rejected(bad):
    with pytest.raises(AnalysisError):
        parse_output(wrap(bad))


@pytest.mark.parametrize("raw", ["not json", "[]", json.dumps({"result": "沒有 JSON"}), json.dumps({"is_error": True})])
def test_bad_envelope_rejected(raw):
    with pytest.raises(AnalysisError):
        parse_output(raw)


def test_not_food_ignores_numbers():
    a = parse_output(wrap({"kind": "not_food", "name": "馬克杯", "ingredients": [], "weight_g": 300, "calories_kcal": 9999}))
    assert a.weight_g is None and a.calories_kcal is None and a.ingredients == ["馬克杯"]


def test_unclear():
    a = parse_output(wrap({"kind": "unclear", "name": "", "ingredients": [], "weight_g": None, "calories_kcal": None}))
    assert a.kind == "unclear"
