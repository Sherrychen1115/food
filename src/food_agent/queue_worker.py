"""一張一張處理照片:下載、分析、存照片、寫 Excel、算累計,回傳要回覆的內容。"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime

import discord

from . import replies
from .analyzer.claude_runner import analyze_photo
from .analyzer.result import Analysis, AnalysisError
from .config import CLAUDE_RETRIES, MAX_PHOTO_BYTES, Config
from .images import ImageError, prepare
from .storage.daily_total import DailyTotal
from .storage.excel_log import ExcelLog, LogRow
from .storage.filenames import save_unique

log = logging.getLogger("food_agent")


@dataclass
class Job:
    message: discord.Message
    attachment: discord.Attachment
    index: int
    total: int


class Processor:
    def __init__(self, cfg: Config, excel: ExcelLog, daily: DailyTotal):
        self.cfg, self.excel, self.daily = cfg, excel, daily

    async def process(self, job: Job) -> replies.Reply:
        att = job.attachment
        if att.size > MAX_PHOTO_BYTES:
            return replies.text(replies.TOO_BIG)
        try:
            data = await att.read()
            prepared = prepare(data)
        except (ImageError, discord.HTTPException) as e:
            log.warning("照片無法使用:%s", type(e).__name__)
            return replies.text(replies.FAILED)

        analysis = await self._analyze(prepared.small_jpeg, job.message.content)
        if analysis is None:
            return replies.text(replies.FAILED)
        if analysis.kind == "unclear":
            return replies.text(replies.UNCLEAR)

        now = datetime.now()
        is_food = analysis.kind == "food"
        title = analysis.name if is_food else "不是食物"
        total = self.daily.add(now, analysis.calories_kcal or 0.0)
        try:
            path = await asyncio.to_thread(
                save_unique, self.cfg.photos_dir, now, title, prepared.ext, data
            )
            row = LogRow(
                when=f"{now:%Y-%m-%d %H:%M:%S}",
                uploader=job.message.author.display_name,
                name=title,
                ingredients="、".join(analysis.ingredients),
                weight_g=analysis.weight_g,
                calories_kcal=analysis.calories_kcal,
                daily_total=total,
                photo=path.relative_to(self.cfg.data_dir).as_posix(),
            )
            await asyncio.to_thread(self.excel.add, row)
        except Exception as e:
            log.error("存檔或記錄失敗:%s", type(e).__name__)
            if analysis.calories_kcal:
                self.daily.add(now, -analysis.calories_kcal)
            return replies.text(replies.FAILED)
        return replies.result(analysis, total)

    async def _analyze(self, jpeg: bytes, user_text: str) -> Analysis | None:
        for attempt in range(1 + CLAUDE_RETRIES):
            try:
                return await analyze_photo(self.cfg, jpeg, user_text)
            except AnalysisError as e:
                log.warning("分析失敗(第 %d 次):%s", attempt + 1, e)
        return None
