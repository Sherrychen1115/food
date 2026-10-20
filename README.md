# 食物照片記錄 Agent

在自己電腦上執行的 Discord agent:指定頻道有人傳食物照片,就用 `claude -p` 判斷、估熱量、記到 Excel、存照片,再回覆上傳者。設計見 `docs/architecture.md`。

## 啟動

1. 到 Discord Developer Portal 打開機器人的 **Message Content Intent**,並邀請機器人進 Server(需要:看頻道、發訊息、加反應、讀歷史訊息、嵌入連結)。
2. `cp .env.example .env`,填入 `DISCORD_TOKEN`、`CHANNEL_ID`、`CLAUDE_MODEL`、`DATA_DIR`。
3. 啟動:

```
uv sync
uv run python -m food_agent
```

Ctrl+C 關機。測試:`uv run pytest`。

## 資料位置(DATA_DIR)

- `records/food_log.xlsx`:一直往下加的紀錄
- `photos/`:照片,檔名 `YYYY-MM-DD hh-mm-ss 名稱.jpg`
- `pending/`:Excel 被開著時的暫存,每 60 秒自動補寫

## 四段防護(行號為大約位置,一開始全部開啟)

| 防護 | 檔案 | 行號 |
|---|---|---|
| 防護 1:claude -p 的檔案範圍隔離 | `src/food_agent/analyzer/claude_runner.py` | 31–36 |
| 防護 2:上傳者打的字只能當資料 | `src/food_agent/analyzer/prompt.py` | 18–21 |
| 防護 3:檔名清洗 | `src/food_agent/storage/filenames.py` | 31–36 |
| 防護 4:Excel 公式防護 | `src/food_agent/storage/excel_log.py` | 34–39 |

要關掉某一段,把 `開始` 到 `結束` 之間整段註解掉即可;程式裡有對應的「無防護」預設行為。
