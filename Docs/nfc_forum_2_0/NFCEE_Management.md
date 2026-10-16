# NFCEE Management（GID = 0x2）— nfc_forum_2_0_pkg

本文件說明 `nci_decoder/nfc_forum_2_0_pkg/NFCEE_Management.py` 中所有 NFCEE Management 控制訊息的解析方式。Dispatch 依 `nfc_forum_2_0_pkg/__ctrl__.py` 中 `tbl_nci_ctrl["NFCEE Management"]` 群組（OID 0x00 ~ 0x03，0x04 ~ 0x3F 為 RFU、未登錄）。vendor 傳 `'None'`（或任何非 `Nxp` 的值）時走 `nfc_forum_2_0_pkg`。

每個 handler 收到的是 3-byte header 之後的 payload hex 字串，以 `p_payload`（hex 字元數 = 2×bytes）往前走並回傳最終 offset；`Decoder_Main.py` 會比對回傳值與 header 宣告的 Payload Length，不一致時印出 `Payload error!!`。表格查找使用 `NFC_table.tbl_xxx.get(value, "RFU")`，`NFC_table` 來自 `nfc_forum_2_0_pkg/__table__.py`（各表內容見 [Tables.md](Tables.md)）。

> 注意：`Decoder_Main.py` 呼叫 handler 時只傳入 `raw`（`pkg.tbl_nci_ctrl[gid_val][oid][mt_val](raw[6::])`），所以 handler 的 `vendor` / `model` 參數一律為預設值 `"None"`，`pkg_import.tbl_import()` 永遠載入 `nfc_forum_2_0_pkg.__table__`。

## 總覽

| OID | CMD | RSP | NTF | Handler |
|---|---|---|---|---|
| 0x00 | `22 00` | `42 00` | `62 00` | [NFCEE_DISCOVER_CMD](#nfcee_discover_cmd--22-00) / [NFCEE_DISCOVER_RSP](#nfcee_discover_rsp--42-00) / [NFCEE_DISCOVER_NTF](#nfcee_discover_ntf--62-00) |
| 0x01 | `22 01` | `42 01` | `62 01` | [NFCEE_MODE_SET_CMD](#nfcee_mode_set_cmd--22-01) / [NFCEE_MODE_SET_RSP](#nfcee_mode_set_rsp--42-01) / [NFCEE_MODE_SET_NTF](#nfcee_mode_set_ntf--62-01) |
| 0x02 | — | — | `62 02` | [NFCEE_STATUS_NTF](#nfcee_status_ntf--62-02) |
| 0x03 | `22 03` | `42 03` | — | [NFCEE_POWER_AND_LINK_CNTRL_CMD](#nfcee_power_and_link_cntrl_cmd--22-03) / [NFCEE_POWER_AND_LINK_CNTRL_RSP](#nfcee_power_and_link_cntrl_rsp--42-03) |

範例皆以下列方式實際執行取得（cwd = `E:/Project/NCI_Decoder/NCI_Decoder`，mode = 2，不印 raw）：

```
python -c "import sys; sys.path.insert(0,'nci_decoder'); import nci_decoder; from Decoder_Main import NFC_NCI_DECODER; raw='220000'; NFC_NCI_DECODER(len(raw)//2, raw, 'None', 'None', 2)"
```

---

<a id="nfcee_discover_cmd"></a><a id="NFCEE_DISCOVER_CMD"></a>
## NFCEE_DISCOVER_CMD  (`22 00`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NFCEE Management / 0x00 / CMD |
| Handler | [`NFCEE_Management.py:6`](../../nci_decoder/nfc_forum_2_0_pkg/NFCEE_Management.py#L6) `NFCEE_DISCOVER_CMD` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| — | （無 payload） | 0 | 固定印出 `(Empty)`，回傳 offset 0 |

### 範例
- Raw：`22 00 00`

```text
  << NFCEE_DISCOVER_CMD >>  
         (Empty)         
#end
```

### 實作備註
- Handler 不讀取任何 byte、固定回傳 0。若輸入帶有 1 byte payload（例如 NCI 1.x 的 Discovery Action 格式 `22 00 01 01`），會觸發長度檢查錯誤（實測輸出）：

```text
  << NFCEE_DISCOVER_CMD >>  
         (Empty)         
Error: Payload error!!
  Packet Len: 4 Octet(s)
  Payload Len: 1 Octet(s)
  Check Len: 0.0 Octet(s)
#end
```

---

<a id="nfcee_discover_rsp"></a><a id="NFCEE_DISCOVER_RSP"></a>
## NFCEE_DISCOVER_RSP  (`42 00`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NFCEE Management / 0x00 / RSP |
| Handler | [`NFCEE_Management.py:19`](../../nci_decoder/nfc_forum_2_0_pkg/NFCEE_Management.py#L19) `NFCEE_DISCOVER_RSP` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)），查無則 `RFU` |
| 2 | Number of NFCEEs | 1 | 轉十進位整數印出 |

### 範例
- Raw：`42 00 02 00 02`

```text
  << NFCEE_DISCOVER_RSP >>  
  * Status: STATUS_OK (00)
  * Number of NFCEEs: 2
#end
```

- Raw：`42 00 02 03 00`

```text
  << NFCEE_DISCOVER_RSP >>  
  * Status: STATUS_FAILED (03)
  * Number of NFCEEs: 0
#end
```

---

<a id="nfcee_discover_ntf"></a><a id="NFCEE_DISCOVER_NTF"></a>
## NFCEE_DISCOVER_NTF  (`62 00`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NFCEE Management / 0x00 / NTF |
| Handler | [`NFCEE_Management.py:41`](../../nci_decoder/nfc_forum_2_0_pkg/NFCEE_Management.py#L41) `NFCEE_DISCOVER_NTF` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | NFCEE ID | 1 | `tbl_nfcee_id`（見 [Tables](Tables.md#tbl_nfcee_id)）：同時印出「精確 key 查表結果」與「`range_lookup.find_range_key` 找到的範圍 key 查表結果」，查不到的部分印空字串 |
| 2 | NFCEE Status | 1 | `tbl_nfcee_disc_status`（見 [Tables](Tables.md#tbl_nfcee_disc_status)），精確查表，查無則 `RFU` |
| 3 | Number of Protocol Information Entries (n) | 1 | 十進位整數 |
| 4 | Supported NFCEE Protocols | n | 逐 byte 以 `range_lookup.lookup(tbl_nfcee_proto, …)`（見 [Tables](Tables.md#tbl_nfcee_proto)）查表（含 `'04-7F'`/`'80-FE'` 範圍 key），查無則 `RFU`；n = 0 時跳過（但仍印一個空行） |
| 5 | Number of NFCEE Information TLVs (m) | 1 | 十進位整數 |
| 6 | NFCEE Information TLV [0..m-1] | 每個 x+2 | 見下方 TLV 說明；m = 0 時跳過 |
| ﹂ | Type | 1 | 先用 `find_range_key(tbl_tlv_type, …)` 轉成範圍 key（無範圍命中則保留原值），再以 `tbl_tlv_type`（見 [Tables](Tables.md#tbl_tlv_type)）查表；括號內印原始 byte |
| ﹂ | Length (x) | 1 | 十進位整數 |
| ﹂ | Value | x | 一律先印原始 hex；Type 為 `02` / `04` 時再進一步解析（見下） |
| 7 | NFCEE Power Supply | 1 | 硬編碼：`00` → `NFCC control power supply for any NFCEE_UICCx`；`01` → `NFCC control power supply for NFCEE_eSE and NFCEE_NDEF`；其他 → `RFU (xx)` |

**TLV Type `02`（T3T Command Set Interface Supplementary Information）Value 解析：**

| # | 欄位 | 長度 (Octets) | 解析方式 |
|---|---|---|---|
| 1 | PMm | 8 | 原始 hex |
| 2 | Number of Entries (k) | 1 | 十進位整數 |
| 3 | Entry [0..k-1] | 每個 10 | |
| ﹂ | System Code | 2 | 原始 hex |
| ﹂ | Idm | 8 | 原始 hex |

**TLV Type `04`（NDEF）Value 解析：**

| # | 欄位 | 長度 (Octets) | 解析方式 |
|---|---|---|---|
| 1 | NDEF max size | 4 | 將 4 bytes **反轉 byte 順序**（以 little-endian 解讀）後轉十進位，單位 Bytes；括號內印原始 hex |
| 2 | Power State | 1 | 印 8-bit 二進位，再對 bit 5 ~ bit 0 逐一以 `tbl_pwr_state`（見 [Tables](Tables.md#tbl_pwr_state)）取名稱，bit = 1 印 `Apply`、0 印 `Not apply` |
| 3 | NDEF-NFCEE characteristics | 1 | 只看 bit 0：`0` → `Not persistent`，`1` → `Persistent` |

Power State bit 對應（來自 `tbl_pwr_state`）：

| Bit | 意義 |
|---|---|
| b7 ~ b6 | 不解析（表中為註解掉的 RFU） |
| b5 | Screen Off lock (Sub-State 3) |
| b4 | Screen On lock (Sub-State 2) |
| b3 | Screen off unlock (Sub-State 1) |
| b2 | Battery Off State |
| b1 | Switch Off State |
| b0 | Switch On State |

其他 TLV Type（`00` Hardware / Registration Identification、`01` ATR Bytes、`03` Host ID in the HCI Network、RFU、proprietary）只印 Type / Len / Val 原始 hex，不再細部解析。

### 範例
- Raw（HCI-NFCEE，APDU，Hardware/Registration ID TLV）：`62 00 0A 86 00 01 00 01 00 02 11 22 01`

```text
  << NFCEE_DISCOVER_NTF >>  
  * NFCEE ID: 86  (HCI-NFCEE)
  * NFCEE Status: Enabled (00)
  * Number of Protocol Info Entries: 1
  * Supported NFCEE Protocols: APDU (00), 
  * Number of NFCEE Info TLVs: 1
  * NFCEE Information:

   ~ [NFCEE Info TLV_0] ~  
    * Type: Hardware / Registration Identification (00)
    * Len: 2
    * Val: 1122

  * NFCEE Power Supply: NFCC control power supply for NFCEE_eSE and NFCEE_NDEF
#end
```

- Raw（T3T Command Set Interface Supplementary Information TLV）：`62 00 1B 10 00 01 02 01 02 13 01 02 03 04 05 06 07 08 01 12 FC 02 FE 00 01 02 03 04 05 00`

```text
  << NFCEE_DISCOVER_NTF >>  
  * NFCEE ID: 10  (NFCEE)
  * NFCEE Status: Enabled (00)
  * Number of Protocol Info Entries: 1
  * Supported NFCEE Protocols: Type 3 Tag Command Set (02), 
  * Number of NFCEE Info TLVs: 1
  * NFCEE Information:

   ~ [NFCEE Info TLV_0] ~  
    * Type: T3T Command Set Interface Supplementary Information (02)
    * Len: 19
    * Val: 01020304050607080112FC02FE000102030405
      * PMm: 0102030405060708
      * Number of Entries: 1
       ~ [Entry_0] ~   
        * System Code: 12FC
        * Idm: 02FE000102030405

  * NFCEE Power Supply: NFCC control power supply for any NFCEE_UICCx
#end
```

- Raw（NDEF TLV）：`62 00 0E 10 00 01 03 01 04 06 00 10 00 00 3F 01 01`

```text
  << NFCEE_DISCOVER_NTF >>  
  * NFCEE ID: 10  (NFCEE)
  * NFCEE Status: Enabled (00)
  * Number of Protocol Info Entries: 1
  * Supported NFCEE Protocols: Transparent (03), 
  * Number of NFCEE Info TLVs: 1
  * NFCEE Information:

   ~ [NFCEE Info TLV_0] ~  
    * Type: NDEF (04)
    * Len: 6
    * Val: 001000003F01
      * NDEF max size: 4096 Bytes (00100000)
      * Power State: 00111111 (3F)
       ~ Screen Off lock (Sub-State 3):    Apply     
       ~ Screen On lock (Sub-State 2):     Apply     
       ~ Screen off unlock (Sub-State 1):  Apply     
       ~ Battery Off State:                Apply     
       ~ Switch Off State:                 Apply     
       ~ Switch On State:                  Apply     
      * NDEF-NFCEE characteristics: Persistent

  * NFCEE Power Supply: NFCC control power supply for NFCEE_eSE and NFCEE_NDEF
#end
```

- Raw（無 Protocol、proprietary TLV Type、RFU Power Supply）：`62 00 07 81 02 00 01 A1 00 05`

```text
  << NFCEE_DISCOVER_NTF >>  
  * NFCEE ID: 81  (HCI-NFCEE)
  * NFCEE Status: Unresponsive (02)
  * Number of Protocol Info Entries: 0

  * Number of NFCEE Info TLVs: 1
  * NFCEE Information:

   ~ [NFCEE Info TLV_0] ~  
    * Type: For proprietary use (A1)
    * Len: 0
    * Val: 

  * NFCEE Power Supply: RFU (05)
#end
```

- Raw（DH-NFCEE，proprietary protocol 值）：`62 00 06 00 00 01 80 00 00`

```text
  << NFCEE_DISCOVER_NTF >>  
  * NFCEE ID: 00 DH-NFCEE 
  * NFCEE Status: Enabled (00)
  * Number of Protocol Info Entries: 1
  * Supported NFCEE Protocols: For proprietary use (80), 
  * Number of NFCEE Info TLVs: 0

  * NFCEE Power Supply: NFCC control power supply for any NFCEE_UICCx
#end
```

### 實作備註
- ✅ 已修正（2026-10）：Supported NFCEE Protocols 改用 `range_lookup.lookup`，`0x80`~`0xFE` 顯示 `For proprietary use`（見上方 `62 00 06 00 00 01 80 00 00` 範例）。
- **NFCEE Status 未做範圍查表**：`tbl_nfcee_disc_status` 的 `'03-FF'` 範圍 key 不會被命中，但 fallback 值剛好也是 `RFU`，輸出結果一致。
- NFCEE ID 的輸出格式為 `NFCEE ID: <hex> <精確值> <範圍值>`，因兩者其中之一必為空字串，輸出會出現連續兩個空白（例如 `10  (NFCEE)`）或行尾多一個空白（例如 `00 DH-NFCEE `）。
- Supported NFCEE Protocols 每個項目後都印 `, `，最後一項也帶逗號。
- NDEF TLV 的 `NDEF max size` 程式以 byte 反序（little-endian）解讀 4 bytes；NDEF TLV / T3T TLV 的子欄位解析不檢查 Length 是否足夠，Value 過短時會以空字串切片（`int('', 16)` 可能拋例外）。
- NFCEE Power Supply 的意義字串為硬編碼（未使用 `__table__.py` 對照表）。

---

<a id="nfcee_mode_set_cmd"></a><a id="NFCEE_MODE_SET_CMD"></a>
## NFCEE_MODE_SET_CMD  (`22 01`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NFCEE Management / 0x01 / CMD |
| Handler | [`NFCEE_Management.py:153`](../../nci_decoder/nfc_forum_2_0_pkg/NFCEE_Management.py#L153) `NFCEE_MODE_SET_CMD` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | NFCEE ID | 1 | `tbl_nfcee_id`（見 [Tables](Tables.md#tbl_nfcee_id)），精確 + 範圍查表（同 NFCEE_DISCOVER_NTF） |
| 2 | NFCEE Mode | 1 | 硬編碼：`00` → `Disable`；`01` → `Enable`；其他 → `RFU (xx)` |

### 範例
- Raw：`22 01 02 10 01`

```text
  << NFCEE_MODE_SET_CMD >>  
  * NFCEE ID: 10  (NFCEE)
  * NFCEE Mode: Enable
#end
```

- Raw：`22 01 02 86 00`

```text
  << NFCEE_MODE_SET_CMD >>  
  * NFCEE ID: 86  (HCI-NFCEE)
  * NFCEE Mode: Disable
#end
```

- Raw：`22 01 02 10 05`

```text
  << NFCEE_MODE_SET_CMD >>  
  * NFCEE ID: 10  (NFCEE)
  * NFCEE Mode: RFU (05)
#end
```

---

<a id="nfcee_mode_set_rsp"></a><a id="NFCEE_MODE_SET_RSP"></a>
## NFCEE_MODE_SET_RSP  (`42 01`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NFCEE Management / 0x01 / RSP |
| Handler | [`NFCEE_Management.py:180`](../../nci_decoder/nfc_forum_2_0_pkg/NFCEE_Management.py#L180) `NFCEE_MODE_SET_RSP` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)），查無則 `RFU` |

### 範例
- Raw：`42 01 01 00`

```text
  << NFCEE_MODE_SET_RSP >>  
  * Status: STATUS_OK (00)
#end
```

---

<a id="nfcee_mode_set_ntf"></a><a id="NFCEE_MODE_SET_NTF"></a>
## NFCEE_MODE_SET_NTF  (`62 01`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NFCEE Management / 0x01 / NTF |
| Handler | [`NFCEE_Management.py:196`](../../nci_decoder/nfc_forum_2_0_pkg/NFCEE_Management.py#L196) `NFCEE_MODE_SET_NTF` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)），查無則 `RFU` |

### 範例
- Raw：`62 01 01 00`

```text
  << NFCEE_MODE_SET_NTF >>  
  * Status: STATUS_OK (00)
#end
```

---

<a id="nfcee_status_ntf"></a><a id="NFCEE_STATUS_NTF"></a>
## NFCEE_STATUS_NTF  (`62 02`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NFCEE Management / 0x02 / NTF |
| Handler | [`NFCEE_Management.py:212`](../../nci_decoder/nfc_forum_2_0_pkg/NFCEE_Management.py#L212) `NFCEE_STATUS_NTF` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | NFCEE ID | 1 | `tbl_nfcee_id`（見 [Tables](Tables.md#tbl_nfcee_id)），精確 + 範圍查表 |
| 2 | NFCEE Status | 1 | `range_lookup.lookup(tbl_nfcee_status, …)`（見 [Tables](Tables.md#tbl_nfcee_status)），含 `'03-7F'`/`'80-FF'` 範圍 key，查無則 `RFU` |

### 範例
- Raw：`62 02 02 10 02`

```text
  << NFCEE_STATUS_NTF >>  
  * NFCEE ID: 10  (NFCEE)
  * NFCEE Status: NFCEE Initialization sequence completed (02)
#end
```

- Raw：`62 02 02 82 81`

```text
  << NFCEE_STATUS_NTF >>  
  * NFCEE ID: 82  (HCI-NFCEE)
  * NFCEE Status: Proprietary (81)
#end
```

### 實作備註
- ✅ 已修正（2026-10）：NFCEE Status 改用 `range_lookup.lookup`，`0x80`~`0xFF` 顯示 `Proprietary`（見上方 `62 02 02 82 81` 範例）。
- 此欄位使用 `tbl_nfcee_status`（Table 122），與 NFCEE_DISCOVER_NTF 的 NFCEE Status（`tbl_nfcee_disc_status`，Table 117）是不同表，程式已正確區分。

---

<a id="nfcee_power_and_link_cntrl_cmd"></a><a id="NFCEE_POWER_AND_LINK_CNTRL_CMD"></a>
## NFCEE_POWER_AND_LINK_CNTRL_CMD  (`22 03`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NFCEE Management / 0x03 / CMD |
| Handler | [`NFCEE_Management.py:234`](../../nci_decoder/nfc_forum_2_0_pkg/NFCEE_Management.py#L234) `NFCEE_POWER_AND_LINK_CNTRL_CMD` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | NFCEE ID | 1 | `tbl_nfcee_id`（見 [Tables](Tables.md#tbl_nfcee_id)），精確 + 範圍查表 |
| 2 | NFCEE Power and Link Configuration | 1 | 硬編碼（見下表），其他 → `RFU (xx)` |

| 值 (hex) | 輸出字串 |
|---|---|
| `00` | NFCC decides (default state). |
| `01` | NFCEE Power Supply always On. |
| `02` | NFCC to NFCEE Communication link always active when the NFCEE is powered on. |
| `03` | NFCEE Power supply and NFCC to NFCEE communication link are always on. |

### 範例
- Raw：`22 03 02 10 03`

```text
  << NFCEE_POWER_AND_LINK_CNTRL_CMD >>  
  * NFCEE ID: 10  (NFCEE)
  * NFCEE Power and Link Cfg: NFCEE Power supply and NFCC to NFCEE communication link are always on.
#end
```

- Raw：`22 03 02 10 07`

```text
  << NFCEE_POWER_AND_LINK_CNTRL_CMD >>  
  * NFCEE ID: 10  (NFCEE)
  * NFCEE Power and Link Cfg: RFU (07)
#end
```

---

<a id="nfcee_power_and_link_cntrl_rsp"></a><a id="NFCEE_POWER_AND_LINK_CNTRL_RSP"></a>
## NFCEE_POWER_AND_LINK_CNTRL_RSP  (`42 03`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NFCEE Management / 0x03 / RSP |
| Handler | [`NFCEE_Management.py:265`](../../nci_decoder/nfc_forum_2_0_pkg/NFCEE_Management.py#L265) `NFCEE_POWER_AND_LINK_CNTRL_RSP` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)），查無則 `RFU` |

### 範例
- Raw：`42 03 01 00`

```text
  << NFCEE_POWER_AND_LINK_CNTRL_RSP >>  
  * Status: STATUS_OK (00)
#end
```

### 實作備註
- 原始碼第 264 行函式上方的註解寫成 `# 22 03`，實際 RSP header 應為 `42 03`（僅註解誤植，不影響 dispatch）。
