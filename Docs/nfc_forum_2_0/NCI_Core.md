# NFC Forum NCI 2.0 — NCI Core (GID 0x0) Command 文件

本文件說明 `nfc_forum_2_0_pkg/NCI_Core.py` 中所有 NCI Core 控制訊息（GID = 0x0，OID 0x00–0x09）的解析方式。
Dispatch 依 `nfc_forum_2_0_pkg/__ctrl__.py` 的 `tbl_nci_ctrl["NCI Core"][oid][mt]` 呼叫對應 handler；handler 收到的是 3-byte header 之後的 payload hex 字串，
以 `p_payload`（hex 字元數 = 2×bytes）逐欄前進並回傳最終 offset，若與宣告的 Payload Length 不符，`Decoder_Main.py` 會印出 `Error: Payload error!!`。
對照表皆來自 `nfc_forum_2_0_pkg/__table__.py`，以 `range_lookup.lookup(NFC_table.tbl_xxx, value)` 查找（先精確 key，再比對 `'XX-YY'` 範圍 key，皆無則 `"RFU"`），詳細內容見 [Tables.md](Tables.md)。

> 注意：`Decoder_Main.py` 呼叫 handler 時只傳入 `raw`（`pkg.tbl_nci_ctrl[gid_val][oid][mt_val](raw[6::])`），`vendor`/`model` 一律使用預設值 `"None"`，因此 handler 內部的 `tbl_import` 永遠解析到 `nfc_forum_2_0_pkg.__table__`。

## 總覽

| OID | CMD | RSP | NTF |
|---|---|---|---|
| 0x00 | `20 00` [CORE_RESET_CMD](#core_reset_cmd--20-00) | `40 00` [CORE_RESET_RSP](#core_reset_rsp--40-00) | `60 00` [CORE_RESET_NTF](#core_reset_ntf--60-00) |
| 0x01 | `20 01` [CORE_INIT_CMD](#core_init_cmd--20-01) | `40 01` [CORE_INIT_RSP](#core_init_rsp--40-01) | — |
| 0x02 | `20 02` [CORE_SET_CONFIG_CMD](#core_set_config_cmd--20-02) | `40 02` [CORE_SET_CONFIG_RSP](#core_set_config_rsp--40-02) | — |
| 0x03 | `20 03` [CORE_GET_CONFIG_CMD](#core_get_config_cmd--20-03) | `40 03` [CORE_GET_CONFIG_RSP](#core_get_config_rsp--40-03) | — |
| 0x04 | `20 04` [CORE_CONN_CREATE_CMD](#core_conn_create_cmd--20-04) | `40 04` [CORE_CONN_CREATE_RSP](#core_conn_create_rsp--40-04) | — |
| 0x05 | `20 05` [CORE_CONN_CLOSE_CMD](#core_conn_close_cmd--20-05) | `40 05` [CORE_CONN_CLOSE_RSP](#core_conn_close_rsp--40-05) | — |
| 0x06 | — | — | `60 06` [CORE_CONN_CREDITS_NTF](#core_conn_credits_ntf--60-06) |
| 0x07 | — | — | `60 07` [CORE_GENERIC_ERROR_NTF](#core_generic_error_ntf--60-07) |
| 0x08 | — | — | `60 08` [CORE_INTERFACE_ERROR_NTF](#core_interface_error_ntf--60-08) |
| 0x09 | `20 09` [CORE_SET_POWER_SUB_STATE_CMD](#core_set_power_sub_state_cmd--20-09) | `40 09` [CORE_SET_POWER_SUB_STATE_RSP](#core_set_power_sub_state_rsp--40-09) | — |

共 10 個 OID、18 個 handler。另有共用函式 [VALUE_OF_CFG_PARA](#附錄value_of_cfg_para--config-parameter-value-解析) 負責 SET_CONFIG / GET_CONFIG 的參數值解析。

範例皆以下列方式實際執行（vendor = `'None'`，mode = 2 不印 raw）：

```
python -c "import sys; sys.path.insert(0, r'E:/Project/NCI_Decoder/NCI_Decoder/nci_decoder'); from Decoder_Main import NFC_NCI_DECODER; r='20000101'; NFC_NCI_DECODER(len(r)//2, r, 'None', 'None', 2)"
```

---

<a id="core_reset_cmd"></a><a id="CORE_RESET_CMD"></a>
## CORE_RESET_CMD  (`20 00`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NCI Core / 0x00 / CMD |
| Handler | [`NCI_Core.py:6`](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L6) `CORE_RESET_CMD` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Reset Type | 1 | `tbl_cfg_status`（見 [Tables](Tables.md#tbl_cfg_status)）：00 = Keep Config，01 = Reset Config，其他 RFU |

### 範例
- Raw：`20 00 01 01`

```text
  << CORE_RESET_CMD >>  
  * Reset Type: Reset Config (01)
#end
```

### 實作備註
- Reset Type 借用 `tbl_cfg_status`（Table 7: Configuration Status）解析；`__table__.py` 中原本的 Table 5 `tbl_rst_msg` 已註解掉，註解說明兩者內容相同。

---

<a id="core_reset_rsp"></a><a id="CORE_RESET_RSP"></a>
## CORE_RESET_RSP  (`40 00`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NCI Core / 0x00 / RSP |
| Handler | [`NCI_Core.py:22`](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L22) `CORE_RESET_RSP` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |

### 範例
- Raw：`40 00 01 00`

```text
  << CORE_RESET_RSP >>  
  * Status: STATUS_OK (00)
#end
```

---

<a id="core_reset_ntf"></a><a id="CORE_RESET_NTF"></a>
## CORE_RESET_NTF  (`60 00`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NCI Core / 0x00 / NTF |
| Handler | [`NCI_Core.py:37`](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L37) `CORE_RESET_NTF` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Reset Trigger | 1 | `tbl_rst_trig`（見 [Tables](Tables.md#tbl_rst_trig)） |
| 2 | Configuration Status | 1 | `tbl_cfg_status`（見 [Tables](Tables.md#tbl_cfg_status)） |
| 3 | NCI Version | 1 | `tbl_nci_ver`（見 [Tables](Tables.md#tbl_nci_ver)） |
| 4 | Manufacturer ID | 1 | `00` → 印 `Info is not available.`；其他值直接印 hex |
| 5 | Manufacturer Specific Information Length (n) | 1 | 轉 int 作為下一欄長度，不印出 |
| 6 | Manufacturer Specific Information | n | 只印 raw hex；n = 0 時整行不印 |

### 範例
- Raw：`60 00 09 02 01 20 04 04 AA BB CC DD`

```text
  << CORE_RESET_NTF >>  
  * Reset Trigger: CORE_RESET_CMD (02)
  * Config Status: Reset Config (01)
  * NCI Version: 2.0 (20)
  * Manufacturer ID: 04
  * Manufacturer Specific Info: AABBCCDD
#end
```

- Raw：`60 00 05 01 00 20 00 00`（Manufacturer ID = 00、Info Length = 0）

```text
  << CORE_RESET_NTF >>  
  * Reset Trigger: NFCC was powered on (01)
  * Config Status: Keep Config (00)
  * NCI Version: 2.0 (20)
  * Manufacturer ID: Info is not available.
#end
```

### 實作備註
- ✅ 已修正（2026-10）：輸出標籤已改為 `Reset Trigger`。
- ✅ 已修正（2026-10）：改以 `int(len, 16) != 0` 判斷，長度為 0 時不再印出 `Manufacturer Specific Info:` 行（見第二個範例）。
- `tbl_rst_trig` 的 `'name'` 欄寫的是 `Table 5: Control Messages to Reset the NFCC`，與其內容（Reset Trigger）不符。

---

<a id="core_init_cmd"></a><a id="CORE_INIT_CMD"></a>
## CORE_INIT_CMD  (`20 01`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NCI Core / 0x01 / CMD |
| Handler | [`NCI_Core.py:80`](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L80) `CORE_INIT_CMD` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Feature Enable | 2 | 只印 raw hex，後綴 `-- RFU` |

### 範例
- Raw：`20 01 02 00 00`

```text
  << CORE_INIT_CMD >>  
  * Feature Enable: 0000 -- RFU
#end
```

### 實作備註
- 逐 octet 的 bit 解析程式碼已被註解掉，未解析 Feature Enable 內容。

---

<a id="core_init_rsp"></a><a id="CORE_INIT_RSP"></a>
## CORE_INIT_RSP  (`40 01`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NCI Core / 0x01 / RSP |
| Handler | [`NCI_Core.py:97`](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L97) `CORE_INIT_RSP` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |
| 2 | NFCC Features | 4 | 先印 raw hex，再逐 octet 解 bit（見下表） |
| 3 | Max Logical Connections | 1 | ≥ 0x0F 且 vendor == `"None"` → `RFU`；否則印十進位 |
| 4 | Max Routing Table Size | 2 | little-endian 轉十進位，印 `<n> (raw)` |
| 5 | Max Control Packet Payload Size | 1 | < 32 → `Invalid size`；否則印十進位 |
| 6 | Max Data Packet Payload Size of the Static HCI Connection | 1 | 十進位 |
| 7 | Number of Credits of the Static HCI Connection | 1 | 十進位 |
| 8 | Max NFC-V RF Frame Size | 2 | little-endian 轉十進位，印 `<n> (raw)` |
| 9 | Number of Supported RF Interfaces (n) | 1 | 十進位 |
| 10 | Supported RF Interface [1..n] | x+2 每筆 | 先印剩餘所有 raw hex，再逐筆解析（見下） |
| ﹂ | Interface | 1 | `tbl_rf_if`（見 [Tables](Tables.md#tbl_rf_if)） |
| ﹂ | Number of Extensions (x) | 1 | 十進位 |
| ﹂ | Extension [0..x] | 1 each | `tbl_rf_if_exten`（見 [Tables](Tables.md#tbl_rf_if_exten)） |

#### NFCC Features bit 對應

| Octet | Bit | 欄位 | 解析 |
|---|---|---|---|
| 0 | b4 | Active Communication Mode | 1 = Support / 0 = Not support |
| 0 | b3 | HCI Network Support | 1 = Implements as defined in [ETSI_102622] / 0 = Not implement |
| 0 | b2–b1 | Discovery Cfg Mode | 00 = DH 為唯一設定者；01 = NFCC 可接收 DH 與其他 NFCEE 設定；其他 RFU |
| 0 | b0 | Discovery Freq Cfg | 1 = Supported in RF_DISCOVER_CMD / 0 = Ignored |
| 1 | b6..b1 | 路由能力 | `tbl_nfcc_feat_oct1`（見 [Tables](Tables.md#tbl_nfcc_feat_oct1)），key 為 bit 編號（int）；1 = Support |
| 2 | b3..b0 | 電源狀態能力 | `tbl_nfcc_feat_oct2`（見 [Tables](Tables.md#tbl_nfcc_feat_oct2)），key 為 bit 編號（int）；1 = Support |
| 3 | 全部 | Proprietary | 只印二進位，後綴 `-- Proprietary` |

### 範例
- Raw：`40 01 15 00 11 1E 0E 00 08 00 02 FF FF 01 01 00 03 01 00 02 00 03 01 01`

```text
  << CORE_INIT_RSP >>  
  * Status: STATUS_OK (00)
  * NFCC Features: 111E0E00

    * Octet 0: 00010001
     ~ Active Communication Mode:       Support
     ~ HCI Network Support:             Not implement
     ~ Discovery Cfg Mode:              The DH is the only entity that configs the NFCC.
     ~ Discovery Freq Cfg:              Supported in RF_DISCOVER_CMD

    * Octet 1: 00011110
     ~ Forced NFCEE routing:            Not support
     ~ APDU Pattern based routing:      Not support
     ~ System Code based routing:       Support
     ~ AID based routing:               Support
     ~ Protocol based routing:          Support
     ~ Technology based routing:        Support

    * Octet 2: 00001110
     ~ RF Cfg in Switched Off State:    Support
     ~ Switched On Sub-Mode States:     Support
     ~ Switched Off State:              Support
     ~ Battery Off State:               Not support

    * Octet 3: 00000000 -- Proprietary

  * Max Logical Connections: 8 (08)
  * Max Routing Table Size: 512 (0002)
  * Max Control Packet Payload Size: 255 (FF)
  * Max Data Packet Payload Size of the Static HCI Connection: 255 (FF)
  * Number of Credits of the Static HCI Connection: 1 (01)
  * Max NFC-V RF Frame Size: 1 (0100)
  * Number of Supported RF Interfaces: 3
  * Supported RF Interface: 01000200030101

   ~ [RF_IF_0] ~  
    * Interface: Frame (01)
    * Number of Extensions: 0

   ~ [RF_IF_1] ~  
    * Interface: ISO-DEP (02)
    * Number of Extensions: 0

   ~ [RF_IF_2] ~  
    * Interface: NFC-DEP (03)
    * Number of Extensions: 1
    * Extension 0: LLCP Symmetry RF Interface Extension (01)
#end
```

### 實作備註
- ✅ 已修正（2026-10）：Max Routing Table Size、Max NFC-V RF Frame Size 以 little-endian 轉十進位並附 raw hex（如 `512 (0002)`）。
- `Supported RF Interface:` 行印的是 `raw[p_payload:]`（payload 剩餘全部內容），而非僅限 RF Interface 區段。
- Max Logical Connections 的 RFU 判斷依賴 `vendor == "None"`；由於 dispatch 不傳 vendor，實際上永遠成立。
- 各 octet 中未列出的 bit（例如 Octet 0 b7–b5、Octet 1 b7/b0、Octet 2 b7–b4）不解析。

---

<a id="core_set_config_cmd"></a><a id="CORE_SET_CONFIG_CMD"></a>
## CORE_SET_CONFIG_CMD  (`20 02`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NCI Core / 0x02 / CMD |
| Handler | [`NCI_Core.py:232`](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L232) `CORE_SET_CONFIG_CMD` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Number of Parameters (n) | 1 | 十進位 |
| 2 | Parameter [1..n]（TLV） | m+2 每筆 | 每筆印 `~ [Param_i] ~` |
| ﹂ | ID (Type) | 1 | `tbl_cfg_para`（見 [Tables](Tables.md#tbl_cfg_para)） |
| ﹂ | Len (m) | 1 | 十進位 |
| ﹂ | Val | m | m ≠ 0 時交給 [`VALUE_OF_CFG_PARA`](#附錄value_of_cfg_para--config-parameter-value-解析) 依 ID 解析；m = 0 不印 Val |

### 範例
- Raw：`20 02 0E 04 00 02 E8 03 02 01 01 32 01 60 80 01 01`

```text
  << CORE_SET_CONFIG_CMD >>  
  * Number of Params: 4

   ~ [Param_0] ~  
    * ID: TOTAL_DURATION (00)
    * Len: 2
    * Val: 1000 ms (E803)

   ~ [Param_1] ~  
    * ID: CON_DISCOVERY_PARAM (02)
    * Len: 1
    * Val: 00000001 (01)
     ~ Polling Mode: Enabled
     ~ DH-NFCEE:     Enabled

   ~ [Param_2] ~  
    * ID: LA_SEL_INFO (32)
    * Len: 1
    * Val: 01100000 (60)
     ~ NFC-DEP Protocol: Supported
     ~ ISO-DEP Protocol: Supported

   ~ [Param_3] ~  
    * ID: RF_FIELD_INFO (80)
    * Len: 1
    * Val: 01
     ~ RF_FIELD_INFO_NTF: Enabled
#end
```

### 實作備註
- ✅ 已修正（2026-10）：ID 改用 `range_lookup.lookup` 查表，範圍 key 可命中（如 `05` → `RFU`、`A0`–`FE` → `Reserved`）。

---

<a id="core_set_config_rsp"></a><a id="CORE_SET_CONFIG_RSP"></a>
## CORE_SET_CONFIG_RSP  (`40 02`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NCI Core / 0x02 / RSP |
| Handler | [`NCI_Core.py:275`](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L275) `CORE_SET_CONFIG_RSP` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |
| 2 | Number of Parameters (n) | 1 | 十進位 |
| 3 | Parameter ID [0..n] | 1 each | `tbl_cfg_para`（見 [Tables](Tables.md#tbl_cfg_para)）；n = 0 時不印 `Set Param ID:` |

### 範例
- Raw：`40 02 04 09 02 33 50`

```text
  << CORE_SET_CONFIG_RSP >>  
  * Status: STATUS_INVALID_PARAM (09)
  * Number of Params: 2
  * Set Param ID:
    * ID 0: LA_NFCID1 (33)
    * ID 1: LF_PROTOCOL_TYPE (50)
#end
```

---

<a id="core_get_config_cmd"></a><a id="CORE_GET_CONFIG_CMD"></a>
## CORE_GET_CONFIG_CMD  (`20 03`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NCI Core / 0x03 / CMD |
| Handler | [`NCI_Core.py:306`](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L306) `CORE_GET_CONFIG_CMD` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Number of Parameters (n) | 1 | 十進位 |
| 2 | Parameter ID [0..n] | 1 each | `tbl_cfg_para`（見 [Tables](Tables.md#tbl_cfg_para)） |

### 範例
- Raw：`20 03 03 02 00 80`

```text
  << CORE_GET_CONFIG_CMD >>  
  * Number of Params: 2
  * Get Param ID:
    * ID 0: TOTAL_DURATION (00)
    * ID 1: RF_FIELD_INFO (80)
#end
```

### 實作備註
- 與 SET_CONFIG_RSP 不同，n = 0 時仍會印出 `Get Param ID:` 標題。

---

<a id="core_get_config_rsp"></a><a id="CORE_GET_CONFIG_RSP"></a>
## CORE_GET_CONFIG_RSP  (`40 03`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NCI Core / 0x03 / RSP |
| Handler | [`NCI_Core.py:331`](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L331) `CORE_GET_CONFIG_RSP` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |
| 2 | Number of Parameters (n) | 1 | 十進位 |
| 3 | Parameter [1..n]（TLV） | m+2 每筆 | 每筆印 `~ [Param_i] ~` |
| ﹂ | ID (Type) | 1 | `tbl_cfg_para`（見 [Tables](Tables.md#tbl_cfg_para)） |
| ﹂ | Len (m) | 1 | 十進位 |
| ﹂ | Val | m | m ≠ 0 時交給 [`VALUE_OF_CFG_PARA`](#附錄value_of_cfg_para--config-parameter-value-解析)；m = 0 不印 Val |

### 範例
- Raw：`40 03 09 00 02 00 02 F4 01 83 01 11`

```text
  << CORE_GET_CONFIG_RSP >>  
  * Status: STATUS_OK (00)
  * Number of Params: 2

   ~ [Param_0] ~  
    * ID: TOTAL_DURATION (00)
    * Len: 2
    * Val: 500 ms (F401)

   ~ [Param_1] ~  
    * ID: LLCP_VERSION (83)
    * Len: 1
    * Val: 1.1 (11)
#end
```

完整涵蓋 `VALUE_OF_CFG_PARA` 所有分支的範例見[附錄](#完整範例涵蓋所有分支)。

---

<a id="core_conn_create_cmd"></a><a id="CORE_CONN_CREATE_CMD"></a>
## CORE_CONN_CREATE_CMD  (`20 04`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NCI Core / 0x04 / CMD |
| Handler | [`NCI_Core.py:378`](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L378) `CORE_CONN_CREATE_CMD` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Destination Type | 1 | `tbl_dest_type`（見 [Tables](Tables.md#tbl_dest_type)） |
| 2 | Number of Destination-specific Parameters (n) | 1 | 十進位 |
| 3 | Destination-specific Parameter [0..n]（TLV） | m+2 每筆 | 每筆印 `~ [Dest-spec Parameter_i] ~` |
| ﹂ | Type | 1 | `tbl_d_spec_type`（見 [Tables](Tables.md#tbl_d_spec_type)） |
| ﹂ | Len (m) | 1 | 十進位 |
| ﹂ | Val | m | 先印 raw hex，再依 Type 分支解析（見下） |

#### Val 依 Type 分支

| Type | Val Octet | 欄位 | 解析 |
|---|---|---|---|
| `00` | 0 | RF Discovery ID | `lookup(tbl_rf_dis_id, v)`（見 [Tables](Tables.md#tbl_rf_dis_id)）：`00`/`FF` → `RFU`，`01`–`FE` → `Dynamically assigned by the NFCC`；印 `<text> (raw)` |
| `00` | 1 | RF Protocol | `tbl_rf_proto`（見 [Tables](Tables.md#tbl_rf_proto)） |
| `01` | 0 | NFCEE ID | `lookup(tbl_nfcee_id, v)`（見 [Tables](Tables.md#tbl_nfcee_id)），去掉表值外層括號後印 `<text> (raw)`：`00` → `DH-NFCEE`、`01` → `HCI-NTWK-NFCEE (RFU)`、`02`–`0F` → `Static IDs`、`10`–`7F` → `NFCEE`、`80`–`FE` → `HCI-NFCEE`、`FF` → `RFU` |
| `01` | 1 | NFCEE Interface Protocol | `tbl_nfcee_proto`（見 [Tables](Tables.md#tbl_nfcee_proto)） |
| 其他 | — | — | 印一行 `~ Type <xx>: For proprietary use`（Type ≥ 0xA0）或 `~ Type <xx>: RFU`（其他） |

### 範例
- Raw：`20 04 06 02 01 00 02 01 04`（Remote NFC Endpoint）

```text
  << CORE_CONN_CREATE_CMD >>  
  * Destination Type: Remote NFC Endpoint (02)
  * Number of Destination-specific Params: 1

   ~ [Dest-spec Parameter_0] ~  
    * Type: RF Discovery ID + RF Protocol (00)
    * Len: 2
    * Val: 0104
      * RF Discovery ID: Dynamically assigned by the NFCC (01)
      * RF Protocol: ISO-DEP (04)
#end
```

- Raw：`20 04 06 03 01 01 02 80 00`（NFCEE）

```text
  << CORE_CONN_CREATE_CMD >>  
  * Destination Type: NFCEE (03)
  * Number of Destination-specific Params: 1

   ~ [Dest-spec Parameter_0] ~  
    * Type: NFCEE ID + NFCEE Interface Protocol (01)
    * Len: 2
    * Val: 8000
      * NFCEE ID: HCI-NFCEE (80)
      * NFCEE Interface Protocol: APDU (00)
#end
```

### 實作備註
- ✅ 已修正（2026-10）：NFCEE ID 只印一行，依實際值所屬範圍顯示對應名稱。
- ✅ 已修正（2026-10）：NFCEE ID 改用 `lookup(tbl_nfcee_id, ...)` 查表（含範圍 key）。
- ✅ 已修正（2026-10）：RF Discovery ID 改用 `lookup`，`01`–`FE` 命中 `'01-FF'` 範圍 key 顯示 `Dynamically assigned by the NFCC`，`FF` 仍為 `RFU`。
- ✅ 已修正（2026-10）：未知 Type 時 `Val:` 只印一次，另附一行 `~ Type <xx>: For proprietary use / RFU`。
- `tbl_dest_type` 無 `00` 項，0x00 及 0x04 以上顯示 `RFU`。

---

<a id="core_conn_create_rsp"></a><a id="CORE_CONN_CREATE_RSP"></a>
## CORE_CONN_CREATE_RSP  (`40 04`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NCI Core / 0x04 / RSP |
| Handler | [`NCI_Core.py:448`](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L448) `CORE_CONN_CREATE_RSP` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |
| 2 | Max Data Packet Payload Size | 1 | 十進位 |
| 3 | Initial Number of Credits | 1 | 若在 `tbl_init_credits`（見 [Tables](Tables.md#tbl_init_credits)）中（`FF`）印對應文字，否則十進位 |
| 4 | Conn ID | 1 | 取低 4 bits（`& 0x0F`）印十進位 +（以 4 位二進位字串查 `tbl_conn_id`，見 [Tables](Tables.md#tbl_conn_id)；查無則 `Dynamically assigned by the NFCC`） |

### 範例
- Raw：`40 04 04 00 FF FF 02`

```text
  << CORE_CONN_CREATE_RSP >>  
  * Status: STATUS_OK (00)
  * Max Data Packet Payload Size: 255
  * Initial Number of Credits: Data flow control is not used
  * Conn ID: 2 (Dynamically assigned by the NFCC)
#end
```

### 實作備註
- ✅ 已修正（2026-10）：Conn ID 十進位值與表查找一致，皆取低 4 bits（`& 0x0F`）。
- `tbl_conn_id` 的範圍 key `'0010-1111'`（4 位二進位，非 `XX-YY` hex 形式）仍不會命中，靠預設字串 `Dynamically assigned by the NFCC` 顯示。

---

<a id="core_conn_close_cmd"></a><a id="CORE_CONN_CLOSE_CMD"></a>
## CORE_CONN_CLOSE_CMD  (`20 05`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NCI Core / 0x05 / CMD |
| Handler | [`NCI_Core.py:482`](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L482) `CORE_CONN_CLOSE_CMD` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Conn ID | 1 | 同 CORE_CONN_CREATE_RSP：低 4 bits 十進位 + 查 `tbl_conn_id`（見 [Tables](Tables.md#tbl_conn_id)） |

### 範例
- Raw：`20 05 01 02`

```text
  << CORE_CONN_CLOSE_CMD >>  
  * Conn ID: 2 (Dynamically assigned by the NFCC)
#end
```

### 實作備註
- ✅ 已修正（2026-10）：改用共用的 `CONN_ID_TEXT`，輸出 `<n> (<text>)` 括號完整。

---

<a id="core_conn_close_rsp"></a><a id="CORE_CONN_CLOSE_RSP"></a>
## CORE_CONN_CLOSE_RSP  (`40 05`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NCI Core / 0x05 / RSP |
| Handler | [`NCI_Core.py:498`](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L498) `CORE_CONN_CLOSE_RSP` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |

### 範例
- Raw：`40 05 01 00`

```text
  << CORE_CONN_CLOSE_RSP >>  
  * Status: STATUS_OK (00)
#end
```

---

<a id="core_conn_credits_ntf"></a><a id="CORE_CONN_CREDITS_NTF"></a>
## CORE_CONN_CREDITS_NTF  (`60 06`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NCI Core / 0x06 / NTF |
| Handler | [`NCI_Core.py:514`](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L514) `CORE_CONN_CREDITS_NTF` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Number of Entries (n) | 1 | 十進位 |
| 2 | Entry [1..n] | 2 每筆 | 每筆印 `~ [Entry_i] ~` |
| ﹂ | Conn ID | 1 | 低 4 bits 十進位 + 查 `tbl_conn_id`（見 [Tables](Tables.md#tbl_conn_id)） |
| ﹂ | Credits | 1 | 十進位 |

### 範例
- Raw：`60 06 05 02 00 01 02 03`

```text
  << CORE_CONN_CREDITS_NTF >>  
  * Number of Entries: 2

   ~ [Entry_0] ~  
    * Conn ID: 0 (Static: DH -- Remote NFC Endpoint)
    * Credits: 1

   ~ [Entry_1] ~  
    * Conn ID: 2 (Dynamically assigned by the NFCC)
    * Credits: 3
#end
```

---

<a id="core_generic_error_ntf"></a><a id="CORE_GENERIC_ERROR_NTF"></a>
## CORE_GENERIC_ERROR_NTF  (`60 07`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NCI Core / 0x07 / NTF |
| Handler | [`NCI_Core.py:549`](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L549) `CORE_GENERIC_ERROR_NTF` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |

### 範例
- Raw：`60 07 01 B2`

```text
  << CORE_GENERIC_ERROR_NTF >>  
  * Status: RF_TIMEOUT_EXCEPTION (B2)
#end
```

---

<a id="core_interface_error_ntf"></a><a id="CORE_INTERFACE_ERROR_NTF"></a>
## CORE_INTERFACE_ERROR_NTF  (`60 08`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NCI Core / 0x08 / NTF |
| Handler | [`NCI_Core.py:565`](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L565) `CORE_INTERFACE_ERROR_NTF` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |
| 2 | Conn ID | 1 | 低 4 bits 十進位 + 查 `tbl_conn_id`（見 [Tables](Tables.md#tbl_conn_id)） |

### 範例
- Raw：`60 08 02 B0 00`

```text
  << CORE_INTERFACE_ERROR_NTF >>  
  * Status: RF_TRANSMISSION_EXCEPTION (B0)
  * Conn ID: 0 (Static: DH -- Remote NFC Endpoint)
#end
```

### 實作備註
- ✅ 已修正（2026-10）：改用共用的 `CONN_ID_TEXT`，括號完整且 `Conn ID:` 後只有一個空白。

---

<a id="core_set_power_sub_state_cmd"></a><a id="CORE_SET_POWER_SUB_STATE_CMD"></a>
## CORE_SET_POWER_SUB_STATE_CMD  (`20 09`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NCI Core / 0x09 / CMD |
| Handler | [`NCI_Core.py:586`](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L586) `CORE_SET_POWER_SUB_STATE_CMD` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Power State | 1 | if/elif 硬寫（無對照表），見下表 |

| 值 | Power State | Screen | Device |
|---|---|---|---|
| `00` | Switched On State | On | Unlocked |
| `01` | Switched On Sub-State 1 | Off | Unlocked |
| `02` | Switched On Sub-State 2 | On | Locked |
| `03` | Switched On Sub-State 3 | Off | Locked |
| 其他 | `RFU (xx)` | — | — |

### 範例
- Raw：`20 09 01 03`

```text
  << CORE_SET_POWER_SUB_STATE_CMD >>  
  * Power State: Switched On Sub-State 3
    * Screen: Off
    * Device: Locked
#end
```

### 實作備註
- ✅ 已修正（2026-10）：`03`（Sub-State 3）改印 `Screen: Off / Device: Locked`，與 `tbl_pwr_state`（Table 59）的 `Screen Off lock` 一致。

---

<a id="core_set_power_sub_state_rsp"></a><a id="CORE_SET_POWER_SUB_STATE_RSP"></a>
## CORE_SET_POWER_SUB_STATE_RSP  (`40 09`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NCI Core / 0x09 / RSP |
| Handler | [`NCI_Core.py:619`](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L619) `CORE_SET_POWER_SUB_STATE_RSP` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |

### 範例
- Raw：`40 09 01 00`

```text
  << CORE_SET_POWER_SUB_STATE_RSP >>  
  * Status: STATUS_OK (00)
#end
```

---

## 附錄：VALUE_OF_CFG_PARA — Config Parameter Value 解析

| 項目 | 值 |
|---|---|
| Handler | [`NCI_Core.py:656`](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L656) `VALUE_OF_CFG_PARA(id, val, NFC_table)` |
| 呼叫者 | CORE_SET_CONFIG_CMD、CORE_GET_CONFIG_RSP（僅在 Len ≠ 0 時呼叫） |
| 長度檢查 | 1-octet bit-field 參數（`CFG_BITFIELD_1OCT`：`02`、`13`、`2A`、`30`、`31`、`32`、`38`、`3C`、`50`、`5C`、`62`、`82`、`85`）若 Len > 1，只以第 1 octet 解析，並在該參數輸出最後加一行 `* Warning: Len <m>, expected 1 (raw <val>)` |
| ID 名稱表 | `tbl_cfg_para`（見 [Tables](Tables.md#tbl_cfg_para)） |

`id` 為 1-octet hex 字串（大寫），`val` 為整段 Value 的 hex 字串。下表中的 bit 編號以 b7（MSB）… b0（LSB）表示；程式內以 `val_b = bin(int(val,16))[2:].zfill(8)` 取得字串，`val_b[k]` 對應 b(7−k)。

### 程式支援的 Parameter ID 與 Value 解析方式

| ID | 名稱 | Value 解析方式 |
|---|---|---|
| `00` | TOTAL_DURATION | 取前 2 octets 以 little-endian 轉十進位，印 `<n> ms (raw)` |
| `02` | CON_DISCOVERY_PARAM | 印 8-bit 二進位；b0 = 1 → `Polling Mode: Enabled`，否則 Disabled；b1 = 1 → `DH-NFCEE: Disabled`，否則 Enabled |
| `03` | POWER_STATE | 印 raw；`02` → `Current CORE_GET_CONFIG_CMD apply for Switched Off State`，其他 → `RFU` |
| `08` / `11` / `19` | PA_BAIL_OUT / PB_BAIL_OUT / PF_BAIL_OUT | 印 raw；`00` → Not apply，`01` → Apply，其他 → RFU；技術名稱依 ID 對應 NFC-A / NFC-B / NFC-F |
| `09` / `14` / `1A` / `2F` | PA / PB / PF / PV_DEVICES_LIMIT | 印 raw + 固定說明 `As defined in [ACTIVITY] for the Collision Resolution Activity.` |
| `10` | PB_AFI | 印 raw + 固定說明（Application family identifier） |
| `12` | PB_ATTRIB_PARAM1 | 印 raw + 固定說明（ATTRIB Param 1） |
| `13` | PB_SENSB_REQ_PARAM | 印 8-bit 二進位；b4 = 1 → `Extended SENSB_RES: Support`，否則 Not support |
| `18` / `21` / `3E` / `5B` / `68` | PF_BIT_RATE / PI_BIT_RATE / LB_BIT_RATE / LI_A_BIT_RATE / PACM_BIT_RATE | `BIT_RATE_TEXT`：查 `tbl_bit_rates`（見 [Tables](Tables.md#tbl_bit_rates)）；未定義值中 `80`–`FE` → `For proprietary use`，其餘 → `RFU` |
| `20` | PI_B_H_INFO | 印 raw + 固定說明（Higher layer INF of ATTRIB） |
| `28` | PN_NFC_DEP_PSL | 印 raw；`00` → Highest available，`01` → Maintain，其他 → RFU |
| `29` | PN_ATR_REQ_GEN_BYTES | 印 raw + 固定說明 `General Bytes for ATR_REQ.` |
| `2A` / `62` | PN_ATR_REQ_CONFIG / LN_ATR_RES_CONFIG | 印 8-bit 二進位 + `NOTE: Needs to be always set to 0x30 for LLCP`；`Value for LR` = b5–b4 |
| `30` | LA_BIT_FRAME_SDD | 印 8-bit 二進位 + 固定說明（5-bit value，SENS_RES Byte 1） |
| `31` | LA_PLATFORM_CONFIG | 印 8-bit 二進位 + 固定說明（4-bit value，SENS_RES Byte 2） |
| `32` | LA_SEL_INFO | 印 8-bit 二進位；b6 → NFC-DEP Protocol Supported/Not supported；b5 → ISO-DEP Protocol Supported/Not supported |
| `33` | LA_NFCID1 | 印 raw + 固定說明 |
| `38` | LB_SENSB_INFO | 印 8-bit 二進位；b0 → ISO-DEP Protocol Supported/Not supported |
| `39` | LB_NFCID0 | 印 raw + 固定說明 |
| `3A` | LB_APPLICATION_DATA | 印 raw + 固定說明（SENSB_RES Bytes 6-9） |
| `3B` | LB_SFGI | 印 raw + 固定說明 |
| `3C` | LB_FWI_ADC_FO | 印 8-bit 二進位；FWI = b7–b4（十進位 + 二進位）；ADC b3 欄位印 b3 的值；DID 印 b0 的值 |
| `40`–`4F` | LF_T3T_IDENTIFIERS_1..16 | 印 raw；`val[0:4]` = System Code（2 octets），`val[4:20]` = NFCID2（8 octets），`val[20:36]` = PAD0/PAD1/MRTI_check/MRTI_update/PAD2（8 octets） |
| `50` | LF_PROTOCOL_TYPE | 印 8-bit 二進位；b1 → NFC-DEP Protocol Supported/Not supported |
| `52` | LF_T3T_MAX | 值 ≤ 16 印十進位，否則 `RFU (raw)` |
| `53` | LF_T3T_FLAGS | 2 octets；印兩個 8-bit 二進位；Octet0 b0..b7 對應 IDENTIFIERS_1..8，Octet1 b0..b7 對應 IDENTIFIERS_9..16；1 = Enabled，0 = Disabled |
| `55` | LF_T3T_RD_ALLOWED | `00` → SHALL NOT include RD bytes；`01` → MAY include RD bytes；其他 → `RFU (raw)` |
| `58` | LI_A_RATS_TB1 | 印 raw + 固定說明 |
| `59` | LI_A_HIST_BY | 印 raw + 固定說明（Historical Bytes） |
| `5A` | LI_B_H_INFO_RESP | 印 raw + 固定說明 |
| `5C` | LI_A_RATS_TC1 | 印 8-bit 二進位；DID 說明後附 b1 的值 |
| `60` | LN_WT | WT 指數：印 `<n> (raw)`；n ≤ 14 時附 `RWT = 256*16/fc * 2^WT = <x.xxx> ms`，n > 14 附 `RFU (WT > 14)` |
| `61` | LN_ATR_RES_GEN_BYTES | 印 raw + 固定說明 |
| `80` | RF_FIELD_INFO | `00` → `RF_FIELD_INFO_NTF: Disabled`；`01` → Enabled；其他 → `RFU (raw)` |
| `81` | RF_NFCEE_ACTION | `00` → `RF_NFCEE_ACTION_NTF: Disabled`；`01` → Enabled；其他 → `RFU (raw)` |
| `82` | NFCDEP_OP | 印 8-bit 二進位；b4：1 → `Waiting Time: <= 10`，0 → `<= WT_(NFCDEP,MAX)`；b3 = 1 → chaining PDU 必須用最大 Transport Data Bytes；b2 = 1 → 不送無資料 Info PDU；b1 = 1 → Initiator 僅以 ATTENTION 做錯誤復原；b0 = 1 → Target 不送 RTOX（各 bit 為 0 時不印） |
| `83` | LLCP_VERSION | 高 nibble = major、低 nibble = minor，印 `major.minor (raw)` |
| `85` | NFCC_CONFIG_CONTROL | 印 8-bit 二進位；b0 = 0 → NFCC is not allowed to manage RF config；b0 = 1 → allowed |
| 其他 | （含 RFU、0xA0–0xFE proprietary、`84` 等；ID 名稱經 `lookup` 範圍 key 顯示 `RFU` / `Reserved`） | 只印 `Val: <raw>` |

### 完整範例（涵蓋所有分支）
- Raw：

```
40 03 B7 00 31 00 02 E8 03 02 01 03 03 01 02 08 01 01 11 01 00 19 01 05 09 01 01 14 01 02 1A 01 01 2F 01 01 10 01 00 12 01 00 13 01 10 18 01 01 21 01 02 3E 01 00 5B 01 03 68 01 07 20 02 AA BB 28 01 00 29 03 46 66 6D 2A 01 30 62 01 30 30 01 04 31 01 0C 32 01 60 33 04 01 02 03 04 38 01 01 39 04 11 22 33 44 3A 04 00 00 00 00 3B 01 00 3C 01 75 40 12 02 FE 01 FE 00 00 00 00 00 00 FF FF FF FF FF FF FF FF 52 01 10 53 02 03 80 55 01 01 50 01 02 58 01 70 59 02 80 00 5A 01 00 5C 01 02 60 01 0E 61 03 46 66 6D 80 01 01 81 01 00 82 01 1F 83 01 11 85 01 01 A0 01 55
```

```text
  << CORE_GET_CONFIG_RSP >>  
  * Status: STATUS_OK (00)
  * Number of Params: 49

   ~ [Param_0] ~  
    * ID: TOTAL_DURATION (00)
    * Len: 2
    * Val: 1000 ms (E803)

   ~ [Param_1] ~  
    * ID: CON_DISCOVERY_PARAM (02)
    * Len: 1
    * Val: 00000011 (03)
     ~ Polling Mode: Enabled
     ~ DH-NFCEE:     Disabled

   ~ [Param_2] ~  
    * ID: POWER_STATE (03)
    * Len: 1
    * Val: 02
     ~ Current CORE_GET_CONFIG_CMD apply for Switched Off State

   ~ [Param_3] ~  
    * ID: PA_BAIL_OUT (08)
    * Len: 1
    * Val: 01
     ~ Bail out when NFC-A Technology has been detected: Apply

   ~ [Param_4] ~  
    * ID: PB_BAIL_OUT (11)
    * Len: 1
    * Val: 00
     ~ Bail out when NFC-B Technology has been detected: Not apply

   ~ [Param_5] ~  
    * ID: PF_BAIL_OUT (19)
    * Len: 1
    * Val: 05
     ~ Bail out when NFC-F Technology has been detected: RFU

   ~ [Param_6] ~  
    * ID: PA_DEVICES_LIMIT (09)
    * Len: 1
    * Val: 01
     ~ As defined in [ACTIVITY] for the Collision Resolution Activity.

   ~ [Param_7] ~  
    * ID: PB_DEVICES_LIMIT (14)
    * Len: 1
    * Val: 02
     ~ As defined in [ACTIVITY] for the Collision Resolution Activity.

   ~ [Param_8] ~  
    * ID: PF_DEVICES_LIMIT (1A)
    * Len: 1
    * Val: 01
     ~ As defined in [ACTIVITY] for the Collision Resolution Activity.

   ~ [Param_9] ~  
    * ID: PV_DEVICES_LIMIT (2F)
    * Len: 1
    * Val: 01
     ~ As defined in [ACTIVITY] for the Collision Resolution Activity.

   ~ [Param_10] ~  
    * ID: PB_AFI (10)
    * Len: 1
    * Val:  00
     ~ Application family identifier (as defined in [DIGITAL]).

   ~ [Param_11] ~  
    * ID: PB_ATTRIB_PARAM1 (12)
    * Len: 1
    * Val: 00
     ~ The values and coding of this parameter SHALL be as defined in [DIGITAL] for Param 1 of the ATTRIB command.

   ~ [Param_12] ~  
    * ID: PB_SENSB_REQ_PARAM (13)
    * Len: 1
    * Val: 00010000 (10)
     ~ Extended SENSB_RES: Support

   ~ [Param_13] ~  
    * ID: PF_BIT_RATE (18)
    * Len: 1
    * Val: 212 Kbit/s (01)

   ~ [Param_14] ~  
    * ID: PI_BIT_RATE (21)
    * Len: 1
    * Val: 424 Kbit/s (02)

   ~ [Param_15] ~  
    * ID: LB_BIT_RATE (3E)
    * Len: 1
    * Val: 106 Kbit/s (00)

   ~ [Param_16] ~  
    * ID: LI_A_BIT_RATE (5B)
    * Len: 1
    * Val: 848 Kbit/s (03)

   ~ [Param_17] ~  
    * ID: PACM_BIT_RATE (68)
    * Len: 1
    * Val: RFU (07)

   ~ [Param_18] ~  
    * ID: PI_B_H_INFO (20)
    * Len: 2
    * Val: AABB
     ~ Higher layer INF field of the ATTRIB Command (as defined in [DIGITAL]).

   ~ [Param_19] ~  
    * ID: PN_NFC_DEP_PSL (28)
    * Len: 1
    * Val: 00
     ~ Bit Rates and Length Reduction: Highest available

   ~ [Param_20] ~  
    * ID: PN_ATR_REQ_GEN_BYTES (29)
    * Len: 3
    * Val: 46666D
     ~ General Bytes for ATR_REQ.

   ~ [Param_21] ~  
    * ID: PN_ATR_REQ_CONFIG (2A)
    * Len: 1
    * Val: 00110000 (30)
     ~ NOTE: Needs to be always set to 0x30 for LLCP
     ~ Value for LR: 11

   ~ [Param_22] ~  
    * ID: LN_ATR_RES_CONFIG (62)
    * Len: 1
    * Val: 00110000 (30)
     ~ NOTE: Needs to be always set to 0x30 for LLCP
     ~ Value for LR: 11

   ~ [Param_23] ~  
    * ID: LA_BIT_FRAME_SDD (30)
    * Len: 1
    * Val: 00000100 (04)
     ~ Bit Frame SDD value to be sent in Byte 1 of SENS_RES. This is a 5-bit value.

   ~ [Param_24] ~  
    * ID: LA_PLATFORM_CONFIG (31)
    * Len: 1
    * Val: 00001100 (0C)
     ~ Platform Configuration value to be sent in Byte 2 of SENS_RES. This is a 4-bit value.

   ~ [Param_25] ~  
    * ID: LA_SEL_INFO (32)
    * Len: 1
    * Val: 01100000 (60)
     ~ NFC-DEP Protocol: Supported
     ~ ISO-DEP Protocol: Supported

   ~ [Param_26] ~  
    * ID: LA_NFCID1 (33)
    * Len: 4
    * Val: 01020304
     ~ NFCID1 as defined in [DIGITAL].

   ~ [Param_27] ~  
    * ID: LB_SENSB_INFO (38)
    * Len: 1
    * Val: 00000001 (01)
     ~ ISO-DEP Protocol: Supported

   ~ [Param_28] ~  
    * ID: LB_NFCID0 (39)
    * Len: 4
    * Val: 11223344
     ~ NFCID0 as defined in [DIGITAL].

   ~ [Param_29] ~  
    * ID: LB_APPLICATION_DATA (3A)
    * Len: 4
    * Val: 00000000
     ~ Application Data (Bytes 6-9) of SENSB_RES (as defined in [DIGITAL]).

   ~ [Param_30] ~  
    * ID: LB_SFGI (3B)
    * Len: 1
    * Val: 00
     ~ Start-Up Frame Guard Time, as defined in [DIGITAL].

   ~ [Param_31] ~  
    * ID: LB_FWI_ADC_FO (3C)
    * Len: 1
    * Val: 01110101 (75)
     ~ Frame Waiting time Integer: 7 (0111)
     ~ b3 of ADC Coding field of SENSB_RES (Byte 12) as defined in [DIGITAL] (0)
     ~ If set to 1b DID MAY be used. Otherwise it SHALL NOT be used. (1)

   ~ [Param_32] ~  
    * ID: LF_T3T_IDENTIFIERS_1 (40)
    * Len: 18
    * Val: 02FE01FE000000000000FFFFFFFFFFFFFFFF
     ~ System Code of T3T Emulation: 02FE
     ~ NFCID2 for the T3T Platform: 01FE000000000000
     ~ PAD0, PAD1, MRTI_check, MRTI_update and PAD2 of SENSF_RES: FFFFFFFFFFFFFFFF

   ~ [Param_33] ~  
    * ID: LF_T3T_MAX (52)
    * Len: 1
    * Val: 16

   ~ [Param_34] ~  
    * ID: LF_T3T_FLAGS (53)
    * Len: 2
    * Val: 00000011 10000000 (0380)
     ~ LF_T3T_IDENTIFIERS_1:   Enabled
     ~ LF_T3T_IDENTIFIERS_2:   Enabled
     ~ LF_T3T_IDENTIFIERS_3:   Disabled
     ~ LF_T3T_IDENTIFIERS_4:   Disabled
     ~ LF_T3T_IDENTIFIERS_5:   Disabled
     ~ LF_T3T_IDENTIFIERS_6:   Disabled
     ~ LF_T3T_IDENTIFIERS_7:   Disabled
     ~ LF_T3T_IDENTIFIERS_8:   Disabled
     ~ LF_T3T_IDENTIFIERS_9:   Disabled
     ~ LF_T3T_IDENTIFIERS_10:  Disabled
     ~ LF_T3T_IDENTIFIERS_11:  Disabled
     ~ LF_T3T_IDENTIFIERS_12:  Disabled
     ~ LF_T3T_IDENTIFIERS_13:  Disabled
     ~ LF_T3T_IDENTIFIERS_14:  Disabled
     ~ LF_T3T_IDENTIFIERS_15:  Disabled
     ~ LF_T3T_IDENTIFIERS_16:  Enabled

   ~ [Param_35] ~  
    * ID: LF_T3T_RD_ALLOWED (55)
    * Len: 1
    * Val: 01
     ~ The NFCC MAY include RD bytes in its SENSF_RES if it receives a SENSF_REQ with RC set to 0x02.

   ~ [Param_36] ~  
    * ID: LF_PROTOCOL_TYPE (50)
    * Len: 1
    * Val: 00000010 (02)
     ~ NFC-DEP Protocol: Supported

   ~ [Param_37] ~  
    * ID: LI_A_RATS_TB1 (58)
    * Len: 1
    * Val: 70
     ~ RATS Response Interface Byte TB(1) (defined in [DIGITAL]).

   ~ [Param_38] ~  
    * ID: LI_A_HIST_BY (59)
    * Len: 2
    * Val: 8000
     ~ Historical Bytes (only applicable for Type 4A Tag) (defined in [DIGITAL]).

   ~ [Param_39] ~  
    * ID: LI_B_H_INFO_RESP (5A)
    * Len: 1
    * Val: 00
     ~ Higher Layer – Response field of the ATTRIB response (defined in [DIGITAL]).

   ~ [Param_40] ~  
    * ID: LI_A_RATS_TC1 (5C)
    * Len: 1
    * Val: 00000010 (02)
     ~ If set to 1b DID MAY be used. Otherwise it SHALL NOT be used. (1)

   ~ [Param_41] ~  
    * ID: LN_WT (60)
    * Len: 1
    * Val: 14 (0E)
     ~ Waiting Time defined in [DIGITAL]: RWT = 256*16/fc * 2^WT = 4949.031 ms

   ~ [Param_42] ~  
    * ID: LN_ATR_RES_GEN_BYTES (61)
    * Len: 3
    * Val: 46666D
     ~ General Bytes in ATR_RES (defined in [DIGITAL]).

   ~ [Param_43] ~  
    * ID: RF_FIELD_INFO (80)
    * Len: 1
    * Val: 01
     ~ RF_FIELD_INFO_NTF: Enabled

   ~ [Param_44] ~  
    * ID: RF_NFCEE_ACTION (81)
    * Len: 1
    * Val: 00
     ~ RF_NFCEE_ACTION_NTF: Disabled

   ~ [Param_45] ~  
    * ID: NFCDEP_OP (82)
    * Len: 1
    * Val: 00011111 (1F)
     ~ Waiting Time: <= 10
     ~ All PDUs indicating chaining (MI bit set) SHALL use the maximum number of Transport Data Bytes.
     ~ Info PDU with no Transport Data Bytes SHALL NOT be sent.
     ~ NFC-DEP Initiator SHALL use the ATTENTION command only as the error recovery procedure described in [DIGITAL].
     ~ NFC-DEP Target SHALL NOT send RTOX requests.

   ~ [Param_46] ~  
    * ID: LLCP_VERSION (83)
    * Len: 1
    * Val: 1.1 (11)

   ~ [Param_47] ~  
    * ID: NFCC_CONFIG_CONTROL (85)
    * Len: 1
    * Val: 00000001 (01)
     ~ NFCC is allowed to manage RF config.

   ~ [Param_48] ~  
    * ID: Reserved (A0)
    * Len: 1
    * Val: 55
#end
```

### 實作備註
- ✅ 已修正（2026-10）：`LB_FWI_ADC_FO`（3C）的 `b3 of ADC Coding field` 改取 `val_b[4:5]`，即 b3。
- ✅ 已修正（2026-10）：`LN_WT`（60）視為 WT 指數，印 `<n> (raw)` 並依 `RWT = 256*16/fc * 2^WT` 換算毫秒（WT > 14 顯示 RFU）。
- `PB_AFI`（10）：`print("    * Val: ", val)` 造成 `Val:` 後多一個空白。
- ✅ 已修正（2026-10）：1-octet bit-field 參數（`CFG_BITFIELD_1OCT`）若 Len > 1，只解析第 1 octet 並加印 `* Warning: Len <m>, expected 1 (raw <val>)`。（`TOTAL_DURATION` 仍只取前 2 octets，多餘部分忽略。）
- ✅ 已修正（2026-10）：`tbl_cfg_para` 改用 `lookup`，`0xA0`–`0xFE` 顯示 `Reserved`、`0x86`–`0x9F` 等範圍 key 顯示 `RFU`；Value 仍走預設分支只印 raw。
- ✅ 已修正（2026-10）：Bit Rate 改用 `BIT_RATE_TEXT`，只有 `80`–`FE` 顯示 `For proprietary use`，其他未定義值（如 `07`）顯示 `RFU`。
