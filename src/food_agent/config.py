"""讀 .env、固定的數字、開機檢查。DISCORD_TOKEN 不可以被印出來或寫進任何訊息。"""

import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from dotenv import dotenv_values

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MAX_PHOTOS_PER_MESSAGE = 3
QUEUE_LIMIT = 20
PER_USER_LIMIT = 3
MAX_PHOTO_BYTES = 10 * 1024 * 1024
CLAUDE_TIMEOUT_SECONDS = 120
CLAUDE_RETRIES = 1
EXCEL_RETRY_SECONDS = 60


class ConfigError(Exception):
    """設定有問題。訊息是給人看的白話,不含任何機密。"""


@dataclass(frozen=True)
class Config:
    token: str
    channel_id: int
    model: str
    data_dir: Path
    claude_path: str

    @property
    def records_dir(self) -> Path:
        return self.data_dir / "records"

    @property
    def photos_dir(self) -> Path:
        return self.data_dir / "photos"

    @property
    def pending_dir(self) -> Path:
        return self.data_dir / "pending"


def load_config() -> Config:
    values = dotenv_values(PROJECT_ROOT / ".env")

    def get(key: str) -> str:
        return (values.get(key) or os.environ.get(key) or "").strip()

    missing = [k for k in ("DISCORD_TOKEN", "CHANNEL_ID", "CLAUDE_MODEL", "DATA_DIR") if not get(k)]
    if missing:
        raise ConfigError(f".env 缺少設定:{'、'.join(missing)}(可參考 .env.example)")

    if not get("CHANNEL_ID").isdigit():
        raise ConfigError("CHANNEL_ID 必須是純數字的頻道編號")

    data_dir = Path(get("DATA_DIR")).expanduser()
    if not data_dir.is_absolute():
        data_dir = PROJECT_ROOT / data_dir
    try:
        for sub in ("records", "photos", "pending"):
            (data_dir / sub).mkdir(parents=True, exist_ok=True)
        probe = data_dir / ".write_test"
        probe.write_text("ok")
        probe.unlink()
    except OSError as e:
        raise ConfigError(f"DATA_DIR 無法寫入:{data_dir}({e.strerror})") from None

    claude_path = shutil.which("claude")
    if not claude_path:
        raise ConfigError("找不到 claude 指令,請先安裝 Claude Code 並登入")

    return Config(
        token=get("DISCORD_TOKEN"),
        channel_id=int(get("CHANNEL_ID")),
        model=get("CLAUDE_MODEL"),
        data_dir=data_dir.resolve(),
        claude_path=claude_path,
    )
