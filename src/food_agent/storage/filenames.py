"""照片檔名:清洗食物名稱、組出不會跑出照片資料夾的路徑、同一秒撞名加 -2、-3。"""

import re
import unicodedata
from datetime import datetime
from pathlib import Path

NAME_MAX = 20
DEFAULT_NAME = "食物"
_WINDOWS_RESERVED = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}


def _clean(name: str) -> str:
    name = unicodedata.normalize("NFKC", name)
    name = "".join(c for c in name if c.isprintable())
    name = re.sub(r'[/\\:*?"<>|]', "_", name)
    while ".." in name:
        name = name.replace("..", "_")
    name = re.sub(r"\s+", "_", name).strip("._ ")[:NAME_MAX].strip("._ ")
    if not name:
        return DEFAULT_NAME
    if name.split(".")[0].upper() in _WINDOWS_RESERVED:
        name = "_" + name
    return name


def save_unique(photos_dir: Path, when: datetime, name: str, ext: str, data: bytes) -> Path:
    """把照片存成「YYYY-MM-DD hh-mm-ss 名稱.ext」,回傳實際存下的路徑。"""
    stem = f"{when:%Y-%m-%d %H-%M-%S}"

    # ==== 防護 3：檔名清洗　開始 ====
    # 清掉 / \ .. : 等會讓路徑亂跑的字,並確認組出的路徑仍在照片資料夾裡面。
    name = _clean(name)
    if (photos_dir / f"{stem} {name}{ext}").resolve().parent != photos_dir.resolve():
        raise ValueError("檔名超出照片資料夾")
    # ==== 防護 3 結束 ====

    for n in range(1, 1000):
        suffix = "" if n == 1 else f"-{n}"
        path = photos_dir / f"{stem} {name}{suffix}{ext}"
        try:
            with open(path, "xb") as f:  # 只在檔案不存在時才建立,不會蓋掉別人的照片
                f.write(data)
        except FileExistsError:
            continue
        return path
    raise OSError("同一秒撞名太多次")
