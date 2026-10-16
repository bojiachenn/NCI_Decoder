# NCI Parsing Tool — 網頁版

`NCI_Decoder`（Python CLI）的 JavaScript 版本。純前端執行，log 檔只在瀏覽器內處理，不會上傳。

## 使用

- **直接開啟**：`dist/index.html` 是單一檔案（JS/CSS/文件全部內嵌），可以複製給同事，或放到任何 web server。
- **開發**：`npm install` → `npm run dev`（http://localhost:5173）

頁面：
| 頁面 | 功能 |
|---|---|
| Decode | 貼上 hex（一行一個封包，依序解碼，可解析 HDLL CMD → DL_OK 這類前後相依的封包）。可切換結構 / 文字檢視；滑過欄位會標示對應的 bytes；點指令名或表名開啟文件 |
| Log | 拖放 / 選擇 / 貼上 logcat。Decode keyword 預設 `auto`，會自動偵測 NXP（`NxpNciX/NciR`）或 ST（`StNfcHal: (#N) Tx/Rx`）格式，NXP log 也會自動改用 NXP vendor。可依類型、錯誤、關鍵字篩選，並下載與 CLI 相同格式的 `<檔名>_d.txt` |
| Reference | 瀏覽 repo 根目錄 `Docs/` 的全部文件（build 時內嵌）；可用指令名、header hex（如 `61 05`）、表名搜尋 |

右上角的 Vendor 對應 CLI `config.json` 的 `vendor`：`NFC Forum NCI 2.0`（預設）或 `NXP`。

## 開發

```
npm test              # golden 比對 + 單元測試
npm run build         # 產出 dist/index.html
npm run tables        # Python __table__.py 有變更時：重新匯出 src/data/tables.*.json
npm run golden        # 重新以 Python decoder 產生 tests/golden/*.json
python scripts/gen_log_golden.py   # log 模式的 golden
```

- 架構與移植慣例：[PORTING.md](PORTING.md)
- 行為以 Python 為準：`tests/golden/*.json` 是 Python 的實際輸出。JS 必須逐行一致，例外有兩類：
  - `tests/known_diffs/*.json`：刻意修正 Python bug 的案例，每筆都附原因。
  - Python 本身會 crash 的案例：只要求 JS 不 crash。
- 在 Python 端新增 command 時：先在 `src/core/ctrl_spec.js` 加入名稱（由 `__ctrl__.py` 產生），再到 `src/handlers/<vendor>/` 實作 handler。`tests/registry.test.js` 會檢查是否有遺漏的 handler。
