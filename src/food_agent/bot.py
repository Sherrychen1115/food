"""Discord:收訊息、過濾、排隊、回覆。只聽 CHANNEL_ID 那一個頻道。"""

import asyncio
import logging
from collections import Counter
from datetime import datetime

import discord

from . import replies
from .config import EXCEL_RETRY_SECONDS, MAX_PHOTOS_PER_MESSAGE, PER_USER_LIMIT, QUEUE_LIMIT, Config
from .queue_worker import Job, Processor
from .storage.daily_total import DailyTotal
from .storage.excel_log import ExcelLog

log = logging.getLogger("food_agent")

HOURGLASS = "⏳"
IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
REQUIRED_PERMISSIONS = ("view_channel", "send_messages", "read_message_history", "add_reactions", "embed_links")


def _is_image(att: discord.Attachment) -> bool:
    return (att.content_type or "").split(";")[0].strip().lower() in IMAGE_TYPES


class FoodBot(discord.Client):
    def __init__(self, cfg: Config):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.cfg = cfg
        self.excel = ExcelLog(cfg.records_dir, cfg.pending_dir)
        self.daily = DailyTotal(datetime.now().date())
        self.processor = Processor(cfg, self.excel, self.daily)
        self.queue: asyncio.Queue[Job] = asyncio.Queue(maxsize=QUEUE_LIMIT)
        self.user_pending: Counter[int] = Counter()
        self.message_pending: Counter[int] = Counter()
        self._tasks: list[asyncio.Task] = []

    async def setup_hook(self) -> None:
        await asyncio.to_thread(self.excel.flush_pending)
        today = datetime.now()
        self.daily = self.processor.daily = DailyTotal(
            today.date(), await asyncio.to_thread(self.excel.sum_for_date, f"{today:%Y-%m-%d}")
        )
        self._tasks = [asyncio.create_task(self._worker()), asyncio.create_task(self._flush_loop())]

    async def on_ready(self) -> None:
        channel = self.get_channel(self.cfg.channel_id)
        if channel is None:
            print("找不到 CHANNEL_ID 指定的頻道,請確認機器人已加入該 Server。")
            await self.close()
            return
        perms = channel.permissions_for(channel.guild.me)
        lacking = [p for p in REQUIRED_PERMISSIONS if not getattr(perms, p)]
        if lacking:
            print(f"機器人在該頻道缺少權限:{', '.join(lacking)}")
            await self.close()
            return
        print(f"已上線,監聽頻道 #{channel.name}。今日累計 {self.daily.kcal:.0f} 大卡。")

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot or message.channel.id != self.cfg.channel_id:
            return
        images = [a for a in message.attachments if _is_image(a)]
        if not images:
            return
        if len(images) > MAX_PHOTOS_PER_MESSAGE:
            await self._reply(message, replies.text(replies.TOO_MANY_PHOTOS))
            images = images[:MAX_PHOTOS_PER_MESSAGE]

        for i, att in enumerate(images, start=1):
            if self.user_pending[message.author.id] >= PER_USER_LIMIT:
                await self._reply(message, replies.text(replies.USER_LIMIT))
                break
            job = Job(message, att, i, len(images))
            try:
                self.queue.put_nowait(job)
            except asyncio.QueueFull:
                await self._reply(message, replies.text(replies.QUEUE_FULL))
                break
            self.user_pending[message.author.id] += 1
            self.message_pending[message.id] += 1
            try:
                await message.add_reaction(HOURGLASS)
            except discord.HTTPException:
                pass

    async def _worker(self) -> None:
        while True:
            job = await self.queue.get()
            try:
                reply = await self.processor.process(job)
                if job.total > 1 and reply.content:
                    reply.content = f"（第 {job.index}/{job.total} 張）{reply.content}"
                elif job.total > 1:
                    reply.content = f"（第 {job.index}/{job.total} 張）"
                await self._reply(job.message, reply)
            except asyncio.CancelledError:
                raise
            except Exception:
                log.exception("處理照片時發生未預期的錯誤")
                await self._reply(job.message, replies.text(replies.FAILED))
            finally:
                await self._release(job)
                self.queue.task_done()

    async def _release(self, job: Job) -> None:
        self.user_pending[job.message.author.id] -= 1
        self.message_pending[job.message.id] -= 1
        if self.message_pending[job.message.id] <= 0:
            del self.message_pending[job.message.id]
            try:
                await job.message.remove_reaction(HOURGLASS, self.user)
            except discord.HTTPException:
                pass

    async def _reply(self, message: discord.Message, reply: replies.Reply) -> None:
        mentions = discord.AllowedMentions(everyone=False, roles=False, users=[message.author], replied_user=True)
        try:
            await message.reply(content=reply.content, embed=reply.embed, allowed_mentions=mentions)
        except discord.HTTPException as e:
            log.warning("回覆失敗:%s", type(e).__name__)

    async def _flush_loop(self) -> None:
        while True:
            await asyncio.sleep(EXCEL_RETRY_SECONDS)
            await asyncio.to_thread(self.excel.flush_pending)

    async def close(self) -> None:
        for t in self._tasks:
            t.cancel()
        # 關機時還在排隊的:移除 ⏳,讓大家知道沒處理
        while not self.queue.empty():
            job = self.queue.get_nowait()
            await self._release(job)
        await super().close()
