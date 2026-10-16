# NXP (SN2x0) RF Management（GID = 1）

本文件說明 `Nxp_pkg/RF_Management.py` 中所有 RF Management 控制訊息 handler（依 `Nxp_pkg/__ctrl__.py` 的 `"RF Management"` 群組）。
內容分為兩部分：

1. **NFC Forum 標準 OID 0x00–0x11**：大多數 handler 只是把 payload 轉交給 `nfc_forum_2_0_pkg/RF_Management.py`（`from nfc_forum_2_0_pkg import RF_Management as Origin`），並傳入 `vendor="nxp"`。因此解析邏輯與 forum 版完全相同，**唯一差異是對照表改從 `Nxp_pkg/__table__.py` 載入**（`__pkg_import__.tbl_import` → `vendor_registry.resolve("nxp")` → `Nxp_pkg.__table__`）。這類 handler 只描述 NXP 差異，詳細格式請見 forum 文件。OID 0x0C/0x0D/0x0E/0x0F/0x11 則是 NXP 版自行改寫成「No Support」stub，不解析 payload。
2. **NXP SN2x0 擴充 NTF（OID 0x18/0x20/0x21/0x23/0x28/0x29/0x2A/0x2B）**：由 NXP 版自行實作，完整列出 payload。

### NXP 對照表與 forum 對照表的差異（影響 delegate handler 的輸出）

以下為實際比對 `Nxp_pkg.__table__` 與 `nfc_forum_2_0_pkg.__table__` 中 RF Management 用到的表所得結果（其餘用到的表 `tbl_mode`、`tbl_more`、`tbl_L_mode_routing_entry_type`、`tbl_pwr_state`、`tbl_rf_tech`、`tbl_rf_dis_id`、`tbl_len_rdu_val`、`tbl_deactivate_type`、`tbl_deactivate_reason`、`tbl_rf_field_status`、`tbl_nfcee_ntf_trig`、`tbl_nfcee_disc_req_type`、`tbl_rf_commu_para_id`、`tbl_rf_if_exten` 兩邊內容相同）：

| 表 | NXP 版差異 |
|---|---|
| [`tbl_rf_proto`](Tables.md#tbl_rf_proto) | 新增 `80` = `MIFARE_CLASSIC`；移除 forum 的 range key `80-FE`（For proprietary use） |
| [`tbl_rf_if`](Tables.md#tbl_rf_if) | 新增 `80` = `TAG-CMD`、`81` = `WLC_RF`、`83` = `NFCEE_DEP_RF_eSE`；移除 `80-FE` |
| [`tbl_status_codes`](Tables.md#tbl_status_codes) | 新增 `E3`–`E7`、`EA`、`ED`–`F0`、`FA` 等 NXP 專屬狀態碼（例如 `E3` = `STATUS_PMU_TXLDO_OVERCURRENT`） |
| [`tbl_nfcee_id`](Tables.md#tbl_nfcee_id) | 新增 `10` = `NFCEE_NDEF`、`80`/`81` = `NFCEE_UICC1/2`、`C0` = `NFCEE_eSE`、`C1`/`C2` = eUICC Profile 1/2（range key `02-0F`/`10-7F`/`80-FE` 保留，故會同時印出具體名稱與 range 名稱） |
| [`tbl_rf_tech_mode`](Tables.md#tbl_rf_tech_mode) | `03` 改為 `ACTIVE_POLL ( Not supported )`、`83` 改為 `ACTIVE_LISTEN ( Not supported )`；新增 `71` = `SILENT_PASSIVE_POLL`；移除所有 range key（`04-05`、`07-6F`、`70-7F`、`84-EF`、`F0-FF`） |
| [`tbl_bit_rates`](Tables.md#tbl_bit_rates) | 新增 `80` = `212 Kbit/s & 424 Kbit/s`；移除 `80-FE` |

## 總覽

| OID | CMD | RSP | NTF | Handler |
|---|---|---|---|---|
| 0x00 | `21 00` | `41 00` | – | [RF_DISCOVER_MAP_CMD](#rf_discover_map_cmd) / [RF_DISCOVER_MAP_RSP](#rf_discover_map_rsp) |
| 0x01 | `21 01` | `41 01` | – | [RF_SET_LISTEN_MODE_ROUTING_CMD](#rf_set_listen_mode_routing_cmd) / [RF_SET_LISTEN_MODE_ROUTING_RSP](#rf_set_listen_mode_routing_rsp) |
| 0x02 | `21 02` | `41 02` | `61 02` | [RF_GET_LISTEN_MODE_ROUTING_CMD](#rf_get_listen_mode_routing_cmd) / [RF_GET_LISTEN_MODE_ROUTING_RSP](#rf_get_listen_mode_routing_rsp) / [RF_GET_LISTEN_MODE_ROUTING_NTF](#rf_get_listen_mode_routing_ntf) |
| 0x03 | `21 03` | `41 03` | `61 03` | [RF_DISCOVER_CMD](#rf_discover_cmd) / [RF_DISCOVER_RSP](#rf_discover_rsp) / [RF_DISCOVER_NTF](#rf_discover_ntf) |
| 0x04 | `21 04` | `41 04` | – | [RF_DISCOVER_SELECT_CMD](#rf_discover_select_cmd) / [RF_DISCOVER_SELECT_RSP](#rf_discover_select_rsp) |
| 0x05 | – | – | `61 05` | [RF_INTF_ACTIVATED_NTF](#rf_intf_activated_ntf) |
| 0x06 | `21 06` | `41 06` | `61 06` | [RF_DEACTIVATE_CMD](#rf_deactivate_cmd) / [RF_DEACTIVATE_RSP](#rf_deactivate_rsp) / [RF_DEACTIVATE_NTF](#rf_deactivate_ntf) |
| 0x07 | – | – | `61 07` | [RF_FIELD_INFO_NTF](#rf_field_info_ntf) |
| 0x08 | `21 08` | `41 08` | `61 08` | [RF_T3T_POLLING_CMD](#rf_t3t_polling_cmd) / [RF_T3T_POLLING_RSP](#rf_t3t_polling_rsp) / [RF_T3T_POLLING_NTF](#rf_t3t_polling_ntf) |
| 0x09 | – | – | `61 09` | [RF_NFCEE_ACTION_NTF](#rf_nfcee_action_ntf) |
| 0x0A | – | – | `61 0A` | [RF_NFCEE_DISCOVERY_REQ_NTF](#rf_nfcee_discovery_req_ntf) |
| 0x0B | `21 0B` | `41 0B` | – | [RF_PARAMETER_UPDATE_CMD](#rf_parameter_update_cmd) / [RF_PARAMETER_UPDATE_RSP](#rf_parameter_update_rsp) |
| 0x0C | `21 0C` | `41 0C` | – | [RF_INTF_EXT_START_CMD](#rf_intf_ext_start_cmd) / [RF_INTF_EXT_START_RSP](#rf_intf_ext_start_rsp) |
| 0x0D | `21 0D` | `41 0D` | – | [RF_INTF_EXT_STOP_CMD](#rf_intf_ext_stop_cmd) / [RF_INTF_EXT_STOP_RSP](#rf_intf_ext_stop_rsp) |
| 0x0E | `21 0E` | `41 0E` | – | [RF_EXT_AGG_ABORT_CMD](#rf_ext_agg_abort_cmd) / [RF_EXT_AGG_ABORT_RSP](#rf_ext_agg_abort_rsp) |
| 0x0F | `21 0F` | `41 0F` | – | [RF_NDEF_ABORT_CMD](#rf_ndef_abort_cmd) / [RF_NDEF_ABORT_RSP](#rf_ndef_abort_rsp) |
| 0x10 | `21 10` | `41 10` | `61 10` | [RF_ISO_DEP_NAK_PRESENCE_CMD](#rf_iso_dep_nak_presence_cmd) / [RF_ISO_DEP_NAK_PRESENCE_RSP](#rf_iso_dep_nak_presence_rsp) / [RF_ISO_DEP_NAK_PRESENCE_NTF](#rf_iso_dep_nak_presence_ntf) |
| 0x11 | `21 11` | `41 11` | – | [RF_SET_FORCED_NFCEE_ROUTING_CMD](#rf_set_forced_nfcee_routing_cmd) / [RF_SET_FORCED_NFCEE_ROUTING_RSP](#rf_set_forced_nfcee_routing_rsp) |
| 0x18 | – | – | `61 18` | [IOT_RETRY_NTF](#iot_retry_ntf)（SN2x0） |
| 0x20 | – | – | `61 20` | [FIELD_DETECT_NTF](#field_detect_ntf)（SN2x0） |
| 0x21 | – | – | `61 21` | [PLL_UNLOCKED_NTF](#pll_unlocked_ntf)（SN2x0） |
| 0x23 | – | – | `61 23` | [TxLDO_ERROR_NTF](#txldo_error_ntf)（SN2x0） |
| 0x28 | – | – | `61 28` | [PLL_LOSTLOCK_NTF](#pll_lostlock_ntf)（SN2x0） |
| 0x29 | – | – | `61 29` | [SETTINGS_CHANGE_NTF](#settings_change_ntf)（SN2x0） |
| 0x2A | – | – | `61 2A` | [RF_FREQ_ERROR_NTF](#rf_freq_error_ntf)（SN2x0） |
| 0x2B | – | – | `61 2B` | [LPDET_ERROR_NTF](#lpdet_error_ntf)（SN2x0） |

共 45 個 handler（OID 0x00–0x11 共 37 個、SN2x0 擴充 NTF 8 個）。

範例皆以 `NFC_NCI_DECODER(len(raw)//2, raw, 'Nxp', 'None', 2)` 實際執行取得（mode=2，故 handler 名稱後不印 raw）。

---

# Part 1：NFC Forum 標準 OID 0x00–0x11

<a id="rf_discover_map_cmd"></a><a id="RF_DISCOVER_MAP_CMD"></a>
## RF_DISCOVER_MAP_CMD  (`21 00`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x00 / CMD |
| Handler | [`RF_Management.py:7`](../../nci_decoder/Nxp_pkg/RF_Management.py#L7) `RF_DISCOVER_MAP_CMD` |
| 實作方式 | Delegate → `Origin.RF_DISCOVER_MAP_CMD(raw, "nxp")`，詳見 [forum 版](../nfc_forum_2_0/RF_Management.md#rf_discover_map_cmd) |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Number of Mapping Configurations | 1 | 數值 n |
| 2 | Mapping Configuration [1..n] | 3×n | |
| ﹂ | RF Protocol | 1 | `tbl_rf_proto`（見 [Tables](Tables.md#tbl_rf_proto)） |
| ﹂ | Mode | 1 | `tbl_mode`（見 [Tables](Tables.md#tbl_mode)） |
| ﹂ | RF Interface | 1 | `tbl_rf_if`（見 [Tables](Tables.md#tbl_rf_if)） |

NXP 差異：`tbl_rf_proto` 可解出 `80` = `MIFARE_CLASSIC`，`tbl_rf_if` 可解出 `80` = `TAG-CMD` 等 NXP 介面。

### 範例
- Raw：`21 00 07 02 04 03 02 80 02 80`

```text
  << RF_DISCOVER_MAP_CMD >>  
  * Number of Mapping Configs: 2 (02)

   ~ [Mapping Cfg_0] ~  
    * RF Protocol: ISO-DEP (04)
    * Mode: Listen/Polling (03)
    * RF Interface: ISO-DEP (02)

   ~ [Mapping Cfg_1] ~  
    * RF Protocol: MIFARE_CLASSIC (80)
    * Mode: Listen (02)
    * RF Interface: TAG-CMD (80)
#end
```

<a id="rf_discover_map_rsp"></a><a id="RF_DISCOVER_MAP_RSP"></a>
## RF_DISCOVER_MAP_RSP  (`41 00`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x00 / RSP |
| Handler | [`RF_Management.py:21`](../../nci_decoder/Nxp_pkg/RF_Management.py#L21) `RF_DISCOVER_MAP_RSP` |
| 實作方式 | Delegate → `Origin.RF_DISCOVER_MAP_RSP(raw, "nxp")`，詳見 [forum 版](../nfc_forum_2_0/RF_Management.md#rf_discover_map_rsp) |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |

NXP 差異：Status 使用 NXP 版 `tbl_status_codes`（含 NXP 專屬錯誤碼）。

### 範例
- Raw：`41 00 01 00`

```text
  << RF_DISCOVER_MAP_RSP >>  
  * Status: STATUS_OK (00)
#end
```

<a id="rf_set_listen_mode_routing_cmd"></a><a id="RF_SET_LISTEN_MODE_ROUTING_CMD"></a>
## RF_SET_LISTEN_MODE_ROUTING_CMD  (`21 01`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x01 / CMD |
| Handler | [`RF_Management.py:152`](../../nci_decoder/Nxp_pkg/RF_Management.py#L152) `RF_SET_LISTEN_MODE_ROUTING_CMD` |
| 實作方式 | Delegate → `Origin.RF_SET_LISTEN_MODE_ROUTING_CMD(raw, "nxp")`（內部呼叫 forum 版共用函式 `LISTEN_MODE_ROUTING_INFO`），詳見 [forum 版](../nfc_forum_2_0/RF_Management.md#rf_set_listen_mode_routing_cmd) |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | More | 1 | `tbl_more`（見 [Tables](Tables.md#tbl_more)） |
| 2 | Number of Routing Entries | 1 | 數值 n |
| 3 | Routing Entry [1..n] | x+2 each | |
| ﹂ | Qualifier-Type | 1 | 低 nibble：`tbl_L_mode_routing_entry_type`（見 [Tables](Tables.md#tbl_L_mode_routing_entry_type)）；高 nibble bit 位元旗標，見 forum 文件 |
| ﹂ | Length | 1 | 數值 x |
| ﹂ | Value | x | 第 1 byte Route：`tbl_nfcee_id`（見 [Tables](Tables.md#tbl_nfcee_id)）+ range bucket；第 2 byte Power State：bit0–bit5 以 `tbl_pwr_state`（見 [Tables](Tables.md#tbl_pwr_state)）列出 Apply/Not apply；其後依 Type 分支（Technology→`tbl_rf_tech`（見 [Tables](Tables.md#tbl_rf_tech)）、Protocol→`tbl_rf_proto`、AID、System Code、APDU pattern），詳見 forum 文件 |

NXP 差異：Route 欄位會額外顯示 NXP NFCEE 名稱（如 `C0` → `NFCEE_eSE (HCI-NFCEE)`）；Protocol-based entry 可解出 `MIFARE_CLASSIC`。

### 範例
- Raw：`21 01 12 00 02 00 03 C0 3B 00 12 09 C0 3B A0 00 00 00 03 10 10`

```text
  << RF_SET_LISTEN_MODE_ROUTING_CMD >>  
  * More: Last Message (00)
  * Number of Routing Entries: 2 (02)

   ~ [Routing Entry_0] ~  
    * Type: Technology-based routing entry (00)
    * Len: 3
    * Val: C03B00
      * Route: NFCEE_eSE (HCI-NFCEE) (C0)
      * Power State: 00111011 (3B)
       ~ Screen Off lock (Sub-State 3):         Apply
       ~ Screen On lock (Sub-State 2):          Apply
       ~ Screen off unlock (Sub-State 1):       Apply
       ~ Battery Off State:                 Not apply
       ~ Switch Off State:                      Apply
       ~ Switch On State:                       Apply
      * Technology: NFC_RF_TECHNOLOGY_A (00)

   ~ [Routing Entry_1] ~  
    * Type: AID-based routing entry (12)
     ~ Match is allowed when the SELECT AID is longer than the AID in this routing table entry.
    * Len: 9
    * Val: C03BA0000000031010
      * Route: NFCEE_eSE (HCI-NFCEE) (C0)
      * Power State: 00111011 (3B)
       ~ Screen Off lock (Sub-State 3):         Apply
       ~ Screen On lock (Sub-State 2):          Apply
       ~ Screen off unlock (Sub-State 1):       Apply
       ~ Battery Off State:                 Not apply
       ~ Switch Off State:                      Apply
       ~ Switch On State:                       Apply
      * AID: A0000000031010
#end
```

### 實作備註
- NXP 檔案中保留了一份被整段註解掉的舊版 `LISTEN_MODE_ROUTING_INFO`（[`RF_Management.py:30-149`](../../nci_decoder/Nxp_pkg/RF_Management.py#L30)），目前不會被執行；實際使用 forum 版。

<a id="rf_set_listen_mode_routing_rsp"></a><a id="RF_SET_LISTEN_MODE_ROUTING_RSP"></a>
## RF_SET_LISTEN_MODE_ROUTING_RSP  (`41 01`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x01 / RSP |
| Handler | [`RF_Management.py:158`](../../nci_decoder/Nxp_pkg/RF_Management.py#L158) `RF_SET_LISTEN_MODE_ROUTING_RSP` |
| 實作方式 | Delegate → `Origin.RF_SET_LISTEN_MODE_ROUTING_RSP(raw, "nxp")`，詳見 [forum 版](../nfc_forum_2_0/RF_Management.md#rf_set_listen_mode_routing_rsp) |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |

NXP 差異：使用 NXP 版 `tbl_status_codes`。

### 範例
- Raw：`41 01 01 00`

```text
  << RF_SET_LISTEN_MODE_ROUTING_RSP >>  
  * Status: STATUS_OK (00)
#end
```

<a id="rf_get_listen_mode_routing_cmd"></a><a id="RF_GET_LISTEN_MODE_ROUTING_CMD"></a>
## RF_GET_LISTEN_MODE_ROUTING_CMD  (`21 02`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x02 / CMD |
| Handler | [`RF_Management.py:168`](../../nci_decoder/Nxp_pkg/RF_Management.py#L168) `RF_GET_LISTEN_MODE_ROUTING_CMD` |
| 實作方式 | Delegate → `Origin.RF_GET_LISTEN_MODE_ROUTING_CMD(raw, "nxp")`，詳見 [forum 版](../nfc_forum_2_0/RF_Management.md#rf_get_listen_mode_routing_cmd) |

### Payload 格式
(Empty)，handler 只印 `(Empty)` 並回傳 0。NXP 無差異。

### 範例
- Raw：`21 02 00`

```text
  << RF_GET_LISTEN_MODE_ROUTING_CMD >>  
         (Empty)         
#end
```

<a id="rf_get_listen_mode_routing_rsp"></a><a id="RF_GET_LISTEN_MODE_ROUTING_RSP"></a>
## RF_GET_LISTEN_MODE_ROUTING_RSP  (`41 02`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x02 / RSP |
| Handler | [`RF_Management.py:178`](../../nci_decoder/Nxp_pkg/RF_Management.py#L178) `RF_GET_LISTEN_MODE_ROUTING_RSP` |
| 實作方式 | Delegate → `Origin.RF_GET_LISTEN_MODE_ROUTING_RSP(raw, "nxp")`，詳見 [forum 版](../nfc_forum_2_0/RF_Management.md#rf_get_listen_mode_routing_rsp) |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |

NXP 差異：使用 NXP 版 `tbl_status_codes`。

### 範例
- Raw：`41 02 01 00`

```text
  << RF_GET_LISTEN_MODE_ROUTING_RSP >>  
  * Status: STATUS_OK (00)
#end
```

<a id="rf_get_listen_mode_routing_ntf"></a><a id="RF_GET_LISTEN_MODE_ROUTING_NTF"></a>
## RF_GET_LISTEN_MODE_ROUTING_NTF  (`61 02`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x02 / NTF |
| Handler | [`RF_Management.py:188`](../../nci_decoder/Nxp_pkg/RF_Management.py#L188) `RF_GET_LISTEN_MODE_ROUTING_NTF` |
| 實作方式 | Delegate → `Origin.RF_GET_LISTEN_MODE_ROUTING_NTF(raw, "nxp")`（共用 `LISTEN_MODE_ROUTING_INFO`），詳見 [forum 版](../nfc_forum_2_0/RF_Management.md#rf_get_listen_mode_routing_ntf) |

### Payload 格式
與 [RF_SET_LISTEN_MODE_ROUTING_CMD](#rf_set_listen_mode_routing_cmd) 相同（More / Number of Routing Entries / Routing Entry[1..n]）。NXP 差異同該節。

### 範例
- Raw：`61 02 07 00 01 01 03 00 3B 80`

```text
  << RF_GET_LISTEN_MODE_ROUTING_NTF >>  
  * More: Last Message (00)
  * Number of Routing Entries: 1 (01)

   ~ [Routing Entry_0] ~  
    * Type: Protocol-based routing entry (01)
    * Len: 3
    * Val: 003B80
      * Route: DH-NFCEE  (00)
      * Power State: 00111011 (3B)
       ~ Screen Off lock (Sub-State 3):         Apply
       ~ Screen On lock (Sub-State 2):          Apply
       ~ Screen off unlock (Sub-State 1):       Apply
       ~ Battery Off State:                 Not apply
       ~ Switch Off State:                      Apply
       ~ Switch On State:                       Apply
      * Protocol: MIFARE_CLASSIC (80)
#end
```

<a id="rf_discover_cmd"></a><a id="RF_DISCOVER_CMD"></a>
## RF_DISCOVER_CMD  (`21 03`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x03 / CMD |
| Handler | [`RF_Management.py:194`](../../nci_decoder/Nxp_pkg/RF_Management.py#L194) `RF_DISCOVER_CMD` |
| 實作方式 | Delegate → `Origin.RF_DISCOVER_CMD(raw, "nxp")`，詳見 [forum 版](../nfc_forum_2_0/RF_Management.md#rf_discover_cmd) |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Number of Configurations | 1 | 數值 n |
| 2 | Configuration [1..n] | 2×n | |
| ﹂ | RF Technology and Mode | 1 | `tbl_rf_tech_mode`（見 [Tables](Tables.md#tbl_rf_tech_mode)） |
| ﹂ | Discovery Frequency | 1 | 十進位；`00` 或 > 10 印 `RFU` |

NXP 差異：`tbl_rf_tech_mode` 的 `03`/`83` 顯示為 `( Not supported )`，`71` 顯示 `SILENT_PASSIVE_POLL`；NXP 表無 range key，未定義值一律顯示 `RFU`。

### 範例
- Raw：`21 03 09 04 00 01 01 01 02 01 80 01`

```text
  << RF_DISCOVER_CMD >>  
  * Number of Configs: 4 (04)

   ~ [Config_0] ~  
    * Mode: A_PASSIVE_POLL (00)
    * Discovery Freq: 1

   ~ [Config_1] ~  
    * Mode: B_PASSIVE_POLL (01)
    * Discovery Freq: 1

   ~ [Config_2] ~  
    * Mode: F_PASSIVE_POLL (02)
    * Discovery Freq: 1

   ~ [Config_3] ~  
    * Mode: A_PASSIVE_LISTEN (80)
    * Discovery Freq: 1
#end
```

<a id="rf_discover_rsp"></a><a id="RF_DISCOVER_RSP"></a>
## RF_DISCOVER_RSP  (`41 03`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x03 / RSP |
| Handler | [`RF_Management.py:207`](../../nci_decoder/Nxp_pkg/RF_Management.py#L207) `RF_DISCOVER_RSP` |
| 實作方式 | Delegate → `Origin.RF_DISCOVER_RSP(raw, "nxp")`，詳見 [forum 版](../nfc_forum_2_0/RF_Management.md#rf_discover_rsp) |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |

NXP 差異：使用 NXP 版 `tbl_status_codes`。

### 範例
- Raw：`41 03 01 00`

```text
  << RF_DISCOVER_RSP >>  
  * Status: STATUS_OK (00)
#end
```

<a id="rf_discover_ntf"></a><a id="RF_DISCOVER_NTF"></a>
## RF_DISCOVER_NTF  (`61 03`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x03 / NTF |
| Handler | [`RF_Management.py:392`](../../nci_decoder/Nxp_pkg/RF_Management.py#L392) `RF_DISCOVER_NTF` |
| 實作方式 | Delegate → `Origin.RF_DISCOVER_NTF(raw, "nxp")`（RF Technology Specific Parameters 由 forum 版 `RF_TECH_SPEC_PARA` 解析），詳見 [forum 版](../nfc_forum_2_0/RF_Management.md#rf_discover_ntf) |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | RF Discovery ID | 1 | `tbl_rf_dis_id`（見 [Tables](Tables.md#tbl_rf_dis_id)），查不到印原值 |
| 2 | RF Protocol | 1 | `tbl_rf_proto`（見 [Tables](Tables.md#tbl_rf_proto)） |
| 3 | RF Technology and Mode | 1 | `tbl_rf_tech_mode`（見 [Tables](Tables.md#tbl_rf_tech_mode)） |
| 4 | Length of RF Technology Specific Parameters | 1 | 數值 n |
| 5 | RF Technology Specific Parameters | n | 依 #3 的 **hex code** 分支（`00`/`01`/`02`/`06` Poll、`80`/`81`/`82` Listen、`03` ACTIVE_POLL、`83` ACTIVE_LISTEN），其他值印 `Proprietary parameters: <raw>`；格式見 forum 文件 |
| 6 | Notification Type | 1 | 程式內寫死：`00` Last NTF、`01` Last NTF (resource limit)、`02` More NTF to follow、其他 RFU |

NXP 差異：
- 可解出 `MIFARE_CLASSIC` (80) 協定。
- NXP `tbl_rf_tech_mode` 把 `03`/`83` 顯示為 `ACTIVE_POLL ( Not supported )` / `ACTIVE_LISTEN ( Not supported )`；✅ 已修正（2026-10）：`RF_TECH_SPEC_PARA` 改依 hex code 分支，`03`/`83` 仍會解析 ATR_RES / ATR_REQ（見下例）。`71` SILENT_PASSIVE_POLL 不在任何分支內，只印 `Proprietary parameters: <raw>`。

### 範例
- Raw：`61 03 0F 01 80 00 0A 04 00 04 11 22 33 44 01 08 00 02`

```text
  << RF_DISCOVER_NTF >>  
  * RF Discovery ID: 01
  * RF Protocol: MIFARE_CLASSIC (80)
  * Mode: A_PASSIVE_POLL (00)
  * Len of RF Tech Specific Params: 10
  * SENS_RES Response: 0400
  * NFCID1 Len: 4
  * NFCID1: 11223344
  * SEL_RES Rsp Len: 1
  * SEL_RES Rsp: 08
  * HRx Len: 0
  * NTF Type: More NTF to follow (02)
#end
```

- Raw（ACTIVE_POLL：NXP 表名稱為 `ACTIVE_POLL ( Not supported )`，但依 hex code 仍進入 ATR_RES 分支）：`61 03 06 02 04 03 01 AA 00`

```text
  << RF_DISCOVER_NTF >>  
  * RF Discovery ID: 02
  * RF Protocol: ISO-DEP (04)
  * Mode: ACTIVE_POLL ( Not supported ) (03)
  * Len of RF Tech Specific Params: 1
  * ATR_RES Rsp Len: 170
  * Error: RF Technology Specific Parameters: Payload too short: need 170 byte(s) for ATR_RES Rsp, 0 left
  * NTF Type: Last NTF (00)
#end
```

### 實作備註
- NXP 檔案中保留一份被註解掉的舊版 `RF_TECH_SPEC_PARA`（[`RF_Management.py:216-389`](../../nci_decoder/Nxp_pkg/RF_Management.py#L216)），不會執行。

<a id="rf_discover_select_cmd"></a><a id="RF_DISCOVER_SELECT_CMD"></a>
## RF_DISCOVER_SELECT_CMD  (`21 04`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x04 / CMD |
| Handler | [`RF_Management.py:407`](../../nci_decoder/Nxp_pkg/RF_Management.py#L407) `RF_DISCOVER_SELECT_CMD` |
| 實作方式 | Delegate → `Origin.RF_DISCOVER_SELECT_CMD(raw, "nxp")`，詳見 [forum 版](../nfc_forum_2_0/RF_Management.md#rf_discover_select_cmd) |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | RF Discovery ID | 1 | `tbl_rf_dis_id`（見 [Tables](Tables.md#tbl_rf_dis_id)） |
| 2 | RF Protocol | 1 | `tbl_rf_proto`（見 [Tables](Tables.md#tbl_rf_proto)） |
| 3 | RF Interface | 1 | `tbl_rf_if`（見 [Tables](Tables.md#tbl_rf_if)） |

NXP 差異：可解出 `MIFARE_CLASSIC` 協定與 `TAG-CMD`/`WLC_RF`/`NFCEE_DEP_RF_eSE` 介面。

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
- ✅ 已修正（2026-10）：forum 版 RF Interface 行的括號改印 `rf_if` 本身的 hex（上例 `ISO-DEP (02)`）。

<a id="rf_discover_select_rsp"></a><a id="RF_DISCOVER_SELECT_RSP"></a>
## RF_DISCOVER_SELECT_RSP  (`41 04`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x04 / RSP |
| Handler | [`RF_Management.py:419`](../../nci_decoder/Nxp_pkg/RF_Management.py#L419) `RF_DISCOVER_SELECT_RSP` |
| 實作方式 | Delegate → `Origin.RF_DISCOVER_SELECT_RSP(raw, "nxp")`，詳見 [forum 版](../nfc_forum_2_0/RF_Management.md#rf_discover_select_rsp) |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |

NXP 差異：使用 NXP 版 `tbl_status_codes`。

### 範例
- Raw：`41 04 01 00`

```text
  << RF_DISCOVER_SELECT_RSP >>  
  * Status: STATUS_OK (00)
#end
```

<a id="rf_intf_activated_ntf"></a><a id="RF_INTF_ACTIVATED_NTF"></a>
## RF_INTF_ACTIVATED_NTF  (`61 05`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x05 / NTF |
| Handler | [`RF_Management.py:429`](../../nci_decoder/Nxp_pkg/RF_Management.py#L429) `RF_INTF_ACTIVATED_NTF` |
| 實作方式 | Delegate → `Origin.RF_INTF_ACTIVATED_NTF(raw, "nxp")`，詳見 [forum 版](../nfc_forum_2_0/RF_Management.md#rf_intf_activated_ntf) |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | RF Discovery ID | 1 | `tbl_rf_dis_id`（見 [Tables](Tables.md#tbl_rf_dis_id)） |
| 2 | RF Interface | 1 | `tbl_rf_if`（見 [Tables](Tables.md#tbl_rf_if)） |
| 3 | RF Protocol | 1 | `tbl_rf_proto`（見 [Tables](Tables.md#tbl_rf_proto)） |
| 4 | Activation RF Technology and Mode | 1 | `tbl_rf_tech_mode`（見 [Tables](Tables.md#tbl_rf_tech_mode)） |
| 5 | Max Data Packet Payload Size | 1 | 十進位 |
| 6 | Initial Number of Credits | 1 | `FF` → `Not used`；其他以 `int(x, 16)` 轉成十進位 |
| 7 | Length of RF Technology Specific Parameters | 1 | 數值 l |
| 8 | RF Technology Specific Parameters | l | 同 [RF_DISCOVER_NTF](#rf_discover_ntf) 的 `RF_TECH_SPEC_PARA` |
| 9 | Data Exchange RF Technology and Mode | 1 | `tbl_rf_tech_mode` |
| 10 | Data Exchange Transmit Bit Rate | 1 | `tbl_bit_rates`（見 [Tables](Tables.md#tbl_bit_rates)） |
| 11 | Data Exchange Receive Bit Rate | 1 | `tbl_bit_rates` |
| 12 | Length of Activation Parameters | 1 | 數值 n |
| 13 | Activation Parameters | n | 依 RF Interface 與 Activation Mode 的 **hex code** 分支（`02` ISO-DEP、`03` NFC-DEP）；NFC-DEP 的 Poll（`00`/`02`）與 Listen（`80`/`82`）分支都在 ATR 之後讀 1 octet `Data Exchange LR`（`tbl_len_rdu_val`，見 [Tables](Tables.md#tbl_len_rdu_val)）；有剩餘 bytes 時印 `Remaining Activation Params`；其他情況印 raw。詳見 forum 文件 |

NXP 差異：
- RF Interface 為 NXP 專屬值（如 `80` TAG-CMD、`81` WLC_RF、`83` NFCEE_DEP_RF_eSE）時不屬於 ISO-DEP/NFC-DEP 分支，Activation Parameters 只印 raw。
- `tbl_bit_rates` 可解出 `80` = `212 Kbit/s & 424 Kbit/s`。
- Activation Mode 為 `71` 時 Tech Specific Params 只印 raw；`03`/`83` 依 hex code 正常解析（同 RF_DISCOVER_NTF）。

### 範例
- Raw：`61 05 1B 01 02 04 00 FF FF 0A 04 00 04 11 22 33 44 01 20 00 00 00 00 06 05 05 78 80 70 02`

```text
  << RF_INTF_ACTIVATED_NTF >>  
  * RF Discovery ID: 01
  * RF Interface: ISO-DEP (02)
  * RF Protocol: ISO-DEP (04)
  * Activation Mode: A_PASSIVE_POLL (00)
  * Max Data Size: 255 (FF)
  * Number of Credits: Not used (FF)
  * Len of RF Tech Specific Params: 10
  * SENS_RES Response: 0400
  * NFCID1 Len: 4
  * NFCID1: 11223344
  * SEL_RES Rsp Len: 1
  * SEL_RES Rsp: 20
  * HRx Len: 0
  * Data Mode: A_PASSIVE_POLL (00)
  * Tx: 106 Kbit/s (00)
  * Rx: 106 Kbit/s (00)
  * Len of Activation Params: 6
  * RATS Rsp Len: 5 (05)
  * RATS Rsp: 0578807002
#end
```

### 實作備註
- ✅ 已修正（2026-10）：forum 版 Initial Number of Credits 改以 base 16 解析（`0A` → 10、`10` → 16），不再拋 `ValueError`。

<a id="rf_deactivate_cmd"></a><a id="RF_DEACTIVATE_CMD"></a>
## RF_DEACTIVATE_CMD  (`21 06`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x06 / CMD |
| Handler | [`RF_Management.py:451`](../../nci_decoder/Nxp_pkg/RF_Management.py#L451) `RF_DEACTIVATE_CMD` |
| 實作方式 | Delegate → `Origin.RF_DEACTIVATE_CMD(raw, "nxp")`，詳見 [forum 版](../nfc_forum_2_0/RF_Management.md#rf_deactivate_cmd) |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Deactivation Type | 1 | `tbl_deactivate_type`（見 [Tables](Tables.md#tbl_deactivate_type)） |

NXP 差異：無（NXP 與 forum 的 `tbl_deactivate_type` 內容相同）。

### 範例
- Raw：`21 06 01 03`

```text
  << RF_DEACTIVATE_CMD >>  
  * Deactivation Type: Discovery (03)
#end
```

<a id="rf_deactivate_rsp"></a><a id="RF_DEACTIVATE_RSP"></a>
## RF_DEACTIVATE_RSP  (`41 06`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x06 / RSP |
| Handler | [`RF_Management.py:461`](../../nci_decoder/Nxp_pkg/RF_Management.py#L461) `RF_DEACTIVATE_RSP` |
| 實作方式 | Delegate → `Origin.RF_DEACTIVATE_RSP(raw, "nxp")`，詳見 [forum 版](../nfc_forum_2_0/RF_Management.md#rf_deactivate_rsp) |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |

NXP 差異：使用 NXP 版 `tbl_status_codes`。

### 範例
- Raw：`41 06 01 00`

```text
  << RF_DEACTIVATE_RSP >>  
  * Status: STATUS_OK (00)
#end
```

<a id="rf_deactivate_ntf"></a><a id="RF_DEACTIVATE_NTF"></a>
## RF_DEACTIVATE_NTF  (`61 06`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x06 / NTF |
| Handler | [`RF_Management.py:471`](../../nci_decoder/Nxp_pkg/RF_Management.py#L471) `RF_DEACTIVATE_NTF` |
| 實作方式 | Delegate → `Origin.RF_DEACTIVATE_NTF(raw, "nxp")`，詳見 [forum 版](../nfc_forum_2_0/RF_Management.md#rf_deactivate_ntf) |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Deactivation Type | 1 | `tbl_deactivate_type`（見 [Tables](Tables.md#tbl_deactivate_type)） |
| 2 | Deactivation Reason | 1 | `tbl_deactivate_reason`（見 [Tables](Tables.md#tbl_deactivate_reason)） |

NXP 差異：無（兩張表內容與 forum 相同）。

### 範例
- Raw：`61 06 02 03 00`

```text
  << RF_DEACTIVATE_NTF >>  
  * Deactivation Type: Discovery (03)
  * Deactivation Reason: DH_Request (00)
#end
```

<a id="rf_field_info_ntf"></a><a id="RF_FIELD_INFO_NTF"></a>
## RF_FIELD_INFO_NTF  (`61 07`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x07 / NTF |
| Handler | [`RF_Management.py:482`](../../nci_decoder/Nxp_pkg/RF_Management.py#L482) `RF_FIELD_INFO_NTF` |
| 實作方式 | Delegate → `Origin.RF_FIELD_INFO_NTF(raw, "nxp")`，詳見 [forum 版](../nfc_forum_2_0/RF_Management.md#rf_field_info_ntf) |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | RF Field Status | 1 | `tbl_rf_field_status`（見 [Tables](Tables.md#tbl_rf_field_status)）；查不到時 fallback 為 `tbl_rf_field_status['00']` 的字串（不印 raw 值） |

NXP 差異：無（表內容相同）。

### 範例
- Raw：`61 07 01 01`

```text
  << RF_FIELD_INFO_NTF >>  
  * RF Field Status: Operating field generated by Remote NFC Endpoint.
#end
```

<a id="rf_t3t_polling_cmd"></a><a id="RF_T3T_POLLING_CMD"></a>
## RF_T3T_POLLING_CMD  (`21 08`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x08 / CMD |
| Handler | [`RF_Management.py:492`](../../nci_decoder/Nxp_pkg/RF_Management.py#L492) `RF_T3T_POLLING_CMD` |
| 實作方式 | Delegate → `Origin.RF_T3T_POLLING_CMD(raw, "nxp")`，詳見 [forum 版](../nfc_forum_2_0/RF_Management.md#rf_t3t_polling_cmd) |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | SENSF_REQ_PARAMS | 4 | 只印 raw hex |

NXP 差異：無。

### 範例
- Raw：`21 08 04 FF FF 01 00`

```text
  << RF_T3T_POLLING_CMD >>  
  * SENSF_REQ_PARAMS: FFFF0100
#end
```

<a id="rf_t3t_polling_rsp"></a><a id="RF_T3T_POLLING_RSP"></a>
## RF_T3T_POLLING_RSP  (`41 08`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x08 / RSP |
| Handler | [`RF_Management.py:502`](../../nci_decoder/Nxp_pkg/RF_Management.py#L502) `RF_T3T_POLLING_RSP` |
| 實作方式 | Delegate → `Origin.RF_T3T_POLLING_RSP(raw, "nxp")`，詳見 [forum 版](../nfc_forum_2_0/RF_Management.md#rf_t3t_polling_rsp) |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |

NXP 差異：使用 NXP 版 `tbl_status_codes`。

### 範例
- Raw：`41 08 01 00`

```text
  << RF_T3T_POLLING_RSP >>  
  * Status: STATUS_OK (00)
#end
```

<a id="rf_t3t_polling_ntf"></a><a id="RF_T3T_POLLING_NTF"></a>
## RF_T3T_POLLING_NTF  (`61 08`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x08 / NTF |
| Handler | [`RF_Management.py:512`](../../nci_decoder/Nxp_pkg/RF_Management.py#L512) `RF_T3T_POLLING_NTF` |
| 實作方式 | Delegate → `Origin.RF_T3T_POLLING_NTF(raw, "nxp")`，詳見 [forum 版](../nfc_forum_2_0/RF_Management.md#rf_t3t_polling_ntf) |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |
| 2 | Number of Responses | 1 | 數值 n |
| 3 | Responses [1..n] | m+1 each | |
| ﹂ | Length | 1 | 數值 m |
| ﹂ | SENSF_RES | m | 只印 raw hex |

NXP 差異：Status 使用 NXP 版 `tbl_status_codes`。

### 範例
- Raw：`61 08 15 00 01 12 01 02 03 04 05 06 07 08 00 F1 00 00 00 01 43 00 88 B4`

```text
  << RF_T3T_POLLING_NTF >>  
  * Status: STATUS_OK (00)
  * Number of Rsp: 1 (01)

   ~ [Rsp_0] ~  
    * Len: 18 (12)
    * SENSF_RES: 010203040506070800F100000001430088B4
#end
```

### 實作備註
- NXP 版 docstring 標題誤寫為 `[RF_T3T_POLLING_RSP]`（僅註解，不影響執行）。

<a id="rf_nfcee_action_ntf"></a><a id="RF_NFCEE_ACTION_NTF"></a>
## RF_NFCEE_ACTION_NTF  (`61 09`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x09 / NTF |
| Handler | [`RF_Management.py:526`](../../nci_decoder/Nxp_pkg/RF_Management.py#L526) `RF_NFCEE_ACTION_NTF` |
| 實作方式 | Delegate → `Origin.RF_NFCEE_ACTION_NTF(raw, "nxp")`，詳見 [forum 版](../nfc_forum_2_0/RF_Management.md#rf_nfcee_action_ntf) |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | NFCEE ID | 1 | `tbl_nfcee_id`（見 [Tables](Tables.md#tbl_nfcee_id)）精確值 + `range_lookup.find_range_key` 的 range bucket 名稱 |
| 2 | Trigger | 1 | `tbl_nfcee_ntf_trig`（見 [Tables](Tables.md#tbl_nfcee_ntf_trig)），先試 range key |
| 3 | Supporting Data Length | 1 | 數值 n |
| 4 | Supporting Data | n | 依 Trigger：`00` AID（raw）、`01` RF Protocol（`tbl_rf_proto`）、`02`/`05` RF Technology（`tbl_rf_tech`，見 [Tables](Tables.md#tbl_rf_tech)）、`03` SC Route（raw）、`04` Reference data / Mask（各取 n/2 octets） |

NXP 差異：NFCEE ID 可顯示 NXP 名稱（`C0` → `NFCEE_eSE (HCI-NFCEE)` 等）；Trigger `01` 可解出 `MIFARE_CLASSIC`。

### 範例
- Raw：`61 09 0A C0 00 07 A0 00 00 00 03 10 10`

```text
  << RF_NFCEE_ACTION_NTF >>  
  * NFCEE ID: C0 NFCEE_eSE (HCI-NFCEE)
  * Trigger: [ISO/IEC_7816-4] SELECT command with an AID (00)
  * Supporting Data Len: 7
  * Supporting Data: 
    * AID: A0000000031010
#end
```

### 實作備註
- ✅ 已修正（2026-10）：forum 版 Trigger `04`（APDU pattern）改以整數 octets 平分 Supporting Data（例：`61 09 07 C0 04 04 11 22 FF FF` → Reference data `1122`、Mask `FFFF`），不再拋 `TypeError`。

<a id="rf_nfcee_discovery_req_ntf"></a><a id="RF_NFCEE_DISCOVERY_REQ_NTF"></a>
## RF_NFCEE_DISCOVERY_REQ_NTF  (`61 0A`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x0A / NTF |
| Handler | [`RF_Management.py:539`](../../nci_decoder/Nxp_pkg/RF_Management.py#L539) `RF_NFCEE_DISCOVERY_REQ_NTF` |
| 實作方式 | Delegate → `Origin.RF_NFCEE_DISCOVERY_REQ_NTF(raw, "nxp")`，詳見 [forum 版](../nfc_forum_2_0/RF_Management.md#rf_nfcee_discovery_req_ntf) |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Number of Information Entries | 1 | 數值 n |
| 2 | Information Entry [1..n] | x+2 each | |
| ﹂ | Type | 1 | `tbl_nfcee_disc_req_type`（見 [Tables](Tables.md#tbl_nfcee_disc_req_type)），先試 range key；輸出不含 raw 值 |
| ﹂ | Length | 1 | 數值 x |
| ﹂ | Value | x | Type 為 `00`/`01` 時：byte0 NFCEE（`tbl_nfcee_id`，見 [Tables](Tables.md#tbl_nfcee_id)）、byte1 RF Technology and Mode（`tbl_rf_tech_mode`，見 [Tables](Tables.md#tbl_rf_tech_mode)）、byte2 RF Protocol（`tbl_rf_proto`，見 [Tables](Tables.md#tbl_rf_proto)）；其他 Type 只印 raw |

NXP 差異：NFCEE 顯示 NXP 名稱；NXP `tbl_rf_tech_mode` 無 range key，`find_range_key` 回傳 None 後以原值直接查表（未定義值印 `RFU`）。

### 範例
- Raw：`61 0A 06 01 00 03 C0 80 04`

```text
  << RF_NFCEE_DISCOVERY_REQ_NTF >>  
  * Number Of Info Entries: 1

   ~ [Info Entry_0] ~  
    * Type: Added to list
    * Len: 3
    * Val: C08004
      * NFCEE: C0 NFCEE_eSE (HCI-NFCEE)
      * Mode: A_PASSIVE_LISTEN (80)
      * RF Protocol: ISO-DEP (04)
#end
```

<a id="rf_parameter_update_cmd"></a><a id="RF_PARAMETER_UPDATE_CMD"></a>
## RF_PARAMETER_UPDATE_CMD  (`21 0B`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x0B / CMD |
| Handler | [`RF_Management.py:553`](../../nci_decoder/Nxp_pkg/RF_Management.py#L553) `RF_PARAMETER_UPDATE_CMD` |
| 實作方式 | Delegate → `Origin.RF_PARAMETER_UPDATE_CMD(raw, "nxp")`，詳見 [forum 版](../nfc_forum_2_0/RF_Management.md#rf_parameter_update_cmd) |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Number of Parameters | 1 | 數值 n |
| 2 | RF Communication Parameters [1..n] | x+2 each | |
| ﹂ | ID | 1 | `tbl_rf_commu_para_id`（見 [Tables](Tables.md#tbl_rf_commu_para_id)） |
| ﹂ | Length | 1 | 數值 x |
| ﹂ | Value | x | ID `00`：`tbl_rf_tech_mode`；`01`/`02`：Tx/Rx `tbl_bit_rates`（見 [Tables](Tables.md#tbl_bit_rates)）；`03`：NFC-B Data Exchange Config bit field（bit7-6 Min TR0、bit5-4 Min TR1、bit3 Suppression of EoS、bit2 Suppression of SoS、bit1-0 Min TR3） |

NXP 差異：`tbl_rf_tech_mode`/`tbl_bit_rates` 使用 NXP 版。程式註解記載：NXP 不完整支援 RF_PARAMETER_UPDATE_CMD（使用 ISO-DEP RF Interface 時可自動滿足相應情境），但解析邏輯照常執行。

### 範例
- Raw：`21 0B 07 02 00 01 00 03 01 00`

```text
  << RF_PARAMETER_UPDATE_CMD >>  
  * Number of Params: 2 (02)

   ~ [RF Communication 0] ~  
  * Type ID: RF Technology and Mode (coded as defined in Table 131) (00)
  * Len: 1
  * Val: 00
    * Mode: A_PASSIVE_POLL (00)

   ~ [RF Communication 1] ~  
  * Type ID: NFC-B Data Exchange Configuration (coded as defined in Table 92) (03)
  * Len: 1
  * Val: 00
    * NFC-B Data Exchange Config: 00
     ~ Minimum TR0:      00
     ~ Minimum TR1:      00
     ~ Suppression of EoS: 0
     ~ Suppression of SoS: 0
     ~ Minimum TR3:      00
#end
```

<a id="rf_parameter_update_rsp"></a><a id="RF_PARAMETER_UPDATE_RSP"></a>
## RF_PARAMETER_UPDATE_RSP  (`41 0B`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x0B / RSP |
| Handler | [`RF_Management.py:568`](../../nci_decoder/Nxp_pkg/RF_Management.py#L568) `RF_PARAMETER_UPDATE_RSP` |
| 實作方式 | Delegate → `Origin.RF_PARAMETER_UPDATE_RSP(raw, "nxp")`，詳見 [forum 版](../nfc_forum_2_0/RF_Management.md#rf_parameter_update_rsp) |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |
| 2 | Number of Parameters | 1 | 數值 n |
| 3 | RF Communication Parameter ID [1..n] | n | 每個 1 octet，`tbl_rf_commu_para_id`（見 [Tables](Tables.md#tbl_rf_commu_para_id)） |

NXP 差異：Status 使用 NXP 版 `tbl_status_codes`。

### 範例
- Raw：`41 0B 03 00 01 00`

```text
  << RF_PARAMETER_UPDATE_RSP >>  
  * Status: STATUS_OK (00)
  * Number of Params: 1
  * RF Communication Param ID: 
  * Type ID 0: RF Technology and Mode (coded as defined in Table 131) (00)
#end
```

<a id="rf_intf_ext_start_cmd"></a><a id="RF_INTF_EXT_START_CMD"></a>
## RF_INTF_EXT_START_CMD  (`21 0C`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x0C / CMD |
| Handler | [`RF_Management.py:580`](../../nci_decoder/Nxp_pkg/RF_Management.py#L580) `RF_INTF_EXT_START_CMD` |
| 實作方式 | **NXP 自行實作的 stub**（不 delegate）：只印 `[NCI] control message No Support`，回傳 0。forum 版有完整解析，參考 [forum 版](../nfc_forum_2_0/RF_Management.md#rf_intf_ext_start_cmd) |

### Payload 格式（依 docstring，程式未解析）
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | RF Interface Extension | 1 | 未解析 |
| 2 | Start Parameter Length | 1 | 未解析 |
| 3 | Start Parameter | x | 未解析 |

### 範例
- Raw：`21 0C 03 00 01 00`

```text
  << RF_INTF_EXT_START_CMD >>  
[NCI] control message No Support
Error: Payload error!!
  Packet Len: 6 Octet(s)
  Payload Len: 3 Octet(s)
  Check Len: 0.0 Octet(s)
#end
```

### 實作備註
- 回傳值固定為 0，只要 payload 非空就必然觸發 `Payload error!!`。

<a id="rf_intf_ext_start_rsp"></a><a id="RF_INTF_EXT_START_RSP"></a>
## RF_INTF_EXT_START_RSP  (`41 0C`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x0C / RSP |
| Handler | [`RF_Management.py:593`](../../nci_decoder/Nxp_pkg/RF_Management.py#L593) `RF_INTF_EXT_START_RSP` |
| 實作方式 | NXP stub：印 `No Support`，回傳 0。參考 [forum 版](../nfc_forum_2_0/RF_Management.md#rf_intf_ext_start_rsp) |

### Payload 格式（依 docstring，程式未解析）
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | 未解析 |

### 範例
- Raw：`41 0C 01 00`

```text
  << RF_INTF_EXT_START_RSP >>  
[NCI] control message No Support
Error: Payload error!!
  Packet Len: 4 Octet(s)
  Payload Len: 1 Octet(s)
  Check Len: 0.0 Octet(s)
#end
```

### 實作備註
- 回傳 0，必然觸發 `Payload error!!`。

<a id="rf_intf_ext_stop_cmd"></a><a id="RF_INTF_EXT_STOP_CMD"></a>
## RF_INTF_EXT_STOP_CMD  (`21 0D`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x0D / CMD |
| Handler | [`RF_Management.py:604`](../../nci_decoder/Nxp_pkg/RF_Management.py#L604) `RF_INTF_EXT_STOP_CMD` |
| 實作方式 | NXP stub：印 `No Support`，回傳 0。參考 [forum 版](../nfc_forum_2_0/RF_Management.md#rf_intf_ext_stop_cmd) |

### Payload 格式（依 docstring，程式未解析）
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | RF Interface Extension | 1 | 未解析 |
| 2 | Stop Parameter Length | 1 | 未解析 |
| 3 | Stop Parameter | x | 未解析 |

### 範例
- Raw：`21 0D 03 00 01 00`

```text
  << RF_INTF_EXT_STOP_CMD >>  
[NCI] control message No Support
Error: Payload error!!
  Packet Len: 6 Octet(s)
  Payload Len: 3 Octet(s)
  Check Len: 0.0 Octet(s)
#end
```

### 實作備註
- 回傳 0，payload 非空即觸發 `Payload error!!`。

<a id="rf_intf_ext_stop_rsp"></a><a id="RF_INTF_EXT_STOP_RSP"></a>
## RF_INTF_EXT_STOP_RSP  (`41 0D`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x0D / RSP |
| Handler | [`RF_Management.py:617`](../../nci_decoder/Nxp_pkg/RF_Management.py#L617) `RF_INTF_EXT_STOP_RSP` |
| 實作方式 | NXP stub：印 `No Support`，回傳 0。參考 [forum 版](../nfc_forum_2_0/RF_Management.md#rf_intf_ext_stop_rsp) |

### Payload 格式（依 docstring，程式未解析）
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | 未解析 |

### 範例
- Raw：`41 0D 01 00`

```text
  << RF_INTF_EXT_STOP_RSP >>  
[NCI] control message No Support
Error: Payload error!!
  Packet Len: 4 Octet(s)
  Payload Len: 1 Octet(s)
  Check Len: 0.0 Octet(s)
#end
```

### 實作備註
- 回傳 0，必然觸發 `Payload error!!`。

<a id="rf_ext_agg_abort_cmd"></a><a id="RF_EXT_AGG_ABORT_CMD"></a>
## RF_EXT_AGG_ABORT_CMD  (`21 0E`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x0E / CMD |
| Handler | [`RF_Management.py:628`](../../nci_decoder/Nxp_pkg/RF_Management.py#L628) `RF_EXT_AGG_ABORT_CMD` |
| 實作方式 | NXP stub：印 `No Support`，回傳 0。參考 [forum 版](../nfc_forum_2_0/RF_Management.md#rf_ext_agg_abort_cmd) |

### Payload 格式
(Empty)。因 payload 本來就為空，回傳 0 與宣告長度一致，不會出現 Payload error。

### 範例
- Raw：`21 0E 00`

```text
  << RF_EXT_AGG_ABORT_CMD >>  
[NCI] control message No Support
#end
```

<a id="rf_ext_agg_abort_rsp"></a><a id="RF_EXT_AGG_ABORT_RSP"></a>
## RF_EXT_AGG_ABORT_RSP  (`41 0E`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x0E / RSP |
| Handler | [`RF_Management.py:638`](../../nci_decoder/Nxp_pkg/RF_Management.py#L638) `RF_EXT_AGG_ABORT_RSP` |
| 實作方式 | NXP stub：印 `No Support`，回傳 0。參考 [forum 版](../nfc_forum_2_0/RF_Management.md#rf_ext_agg_abort_rsp) |

### Payload 格式（依 docstring，程式未解析）
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | 未解析 |

### 範例
- Raw：`41 0E 01 00`

```text
  << RF_EXT_AGG_ABORT_RSP >>  
[NCI] control message No Support
Error: Payload error!!
  Packet Len: 4 Octet(s)
  Payload Len: 1 Octet(s)
  Check Len: 0.0 Octet(s)
#end
```

### 實作備註
- 回傳 0，必然觸發 `Payload error!!`。

<a id="rf_ndef_abort_cmd"></a><a id="RF_NDEF_ABORT_CMD"></a>
## RF_NDEF_ABORT_CMD  (`21 0F`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x0F / CMD |
| Handler | [`RF_Management.py:649`](../../nci_decoder/Nxp_pkg/RF_Management.py#L649) `RF_NDEF_ABORT_CMD` |
| 實作方式 | NXP stub：印 `No Support`，回傳 0。參考 [forum 版](../nfc_forum_2_0/RF_Management.md#rf_ndef_abort_cmd) |

### Payload 格式
(Empty)。回傳 0 與宣告長度一致。

### 範例
- Raw：`21 0F 00`

```text
  << RF_NDEF_ABORT_CMD >>  
[NCI] control message No Support
#end
```

<a id="rf_ndef_abort_rsp"></a><a id="RF_NDEF_ABORT_RSP"></a>
## RF_NDEF_ABORT_RSP  (`41 0F`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x0F / RSP |
| Handler | [`RF_Management.py:659`](../../nci_decoder/Nxp_pkg/RF_Management.py#L659) `RF_NDEF_ABORT_RSP` |
| 實作方式 | NXP stub：印 `No Support`，回傳 0。參考 [forum 版](../nfc_forum_2_0/RF_Management.md#rf_ndef_abort_rsp) |

### Payload 格式（依 docstring，程式未解析）
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | 未解析 |

### 範例
- Raw：`41 0F 01 00`

```text
  << RF_NDEF_ABORT_RSP >>  
[NCI] control message No Support
Error: Payload error!!
  Packet Len: 4 Octet(s)
  Payload Len: 1 Octet(s)
  Check Len: 0.0 Octet(s)
#end
```

### 實作備註
- 回傳 0，必然觸發 `Payload error!!`。

<a id="rf_iso_dep_nak_presence_cmd"></a><a id="RF_ISO_DEP_NAK_PRESENCE_CMD"></a>
## RF_ISO_DEP_NAK_PRESENCE_CMD  (`21 10`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x10 / CMD |
| Handler | [`RF_Management.py:670`](../../nci_decoder/Nxp_pkg/RF_Management.py#L670) `RF_ISO_DEP_NAK_PRESENCE_CMD` |
| 實作方式 | Delegate → `Origin.RF_ISO_DEP_NAK_PRESENCE_CMD(raw, "nxp")`，詳見 [forum 版](../nfc_forum_2_0/RF_Management.md#rf_iso_dep_nak_presence_cmd) |

### Payload 格式
(Empty)。NXP 無差異。

### 範例
- Raw：`21 10 00`

```text
  << RF_ISO_DEP_NAK_PRESENCE_CMD >>  
         (Empty)         
#end
```

<a id="rf_iso_dep_nak_presence_rsp"></a><a id="RF_ISO_DEP_NAK_PRESENCE_RSP"></a>
## RF_ISO_DEP_NAK_PRESENCE_RSP  (`41 10`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x10 / RSP |
| Handler | [`RF_Management.py:679`](../../nci_decoder/Nxp_pkg/RF_Management.py#L679) `RF_ISO_DEP_NAK_PRESENCE_RSP` |
| 實作方式 | Delegate → `Origin.RF_ISO_DEP_NAK_PRESENCE_RSP(raw, "nxp")`，詳見 [forum 版](../nfc_forum_2_0/RF_Management.md#rf_iso_dep_nak_presence_rsp) |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | NXP `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |

### 範例
- Raw：`41 10 01 E3`

```text
  << RF_ISO_DEP_NAK_PRESENCE_RSP >>  
  * Status: STATUS_PMU_TXLDO_OVERCURRENT (E3)
#end
```

### 實作備註
- ✅ 已修正（2026-10）：delegate 時補傳 `"nxp"`，改查 NXP `tbl_status_codes`，NXP 專屬狀態碼（如 `E3`）正確顯示為 `STATUS_PMU_TXLDO_OVERCURRENT`，與 [RF_ISO_DEP_NAK_PRESENCE_NTF](#rf_iso_dep_nak_presence_ntf) 一致。

<a id="rf_iso_dep_nak_presence_ntf"></a><a id="RF_ISO_DEP_NAK_PRESENCE_NTF"></a>
## RF_ISO_DEP_NAK_PRESENCE_NTF  (`61 10`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x10 / NTF |
| Handler | [`RF_Management.py:689`](../../nci_decoder/Nxp_pkg/RF_Management.py#L689) `RF_ISO_DEP_NAK_PRESENCE_NTF` |
| 實作方式 | Delegate → `Origin.RF_ISO_DEP_NAK_PRESENCE_NTF(raw, "nxp")`，詳見 [forum 版](../nfc_forum_2_0/RF_Management.md#rf_iso_dep_nak_presence_ntf) |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |

NXP 差異：使用 NXP 版 `tbl_status_codes`。

### 範例
- Raw：`61 10 01 E3`

```text
  << RF_ISO_DEP_NAK_PRESENCE_NTF >>  
  * Status: STATUS_PMU_TXLDO_OVERCURRENT (E3)
#end
```

<a id="rf_set_forced_nfcee_routing_cmd"></a><a id="RF_SET_FORCED_NFCEE_ROUTING_CMD"></a>
## RF_SET_FORCED_NFCEE_ROUTING_CMD  (`21 11`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x11 / CMD |
| Handler | [`RF_Management.py:699`](../../nci_decoder/Nxp_pkg/RF_Management.py#L699) `RF_SET_FORCED_NFCEE_ROUTING_CMD` |
| 實作方式 | NXP stub：印 `No Support`，回傳 0。forum 版有完整解析，參考 [forum 版](../nfc_forum_2_0/RF_Management.md#rf_set_forced_nfcee_routing_cmd) |

### Payload 格式（依 docstring，程式未解析）
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Forced NFCEE Routing State | 1 | 未解析 |
| 2 | Forced NFCEE Value Field | 0 或 2 | 未解析 |
| ﹂ | Forced NFCEE | 1 | 未解析 |
| ﹂ | Forced Power State | 1 | 未解析 |

### 範例
- Raw：`21 11 03 01 C0 3B`

```text
  << RF_SET_FORCED_NFCEE_ROUTING_CMD >>  
[NCI] control message No Support
Error: Payload error!!
  Packet Len: 6 Octet(s)
  Payload Len: 3 Octet(s)
  Check Len: 0.0 Octet(s)
#end
```

### 實作備註
- 回傳 0，payload 非空即觸發 `Payload error!!`。

<a id="rf_set_forced_nfcee_routing_rsp"></a><a id="RF_SET_FORCED_NFCEE_ROUTING_RSP"></a>
## RF_SET_FORCED_NFCEE_ROUTING_RSP  (`41 11`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x11 / RSP |
| Handler | [`RF_Management.py:713`](../../nci_decoder/Nxp_pkg/RF_Management.py#L713) `RF_SET_FORCED_NFCEE_ROUTING_RSP` |
| 實作方式 | NXP stub：印 `No Support`，回傳 0。參考 [forum 版](../nfc_forum_2_0/RF_Management.md#rf_set_forced_nfcee_routing_rsp) |

### Payload 格式（依 docstring，程式未解析）
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | 未解析 |

### 範例
- Raw：`41 11 01 00`

```text
  << RF_SET_FORCED_NFCEE_ROUTING_RSP >>  
[NCI] control message No Support
Error: Payload error!!
  Packet Len: 4 Octet(s)
  Payload Len: 1 Octet(s)
  Check Len: 0.0 Octet(s)
#end
```

### 實作備註
- 回傳 0，必然觸發 `Payload error!!`。

---

# Part 2：NXP SN2x0 擴充 NTF

以下 handler 皆為 NXP 版自行實作，不使用任何對照表。

<a id="iot_retry_ntf"></a><a id="IOT_RETRY_NTF"></a>
## IOT_RETRY_NTF  (`61 18`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x18 / NTF |
| Handler | [`RF_Management.py:724`](../../nci_decoder/Nxp_pkg/RF_Management.py#L724) `IOT_RETRY_NTF` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | WupCounter | 1 | 十六進位轉十進位印出。依程式註解：每送出一次對 WupA 的回應即遞增的計數器 |

### 範例
- Raw：`61 18 01 05`

```text
  << IOT_RETRY_NTF >>  
  * WupCounter: 5
#end
```

<a id="field_detect_ntf"></a><a id="FIELD_DETECT_NTF"></a>
## FIELD_DETECT_NTF  (`61 20`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x20 / NTF |
| Handler | [`RF_Management.py:736`](../../nci_decoder/Nxp_pkg/RF_Management.py#L736) `FIELD_DETECT_NTF` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Detection | 1 | 印 8-bit 二進位字串與 raw，再固定印出下列 bit 說明（不依實際值判斷） |
| 2 | RFU | 1 | 跳過，不印 |
| 3 | System Code | 2 | raw hex；若 Detection **bit3**（`& 0x08`，PollReq typeF）為 1，標示為 `POLL_REQ SC0-SC1`，否則標示 `System Code` |

Detection bit 說明（程式固定輸出的文字）：

| Bit | 意義 |
|---|---|
| 0 | RFU |
| 1 | WupA/ReqA detected |
| 2 | WupB/ReqB detected |
| 3 | PollReq (typeF) detected |
| 6 | RFU |
| 7 | RX error detected |

（bit4、bit5 程式未列出說明。）

### 範例
- Raw：`61 20 04 02 00 12 FC`

```text
  << FIELD_DETECT_NTF >>  
  * Detection: 00000010 (02)
   ~ Bit0 = RFU
   ~ Bit1 = WupA/ReqA detected
   ~ Bit2 = WupB/ReqB detected
   ~ Bit3 = PollReq (typeF) detected
   ~ Bit6 = RFU
   ~ Bit7 = RX error detected
  * System Code: 12FC
#end
```

- Raw（Detection = `10`，bit4 = 1，非 bit3，故仍標示 `System Code`）：`61 20 04 10 00 12 FC`

```text
  << FIELD_DETECT_NTF >>  
  * Detection: 00010000 (10)
   ~ Bit0 = RFU
   ~ Bit1 = WupA/ReqA detected
   ~ Bit2 = WupB/ReqB detected
   ~ Bit3 = PollReq (typeF) detected
   ~ Bit6 = RFU
   ~ Bit7 = RX error detected
  * System Code: 12FC
#end
```

### 實作備註
- ✅ 已修正（2026-10）：讀取 System Code 後 `p_payload` 會前進 2 octets，正常 4-octet payload 不再觸發 `Payload error!!`。
- ✅ 已修正（2026-10）：POLL_REQ 判斷改為 `int(detect, 16) & 0x08`（bit3），與說明一致：`08` → `POLL_REQ SC0-SC1`，`10` → `System Code`。
- Bit 說明為固定字串，不會依實際 bit 值顯示是否成立。

<a id="pll_unlocked_ntf"></a><a id="PLL_UNLOCKED_NTF"></a>
## PLL_UNLOCKED_NTF  (`61 21`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x21 / NTF |
| Handler | [`RF_Management.py:769`](../../nci_decoder/Nxp_pkg/RF_Management.py#L769) `PLL_UNLOCKED_NTF` |

### Payload 格式
(Empty)，只印 `(Empty)`，回傳 0。

### 範例
- Raw：`61 21 00`

```text
  << PLL_UNLOCKED_NTF >>  
         (Empty)         
#end
```

<a id="txldo_error_ntf"></a><a id="TxLDO_ERROR_NTF"></a>
## TxLDO_ERROR_NTF  (`61 23`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x23 / NTF |
| Handler | [`RF_Management.py:781`](../../nci_decoder/Nxp_pkg/RF_Management.py#L781) `TxLDO_ERROR_NTF` |

### Payload 格式
(Empty)，只印 `(Empty)`，回傳 0。

### 範例
- Raw：`61 23 00`

```text
  << TxLDO_ERROR_NTF >>  
         (Empty)         
#end
```

<a id="pll_lostlock_ntf"></a><a id="PLL_LOSTLOCK_NTF"></a>
## PLL_LOSTLOCK_NTF  (`61 28`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x28 / NTF |
| Handler | [`RF_Management.py:793`](../../nci_decoder/Nxp_pkg/RF_Management.py#L793) `PLL_LOSTLOCK_NTF` |

### Payload 格式
(Empty)，只印 `(Empty)`，回傳 0。

### 範例
- Raw：`61 28 00`

```text
  << PLL_LOSTLOCK_NTF >>  
         (Empty)         
#end
```

<a id="settings_change_ntf"></a><a id="SETTINGS_CHANGE_NTF"></a>
## SETTINGS_CHANGE_NTF  (`61 29`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x29 / NTF |
| Handler | [`RF_Management.py:805`](../../nci_decoder/Nxp_pkg/RF_Management.py#L805) `SETTINGS_CHANGE_NTF` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Index | 1 | 只印 raw hex。依程式註解：目前 settings change table 的 index |

### 範例
- Raw：`61 29 01 03`

```text
  << SETTINGS_CHANGE_NTF >>  
  * Index: 03
#end
```

<a id="rf_freq_error_ntf"></a><a id="RF_FREQ_ERROR_NTF"></a>
## RF_FREQ_ERROR_NTF  (`61 2A`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x2A / NTF |
| Handler | [`RF_Management.py:817`](../../nci_decoder/Nxp_pkg/RF_Management.py#L817) `RF_FREQ_ERROR_NTF` |

### Payload 格式
(Empty)，只印 `(Empty)`，回傳 0。

### 範例
- Raw：`61 2A 00`

```text
  << RF_FREQ_ERROR_NTF >>  
         (Empty)         
#end
```

<a id="lpdet_error_ntf"></a><a id="LPDET_ERROR_NTF"></a>
## LPDET_ERROR_NTF  (`61 2B`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x2B / NTF |
| Handler | [`RF_Management.py:829`](../../nci_decoder/Nxp_pkg/RF_Management.py#L829) `LPDET_ERROR_NTF` |

### Payload 格式
(Empty)，只印 `(Empty)`，回傳 0。

### 範例
- Raw：`61 2B 00`

```text
  << LPDET_ERROR_NTF >>  
         (Empty)         
#end
```
