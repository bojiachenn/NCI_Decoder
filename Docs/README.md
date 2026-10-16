# NCI Decoder — Command Payload 與 Parsing Table 文件

本資料夾整理 `NCI_Decoder` 專案（repo 根目錄的 `nci_decoder/`）中所有 NCI command 的 payload 格式、解析方式與對照表（`tbl_*`），以程式碼實作為準，並附實際執行 decoder 取得的範例輸出。

## 目錄

| Package | 文件 | 內容 |
|---|---|---|
| `nfc_forum_2_0_pkg`（預設） | [NCI_Core.md](nfc_forum_2_0/NCI_Core.md) | GID 0x0 NCI Core（CORE_RESET / INIT / SET_CONFIG / GET_CONFIG / CONN_* ...） |
| | [RF_Management.md](nfc_forum_2_0/RF_Management.md) | GID 0x1 RF Management（RF_DISCOVER / INTF_ACTIVATED / DEACTIVATE / Listen Mode Routing ...） |
| | [NFCEE_Management.md](nfc_forum_2_0/NFCEE_Management.md) | GID 0x2 NFCEE Management |
| | [Tables.md](nfc_forum_2_0/Tables.md) | `nfc_forum_2_0_pkg/__table__.py` 全部對照表 + MT/GID 表 |
| `Nxp_pkg`（vendor = `Nxp`） | [NCI_Core.md](nxp/NCI_Core.md) | NXP 版 NCI Core（含 NXP 專屬 config parameter） |
| | [RF_Management.md](nxp/RF_Management.md) | NXP 版 RF Management + SN2x0 擴充 NTF |
| | [NFCEE_Management.md](nxp/NFCEE_Management.md) | NXP 版 NFCEE Management |
| | [Proprietary.md](nxp/Proprietary.md) | GID 0xF Proprietary（2F/4F/6F） |
| | [HDLL.md](nxp/HDLL.md) | NXP HDLL 下載協定（2-byte header + CRC16） |
| | [Tables.md](nxp/Tables.md) | `Nxp_pkg/__table__.py` 全部對照表（含與 forum 版差異） |
| `nfc_forum_2_3_pkg`（未接上 dispatch） | [README.md](nfc_forum_2_3/README.md) | NCI 2.3 相對 2.0 的增量 command 與表格 |

## NCI 封包結構

### Control Packet（CMD / RSP / NTF）

```
Octet 0                         Octet 1                 Octet 2          Octet 3..
+-------+-----+---------+       +-----+-----------+     +-------------+  +---------+
| MT(3) |PBF(1)| GID(4) |       | RFU | OID (6)   |     | Payload Len |  | Payload |
+-------+-----+---------+       +-----+-----------+     +-------------+  +---------+
```

| MT (bits 7-5) | 類型 | Octet 0 高 nibble |
|---|---|---|
| `000b` | DATA | `0x0_` |
| `001b` | CMD | `0x2_` |
| `010b` | RSP | `0x4_` |
| `011b` | NTF | `0x6_` |
| `100b`-`111b` | RFU | — |

| GID | 群組 | CMD / RSP / NTF 首 byte |
|---|---|---|
| `0000b` | NCI Core | `20` / `40` / `60` |
| `0001b` | RF Management | `21` / `41` / `61` |
| `0010b` | NFCEE Management | `22` / `42` / `62` |
| `0011b` | NFCC Management | `23` / `43` / `63`（未實作 handler） |
| `0100b` | Test Management | `24` / `44` / `64`（未實作 handler） |
| `1111b` | Proprietary | `2F` / `4F` / `6F`（僅 Nxp_pkg） |

PBF = 1 表示分段封包，decoder 會在輸出最後印出 `PBF: 1`。

### Data Packet

```
Octet 0: MT=000 | PBF | Conn ID(4)    Octet 1: RFU(6) | Credits(2)    Octet 2: Payload Len    Octet 3..: Data
```

Conn ID `0` = Static RF Connection（DH ↔ Remote NFC Endpoint）、`1` = Static HCI Connection、其他 = 動態分配。Data payload 目前只印 raw hex，不再解析。

## 解碼流程（`nci_decoder/Decoder_Main.py` → `NFC_NCI_DECODER`）

1. `vendor_registry.resolve(vendor)` 取得 package：`"Nxp"`（不分大小寫）→ `Nxp_pkg`，其他 → `nfc_forum_2_0_pkg`。
2. 解析 Octet 0 → MT / PBF / GID，Octet 1 → OID，Octet 2 → Payload Length。
3. 若 `Payload Length == 封包總長 - 3`：
   - DATA → 直接印出 Conn ID / Credits / data。
   - 控制封包 → 呼叫 `pkg.tbl_nci_ctrl[GID][OID][MT](payload_hex)`（定義於各 package 的 `__ctrl__.py`）；找不到則印 `<< ERROR_NOT_FOUND >>`。
4. 否則若符合 NXP HDLL 長度規則（13-bit frame length == 封包總長 - 4）→ `pkg.HDLL(raw, mode)`，見 [nxp/HDLL.md](nxp/HDLL.md)。
5. 都不符合 → `Error: Unknown raw data!`。

每個 handler 以 `p_payload`（hex 字元 offset，1 byte = 2）逐欄解析並回傳最終 offset；若 ≠ `2 × (封包長 - 3)`，印出 `Error: Payload error!!` 與 `Check Len`。欄位值以 `NFC_table.tbl_xxx.get(value, "RFU")` 查表，查不到的值顯示 `RFU`。

## 參考

- NCI 2.0 規範與表格比對：`NCI_ref/NCI_commands_table_ref.md`（位於 repo 外的工作資料夾 `E:\Project\NCI_Decoder\NCI_ref\`，未納入版本控制）
- 新增 command / vendor 的步驟：[`CLAUDE.md`](../CLAUDE.md)
- 網頁版 parsing tool：[`Web_ver/`](../Web_ver/README.md)（其 Reference 頁面顯示的就是本資料夾的內容）
