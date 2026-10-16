# NXP HDLL（Host Data Link Layer）

NXP SN2x0 在下載模式（bootloader / firmware download）下使用的 HDLL 協定，與 NCI 封包格式不同：沒有 MT/GID/OID，而是「2 bytes header + Op Code + Payload + 2 bytes CRC-16」。本工具只在 vendor = `'Nxp'` 時能解析 HDLL；解析入口為 [`Nxp_pkg/__ctrl__.py:117`](../../nci_decoder/Nxp_pkg/__ctrl__.py#L117) `HDLL()`，各 op code 的 handler 定義於 [`Nxp_pkg/HDLL.py`](../../nci_decoder/Nxp_pkg/HDLL.py)，op code 對照表為 [`__ctrl__.py:90`](../../nci_decoder/Nxp_pkg/__ctrl__.py#L90) 的 `tbl_nci_ctrl["HDLL"]`。

## 總覽

HDLL 沒有 GID/OID，下表的「Op Code」即 frame 的第 3 個 byte。CMD 與 RSP 共用同一張 `tbl_nci_ctrl["HDLL"]`，只靠 op code 值區分。

### CMD Op Codes

| Op Code | 類型 | Handler | 說明 |
|---|---|---|---|
| `F0` | CMD | [`DL_RESET`](#dl_reset--f0) | 重置 |
| `F1` | CMD | [`DL_GET_VERSION`](#dl_get_version--f1) | 讀取版本 |
| `F2` | CMD | [`DL_GET_SESSION_STATE`](#dl_get_session_state--f2) | 讀取 session 狀態 |
| `F4` | CMD | [`DL_GET_DIE_ID`](#dl_get_die_id--f4) | 讀取 Die ID |
| `E0` | CMD | [`DL_CHECK_INTEGRITY`](#dl_check_integrity--e0) | flash 完整性檢查 |
| `C0` | CMD | [`DL_SEC_WRITE`](#dl_sec_write--c0) | 安全寫入（韌體下載） |
| `C1` | CMD | [`DL_CERT_FRAME`](#dl_cert_frame--c1) | 憑證 frame |

### RSP Op Codes（狀態碼）

| Op Code | 類型 | Handler | 說明 |
|---|---|---|---|
| `00` | RSP | [`DL_OK`](#dl_ok--00) | 成功；payload 格式依前一個 op code 決定 |
| `01` | RSP | [`EDL_INVALID_ADDR`](#錯誤--狀態-rsp01--31) | |
| `02` | RSP | [`EDL_GENERIC_ERROR`](#錯誤--狀態-rsp01--31) | |
| `0B` | RSP | [`EDL_UNKNOW_CMD`](#錯誤--狀態-rsp01--31) | |
| `0C` | RSP | [`EDL_ABORTED_CMD`](#錯誤--狀態-rsp01--31) | |
| `1E` | RSP | [`EDL_ADDR_RANGE_OFL_ERROR`](#錯誤--狀態-rsp01--31) | |
| `1F` | RSP | [`EDL_BUFFER_OFL_ERROR`](#錯誤--狀態-rsp01--31) | |
| `20` | RSP | [`EDL_MEM_BSY`](#錯誤--狀態-rsp01--31) | |
| `21` | RSP | [`EDL_SIGNATURE_ERROR`](#錯誤--狀態-rsp01--31) | |
| `24` | RSP | [`EDL_FIRMWARE_VERSION_ERROR`](#錯誤--狀態-rsp01--31) | |
| `28` | RSP | [`EDL_PROTOCOL_ERROR`](#錯誤--狀態-rsp01--31) | |
| `2D` | RSP | [`PH_STATUS_DL_FIRST_CHUNK`](#錯誤--狀態-rsp01--31) | |
| `2E` | RSP | [`PH_STATUS_DL_NEXT_CHUNK`](#錯誤--狀態-rsp01--31) | |
| `31` | RSP | [`PH_STATUS_EDL_CERT_ERROR`](#錯誤--狀態-rsp01--31) | |

## 判斷是否走 HDLL（`Decoder_Main.py`）

[`Decoder_Main.py:44`](../../nci_decoder/Decoder_Main.py#L44) 先嘗試 NCI：若 `raw[4:6]`（第 3 byte）的值 == 封包總長度 − 3，就當成 NCI 封包解析。**只有在 NCI 長度檢查失敗時**，才檢查 [`Decoder_Main.py:106`](../../nci_decoder/Decoder_Main.py#L106)：

```python
int(first_oct_b[3:] + bin(int(raw[2:4],16))[2::].zfill(8), 2) == int(len)-4   # 2 Bytes header (HDLL) + CRC16 (2 Bytes)
```

也就是「byte0 低 5 bits ‖ byte1」組成的 13-bit frame length == 總長度 − 4（2 bytes header + 2 bytes CRC）。成立則呼叫 `pkg.HDLL(raw, mode)`；兩者都不成立印 `Error: Unknown raw data!`。

## Frame 格式

```
| Byte0          | Byte1         | Byte2   | Byte3 .. Byte(N)       | CRC (2)     |
| b7 b6 b5 b4..0 | b7..0         | Op Code | Payload (FrameLen - 1) | CRC16 MSB/LSB |
|  -  -  C  Len[12:8] | Len[7:0] |         |                        |             |
```

| # | 欄位 | 長度 (Octets) | 解析方式 |
|---|---|---|---|
| 1 | Header byte0 | 1 | bit 7–6：程式未使用；bit 5：Chunk bit（`first_oct_b[2:3]`，為 1 時印 `* Chunk: 1`）；bit 4–0：Frame Length 高 5 bits |
| 2 | Header byte1 | 1 | Frame Length 低 8 bits。Frame Length（13 bits）= Op Code + Payload 的 byte 數，**不含** header 與 CRC |
| 3 | Op Code | 1 | `tbl_nci_ctrl["HDLL"].get(op_code)` 取得 handler；找不到時標題印 `UNKNOWN (XX)`，並印 `Error: unknown HDLL op code XX, raw: <整串 raw>` |
| 4 | Payload | Frame Length − 1 | 交給 handler：`handler(frame_len, msg, HDLL_CMD)`，`msg` 為 op code 之後的 payload hex 字串 |
| 5 | CRC | 2 | 印 `* CRC: XXXX (CRC-16-CCITT-FALSE)`，並以 `HDLL.crc16_ccitt_false()` 對 header + op code + payload 重新計算；不一致時多印 `    ! CRC mismatch: calculated YYYY` |

CRC-16-CCITT-FALSE：poly `0x1021`、init `0xFFFF`、不反射、xorout `0x0000`，計算範圍為 header + op code + payload，結果以 big-endian 放在 frame 尾端。本文件範例的 CRC 皆以此演算法計算（`00 04 F1 00 00 00` → `6E EF`，與 NXP 常見的 DL_GET_VERSION frame 一致）。

### `HDLL()` 處理流程（[`__ctrl__.py:117`](../../nci_decoder/Nxp_pkg/__ctrl__.py#L117)）

1. 由 byte0/byte1 算出 `frame_len`，取 op code、`msg`（payload）。
2. 印 `  << Nxp HDLL: <handler 名> >>  `；`mode == 1` 時同一行接著印整串 raw，`mode == 2` 只換行。
3. 若 `chunk == '1'`（byte0 bit 5 = 1）印 `* Chunk: 1`。
4. 若 op code 有對應 handler，呼叫 `handler(frame_len, msg, HDLL_CMD)`，回傳 `check`（handler 走過的 hex 字元數）；否則印 `Error: unknown HDLL op code XX, raw: <raw>`，`check = None`。標題中的 handler 名稱在找不到時為 `UNKNOWN (XX)`。
5. `HDLL_CMD = op_code`：把**這一個** frame 的 op code 存入模組全域變數（初始值 [`__ctrl__.py:7`](../../nci_decoder/Nxp_pkg/__ctrl__.py#L7) `HDLL_CMD = '00'`）。
6. 印 CRC，並以 CRC-16-CCITT-FALSE 驗證；不一致時印 `    ! CRC mismatch: calculated YYYY`。
7. 長度檢查（僅 `check` 不為 `None` 時）：`hdll_payload != len(raw)` 或 `check + 2 != frame_len * 2` 時印 `Error: Payload error!!` 及 `check` / `Packet Len` / `Frame Len`。`check + 2` 的 `+2` 是補上 op code 的 1 byte，因此 handler 必須剛好走完 `Frame Length − 1` bytes。
8. 印 `#end`。

### RSP 如何依前一個 CMD 決定格式

HDLL RSP 本身不帶「回應哪個 CMD」的資訊，因此 `HDLL()` 用全域變數 `HDLL_CMD` 記住**上一個被解析的 frame 的 op code**，作為第三個參數 `pre_op` 傳給 handler。只有 `DL_OK`（`00`）會使用 `pre_op`：

| `pre_op` | `DL_OK` payload 格式 |
|---|---|
| `F1` | DL_GET_VERSION 回應（見 [DL_OK](#dl_ok--00)） |
| `F2` | Session State |
| `F4` | Die ID |
| `E0` | Flash integrity 結果 |
| 其他（含 `F0`、`C0`、`C1`、`00`、錯誤碼等） | 固定 3 bytes，不解析 |

注意 `HDLL_CMD` 在每個 frame 後都會更新（包括 RSP），因此 log 必須依序、逐行送進同一個 Python process 才能正確配對；第二個連續的 `DL_OK` 會拿到 `pre_op = '00'`（見 DL_OK 範例 3）。

---

<a id="dl_reset"></a><a id="DL_RESET"></a>
## DL_RESET  (`F0`)

| 項目 | 值 |
|---|---|
| Op Code / 類型 | `F0` / CMD |
| Handler | [`HDLL.py:14`](../../nci_decoder/Nxp_pkg/HDLL.py#L14) `DL_RESET` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | （保留 / 填 0） | 3 | 不解析，直接跳過（Frame Length = 4） |

### 範例
- Raw：`00 04 F0 00 00 00 18 5B`

```text
  << Nxp HDLL: DL_RESET >>  
  * HDLL CMD: DL_RESET
  * CRC: 185B (CRC-16-CCITT-FALSE)
#end
```


範例：Frame Length = 1（無 3 bytes padding）時的長度錯誤：
- Raw：`00 01 F0 10 B2`

```text
  << Nxp HDLL: DL_RESET >>  
  * HDLL CMD: DL_RESET
  * CRC: 10B2 (CRC-16-CCITT-FALSE)

Error: Payload error!!
  check: 3 Octet(s)
  Packet Len: 5.0 Octet(s)
  Frame Len: 1 Octet(s)
#end
```


<a id="dl_get_version"></a><a id="DL_GET_VERSION"></a>
## DL_GET_VERSION  (`F1`)

| 項目 | 值 |
|---|---|
| Op Code / 類型 | `F1` / CMD |
| Handler | [`HDLL.py:22`](../../nci_decoder/Nxp_pkg/HDLL.py#L22) `DL_GET_VERSION` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | （保留 / 填 0） | 3 | 不解析，直接跳過 |

### 範例
- Raw：`00 04 F1 00 00 00 6E EF`

```text
  << Nxp HDLL: DL_GET_VERSION >>  
  * HDLL CMD: DL_GET_VERSION
  * CRC: 6EEF (CRC-16-CCITT-FALSE)
#end
```


設定 Chunk bit（byte0 = `0x20`）的同一個 CMD——輸出多一行 `* Chunk: 1`：
- Raw：`20 04 F1 00 00 00 5B E7`

```text
  << Nxp HDLL: DL_GET_VERSION >>  
  * Chunk: 1
  * HDLL CMD: DL_GET_VERSION
  * CRC: 5BE7 (CRC-16-CCITT-FALSE)
#end
```


<a id="dl_get_session_state"></a><a id="DL_GET_SESSION_STATE"></a>
## DL_GET_SESSION_STATE  (`F2`)

| 項目 | 值 |
|---|---|
| Op Code / 類型 | `F2` / CMD |
| Handler | [`HDLL.py:30`](../../nci_decoder/Nxp_pkg/HDLL.py#L30) `DL_GET_SESSION_STATE` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | （保留 / 填 0） | 3 | 不解析，直接跳過 |

### 範例
- Raw：`00 04 F2 00 00 00 F5 33`

```text
  << Nxp HDLL: DL_GET_SESSION_STATE >>  
  * HDLL CMD: DL_GET_SESSION_STATE
  * CRC: F533 (CRC-16-CCITT-FALSE)
#end
```


<a id="dl_get_die_id"></a><a id="DL_GET_DIE_ID"></a>
## DL_GET_DIE_ID  (`F4`)

| 項目 | 值 |
|---|---|
| Op Code / 類型 | `F4` / CMD |
| Handler | [`HDLL.py:38`](../../nci_decoder/Nxp_pkg/HDLL.py#L38) `DL_GET_DIE_ID` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | （保留 / 填 0） | 3 | 不解析，直接跳過 |

### 範例
- Raw：`00 04 F4 00 00 00 D2 AA`

```text
  << Nxp HDLL: DL_GET_DIE_ID >>  
  * HDLL CMD: DL_GET_DIE_ID
  * CRC: D2AA (CRC-16-CCITT-FALSE)
#end
```


<a id="dl_check_integrity"></a><a id="DL_CHECK_INTEGRITY"></a>
## DL_CHECK_INTEGRITY  (`E0`)

| 項目 | 值 |
|---|---|
| Op Code / 類型 | `E0` / CMD |
| Handler | [`HDLL.py:46`](../../nci_decoder/Nxp_pkg/HDLL.py#L46) `DL_CHECK_INTEGRITY` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | （保留 / 填 0） | 3 | 不解析，直接跳過 |

### 範例
- Raw：`00 04 E0 00 00 00 03 FC`

```text
  << Nxp HDLL: DL_CHECK_INTEGRITY >>  
  * HDLL CMD: DL_CHECK_INTEGRITY
  * CRC: 03FC (CRC-16-CCITT-FALSE)
#end
```


<a id="dl_sec_write"></a><a id="DL_SEC_WRITE"></a>
## DL_SEC_WRITE  (`C0`)

| 項目 | 值 |
|---|---|
| Op Code / 類型 | `C0` / CMD |
| Handler | [`HDLL.py:54`](../../nci_decoder/Nxp_pkg/HDLL.py#L54) `DL_SEC_WRITE` |

依 `len`（= Frame Length）分兩種格式：

### Payload 格式 — First frame（`len == 502`）
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | （未命名） | 1 | 跳過，不印 |
| 2 | FW version | 2 | raw hex |
| 3 | NONCE | 16 | raw hex |
| 4 | DIEID | 16 | raw hex |
| 5 | CHIPMASK | 2 | raw hex |
| 6 | MASKEDKEY | 16 | raw hex |
| 7 | UDFSEED | 32 | raw hex |
| 8 | HASH | 32 | raw hex |
| 9 | SIGN | 384 | raw hex |

合計 501 bytes + op code = Frame Length 502。

### Payload 格式 — Middle / Last frame（`len != 502`）
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Data size | 2 | big-endian 整數 `N`，不印 |
| 2 | ADDR | 3 | raw hex |
| 3 | DATA | N | raw hex |
| 4 | HASH | 32 | **僅 Middle**：當 `(len-1)*2 > p_payload`（DATA 之後還有剩餘 bytes）時才讀 32 bytes HASH；否則視為 Last frame，沒有 HASH |

### 範例
First frame（Chunk bit = 1，Frame Length = 0x1F6 = 502；欄位內容為測試用填充值）：
- Raw（506 bytes）：

```text
21F6C000010311111111111111111111111111111111222222222222222222222222222222220F0F3333333333333333333333333333333344444444444444444444444444444444444444444444444444444444444444445555555555555555555555555555555555555555555555555555555555555555ABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABAB74E3
```

```text
  << Nxp HDLL: DL_SEC_WRITE >>  
  * Chunk: 1
  * HDLL CMD: DL_SEC_WRITE
  * FW version: 0103
  * NONCE: 11111111111111111111111111111111
  * DIEID: 22222222222222222222222222222222
  * CHIPMASK: 0F0F
  * MASKEDKEY: 33333333333333333333333333333333
  * UDFSEED: 4444444444444444444444444444444444444444444444444444444444444444
  * HASH: 5555555555555555555555555555555555555555555555555555555555555555
  * SIGN: ABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABABAB
  * CRC: 74E3 (CRC-16-CCITT-FALSE)
#end
```


Middle frame（Data size = 4，帶 HASH）：
- Raw：`20 2A C0 00 04 01 20 00 DE AD BE EF 66 66 66 66 66 66 66 66 66 66 66 66 66 66 66 66 66 66 66 66 66 66 66 66 66 66 66 66 66 66 66 66 1C 2E`

```text
  << Nxp HDLL: DL_SEC_WRITE >>  
  * Chunk: 1
  * HDLL CMD: DL_SEC_WRITE
  * ADDR: 012000
  * DATA: DEADBEEF
  * HASH: 6666666666666666666666666666666666666666666666666666666666666666
  * CRC: 1C2E (CRC-16-CCITT-FALSE)
#end
```


Last frame（Data size = 4，無 HASH）：
- Raw：`00 0A C0 00 04 01 20 04 CA FE BA BE 8F 67`

```text
  << Nxp HDLL: DL_SEC_WRITE >>  
  * HDLL CMD: DL_SEC_WRITE
  * ADDR: 012004
  * DATA: CAFEBABE
  * CRC: 8F67 (CRC-16-CCITT-FALSE)
#end
```


### 實作備註
- First / Middle / Last 的判斷完全依 Frame Length：只要 Frame Length 恰為 502 就當 First frame，不看 chunk bit 或內容。
- First frame 第 1 個 byte 被跳過且不印。

<a id="dl_cert_frame"></a><a id="DL_CERT_FRAME"></a>
## DL_CERT_FRAME  (`C1`)

| 項目 | 值 |
|---|---|
| Op Code / 類型 | `C1` / CMD |
| Handler | [`HDLL.py:102`](../../nci_decoder/Nxp_pkg/HDLL.py#L102) `DL_CERT_FRAME` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | （未命名） | 1 | 跳過，不印 |
| 2 | Chip version | 2 | raw hex |
| 3 | Chip Life Cycle | 2 | raw hex |
| 4 | Certificate version | 2 | raw hex |
| 5 | PK_MOD | 384 | raw hex |
| 6 | PK_EXP | 8 | raw hex |
| 7 | PK_CRC | 4 | raw hex |
| 8 | SIGN | 384 | raw hex |

合計 787 bytes + op code = Frame Length 788（0x314）。

### 範例
（欄位內容為測試用填充值）
- Raw（792 bytes）：

```text
0314C1003300C5A00100777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777000000000001000112345678888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888342E
```

```text
  << Nxp HDLL: DL_CERT_FRAME >>  
  * HDLL CMD: DL_CERT_FRAME
  * Chip version: 3300
  * Chip Life Cycle: C5A0
  * Certificate version: 0100
  * PK_MOD: 777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777
  * PK_EXP: 0000000000010001
  * PK_CRC: 12345678
  * SIGN: 888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888
  * CRC: 342E (CRC-16-CCITT-FALSE)
#end
```


### 實作備註
- 第 1 個 byte 被跳過且不印。
- 格式固定，未依長度分支；Frame Length 不是 788 時會出現 `Payload error!!`。

---

<a id="dl_ok"></a><a id="DL_OK"></a>
## DL_OK  (`00`)

| 項目 | 值 |
|---|---|
| Op Code / 類型 | `00` / RSP（DL_STATUS_OK） |
| Handler | [`HDLL.py:130`](../../nci_decoder/Nxp_pkg/HDLL.py#L130) `DL_OK` |

先印 `* HDLL RSP: DL_STATUS_OK`，再依 `pre_op`（前一個 frame 的 op code，即全域 `HDLL_CMD`）分支：

### Payload 格式 — `pre_op == 'F1'`（DL_GET_VERSION 回應）
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | HW version | 1 | raw hex |
| 2 | ROM code | 1 | raw hex |
| 3 | Model ID | 1 | raw hex |
| 4 | FW version | 2 | raw hex |
| 5 | Internal FW build revision | 4 | raw hex |
| 6 | Chip version | 2 | raw hex |
| 7 | Chip Life Cycle | 2 | raw hex |
| 8 | Certificate version | 2 | raw hex |

合計 15 bytes（Frame Length 16）。

### Payload 格式 — `pre_op == 'F2'`（DL_GET_SESSION_STATE 回應）
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Session State | 1 | handler 內區域表 `tbl_ssta`：`00` = closed、`01` = open、`02` = locked；其他值印 `RFU (xx)` |
| 2 | （保留） | 2 | 跳過（程式一次前進 3 bytes） |

### Payload 格式 — `pre_op == 'F4'`（DL_GET_DIE_ID 回應）
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | （保留） | 3 | 跳過，不印 |
| 2 | DIEID | 16 | raw hex |

合計 19 bytes（Frame Length 20）。

### Payload 格式 — `pre_op == 'E0'`（DL_CHECK_INTEGRITY 回應）
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Nb of data sections | 1 | 整數 `data_num`（只用於表格輸出） |
| 2 | Nb of code sections | 1 | 整數 `code_num` |
| 3 | （保留） | 1 | 跳過 |
| 4 | CRC check status | 4 | 32-bit 狀態位元，**以 little-endian 解讀**：第 4 個 byte 印為 `sections 1 to 8`、第 3 個為 `9 to 16`、第 2 個為 `17 to 24`、第 1 個為 `25 to 32`。之後把這 4 個 byte 依 1–8、9–16、17–24、25–32 的順序串成 32 字元的 bit 字串（每 byte MSB 在前）；data section `i`（1-based）的狀態 = 第 `i` 個 bit，code section `i` 的狀態 = 第 `i+28` 個 bit；`1` = OK、`0` = KO（handler 內區域表 `tbl_status`） |
| 5 | Data sections | 4 × 28 = 112 | 固定 28 個 4-byte 值，每個值以 little-endian 反轉後顯示於括號內 |
| 6 | Code sections | 4 × 4 = 16 | 固定 4 個 4-byte 值，同樣反轉後顯示 |

合計 135 bytes（Frame Length 136 = 0x88）。輸出為 `* Flash integrity:` 表格，共 `min(max(data_num, code_num), 28)` 列：第 `i` 列在 `i` < `data_num` 時印 data section 狀態與值，`i` < `code_num` 時於同列右側印 code section 狀態與值；只有 code section 的列，左側 data 欄留白。

### Payload 格式 — 其他 `pre_op`
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | （保留） | 3 | 跳過，不印 |

### 範例
範例 1：`DL_GET_VERSION` → `DL_OK`（`pre_op = 'F1'`）
- 第 1 筆 Raw：`00 04 F1 00 00 00 6E EF`

```text
  << Nxp HDLL: DL_GET_VERSION >>  
  * HDLL CMD: DL_GET_VERSION
  * CRC: 6EEF (CRC-16-CCITT-FALSE)
#end
```

- 第 2 筆 Raw：`00 10 00 12 40 04 01 03 01 02 03 04 33 00 C5 A0 01 00 CD D5`

```text
  << Nxp HDLL: DL_OK >>  
  * HDLL RSP: DL_STATUS_OK
  * HW version: 12
  * ROM code: 40
  * Model ID: 04
  * FW version: 0103
  * Internal FW build revision: 01020304
  * Chip version: 3300
  * Chip Life Cycle: C5A0
  * Certificate version: 0100
  * CRC: CDD5 (CRC-16-CCITT-FALSE)
#end
```


範例 2：`DL_GET_SESSION_STATE` → `DL_OK`（`pre_op = 'F2'`）
- 第 1 筆 Raw：`00 04 F2 00 00 00 F5 33`

```text
  << Nxp HDLL: DL_GET_SESSION_STATE >>  
  * HDLL CMD: DL_GET_SESSION_STATE
  * CRC: F533 (CRC-16-CCITT-FALSE)
#end
```

- 第 2 筆 Raw：`00 04 00 01 00 00 B0 26`

```text
  << Nxp HDLL: DL_OK >>  
  * HDLL RSP: DL_STATUS_OK
  * Session State: open
  * CRC: B026 (CRC-16-CCITT-FALSE)
#end
```


範例 3：`DL_GET_SESSION_STATE` → `DL_OK` → `DL_OK`（第二個 `DL_OK` 的 `pre_op = '00'`，走「其他」分支）
- 第 1 筆 Raw：`00 04 F2 00 00 00 F5 33`

```text
  << Nxp HDLL: DL_GET_SESSION_STATE >>  
  * HDLL CMD: DL_GET_SESSION_STATE
  * CRC: F533 (CRC-16-CCITT-FALSE)
#end
```

- 第 2 筆 Raw：`00 04 00 01 00 00 B0 26`

```text
  << Nxp HDLL: DL_OK >>  
  * HDLL RSP: DL_STATUS_OK
  * Session State: open
  * CRC: B026 (CRC-16-CCITT-FALSE)
#end
```

- 第 3 筆 Raw：`00 04 00 00 00 00 87 16`

```text
  << Nxp HDLL: DL_OK >>  
  * HDLL RSP: DL_STATUS_OK
  * CRC: 8716 (CRC-16-CCITT-FALSE)
#end
```


範例 4：`DL_GET_DIE_ID` → `DL_OK`（`pre_op = 'F4'`）
- 第 1 筆 Raw：`00 04 F4 00 00 00 D2 AA`

```text
  << Nxp HDLL: DL_GET_DIE_ID >>  
  * HDLL CMD: DL_GET_DIE_ID
  * CRC: D2AA (CRC-16-CCITT-FALSE)
#end
```

- 第 2 筆 Raw：`00 14 00 00 00 00 00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF 64 8A`

```text
  << Nxp HDLL: DL_OK >>  
  * HDLL RSP: DL_STATUS_OK
  * DIEID: 00112233445566778899AABBCCDDEEFF
  * CRC: 648A (CRC-16-CCITT-FALSE)
#end
```


範例 5：`DL_CHECK_INTEGRITY` → `DL_OK`（`pre_op = 'E0'`；3 個 data sections、2 個 code sections，status byte 4 = `A0` = `10100000`，data section 1 OK / 2 KO / 3 OK；code section 1、2 對應第 29、30 bit，在 byte 1（`00`）中，故為 KO）
- 第 1 筆 Raw：`00 04 E0 00 00 00 03 FC`

```text
  << Nxp HDLL: DL_CHECK_INTEGRITY >>  
  * HDLL CMD: DL_CHECK_INTEGRITY
  * CRC: 03FC (CRC-16-CCITT-FALSE)
#end
```

- 第 2 筆 Raw（140 bytes）：

```text
008800030200000000A00100010002000100030001000400010005000100060001000700010008000100090001000A0001000B0001000C0001000D0001000E0001000F000100100001001100010012000100130001001400010015000100160001001700010018000100190001001A0001001B0001001C000100810003008200030083000300840003000F4A
```

```text
  << Nxp HDLL: DL_OK >>  
  * HDLL RSP: DL_STATUS_OK
  * CRC check for sections  1 to  8: A0
  *                         9 to 16: 00
  *                        17 to 24: 00
  *                        25 to 32: 00
  * Flash integrity:
         Data:  3               Code:  2
     1   OK (00010001)          KO (00030081)
     2   KO (00010002)          KO (00030082)
     3   OK (00010003)
  * CRC: 0F4A (CRC-16-CCITT-FALSE)
#end
```


範例 6：`DL_CHECK_INTEGRITY` 後收到只有 3 bytes payload 的 `DL_OK` → handler 例外
- 第 1 筆 Raw：`00 04 E0 00 00 00 03 FC`

```text
  << Nxp HDLL: DL_CHECK_INTEGRITY >>  
  * HDLL CMD: DL_CHECK_INTEGRITY
  * CRC: 03FC (CRC-16-CCITT-FALSE)
#end
```

- 第 2 筆 Raw：`00 04 00 00 00 00 87 16`

```text
  << Nxp HDLL: DL_OK >>  
  * HDLL RSP: DL_STATUS_OK
  * CRC check for sections  1 to  8: 
  *                         9 to 16: 
  *                        17 to 24: 
  *                        25 to 32: 
(Python 例外：ValueError: invalid literal for int() with base 16: '')
```


### 實作備註
- `pre_op == 'E0'` 分支假設 payload 一定是完整的 135 bytes；payload 不足時 `int('', 16)` 丟出 `ValueError`（範例 6），整行解析中斷、沒有 `#end`。
- E0 分支的 `Nb of data sections` / `Nb of code sections` 原本的 print 被註解掉，只出現在 `Flash integrity` 表頭。
- ✅ 已修正（2026-10）：E0 分支表格改跑 `max(data_num, code_num)` 列（上限 28），`code_num > data_num` 時多出的 code section 以 code-only 列印出。
- code 狀態取 bit `i+28`，等於只用到 32-bit 狀態中的最後 4 bits（code section 最多 4 個）。
- ✅ 已修正（2026-10）：`pre_op == 'F2'` 未知的 Session State 印 `RFU (xx)`。

## 錯誤 / 狀態 RSP（`01` – `31`）

| Op Code | Handler |
|---|---|
| `01` | [`HDLL.py:200`](../../nci_decoder/Nxp_pkg/HDLL.py#L200) `EDL_INVALID_ADDR` |
| `02` | [`HDLL.py:207`](../../nci_decoder/Nxp_pkg/HDLL.py#L207) `EDL_GENERIC_ERROR` |
| `0B` | [`HDLL.py:214`](../../nci_decoder/Nxp_pkg/HDLL.py#L214) `EDL_UNKNOW_CMD` |
| `0C` | [`HDLL.py:221`](../../nci_decoder/Nxp_pkg/HDLL.py#L221) `EDL_ABORTED_CMD` |
| `1E` | [`HDLL.py:228`](../../nci_decoder/Nxp_pkg/HDLL.py#L228) `EDL_ADDR_RANGE_OFL_ERROR` |
| `1F` | [`HDLL.py:235`](../../nci_decoder/Nxp_pkg/HDLL.py#L235) `EDL_BUFFER_OFL_ERROR` |
| `20` | [`HDLL.py:242`](../../nci_decoder/Nxp_pkg/HDLL.py#L242) `EDL_MEM_BSY` |
| `21` | [`HDLL.py:249`](../../nci_decoder/Nxp_pkg/HDLL.py#L249) `EDL_SIGNATURE_ERROR` |
| `24` | [`HDLL.py:256`](../../nci_decoder/Nxp_pkg/HDLL.py#L256) `EDL_FIRMWARE_VERSION_ERROR` |
| `28` | [`HDLL.py:263`](../../nci_decoder/Nxp_pkg/HDLL.py#L263) `EDL_PROTOCOL_ERROR` |
| `2D` | [`HDLL.py:270`](../../nci_decoder/Nxp_pkg/HDLL.py#L270) `PH_STATUS_DL_FIRST_CHUNK` |
| `2E` | [`HDLL.py:277`](../../nci_decoder/Nxp_pkg/HDLL.py#L277) `PH_STATUS_DL_NEXT_CHUNK` |
| `31` | [`HDLL.py:284`](../../nci_decoder/Nxp_pkg/HDLL.py#L284) `PH_STATUS_EDL_CERT_ERROR` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | （保留） | 3 | 跳過，不印（所有錯誤 / 狀態 RSP 相同，不使用 `pre_op`） |

### 範例
- Raw：`00 04 01 00 00 00 F1 A2`

```text
  << Nxp HDLL: EDL_INVALID_ADDR >>  
  * CRC: F1A2 (CRC-16-CCITT-FALSE)
#end
```

- Raw：`00 04 02 00 00 00 6A 7E`

```text
  << Nxp HDLL: EDL_GENERIC_ERROR >>  
  * CRC: 6A7E (CRC-16-CCITT-FALSE)
#end
```

- Raw：`00 04 0B 00 00 00 99 09`

```text
  << Nxp HDLL: EDL_UNKNOW_CMD >>  
  * CRC: 9909 (CRC-16-CCITT-FALSE)
#end
```

- Raw：`00 04 0C 00 00 00 C8 24`

```text
  << Nxp HDLL: EDL_ABORTED_CMD >>  
  * CRC: C824 (CRC-16-CCITT-FALSE)
#end
```

- Raw：`00 04 1E 00 00 00 3E EB`

```text
  << Nxp HDLL: EDL_ADDR_RANGE_OFL_ERROR >>  
  * CRC: 3EEB (CRC-16-CCITT-FALSE)
#end
```

- Raw：`00 04 1F 00 00 00 48 5F`

```text
  << Nxp HDLL: EDL_BUFFER_OFL_ERROR >>  
  * CRC: 485F (CRC-16-CCITT-FALSE)
#end
```

- Raw：`00 04 20 00 00 00 B0 58`

```text
  << Nxp HDLL: EDL_MEM_BSY >>  
  * CRC: B058 (CRC-16-CCITT-FALSE)
#end
```

- Raw：`00 04 21 00 00 00 C6 EC`

```text
  << Nxp HDLL: EDL_SIGNATURE_ERROR >>  
  * CRC: C6EC (CRC-16-CCITT-FALSE)
#end
```

- Raw：`00 04 24 00 00 00 7A A9`

```text
  << Nxp HDLL: EDL_FIRMWARE_VERSION_ERROR >>  
  * CRC: 7AA9 (CRC-16-CCITT-FALSE)
#end
```

- Raw：`00 04 28 00 00 00 35 9B`

```text
  << Nxp HDLL: EDL_PROTOCOL_ERROR >>  
  * CRC: 359B (CRC-16-CCITT-FALSE)
#end
```

- Raw：`00 04 2D 00 00 00 89 DE`

```text
  << Nxp HDLL: PH_STATUS_DL_FIRST_CHUNK >>  
  * CRC: 89DE (CRC-16-CCITT-FALSE)
#end
```

- Raw：`00 04 2E 00 00 00 12 02`

```text
  << Nxp HDLL: PH_STATUS_DL_NEXT_CHUNK >>  
  * CRC: 1202 (CRC-16-CCITT-FALSE)
#end
```

- Raw：`00 04 31 00 00 00 DD 4B`

```text
  << Nxp HDLL: PH_STATUS_EDL_CERT_ERROR >>  
  * CRC: DD4B (CRC-16-CCITT-FALSE)
#end
```


### 實作備註
- 這些 handler 不印任何欄位（連狀態名稱的 `* HDLL RSP:` 行都沒有），只靠標題 `<< Nxp HDLL: <名稱> >>` 表示狀態。

---

## 整體實作備註

- ✅ 已修正（2026-10）：Chunk bit 判斷改為 `chunk == '1'`，byte0 bit 5 = 1 時印 `* Chunk: 1`（見 DL_GET_VERSION、DL_SEC_WRITE Middle 範例）。
- ✅ 已修正（2026-10）：未知 op code 改用 `.get()`，標題印 `UNKNOWN (XX)`，並印 `Error: unknown HDLL op code XX, raw: <raw>`，不再 `KeyError`；例如：
- Raw：`00 04 AA 00 00 00 05 CB`

```text
  << Nxp HDLL: UNKNOWN (AA) >>  
Error: unknown HDLL op code AA, raw: 0004AA00000005CB
  * CRC: 05CB (CRC-16-CCITT-FALSE)
#end
```

- **只有 Nxp vendor 有 HDLL**：`Decoder_Main.py` 的 HDLL 分支呼叫 `pkg.HDLL`，但只有 `Nxp_pkg.__ctrl__` 定義 `HDLL()`。vendor 傳 `'None'` 時同一筆 `00 04 F1 00 00 00 6E EF` 會丟出 `AttributeError: module 'nfc_forum_2_0_pkg.__ctrl__' has no attribute 'HDLL'`（已實際執行確認）。
- ✅ 已修正（2026-10）：CRC 以 CRC-16-CCITT-FALSE 驗證，不一致時印 `    ! CRC mismatch: calculated YYYY`。
- **CMD / RSP 不分方向**：完全靠 op code 值判斷（CMD 為 `C0`–`F4`、RSP 為 `00`–`31`），`HDLL_CMD` 也會被 RSP 覆寫。
- **NCI 優先判斷**：若 HDLL frame 的第 3 byte（op code）剛好等於總長度 − 3，會被誤判為 NCI 封包；以目前的 op code 值與常見長度不會發生，但判斷順序如此。
- 無 payload 的 CMD（`F0`/`F1`/`F2`/`F4`/`E0`）與錯誤 RSP 都假設 payload 固定為 3 bytes（Frame Length = 4）；其他長度會印 `Payload error!!`（見 DL_RESET 第二個範例）。
- `Payload error!!` 訊息中印出的 `check` 為 handler 走過的 byte 數（不含 op code）。

## 範例產生方式

所有範例皆以 vendor `'Nxp'`、`mode = 2` 實際呼叫 `NFC_NCI_DECODER(len(raw)//2, raw, 'Nxp', 'None', 2)` 取得輸出（handler 丟出例外時，由測試程式 try/except 捕捉並以 `[測試程式捕捉到的例外]` 標示，該行不是 decoder 本身的輸出）；同一個「範例」中的多筆 frame 在同一個 Python process 內依序送入（以保留 `HDLL_CMD` 狀態），不同範例使用獨立 process（`HDLL_CMD` 從 `'00'` 開始）。CRC 欄位以 CRC-16-CCITT-FALSE 計算後附加。
