# 食物照片記錄 Agent

在自己電腦上執行的 Discord agent:指定頻道裡有人傳食物照片,就用 `claude -p` 判斷、估熱量、記到 Excel、存照片,再回覆上傳者。

- 開始任何工作前,先讀 `docs/architecture.md`。
- 四段防護(`docs/architecture.md` 第 12.2 節)要各自用清楚的註解標起來,有開始和結束標記,格式照課程 P6:`# ==== 防護 1：<名稱>　開始 ====` / `# ==== 防護 1 結束 ====`。一開始全部開啟。
- 不可以把 `.env` commit 進 git(只有 `.env.example` 可以 commit)。`DISCORD_TOKEN` 不可以出現在程式碼、log、錯誤訊息或 repo 的任何地方。
- `DATA_DIR` 裡的照片和 Excel 也不要 commit。
