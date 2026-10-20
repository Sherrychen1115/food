"""啟動入口:uv run python -m food_agent"""

import logging
import sys

import discord

from .bot import FoodBot
from .config import ConfigError, load_config


def main() -> None:
    try:
        cfg = load_config()
    except ConfigError as e:
        print(f"無法啟動:{e}")
        sys.exit(1)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    try:
        FoodBot(cfg).run(cfg.token, log_handler=None)
    except discord.LoginFailure:
        print("無法啟動:Discord 拒絕登入,請確認 .env 的 DISCORD_TOKEN")
        sys.exit(1)


if __name__ == "__main__":
    main()
