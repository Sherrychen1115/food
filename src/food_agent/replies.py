"""回覆內容。"""

from dataclasses import dataclass

import discord

from .analyzer.result import Analysis

FAILED = "分析失敗，請再傳一次"
UNCLEAR = "看不清楚，請重傳"
TOO_BIG = "照片太大，請縮小後重傳"
TOO_MANY_PHOTOS = "一次最多處理 3 張"
QUEUE_FULL = "目前排隊已滿，請稍後再傳"
USER_LIMIT = "你還有 3 張在處理，請等一下"


@dataclass
class Reply:
    content: str | None = None
    embed: discord.Embed | None = None


def _num(x: float) -> str:
    return f"{x:.0f}" if float(x).is_integer() else f"{x:.1f}"


def text(message: str) -> Reply:
    return Reply(content=message)


def result(a: Analysis, daily_total: float) -> Reply:
    ingredients = "、".join(a.ingredients) or "—"
    if a.kind == "food":
        embed = discord.Embed(title=a.name, color=discord.Color.green())
        embed.add_field(name="是否食物", value="是食物", inline=True)
        embed.add_field(name="成份", value=ingredients, inline=False)
        embed.add_field(name="估計重量", value=f"{_num(a.weight_g)} 公克", inline=True)
        embed.add_field(name="估計熱量", value=f"{_num(a.calories_kcal)} 大卡", inline=True)
    else:
        embed = discord.Embed(title="這不是食物", description=f"看起來是：{ingredients}", color=discord.Color.light_grey())
    embed.add_field(name="當日已攝取熱量", value=f"{_num(daily_total)} 大卡", inline=False)
    return Reply(embed=embed)
