# Discord Bot 設定步驟

> 這份文件教你:在 Discord Developer Portal 建立 application 和 bot、打開 Message Content Intent、拿到 bot token、設定權限、把 bot 邀進你自己的 Server。
> 你的電腦是 **macOS**,快捷鍵用 macOS 的寫法(`⌘` 就是 Command 鍵)。
> Discord 偶爾改版,畫面上的字可能略有不同,找意思最接近的選項(括號裡附了英文名稱)。
> 這份文件**不需要寫任何程式**。請先完成 `docs/discord-server-setup.md`。

**名詞先說明**:

- **Developer Portal(開發者後台)**:Discord 給開發者用的網站,在這裡建立和管理機器人。
- **Application(應用程式)**:你在 Developer Portal 建立的一個「專案」,bot 是它裡面的一部分。
- **Bot(機器人)**:一個像使用者一樣能進 Server、收訊息、發訊息的帳號。我們的 agent 程式會用它來收照片和回覆。
- **Bot token(機器人密碼)**:一串很長的文字,**誰拿到它,誰就能完全控制你的 bot**。是這個專案最重要的祕密。

---

## ⚠️ 先看這段:bot token 的規定

**bot token 絕對不能:**

1. **貼給任何人**(同學、朋友、老師、客服都不行)
2. **貼進這個對話**(貼給我 Claude 也不行)
3. **commit 進 git、push 到 GitHub**

**為什麼**:拿到 token 的人可以用你的 bot 在你的 Server 發訊息、讀頻道、做任何你的 bot 能做的事。放在 GitHub 上還會被全世界的程式自動掃描。

**token 只能放在哪裡**:

- 日後寫程式時,只放在專案資料夾的 **`.env`** 檔案裡(`DISCORD_TOKEN=...` 這一行)。`.env` 會被 `.gitignore` 排除,不會被 commit。
- 在 `.env` 建立之前,如果需要暫存,放在**你自己的密碼管理器**(例如 macOS 的「密碼」App)。**不要**放在專案資料夾、不要寄給自己、不要貼在任何聊天軟體。

**如果不小心洩漏了**(貼到對話、貼到 GitHub、截圖給別人看到):**立刻**回到 Developer Portal 按「重設 Token」(第 4 節的步驟),舊的就會馬上失效。重設不會有任何損失,只是要把新的 token 更新到 `.env`。**別猶豫、別想「應該沒人看到」。**

---

## 1. 建立 Application

1. 用瀏覽器打開 https://discord.com/developers/applications。
2. 如果要求登入,用你平常的 Discord 帳號登入。
3. 看畫面**右上角**,點藍色的 **「New Application」**(新增應用程式)。
4. 在「Name」(名稱)輸入名字,例如 `food-agent`。這會是 bot 顯示在 Server 裡的名字(之後可以改)。
5. 勾選下面的同意條款(Discord Developer Terms of Service 和 Developer Policy)。
6. 點 **「Create」**(建立)。如果跳出「我不是機器人」的驗證,照著完成。
7. 建好後會進到這個 Application 的頁面,左邊有一排選單:General Information、Installation、OAuth2、**Bot** 等。

---

## 2. 設定 Bot 並打開 Message Content Intent

1. 在左邊選單點 **「Bot」**。(新的 Application 會自動有一個 bot,不用另外建立。)
2. 往下捲,找到 **「Privileged Gateway Intents」**(特權閘道意圖)這一區。
3. 找到 **「Message Content Intent」**(訊息內容意圖),把右邊的開關**打開**(變成藍色)。
4. 另外兩個(Presence Intent、Server Members Intent)**保持關閉**,我們用不到。
5. 頁面下方(或上方)會出現一條 **「Save Changes」**(儲存變更)的提示,**點它**。沒有按儲存,剛剛的開關不會生效。

**為什麼一定要打開 Message Content Intent**:

Discord 為了保護隱私,預設**不讓 bot 看到訊息的內容**。對 bot 來說,訊息裡的「附件」(也就是別人傳的照片)也算內容的一部分。沒打開這個開關,bot 收到的訊息裡,**照片的欄位是空的**,agent 就完全看不到有人傳了照片,也就什麼都不會處理,而且不會有任何錯誤訊息,很難發現原因。

> 一般的 bot 在 Server 少於 100 個時,可以自己打開這個開關,不需要 Discord 審核。你的情況符合。

---

## 3. 關掉「Public Bot」(建議)

還在 **Bot** 頁面。

1. 往上捲,找到 **「Public Bot」**(公開機器人)的開關。
2. 把它**關閉**。
3. 點 **「Save Changes」**。

**為什麼**:關閉後,只有你自己能把這個 bot 邀進 Server。別人不能拿到你的 bot 的邀請連結,把它加進他們的 Server。

---

## 4. 拿到 Bot Token

**做這步前請再確認:周圍沒有人在看你的螢幕、你沒有在螢幕分享或錄影。**

1. 還在 **Bot** 頁面,找到 **「Token」** 這一區。
2. 點 **「Reset Token」**(重設 Token)。
3. 跳出確認視窗,點 **「Yes, do it!」**(是的,執行)。Discord 可能會要求你輸入密碼或兩步驟驗證碼。
4. 畫面上會出現一串很長的文字,旁邊有 **「Copy」**(複製)按鈕。點 **「Copy」**。
5. **Token 只會顯示這一次。** 重新整理頁面後就看不到了,只能再「Reset Token」產生新的。
6. 把它貼到你的**密碼管理器**(例如 macOS 的「密碼」App)。**不要**貼到備忘錄、聊天軟體、這個對話、專案資料夾。
7. 日後建立 `.env` 時,才把它填進去:`DISCORD_TOKEN=你的token`。

> 看起來像這樣(**這是假的範例,不是真的 token**):`MTIzNDU2.XXXXXX.xxxxxxxxxxxxxxxxxxxxxxxxxxx`。三段用點隔開。

**不要搞錯**:Developer Portal 還有別的長字串,**都不是 bot token**,也不需要:

| 名稱 | 在哪 | 要不要 |
|---|---|---|
| Application ID(應用程式 ID) | General Information | 不需要(下面第 6 節網址會自動帶入) |
| Public Key(公開金鑰) | General Information | 不需要 |
| Client Secret(用戶端密鑰) | OAuth2 | **不需要,也不能公開** |
| **Bot Token** | **Bot → Reset Token** | **需要,絕對不能公開** |

---

## 5. 決定權限:要給 bot 哪些權限

**原則**:只給 agent 真的需要的,**不要給「Administrator」(管理員)**。

這個 agent 需要的權限:

| 權限(英文) | 中文名稱 | 為什麼需要 |
|---|---|---|
| View Channels | 查看頻道 | 才看得到那個頻道,收得到訊息 |
| Send Messages | 傳送訊息 | 回覆「處理中」和結果 |
| Read Message History | 讀取訊息歷史 | 回覆某一則指定的訊息(我們用「回覆」功能指向那張照片)需要 |
| Embed Links | 嵌入連結 | 結果用排版過的卡片(Embed)顯示 |

**不需要**的:Administrator、Manage Messages、Manage Channels、Attach Files、Mention Everyone 等。不要勾。

---

## 6. 產生邀請連結並把 Bot 邀進你的 Server

1. 在 Developer Portal 左邊選單,點 **「OAuth2」**。
2. 往下捲,找到 **「OAuth2 URL Generator」**(OAuth2 網址產生器)。
3. 在 **「Scopes」**(範圍)這一區,勾選 **`bot`**。其他的**都不要勾**。
4. 勾了 `bot` 之後,下面會多出一區 **「Bot Permissions」**(機器人權限)。依第 5 節,勾選這四個:
   - **View Channels**
   - **Send Messages**
   - **Read Message History**
   - **Embed Links**
5. 頁面最下面有 **「Generated URL」**(產生的網址),旁邊有 **「Copy」**。點 **「Copy」**。
6. 打開一個新的瀏覽器分頁,貼上這個網址,按 Enter。
7. 頁面會問你「要把 bot 加到哪個 Server?」。在下拉選單選**你自己建立的那個 Server**(例如「食物記錄測試」)。(看不到你的 Server,代表你登入的帳號不對,或你不是該 Server 的管理者。)
8. 點 **「繼續」**(Continue)。
9. 下一頁會列出你授權的權限,確認就是剛剛那四個。點 **「授權」**(Authorize)。
10. 完成驗證(「我不是機器人」)。看到「已授權」(Authorized)就成功了。

> 這個邀請網址**不是祕密**(裡面沒有 token),但因為已經關掉 Public Bot,別人用了也加不進去。

---

## 7. 確認 Bot 進到 Server 了

1. 回到 Discord App 或網頁,打開你的 Server。
2. 看右邊的**成員清單**(右上角有一個像兩個人的圖示,可以切換顯示)。**bot 會出現在清單裡,旁邊有一個藍色的「APP」小標籤,而且是「離線」(灰色)。**
   - 離線是正常的!bot 只有在你**之後執行 agent 程式**時才會上線。現在還沒寫程式,所以離線。
3. 確認 bot 看得到你的 `food-log` 頻道:
   - 在頻道清單,**對 `food-log` 按右鍵 → 「編輯頻道」**(Edit Channel) → 左邊 **「權限」**(Permissions)。
   - 因為這個頻道不是私人頻道,bot 預設就能看到。只要你沒有手動把「@everyone」的「查看頻道」關掉,就不需要再設定。

---

## 8. 確認完成

- [ ] 我在 Developer Portal 建立了一個 Application。
- [ ] **Message Content Intent 已打開,並且按了 Save Changes。**
- [ ] Public Bot 已關閉。
- [ ] 我拿到 bot token,而且**只存在密碼管理器**裡,沒有貼給任何人、沒有貼到這個對話、沒有放進專案資料夾。
- [ ] 我用 OAuth2 URL Generator(只勾 `bot` 和四個權限)產生網址,把 bot 邀進我自己的 Server。
- [ ] 我在 Server 的成員清單看到 bot(離線,有 APP 標籤)。
- [ ] 我手上有兩個值:`CHANNEL_ID`(上一份文件)和 `DISCORD_TOKEN`(這份文件),準備日後填進 `.env`。

---

## 常見問題

| 狀況 | 可能原因與處理 |
|---|---|
| 以後 agent 開著,但完全不處理照片 | 最常見的原因:**Message Content Intent 沒打開**,或打開了但沒按 Save Changes。回第 2 節檢查 |
| 以後 agent 啟動時顯示「登入失敗」或「Improper token」 | token 複製錯了(多了空格或少了一段),或已經被重設過。到第 4 節重新 Reset Token 再複製一次 |
| 以後 agent 能收到照片,但回覆不出來 | bot 少了 Send Messages 或 Embed Links 權限。可以重新做第 6 節產生新網址再邀請一次(不會重複加入),或在 Server 設定 → 身分組 裡調整 bot 的權限 |
| 邀請時看不到我的 Server | 登入的帳號不是 Server 擁有者或管理者。確認登入的是建立 Server 的那個帳號 |
| 不小心把 token 貼出去了 | **立刻回第 4 節 Reset Token。** 舊的馬上失效 |
