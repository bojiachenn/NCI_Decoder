# NXP Proprietary（GID 0xF）

本文件說明 `nci_decoder/Nxp_pkg/Proprietary.py` 中，由 `Nxp_pkg/__ctrl__.py` 的 `tbl_nci_ctrl["Proprietary"]` 註冊的 SN2x0 NFCC-NCI 擴充控制訊息（程式註解引用 *Table 181. [SN2x0 NFCC-NCI] extensions to Control Messages*、*Table 13. SN2x0 NFCC-NCI additional commands/notifications*）。
Header 首 byte：CMD = `2F`、RSP = `4F`、NTF = `6F`。Dispatch 時 vendor 需傳 `'Nxp'`，handler 收到 header 之後的 payload hex 字串（`Decoder_Main.py` 已將其轉為大寫）。

對照表：`NFC_table` = `Nxp_pkg/__table__.py`，內容見 [Tables.md](Tables.md)。handler 內部自行宣告的 local dict（例如 `tbl_spc_status`）不在 `__table__.py`，直接列在本文件各節中。

模組層級的狀態變數（跨封包保存，影響後續解碼）：

| 變數 | 初始值 | 寫入者 | 讀取者 |
|---|---|---|---|
| `PWR_MODE_00` | `'0'` | `CORE_SET_POWER_MODE_CMD` | `NCI_Core.py` 中 `A10B` (AUTONOMOUS_START_TIMEOUT) 參數解析 |
| `TEST_ID_3F` | `'32'` | `OPTIONAL_CMD` | `OPTIONAL_RSP` |
| `DPC_TYPE` | `'02'` | `OPTIONAL_CMD`（Test ID 0x70） | `OPTIONAL_RSP` |
| `AST_LOOP` | `'00'` | （無任何程式寫入；原始碼已加註解說明） | `READ_OPTION_CMD` / `READ_OPTION_RSP` |

## 總覽

| OID | CMD (`2F`) | RSP (`4F`) | NTF (`6F`) |
|---|---|---|---|
| 0x00 | [`CORE_SET_POWER_MODE_CMD`](#core_set_power_mode_cmd--2f-00) | [`CORE_SET_POWER_MODE_RSP`](#core_set_power_mode_rsp--4f-00) | |
| 0x01 | [`SET_NFC_SERVICE_STATUS_CMD`](#set_nfc_service_status_cmd--2f-01) | [`SET_NFC_SERVICE_STATUS_RSP`](#set_nfc_service_status_rsp--4f-01) | |
| 0x02 | [`NCI_PROPRIETARY_ACT_CMD`](#nci_proprietary_act_cmd--2f-02) | [`NCI_PROPRIETARY_ACT_RSP`](#nci_proprietary_act_rsp--4f-02) | |
| 0x04 | | | [`APDU_LOGGING_NTF`](#apdu_logging_ntf--6f-04) |
| 0x14 | [`RF_GET_TRANSITION_CMD`](#rf_get_transition_cmd--2f-14) | [`RF_GET_TRANSITION_RSP`](#rf_get_transition_rsp--4f-14) | |
| 0x17 | | | [`WTX_NTF`](#wtx_ntf--6f-17) |
| 0x1C | [`LOW_POWER_TAG_REMOVAL_CMD`](#low_power_tag_removal_cmd--2f-1c) | [`LOW_POWER_TAG_REMOVAL_RSP`](#low_power_tag_removal_rsp--4f-1c) | [`LOW_POWER_TAG_REMOVAL_NTF`](#low_power_tag_removal_ntf--6f-1c) |
| 0x1E | [`SYSTEM_ESE_POWER_CYCLE_CMD`](#system_ese_power_cycle_cmd--2f-1e) | [`SYSTEM_ESE_POWER_CYCLE_RSP`](#system_ese_power_cycle_rsp--4f-1e) | |
| 0x1F | [`COLD_RESET_CMD`](#cold_reset_cmd--2f-1f) | [`COLD_RESET_RSP`](#cold_reset_rsp--4f-1f) | [`COLD_RESET_NTF`](#cold_reset_ntf--6f-1f) |
| 0x21 | [`FLUSH_SRAM_AO_TO_FLASH_CMD`](#flush_sram_ao_to_flash_cmd--2f-21) | [`FLUSH_SRAM_AO_TO_FLASH_RSP`](#flush_sram_ao_to_flash_rsp--4f-21) | |
| 0x25 | | | （註解掉，見[未註冊 / 已停用的 handler](#未註冊--已停用的-handler)） |
| 0x30 | [`TEST_PRBS_CMD`](#test_prbs_cmd--2f-30) | [`TEST_PRBS_RSP`](#test_prbs_rsp--4f-30) | |
| 0x32 | [`READ_OPTION_CMD`](#read_option_cmd--2f-32) | [`READ_OPTION_RSP`](#read_option_rsp--4f-32) | |
| 0x33 | [`TEST_PRBS_CARD_CMD`](#test_prbs_card_cmd--2f-33) | [`TEST_PRBS_CARD_RSP`](#test_prbs_card_rsp--4f-33) | |
| 0x35 | | | [`L1_DEBUG_NTF`](#l1_debug_ntf--6f-35) |
| 0x36 | | | [`L2_DEBUG_NTF`](#l2_debug_ntf--6f-36) |
| 0x3D | [`RF_SPC_CMD`](#rf_spc_cmd--2f-3d) | [`RF_SPC_RSP`](#rf_spc_rsp--4f-3d) | [`RF_SPC_NTF`](#rf_spc_ntf--6f-3d) |
| 0x3E | [`TEST_SWP_CMD`](#test_swp_cmd--2f-3e) | [`TEST_SWP_RSP`](#test_swp_rsp--4f-3e) | [`TEST_SWP_NTF`](#test_swp_ntf--6f-3e) |
| 0x3F | [`OPTIONAL_CMD`](#optional_cmd--2f-3f) | [`OPTIONAL_RSP`](#optional_rsp--4f-3f) | |

已註冊：18 個 OID、36 個 handler（CMD 14、RSP 14、NTF 8；OID 1C/1F/3D/3E 三種 MT 皆有）。

> 範例皆以 `NFC_NCI_DECODER(len(raw)//2, raw, 'Nxp', 'None', 2)` 於同一個 Python process 中依序實際執行取得（mode 2：標題行不印 raw）。

---

<a id="core_set_power_mode_cmd"></a><a id="CORE_SET_POWER_MODE_CMD"></a>
## CORE_SET_POWER_MODE_CMD  (`2F 00`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | Proprietary / 0x00 / CMD |
| Handler | [`Proprietary.py:15`](../../nci_decoder/Nxp_pkg/Proprietary.py#L15) `CORE_SET_POWER_MODE_CMD` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Mode | 1 | if/elif：`00` Standby State disabled、`01` Standby State enabled、`02` Autonomous Mode enabled、`03` ULPDET State enabled、`04` Autonomous Mode enabled with Poll、`05` ULPDET enabled with NCI notifications、其他 RFU |

### 範例
- Raw：`2F 00 01 01`
```text
  << CORE_SET_POWER_MODE_CMD >>  
  * Mode: Standby State enabled
#end
```
- Raw：`2F 00 01 05`
```text
  << CORE_SET_POWER_MODE_CMD >>  
  * Mode: ULPDET enabled with NCI notifications
#end
```

### 實作備註
- Mode 值會寫入模組全域 `PWR_MODE_00`，`NCI_Core.py` 解析參數 `A10B` (AUTONOMOUS_START_TIMEOUT) 時用它判斷 Autonomous Mode 是否啟用（值為 `02` / `04` 時視為啟用）。

<a id="core_set_power_mode_rsp"></a><a id="CORE_SET_POWER_MODE_RSP"></a>
## CORE_SET_POWER_MODE_RSP  (`4F 00`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | Proprietary / 0x00 / RSP |
| Handler | [`Proprietary.py:46`](../../nci_decoder/Nxp_pkg/Proprietary.py#L46) `CORE_SET_POWER_MODE_RSP` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |

### 範例
- Raw：`4F 00 01 00`
```text
  << CORE_SET_POWER_MODE_RSP >>  
  * Status: STATUS_OK
#end
```

<a id="set_nfc_service_status_cmd"></a><a id="SET_NFC_SERVICE_STATUS_CMD"></a>
## SET_NFC_SERVICE_STATUS_CMD  (`2F 01`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | Proprietary / 0x01 / CMD |
| Handler | [`Proprietary.py:60`](../../nci_decoder/Nxp_pkg/Proprietary.py#L60) `SET_NFC_SERVICE_STATUS_CMD` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Mode | 1 | `00` NFC service OFF、`01` NFC service ON、其他 RFU |

### 範例
- Raw：`2F 01 01 01`
```text
  << SET_NFC_SERVICE_STATUS_CMD >>  
  * Mode: NFC service ON
#end
```

<a id="set_nfc_service_status_rsp"></a><a id="SET_NFC_SERVICE_STATUS_RSP"></a>
## SET_NFC_SERVICE_STATUS_RSP  (`4F 01`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | Proprietary / 0x01 / RSP |
| Handler | [`Proprietary.py:79`](../../nci_decoder/Nxp_pkg/Proprietary.py#L79) `SET_NFC_SERVICE_STATUS_RSP` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |

### 範例
- Raw：`4F 01 01 00`
```text
  << SET_NFC_SERVICE_STATUS_RSP >>  
  * Status: STATUS_OK
#end
```

<a id="nci_proprietary_act_cmd"></a><a id="NCI_PROPRIETARY_ACT_CMD"></a>
## NCI_PROPRIETARY_ACT_CMD  (`2F 02`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | Proprietary / 0x02 / CMD |
| Handler | [`Proprietary.py:93`](../../nci_decoder/Nxp_pkg/Proprietary.py#L93) `NCI_PROPRIETARY_ACT_CMD` |

### Payload 格式
無 payload（印出置中的 `(Empty)`）。

### 範例
- Raw：`2F 02 00`
```text
  << NCI_PROPRIETARY_ACT_CMD >>  
         (Empty)         
#end
```

<a id="nci_proprietary_act_rsp"></a><a id="NCI_PROPRIETARY_ACT_RSP"></a>
## NCI_PROPRIETARY_ACT_RSP  (`4F 02`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | Proprietary / 0x02 / RSP |
| Handler | [`Proprietary.py:106`](../../nci_decoder/Nxp_pkg/Proprietary.py#L106) `NCI_PROPRIETARY_ACT_RSP` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | 僅 `00`/`03` 查 `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)），其他值印 `Forbidden` |
| 2 | FW_Build_Nb | 4 | 原樣印出 hex 字串（未轉換位元組序） |

### 範例
- Raw：`4F 02 05 00 12 34 56 78`
```text
  << NCI_PROPRIETARY_ACT_RSP >>  
  * Status: STATUS_OK
  * FW_Build_Nb: 12345678
#end
```
- Raw：`4F 02 05 01 12 34 56 78`
```text
  << NCI_PROPRIETARY_ACT_RSP >>  
  * Status: Forbidden
  * FW_Build_Nb: 12345678
#end
```

<a id="apdu_logging_ntf"></a><a id="APDU_LOGGING_NTF"></a>
## APDU_LOGGING_NTF  (`6F 04`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | Proprietary / 0x04 / NTF |
| Handler | [`Proprietary.py:127`](../../nci_decoder/Nxp_pkg/Proprietary.py#L127) `APDU_LOGGING_NTF` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Logging Opcode | 1 | 應為 `60`；不是時附註 `(Should be 0x60)` |
| 2 | RFU Length | 1 | 跳過不印（Do not Care） |
| 3 | Timestamp | 2 | 以 big-endian 讀成整數 step，`step × 16 µs / 1000` 印成 ms（最大 1024 ms） |
| 4 | Category | 1 | `0B` C-APDU from eSE、`1B` R-APDU from eSE、`2B` C-APDU from UICCx、`3B` R-APDU from UICCx、其他印 `Error <值>` |
| 5 | APDU Data | 5、2 或剩餘全部 | Category 為 `0B`/`2B`（C-APDU）：5 octets，C-APDU 前 5 bytes；`1B`/`3B`（R-APDU）：2 octets，R-APDU 最後 2 bytes；其他 Category：剩餘所有 bytes 原樣印出 |

### 範例
- Raw：`6F 04 0A 60 00 00 64 0B 00 A4 04 00 07`
```text
  << APDU_LOGGING_NTF >>  
  * Logging Opcode: 60
  * Timestamp: 1.6 ms
  * Category: C-APDU from eSE
  * APDU Data: 00A4040007 (First 5 bytes of the C-APDU)
#end
```
- Raw：`6F 04 07 60 00 01 00 1B 90 00`
```text
  << APDU_LOGGING_NTF >>  
  * Logging Opcode: 60
  * Timestamp: 4.096 ms
  * Category: R-APDU from eSE
  * APDU Data: 9000 (Last 2 bytes of the R-APDU)
#end
```

### 實作備註
- ✅ 已修正（2026-10）：Category 不在 4 個已知值時，把剩餘 bytes 全部印為 `* APDU Data: <hex>`，不再觸發 `Payload error!!`。

<a id="rf_get_transition_cmd"></a><a id="RF_GET_TRANSITION_CMD"></a>
## RF_GET_TRANSITION_CMD  (`2F 14`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | Proprietary / 0x14 / CMD |
| Handler | [`Proprietary.py:185`](../../nci_decoder/Nxp_pkg/Proprietary.py#L185) `RF_GET_TRANSITION_CMD` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | RF Transition ID | 1 | `tbl_rf_trans_id`（見 [Tables](Tables.md#tbl_rf_trans_id)），後附原始 hex |
| 2 | CLIF Register Offset | 1 | 原樣印出 hex |

### 範例
- Raw：`2F 14 02 22 10`
```text
  << RF_GET_TRANSITION_CMD >>  
  * RF Transition ID: RF_RM_TX_A106 (22)
  * CLIF Register Offset: 10
#end
```

<a id="rf_get_transition_rsp"></a><a id="RF_GET_TRANSITION_RSP"></a>
## RF_GET_TRANSITION_RSP  (`4F 14`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | Proprietary / 0x14 / RSP |
| Handler | [`Proprietary.py:204`](../../nci_decoder/Nxp_pkg/Proprietary.py#L204) `RF_GET_TRANSITION_RSP` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | 僅 `00`/`01`/`06` 查 `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)），其他值印 `Forbidden` |
| 2 | RF Transition Length | 1 | 轉十進位印出（L） |
| 3 | RF Transition Value | L（1、2 或 4） | Little Endian：印 `0x<反轉後 hex> (raw <原始 hex>)`（例：`34 12` → `0x1234 (raw 3412)`） |

### 範例
- Raw：`4F 14 04 00 02 34 12`
```text
  << RF_GET_TRANSITION_RSP >>  
  * Status: STATUS_OK
  * RF Transition Len: 2
  * RF Transition Val: 0x1234 (raw 3412)
#end
```

### 實作備註
- ✅ 已修正（2026-10）：Value 依 Little Endian 反轉後印 `0x<LE>`，並保留 `(raw ..)` 原始 hex。

<a id="wtx_ntf"></a><a id="WTX_NTF"></a>
## WTX_NTF  (`6F 17`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | Proprietary / 0x17 / NTF |
| Handler | [`Proprietary.py:231`](../../nci_decoder/Nxp_pkg/Proprietary.py#L231) `WTX_NTF` |

### Payload 格式
無 payload（表示 RF 通訊處於長時間 WTX(RTOX) REQ/RESP 交換）。

### 範例
- Raw：`6F 17 00`
```text
  << WTX_NTF >>  
         (Empty)         
#end
```

<a id="low_power_tag_removal_cmd"></a><a id="LOW_POWER_TAG_REMOVAL_CMD"></a>
## LOW_POWER_TAG_REMOVAL_CMD  (`2F 1C`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | Proprietary / 0x1C / CMD |
| Handler | [`Proprietary.py:245`](../../nci_decoder/Nxp_pkg/Proprietary.py#L245) `LOW_POWER_TAG_REMOVAL_CMD` |

### Payload 格式
無 payload（啟動 low power tag removal detection）。

### 範例
- Raw：`2F 1C 00`
```text
  << LOW_POWER_TAG_REMOVAL_CMD >>  
         (Empty)         
#end
```

<a id="low_power_tag_removal_rsp"></a><a id="LOW_POWER_TAG_REMOVAL_RSP"></a>
## LOW_POWER_TAG_REMOVAL_RSP  (`4F 1C`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | Proprietary / 0x1C / RSP |
| Handler | [`Proprietary.py:258`](../../nci_decoder/Nxp_pkg/Proprietary.py#L258) `LOW_POWER_TAG_REMOVAL_RSP` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | 僅 `00`/`01`/`09` 查 `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)），其他值印 `Forbidden` |

### 範例
- Raw：`4F 1C 01 00`
```text
  << LOW_POWER_TAG_REMOVAL_RSP >>  
  * Status: STATUS_OK
#end
```

### 實作備註
- docstring 文字（「The NFCC reset the eSE ...」）是從 SYSTEM_ESE_POWER_CYCLE_RSP 複製過來的，與本命令語意不符。
- ✅ 已修正（2026-10）：對應的 `LOW_POWER_TAG_REMOVAL_NTF`（`6F 1C`）已註冊，見 [LOW_POWER_TAG_REMOVAL_NTF](#low_power_tag_removal_ntf--6f-1c)。

<a id="low_power_tag_removal_ntf"></a><a id="LOW_POWER_TAG_REMOVAL_NTF"></a>
## LOW_POWER_TAG_REMOVAL_NTF  (`6F 1C`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | Proprietary / 0x1C / NTF |
| Handler | [`Proprietary.py:276`](../../nci_decoder/Nxp_pkg/Proprietary.py#L276) `LOW_POWER_TAG_REMOVAL_NTF` |

### Payload 格式
無 payload（通知 host 先前偵測到的 target 已離開 NFCC 感應範圍）。印 `(Empty)`，回傳 0。

### 範例
- Raw：`6F 1C 00`
```text
  << LOW_POWER_TAG_REMOVAL_NTF >>  
         (Empty)         
#end
```

### 實作備註
- ✅ 已修正（2026-10）：已在 `__ctrl__.py` 的 OID `1C` 註冊為 NTF handler，`6F 1C 00` 不再 `ERROR_NOT_FOUND`。

<a id="system_ese_power_cycle_cmd"></a><a id="SYSTEM_ESE_POWER_CYCLE_CMD"></a>
## SYSTEM_ESE_POWER_CYCLE_CMD  (`2F 1E`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | Proprietary / 0x1E / CMD |
| Handler | [`Proprietary.py:290`](../../nci_decoder/Nxp_pkg/Proprietary.py#L290) `SYSTEM_ESE_POWER_CYCLE_CMD` |

### Payload 格式
無 payload（要求重置 eSE）。

### 範例
- Raw：`2F 1E 00`
```text
  << SYSTEM_ESE_POWER_CYCLE_CMD >>  
         (Empty)         
#end
```

<a id="system_ese_power_cycle_rsp"></a><a id="SYSTEM_ESE_POWER_CYCLE_RSP"></a>
## SYSTEM_ESE_POWER_CYCLE_RSP  (`4F 1E`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | Proprietary / 0x1E / RSP |
| Handler | [`Proprietary.py:303`](../../nci_decoder/Nxp_pkg/Proprietary.py#L303) `SYSTEM_ESE_POWER_CYCLE_RSP` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | 僅 `00`/`01`/`09` 查 `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)），其他值印 `Forbidden` |

### 範例
- Raw：`4F 1E 01 00`
```text
  << SYSTEM_ESE_POWER_CYCLE_RSP >>  
  * Status: STATUS_OK
#end
```

<a id="cold_reset_cmd"></a><a id="COLD_RESET_CMD"></a>
## COLD_RESET_CMD  (`2F 1F`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | Proprietary / 0x1F / CMD |
| Handler | [`Proprietary.py:321`](../../nci_decoder/Nxp_pkg/Proprietary.py#L321) `COLD_RESET_CMD` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | RESET by pin | 1 | `"SE reset " + lookup(tbl_general_status_n, 值)`（見 [Tables](Tables.md#tbl_general_status_n)；`00` Enabled、`01` Disabled、其他 RFU） |

### 範例
- Raw：`2F 1F 01 00`
```text
  << COLD_RESET_CMD >>  
  * RESET by pin: SE reset Enabled 
#end
```

### 實作備註
- ✅ 已修正（2026-10）：改用 `lookup(NFC_table.tbl_general_status_n, rst_pin)` 查表，不再丟 `TypeError`，正常印出 `SE reset Enabled/Disabled`。

<a id="cold_reset_rsp"></a><a id="COLD_RESET_RSP"></a>
## COLD_RESET_RSP  (`4F 1F`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | Proprietary / 0x1F / RSP |
| Handler | [`Proprietary.py:335`](../../nci_decoder/Nxp_pkg/Proprietary.py#L335) `COLD_RESET_RSP` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |

### 範例
- Raw：`4F 1F 01 00`
```text
  << COLD_RESET_RSP >>  
  * Status: STATUS_OK
#end
```

<a id="cold_reset_ntf"></a><a id="COLD_RESET_NTF"></a>
## COLD_RESET_NTF  (`6F 1F`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | Proprietary / 0x1F / NTF |
| Handler | [`Proprietary.py:349`](../../nci_decoder/Nxp_pkg/Proprietary.py#L349) `COLD_RESET_NTF` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `00` successfully done；其他任何值 at least one internal verification failed |

### 範例
- Raw：`6F 1F 01 00`
```text
  << COLD_RESET_NTF >>  
  * Status: successfully done
#end
```
- Raw：`6F 1F 01 01`
```text
  << COLD_RESET_NTF >>  
  * Status: at least one internal verification failed
#end
```

<a id="flush_sram_ao_to_flash_cmd"></a><a id="FLUSH_SRAM_AO_TO_FLASH_CMD"></a>
## FLUSH_SRAM_AO_TO_FLASH_CMD  (`2F 21`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | Proprietary / 0x21 / CMD |
| Handler | [`Proprietary.py:366`](../../nci_decoder/Nxp_pkg/Proprietary.py#L366) `FLUSH_SRAM_AO_TO_FLASH_CMD` |

### Payload 格式
無 payload（將 SRAM Always ON 內容存到 FLASH）。

### 範例
- Raw：`2F 21 00`
```text
  << FLUSH_SRAM_AO_TO_FLASH_CMD >>  
         (Empty)         
#end
```

<a id="flush_sram_ao_to_flash_rsp"></a><a id="FLUSH_SRAM_AO_TO_FLASH_RSP"></a>
## FLUSH_SRAM_AO_TO_FLASH_RSP  (`4F 21`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | Proprietary / 0x21 / RSP |
| Handler | [`Proprietary.py:379`](../../nci_decoder/Nxp_pkg/Proprietary.py#L379) `FLUSH_SRAM_AO_TO_FLASH_RSP` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | 僅 `00`/`01`/`09`/`06` 查 `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)），其他值印 `Forbidden` |

### 範例
- Raw：`4F 21 01 00`
```text
  << FLUSH_SRAM_AO_TO_FLASH_RSP >>  
  * Status: STATUS_OK
#end
```

<a id="test_prbs_cmd"></a><a id="TEST_PRBS_CMD"></a>
## TEST_PRBS_CMD  (`2F 30`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | Proprietary / 0x30 / CMD |
| Handler | [`Proprietary.py:397`](../../nci_decoder/Nxp_pkg/Proprietary.py#L397) `TEST_PRBS_CMD` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | PRBS Mode | 1 | `00` / `01` 皆印 Firmware generated PRBS；其他 RFU |
| 2 | PRBS type | 1 | `00` PRBS9 when Hardware generated PRBS selected、`01` PRBS15 when Hardware generated PRBS selected、其他 Ignored when Firmware generated PRBS is selected |
| 3 | Technology to stream | 1 | `00` Type A、`01` Type B、`02` Type F、`03` Type V、其他 RFU |
| 4 | Bitrate | 1 | `00`~`03` 查 `tbl_bit_rates`（見 [Tables](Tables.md#tbl_bit_rates)）；`04` 印 26 Kbit/s；其他 RFU |
| 5 | PRBS series length | 2 | 原樣印出 hex |

### 範例
- Raw：`2F 30 06 00 00 00 00 01 00`
```text
  << TEST_PRBS_CMD >>  
  * PRBS Mode: Firmware generated PRBS
  * PRBS Type: PRBS9 when Hardware generated PRBS selected
  * Technology to stream: Type A
  * Bitrate: 106 Kbit/s
  * PRBS series length: 0100
#end
```

### 實作備註
- ✅ 已修正（2026-10）：函式結尾補上 `return p_payload`，正常 6-octet payload 解析完畢並印 `#end`。
- PRBS Mode `00` 與 `01` 印出相同字串 "Firmware generated PRBS"（`01` 應是 Hardware generated PRBS 才合理，但程式如此）。
- Bitrate `04` 在 `tbl_bit_rates` 中是 1695 Kbit/s，程式特別改印 26 Kbit/s（不查表）。

<a id="test_prbs_rsp"></a><a id="TEST_PRBS_RSP"></a>
## TEST_PRBS_RSP  (`4F 30`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | Proprietary / 0x30 / RSP |
| Handler | [`Proprietary.py:456`](../../nci_decoder/Nxp_pkg/Proprietary.py#L456) `TEST_PRBS_RSP` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | 僅 `00`/`05`/`06`/`09` 查 `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)），其他值印 `RFU` |

### 範例
- Raw：`4F 30 01 00`
```text
  << TEST_PRBS_RSP >>  
  * Status: STATUS_OK
#end
```

<a id="read_option_cmd"></a><a id="READ_OPTION_CMD"></a>
## READ_OPTION_CMD  (`2F 32`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | Proprietary / 0x32 / CMD |
| Handler | [`Proprietary.py:473`](../../nci_decoder/Nxp_pkg/Proprietary.py#L473) `READ_OPTION_CMD` |

此 OID 原本有三個替代 handler（見[未註冊 / 已停用的 handler](#未註冊--已停用的-handler)），現合併為 `READ_OPTION_CMD`，**由模組全域 `AST_LOOP` 決定 sub-command**（不是由 payload 內容決定），並額外印出一行 `<< 子命令名 >>`。

### Payload 格式（依 `AST_LOOP`）

**`AST_LOOP == '00'` → RF_TEST_API_CMD（預設，也是目前唯一可達的分支）**

| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | HW Regi | 1 | local `tbl_hw_regi`：`08` GPADC_SENSOR_TXLDO_CURRENT、`0C` GPADC_SENSOR_RSSI、`0D` GPADC_SENSOR_VDDPA、其他 RFU |

**`AST_LOOP == '01'` → READ_TXLDO_CURRENT_CMD**

| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Test ID | 1 | 固定印 "Read TxLdo current"（docstring：應為 `0x08`，未檢查） |
| 2 | Wait_Time | 1 | 十進位，單位 µs |

**`AST_LOOP == '02'` → READ_RSSI_CMD**

| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Test ID | 1 | 固定印 "Read RSSI Command"（docstring：應為 `0x20`，未檢查） |
| 2 | Wait_Time | 1 | 十進位，單位 µs |

### 範例
- Raw：`2F 32 01 0C`（`AST_LOOP = '00'`）
```text
  << READ_OPTION_CMD >>  
  << RF_TEST_API_CMD >>  
  * HW Regi: GPADC_SENSOR_RSSI
#end
```
（`AST_LOOP = '01'` / `'02'` 的範例見[未註冊 / 已停用的 handler](#未註冊--已停用的-handler)。）

### 實作備註
- （仍未解決）`AST_LOOP` 在 `Proprietary.py` 中初始化為 `'00'`，repo 內沒有任何程式修改它，因此實際執行時只會走 RF_TEST_API 分支；READ_TXLDO_CURRENT / READ_RSSI 分支僅能靠手動修改原始碼常數啟用。2026-10 起已在原始碼（`AST_LOOP` 宣告處與 `READ_OPTION_CMD/RSP` 內）加註解說明此限制，切換條件需參考 NXP UM 才能決定。

<a id="read_option_rsp"></a><a id="READ_OPTION_RSP"></a>
## READ_OPTION_RSP  (`4F 32`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | Proprietary / 0x32 / RSP |
| Handler | [`Proprietary.py:508`](../../nci_decoder/Nxp_pkg/Proprietary.py#L508) `READ_OPTION_RSP` |

### Payload 格式（依 `AST_LOOP`）

**`AST_LOOP == '00'` → RF_TEST_API_RSP**

| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |
| 2 | HW Regi Val | 2 | 原樣印出 hex |

**`AST_LOOP == '01'` → READ_TXLDO_CURRENT_RSP**

| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |
| 2 | TXLDO_CURRENT | 2 | little-endian：`byte0 + byte1 × 256`，單位 mA（見實作備註） |

**`AST_LOOP == '02'` → READ_RSSI_RSP**

| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |
| 2 | （未命名） | 2 | 直接跳過，不印（docstring 未列此欄位） |
| 3 | RSSI_VALUE | 4 | 原樣印出 hex |
| 4 | Interpolated RSSI | 4 | 原樣印出 hex |

### 範例
- Raw：`4F 32 03 00 34 12`（`AST_LOOP = '00'`）
```text
  << READ_OPTION_RSP >>  
  << RF_TEST_API_RSP >>  
  * Status: STATUS_OK
  * HW Regi Val: 3412
#end
```

### 實作備註
- ✅ 已修正（2026-10）：READ_TXLDO_CURRENT 分支改以 `int(x, 16)` 解析（`34 12` → 4660 mA）；但此分支目前仍不可達（見下一條）。
- 同 CMD，只有 `AST_LOOP == '00'` 分支實際可達。

<a id="test_prbs_card_cmd"></a><a id="TEST_PRBS_CARD_CMD"></a>
## TEST_PRBS_CARD_CMD  (`2F 33`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | Proprietary / 0x33 / CMD |
| Handler | [`Proprietary.py:551`](../../nci_decoder/Nxp_pkg/Proprietary.py#L551) `TEST_PRBS_CARD_CMD` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | PRBS Mode | 1 | local `tbl_prbs_mode`：`00` Start PRBS Card Mode、`01` Stop PRBS Card Mode、其他 RFU |
| 2 | Test Type | 1 | 僅 PRBS Mode = `00` 時存在；bit field（見下） |
| 3 | Pseudo random pattern | 1 | 僅當 Clk-less platform bit = 1 時存在；原樣印 hex |
| 4 | Fixed Pattern | 16 | 僅當 Sys clk platform bit = 1 時存在；每 byte 印成 `0xNN` 以空白分隔 |

Test Type bit field（b7 為 MSB）：

| Bits | 欄位 | 解析 |
|---|---|---|
| b7–b6 | 未使用 | — |
| b5 | Sys clk platform | `tbl_general_status`（見 [Tables](Tables.md#tbl_general_status)；0 Disabled / 1 Enabled） |
| b4 | Clk-less platform | `tbl_general_status`（同上） |
| b3–b2 | Technology | local `tbl_tech`：`00` Type A、`01` Type B、`10` Type F（`11` 無對應，印 `None`） |
| b1–b0 | Bit Rate | local `tbl_bitrate`：`00` 106k、`01` 212k、`10` 424k、`11` 848k |

### 範例
- Raw：`2F 33 03 00 10 AA`（Clk-less mode）
```text
  << TEST_PRBS_CARD_CMD >>  
  * PRBS Mode: Start PRBS Card Mode
  * Test Type: 00010000 (10)
   ~ Sys clk platform:    Disabled
   ~ Clk-less platform:   Enabled 
   ~ Technology:          Type A
   ~ Bit Rate:            106k
  * Pseudo random pattern: AA
#end
```
- Raw：`2F 33 12 00 20 00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF`（Sys clk mode）
```text
  << TEST_PRBS_CARD_CMD >>  
  * PRBS Mode: Start PRBS Card Mode
  * Test Type: 00100000 (20)
   ~ Sys clk platform:    Enabled 
   ~ Clk-less platform:   Disabled
   ~ Technology:          Type A
   ~ Bit Rate:            106k
  Fixed Pattern: 0x00 0x11 0x22 0x33 0x44 0x55 0x66 0x77 0x88 0x99 0xAA 0xBB 0xCC 0xDD 0xEE 0xFF
#end
```
- Raw：`2F 33 01 01`（Stop）
```text
  << TEST_PRBS_CARD_CMD >>  
  * PRBS Mode: Stop PRBS Card Mode
#end
```

### 實作備註
- 是否讀取後續欄位靠比對字串 `'Enabled '`（結尾含空白，與 `tbl_general_status['01']` 一致）。
- 兩個 bit 同時為 1 時，先讀 Pseudo random pattern（1 byte）再讀 Fixed Pattern（16 bytes）。
- `Fixed Pattern` 行沒有 `*` 前綴，與其他欄位格式不一致。

<a id="test_prbs_card_rsp"></a><a id="TEST_PRBS_CARD_RSP"></a>
## TEST_PRBS_CARD_RSP  (`4F 33`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | Proprietary / 0x33 / RSP |
| Handler | [`Proprietary.py:594`](../../nci_decoder/Nxp_pkg/Proprietary.py#L594) `TEST_PRBS_CARD_RSP` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |

### 範例
- Raw：`4F 33 01 00`
```text
  << TEST_PRBS_CARD_RSP >>  
  * Status: STATUS_OK
#end
```

<a id="l1_debug_ntf"></a><a id="L1_DEBUG_NTF"></a>
## L1_DEBUG_NTF  (`6F 35`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | Proprietary / 0x35 / NTF |
| Handler | [`Proprietary.py:609`](../../nci_decoder/Nxp_pkg/Proprietary.py#L609) `L1_DEBUG_NTF` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Major_Time_Stamp | 2 | little-endian，單位 ms |
| 2 | Minor_Time_Stamp | 2 | little-endian，單位 µs；與上欄合印為 `Time: <ms> ms <µs> µs` |
| 3 | RSSI 或 DLMA | 2 或 4 | 依剩餘 **byte** 數判斷：剩 3/4 bytes → non-TX event，RSSI 2 octets（印 `(MSB)`）；剩 5/6 bytes → TX event，DLMA 4 octets（印 `(LSB)`）；皆原樣印 hex |
| 4 | CLIF State | 1 | 高 nibble = Tech & Mode，低 nibble = Trigger Type（見下） |
| 5 | Extra Debug data | 1（選用；剩餘 4 或 6 bytes 時存在） | 原樣印 hex |

CLIF State 高 nibble（local `tbl_tech_mode`）：`0` Not detected yet、`1` Card Emulation NFC-A、`2` Card Emulation NFC-B、`3` Card Emulation NFC-F、`8` Reader mode NFC-A、`9` Reader mode NFC-B、`A` Reader mode NFC-F、`F` Reader mode NFC-V。

CLIF State 低 nibble（Trigger Type，高 nibble 為 `0`/`3` 時不印）：

| 高 nibble | 使用表 | 內容 |
|---|---|---|
| `1`/`2`/`8`/`9` | `tbl_TTC_1` | `1` ACTIVATED、`2` DATA_RX、`3` RX_DESELECT、`4` RX_WTX、`5` ERROR、`6` RX_ACK、`7` RX_NAK、`8` DATA_TX、`A` TX_DESELECT、`B` TX_WTX、`C` TX_ACK、`D` TX_NAK、`E` EXTENDED |
| `A` | `tbl_TTC_2` | `1` ACTIVATED、`2` DATA_RX、`3` RX_READ、`4` RX_WRITE、`5` ERROR、`6` DATA_TX、`7` TX_READ、`8` TX_WRITE |
| `F` | `tbl_TTC_3` | `2` DATA_RX、`8` DATA_TX |

### 範例
- Raw：`6F 35 07 10 00 20 00 01 23 12`（RSSI + CLIF State，7 octets）
```text
  << L1_DEBUG_NTF >>  
  * Time: 16 ms 32 µs
  * RSSI: 0123 (MSB)
  * CLIF State: 12
    * Tech & Mode: Card Emulation NFC-A
    * Trigger Type: DATA_RX
#end
```
- Raw：`6F 35 0A 10 00 20 00 01 02 03 04 82 05`（DLMA + CLIF State + Extra，10 octets）
```text
  << L1_DEBUG_NTF >>  
  * Time: 16 ms 32 µs
  * DLMA: 01020304 (LSB)
  * CLIF State: 82
    * Tech & Mode: Reader mode NFC-A
    * Trigger Type: DATA_RX
  * Extra Debug data: 05
#end
```

### 實作備註
- ✅ 已修正（2026-10）：分支判斷改用剩餘 **byte** 數（`len(raw[p_payload:]) // 2`），RSSI / DLMA / Extra 依 3/4/5/6 bytes 正確選擇，符合 docstring 的封包可完整解出。

<a id="l2_debug_ntf"></a><a id="L2_DEBUG_NTF"></a>
## L2_DEBUG_NTF  (`6F 36`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | Proprietary / 0x36 / NTF |
| Handler | [`Proprietary.py:697`](../../nci_decoder/Nxp_pkg/Proprietary.py#L697) `L2_DEBUG_NTF` |

### Payload 格式
共同前段：

| # | 欄位 | 長度 | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Tag | 4 bits（第 1 byte 高 nibble） | local `tbl_tag`：`1` L2 EVENT、`2` FELICA CMD、`3` FELICA SYSTEM CODE、`4` FELICA RSP、`5` MISC、`A` CMA、其他 RFU |
| 2 | Length | 4 bits（第 1 byte 低 nibble） | 十進位整數 L，不印，用於判斷選用欄位 |
| 3 | Major_Time_Stamp | 2 octets | little-endian，ms |
| 4 | Minor_Time_Stamp | 2 octets | little-endian，µs |

之後依 Tag 分支：

**Tag `1` – L2 EVENT**

| # | 欄位 | 長度 (Octets) | 解析方式 |
|---|---|---|---|
| 5 | RSSI / DLMA | 2 或 4 | L = 7/8：RSSI 2 octets（`(MSB)`）；L = 9/10：DLMA 4 octets（`(LSB)`） |
| 6 | CLIF State | 1 | 高 nibble：local `tbl_tech_mode`（`1` CE NFC-A、`2` CE NFC-B、`3` CE NFC-F、`8` Reader NFC-A、`9` Reader NFC-B、`A` Reader NFC-F、`F` Reader NFC-V）；低 nibble Trigger Type 見下 |
| 7 | Extra data info | 1（L = 8 或 10 時） | 原樣 hex |

Trigger Type（高 nibble 為 `0`/`3` 時不印）：
- 高 nibble `1`/`2`/`8`/`9`/`A` → `tbl_TTC_1`：`1` MODULATION_DETECTED、`2` DATA_RX、`3` TIMEOUT/RSSI、`4` ACTIVE_ISO14443_3、`5` ERROR、`6` SENSING、`7` ACTIVE_ISO14443_4、`8` RF_ON、`9` RF_OFF、`A` DATA_TX、`C` LPCD_WUP
- 高 nibble `F` → `tbl_TTC_2`：`1` SLPV_REQ、`2` INVENTORY_RESP、`6` INVENTORY_REQ_1_SLOT、`7` ACTIVATION、`A` INVENTORY_REQ_16_SLOT

**Tag `2` – FELICA CMD**

| # | 欄位 | 長度 (Octets) | 解析方式 |
|---|---|---|---|
| 5 | RSSI | 2 | 原樣 hex `(MSB)` |
| 6 | FeliCa CMD | 1 | 原樣 hex |
| 7 | Extra data info | 1（L = 8 時） | 原樣 hex |

**Tag `3` – FELICA SYSTEM CODE**

| # | 欄位 | 長度 (Octets) | 解析方式 |
|---|---|---|---|
| 5 | FeliCa CMD（System Code） | 2 | 原樣 hex（標籤印成 "FeliCa CMD"） |

**Tag `4` – FELICA RSP**

| # | 欄位 | 長度 (Octets) | 解析方式 |
|---|---|---|---|
| 5 | DLMA | 4 | 原樣 hex `(LSB)` |
| 6 | FeliCa RSP | 1 | 原樣 hex |
| 7 | RSP status flag | 2 | 原樣 hex |
| 8 | Extra data info | 1（L = 12 時） | 原樣 hex |

**Tag `5` – MISC**

| # | 欄位 | 長度 (Octets) | 解析方式 |
|---|---|---|---|
| 5 | Misc Event trig | 1 | local `tbl_misc_event`：`01` GENERIC ERROR、`02` FELICA CM: EMPTY FRAME FROM ESE、`03` L2 NTF BUFFER OVERFLOW、`05` FELICA CM: RF ERROR、其他 RFU |
| 6 | Extra data info | 1（L = 6 時） | 原樣 hex |

**Tag `A` – CMA**

| # | 欄位 | 長度 (Octets) | 解析方式 |
|---|---|---|---|
| 5 | Trig type | 1 | local `tbl_TT_cma`：`03` CLT_CMD、`04` CLT_DATA_RX、`05` CLT_DATA_TX、`06` RATS_RECEIVED、`07` ATQA_SENT、`08` UID_SENT、`0A` ATS_SENT、`0B` HLTA_DETECTED、`0C` ERROR、`0D` EMD_DETECTED、其他 RFU |
| 6 | Extra data info | 其餘（L > 5 時） | 先把剩餘全部原樣印出，再依 Trig type 細分： |

CMA Extra data 細分：

| Trig type | 子欄位 |
|---|---|
| `03` CLT_CMD | 1 octet：`08` → CLT_IDLE、`09` → CLT_HALT |
| `04` CLT_DATA_RX | 1 octet 長度 n + n octets CLT RX Data（n 只受剩餘資料長度限制） |
| `05` CLT_DATA_TX | 1 octet 長度 n + n octets CLT TX Data（n 只受剩餘資料長度限制） |
| `06` RATS_RECEIVED | 2 octets RATS |
| `07` ATQA_SENT | 1 octet 類型（`26` REQA、`52` WUPA）+ 2 octets ATQA |
| `08` UID_SENT | 1 octet Anti-Collision Lv |
| `0A` ATS_SENT | 4 octets APC + 5 octets ATS |
| `0B` HLTA_DETECTED | 2 octets HLTA |
| `0C` ERROR | 2 octets 長度 n（little-endian）+ n octets Data received（n 只受剩餘資料長度限制） |
| `0D` 及其他 | 只印 Extra data info，不消耗 offset |

### 範例
- Raw：`6F 36 08 17 10 00 20 00 01 23 12`（L2 EVENT，RSSI）
```text
  << L2_DEBUG_NTF >>  
  * Tag: L2 EVENT
  * Time: 16 ms 32 µs
  * RSSI: 0123 (MSB)
  * CLIF State: 12
    * Tech & Mode: Card Emulation NFC-A
    * Trigger Type: DATA_RX
#end
```
- Raw：`6F 36 08 27 10 00 20 00 01 23 06`（FELICA CMD）
```text
  << L2_DEBUG_NTF >>  
  * Tag: FELICA CMD
  * Time: 16 ms 32 µs
  * RSSI: 0123 (MSB)
  * FeliCa CMD: 06
#end
```
- Raw：`6F 36 07 35 10 00 20 00 12 34`（FELICA SYSTEM CODE）
```text
  << L2_DEBUG_NTF >>  
  * Tag: FELICA SYSTEM CODE
  * Time: 16 ms 32 µs
  * FeliCa CMD: 1234
#end
```
- Raw：`6F 36 0D 4C 10 00 20 00 01 02 03 04 07 00 00 05`（FELICA RSP + Extra）
```text
  << L2_DEBUG_NTF >>  
  * Tag: FELICA RSP
  * Time: 16 ms 32 µs
  * DLMA: 01020304 (LSB)
  * FeliCa RSP: 07
  * RSP status flag: 0000
  * Extra data info: 05
#end
```
- Raw：`6F 36 06 55 10 00 20 00 01`（MISC）
```text
  << L2_DEBUG_NTF >>  
  * Tag: MISC
  * Time: 16 ms 32 µs
  * Misc Event trig: GENERIC ERROR
#end
```
- Raw：`6F 36 09 A8 10 00 20 00 07 26 04 00`（CMA ATQA_SENT）
```text
  << L2_DEBUG_NTF >>  
  * Tag: CMA
  * Time: 16 ms 32 µs
  * Trig type: ATQA_SENT
  * Extra data info: 260400
    * Type: REQA (26)
    * ATQA sent: 0400
#end
```
- Raw：`6F 36 07 A6 10 00 20 00 03 08`（CMA CLT_CMD）
```text
  << L2_DEBUG_NTF >>  
  * Tag: CMA
  * Time: 16 ms 32 µs
  * Trig type: CLT_CMD
  * Extra data info: 08
    * Type: CLT_IDLE (08)
#end
```

### 實作備註
- 一個 NTF 只解析一筆 TLV 記錄；Length nibble 只用來判斷選用欄位，不與實際 payload 長度比對。
- Tag `1` 時若 L 不是 7/8/9/10，RSSI/DLMA 都不讀，CLIF State 會讀錯位置。
- Tag `1` 的 `tbl_tech_mode` 沒有 `0`（不同於 L1）；Tag `3` 讀到的是 System Code，但印出標籤為 "FeliCa CMD"。
- ✅ 已修正（2026-10）：CMA 的 RX/TX/ERROR 資料長度不再截為 9 / 9 / 8 bytes，改以宣告長度讀取（最多到剩餘資料結尾）。

<a id="rf_spc_cmd"></a><a id="RF_SPC_CMD"></a>
## RF_SPC_CMD  (`2F 3D`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | Proprietary / 0x3D / CMD |
| Handler | [`Proprietary.py:924`](../../nci_decoder/Nxp_pkg/Proprietary.py#L924) `RF_SPC_CMD` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | SPC Config | 1 | local `tbl_spc_cfg`：`30` Configure NFCC for SPC、`31` Start SPC algorithm、其他 RFU |
| 2 | Block Nb | 1 | 僅 SPC Config = `30` 時存在；原樣 hex |
| 3 | Algo settings / PLL settings | 其餘全部 | 僅 SPC Config = `30` 時存在；Block Nb = `00` 印 Algo settings，否則印 PLL settings；原樣 hex |

### 範例
- Raw：`2F 3D 01 31`
```text
  << RF_SPC_CMD >>  
  * SPC Cfg: Start SPC algorithm
#end
```
- Raw：`2F 3D 04 30 00 AA BB`
```text
  << RF_SPC_CMD >>  
  * SPC Cfg: Configure NFCC for SPC
  * Block Nb: 00
  * Algo settings: AABB
#end
```

<a id="rf_spc_rsp"></a><a id="RF_SPC_RSP"></a>
## RF_SPC_RSP  (`4F 3D`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | Proprietary / 0x3D / RSP |
| Handler | [`Proprietary.py:952`](../../nci_decoder/Nxp_pkg/Proprietary.py#L952) `RF_SPC_RSP` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |

### 範例
- Raw：`4F 3D 01 00`
```text
  << RF_SPC_RSP >>  
  * Status: STATUS_OK
#end
```

<a id="rf_spc_ntf"></a><a id="RF_SPC_NTF"></a>
## RF_SPC_NTF  (`6F 3D`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | Proprietary / 0x3D / NTF |
| Handler | [`Proprietary.py:967`](../../nci_decoder/Nxp_pkg/Proprietary.py#L967) `RF_SPC_NTF` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | local `tbl_spc_status`：`00` SPC_STATUS_OK (OK, phase offset updated)、`01` SPC_STATUS_RX_PROTECTION (NOK)、`02` SPC_STATUS_OVERCURRENT (NOK)、`04` SPC_STATUS_OVERCURRENT_DISCARD (OK, phase offset updated)、`08` SPC_STATUS_RSSITHRESH_DISCARD、`F0` RFU |
| 2 | IndexStart | 1 | 十進位 + 原始 hex |
| 3 | IndexEnd | 1 | 十進位 + 原始 hex |
| 4 | RSSI | 2 | little-endian：`byte0 + byte1 × 256` |
| 5 | CustomerPhaseTrim | 2 | little-endian（base 16）組合後視為 signed 16-bit，× 0.25 印成 `* Phase: <deg> °`（例：`0A 00` → 2.5 °、`FC FF` → -1.0 °） |

### 範例
- Raw：`6F 3D 07 00 05 10 34 12 04 00`
```text
  << RF_SPC_NTF >>  
  * Status: SPC_STATUS_OK (OK, phase offset updated)
  * IndexStart: 5 (05)
  * IndexEnd: 16 (10)
  * RSSI: 4660
  * Phase: 1.0 °
#end
```
- Raw：`6F 3D 07 00 05 10 34 12 0A 00`（Phase 含 hex 字母）
```text
  << RF_SPC_NTF >>  
  * Status: SPC_STATUS_OK (OK, phase offset updated)
  * IndexStart: 5 (05)
  * IndexEnd: 16 (10)
  * RSSI: 4660
  * Phase: 2.5 °
#end
```

### 實作備註
- ✅ 已修正（2026-10）：Phase 改以 base 16 解析，含 A–F 的值正常解碼（見上例 `0A 00` → 2.5 °），負值判斷 `& 0x8000` 生效。
- Status 查表 `tbl_spc_status.get(status)` 沒有預設值，未列出的值會印 `None`。

<a id="test_swp_cmd"></a><a id="TEST_SWP_CMD"></a>
## TEST_SWP_CMD  (`2F 3E`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | Proprietary / 0x3E / CMD |
| Handler | [`Proprietary.py:1011`](../../nci_decoder/Nxp_pkg/Proprietary.py#L1011) `TEST_SWP_CMD` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Link Identifier | 1 | `00` NFC_SIM_SWIO1 (UICC1)、`01` Mailbox (eSE)、`02` NFC_SIM_SWIO2 (UICC2)、其他 Forbidden |

### 範例
- Raw：`2F 3E 01 00`
```text
  << TEST_SWP_CMD >>  
  * Link ID: NFC_SIM_SWIO1 (UICC1)
#end
```

<a id="test_swp_rsp"></a><a id="TEST_SWP_RSP"></a>
## TEST_SWP_RSP  (`4F 3E`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | Proprietary / 0x3E / RSP |
| Handler | [`Proprietary.py:1032`](../../nci_decoder/Nxp_pkg/Proprietary.py#L1032) `TEST_SWP_RSP` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | 僅 `00`/`05` 查 `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)），其他值印 `Forbidden` |

### 範例
- Raw：`4F 3E 01 00`
```text
  << TEST_SWP_RSP >>  
  * Status: STATUS_OK
#end
```

<a id="test_swp_ntf"></a><a id="TEST_SWP_NTF"></a>
## TEST_SWP_NTF  (`6F 3E`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | Proprietary / 0x3E / NTF |
| Handler | [`Proprietary.py:1049`](../../nci_decoder/Nxp_pkg/Proprietary.py#L1049) `TEST_SWP_NTF` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | 僅 `00`/`03` 查 `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)），其他值印 `Forbidden` |
| 2 | Power Mode | 1 | `00` No SIMVCC、`01` SIMVCC = 1.8V、`02` SIMVCC = 3.3V、`03` SIMVCC undetermined、其他 RFU |

### 範例
- Raw：`6F 3E 02 00 01`
```text
  << TEST_SWP_NTF >>  
  * Status: STATUS_OK
  * Power Mode: SIMVCC = 1.8V
#end
```

<a id="optional_cmd"></a><a id="OPTIONAL_CMD"></a>
## OPTIONAL_CMD  (`2F 3F`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | Proprietary / 0x3F / CMD |
| Handler | [`Proprietary.py:1081`](../../nci_decoder/Nxp_pkg/Proprietary.py#L1081) `OPTIONAL_CMD` |

此 OID 原本有三個替代 handler（AST_UTILITY / DPC_HELPER / SWITCH_RF_FIELD，見[未註冊 / 已停用的 handler](#未註冊--已停用的-handler)），現合併為 `OPTIONAL_CMD`，**以 payload 第 1 byte（Test ID / Param 1）區分 sub-command**，並存入全域 `TEST_ID_3F` 供 `OPTIONAL_RSP` 使用；另外印一行 `<< 子命令名 >>`。

### Payload 格式（依第 1 byte）

**`70` → AST_UTILITY_CMD**

| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Param 1 | 1 | `70`，印 "Antenna Self-Test utility APIs" |
| 2 | Param 2 | 1 | local `tbl_ast_param2`：`00` READ_VDDPA_CODE_CMD、`01` FORCE_NEW_VDDPA_CMD、`02` FORCE_DPC_OFF_CMD、其他 RFU；同時存入全域 `DPC_TYPE` |
| 3 | Input | 1 | 原樣 hex |

**`04` → DPC_HELPER_ACT_CMD**

| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Test ID | 1 | `04`，印 "ENABLE DPC HELPER" |
| 2 | Reserved | 1 | RFU，跳過不印 |
| 3 | Reserved | 1 | RFU，跳過不印 |

**`05` → DPC_HELPER_CMD**

| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Test ID | 1 | `05`，印 "READ DPC HELPER DATA" |
| 2 | Reserved | 1 | RFU，跳過不印 |
| 3 | Reserved | 1 | RFU，跳過不印 |

**`32` → SWITCH_RF_FIELD_CMD**

| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Test ID | 1 | `32`，印 "Switch RF Field On/Off" |
| 2 | Field Type | 1 | local `tbl_field_type`：`00` Field Off、`01` Field On AST1、`02` Field On AST2、其他 RFU |
| 3 | Reserved | 1 | RFU，跳過不印 |

### 範例
- Raw：`2F 3F 03 70 00 00`
```text
  << OPTIONAL_CMD >>  
  << AST_UTILITY_CMD >>  
  * Param 1: Antenna Self-Test utility APIs
  * Param 2: READ_VDDPA_CODE_CMD
  * Input: 00
#end
```
- Raw：`2F 3F 03 70 02 00`
```text
  << OPTIONAL_CMD >>  
  << AST_UTILITY_CMD >>  
  * Param 1: Antenna Self-Test utility APIs
  * Param 2: FORCE_DPC_OFF_CMD
  * Input: 00
#end
```
- Raw：`2F 3F 03 04 00 00`
```text
  << OPTIONAL_CMD >>  
  << DPC_HELPER_ACT_CMD >>  
  * Test ID: ENABLE DPC HELPER
#end
```
- Raw：`2F 3F 03 05 00 00`
```text
  << OPTIONAL_CMD >>  
  << DPC_HELPER_CMD >>  
  * Test ID: READ DPC HELPER DATA
#end
```
- Raw：`2F 3F 03 32 01 00`
```text
  << OPTIONAL_CMD >>  
  << SWITCH_RF_FIELD_CMD >>  
  * Test ID: Switch RF Field On/Off
  * Field Type: Field On AST1
#end
```

### 實作備註
- 第 1 byte 不是 `70`/`04`/`05`/`32` 時，什麼都不印、回傳 0，必然 `Payload error!!`；但 `TEST_ID_3F` 仍會被覆寫成該值，導致下一個 `OPTIONAL_RSP` 也不解析。

<a id="optional_rsp"></a><a id="OPTIONAL_RSP"></a>
## OPTIONAL_RSP  (`4F 3F`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | Proprietary / 0x3F / RSP |
| Handler | [`Proprietary.py:1135`](../../nci_decoder/Nxp_pkg/Proprietary.py#L1135) `OPTIONAL_RSP` |

RSP 本身沒有 sub-command 欄位，**完全依前一個 `OPTIONAL_CMD` 留下的 `TEST_ID_3F`（初始 `'32'`）與 `DPC_TYPE`（初始 `'02'`）決定格式**。

### Payload 格式（依 `TEST_ID_3F`）

**`70` → AST_UTILITY_RSP**

| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status 或 VDDPA voltage code | 1 | `DPC_TYPE` 為 `01`/`02`：Status，查 `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)）；`DPC_TYPE` 為 `00`：VDDPA = `1.5 + int(code, 16) × 0.05` V；其他 `DPC_TYPE`：不印但仍消耗 1 octet |

**`04` → DPC_HELPER_ACT_RSP**

| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Test ID | 1 | 不讀值，固定印 "ENABLE DPC HELPER" |
| 2 | Reserved | 1 | 跳過 |
| 3 | Reserved | 1 | 跳過 |

**`05` → DPC_HELPER_RSP**

| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |
| 2 | （未知） | 1 | 跳過；程式註解「(0F) 不確定用途」 |
| 3 | DPC Info | 6 × N | 先原樣印出全部，再每 6 octets 一筆印成表格（見下） |

DPC Info 每筆 6 octets（以 hex 字元索引描述）：
- `Current (mA)` = `int(byte0, 16) + (int(byte1, 16) & 0x0F) × 256`（12-bit；byte1 高 nibble 為旗標 / RFU，依 NXP UM）
- `VDDPA (V)` = `int(byte2, 16) × 0.05 + 1.5`
- `Power (W)` = `VDDPA × Current / 1000`
- `NCI cmd` 欄印 byte0–byte2 原始 hex；byte3–byte5 不解析。

**`32` → SWITCH_RF_FIELD_RSP**

| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |

### 範例
（每個 RSP 都緊接在上方對應的 `OPTIONAL_CMD` 範例之後執行。）
- 前一 CMD `2F 3F 03 70 00 00`（READ_VDDPA_CODE）→ Raw：`4F 3F 01 10`
```text
  << OPTIONAL_RSP >>  
  << AST_UTILITY_RSP >>  
  * VDDPA: 2.3 V
#end
```
- 前一 CMD `2F 3F 03 70 02 00`（FORCE_DPC_OFF）→ Raw：`4F 3F 01 00`
```text
  << OPTIONAL_RSP >>  
  << AST_UTILITY_RSP >>  
  * Status: STATUS_OK
#end
```
- 前一 CMD `2F 3F 03 04 00 00` → Raw：`4F 3F 03 04 00 00`
```text
  << OPTIONAL_RSP >>  
  << DPC_HELPER_ACT_RSP >>  
  * Test ID: ENABLE DPC HELPER
#end
```
- 前一 CMD `2F 3F 03 05 00 00` → Raw：`4F 3F 0E 00 0F 36 81 0D 00 00 00 37 81 0C 00 00 00`
```text
  << OPTIONAL_RSP >>  
  << DPC_HELPER_RSP >>  
  * Status: STATUS_OK
  * DPC Info: 36810D00000037810C000000
   ~  #  ~  Power  ~  VDDPA  ~  Current  ~  NCI cmd  ~
      0    0.666 W    2.15 V     310 mA      36810D
      1    0.653 W    2.10 V     311 mA      37810C
#end
```

- 驗收向量（10 筆 DPC entry，依 NXP UM 的 12-bit current）：前一 CMD `2F 3F 03 05 00 00` → Raw：`4F 3F 3E 00 0F 36 81 0D 00 00 00 37 81 0C 00 00 00 37 81 0C 00 00 00 37 81 0C 00 00 00 36 81 0D 00 00 00 36 81 0D 00 00 00 36 81 0D 00 00 00 37 81 0C 00 00 00 36 81 0D 00 00 00 37 81 0C 00 00 00`

```text
  << OPTIONAL_RSP >>  
  << DPC_HELPER_RSP >>  
  * Status: STATUS_OK
  * DPC Info: 36810D00000037810C00000037810C00000037810C00000036810D00000036810D00000036810D00000037810C00000036810D00000037810C000000
   ~  #  ~  Power  ~  VDDPA  ~  Current  ~  NCI cmd  ~
      0    0.666 W    2.15 V     310 mA      36810D
      1    0.653 W    2.10 V     311 mA      37810C
      2    0.653 W    2.10 V     311 mA      37810C
      3    0.653 W    2.10 V     311 mA      37810C
      4    0.666 W    2.15 V     310 mA      36810D
      5    0.666 W    2.15 V     310 mA      36810D
      6    0.666 W    2.15 V     310 mA      36810D
      7    0.653 W    2.10 V     311 mA      37810C
      8    0.666 W    2.15 V     310 mA      36810D
      9    0.653 W    2.10 V     311 mA      37810C
#end
```
- 前一 CMD `2F 3F 03 32 01 00` → Raw：`4F 3F 01 00`
```text
  << OPTIONAL_RSP >>  
  << SWITCH_RF_FIELD_RSP >>  
  * Status: STATUS_OK
#end
```

### 實作備註
- 有狀態依賴：單獨解碼一個 `4F 3F`（log 中沒有對應 CMD）時會以初始值 `TEST_ID_3F = '32'` 當成 SWITCH_RF_FIELD_RSP 解析。
- ✅ 已修正（2026-10）：AST_UTILITY READ_VDDPA 分支改以 base 16 解析 code（`10` → 2.3 V），與 DPC_HELPER_RSP 一致。
- ✅ 已確認（2026-10，依 NXP UM）：DPC_HELPER_RSP 的 Current 為 12-bit：`byte0 + (byte1 & 0x0F) × 256`，byte1 高 nibble 為旗標 / RFU（例：`36 81` → 310 mA）。（10-15 曾誤改為取整個 byte1，算出 33078 mA，10-16 依 UM 改回。）
- DPC_HELPER_RSP 中 Status 後的 byte（例 `0F`）用途不明，仍直接跳過。
- DPC_HELPER_ACT_RSP 不讀取 payload 值，固定印 "ENABLE DPC HELPER"。

---

## 未註冊 / 已停用的 handler

`__ctrl__.py` 中以下項目被註解掉或從未註冊（`0x1C` NTF 已於 2026-10 補註冊，保留於表中供對照）。對應封包目前在 decoder 中的行為與 `Proprietary.py` 內的實作現況如下。

| OID / MT | `__ctrl__.py` 註解中的 handler | `Proprietary.py` 現況 | 目前解碼結果 |
|---|---|---|---|
| 0x32 CMD/RSP | `READ_TXLDO_CURRENT_CMD` / `_RSP`（AST Loop 1） | 無同名函式；邏輯併入 `READ_OPTION_CMD/RSP` 的 `AST_LOOP == '01'` 分支 | 走 `READ_OPTION_*`，但因 `AST_LOOP` 固定 `'00'`，實際以 RF_TEST_API 格式解析 |
| 0x32 CMD/RSP | `READ_RSSI_CMD` / `_RSP`（AST Loop 2） | 無同名函式；併入 `AST_LOOP == '02'` 分支 | 同上 |
| 0x32 CMD/RSP | `RF_TEST_API_CMD` / `_RSP` | 無同名函式；併入 `AST_LOOP == '00'` 分支（即目前生效的分支） | 正常解析 |
| 0x3F CMD/RSP | `AST_UTILITY_CMD` / `_RSP` | 無同名函式；併入 `OPTIONAL_CMD/RSP` 的 Test ID `70` 分支 | 正常解析（見 [OPTIONAL_CMD](#optional_cmd--2f-3f)） |
| 0x3F CMD/RSP | `DPC_HELPER_CMD` / `_RSP` | 無同名函式；併入 Test ID `04`（DPC_HELPER_ACT）與 `05`（DPC_HELPER）分支 | 正常解析 |
| 0x3F CMD/RSP | `SWITCH_RF_FIELD_CMD` / `_RSP` | 無同名函式；併入 Test ID `32` 分支 | 正常解析 |
| 0x25 NTF | `LPCD_FPC_NTF`（註解「找不到實作」） | **不存在**任何實作 | `6F 25 00` → `<< ERROR_NOT_FOUND >>` 並丟出 `KeyError: '25'` |
| 0x1C NTF | ✅ 已修正（2026-10）：已註冊於 `__ctrl__.py` OID `1C` | `LOW_POWER_TAG_REMOVAL_NTF`（[`Proprietary.py:276`](../../nci_decoder/Nxp_pkg/Proprietary.py#L276)）；無 payload，印 `(Empty)`，回傳 0 | 正常解析（見 [LOW_POWER_TAG_REMOVAL_NTF](#low_power_tag_removal_ntf--6f-1c)） |

### OID 0x32 已停用分支的 payload 格式

**READ_TXLDO_CURRENT（`AST_LOOP == '01'`）**

| 方向 | # | 欄位 | 長度 (Octets) | 解析方式 |
|---|---|---|---|---|
| CMD | 1 | Test ID | 1 | 應為 `08`（不檢查），印 "Read TxLdo current" |
| CMD | 2 | Wait_Time | 1 | 十進位 µs |
| RSP | 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |
| RSP | 2 | TXLDO_CURRENT | 2 | `int(byte0, 16) + int(byte1, 16) × 256` mA（little endian） |

**READ_RSSI（`AST_LOOP == '02'`）**

| 方向 | # | 欄位 | 長度 (Octets) | 解析方式 |
|---|---|---|---|---|
| CMD | 1 | Test ID | 1 | 應為 `20`（不檢查），印 "Read RSSI Command" |
| CMD | 2 | Wait_Time | 1 | 十進位 µs |
| RSP | 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |
| RSP | 2 | （未命名） | 2 | 跳過 |
| RSP | 3 | RSSI_VALUE | 4 | 原樣 hex |
| RSP | 4 | Interpolated RSSI | 4 | 原樣 hex |

**RF_TEST_API（`AST_LOOP == '00'`）**：格式同 [READ_OPTION_CMD](#read_option_cmd--2f-32) / [READ_OPTION_RSP](#read_option_rsp--4f-32) 的預設分支。

以下範例為驗證用：在執行前以 `setattr(Nxp_pkg.Proprietary, 'AST_LOOP', ...)` 暫時改寫模組變數取得，正常使用 decoder 時不會出現。

- `AST_LOOP = '01'`，Raw：`2F 32 02 08 0A`
```text
  << READ_OPTION_CMD >>  
  << READ_TXLDO_CURRENT_CMD >>  
  * Test ID: Read TxLdo current (08)
  * Wait_Time: 10 µs
#end
```
- `AST_LOOP = '01'`，Raw：`4F 32 03 00 34 12`
```text
  << READ_OPTION_RSP >>  
  << READ_TXLDO_CURRENT_RSP >>  
  * Status: STATUS_OK
  * TXLDO_CURRENT: 4660 mA
#end
```
- `AST_LOOP = '02'`，Raw：`2F 32 02 20 0A`
```text
  << READ_OPTION_CMD >>  
  << READ_RSSI_CMD >>  
  * Test ID: Read RSSI Command (20)
  * Wait_Time: 10 µs
#end
```
- `AST_LOOP = '02'`，Raw：`4F 32 0B 00 00 00 11 22 33 44 55 66 77 88`
```text
  << READ_OPTION_RSP >>  
  << READ_RSSI_RSP >>  
  * Status: STATUS_OK
  * RSSI_VALUE: 11223344
  * Interpolated RSSI: 55667788
#end
```

### OID 0x3F 已停用 handler 的 payload 格式
AST_UTILITY / DPC_HELPER(_ACT) / SWITCH_RF_FIELD 的 CMD 與 RSP 格式已完整列於 [OPTIONAL_CMD](#optional_cmd--2f-3f) 與 [OPTIONAL_RSP](#optional_rsp--4f-3f)，目前皆可透過合併後的 handler 正常解析。

### 未註冊封包的範例
- Raw：`6F 25 00`
```text
  << ERROR_NOT_FOUND >>  
(Python 例外：KeyError: '25')
```
- Raw：`6F 1C 00`（✅ 已修正（2026-10）：現已註冊，正常解析）
```text
  << LOW_POWER_TAG_REMOVAL_NTF >>  
         (Empty)         
#end
```
（`6F 25 00`：`Decoder_Main` 印出 `ERROR_NOT_FOUND` 後 `raise` 原例外 `KeyError: '25'`。）
