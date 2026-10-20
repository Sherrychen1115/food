"""解析並檢查 claude -p 回傳的 JSON。不能直接相信它回的東西。"""

import json
import math
import re
from dataclasses import dataclass

NAME_MAX = 20
INGREDIENT_MAX = 20
INGREDIENTS_COUNT_MAX = 15
WEIGHT_RANGE = (1, 5000)
KCAL_RANGE = (0, 5000)
KCAL_PER_GRAM_MAX = 9.5

KINDS = ("food", "not_food", "unclear")

JSON_SCHEMA = json.dumps(
    {
        "type": "object",
        "properties": {
            "kind": {"type": "string", "enum": list(KINDS)},
            "name": {"type": "string"},
            "ingredients": {"type": "array", "items": {"type": "string"}},
            "weight_g": {"type": ["number", "null"]},
            "calories_kcal": {"type": ["number", "null"]},
        },
        "required": ["kind", "name", "ingredients", "weight_g", "calories_kcal"],
    }
)


class AnalysisError(Exception):
    """這次分析不能用(格式錯、數字不合理、逾時等)。呼叫端會重試或回覆失敗。"""


@dataclass(frozen=True)
class Analysis:
    kind: str
    name: str
    ingredients: list[str]
    weight_g: float | None
    calories_kcal: float | None


def parse_output(stdout: str) -> Analysis:
    """claude -p --output-format json 的完整輸出 → Analysis。"""
    try:
        envelope = json.loads(stdout)
    except ValueError:
        raise AnalysisError("外層輸出不是 JSON") from None
    if not isinstance(envelope, dict):
        raise AnalysisError("外層輸出不是物件")
    if envelope.get("is_error"):
        raise AnalysisError("claude 回報錯誤")

    payload = envelope.get("structured_output")
    if not isinstance(payload, dict):
        text = envelope.get("result")
        if not isinstance(text, str):
            raise AnalysisError("找不到回傳內容")
        payload = _extract_json(text)
    return validate(payload)


def _extract_json(text: str) -> dict:
    text = re.sub(r"```(?:json)?", "", text).strip()
    candidates = [text]
    start, end = text.find("{"), text.rfind("}")
    if 0 <= start < end:
        candidates.append(text[start : end + 1])
    for candidate in candidates:
        try:
            value = json.loads(candidate)
        except ValueError:
            continue
        if isinstance(value, dict):
            return value
    raise AnalysisError("回傳內容裡沒有合法的 JSON")


def _number(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise AnalysisError(f"{label} 不是數字")
    if not math.isfinite(value):
        raise AnalysisError(f"{label} 不是有限的數字")
    return float(value)


def validate(payload: dict) -> Analysis:
    kind = payload.get("kind")
    if kind not in KINDS:
        raise AnalysisError("kind 不是允許的值")

    name = payload.get("name")
    ingredients = payload.get("ingredients")
    if not isinstance(name, str):
        raise AnalysisError("name 不是文字")
    if not isinstance(ingredients, list) or not all(isinstance(i, str) for i in ingredients):
        raise AnalysisError("ingredients 不是文字清單")

    name = " ".join(name.split())[:NAME_MAX]
    items = [" ".join(i.split())[:INGREDIENT_MAX] for i in ingredients]
    items = [i for i in items if i][:INGREDIENTS_COUNT_MAX]

    if kind == "unclear":
        return Analysis(kind, name, items, None, None)

    if not name:
        raise AnalysisError("name 是空的")
    if kind == "not_food":
        # 非食物:不管它填了什麼數字,一律忽略
        return Analysis(kind, name, items or [name], None, None)

    weight = _number(payload.get("weight_g"), "weight_g")
    kcal = _number(payload.get("calories_kcal"), "calories_kcal")
    if not WEIGHT_RANGE[0] <= weight <= WEIGHT_RANGE[1]:
        raise AnalysisError("重量不在合理範圍")
    if not KCAL_RANGE[0] <= kcal <= KCAL_RANGE[1]:
        raise AnalysisError("熱量不在合理範圍")
    if kcal / weight > KCAL_PER_GRAM_MAX:
        raise AnalysisError("熱量與重量不合理")
    return Analysis(kind, name, items, weight, kcal)
