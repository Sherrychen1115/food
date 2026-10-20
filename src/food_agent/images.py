"""確認收到的真的是圖片(看內容不看副檔名),並縮小後再交給 claude。"""

import io
from dataclasses import dataclass

from PIL import Image, ImageOps

MAX_PIXELS = 50_000_000
MAX_EDGE = 1568
EXTENSIONS = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}


class ImageError(Exception):
    pass


@dataclass(frozen=True)
class Prepared:
    ext: str  # 原始照片的副檔名(由內容判斷)
    small_jpeg: bytes  # 給 claude 看的縮小版


def prepare(data: bytes) -> Prepared:
    try:
        with Image.open(io.BytesIO(data)) as im:
            ext = EXTENSIONS.get(im.format or "")
            if ext is None:
                raise ImageError("不是支援的圖片格式")
            if im.width * im.height > MAX_PIXELS:
                raise ImageError("圖片像素太多")
            im.load()
            im = ImageOps.exif_transpose(im).convert("RGB")
        im.thumbnail((MAX_EDGE, MAX_EDGE))
        out = io.BytesIO()
        im.save(out, "JPEG", quality=85)
    except ImageError:
        raise
    except Exception as e:  # 壞檔、解壓縮炸彈等
        raise ImageError(type(e).__name__) from None
    return Prepared(ext, out.getvalue())
