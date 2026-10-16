# NFC Forum NCI 2.0 — RF Management (GID 0x1)

本文件說明 `nfc_forum_2_0_pkg/RF_Management.py` 中所有 RF Management 控制訊息 handler 的 payload 解析方式。Dispatch 依 [`__ctrl__.py`](../../nci_decoder/nfc_forum_2_0_pkg/__ctrl__.py#L21) 的 `"RF Management"` 群組（OID 0x00–0x11，0x12–0x3F 為 RFU）。CMD header 首 byte 為 `21`、RSP 為 `41`、NTF 為 `61`。

Handler 收到的 `raw` 是 3-byte header 之後的 payload hex 字串，以 `p_payload`（hex 字元 offset，1 octet = 2 字元）向後解析，最後回傳 offset；`Decoder_Main.NFC_NCI_DECODER` 會比對回傳值與 header 宣告的長度，不一致時印出 `Error: Payload error!!`。所有對照表都來自 `nfc_forum_2_0_pkg/__table__.py`（透過 `__pkg_import__.tbl_import(vendor, model)` 載入）。注意：`Decoder_Main` 呼叫 handler 時只傳入 `raw`（`pkg.tbl_nci_ctrl[gid][oid][mt](raw[6::])`），所以 handler 內的 `vendor`/`model` 永遠是預設值 `"None"`，一律使用 nfc_forum_2_0 的表。

除非另外註明，表格查詢皆使用 `range_lookup.lookup(NFC_table.tbl_xxx, value)`：先精確鍵值，再比對 `'XX-YY'` 範圍鍵（例如 `'80-FE'`），都沒有才回傳 `RFU`。仍使用 `.get()` 的少數欄位（RF Discovery ID、NFCEE ID 等）各節會特別說明。

含內部長度欄位的子結構（Routing Entry Value、RF Technology Specific Parameters、Activation Parameters、Information Entry Value）都以宣告的長度為界解析：內部欄位超出宣告長度時印 `  * Error: <結構名稱>: Payload too short: need <k> byte(s) for <欄位>, <r> left`，然後從宣告長度之後繼續解析。

本文件的範例都是用 `NFC_NCI_DECODER(len(raw)//2, raw, 'None', 'None', 2)`（vendor = `'None'`，mode = 2，不印 raw）實際執行後取得的輸出。

## 總覽

| OID | CMD (`21 xx`) | RSP (`41 xx`) | NTF (`61 xx`) |
|---|---|---|---|
| 0x00 | [RF_DISCOVER_MAP_CMD](#rf_discover_map_cmd--21-00) | [RF_DISCOVER_MAP_RSP](#rf_discover_map_rsp--41-00) | — |
| 0x01 | [RF_SET_LISTEN_MODE_ROUTING_CMD](#rf_set_listen_mode_routing_cmd--21-01) | [RF_SET_LISTEN_MODE_ROUTING_RSP](#rf_set_listen_mode_routing_rsp--41-01) | — |
| 0x02 | [RF_GET_LISTEN_MODE_ROUTING_CMD](#rf_get_listen_mode_routing_cmd--21-02) | [RF_GET_LISTEN_MODE_ROUTING_RSP](#rf_get_listen_mode_routing_rsp--41-02) | [RF_GET_LISTEN_MODE_ROUTING_NTF](#rf_get_listen_mode_routing_ntf--61-02) |
| 0x03 | [RF_DISCOVER_CMD](#rf_discover_cmd--21-03) | [RF_DISCOVER_RSP](#rf_discover_rsp--41-03) | [RF_DISCOVER_NTF](#rf_discover_ntf--61-03) |
| 0x04 | [RF_DISCOVER_SELECT_CMD](#rf_discover_select_cmd--21-04) | [RF_DISCOVER_SELECT_RSP](#rf_discover_select_rsp--41-04) | — |
| 0x05 | — | — | [RF_INTF_ACTIVATED_NTF](#rf_intf_activated_ntf--61-05) |
| 0x06 | [RF_DEACTIVATE_CMD](#rf_deactivate_cmd--21-06) | [RF_DEACTIVATE_RSP](#rf_deactivate_rsp--41-06) | [RF_DEACTIVATE_NTF](#rf_deactivate_ntf--61-06) |
| 0x07 | — | — | [RF_FIELD_INFO_NTF](#rf_field_info_ntf--61-07) |
| 0x08 | [RF_T3T_POLLING_CMD](#rf_t3t_polling_cmd--21-08) | [RF_T3T_POLLING_RSP](#rf_t3t_polling_rsp--41-08) | [RF_T3T_POLLING_NTF](#rf_t3t_polling_ntf--61-08) |
| 0x09 | — | — | [RF_NFCEE_ACTION_NTF](#rf_nfcee_action_ntf--61-09) |
| 0x0A | — | — | [RF_NFCEE_DISCOVERY_REQ_NTF](#rf_nfcee_discovery_req_ntf--61-0a) |
| 0x0B | [RF_PARAMETER_UPDATE_CMD](#rf_parameter_update_cmd--21-0b) | [RF_PARAMETER_UPDATE_RSP](#rf_parameter_update_rsp--41-0b) | — |
| 0x0C | [RF_INTF_EXT_START_CMD](#rf_intf_ext_start_cmd--21-0c) | [RF_INTF_EXT_START_RSP](#rf_intf_ext_start_rsp--41-0c) | — |
| 0x0D | [RF_INTF_EXT_STOP_CMD](#rf_intf_ext_stop_cmd--21-0d) | [RF_INTF_EXT_STOP_RSP](#rf_intf_ext_stop_rsp--41-0d) | — |
| 0x0E | [RF_EXT_AGG_ABORT_CMD](#rf_ext_agg_abort_cmd--21-0e) | [RF_EXT_AGG_ABORT_RSP](#rf_ext_agg_abort_rsp--41-0e) | — |
| 0x0F | [RF_NDEF_ABORT_CMD](#rf_ndef_abort_cmd--21-0f) | [RF_NDEF_ABORT_RSP](#rf_ndef_abort_rsp--41-0f) | — |
| 0x10 | [RF_ISO_DEP_NAK_PRESENCE_CMD](#rf_iso_dep_nak_presence_cmd--21-10) | [RF_ISO_DEP_NAK_PRESENCE_RSP](#rf_iso_dep_nak_presence_rsp--41-10) | [RF_ISO_DEP_NAK_PRESENCE_NTF](#rf_iso_dep_nak_presence_ntf--61-10) |
| 0x11 | [RF_SET_FORCED_NFCEE_ROUTING_CMD](#rf_set_forced_nfcee_routing_cmd--21-11) | [RF_SET_FORCED_NFCEE_ROUTING_RSP](#rf_set_forced_nfcee_routing_rsp--41-11) | — |

合計 37 個 dispatch handler（CMD 14、RSP 14、NTF 9）。另有兩個共用的內部 helper：[`LISTEN_MODE_ROUTING_INFO`](#共用結構-a-listen_mode_routing_info) 與 [`RF_TECH_SPEC_PARA`](#共用結構-b-rf_tech_spec_para)，以及 RF_INTF_ACTIVATED_NTF 內的 [Activation Parameters 分支](#activation-parameters-分支依-rf-interface--activation-rf-technology-and-mode)。

---

## 共用結構 A LISTEN_MODE_ROUTING_INFO

| 項目 | 值 |
|---|---|
| Handler | [`RF_Management.py:97`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L97) `LISTEN_MODE_ROUTING_INFO` |
| 使用者 | [RF_SET_LISTEN_MODE_ROUTING_CMD](#rf_set_listen_mode_routing_cmd--21-01)、[RF_GET_LISTEN_MODE_ROUTING_NTF](#rf_get_listen_mode_routing_ntf--61-02) |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | More | 1 | `tbl_more`（見 [Tables](Tables.md#tbl_more)） |
| 2 | Number of Routing Entries | 1 (n) | 十進位顯示 |
| 3 | Routing Entry [1..n] | x+2 | 每筆為 TLV，見下 |
| ﹂ | Qualifier-Type (Type) | 1 | 低 nibble 查 `tbl_L_mode_routing_entry_type`（見 [Tables](Tables.md#tbl_L_mode_routing_entry_type)）；高 nibble 依 Table 52 解 bit flag（見下） |
| ﹂ | Length | 1 (x) | 十進位顯示 |
| ﹂ | Value | x | 先整串印出 `Val:`，再依 Type 拆解（見下表） |

**Qualifier-Type bit field（Table 52，程式直接實作在 code 中）**

| Bit | 意義（程式印出的文字） |
|---|---|
| b7 | RFU（程式不檢查） |
| b6 | `Routing is blocked for the power modes where it is not supported.` |
| b5 | `Match is allowed when the SELECT AID is shorter than the AID in this routing table entry.` |
| b4 | `Match is allowed when the SELECT AID is longer than the AID in this routing table entry.` |
| b3–b0 | Routing Entry Type（`tbl_L_mode_routing_entry_type`） |

**Value 欄位共同前綴（所有 Type 都先解這兩個 octet）**

| # | 欄位 | 長度 | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Route | 1 | `tbl_nfcee_id`（見 [Tables](Tables.md#tbl_nfcee_id)）：先精確查詢（查不到就印原值），再用 `range_lookup.find_range_key` 找範圍鍵（`02-0F`/`10-7F`/`80-FE`）附加說明 |
| 2 | Power State | 1 | 印出 8-bit 二進位，再對 bit5..bit0 逐一查 `tbl_pwr_state`（見 [Tables](Tables.md#tbl_pwr_state)），1 = `Apply`、0 = `Not apply` |

**Power State bit 對應（`tbl_pwr_state`，Table 59）**

| Bit | 意義 |
|---|---|
| b7–b6 | RFU（不印） |
| b5 | Screen Off lock (Sub-State 3) |
| b4 | Screen On lock (Sub-State 2) |
| b3 | Screen off unlock (Sub-State 1) |
| b2 | Battery Off State |
| b1 | Switch Off State |
| b0 | Switch On State |

**依 Routing Entry Type 的 Value 其餘欄位**

| Type (低 nibble) | 名稱 | Value 格式（Route + Power State 之後） | 解析方式 |
|---|---|---|---|
| `0` | Technology-based routing entry（Table 54） | Technology：1 octet | `tbl_rf_tech`（見 [Tables](Tables.md#tbl_rf_tech)） |
| `1` | Protocol-based routing entry（Table 55） | Protocol：1 octet | `tbl_rf_proto`（見 [Tables](Tables.md#tbl_rf_proto)），`lookup` 可解析 `80-FE` proprietary |
| `2` | AID-based routing entry（Table 56） | AID：0–16 octets | 不查表；Route + Power State 之後剩餘的 octets（> 0 時）整段印 hex |
| `3` | System Code-based routing entry（Table 57） | SC Route List：2n octets | 依 `(x-2)//2` 筆，每筆 2 octet 印 hex，標籤為 `SC Route <j>`（j = SC 索引） |
| `4` | APDU Pattern-based routing entry（Table 58） | Reference data：n octets、Mask：n octets（n = (x-2)//2） | 各印完整 n octets 的 hex |
| 其他 | — | — | 只印 Type `RFU`、Route、Power State，不再拆解 |

### 實作備註
- ✅ 已修正（2026-10）：AID-based（Type 2）只要 Route + Power State 之後還有資料就印 `AID:`，1–2 octets 的 AID 也會印出（見第二個範例）。
- ✅ 已修正（2026-10）：System Code-based（Type 3）的標籤改用 SC 自己的索引（`SC Route 0`、`SC Route 1`…）。
- ✅ 已修正（2026-10）：APDU Pattern-based（Type 4）的 Reference data 與 Mask 各印完整 n = (x-2)//2 octets（如 `00A4` / `FFFF`）。
- ✅ 已修正（2026-10）：Value 以宣告的 Length 為界解析，內部欄位不足時印 `* Error: Routing Entry Value: Payload too short: ...`，不再讀到下一筆 entry。
- Type 欄位查表用的是 `q_type[1:2]`（低 nibble 字元），印出的是整個 octet 原值（例如 `(72)`）。
- 函式內用 `len` 當變數名稱，遮蔽了 Python 內建的 `len`（只影響這個函式的區域範圍）。

---

## 共用結構 B RF_TECH_SPEC_PARA

| 項目 | 值 |
|---|---|
| Handler | [`RF_Management.py:328`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L328) `RF_TECH_SPEC_PARA` |
| 使用者 | [RF_DISCOVER_NTF](#rf_discover_ntf--61-03)、[RF_INTF_ACTIVATED_NTF](#rf_intf_activated_ntf--61-05) |

這個函式解析 RF Technology Specific Parameters。分支條件是 RF Technology and Mode 的 hex code 本身（`00`、`80`、`01`…，見 [Tables](Tables.md#tbl_rf_tech_mode)），不再依查表得到的名稱字串。讀取範圍限制在外層宣告的 Length 之內（`_SubRaw`）；函式沒有回傳值，呼叫端用外層的 Length 欄位前進 offset。

| RF Technology and Mode | 規範表 | 欄位（依序） | 長度 (Octets) | 解析方式 |
|---|---|---|---|---|
| `00` A_PASSIVE_POLL | Table 68 | SENS_RES Response | 2 | 印 hex |
| | | NFCID1 Length | 1 (l) | 十進位 |
| | | NFCID1 | l（4/7/10） | 印 hex |
| | | SEL_RES Response Length | 1 (l) | 十進位 |
| | | SEL_RES Response | l（0 或 1） | 印 hex |
| | | HRx Length | 1 (l) | 十進位 |
| | | HRx | l（0 或 2） | 只在 l ≠ 0 時印 hex |
| `80` A_PASSIVE_LISTEN | Table 69 | （無） | 0 | 印 `There is no RF Technology Specific Parameters` |
| `01` B_PASSIVE_POLL | Table 70 | SENSB_RES Response Length | 1 (l) | 十進位 |
| | | SENSB_RES Response | l（11 或 12） | 印 hex |
| `81` B_PASSIVE_LISTEN | Table 71 | SENSB_REQ Command | 1 | 印 hex |
| `02` F_PASSIVE_POLL | Table 72 | Bit Rate | 1 | 程式內寫死：`01` → `212 kbps`、`02` → `424 kbps`，其他 → `RFU (xx)` |
| | | SENSF_RES Response Length | 1 (l) | 十進位 |
| | | SENSF_RES Response | l（16 或 18） | 印 hex（`SENSF_RES_PARSER` 呼叫已被註解掉） |
| `82` F_PASSIVE_LISTEN | Table 73 | Local NFCID2 Length | 1 (l) | 十進位 |
| | | Local NFCID2 | l（0 或 8） | 印 hex |
| `06` V_PASSIVE_POLL | Table 74 | RES_FLAG | 1 | 印 hex |
| | | DSFID | 1 | 印 hex |
| | | UID | 8 | 印 hex |
| `03` ACTIVE_POLL | Table 75 | ATR_RES Response Length | 1 (n) | 十進位 |
| | | ATR_RES Response | n | 印 hex |
| `83` ACTIVE_LISTEN | Table 76 | ATR_REQ Command Length | 1 (n) | 十進位 |
| | | ATR_REQ Command | n | 印 hex |
| 其他（hex code 不是上述值，包含 RFU 與 `70-7F`/`F0-FF` proprietary） | — | Proprietary parameters | 全部 | 整段印 hex：`Proprietary parameters: ...` |

### 實作備註
- ✅ 已修正（2026-10）：改依 hex code 分支，不再依查表字串（NXP 表的名稱如 `ACTIVE_POLL ( Not supported )` 不影響分支）。未列出的 code（`70`–`7F`、`F0`–`FF` proprietary 及 `04`、`05` 等 RFU）仍走 `else` 印 `Proprietary parameters`。
- ✅ 已修正（2026-10）：讀取以外層宣告的 Length 為界，內部欄位超出時印 `* Error: RF Technology Specific Parameters: Payload too short: ...`（例如 A_PASSIVE_POLL 搭配 Length 0）。
- 內部欄位讀完後若宣告長度還有剩餘 octets，不會印出也不會警告（例如 B_PASSIVE_LISTEN 宣告 Length 2 只印 SENSB_REQ 1 octet）。
- NFC-B Poll 的 SENSB_RES、NFC-F Poll 的 SENSF_RES 都只印 raw hex，沒有再拆欄位。

---

<a id="rf_discover_map_cmd"></a><a id="RF_DISCOVER_MAP_CMD"></a>
## RF_DISCOVER_MAP_CMD  (`21 00`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x00 / CMD |
| Handler | [`RF_Management.py:42`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L42) `RF_DISCOVER_MAP_CMD` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Number of Mapping Configurations | 1 (n) | 十進位 |
| 2 | Mapping Configuration [1..n] | 3 | |
| ﹂ | RF Protocol | 1 | `tbl_rf_proto`（見 [Tables](Tables.md#tbl_rf_proto)） |
| ﹂ | Mode | 1 | `tbl_mode`（見 [Tables](Tables.md#tbl_mode)） |
| ﹂ | RF Interface | 1 | `tbl_rf_if`（見 [Tables](Tables.md#tbl_rf_if)） |

### 範例
- Raw：`21 00 07 02 04 01 02 05 03 03`

```text
  << RF_DISCOVER_MAP_CMD >>  
  * Number of Mapping Configs: 2 (02)

   ~ [Mapping Cfg_0] ~  
    * RF Protocol: ISO-DEP (04)
    * Mode: Polling (01)
    * RF Interface: ISO-DEP (02)

   ~ [Mapping Cfg_1] ~  
    * RF Protocol: NFC-DEP (05)
    * Mode: Listen/Polling (03)
    * RF Interface: NFC-DEP (03)
#end
```

### 實作備註
- ✅ 已修正（2026-10）：`tbl_rf_proto`、`tbl_rf_if` 改用 `lookup`，proprietary 值（`80-FE`）顯示 `For proprietary use`。

---

<a id="rf_discover_map_rsp"></a><a id="RF_DISCOVER_MAP_RSP"></a>
## RF_DISCOVER_MAP_RSP  (`41 00`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x00 / RSP |
| Handler | [`RF_Management.py:82`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L82) `RF_DISCOVER_MAP_RSP` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |

### 範例
- Raw：`41 00 01 00`

```text
  << RF_DISCOVER_MAP_RSP >>  
  * Status: STATUS_OK (00)
#end
```

---

<a id="rf_set_listen_mode_routing_cmd"></a><a id="RF_SET_LISTEN_MODE_ROUTING_CMD"></a>
## RF_SET_LISTEN_MODE_ROUTING_CMD  (`21 01`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x01 / CMD |
| Handler | [`RF_Management.py:209`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L209) `RF_SET_LISTEN_MODE_ROUTING_CMD` |

### Payload 格式
直接呼叫 [`LISTEN_MODE_ROUTING_INFO`](#共用結構-a-listen_mode_routing_info)，格式見共用結構 A：

| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | More | 1 | `tbl_more`（見 [Tables](Tables.md#tbl_more)） |
| 2 | Number of Routing Entries | 1 (n) | 十進位 |
| 3 | Routing Entry [1..n]（TLV） | x+2 | Type：`tbl_L_mode_routing_entry_type`（見 [Tables](Tables.md#tbl_L_mode_routing_entry_type)）+ Table 52 flags；Value：Route（`tbl_nfcee_id`）、Power State（`tbl_pwr_state`）+ 依 Type 的欄位（Technology `tbl_rf_tech` / Protocol `tbl_rf_proto` / AID / SC Route List / APDU Reference data + Mask） |

### 範例
- Raw（5 種 routing entry type 各一筆；AID entry 的 Type = `72`，高 nibble 三個 flag 全開）：
  `21 01 27 00 05 00 03 00 01 00 01 03 80 3B 04 72 09 80 3B A0 00 00 00 03 10 10 03 06 02 01 40 00 FE 00 04 06 80 01 00 A4 FF FF`

```text
  << RF_SET_LISTEN_MODE_ROUTING_CMD >>  
  * More: Last Message (00)
  * Number of Routing Entries: 5 (05)

   ~ [Routing Entry_0] ~  
    * Type: Technology-based routing entry (00)
    * Len: 3
    * Val: 000100
      * Route: DH-NFCEE  (00)
      * Power State: 00000001 (01)
       ~ Screen Off lock (Sub-State 3):     Not apply
       ~ Screen On lock (Sub-State 2):      Not apply
       ~ Screen off unlock (Sub-State 1):   Not apply
       ~ Battery Off State:                 Not apply
       ~ Switch Off State:                  Not apply
       ~ Switch On State:                       Apply
      * Technology: NFC_RF_TECHNOLOGY_A (00)

   ~ [Routing Entry_1] ~  
    * Type: Protocol-based routing entry (01)
    * Len: 3
    * Val: 803B04
      * Route: 80 (HCI-NFCEE) (80)
      * Power State: 00111011 (3B)
       ~ Screen Off lock (Sub-State 3):         Apply
       ~ Screen On lock (Sub-State 2):          Apply
       ~ Screen off unlock (Sub-State 1):       Apply
       ~ Battery Off State:                 Not apply
       ~ Switch Off State:                      Apply
       ~ Switch On State:                       Apply
      * Protocol: ISO-DEP (04)

   ~ [Routing Entry_2] ~  
    * Type: AID-based routing entry (72)
     ~ Routing is blocked for the power modes where it is not supported.
     ~ Match is allowed when the SELECT AID is shorter than the AID in this routing table entry.
     ~ Match is allowed when the SELECT AID is longer than the AID in this routing table entry.
    * Len: 9
    * Val: 803BA0000000031010
      * Route: 80 (HCI-NFCEE) (80)
      * Power State: 00111011 (3B)
       ~ Screen Off lock (Sub-State 3):         Apply
       ~ Screen On lock (Sub-State 2):          Apply
       ~ Screen off unlock (Sub-State 1):       Apply
       ~ Battery Off State:                 Not apply
       ~ Switch Off State:                      Apply
       ~ Switch On State:                       Apply
      * AID: A0000000031010

   ~ [Routing Entry_3] ~  
    * Type: System Code-based routing entry (03)
    * Len: 6
    * Val: 02014000FE00
      * Route: 02 (Static IDs) (02)
      * Power State: 00000001 (01)
       ~ Screen Off lock (Sub-State 3):     Not apply
       ~ Screen On lock (Sub-State 2):      Not apply
       ~ Screen off unlock (Sub-State 1):   Not apply
       ~ Battery Off State:                 Not apply
       ~ Switch Off State:                  Not apply
       ~ Switch On State:                       Apply
      * SC Route 0: 4000
      * SC Route 1: FE00

   ~ [Routing Entry_4] ~  
    * Type: APDU Pattern-based routing entry (04)
    * Len: 6
    * Val: 800100A4FFFF
      * Route: 80 (HCI-NFCEE) (80)
      * Power State: 00000001 (01)
       ~ Screen Off lock (Sub-State 3):     Not apply
       ~ Screen On lock (Sub-State 2):      Not apply
       ~ Screen off unlock (Sub-State 1):   Not apply
       ~ Battery Off State:                 Not apply
       ~ Switch Off State:                  Not apply
       ~ Switch On State:                       Apply
      * Reference data: 00A4
      * Mask: FFFF
#end
```

- Raw（AID 只有 1 octet，AID 不會被印出）：`21 01 07 00 01 02 03 00 01 A0`

```text
  << RF_SET_LISTEN_MODE_ROUTING_CMD >>  
  * More: Last Message (00)
  * Number of Routing Entries: 1 (01)

   ~ [Routing Entry_0] ~  
    * Type: AID-based routing entry (02)
    * Len: 3
    * Val: 0001A0
      * Route: DH-NFCEE  (00)
      * Power State: 00000001 (01)
       ~ Screen Off lock (Sub-State 3):     Not apply
       ~ Screen On lock (Sub-State 2):      Not apply
       ~ Screen off unlock (Sub-State 1):   Not apply
       ~ Battery Off State:                 Not apply
       ~ Switch Off State:                  Not apply
       ~ Switch On State:                       Apply
      * AID: A0
#end
```

### 實作備註
見 [共用結構 A 的實作備註](#共用結構-a-listen_mode_routing_info)（AID 長度條件、SC Route 標籤索引、APDU 只印第 1 octet 三項皆已於 2026-10 修正）。

---

<a id="rf_set_listen_mode_routing_rsp"></a><a id="RF_SET_LISTEN_MODE_ROUTING_RSP"></a>
## RF_SET_LISTEN_MODE_ROUTING_RSP  (`41 01`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x01 / RSP |
| Handler | [`RF_Management.py:216`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L216) `RF_SET_LISTEN_MODE_ROUTING_RSP` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |

### 範例
- Raw：`41 01 01 00`

```text
  << RF_SET_LISTEN_MODE_ROUTING_RSP >>  
  * Status: STATUS_OK (00)
#end
```

---

<a id="rf_get_listen_mode_routing_cmd"></a><a id="RF_GET_LISTEN_MODE_ROUTING_CMD"></a>
## RF_GET_LISTEN_MODE_ROUTING_CMD  (`21 02`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x02 / CMD |
| Handler | [`RF_Management.py:232`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L232) `RF_GET_LISTEN_MODE_ROUTING_CMD` |

### Payload 格式
無 payload（Empty）。Handler 印出置中的 `(Empty)`，回傳 0。

### 範例
- Raw：`21 02 00`

```text
  << RF_GET_LISTEN_MODE_ROUTING_CMD >>  
         (Empty)         
#end
```

---

<a id="rf_get_listen_mode_routing_rsp"></a><a id="RF_GET_LISTEN_MODE_ROUTING_RSP"></a>
## RF_GET_LISTEN_MODE_ROUTING_RSP  (`41 02`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x02 / RSP |
| Handler | [`RF_Management.py:245`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L245) `RF_GET_LISTEN_MODE_ROUTING_RSP` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |

### 範例
- Raw：`41 02 01 00`

```text
  << RF_GET_LISTEN_MODE_ROUTING_RSP >>  
  * Status: STATUS_OK (00)
#end
```

### 實作備註
- docstring 標題寫成 `[RF_SET_LISTEN_MODE_ROUTING_RSP]`（複製貼上的筆誤），不影響執行。

---

<a id="rf_get_listen_mode_routing_ntf"></a><a id="RF_GET_LISTEN_MODE_ROUTING_NTF"></a>
## RF_GET_LISTEN_MODE_ROUTING_NTF  (`61 02`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x02 / NTF |
| Handler | [`RF_Management.py:261`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L261) `RF_GET_LISTEN_MODE_ROUTING_NTF` |

### Payload 格式
與 [RF_SET_LISTEN_MODE_ROUTING_CMD](#rf_set_listen_mode_routing_cmd--21-01) 相同，直接呼叫 [`LISTEN_MODE_ROUTING_INFO`](#共用結構-a-listen_mode_routing_info)。

| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | More | 1 | `tbl_more`（見 [Tables](Tables.md#tbl_more)） |
| 2 | Number of Routing Entries | 1 (n) | 十進位 |
| 3 | Routing Entry [1..n]（TLV） | x+2 | 見共用結構 A |

### 範例
- Raw：`61 02 13 01 02 00 03 00 11 02 42 0A 10 3F A0 00 00 01 51 00 00 00`

```text
  << RF_GET_LISTEN_MODE_ROUTING_NTF >>  
  * More: More Message(s) to follow (01)
  * Number of Routing Entries: 2 (02)

   ~ [Routing Entry_0] ~  
    * Type: Technology-based routing entry (00)
    * Len: 3
    * Val: 001102
      * Route: DH-NFCEE  (00)
      * Power State: 00010001 (11)
       ~ Screen Off lock (Sub-State 3):     Not apply
       ~ Screen On lock (Sub-State 2):          Apply
       ~ Screen off unlock (Sub-State 1):   Not apply
       ~ Battery Off State:                 Not apply
       ~ Switch Off State:                  Not apply
       ~ Switch On State:                       Apply
      * Technology: NFC_RF_TECHNOLOGY_F (02)

   ~ [Routing Entry_1] ~  
    * Type: AID-based routing entry (42)
     ~ Routing is blocked for the power modes where it is not supported.
    * Len: 10
    * Val: 103FA000000151000000
      * Route: 10 (NFCEE) (10)
      * Power State: 00111111 (3F)
       ~ Screen Off lock (Sub-State 3):         Apply
       ~ Screen On lock (Sub-State 2):          Apply
       ~ Screen off unlock (Sub-State 1):       Apply
       ~ Battery Off State:                     Apply
       ~ Switch Off State:                      Apply
       ~ Switch On State:                       Apply
      * AID: A000000151000000
#end
```

---

<a id="rf_discover_cmd"></a><a id="RF_DISCOVER_CMD"></a>
## RF_DISCOVER_CMD  (`21 03`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x03 / CMD |
| Handler | [`RF_Management.py:268`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L268) `RF_DISCOVER_CMD` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Number of Configurations | 1 (n) | 十進位 |
| 2 | Configuration [1..n] | 2 | |
| ﹂ | RF Technology and Mode | 1 | `tbl_rf_tech_mode`（見 [Tables](Tables.md#tbl_rf_tech_mode)） |
| ﹂ | Discovery Frequency | 1 | 程式內判斷：`00` 或 > `0A`（10）印 `RFU`，否則印十進位值 |

### 範例
- Raw：`21 03 0B 05 00 01 01 01 02 0A 80 01 06 0B`

```text
  << RF_DISCOVER_CMD >>  
  * Number of Configs: 5 (05)

   ~ [Config_0] ~  
    * Mode: A_PASSIVE_POLL (00)
    * Discovery Freq: 1

   ~ [Config_1] ~  
    * Mode: B_PASSIVE_POLL (01)
    * Discovery Freq: 1

   ~ [Config_2] ~  
    * Mode: F_PASSIVE_POLL (02)
    * Discovery Freq: 10

   ~ [Config_3] ~  
    * Mode: A_PASSIVE_LISTEN (80)
    * Discovery Freq: 1

   ~ [Config_4] ~  
    * Mode: V_PASSIVE_POLL (06)
    * Discovery Freq: RFU
#end
```

### 實作備註
- Discovery Frequency 的 `02`–`0A` 依程式註解只適用於 Poll Mode，但程式不分 Poll/Listen 一律接受。
- ✅ 已修正（2026-10）：RF Technology and Mode 改用 `lookup`，範圍鍵（`70-7F`、`F0-FF` 等）顯示表中文字。

---

<a id="rf_discover_rsp"></a><a id="RF_DISCOVER_RSP"></a>
## RF_DISCOVER_RSP  (`41 03`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x03 / RSP |
| Handler | [`RF_Management.py:313`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L313) `RF_DISCOVER_RSP` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |

### 範例
- Raw：`41 03 01 00`

```text
  << RF_DISCOVER_RSP >>  
  * Status: STATUS_OK (00)
#end
```

---

<a id="rf_discover_ntf"></a><a id="RF_DISCOVER_NTF"></a>
## RF_DISCOVER_NTF  (`61 03`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x03 / NTF |
| Handler | [`RF_Management.py:502`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L502) `RF_DISCOVER_NTF` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | RF Discovery ID | 1 | `tbl_rf_dis_id.get(id, id)`（見 [Tables](Tables.md#tbl_rf_dis_id)）：只有 `00`、`FF` 會顯示 `RFU`，其他值直接印原值 |
| 2 | RF Protocol | 1 | `tbl_rf_proto`（見 [Tables](Tables.md#tbl_rf_proto)） |
| 3 | RF Technology and Mode | 1 | `tbl_rf_tech_mode`（見 [Tables](Tables.md#tbl_rf_tech_mode)） |
| 4 | Length of RF Technology Specific Parameters | 1 (n) | 十進位 |
| 5 | RF Technology Specific Parameters | n | 交給 [`RF_TECH_SPEC_PARA`](#共用結構-b-rf_tech_spec_para)，依欄位 3 的 hex code 分支（見下），讀取以 n 為界 |
| 6 | Notification Type | 1 | 程式內判斷：`00` Last NTF、`01` Last NTF (due to NFCC reaching its resource limit)、`02` More NTF to follow，其他 `RFU` |

**RF Technology Specific Parameters 依 RF Technology and Mode 的格式**（完整定義見[共用結構 B](#共用結構-b-rf_tech_spec_para)）：

| RF Technology and Mode | 參數格式 |
|---|---|
| `00` A_PASSIVE_POLL | SENS_RES(2) + NFCID1 Len(1) + NFCID1(l) + SEL_RES Len(1) + SEL_RES(l) + HRx Len(1) + HRx(l) |
| `01` B_PASSIVE_POLL | SENSB_RES Len(1) + SENSB_RES(l) |
| `02` F_PASSIVE_POLL | Bit Rate(1) + SENSF_RES Len(1) + SENSF_RES(l) |
| `06` V_PASSIVE_POLL | RES_FLAG(1) + DSFID(1) + UID(8) |
| `03` ACTIVE_POLL | ATR_RES Len(1) + ATR_RES(n) |
| `80` A_PASSIVE_LISTEN | 無 |
| `81` B_PASSIVE_LISTEN | SENSB_REQ Command(1) |
| `82` F_PASSIVE_LISTEN | Local NFCID2 Len(1) + Local NFCID2(l) |
| `83` ACTIVE_LISTEN | ATR_REQ Len(1) + ATR_REQ(n) |
| 其他 | 整段印 `Proprietary parameters` |

### 範例
- NFC-A Poll（ISO-DEP）— Raw：`61 03 12 01 04 00 0D 44 00 07 04 11 22 33 44 55 66 01 20 00 02`

```text
  << RF_DISCOVER_NTF >>  
  * RF Discovery ID: 01
  * RF Protocol: ISO-DEP (04)
  * Mode: A_PASSIVE_POLL (00)
  * Len of RF Tech Specific Params: 13
  * SENS_RES Response: 4400
  * NFCID1 Len: 7
  * NFCID1: 04112233445566
  * SEL_RES Rsp Len: 1
  * SEL_RES Rsp: 20
  * HRx Len: 0
  * NTF Type: More NTF to follow (02)
#end
```

- NFC-A Poll（T1T，含 HRx）— Raw：`61 03 11 02 01 00 0C 0C 00 04 11 22 33 44 01 00 02 11 00 02`

```text
  << RF_DISCOVER_NTF >>  
  * RF Discovery ID: 02
  * RF Protocol: T1T (01)
  * Mode: A_PASSIVE_POLL (00)
  * Len of RF Tech Specific Params: 12
  * SENS_RES Response: 0C00
  * NFCID1 Len: 4
  * NFCID1: 11223344
  * SEL_RES Rsp Len: 1
  * SEL_RES Rsp: 00
  * HRx Len: 2
  * HRx: 1100
  * NTF Type: More NTF to follow (02)
#end
```

- NFC-B Poll — Raw：`61 03 11 03 04 01 0C 0B 50 11 22 33 44 00 00 00 00 71 81 02`

```text
  << RF_DISCOVER_NTF >>  
  * RF Discovery ID: 03
  * RF Protocol: ISO-DEP (04)
  * Mode: B_PASSIVE_POLL (01)
  * Len of RF Tech Specific Params: 12
  * SENSB_RES Rsp Len: 11
  * SENSB_RES Rsp: 5011223344000000007181
  * NTF Type: More NTF to follow (02)
#end
```

- NFC-F Poll — Raw：`61 03 19 04 03 02 14 01 12 01 01 FE 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F 02`

```text
  << RF_DISCOVER_NTF >>  
  * RF Discovery ID: 04
  * RF Protocol: T3T (03)
  * Mode: F_PASSIVE_POLL (02)
  * Len of RF Tech Specific Params: 20
  * Bit Rate: 212 kbps
  * SENSF_RES Rsp Len: 18
  * SENSF_RES Rsp: 0101FE0102030405060708090A0B0C0D0E0F
  * NTF Type: More NTF to follow (02)
#end
```

- NFC-V Poll — Raw：`61 03 0F 05 06 06 0A 00 00 E0 04 01 00 00 00 00 01 01`

```text
  << RF_DISCOVER_NTF >>  
  * RF Discovery ID: 05
  * RF Protocol: T5T (06)
  * Mode: V_PASSIVE_POLL (06)
  * Len of RF Tech Specific Params: 10
  * RES_FLAG: 00
  * DSFID: 00
  * UID: E004010000000001
  * NTF Type: Last NTF (due to NFCC reaching its resource limit) (01)
#end
```

- ACTIVE_POLL — Raw：`61 03 0A 06 05 03 05 04 D5 01 AA BB 00`

```text
  << RF_DISCOVER_NTF >>  
  * RF Discovery ID: 06
  * RF Protocol: NFC-DEP (05)
  * Mode: ACTIVE_POLL (03)
  * Len of RF Tech Specific Params: 5
  * ATR_RES Rsp Len: 4
  * ATR_RES Rsp: D501AABB
  * NTF Type: Last NTF (00)
#end
```

- Proprietary（Mode `70`、Protocol `80`）— Raw：`61 03 07 07 80 70 02 AA BB 00`

```text
  << RF_DISCOVER_NTF >>  
  * RF Discovery ID: 07
  * RF Protocol: For proprietary use (80)
  * Mode: Reserved for Proprietary Technologies in Poll Mode (70)
  * Len of RF Tech Specific Params: 2
  * Proprietary parameters: AABB
  * NTF Type: Last NTF (00)
#end
```

（Listen 模式的 RF Technology Specific Parameters 範例見 [RF_INTF_ACTIVATED_NTF](#rf_intf_activated_ntf--61-05)，兩者使用同一個 `RF_TECH_SPEC_PARA`。）

### 實作備註
- RF Discovery ID 查詢 `tbl_rf_dis_id.get(id, id)` 不使用範圍鍵 `01-FF`，所以有效 ID 只會印出原值（例如 `01`）；`00` 會印 `RFU`（已實測）。
- ✅ 已修正（2026-10）：RF Protocol `80`、Mode `70` 經 `lookup` 範圍鍵顯示 `For proprietary use` / `Reserved for Proprietary Technologies in Poll Mode`；Specific Parameters 仍進入 `Proprietary parameters` 分支。
- ✅ 已修正（2026-10）：Length = 0 但 Mode 需要固定欄位時，不再丟 `ValueError`，改印 `* Error: RF Technology Specific Parameters: Payload too short: need 2 byte(s) for SENS_RES Response, 0 left` 後繼續解析 Notification Type。

---

<a id="rf_discover_select_cmd"></a><a id="RF_DISCOVER_SELECT_CMD"></a>
## RF_DISCOVER_SELECT_CMD  (`21 04`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x04 / CMD |
| Handler | [`RF_Management.py:551`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L551) `RF_DISCOVER_SELECT_CMD` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | RF Discovery ID | 1 | `tbl_rf_dis_id.get(id, id)`（見 [Tables](Tables.md#tbl_rf_dis_id)） |
| 2 | RF Protocol | 1 | `tbl_rf_proto`（見 [Tables](Tables.md#tbl_rf_proto)） |
| 3 | RF Interface | 1 | `tbl_rf_if`（見 [Tables](Tables.md#tbl_rf_if)） |

### 範例
- Raw：`21 04 03 01 04 02`

```text
  << RF_DISCOVER_SELECT_CMD >>  
  * RF Discovery ID: 01
  * RF Protocol: ISO-DEP (04)
  * RF Interface: ISO-DEP (02)
#end
```

### 實作備註
- ✅ 已修正（2026-10）：RF Interface 那行括號內改印 `rf_if` 本身的 hex（範例為 `(02)`）。
- RF Discovery ID 仍用 `tbl_rf_dis_id.get(id, id)`，`01`–`FE` 只印原值（同 RF_DISCOVER_NTF）。

---

<a id="rf_discover_select_rsp"></a><a id="RF_DISCOVER_SELECT_RSP"></a>
## RF_DISCOVER_SELECT_RSP  (`41 04`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x04 / RSP |
| Handler | [`RF_Management.py:577`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L577) `RF_DISCOVER_SELECT_RSP` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |

### 範例
- Raw：`41 04 01 00`

```text
  << RF_DISCOVER_SELECT_RSP >>  
  * Status: STATUS_OK (00)
#end
```

---

<a id="rf_intf_activated_ntf"></a><a id="RF_INTF_ACTIVATED_NTF"></a>
## RF_INTF_ACTIVATED_NTF  (`61 05`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x05 / NTF |
| Handler | [`RF_Management.py:593`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L593) `RF_INTF_ACTIVATED_NTF` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | RF Discovery ID | 1 | `tbl_rf_dis_id.get(id, id)`（見 [Tables](Tables.md#tbl_rf_dis_id)） |
| 2 | RF Interface | 1 | `tbl_rf_if`（見 [Tables](Tables.md#tbl_rf_if)） |
| 3 | RF Protocol | 1 | `tbl_rf_proto`（見 [Tables](Tables.md#tbl_rf_proto)） |
| 4 | Activation RF Technology and Mode | 1 | `tbl_rf_tech_mode`（見 [Tables](Tables.md#tbl_rf_tech_mode)） |
| 5 | Max Data Packet Payload Size | 1 | 十進位 + 原值 |
| 6 | Initial Number of Credits | 1 | `FF` → `Not used (FF)`；其他以 `int(x, 16)` 轉十進位 |
| 7 | Length of RF Technology Specific Parameters | 1 (l) | 十進位 |
| 8 | RF Technology Specific Parameters | l | 只在 l ≠ 0 時交給 [`RF_TECH_SPEC_PARA`](#共用結構-b-rf_tech_spec_para)，依欄位 4 的 hex code 分支、讀取以 l 為界（格式表見 [RF_DISCOVER_NTF](#rf_discover_ntf--61-03)） |
| 9 | Data Exchange RF Technology and Mode | 1 | `tbl_rf_tech_mode`（見 [Tables](Tables.md#tbl_rf_tech_mode)） |
| 10 | Data Exchange Transmit Bit Rate | 1 | `tbl_bit_rates`（見 [Tables](Tables.md#tbl_bit_rates)） |
| 11 | Data Exchange Receive Bit Rate | 1 | `tbl_bit_rates`（見 [Tables](Tables.md#tbl_bit_rates)） |
| 12 | Length of Activation Parameters | 1 (n) | 十進位 |
| 13 | Activation Parameters | n | n = 0 時不讀任何內容；否則依欄位 2（RF Interface hex code）+ 欄位 4（Activation Mode hex code）分支，見下表。讀取以 n 為界：內部欄位不足印 `* Error: Activation Parameters: Payload too short: ...`；專屬分支解析完仍有剩餘時印 `* Remaining Activation Params: <hex>` |

#### Activation Parameters 分支（依 RF Interface × Activation RF Technology and Mode）

| RF Interface | Activation Mode | 規範表 | 欄位（依序） | 解析方式 |
|---|---|---|---|---|
| ISO-DEP (`02`) | A_PASSIVE_POLL (`00`) | Table 95 | RATS Response Length(1, l) + RATS Response(l) | 長度十進位 + 原值；內容印 hex |
| ISO-DEP | B_PASSIVE_POLL (`01`) | Table 96 | ATTRIB Response Length(1, l) + ATTRIB Response(l) | 同上 |
| ISO-DEP | A_PASSIVE_LISTEN (`80`) | Table 98 | RATS Command Param(1) | 印 hex |
| ISO-DEP | B_PASSIVE_LISTEN (`81`) | Table 99 | ATTRIB Command Length(1, l) + ATTRIB Command(l) | 長度十進位；內容印 hex |
| ISO-DEP | 其他 | — | Activation Parameters(n) | n > 0 時整段印 hex |
| NFC-DEP (`03`) | A_PASSIVE_POLL (`00`) 或 F_PASSIVE_POLL (`02`) | Table 102 | ATR_RES Response Length(1, l) + ATR_RES Response(l) + Data Exchange Length Reduction(1) | 長度十進位；ATR_RES 印 hex；LR 查 `tbl_len_rdu_val`（見 [Tables](Tables.md#tbl_len_rdu_val)），印 `Data Exchange LR: <text> (raw)` |
| NFC-DEP | A_PASSIVE_LISTEN (`80`) 或 F_PASSIVE_LISTEN (`82`) | Table 103 | ATR_REQ Command Length(1, l) + ATR_REQ Command(l) + Data Exchange Length Reduction(1) | 長度十進位；ATR_REQ 印 hex；LR 查 `tbl_len_rdu_val`（見 [Tables](Tables.md#tbl_len_rdu_val)） |
| NFC-DEP | 其他（包括 ACTIVE_POLL `03`、ACTIVE_LISTEN `83`） | — | Activation Parameters(n) | n > 0 時整段印 hex |
| 其他（NFCEE Direct `00`、Frame `01`、NDEF `06`、proprietary/RFU） | 任意 | — | Activation Parameters(n) | n > 0 時整段印 hex |

### 範例

**ISO-DEP / NFC-A Poll（Table 68 + Table 95）** — Raw：`61 05 1D 01 02 04 00 FF 01 0D 44 00 07 04 11 22 33 44 55 66 01 20 00 00 00 00 05 04 78 80 70 02`

```text
  << RF_INTF_ACTIVATED_NTF >>  
  * RF Discovery ID: 01
  * RF Interface: ISO-DEP (02)
  * RF Protocol: ISO-DEP (04)
  * Activation Mode: A_PASSIVE_POLL (00)
  * Max Data Size: 255 (FF)
  * Number of Credits: 1
  * Len of RF Tech Specific Params: 13
  * SENS_RES Response: 4400
  * NFCID1 Len: 7
  * NFCID1: 04112233445566
  * SEL_RES Rsp Len: 1
  * SEL_RES Rsp: 20
  * HRx Len: 0
  * Data Mode: A_PASSIVE_POLL (00)
  * Tx: 106 Kbit/s (00)
  * Rx: 106 Kbit/s (00)
  * Len of Activation Params: 5
  * RATS Rsp Len: 4 (04)
  * RATS Rsp: 78807002
#end
```

**ISO-DEP / NFC-B Poll（Table 70 + Table 96）** — Raw：`61 05 19 01 02 04 01 FF 01 0C 0B 50 11 22 33 44 00 00 00 00 71 81 01 00 00 02 01 00`

```text
  << RF_INTF_ACTIVATED_NTF >>  
  * RF Discovery ID: 01
  * RF Interface: ISO-DEP (02)
  * RF Protocol: ISO-DEP (04)
  * Activation Mode: B_PASSIVE_POLL (01)
  * Max Data Size: 255 (FF)
  * Number of Credits: 1
  * Len of RF Tech Specific Params: 12
  * SENSB_RES Rsp Len: 11
  * SENSB_RES Rsp: 5011223344000000007181
  * Data Mode: B_PASSIVE_POLL (01)
  * Tx: 106 Kbit/s (00)
  * Rx: 106 Kbit/s (00)
  * Len of Activation Params: 2
  * ATTRIB Rsp Len: 1 (01)
  * ATTRIB Rsp: 00
#end
```

**ISO-DEP / NFC-A Listen（Table 69 + Table 98）** — Raw：`61 05 0C 01 02 04 80 FF 01 00 80 00 00 01 81`

```text
  << RF_INTF_ACTIVATED_NTF >>  
  * RF Discovery ID: 01
  * RF Interface: ISO-DEP (02)
  * RF Protocol: ISO-DEP (04)
  * Activation Mode: A_PASSIVE_LISTEN (80)
  * Max Data Size: 255 (FF)
  * Number of Credits: 1
  * Len of RF Tech Specific Params: 0
  * Data Mode: A_PASSIVE_LISTEN (80)
  * Tx: 106 Kbit/s (00)
  * Rx: 106 Kbit/s (00)
  * Len of Activation Params: 1
  * RATS Cmd Param: 81
#end
```

**ISO-DEP / NFC-B Listen（Table 71 + Table 99）** — Raw：`61 05 16 01 02 04 81 FF 01 01 00 81 00 00 0A 09 1D 11 22 33 44 00 08 01 00`

```text
  << RF_INTF_ACTIVATED_NTF >>  
  * RF Discovery ID: 01
  * RF Interface: ISO-DEP (02)
  * RF Protocol: ISO-DEP (04)
  * Activation Mode: B_PASSIVE_LISTEN (81)
  * Max Data Size: 255 (FF)
  * Number of Credits: 1
  * Len of RF Tech Specific Params: 1
  * SENSB_REQ Command: 00
  * Data Mode: B_PASSIVE_LISTEN (81)
  * Tx: 106 Kbit/s (00)
  * Rx: 106 Kbit/s (00)
  * Len of Activation Params: 10
  * ATTRIB Cmd Len: 9
  * ATTRIB Cmd: 1D1122334400080100
#end
```

**NFC-DEP / NFC-A Poll（Table 68 + Table 102）** — Raw：`61 05 1D 01 03 05 00 FB 01 0D 44 00 07 04 11 22 33 44 55 66 01 20 00 00 00 00 05 04 D5 01 AA BB`

```text
  << RF_INTF_ACTIVATED_NTF >>  
  * RF Discovery ID: 01
  * RF Interface: NFC-DEP (03)
  * RF Protocol: NFC-DEP (05)
  * Activation Mode: A_PASSIVE_POLL (00)
  * Max Data Size: 251 (FB)
  * Number of Credits: 1
  * Len of RF Tech Specific Params: 13
  * SENS_RES Response: 4400
  * NFCID1 Len: 7
  * NFCID1: 04112233445566
  * SEL_RES Rsp Len: 1
  * SEL_RES Rsp: 20
  * HRx Len: 0
  * Data Mode: A_PASSIVE_POLL (00)
  * Tx: 106 Kbit/s (00)
  * Rx: 106 Kbit/s (00)
  * Len of Activation Params: 5
  * ATR_RES Rsp Len: 4
  * ATR_RES Rsp: D501AABB
  * Error: Activation Parameters: Payload too short: need 1 byte(s) for Data Exchange LR, 0 left
#end
```

**NFC-DEP / NFC-F Poll（Table 72 + Table 102）** — Raw：`61 05 24 01 03 05 02 FB 01 14 01 12 01 01 FE 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F 02 01 01 05 04 D5 01 AA BB`

```text
  << RF_INTF_ACTIVATED_NTF >>  
  * RF Discovery ID: 01
  * RF Interface: NFC-DEP (03)
  * RF Protocol: NFC-DEP (05)
  * Activation Mode: F_PASSIVE_POLL (02)
  * Max Data Size: 251 (FB)
  * Number of Credits: 1
  * Len of RF Tech Specific Params: 20
  * Bit Rate: 212 kbps
  * SENSF_RES Rsp Len: 18
  * SENSF_RES Rsp: 0101FE0102030405060708090A0B0C0D0E0F
  * Data Mode: F_PASSIVE_POLL (02)
  * Tx: 212 Kbit/s (01)
  * Rx: 212 Kbit/s (01)
  * Len of Activation Params: 5
  * ATR_RES Rsp Len: 4
  * ATR_RES Rsp: D501AABB
  * Error: Activation Parameters: Payload too short: need 1 byte(s) for Data Exchange LR, 0 left
#end
```

**NFC-DEP / NFC-A Listen（Table 69 + Table 103）** — Raw：`61 05 11 01 03 05 80 FB 01 00 80 00 00 06 04 D4 00 11 22 01`

```text
  << RF_INTF_ACTIVATED_NTF >>  
  * RF Discovery ID: 01
  * RF Interface: NFC-DEP (03)
  * RF Protocol: NFC-DEP (05)
  * Activation Mode: A_PASSIVE_LISTEN (80)
  * Max Data Size: 251 (FB)
  * Number of Credits: 1
  * Len of RF Tech Specific Params: 0
  * Data Mode: A_PASSIVE_LISTEN (80)
  * Tx: 106 Kbit/s (00)
  * Rx: 106 Kbit/s (00)
  * Len of Activation Params: 6
  * ATR_REQ Cmd Len: 4
  * ATR_REQ Cmd: D4001122
  * Data Exchange LR: 254 Bytes (01)
#end
```

**NFC-DEP / NFC-F Listen（Table 73 + Table 103）** — Raw：`61 05 1A 01 03 05 82 FB 01 09 08 02 FE 00 00 00 00 00 00 82 02 02 06 04 D4 00 11 22 03`

```text
  << RF_INTF_ACTIVATED_NTF >>  
  * RF Discovery ID: 01
  * RF Interface: NFC-DEP (03)
  * RF Protocol: NFC-DEP (05)
  * Activation Mode: F_PASSIVE_LISTEN (82)
  * Max Data Size: 251 (FB)
  * Number of Credits: 1
  * Len of RF Tech Specific Params: 9
  * Local NFCID2 Len: 8
  * Local NFCID2: 02FE000000000000
  * Data Mode: F_PASSIVE_LISTEN (82)
  * Tx: 424 Kbit/s (02)
  * Rx: 424 Kbit/s (02)
  * Len of Activation Params: 6
  * ATR_REQ Cmd Len: 4
  * ATR_REQ Cmd: D4001122
  * Data Exchange LR: 128 Bytes (03)
#end
```

**NFC-DEP / ACTIVE_POLL（Table 75，Activation Params 只印 raw）** — Raw：`61 05 15 01 03 05 03 FB 01 05 04 D5 01 AA BB 03 02 02 05 04 D5 01 AA BB`

```text
  << RF_INTF_ACTIVATED_NTF >>  
  * RF Discovery ID: 01
  * RF Interface: NFC-DEP (03)
  * RF Protocol: NFC-DEP (05)
  * Activation Mode: ACTIVE_POLL (03)
  * Max Data Size: 251 (FB)
  * Number of Credits: 1
  * Len of RF Tech Specific Params: 5
  * ATR_RES Rsp Len: 4
  * ATR_RES Rsp: D501AABB
  * Data Mode: ACTIVE_POLL (03)
  * Tx: 424 Kbit/s (02)
  * Rx: 424 Kbit/s (02)
  * Len of Activation Params: 5
  * Activation Params: 04D501AABB
#end
```

**NFC-DEP / ACTIVE_LISTEN（Table 76，Activation Params 只印 raw）** — Raw：`61 05 15 01 03 05 83 FB 01 05 04 D4 00 11 22 83 02 02 05 04 D4 00 11 22`

```text
  << RF_INTF_ACTIVATED_NTF >>  
  * RF Discovery ID: 01
  * RF Interface: NFC-DEP (03)
  * RF Protocol: NFC-DEP (05)
  * Activation Mode: ACTIVE_LISTEN (83)
  * Max Data Size: 251 (FB)
  * Number of Credits: 1
  * Len of RF Tech Specific Params: 5
  * ATR_REQ Cmd Len: 4
  * ATR_REQ Cmd: D4001122
  * Data Mode: ACTIVE_LISTEN (83)
  * Tx: 424 Kbit/s (02)
  * Rx: 424 Kbit/s (02)
  * Len of Activation Params: 5
  * Activation Params: 04D4001122
#end
```

**Frame / T2T / NFC-A Poll（無 Activation Params）** — Raw：`61 05 18 01 01 02 00 FF FF 0D 44 00 07 04 11 22 33 44 55 66 01 00 00 00 00 00 00`

```text
  << RF_INTF_ACTIVATED_NTF >>  
  * RF Discovery ID: 01
  * RF Interface: Frame (01)
  * RF Protocol: T2T (02)
  * Activation Mode: A_PASSIVE_POLL (00)
  * Max Data Size: 255 (FF)
  * Number of Credits: Not used (FF)
  * Len of RF Tech Specific Params: 13
  * SENS_RES Response: 4400
  * NFCID1 Len: 7
  * NFCID1: 04112233445566
  * SEL_RES Rsp Len: 1
  * SEL_RES Rsp: 00
  * HRx Len: 0
  * Data Mode: A_PASSIVE_POLL (00)
  * Tx: 106 Kbit/s (00)
  * Rx: 106 Kbit/s (00)
  * Len of Activation Params: 0
#end
```

**Frame / T3T / NFC-F Poll** — Raw：`61 05 1F 01 01 03 02 FF FF 14 01 12 01 01 FE 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F 02 01 01 00`

```text
  << RF_INTF_ACTIVATED_NTF >>  
  * RF Discovery ID: 01
  * RF Interface: Frame (01)
  * RF Protocol: T3T (03)
  * Activation Mode: F_PASSIVE_POLL (02)
  * Max Data Size: 255 (FF)
  * Number of Credits: Not used (FF)
  * Len of RF Tech Specific Params: 20
  * Bit Rate: 212 kbps
  * SENSF_RES Rsp Len: 18
  * SENSF_RES Rsp: 0101FE0102030405060708090A0B0C0D0E0F
  * Data Mode: F_PASSIVE_POLL (02)
  * Tx: 212 Kbit/s (01)
  * Rx: 212 Kbit/s (01)
  * Len of Activation Params: 0
#end
```

**Frame / T5T / NFC-V Poll** — Raw：`61 05 15 01 01 06 06 FF FF 0A 00 00 E0 04 01 00 00 00 00 01 06 20 20 00`

```text
  << RF_INTF_ACTIVATED_NTF >>  
  * RF Discovery ID: 01
  * RF Interface: Frame (01)
  * RF Protocol: T5T (06)
  * Activation Mode: V_PASSIVE_POLL (06)
  * Max Data Size: 255 (FF)
  * Number of Credits: Not used (FF)
  * Len of RF Tech Specific Params: 10
  * RES_FLAG: 00
  * DSFID: 00
  * UID: E004010000000001
  * Data Mode: V_PASSIVE_POLL (06)
  * Tx: 26 Kbit/s (20)
  * Rx: 26 Kbit/s (20)
  * Len of Activation Params: 0
#end
```

**NDEF Interface（Activation Params 只印 raw）** — Raw：`61 05 1A 01 06 07 00 FF 01 0D 44 00 07 04 11 22 33 44 55 66 01 00 00 00 00 00 02 AA BB`

```text
  << RF_INTF_ACTIVATED_NTF >>  
  * RF Discovery ID: 01
  * RF Interface: NDEF (06)
  * RF Protocol: NDEF (07)
  * Activation Mode: A_PASSIVE_POLL (00)
  * Max Data Size: 255 (FF)
  * Number of Credits: 1
  * Len of RF Tech Specific Params: 13
  * SENS_RES Response: 4400
  * NFCID1 Len: 7
  * NFCID1: 04112233445566
  * SEL_RES Rsp Len: 1
  * SEL_RES Rsp: 00
  * HRx Len: 0
  * Data Mode: A_PASSIVE_POLL (00)
  * Tx: 106 Kbit/s (00)
  * Rx: 106 Kbit/s (00)
  * Len of Activation Params: 2
  * Activation Params: AABB
#end
```

**Initial Number of Credits = `0A`（十六進位解析）** — Raw：`61 05 18 01 01 02 00 FF 0A 0D 44 00 07 04 11 22 33 44 55 66 01 00 00 00 00 00 00`

```text
  << RF_INTF_ACTIVATED_NTF >>  
  * RF Discovery ID: 01
  * RF Interface: Frame (01)
  * RF Protocol: T2T (02)
  * Activation Mode: A_PASSIVE_POLL (00)
  * Max Data Size: 255 (FF)
  * Number of Credits: 10
  * Len of RF Tech Specific Params: 13
  * SENS_RES Response: 4400
  * NFCID1 Len: 7
  * NFCID1: 04112233445566
  * SEL_RES Rsp Len: 1
  * SEL_RES Rsp: 00
  * HRx Len: 0
  * Data Mode: A_PASSIVE_POLL (00)
  * Tx: 106 Kbit/s (00)
  * Rx: 106 Kbit/s (00)
  * Len of Activation Params: 0
#end
```

### 實作備註
- ✅ 已修正（2026-10）：Initial Number of Credits 改用 `int(x, 16)`，`0A` 印 `10`、`10` 印 `16`（見上方範例）。
- ✅ 已修正（2026-10）：Activation Parameters 以宣告長度 n 為界：n = 0 時不讀任何內容；內部欄位超出 n 時印 `* Error: Activation Parameters: Payload too short: ...`；解析完仍有剩餘時印 `* Remaining Activation Params: <hex>`。
- ✅ 已修正（2026-10）：NFC-DEP Poll（Table 102）也在 ATR_RES 之後讀 1 octet 的 Data Exchange Length Reduction（`tbl_len_rdu_val`），與 Listen（Table 103）一致；資料不足時印 Error 行（見 NFC-DEP / NFC-A Poll 範例）。
- RF Technology Specific Parameters 只在 Length ≠ 0 時才呼叫 `RF_TECH_SPEC_PARA`，所以 A_PASSIVE_LISTEN 搭配 Length 0 時不會印 `There is no RF Technology Specific Parameters`（RF_DISCOVER_NTF 則會印）。
- ACTIVE_POLL / ACTIVE_LISTEN 搭配 NFC-DEP 時沒有專屬的 Activation Parameters 分支，只會印 raw。
- ✅ 已修正（2026-10）：RF Interface、RF Protocol、Mode、Bit Rate 改用 `lookup`，proprietary 範圍值（`80-FE` 等）顯示表中文字；Activation Parameters 改依 hex code 分支（proprietary interface 仍走 raw 分支）。
- RF Discovery ID 仍用 `tbl_rf_dis_id.get(id, id)`，`01`–`FE` 只印原值（同 RF_DISCOVER_NTF）。

---

<a id="rf_deactivate_cmd"></a><a id="RF_DEACTIVATE_CMD"></a>
## RF_DEACTIVATE_CMD  (`21 06`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x06 / CMD |
| Handler | [`RF_Management.py:675`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L675) `RF_DEACTIVATE_CMD` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Deactivation Type | 1 | `tbl_deactivate_type`（見 [Tables](Tables.md#tbl_deactivate_type)） |

### 範例
- Raw：`21 06 01 03`

```text
  << RF_DEACTIVATE_CMD >>  
  * Deactivation Type: Discovery (03)
#end
```

---

<a id="rf_deactivate_rsp"></a><a id="RF_DEACTIVATE_RSP"></a>
## RF_DEACTIVATE_RSP  (`41 06`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x06 / RSP |
| Handler | [`RF_Management.py:691`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L691) `RF_DEACTIVATE_RSP` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |

### 範例
- Raw：`41 06 01 00`

```text
  << RF_DEACTIVATE_RSP >>  
  * Status: STATUS_OK (00)
#end
```

---

<a id="rf_deactivate_ntf"></a><a id="RF_DEACTIVATE_NTF"></a>
## RF_DEACTIVATE_NTF  (`61 06`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x06 / NTF |
| Handler | [`RF_Management.py:707`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L707) `RF_DEACTIVATE_NTF` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Deactivation Type | 1 | `tbl_deactivate_type`（見 [Tables](Tables.md#tbl_deactivate_type)） |
| 2 | Deactivation Reason | 1 | `tbl_deactivate_reason`（見 [Tables](Tables.md#tbl_deactivate_reason)） |

### 範例
- Raw：`61 06 02 01 01`

```text
  << RF_DEACTIVATE_NTF >>  
  * Deactivation Type: Sleep Mode (01)
  * Deactivation Reason: Endpoint_Request (01)
#end
```

---

<a id="rf_field_info_ntf"></a><a id="RF_FIELD_INFO_NTF"></a>
## RF_FIELD_INFO_NTF  (`61 07`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x07 / NTF |
| Handler | [`RF_Management.py:728`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L728) `RF_FIELD_INFO_NTF` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | RF Field Status | 1 | `tbl_rf_field_status`（見 [Tables](Tables.md#tbl_rf_field_status)）；查不到時印 `RFU (raw)` |

### 範例
- Raw：`61 07 01 01`

```text
  << RF_FIELD_INFO_NTF >>  
  * RF Field Status: Operating field generated by Remote NFC Endpoint.
#end
```

- Raw（未定義值 `02`）：`61 07 01 02`

```text
  << RF_FIELD_INFO_NTF >>  
  * RF Field Status: RFU (02)
#end
```

### 實作備註
- ✅ 已修正（2026-10）：未定義值改印 `RFU (xx)`（見上方 `02` 範例）。

---

<a id="rf_t3t_polling_cmd"></a><a id="RF_T3T_POLLING_CMD"></a>
## RF_T3T_POLLING_CMD  (`21 08`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x08 / CMD |
| Handler | [`RF_Management.py:747`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L747) `RF_T3T_POLLING_CMD` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | SENSF_REQ_PARAMS | 4 | 整段印 hex，不拆 SC / RC / TSN |

### 範例
- Raw：`21 08 04 FF FF 01 0F`

```text
  << RF_T3T_POLLING_CMD >>  
  * SENSF_REQ_PARAMS: FFFF010F
#end
```

---

<a id="rf_t3t_polling_rsp"></a><a id="RF_T3T_POLLING_RSP"></a>
## RF_T3T_POLLING_RSP  (`41 08`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x08 / RSP |
| Handler | [`RF_Management.py:763`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L763) `RF_T3T_POLLING_RSP` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |

### 範例
- Raw：`41 08 01 00`

```text
  << RF_T3T_POLLING_RSP >>  
  * Status: STATUS_OK (00)
#end
```

---

<a id="rf_t3t_polling_ntf"></a><a id="RF_T3T_POLLING_NTF"></a>
## RF_T3T_POLLING_NTF  (`61 08`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x08 / NTF |
| Handler | [`RF_Management.py:779`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L779) `RF_T3T_POLLING_NTF` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |
| 2 | Number of Responses | 1 (n) | 十進位 + 原值 |
| 3 | Responses [1..n] | m+1 | |
| ﹂ | Length | 1 (m) | 十進位 + 原值 |
| ﹂ | SENSF_RES | m | 整段印 hex（`SENSF_RES_PARSER` 已被註解掉） |

### 範例
- Raw：`61 08 28 00 02 13 01 01 02 03 04 05 06 07 08 C0 C1 C2 C3 C4 C5 C6 C7 12 FC 11 01 11 12 13 14 15 16 17 18 C0 C1 C2 C3 C4 C5 C6 C7`

```text
  << RF_T3T_POLLING_NTF >>  
  * Status: STATUS_OK (00)
  * Number of Rsp: 2 (02)

   ~ [Rsp_0] ~  
    * Len: 19 (13)
    * SENSF_RES: 010102030405060708C0C1C2C3C4C5C6C712FC

   ~ [Rsp_1] ~  
    * Len: 17 (11)
    * SENSF_RES: 011112131415161718C0C1C2C3C4C5C6C7
#end
```

### 實作備註
- docstring 標題寫成 `[RF_T3T_POLLING_RSP]`（筆誤），不影響執行。

---

<a id="rf_nfcee_action_ntf"></a><a id="RF_NFCEE_ACTION_NTF"></a>
## RF_NFCEE_ACTION_NTF  (`61 09`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x09 / NTF |
| Handler | [`RF_Management.py:819`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L819) `RF_NFCEE_ACTION_NTF` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | NFCEE ID | 1 | 印原值，再加上 `tbl_nfcee_id` 的精確查詢結果與 `find_range_key` 範圍查詢結果（見 [Tables](Tables.md#tbl_nfcee_id)） |
| 2 | Trigger | 1 | `lookup(tbl_nfcee_ntf_trig, ...)`（見 [Tables](Tables.md#tbl_nfcee_ntf_trig)），範圍鍵 `06-0F`/`10-7F`/`80-FF` 可命中；分支仍依原始 Trigger 值 |
| 3 | Supporting Data Length | 1 (n) | 十進位 |
| 4 | Supporting Data | n | 依 Trigger 解析，見下表 |

**Supporting Data 依 Trigger 的格式**

| Trigger | 意義 | Supporting Data 解析 |
|---|---|---|
| `00` | [ISO/IEC_7816-4] SELECT command with an AID | `AID:` 印 hex |
| `01` | Protocol-based Route Selection | 整段（應為 1 octet）查 `tbl_rf_proto`（見 [Tables](Tables.md#tbl_rf_proto)） |
| `02` | Technology-based Route Selection | 整段查 `tbl_rf_tech`（見 [Tables](Tables.md#tbl_rf_tech)） |
| `03` | System Code-based Route Selection | `SC Route:` 印 hex |
| `04` | APDU Pattern-based Route Selection | 前 `n//2` octets 印 `Reference data:`，其餘（n 為奇數時多 1 octet）印 `Mask:` |
| `05` | Forced NFCEE Routing | 整段查 `tbl_rf_tech` |
| `06-0F`、`10-7F`、`80-FF` | RFU / Application specific / RFU | n > 0 時印 `Data: <hex>` |

### 範例
- Trigger `00`（AID）— Raw：`61 09 0A 80 00 07 A0 00 00 00 03 10 10`

```text
  << RF_NFCEE_ACTION_NTF >>  
  * NFCEE ID: 80  (HCI-NFCEE)
  * Trigger: [ISO/IEC_7816-4] SELECT command with an AID (00)
  * Supporting Data Len: 7
  * Supporting Data: 
    * AID: A0000000031010
#end
```

- Trigger `01`（Protocol）— Raw：`61 09 04 02 01 01 04`

```text
  << RF_NFCEE_ACTION_NTF >>  
  * NFCEE ID: 02  (Static IDs)
  * Trigger: Protocol-based Route Selection Process (ref to Table 133) (01)
  * Supporting Data Len: 1
  * Supporting Data: 
    * RF Protocol: ISO-DEP (04)
#end
```

- Trigger `02`（Technology）— Raw：`61 09 04 02 02 01 01`

```text
  << RF_NFCEE_ACTION_NTF >>  
  * NFCEE ID: 02  (Static IDs)
  * Trigger: Technology-based Route Selection Process (ref to Table 130) (02)
  * Supporting Data Len: 1
  * Supporting Data: 
    * RF Technology: NFC_RF_TECHNOLOGY_B (01)
#end
```

- Trigger `03`（System Code）— Raw：`61 09 05 02 03 02 40 00`

```text
  << RF_NFCEE_ACTION_NTF >>  
  * NFCEE ID: 02  (Static IDs)
  * Trigger: System Code-based Route Selection Process (03)
  * Supporting Data Len: 2
  * Supporting Data: 
    * SC Route: 4000
#end
```

- Trigger `04`（APDU Pattern）— Raw：`61 09 07 02 04 04 00 A4 FF FF`

```text
  << RF_NFCEE_ACTION_NTF >>  
  * NFCEE ID: 02  (Static IDs)
  * Trigger: TAPDU Pattern-based Route Selection Process (as defined in Table 58) (04)
  * Supporting Data Len: 4
  * Supporting Data: 
    * Reference data: 00A4
    * Mask: FFFF
#end
```

- Trigger `05`（Forced NFCEE Routing）— Raw：`61 09 04 02 05 01 00`

```text
  << RF_NFCEE_ACTION_NTF >>  
  * NFCEE ID: 02  (Static IDs)
  * Trigger: Forced NFCEE Routing is used (See Table 130) (05)
  * Supporting Data Len: 1
  * Supporting Data: 
    * RF Technology: NFC_RF_TECHNOLOGY_A (00)
#end
```

- Trigger `10`（Application specific）— Raw：`61 09 05 10 10 02 AA BB`

```text
  << RF_NFCEE_ACTION_NTF >>  
  * NFCEE ID: 10  (NFCEE)
  * Trigger: Application specific (10)
  * Supporting Data Len: 2
  * Supporting Data: 
    * Data: AABB
#end
```

### 實作備註
- ✅ 已修正（2026-10）：Trigger `04` 以 `(n//2)*2` 個 hex 字元切開，前 n//2 octets 為 Reference data、其餘為 Mask，不再丟 `TypeError`。
- ✅ 已修正（2026-10）：Trigger 落在範圍鍵（`06-0F`、`10-7F`、`80-FF`）時，Supporting Data 內容（n > 0）以 `Data: <hex>` 印出。
- Trigger `01`/`02`/`05` 用整段 `data_val` 查表；若長度不是 1 octet 會顯示 `RFU`。

---

<a id="rf_nfcee_discovery_req_ntf"></a><a id="RF_NFCEE_DISCOVERY_REQ_NTF"></a>
## RF_NFCEE_DISCOVERY_REQ_NTF  (`61 0A`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x0A / NTF |
| Handler | [`RF_Management.py:868`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L868) `RF_NFCEE_DISCOVERY_REQ_NTF` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Number of Information Entries | 1 (n) | 十進位 |
| 2 | Information Entry [1..n]（TLV） | x+2 | Value 以 x 為界解析，不足時印 `* Error: Information Entry Value: Payload too short: ...` |
| ﹂ | Type | 1 | `lookup(tbl_nfcee_disc_req_type, ...)`（見 [Tables](Tables.md#tbl_nfcee_disc_req_type)），範圍鍵 `02-7F`/`80-FF` 可命中；只印名稱不印原值 |
| ﹂ | Length | 1 (x) | 十進位 |
| ﹂ | Value | x | 先整段印 `Val:`；Type 為 `00`/`01` 時再拆解（見下） |

**Type `00`（Added to list）/ `01`（Removed from list）的 Value**

| # | 欄位 | 長度 | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | NFCEE ID | 1 | 原值 + `tbl_nfcee_id` 精確查詢 + `find_range_key` 範圍查詢（見 [Tables](Tables.md#tbl_nfcee_id)） |
| 2 | RF Technology and Mode | 1 | `tbl_rf_tech_mode`（見 [Tables](Tables.md#tbl_rf_tech_mode)），`lookup`（含範圍鍵） |
| 3 | RF Protocol | 1 | `tbl_rf_proto`（見 [Tables](Tables.md#tbl_rf_proto)），`lookup`（含範圍鍵） |

其他 Type 只印 `Val:` 原值。

### 範例
- Raw：`61 0A 0F 03 00 03 80 00 04 01 03 10 81 04 80 02 AA BB`

```text
  << RF_NFCEE_DISCOVERY_REQ_NTF >>  
  * Number Of Info Entries: 3

   ~ [Info Entry_0] ~  
    * Type: Added to list
    * Len: 3
    * Val: 800004
      * NFCEE: 80  (HCI-NFCEE)
      * Mode: A_PASSIVE_POLL (00)
      * RF Protocol: ISO-DEP (04)

   ~ [Info Entry_1] ~  
    * Type: Removed from list
    * Len: 3
    * Val: 108104
      * NFCEE: 10  (NFCEE)
      * Mode: B_PASSIVE_LISTEN (81)
      * RF Protocol: ISO-DEP (04)

   ~ [Info Entry_2] ~  
    * Type: For proprietary use
    * Len: 2
    * Val: AABB
#end
```

### 實作備註
- Type 欄位只印查表名稱，不附原始 hex。

---

<a id="rf_parameter_update_cmd"></a><a id="RF_PARAMETER_UPDATE_CMD"></a>
## RF_PARAMETER_UPDATE_CMD  (`21 0B`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x0B / CMD |
| Handler | [`RF_Management.py:919`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L919) `RF_PARAMETER_UPDATE_CMD` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Number of Parameters | 1 (n) | 十進位 + 原值 |
| 2 | RF Communication Parameter [1..n]（TLV） | x+2 | |
| ﹂ | ID | 1 | `tbl_rf_commu_para_id`（見 [Tables](Tables.md#tbl_rf_commu_para_id)） |
| ﹂ | Length | 1 (x) | 十進位 |
| ﹂ | Value | x | 先整段印 `Val:`，再依 ID 解析第 1 octet（見下）；x = 0 時只印空的 `Val:`，不再解析 |

**Value 依 ID 的解析**

| ID | 意義 | 解析方式 |
|---|---|---|
| `00` | RF Technology and Mode | 第 1 octet 查 `tbl_rf_tech_mode`（見 [Tables](Tables.md#tbl_rf_tech_mode)） |
| `01` | Transmit Bit Rate | 第 1 octet 查 `tbl_bit_rates`（見 [Tables](Tables.md#tbl_bit_rates)），標 `Tx` |
| `02` | Receive Bit Rate | 第 1 octet 查 `tbl_bit_rates`，標 `Rx` |
| `03` | NFC-B Data Exchange Configuration（Table 92） | 第 1 octet 拆 bit，見下表 |
| 其他 | — | 只印 `Val:` 原值 |

**ID `03` NFC-B Data Exchange Configuration bit 對應（程式內實作）**

| Bit | 欄位 |
|---|---|
| b7–b6 | Minimum TR0 |
| b5–b4 | Minimum TR1 |
| b3 | Suppression of EoS |
| b2 | Suppression of SoS |
| b1–b0 | Minimum TR3 |

### 範例
- Raw：`21 0B 0D 04 00 01 00 01 01 02 02 01 02 03 01 E5`

```text
  << RF_PARAMETER_UPDATE_CMD >>  
  * Number of Params: 4 (04)

   ~ [RF Communication 0] ~  
  * Type ID: RF Technology and Mode (coded as defined in Table 131) (00)
  * Len: 1
  * Val: 00
    * Mode: A_PASSIVE_POLL (00)

   ~ [RF Communication 1] ~  
  * Type ID: Transmit Bit Rate (coded as defined in Table 132) (01)
  * Len: 1
  * Val: 02
    * Tx: 424 Kbit/s (02)

   ~ [RF Communication 2] ~  
  * Type ID: Receive Bit Rate (coded as defined in Table 132) (02)
  * Len: 1
  * Val: 02
    * Rx: 424 Kbit/s (02)

   ~ [RF Communication 3] ~  
  * Type ID: NFC-B Data Exchange Configuration (coded as defined in Table 92) (03)
  * Len: 1
  * Val: E5
    * NFC-B Data Exchange Config: E5
     ~ Minimum TR0:      11
     ~ Minimum TR1:      10
     ~ Suppression of EoS: 0
     ~ Suppression of SoS: 1
     ~ Minimum TR3:      01
#end
```

### 實作備註
- ✅ 已修正（2026-10）：`tbl_rf_commu_para_id['01']`/`['02']` 的說明文字已改為 `coded as defined in Table 132`。
- ✅ 已修正（2026-10）：`tbl_rf_commu_para_id` 改用 `lookup`，`80`–`FF` 顯示 `Proprietary`。
- ✅ 已修正（2026-10）：Length = 0（空 Value）時只印 `Val:`，不再嘗試解析第 1 octet。
- 每個參數內的欄位縮排（`  * Type ID`）和外層相同，輸出排版上看不出巢狀層次。

---

<a id="rf_parameter_update_rsp"></a><a id="RF_PARAMETER_UPDATE_RSP"></a>
## RF_PARAMETER_UPDATE_RSP  (`41 0B`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x0B / RSP |
| Handler | [`RF_Management.py:984`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L984) `RF_PARAMETER_UPDATE_RSP` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |
| 2 | Number of Parameters | 1 (n) | 十進位 |
| 3 | RF Communication Parameter ID [1..n] | 1 | 每筆查 `tbl_rf_commu_para_id`（見 [Tables](Tables.md#tbl_rf_commu_para_id)） |

### 範例
- Raw：`41 0B 04 09 02 01 03`

```text
  << RF_PARAMETER_UPDATE_RSP >>  
  * Status: STATUS_INVALID_PARAM (09)
  * Number of Params: 2
  * RF Communication Param ID: 
  * Type ID 0: Transmit Bit Rate (coded as defined in Table 132) (01)
  * Type ID 1: NFC-B Data Exchange Configuration (coded as defined in Table 92) (03)
#end
```

---

<a id="rf_intf_ext_start_cmd"></a><a id="RF_INTF_EXT_START_CMD"></a>
## RF_INTF_EXT_START_CMD  (`21 0C`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x0C / CMD |
| Handler | [`RF_Management.py:1013`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L1013) `RF_INTF_EXT_START_CMD` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | RF Interface Extension | 1 | `tbl_rf_if_exten`（見 [Tables](Tables.md#tbl_rf_if_exten)） |
| 2 | Start Parameter Length | 1 (x) | 十進位 |
| 3 | Start Parameter | x | 印 hex（不依 extension 類型解析） |

### 範例
- Raw：`21 0C 03 01 01 0A`

```text
  << RF_INTF_EXT_START_CMD >>  
  * RF Interface Extension: LLCP Symmetry RF Interface Extension (01)
  * Start Param Len: 1
  * Start Param: 0A
#end
```

---

<a id="rf_intf_ext_start_rsp"></a><a id="RF_INTF_EXT_START_RSP"></a>
## RF_INTF_EXT_START_RSP  (`41 0C`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x0C / RSP |
| Handler | [`RF_Management.py:1040`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L1040) `RF_INTF_EXT_START_RSP` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |

### 範例
- Raw：`41 0C 01 00`

```text
  << RF_INTF_EXT_START_RSP >>  
  * Status: STATUS_OK (00)
#end
```

---

<a id="rf_intf_ext_stop_cmd"></a><a id="RF_INTF_EXT_STOP_CMD"></a>
## RF_INTF_EXT_STOP_CMD  (`21 0D`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x0D / CMD |
| Handler | [`RF_Management.py:1056`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L1056) `RF_INTF_EXT_STOP_CMD` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | RF Interface Extension | 1 | `tbl_rf_if_exten`（見 [Tables](Tables.md#tbl_rf_if_exten)） |
| 2 | Stop Parameter Length | 1 (x) | 十進位 |
| 3 | Stop Parameter | x | 印 hex（x = 0 時印空字串） |

### 範例
- Raw：`21 0D 02 00 00`

```text
  << RF_INTF_EXT_STOP_CMD >>  
  * RF Interface Extension: Frame Aggregated RF Interface Extension (00)
  * Stop Param Len: 0
  * Stop Param: 
#end
```

---

<a id="rf_intf_ext_stop_rsp"></a><a id="RF_INTF_EXT_STOP_RSP"></a>
## RF_INTF_EXT_STOP_RSP  (`41 0D`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x0D / RSP |
| Handler | [`RF_Management.py:1083`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L1083) `RF_INTF_EXT_STOP_RSP` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |

### 範例
- Raw：`41 0D 01 00`

```text
  << RF_INTF_EXT_STOP_RSP >>  
  * Status: STATUS_OK (00)
#end
```

---

<a id="rf_ext_agg_abort_cmd"></a><a id="RF_EXT_AGG_ABORT_CMD"></a>
## RF_EXT_AGG_ABORT_CMD  (`21 0E`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x0E / CMD |
| Handler | [`RF_Management.py:1099`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L1099) `RF_EXT_AGG_ABORT_CMD` |

### Payload 格式
無 payload（Empty）。

### 範例
- Raw：`21 0E 00`

```text
  << RF_EXT_AGG_ABORT_CMD >>  
         (Empty)         
#end
```

---

<a id="rf_ext_agg_abort_rsp"></a><a id="RF_EXT_AGG_ABORT_RSP"></a>
## RF_EXT_AGG_ABORT_RSP  (`41 0E`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x0E / RSP |
| Handler | [`RF_Management.py:1112`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L1112) `RF_EXT_AGG_ABORT_RSP` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |

### 範例
- Raw：`41 0E 01 00`

```text
  << RF_EXT_AGG_ABORT_RSP >>  
  * Status: STATUS_OK (00)
#end
```

---

<a id="rf_ndef_abort_cmd"></a><a id="RF_NDEF_ABORT_CMD"></a>
## RF_NDEF_ABORT_CMD  (`21 0F`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x0F / CMD |
| Handler | [`RF_Management.py:1128`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L1128) `RF_NDEF_ABORT_CMD` |

### Payload 格式
無 payload（Empty）。

### 範例
- Raw：`21 0F 00`

```text
  << RF_NDEF_ABORT_CMD >>  
         (Empty)         
#end
```

---

<a id="rf_ndef_abort_rsp"></a><a id="RF_NDEF_ABORT_RSP"></a>
## RF_NDEF_ABORT_RSP  (`41 0F`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x0F / RSP |
| Handler | [`RF_Management.py:1141`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L1141) `RF_NDEF_ABORT_RSP` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |

### 範例
- Raw：`41 0F 01 00`

```text
  << RF_NDEF_ABORT_RSP >>  
  * Status: STATUS_OK (00)
#end
```

---

<a id="rf_iso_dep_nak_presence_cmd"></a><a id="RF_ISO_DEP_NAK_PRESENCE_CMD"></a>
## RF_ISO_DEP_NAK_PRESENCE_CMD  (`21 10`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x10 / CMD |
| Handler | [`RF_Management.py:1157`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L1157) `RF_ISO_DEP_NAK_PRESENCE_CMD` |

### Payload 格式
無 payload（Empty）。

### 範例
- Raw：`21 10 00`

```text
  << RF_ISO_DEP_NAK_PRESENCE_CMD >>  
         (Empty)         
#end
```

---

<a id="rf_iso_dep_nak_presence_rsp"></a><a id="RF_ISO_DEP_NAK_PRESENCE_RSP"></a>
## RF_ISO_DEP_NAK_PRESENCE_RSP  (`41 10`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x10 / RSP |
| Handler | [`RF_Management.py:1170`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L1170) `RF_ISO_DEP_NAK_PRESENCE_RSP` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |

### 範例
- Raw：`41 10 01 00`

```text
  << RF_ISO_DEP_NAK_PRESENCE_RSP >>  
  * Status: STATUS_OK (00)
#end
```

---

<a id="rf_iso_dep_nak_presence_ntf"></a><a id="RF_ISO_DEP_NAK_PRESENCE_NTF"></a>
## RF_ISO_DEP_NAK_PRESENCE_NTF  (`61 10`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x10 / NTF |
| Handler | [`RF_Management.py:1186`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L1186) `RF_ISO_DEP_NAK_PRESENCE_NTF` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |

### 範例
- Raw：`61 10 01 00`

```text
  << RF_ISO_DEP_NAK_PRESENCE_NTF >>  
  * Status: STATUS_OK (00)
#end
```

---

<a id="rf_set_forced_nfcee_routing_cmd"></a><a id="RF_SET_FORCED_NFCEE_ROUTING_CMD"></a>
## RF_SET_FORCED_NFCEE_ROUTING_CMD  (`21 11`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x11 / CMD |
| Handler | [`RF_Management.py:1202`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L1202) `RF_SET_FORCED_NFCEE_ROUTING_CMD` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Forced NFCEE Routing State | 1 | 程式內判斷：`00` Disabled、`01` Enabled，其他印 `Error (xx)` |
| 2 | Forced NFCEE Value Field | 0 或 2 | 只在 State = `01` 時解析 |
| ﹂ | Forced NFCEE | 1 | 原值 + `tbl_nfcee_id` 精確查詢 + `find_range_key` 範圍查詢（見 [Tables](Tables.md#tbl_nfcee_id)） |
| ﹂ | Forced Power State | 1 | 印 8-bit 二進位，再對 bit5..bit0 查 `tbl_pwr_state`（見 [Tables](Tables.md#tbl_pwr_state)），1 = `Apply`、0 = `Not apply`（bit 對應同[共用結構 A](#共用結構-a-listen_mode_routing_info)） |

### 範例
- Disabled — Raw：`21 11 01 00`

```text
  << RF_SET_FORCED_NFCEE_ROUTING_CMD >>  
  * Forced NFCEE Routing State: Disabled
#end
```

- Enabled — Raw：`21 11 03 01 80 3B`

```text
  << RF_SET_FORCED_NFCEE_ROUTING_CMD >>  
  * Forced NFCEE Routing State: Enabled
  * Forced NFCEE: 80  (HCI-NFCEE)
    * Power State: 00111011 (3B)
     ~ Screen Off lock (Sub-State 3):Apply     
     ~ Screen On lock (Sub-State 2):Apply     
     ~ Screen off unlock (Sub-State 1):Apply     
     ~ Battery Off State:        Not apply 
     ~ Switch Off State:         Apply     
     ~ Switch On State:          Apply     
#end
```

- 不合法的 State — Raw：`21 11 01 02`

```text
  << RF_SET_FORCED_NFCEE_ROUTING_CMD >>  
  * Forced NFCEE Routing State: Error (02)
#end
```

### 實作備註
- Power State 的欄寬是 `'{0:<33}'`，比 Sub-State 標籤短，所以 Sub-State 1–3 的 `Apply`/`Not apply` 會直接接在冒號後面，沒有對齊（純顯示問題，見上方範例）。`LISTEN_MODE_ROUTING_INFO` 則使用 `<43`/`>10`。

---

<a id="rf_set_forced_nfcee_routing_rsp"></a><a id="RF_SET_FORCED_NFCEE_ROUTING_RSP"></a>
## RF_SET_FORCED_NFCEE_ROUTING_RSP  (`41 11`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x11 / RSP |
| Handler | [`RF_Management.py:1243`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L1243) `RF_SET_FORCED_NFCEE_ROUTING_RSP` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |

### 範例
- Raw：`41 11 01 00`

```text
  << RF_SET_FORCED_NFCEE_ROUTING_RSP >>  
  * Status: STATUS_OK (00)
#end
```
