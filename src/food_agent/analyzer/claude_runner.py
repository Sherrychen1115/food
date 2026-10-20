"""呼叫 claude -p 看一張照片。"""

import asyncio
import os
import tempfile
from pathlib import Path

from ..config import CLAUDE_TIMEOUT_SECONDS, Config
from .prompt import build_prompt
from .result import JSON_SCHEMA, Analysis, AnalysisError, parse_output

PHOTO_NAME = "photo.jpg"


async def analyze_photo(cfg: Config, jpeg: bytes, user_text: str = "") -> Analysis:
    with tempfile.TemporaryDirectory(prefix="food-agent-") as tmp:
        (Path(tmp) / PHOTO_NAME).write_bytes(jpeg)

        cmd = [
            cfg.claude_path,
            "-p",
            build_prompt(PHOTO_NAME, user_text),
            "--model", cfg.model,
            "--output-format", "json",
            "--json-schema", JSON_SCHEMA,
            "--no-session-persistence",
        ]
        cwd = str(cfg.data_dir)  # 沒有防護 1 時:在 DATA_DIR 裡執行,看得到所有人的照片和 Excel
        extra = ["--add-dir", tmp]

        # ==== 防護 1：claude -p 的檔案範圍隔離　開始 ====
        # 在全新的暫存資料夾(不在 DATA_DIR 裡)執行,裡面只有這一張照片;
        # 只開放讀檔工具,沒有指令、寫檔、上網;不額外開放其他資料夾。
        cwd = tmp
        extra = ["--tools", "Read", "--permission-mode", "dontAsk"]
        # ==== 防護 1 結束 ====
        cmd += extra

        env = {k: v for k, v in os.environ.items() if k != "DISCORD_TOKEN"}
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=cwd,
            env=env,
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), CLAUDE_TIMEOUT_SECONDS)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            raise AnalysisError("claude -p 逾時") from None
        except BaseException:
            # 例如關機時被取消:不要留下孤兒行程
            if proc.returncode is None:
                proc.kill()
                await proc.wait()
            raise

    if proc.returncode != 0:
        detail = stderr.decode("utf-8", "replace").strip()[:200]
        raise AnalysisError(f"claude -p 結束碼 {proc.returncode}:{detail}")
    return parse_output(stdout.decode("utf-8", "replace"))
