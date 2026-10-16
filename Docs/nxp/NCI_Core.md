# NXP NCI Core（GID 0x0）— `Nxp_pkg/NCI_Core.py`

本文件說明 vendor = `Nxp` 時，GID `0x0`（NCI Core）各 command 的解析方式。Dispatch 表為 [`Nxp_pkg/__ctrl__.py`](../../nci_decoder/Nxp_pkg/__ctrl__.py#L10) 的 `"NCI Core"` 群組，handler 實作於 [`Nxp_pkg/NCI_Core.py`](../../nci_decoder/Nxp_pkg/NCI_Core.py)。對照表一律來自 `Nxp_pkg/__table__.py`（見 [Tables](Tables.md)）。

NXP 版與 forum 版（[`nfc_forum_2_0/NCI_Core.md`](../nfc_forum_2_0/NCI_Core.md)）的關係：

- **大部分 handler 只是 delegate**：`Origin.<HANDLER>(raw, "nxp")`（`Origin` = `nfc_forum_2_0_pkg.NCI_Core`）。forum 函式內以 `pkg_import.tbl_import("nxp", ...)` → `vendor_registry.resolve()`（不分大小寫）載入 **`Nxp_pkg.__table__`**，所以解析流程與 forum 版相同，但查的是 NXP 的表（例如 `tbl_status_codes`、`tbl_rst_trig`、`tbl_rf_if`、`tbl_nfcee_id` 等含 SN2x0 擴充值）。
- **NXP 自行實作的 handler**（6 個）：`CORE_RESET_NTF`、`CORE_SET_CONFIG_CMD`、`CORE_SET_CONFIG_RSP`、`CORE_GET_CONFIG_CMD`、`CORE_GET_CONFIG_RSP`、`CORE_CONN_CREATE_RSP`。
- **NXP 專屬 config parameter**：當 Parameter ID 的第一個 octet 為 `A0` 或 `A1` 時，視為 **2-octet extended tag**（`A0xx` / `A1xx`，程式內稱 "Register"），值由 [`VALUE_OF_REGISTER`](#value_of_register--nxp-extended-parameter-a0xx--a1xx) 解析；其他 1-octet ID 由 NXP 本地版 [`VALUE_OF_CFG_PARA`](#value_of_cfg_para--標準-1-octet-parameter) 解析。

## Command 總覽

| OID | CMD | RSP | NTF | Handler（CMD / RSP / NTF） | 實作 |
|---|---|---|---|---|---|
| 0x00 | `20 00` | `40 00` | `60 00` | [CORE_RESET_CMD](#core_reset_cmd--20-00) / [CORE_RESET_RSP](#core_reset_rsp--40-00) / [CORE_RESET_NTF](#core_reset_ntf--60-00) | delegate / delegate / **NXP** |
| 0x01 | `20 01` | `40 01` | — | [CORE_INIT_CMD](#core_init_cmd--20-01) / [CORE_INIT_RSP](#core_init_rsp--40-01) | delegate / delegate |
| 0x02 | `20 02` | `40 02` | — | [CORE_SET_CONFIG_CMD](#core_set_config_cmd--20-02) / [CORE_SET_CONFIG_RSP](#core_set_config_rsp--40-02) | **NXP** / **NXP** |
| 0x03 | `20 03` | `40 03` | — | [CORE_GET_CONFIG_CMD](#core_get_config_cmd--20-03) / [CORE_GET_CONFIG_RSP](#core_get_config_rsp--40-03) | **NXP** / **NXP** |
| 0x04 | `20 04` | `40 04` | — | [CORE_CONN_CREATE_CMD](#core_conn_create_cmd--20-04) / [CORE_CONN_CREATE_RSP](#core_conn_create_rsp--40-04) | delegate / **NXP** |
| 0x05 | `20 05` | `40 05` | — | [CORE_CONN_CLOSE_CMD](#core_conn_close_cmd--20-05) / [CORE_CONN_CLOSE_RSP](#core_conn_close_rsp--40-05) | delegate / delegate |
| 0x06 | — | — | `60 06` | [CORE_CONN_CREDITS_NTF](#core_conn_credits_ntf--60-06) | delegate |
| 0x07 | — | — | `60 07` | [CORE_GENERIC_ERROR_NTF](#core_generic_error_ntf--60-07) | delegate |
| 0x08 | — | — | `60 08` | [CORE_INTERFACE_ERROR_NTF](#core_interface_error_ntf--60-08) | delegate |
| 0x09 | `20 09` | `40 09` | — | [CORE_SET_POWER_SUB_STATE_CMD](#core_set_power_sub_state_cmd--20-09) / [CORE_SET_POWER_SUB_STATE_RSP](#core_set_power_sub_state_rsp--40-09) | delegate / delegate |

共 **18** 個 handler（OID 0x0A–0x3F RFU，未定義）。另有兩個 helper：[`VALUE_OF_CFG_PARA`](#value_of_cfg_para--標準-1-octet-parameter)（[`NCI_Core.py:417`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L417)）與 [`VALUE_OF_REGISTER`](#value_of_register--nxp-extended-parameter-a0xx--a1xx)（[`NCI_Core.py:664`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L664)）。

> 範例皆以 `NFC_NCI_DECODER(len, raw, 'Nxp', 'None', 2)` 實際執行取得（同一個 Python process 依序執行，見下方「模組狀態」說明）。

### 模組狀態（跨封包的 global）

`VALUE_OF_REGISTER` 使用 module-level global，解析結果會受**先前封包**影響：

| Global | 初值 | 由誰寫入 | 由誰讀取 |
|---|---|---|---|
| `NCI_Core.RSTN_CFG` | `'0'` | `A007`（RSTN_CFG）的 bit0 | `A08E`（PHONE_OFF_ALLOWED） |
| `NCI_Core.ULPDET_CFG` | `'00'` | `A10F`（ULPDET_CFG）的 byte0 | `A015`（DEFAULT_POWER）值 `03`/`05` |
| `Proprietary.PWR_MODE_00` | `'0'` | `CORE_SET_POWER_MODE_CMD`（`2F 00`，見 [Proprietary.md](Proprietary.md)） | `A10B`（AUTONOMOUS_START_TIMEOUT） |

---

<a id="core_reset_cmd"></a><a id="CORE_RESET_CMD"></a>
## CORE_RESET_CMD  (`20 00`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NCI Core / 0x00 / CMD |
| Handler | [`NCI_Core.py:12`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L12) `CORE_RESET_CMD` |
| 實作 | delegate → forum [`CORE_RESET_CMD`](../nfc_forum_2_0/NCI_Core.md#core_reset_cmd--20-00) |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Reset Type | 1 | `tbl_cfg_status`（見 [Tables](Tables.md#tbl_cfg_status)） |

NXP 差異：無（僅查表改用 NXP 的 `tbl_cfg_status`）。

### 範例
- Raw：`20 00 01 01`
```text
  << CORE_RESET_CMD >>  
  * Reset Type: Reset Config (01)
#end
```

<a id="core_reset_rsp"></a><a id="CORE_RESET_RSP"></a>
## CORE_RESET_RSP  (`40 00`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NCI Core / 0x00 / RSP |
| Handler | [`NCI_Core.py:22`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L22) `CORE_RESET_RSP` |
| 實作 | delegate → forum [`CORE_RESET_RSP`](../nfc_forum_2_0/NCI_Core.md#core_reset_rsp--40-00) |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |

NXP 差異：無（查 NXP `tbl_status_codes`）。

### 範例
- Raw：`40 00 01 00`
```text
  << CORE_RESET_RSP >>  
  * Status: STATUS_OK (00)
#end
```

<a id="core_reset_ntf"></a><a id="CORE_RESET_NTF"></a>
## CORE_RESET_NTF  (`60 00`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NCI Core / 0x00 / NTF |
| Handler | [`NCI_Core.py:32`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L32) `CORE_RESET_NTF` |
| 實作 | **NXP 自行實作**（forum 版見 [`CORE_RESET_NTF`](../nfc_forum_2_0/NCI_Core.md#core_reset_ntf--60-00)） |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Reset Trigger | 1 | `tbl_rst_trig`（見 [Tables](Tables.md#tbl_rst_trig)，含 SN2x0 `A0`–`A7`） |
| 2 | Configuration Status | 1 | `tbl_cfg_status`（見 [Tables](Tables.md#tbl_cfg_status)） |

**分支 A：Reset Trigger == `A0`（assert 觸發 reset）**

| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 3 | dw Assertion Program Counter | 4 | 原樣印出 hex |

**分支 B：其他 Reset Trigger**

| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 3 | NCI Version | 1 | `tbl_nci_ver`（見 [Tables](Tables.md#tbl_nci_ver)） |
| 4 | Manufacturer ID | 1 | `00` → "Info is not available."，其他印 hex |
| 5 | Manufacturer Specific Information Length | 1 (n) | 讀取但不單獨顯示；決定下一欄的解析方式 |
| 6 | Manufacturer Specific Information | n | n ≥ 5：拆成以下子欄位（原樣印 hex）；n > 5 時多出的 n−5 bytes 另印 `* Manufacturer Specific Info (extra): <hex>`。0 < n < 5：整段印 `* Manufacturer Specific Info: <hex>`。n = 0：不印 |
| ﹂ | Model ID | 1 | hex |
| ﹂ | Hw Ver nb | 1 | hex |
| ﹂ | ROM Code Ver nb | 1 | hex |
| ﹂ | FLASH Ver | 2 | hex（不做 byte swap） |

與 forum 版差異：forum 版依 Length 欄位讀 n bytes 並整段印出；NXP 版同樣依 Length 讀 n bytes，但 n ≥ 5 時把前 5 bytes 拆成 SN2x0 版本資訊子欄位，並多了 `A0` 分支。

### 範例
- Raw：`60 00 0A 02 01 20 02 05 01 02 03 0A 00`
```text
  << CORE_RESET_NTF >>  
  * Reset Trigger: CORE_RESET_CMD (02)
  * Config Status: Reset Config (01)
  * NCI Version: 2.0 (20)
  * Manufacturer ID: 02
  * Model ID: 01
  * Hw Ver nb: 02
  * ROM Code Ver nb: 03
  * FLASH Ver: 0A00
#end
```
- Raw：`60 00 06 A0 01 12 34 56 78`（assert 分支）
```text
  << CORE_RESET_NTF >>  
  * Reset Trigger: An assert has triggered SN2x0 NFCC reset/reboot (A0)
  * Config Status: Reset Config (01)
  * dw Assertion Program Counter: 12345678
#end
```

### 實作備註
- ✅ 已修正（2026-10）：依 Manufacturer Specific Information Length 讀取；≥ 5 bytes 拆成具名欄位，多出部分印 `(extra)` 行，< 5 bytes 整段印 raw，不再因長度 ≠ 5 而 `Payload error!!`。
- ✅ 已修正（2026-10）：輸出標籤改為正確的 `Reset Trigger`。

<a id="core_init_cmd"></a><a id="CORE_INIT_CMD"></a>
## CORE_INIT_CMD  (`20 01`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NCI Core / 0x01 / CMD |
| Handler | [`NCI_Core.py:95`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L95) `CORE_INIT_CMD` |
| 實作 | delegate → forum [`CORE_INIT_CMD`](../nfc_forum_2_0/NCI_Core.md#core_init_cmd--20-01) |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Feature Enable | 2 | 原樣 hex，後綴 `-- RFU` |

NXP 差異：無。

### 範例
- Raw：`20 01 02 00 00`
```text
  << CORE_INIT_CMD >>  
  * Feature Enable: 0000 -- RFU
#end
```

<a id="core_init_rsp"></a><a id="CORE_INIT_RSP"></a>
## CORE_INIT_RSP  (`40 01`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NCI Core / 0x01 / RSP |
| Handler | [`NCI_Core.py:105`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L105) `CORE_INIT_RSP` |
| 實作 | delegate → forum [`CORE_INIT_RSP`](../nfc_forum_2_0/NCI_Core.md#core_init_rsp--40-01) |

### Payload 格式
欄位與 forum 版完全相同（Status / NFCC Features 4 octets / Max Logical Connections / Max Routing Table Size / Max Control Packet Payload Size / Max Data Packet Payload Size of Static HCI Conn / Number of Credits of Static HCI Conn / Max NFC-V RF Frame Size / Number of Supported RF Interfaces / Supported RF Interface[n] = Interface + Number of Extensions + Extension List），詳見 forum 文件。

使用的 NXP 表：`tbl_status_codes`、`tbl_nfcc_feat_oct1`、`tbl_nfcc_feat_oct2`、`tbl_rf_if`（含 SN2x0 `80` TAG-CMD、`81` WLC_RF、`83` NFCEE_DEP_RF_eSE）、`tbl_rf_if_exten`（見 [Tables](Tables.md#tbl_rf_if)）。

NXP 差異：
- forum 程式中 `if(int(max_logical_conn, 16) >= 15 and vendor == "None")` 才會把 Max Logical Connections ≥ 0x0F 顯示為 RFU；NXP 傳入 `vendor="nxp"`，因此**一律以十進位數值顯示**。

### 範例
- Raw：`40 01 13 00 1F 0E 02 00 0A 00 00 FF 02 FF 00 01 02 02 00 03 01 00`
```text
  << CORE_INIT_RSP >>  
  * Status: STATUS_OK (00)
  * NFCC Features: 1F0E0200

    * Octet 0: 00011111
     ~ Active Communication Mode:       Support
     ~ HCI Network Support:             Implements as defined in [ETSI_102622]
     ~ Discovery Cfg Mode:              RFU
     ~ Discovery Freq Cfg:              Supported in RF_DISCOVER_CMD

    * Octet 1: 00001110
     ~ Forced NFCEE routing:            Not support
     ~ APDU Pattern based routing:      Not support
     ~ System Code based routing:       Not support
     ~ AID based routing:               Support
     ~ Protocol based routing:          Support
     ~ Technology based routing:        Support

    * Octet 2: 00000010
     ~ RF Cfg in Switched Off State:    Not support
     ~ Switched On Sub-Mode States:     Not support
     ~ Switched Off State:              Support
     ~ Battery Off State:               Not support

    * Octet 3: 00000000 -- Proprietary

  * Max Logical Connections: 10 (0A)
  * Max Routing Table Size: 0 (0000)
  * Max Control Packet Payload Size: 255 (FF)
  * Max Data Packet Payload Size of the Static HCI Connection: 2 (02)
  * Number of Credits of the Static HCI Connection: 255 (FF)
  * Max NFC-V RF Frame Size: 256 (0001)
  * Number of Supported RF Interfaces: 2
  * Supported RF Interface: 0200030100

   ~ [RF_IF_0] ~  
    * Interface: ISO-DEP (02)
    * Number of Extensions: 0

   ~ [RF_IF_1] ~  
    * Interface: NFC-DEP (03)
    * Number of Extensions: 1
    * Extension 0: Frame Aggregated RF Interface Extension (00)
#end
```

<a id="core_set_config_cmd"></a><a id="CORE_SET_CONFIG_CMD"></a>
## CORE_SET_CONFIG_CMD  (`20 02`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NCI Core / 0x02 / CMD |
| Handler | [`NCI_Core.py:127`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L127) `CORE_SET_CONFIG_CMD` |
| 實作 | **NXP 自行實作**（forum 版見 [`CORE_SET_CONFIG_CMD`](../nfc_forum_2_0/NCI_Core.md#core_set_config_cmd--20-02)） |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Number of Parameters | 1 (n) | 十進位 |
| 2 | Parameter [1..n] | 每筆 m+2 或 m+3 | 逐筆解析如下 |
| ﹂ | ID（第 1 octet ∉ {`A0`,`A1`}） | 1 | `lookup(tbl_cfg_para, id)`（含範圍 key，例如 `A0-FE` → Reserved；查不到 RFU，見 [Tables](Tables.md#tbl_cfg_para)），印為 `ID:` |
| ﹂ | Register（第 1 octet ∈ {`A0`,`A1`}） | 2 | 讀 2 octets 成 `A0xx`/`A1xx`，`lookup(tbl_cfg_para, reg)`，印為 `Register:` |
| ﹂ | Len | 1 (m) | 十進位 |
| ﹂ | Val | m | m ≠ 0 時：1-octet ID → [`VALUE_OF_CFG_PARA(id, val)`](#value_of_cfg_para--標準-1-octet-parameter)；Register → [`VALUE_OF_REGISTER(reg, val, m)`](#value_of_register--nxp-extended-parameter-a0xx--a1xx)。m = 0 時不印 Val |

與 forum 版差異：forum 版 ID 一律 1 octet；NXP 版新增 `A0`/`A1` 2-octet extended tag 判斷與 `VALUE_OF_REGISTER` 解析。

### 範例
- Raw：`20 02 14 05 00 02 E8 03 80 01 01 A1 0F 02 01 01 A0 15 01 03 A5 01 00`（混合標準 ID、NXP Register、非 A0/A1 的 proprietary ID）
```text
  << CORE_SET_CONFIG_CMD >>  
  * Number of Params: 5

   ~ [Param_0] ~  
    * ID: TOTAL_DURATION (00)
    * Len: 2
    * Val: 1000 ms (E803)

   ~ [Param_1] ~  
    * ID: RF_FIELD_INFO (80)
    * Len: 1
    * Val: 01
     ~ RF_FIELD_INFO_NTF: Enabled

   ~ [Param_2] ~  
    * Register: ULPDET_CFG (A10F)
    * Len: 2
    * Val: 0101
      * ULPDET mode: Enabled 
       ~ NFC_GPIO2_AO is high when wake up from ULPDET mode, Low when enter in Standby mode.

   ~ [Param_3] ~  
    * Register: DEFAULT_POWER (A015)
    * Len: 1
    * Val: Autonomous Mode + ULPDET

   ~ [Param_4] ~  
    * ID: Reserved (A5)
    * Len: 1
    * Val: 00
#end
```
（`A015 = 03` 顯示 "+ ULPDET" 是因為同一封包前面的 `A10F` 已把 global `ULPDET_CFG` 設為 `01`。）

### 實作備註
- ✅ 已修正（2026-10）：改用 `range_lookup.lookup()`，`tbl_cfg_para` 的 `'A0-FE'` 範圍 key 生效，`A2`–`FE` 的 1-octet ID 顯示為 `Reserved`（例如上例 `A5`）。
- 未在 `VALUE_OF_REGISTER` 中列出的 Register（例如 `A001`）只印 `* Val: <hex>`。

<a id="core_set_config_rsp"></a><a id="CORE_SET_CONFIG_RSP"></a>
## CORE_SET_CONFIG_RSP  (`40 02`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NCI Core / 0x02 / RSP |
| Handler | [`NCI_Core.py:177`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L177) `CORE_SET_CONFIG_RSP` |
| 實作 | **NXP 自行實作**（forum 版見 [`CORE_SET_CONFIG_RSP`](../nfc_forum_2_0/NCI_Core.md#core_set_config_rsp--40-02)） |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |
| 2 | Number of Parameters | 1 (n) | 十進位 |
| 3 | Parameter ID [0..n] | 每筆 1 或 2 | 第 1 octet ∈ {`A0`,`A1`} → 讀 2 octets（`A0xx`/`A1xx`），否則讀 1 octet；皆印 `ID i: <name> (id)`，名稱查 `lookup(tbl_cfg_para, id)`（見 [Tables](Tables.md#tbl_cfg_para)） |

與 forum 版差異：forum 版 Parameter ID 一律 1 octet；NXP 版加入 `A0`/`A1` 2-octet extended tag 判斷。

### 範例
- Raw：`40 02 02 00 00`
```text
  << CORE_SET_CONFIG_RSP >>  
  * Status: STATUS_OK (00)
  * Number of Params: 0
#end
```
- Raw：`40 02 04 09 02 A0 15`
```text
  << CORE_SET_CONFIG_RSP >>  
  * Status: STATUS_INVALID_PARAM (09)
  * Number of Params: 2
  * Set Param ID:
    * ID 0: DEFAULT_POWER (A015)
    * ID 1: RFU ()
#end
```

### 實作備註
- ✅ 已修正（2026-10）：改為 NXP 自行實作，`A0xx`/`A1xx` 以 2-octet ID 讀取（如 `A0 15` → `DEFAULT_POWER (A015)`）；上例第 2 筆 `RFU ()` 是因為範例封包本身只帶 1 個 ID 卻宣告 2 個。

<a id="core_get_config_cmd"></a><a id="CORE_GET_CONFIG_CMD"></a>
## CORE_GET_CONFIG_CMD  (`20 03`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NCI Core / 0x03 / CMD |
| Handler | [`NCI_Core.py:208`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L208) `CORE_GET_CONFIG_CMD` |
| 實作 | **NXP 自行實作**（forum 版見 [`CORE_GET_CONFIG_CMD`](../nfc_forum_2_0/NCI_Core.md#core_get_config_cmd--20-03)） |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Number of Parameters | 1 (n) | 十進位 |
| 2 | Parameter ID [0..n] | 1 或 2 | 第 1 octet ∈ {`A0`,`A1`} → 讀 2 octets 印 `Register: <name> (A0xx)`；否則讀 1 octet 印 `ID i: <name> (xx)`。皆查 `tbl_cfg_para`（見 [Tables](Tables.md#tbl_cfg_para)） |

### 範例
- Raw：`20 03 07 04 02 A0 15 A1 0E 85`
```text
  << CORE_GET_CONFIG_CMD >>  
  * Number of Params: 4
  * Get Param ID:
    * ID 0: CON_DISCOVERY_PARAM (02)
    * Register: DEFAULT_POWER (A015)
    * Register: GUARD_TIMEOUT_Tx2Rx (A10E)
    * ID 3: NFCC_CONFIG_CONTROL (85)
#end
```

### 實作備註
- Register 項目不印序號 `i`，只有 1-octet ID 會印 `ID i:`。

<a id="core_get_config_rsp"></a><a id="CORE_GET_CONFIG_RSP"></a>
## CORE_GET_CONFIG_RSP  (`40 03`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NCI Core / 0x03 / RSP |
| Handler | [`NCI_Core.py:237`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L237) `CORE_GET_CONFIG_RSP` |
| 實作 | **NXP 自行實作**（forum 版見 [`CORE_GET_CONFIG_RSP`](../nfc_forum_2_0/NCI_Core.md#core_get_config_rsp--40-03)） |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |
| 2 | Number of Parameters | 1 (n) | 十進位 |
| 3 | Parameter [1..n] | m+2 或 m+3 | 與 [CORE_SET_CONFIG_CMD](#core_set_config_cmd--20-02) 的 Parameter 結構與解析完全相同（ID/Register → Len → Val；Val 交給 `VALUE_OF_CFG_PARA` / `VALUE_OF_REGISTER`） |

### 範例
- Raw：`40 03 10 00 03 A0 15 01 02 A0 85 04 78 88 AA 2C 85 01 01`
```text
  << CORE_GET_CONFIG_RSP >>  
  * Status: STATUS_OK (00)
  * Number of Params: 3

   ~ [Param_0] ~  
    * Register: DEFAULT_POWER (A015)
    * Len: 1
    * Val: Autonomous Mode

   ~ [Param_1] ~  
    * Register: RF_MISC_SETTINGS (A085)
    * Len: 4
    * Val: 7888AA2C
      * b_val: 00101100101010101000100001111000
      * Uncomplia nt 13.5MHz readers:            Enabled 
      * SFGT Early Exchange:                     Enabled 
      * PCD Block nb Check:                      Enabled 
      * Mute To RATS with non ISO-DEP SAK:       Disabled
      * Multiple Tag during collision:           Disabled
      * NAK To RATS:                             Disabled
      * Illegal Uid 0 (Yangchengtong):           Support
      * Non Compliant Mifare Reader:             Not support
      * Non Compliant Mifare Reader (Changchun): Not support

   ~ [Param_2] ~  
    * ID: NFCC_CONFIG_CONTROL (85)
    * Len: 1
    * Val: 00000001 (01)
     ~ NFCC is allowed to manage RF config.
#end
```
更多單一 Register 的解析輸出見 [附錄：Register 解析範例](#附錄register-解析範例)。

### 實作備註
- 即使 Status ≠ `00`，仍會繼續解析 Number of Parameters 與 Parameter 清單（無 status 分支）。

<a id="core_conn_create_cmd"></a><a id="CORE_CONN_CREATE_CMD"></a>
## CORE_CONN_CREATE_CMD  (`20 04`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NCI Core / 0x04 / CMD |
| Handler | [`NCI_Core.py:292`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L292) `CORE_CONN_CREATE_CMD` |
| 實作 | delegate → forum [`CORE_CONN_CREATE_CMD`](../nfc_forum_2_0/NCI_Core.md#core_conn_create_cmd--20-04) |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Destination Type | 1 | `tbl_dest_type`（見 [Tables](Tables.md#tbl_dest_type)） |
| 2 | Number of Destination-specific Parameters | 1 (n) | 十進位 |
| 3 | Destination-specific Parameter [0..n] | m+2 | TLV |
| ﹂ | Type | 1 | `tbl_d_spec_type`（見 [Tables](Tables.md#tbl_d_spec_type)） |
| ﹂ | Len | 1 (m) | 十進位 |
| ﹂ | Val（Type `00`） | 2 | octet0 RF Discovery ID：`tbl_rf_dis_id.get(v, v)`（見 [Tables](Tables.md#tbl_rf_dis_id)）；octet1 RF Protocol：`tbl_rf_proto`（見 [Tables](Tables.md#tbl_rf_proto)） |
| ﹂ | Val（Type `01`） | 2 | octet0 NFCEE ID：`00` DH / `01` HCI Network / `FF` RFU / 其他印 hex + 三行固定範圍說明；octet1 NFCEE Interface Protocol：`tbl_nfcee_proto`（見 [Tables](Tables.md#tbl_nfcee_proto)） |
| ﹂ | Val（其他 Type） | m | 印 raw + 固定 RFU / proprietary 說明 |

NXP 差異：無（查 NXP 表）。注意 NFCEE ID 這裡**不**查 NXP `tbl_nfcee_id`，所以 `C0` 不會顯示 `NFCEE_eSE`。

### 範例
- Raw：`20 04 06 03 01 01 02 C0 00`
```text
  << CORE_CONN_CREATE_CMD >>  
  * Destination Type: NFCEE (03)
  * Number of Destination-specific Params: 1

   ~ [Dest-spec Parameter_0] ~  
    * Type: NFCEE ID + NFCEE Interface Protocol (01)
    * Len: 2
    * Val: C000
      * NFCEE ID: NFCEE_eSE (C0)
      * NFCEE Interface Protocol: APDU (00)
#end
```
- Raw：`20 04 06 02 01 00 02 01 04`
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

<a id="core_conn_create_rsp"></a><a id="CORE_CONN_CREATE_RSP"></a>
## CORE_CONN_CREATE_RSP  (`40 04`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NCI Core / 0x04 / RSP |
| Handler | [`NCI_Core.py:307`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L307) `CORE_CONN_CREATE_RSP` |
| 實作 | **NXP 自行實作**（forum 版見 [`CORE_CONN_CREATE_RSP`](../nfc_forum_2_0/NCI_Core.md#core_conn_create_rsp--40-04)） |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |
| 2 | Max Data Packet Payload Size | 1 | **僅 Status == `00` 時解析**；十進位 |
| 3 | Initial Number of Credits | 1 | 僅 Status == `00`；若值在 `tbl_init_credits`（見 [Tables](Tables.md#tbl_init_credits)）則印表值，否則十進位 |
| 4 | Conn ID | 1 | 僅 Status == `00`；十進位 + `tbl_conn_id`（以低 4 bits 的 binary 字串為 key，見 [Tables](Tables.md#tbl_conn_id)），查不到 → "Dynamically assigned by the NFCC" |

與 forum 版差異：forum 版不論 Status 一律解析 4 個欄位；NXP 版只有 `STATUS_OK` 才解析後 3 欄（符合 NCI 規範中失敗時 RSP 只有 Status 的情況）。

### 範例
- Raw：`40 04 04 00 FF 01 03`
```text
  << CORE_CONN_CREATE_RSP >>  
  * Status: STATUS_OK (00)
  * Max Data Packet Payload Size: 255
  * Initial Number of Credits: 1
  * Conn ID: 3 (Dynamically assigned by the NFCC)
#end
```
- Raw：`40 04 01 03`
```text
  << CORE_CONN_CREATE_RSP >>  
  * Status: STATUS_FAILED (03)
#end
```

### 實作備註
- Conn ID 輸出缺少右括號 `)`（[`NCI_Core.py:335`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L335)，forum 版有補上）。

<a id="core_conn_close_cmd"></a><a id="CORE_CONN_CLOSE_CMD"></a>
## CORE_CONN_CLOSE_CMD  (`20 05`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NCI Core / 0x05 / CMD |
| Handler | [`NCI_Core.py:341`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L341) `CORE_CONN_CLOSE_CMD` |
| 實作 | delegate → forum [`CORE_CONN_CLOSE_CMD`](../nfc_forum_2_0/NCI_Core.md#core_conn_close_cmd--20-05) |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Conn ID | 1 | 低 4 bits 十進位 + `tbl_conn_id`（見 [Tables](Tables.md#tbl_conn_id)） |

NXP 差異：無。

### 範例
- Raw：`20 05 01 03`
```text
  << CORE_CONN_CLOSE_CMD >>  
  * Conn ID: 3 (Dynamically assigned by the NFCC)
#end
```

### 實作備註
- ✅ 已修正（2026-10）：forum 版改用共用的 `CONN_ID_TEXT()`，輸出補上右括號，且 Conn ID 只取低 4 bits（高 bits 為 RFU）。

<a id="core_conn_close_rsp"></a><a id="CORE_CONN_CLOSE_RSP"></a>
## CORE_CONN_CLOSE_RSP  (`40 05`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NCI Core / 0x05 / RSP |
| Handler | [`NCI_Core.py:351`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L351) `CORE_CONN_CLOSE_RSP` |
| 實作 | delegate → forum [`CORE_CONN_CLOSE_RSP`](../nfc_forum_2_0/NCI_Core.md#core_conn_close_rsp--40-05) |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |

NXP 差異：無。

### 範例
- Raw：`40 05 01 00`
```text
  << CORE_CONN_CLOSE_RSP >>  
  * Status: STATUS_OK (00)
#end
```

<a id="core_conn_credits_ntf"></a><a id="CORE_CONN_CREDITS_NTF"></a>
## CORE_CONN_CREDITS_NTF  (`60 06`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NCI Core / 0x06 / NTF |
| Handler | [`NCI_Core.py:361`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L361) `CORE_CONN_CREDITS_NTF` |
| 實作 | delegate → forum [`CORE_CONN_CREDITS_NTF`](../nfc_forum_2_0/NCI_Core.md#core_conn_credits_ntf--60-06) |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Number of Entries | 1 (n) | 十進位 |
| 2 | Entry [1..n] | 2 | |
| ﹂ | Conn ID | 1 | 十進位 + `tbl_conn_id`（見 [Tables](Tables.md#tbl_conn_id)） |
| ﹂ | Credits | 1 | 十進位 |

NXP 差異：無。

### 範例
- Raw：`60 06 05 02 00 01 03 02`
```text
  << CORE_CONN_CREDITS_NTF >>  
  * Number of Entries: 2

   ~ [Entry_0] ~  
    * Conn ID: 0 (Static: DH -- Remote NFC Endpoint)
    * Credits: 1

   ~ [Entry_1] ~  
    * Conn ID: 3 (Dynamically assigned by the NFCC)
    * Credits: 2
#end
```

<a id="core_generic_error_ntf"></a><a id="CORE_GENERIC_ERROR_NTF"></a>
## CORE_GENERIC_ERROR_NTF  (`60 07`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NCI Core / 0x07 / NTF |
| Handler | [`NCI_Core.py:374`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L374) `CORE_GENERIC_ERROR_NTF` |
| 實作 | delegate → forum [`CORE_GENERIC_ERROR_NTF`](../nfc_forum_2_0/NCI_Core.md#core_generic_error_ntf--60-07) |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |

NXP 差異：無（查 NXP `tbl_status_codes`）。

### 範例
- Raw：`60 07 01 0B`
```text
  << CORE_GENERIC_ERROR_NTF >>  
  * Status: RFU (0B)
#end
```

<a id="core_interface_error_ntf"></a><a id="CORE_INTERFACE_ERROR_NTF"></a>
## CORE_INTERFACE_ERROR_NTF  (`60 08`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NCI Core / 0x08 / NTF |
| Handler | [`NCI_Core.py:384`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L384) `CORE_INTERFACE_ERROR_NTF` |
| 實作 | delegate → forum [`CORE_INTERFACE_ERROR_NTF`](../nfc_forum_2_0/NCI_Core.md#core_interface_error_ntf--60-08) |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |
| 2 | Conn ID | 1 | 十進位 + `tbl_conn_id`（見 [Tables](Tables.md#tbl_conn_id)） |

NXP 差異：無。

### 範例
- Raw：`60 08 02 B0 03`
```text
  << CORE_INTERFACE_ERROR_NTF >>  
  * Status: RF_TRANSMISSION_EXCEPTION (B0)
  * Conn ID: 3 (Dynamically assigned by the NFCC)
#end
```

### 實作備註
- ✅ 已修正（2026-10）：forum 版改用共用的 `CONN_ID_TEXT()`，輸出補上右括號，且 Conn ID 只取低 4 bits（高 bits 為 RFU）。

<a id="core_set_power_sub_state_cmd"></a><a id="CORE_SET_POWER_SUB_STATE_CMD"></a>
## CORE_SET_POWER_SUB_STATE_CMD  (`20 09`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NCI Core / 0x09 / CMD |
| Handler | [`NCI_Core.py:395`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L395) `CORE_SET_POWER_SUB_STATE_CMD` |
| 實作 | delegate → forum [`CORE_SET_POWER_SUB_STATE_CMD`](../nfc_forum_2_0/NCI_Core.md#core_set_power_sub_state_cmd--20-09) |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Power State | 1 | 程式內 if/elif：`00` Switched On State、`01`/`02`/`03` Switched On Sub-State 1/2/3（附 Screen / Device 狀態），其他 RFU |

NXP 差異：無。

### 範例
- Raw：`20 09 01 01`
```text
  << CORE_SET_POWER_SUB_STATE_CMD >>  
  * Power State: Switched On Sub-State 1
    * Screen: Off
    * Device: Unlocked
#end
```

<a id="core_set_power_sub_state_rsp"></a><a id="CORE_SET_POWER_SUB_STATE_RSP"></a>
## CORE_SET_POWER_SUB_STATE_RSP  (`40 09`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NCI Core / 0x09 / RSP |
| Handler | [`NCI_Core.py:405`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L405) `CORE_SET_POWER_SUB_STATE_RSP` |
| 實作 | delegate → forum [`CORE_SET_POWER_SUB_STATE_RSP`](../nfc_forum_2_0/NCI_Core.md#core_set_power_sub_state_rsp--40-09) |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |

NXP 差異：無。

### 範例
- Raw：`40 09 01 00`
```text
  << CORE_SET_POWER_SUB_STATE_RSP >>  
  * Status: STATUS_OK (00)
#end
```

---

<a id="value_of_cfg_para"></a><a id="VALUE_OF_CFG_PARA"></a>
## VALUE_OF_CFG_PARA — 標準 1-octet parameter

[`NCI_Core.py:417`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L417) `VALUE_OF_CFG_PARA(id, val)`

NXP 保留一份 forum `VALUE_OF_CFG_PARA`（forum `NCI_Core.py:656`）的本地副本，用於 CORE_SET_CONFIG_CMD / CORE_GET_CONFIG_RSP 中**非** `A0`/`A1` 開頭的 ID。各 ID（`00`、`02`、`03`、`08`/`11`/`19`、`09`/`14`/`1A`/`2F`、`10`、`12`、`13`、`18`/`21`/`3E`/`5B`/`68`、`20`、`28`、`29`、`2A`/`62`、`30`–`33`、`38`–`3C`、`40`–`4F`、`52`、`53`、`55`、`50`、`58`–`5A`、`5C`、`60`、`61`、`80`–`83`、`85`）的解析方式與 forum 版完全相同，詳見 forum 文件 [CORE_SET_CONFIG_CMD](../nfc_forum_2_0/NCI_Core.md#core_set_config_cmd--20-02)；名稱查 NXP [`tbl_cfg_para`](Tables.md#tbl_cfg_para)、bit rate 查 NXP [`tbl_bit_rates`](Tables.md#tbl_bit_rates)。未列出的 ID 一律 `* Val: <hex>`。

與 forum 版唯一差異：**`0x82` NFCDEP_OP** 的 b4–b1 四個 bit，forum 版只在 bit = 1 時印一句完整描述；NXP 版每個 bit 都印 `<描述>: Apply / Not apply`（b5 Waiting Time 兩版相同）。

| bit（val_b index） | NXP 輸出標籤 |
|---|---|
| b4（`[3:4]`） | `Waiting Time: <= 10` / `<= WT_(NFCDEP,MAX)` |
| b3（`[4:5]`） | `PDUs chaining (MI bit set) with max Transport Data Bytes: Apply/Not apply` |
| b2（`[5:6]`） | `PDU with no Transport Data Bytes SHALL NOT be sent: Apply/Not apply` |
| b1（`[6:7]`） | `Initiator SHALL use ATTENTION CMD only as error recovery procedure: Apply/Not apply` |
| b0（`[7:8]`） | `NFC-DEP Target SHALL NOT send RTOX requests: Apply/Not apply` |

（程式中 `val_b = bin(int(val,16))[2:].zfill(8)`，字串 index `i` 對應 bit `7-i`。）

**1-octet bit-field 參數的長度檢查**（2026-10 新增）：`VALUE_OF_CFG_PARA` 現在是一層 wrapper，實際解析在 `VALUE_OF_CFG_PARA_BODY`。對 `CFG_BITFIELD_1OCT` 內的 ID（`02`、`13`、`2A`、`30`、`31`、`32`、`38`、`3C`、`50`、`5C`、`62`、`82`、`85`），若 Len > 1，只取第 1 個 octet 解析，並在最後多印一行 `* Warning: Len <m>, expected 1 (raw <hex>)`（例：`20 02 05 01 02 02 03 00` → `Warning: Len 2, expected 1 (raw 0300)`），不再因整段 value 轉成 bit 字串而錯位。

---

<a id="value_of_register"></a><a id="VALUE_OF_REGISTER"></a>
## VALUE_OF_REGISTER — NXP extended parameter (A0xx / A1xx)

[`NCI_Core.py:664`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L664) `VALUE_OF_REGISTER(tag, val, val_len)`

- `tag`：4 位 hex 字串（例如 `A015`）；`val`：value 的 hex 字串；`val_len`：Len 欄位（octets）。
- 名稱來自 NXP [`tbl_cfg_para`](Tables.md#tbl_cfg_para)（程式註解引用 SN2x0 User Manual Table 97–103、108，及 SN220 RF Register Setting Guidelines / AN13076）。
- 下表「byte n」指 value 的第 n 個 octet（0 起算）；「LE」表示 `int(byte0) + int(byte1)*256`（little endian）；`bN` 指該 byte 的 bit N。`tbl_general_status`：`00` Disabled / `01` Enabled；`tbl_general_status_n`：`00` Enabled / `01` Disabled（反相），程式多以 `'0' + bit` 組 key 查表（見 [Tables](Tables.md#tbl_general_status)、[Tables](Tables.md#tbl_general_status_n)）。
- 函式本身**不檢查長度**、不回傳 offset；外層 handler 一律以 Len 前進，所以 value 太短時欄位會印空字串或丟 exception（見各列備註）。

### Table 97. Core configuration parameters

| Tag | 名稱 | 行 | Value 解析方式 |
|---|---|---|---|
| `A001` | NFCC_DIE_ID | — | 無專屬分支，印 raw |
| `A015` | DEFAULT_POWER | [669](../../nci_decoder/Nxp_pkg/NCI_Core.py#L669) | `01` Standby State；`02` Autonomous Mode；`03` Autonomous Mode（若 global `ULPDET_CFG=='01'` 加 " + ULPDET"）；`05` Autonomous Mode（若 `ULPDET_CFG=='01'` 加 " + ULPDET With Notification"）；其他值印 `RFU (xx)` |
| `A00A` | WAIT_FOR_STABLE_SYSCLOCK | [689](../../nci_decoder/Nxp_pkg/NCI_Core.py#L689) | Guard Time = 整個 value 十進位 × 18.8 μs |
| `A010` | CLKGEN | [694](../../nci_decoder/Nxp_pkg/NCI_Core.py#L694) | 只看 byte1（XtalConfig）：b0 Calibration Restart on Wake-up（`tbl_general_status`）；b0=1 時 b3..b1 → Internal Cap（0 = no internal cap (2 pF parasitic)、1..7 = 4..10 pF）。byte0 不解析 |
| `A011` | RF_CLOCK_CFG | [702](../../nci_decoder/Nxp_pkg/NCI_Core.py#L702) | byte0 Input clock freq（[`tbl_in_clk_freq`](Tables.md#tbl_in_clk_freq)）；byte1 b7=1 且 byte0==`09` → "Reader mode: disable, Card mode: Clock-less"，b7=1 → "Reader XTAL / Card Clock-less"，否則兩者皆 XTAL；byte1 b5=1 → "Phone off: Force XTAL"；byte2 PLL lock 初始延遲 μs；byte3 連續檢查間隔 μs；byte4 檢查次數 |
| `A00E` | PMU_CFG | [717](../../nci_decoder/Nxp_pkg/NCI_Core.py#L717) | 依序切 raw hex：IRQ Enable 4B、Power Cfg 3B、DCDC Cfg 5B、TxLdo Cfg 4B、TxLdo Cfg2 4B、TxLdo Vddpa Cfg 4B、TxLdo delay 4B、Startup Wait 4B（共 32B） |
| `A007` | RSTN_CFG | [736](../../nci_decoder/Nxp_pkg/NCI_Core.py#L736) | b0 存入 global `RSTN_CFG`；b0=1 → "RSTN_internal: Disabled"，0 → "Enabled" |
| `A08E` | PHONE_OFF_ALLOWED | [744](../../nci_decoder/Nxp_pkg/NCI_Core.py#L744) | value==`01` 且 global `RSTN_CFG=='1'` → "Card Emulation in phone off: Enabled"；其餘皆 Disabled |
| `A009` | TO_BEFORE_STDBY_CFG | [756](../../nci_decoder/Nxp_pkg/NCI_Core.py#L756) | Time = 整個 value 以 **little endian** 十進位 / 1000 s（例：`E8 03` → 1.0 s） |
| `A01D` | Lx_DEBUG_CFG | [761](../../nci_decoder/Nxp_pkg/NCI_Core.py#L761) | `tbl_general_status`：byte0 b5 Modulation Detected NTF、b4 L1 Events、b3 L2 Reader Events、b2 Felica SystemCode、b1 Felica RF、b0 L2 Events CE；byte1 b5 L2 Events during RF activation ISO14443-3 |
| `A00F` | MW_AREA | — | 無專屬分支，印 raw |
| `A0FB` | HW_RESET_NTF | [775](../../nci_decoder/Nxp_pkg/NCI_Core.py#L775) | 印 raw + 固定說明（`0x04` 啟用每次 HW reset 送 CORE_RESET_NTF） |

### Table 98. Poll Mode configuration

| Tag | 名稱 | 行 | Value 解析方式 |
|---|---|---|---|
| `A064` | EMVCo_PCD_SETTINGS | [781](../../nci_decoder/Nxp_pkg/NCI_Core.py#L781) | Polling delay = `(byte0 + byte1*256) / 1000` ms（例：`E8 03` → 1.0 ms）；byte2 Max nb of WupA/WupB when LPCD triggered |
| `A044` | POLL_PROFILE_SEL_CFG | [786](../../nci_decoder/Nxp_pkg/NCI_Core.py#L786) | b0 NFC FORUM / EMVCo PCD profile；b1 Removal / Power OFF on Idle deactivation；b2 Removal / Power OFF on discover deactivation；b3 RFU；b4 Polling Type B first / Type A first；b5 EMVCo PCD polling digital / analog |
| `A04D`–`A05C` | MFC_KEY-0_CFG … MFC_KEY-15_CFG | — | 無專屬分支，印 raw |
| `A05D` | FSDI_CFG | [801](../../nci_decoder/Nxp_pkg/NCI_Core.py#L801) | 十進位 Frame Size |
| `A106` | LPCD_FPC | [805](../../nci_decoder/Nxp_pkg/NCI_Core.py#L805) | Threshold = byte0..1 LE |
| `A148` | RF_PATTERN_CHK | [809](../../nci_decoder/Nxp_pkg/NCI_Core.py#L809) | byte0 b0 Short RF guard time check（`tbl_general_status`） |
| `A14B` | PLL_FREQ_CHECK | [814](../../nci_decoder/Nxp_pkg/NCI_Core.py#L814) | 整個 value 查 `tbl_general_status`，查不到 RFU |

### Table 99. Listen Mode Configuration

| Tag | 名稱 | 行 | Value 解析方式 |
|---|---|---|---|
| `A080` | TO_RF_OFF_CFG | [819](../../nci_decoder/Nxp_pkg/NCI_Core.py#L819) | byte0..1 LE ms |
| `A062` | SLOW_HOST_CFG | [824](../../nci_decoder/Nxp_pkg/NCI_Core.py#L824) | `00` 螢幕關閉時繼續送 RF_FIELD_INFO_NTF；`01` 螢幕關閉時停止（除非被外部 reader 成功 activate）；其他 RFU |
| `A085` | RF_MISC_SETTINGS | [834](../../nci_decoder/Nxp_pkg/NCI_Core.py#L834) | 4B LE 組成 32-bit `b_val`（先印出）。`tbl_general_status`：b3 Uncompliant 13.56MHz readers、b4 SFGT Early Exchange、b6 PCD Block nb Check、b9 Mute To RATS with non ISO-DEP SAK、b12 Multiple Tag during collision、b13 NAK To RATS；Support/Not support：b17 Illegal Uid 0 (Yangchengtong)、b18 Non Compliant Mifare Reader、b30 Non Compliant Mifare Reader (Changchun) |
| `A10E` | GUARD_TIMEOUT_Tx2Rx | [849](../../nci_decoder/Nxp_pkg/NCI_Core.py#L849) | 3 個 2B LE 值 × 8/13.56 μs：FDT 14443-A activ (Tx→Rx)、FDT Mifare trans (Rx→Tx)、FDT Mifare trans (Tx→Rx) |
| `A095` | NDEF_NFCEE | [855](../../nci_decoder/Nxp_pkg/NCI_Core.py#L855) | byte0：b0 NDEF NFCEE、b2 FID E108、b3 E107、b4 E106、b5 E105、b6 E104 write from RF IF、b7 Additional proprietary TLV（皆 `tbl_general_status`） |
| `A110` | NDEF_NFCEE_CFG2 | [866](../../nci_decoder/Nxp_pkg/NCI_Core.py#L866) | byte0：b2 FID E108、b3 E107、b4 E106、b5 E105、b6 E104 write from Host IF |
| `A10B` | AUTONOMOUS_START_TIMEOUT | [875](../../nci_decoder/Nxp_pkg/NCI_Core.py#L875) | value==`00` 且 `Proprietary.PWR_MODE_00` ∉ {`02`,`04`} → "Autonomous Mode: Disabled"；否則 "starts afetr guard time N seconds"（N = 十進位） |
| `A10F` | ULPDET_CFG | [882](../../nci_decoder/Nxp_pkg/NCI_Core.py#L882) | byte0 存入 global `ULPDET_CFG` 並查 `tbl_general_status`；byte0==`01` 時解析 byte1：b0 NFC_GPIO2_AO（0 未用 / 1 喚醒時 high）、b1=1 GPIO2_AO 跟隨外部 RF field、b2=1 GPIO3_AO 於卡片 activate 時 high |
| `A096` / `A111` | NOTIFY_ALL_AID / NOTIFY_ALL_FID | [895](../../nci_decoder/Nxp_pkg/NCI_Core.py#L895) | b4 Action Notification、b3 Notification in Screen OFF（`tbl_general_status`） |
| `A086` / `A087` | RF_BITRATE_LIMIT_A_CFG / _B_CFG | [901](../../nci_decoder/Nxp_pkg/NCI_Core.py#L901) | Bit Rate Cfg1 = b2/b1/b0、Bit Rate Cfg2 = b6/b5/b4（各自 `tbl_general_status`）；UICC usage = b7（`tbl_general_status`） |
| `A11B` | MERGE_SAK | [908](../../nci_decoder/Nxp_pkg/NCI_Core.py#L908) | `01` Merge between different NFCEE requests；`02` Force clear；`03` Force merge；其他印 `RFU` |
| `A136` | AUTOMATIC_CARD_SELECTION | — | 無專屬分支，印 raw |
| `A155` | RSSI_CONTINUOUS_NTF | [916](../../nci_decoder/Nxp_pkg/NCI_Core.py#L916) | byte0 `tbl_general_status`（標籤 "Byte"）；byte1 × 10 ms NTF 間隔 |
| `A158` | NFCLD_THRESHOLD_FIELD_DETECT | — | 無專屬分支，印 raw |

### Table 100. SWP configuration parameters

| Tag | 名稱 | 行 | Value 解析方式 |
|---|---|---|---|
| `A0C0` / `A0D1` | SWP_BITRATE_UICC1 / UICC2 | [922](../../nci_decoder/Nxp_pkg/NCI_Core.py#L922) | `01` 200、`02` 416.7、`03` 833.3、`04` 910、`05` 1000、`06` 1250、`07` 1667 kb/s，其他 RFU |
| `A0CB` / `A0D3` | SWP_TS1_HIGHV_UICC1 / UICC2 | [930](../../nci_decoder/Nxp_pkg/NCI_Core.py#L930) | 4B LE / 45 / 1000 ms（SIMVCC HIGH → NFC_SIM_SWIO1 HIGH timeout；浮點數未格式化） |
| `A0EC` / `A0D4` | SWP_UICC1_IF_EN_CFG / UICC2 | [935](../../nci_decoder/Nxp_pkg/NCI_Core.py#L935) | 整個 value 查 `tbl_general_status`，印 "UICC1/UICC2 IF" |
| `A0F1` / `A0F8` | SWP_UICC1/2_SPECIAL_PWR_MODE_CFG | [940](../../nci_decoder/Nxp_pkg/NCI_Core.py#L940) | `00` Low、`01` Full，其他 RFU |
| `A0C5` | SWP_UICC1_ACT_RSET_WAIT | [946](../../nci_decoder/Nxp_pkg/NCI_Core.py#L946) | 十進位 × 128 μs |
| `A11C` | SWP_EXT_RESUME | [950](../../nci_decoder/Nxp_pkg/NCI_Core.py#L950) | b0 UICC1、b1 UICC2（0 不用 extended resume / 1 可用） |

### Table 101. Mailbox configuration parameters

| Tag | 名稱 | 行 | Value 解析方式 |
|---|---|---|---|
| `A0B8` | SE_APDU_LOGGING_EN_CFG | [958](../../nci_decoder/Nxp_pkg/NCI_Core.py#L958) | b0 APDU Logging（`tbl_general_status`）；b2 APDU Logging during Mifare CLT（`tbl_general_status_n`，0=Enabled） |
| `A0ED` | NFCEE_eSE_IF_EN_CFG | [964](../../nci_decoder/Nxp_pkg/NCI_Core.py#L964) | `00` → "NFCEE_eSE IF: Disabled"；`01` NFCEE_eSE、`02` NFCEE_eUICC、`03` NFCEE_eSE and NFCEE_eUICC → "<名稱> IF: Enabled"；其他 "RFU IF: Enabled" |
| `A0F9` | SE_COLD_RESET_NTF | [972](../../nci_decoder/Nxp_pkg/NCI_Core.py#L972) | 整個 value 查 `tbl_general_status`（經 NFC_GPIO0 送 eSE cold reset NTF） |
| `A08A` | SE_POWER_ON_TO_WAKE_UP_GUARD_TIME | [976](../../nci_decoder/Nxp_pkg/NCI_Core.py#L976) | 2B LE µs |
| `A08C` | SE_POWER_OFF_TO_SW_RESET_DELAY_TIME | [980](../../nci_decoder/Nxp_pkg/NCI_Core.py#L980) | 2B LE µs |
| `A08D` | WAKE_UP_SE_TO_ACT_FRAME_DELAY_TIME | [984](../../nci_decoder/Nxp_pkg/NCI_Core.py#L984) | 2B LE µs |
| `A089` | ACT_RESPONSE_GUARD_TIME | [988](../../nci_decoder/Nxp_pkg/NCI_Core.py#L988) | 2B LE ms |
| `A08B` / `A082` | CLT_F_TIMEOUT / CLT_A_TIMEOUT | [992](../../nci_decoder/Nxp_pkg/NCI_Core.py#L992) | 2B LE ms |
| `A094` | SE_TEMP_ERROR_DELAY_TIME | [996](../../nci_decoder/Nxp_pkg/NCI_Core.py#L996) | 依 NXP UM：1 octet；Bit[0:3] 為 timeout 值，Bit[7] = 1 表示單位為秒（印 "s"，否則 "(No unit defined)"），Bit[4:6] 為 RFU 不計入（例：`85` → 5 s、`95` → 5 s、`05` → 5 (No unit defined)）；Len > 1 時只解第 1 octet 並加印 `Warning: Len N, expected 1 (raw ...)` |
| `A084` | VBAT_THRESHOLD_PHONE_OFF | [1008](../../nci_decoder/Nxp_pkg/NCI_Core.py#L1008) | 2B LE mV |

### Table 102. HCI configuration parameters

| Tag | 名稱 | 行 | Value 解析方式 |
|---|---|---|---|
| `A0EA` / `A01E` / `A0EB` | UICC1_SESSIONID / UICC2_SESSIONID / eSE_SESSIONID | — | 無專屬分支，印 raw |
| `A0EF` / `A0E8` / `A0F0` | RF_PARAM_CE_UICC1 / UICC2 / eSE | [1013](../../nci_decoder/Nxp_pkg/NCI_Core.py#L1013) | 依序解析（見下方子表） |
| `A11A` | PHONEOFF_TECH_CFG | [1084](../../nci_decoder/Nxp_pkg/NCI_Core.py#L1084) | b0 CE A、b1 CE B、b2 CE F（`tbl_general_status_n`，0=Enabled） |
| `A022` / `A023` / `A024` / `A025` / `A0E9` / `A012` | HCI pipe status（eSE Connectivity / eSE APDU / UICC1 Connectivity / UICC1 APDU / UICC2 Connectivity / eUICC APDU） | [1091](../../nci_decoder/Nxp_pkg/NCI_Core.py#L1091) | `00` Deleted、`01` Closed、`02` Open，其他 RFU |

`A0EF` / `A0E8` / `A0F0` RF_PARAM_CE_* 子結構：

| # | 欄位 | 長度 (Octets) | 解析 |
|---|---|---|---|
| | **Card Emulation for Type A** | | |
| 1 | Pipe Status | 1 | `00` Not created、`01` Created & Closed、`02` Open |
| 2 | MODE parameter | 1 | hex |
| 3 | UID size | 1 (u) | 不印 |
| 4 | UID | u | hex |
| 5 | SAK | 1 | hex |
| 6 | ATQA | 2 | hex |
| 7 | App. Data size | 1 (a) | 不印 |
| 8 | App. Data | a | hex |
| 9 | FWI_SFGI | 1 | hex |
| 10 | CID support | 1 | hex |
| 11 | CLT support | 1 | hex |
| 12 | Data Rate Max | 3 | hex |
| | **Card Emulation for Type B** | | |
| 13 | Pipe Status | 1 | 同上 |
| 14 | MODE parameter | 1 | hex |
| 15 | PUPI size | 1 (p) | 不印 |
| 16 | PUPI | p | hex |
| 17 | AFI | 1 | hex |
| 18 | ATQB | 4 | hex |
| 19 | Higher Layer RSP size | 1 (h) | 不印 |
| 20 | Higher Layer RSP | h | hex |
| 21 | Data Rate Max | 3 | hex |

### Table 103. RF transitions / RF 相關

| Tag | 名稱 | 行 | Value 解析方式 |
|---|---|---|---|
| `A017` | RF_CUST_PHAS E_COMPENSATI ON（表內名稱含空白） | [1110](../../nci_decoder/Nxp_pkg/NCI_Core.py#L1110) | 2B LE（base 16）signed × 0.25 °，印 `* Phase: <deg> °`（例：`FC FF` → -1.0 °；不印 `* Val:` 行） |
| `A068` | RF_LPCD_CFG | [1119](../../nci_decoder/Nxp_pkg/NCI_Core.py#L1119) | 跳過 byte0–8；byte9 b7 LPCD Enable（Mode 字串 = byte9..10 hex）；Disabled → "LPCD: Disabled (mode)"。Enabled：byte9 b5 與 b3 皆 1 → "with retry poll"；byte10 b4=1 → "Advanced"；byte11 `00` → "LPCD"，否則 "Hybrid LPCD" + Fall-back Counter = byte11；byte12..13 LE Threshold coarse；跳過 byte14–35；byte36..37 LE × 2.63 ms LPCD Period |
| `A149` | RF_ADV_LPCD_CFG | — | 無專屬分支，印 raw |
| `A034` | RF_DLMA_CFG | [1164](../../nci_decoder/Nxp_pkg/NCI_Core.py#L1164) | 跳過 byte0–3；byte4 APC_ID_REF_AB、byte5 NB_ENTRIES_AB；byte6–101 固定 24 筆 × 4B（每筆印前 2B LE）Type A&B RSSI threshold；byte102 APC_ID_REF_F、byte103 NB_ENTRIES_F；byte104–199 24 筆 Type F RSSI threshold（共 200B） |
| `A10A` | RF_DLMA_CLOCK_LESS_CEF_CFG | [1182](../../nci_decoder/Nxp_pkg/NCI_Core.py#L1182) | byte0 APC_ID_REF_F、byte1 NB_ENTRIES_F；byte2–97 24 筆 × 4B（前 2B LE）Type F RSSI threshold |
| `A00B` | RF_DPC_CFG | [1192](../../nci_decoder/Nxp_pkg/NCI_Core.py#L1192) | byte0 bConfig：b0 DPC in Reader、b3 Overcurrent prevention（`_n` 反相）、b4 GPADC threshold detection、b5 Periodic Timer；byte1..2 LE Target Current mA；byte3 Hysteresis mA；跳過 byte4–5；之後 37 筆 × 4B DPC entry（第 i 筆 VDDPA = 1.5 + 0.05·i V）：byte0 Target I reduction mA、byte1 signed MAL change、ASK100 rise/fall = byte2 高/低 nibble、ASK10 rise/fall = byte3 高/低 nibble（皆 4-bit signed） |
| `A00D` | RF_TRANSITION_CFG | [1230](../../nci_decoder/Nxp_pkg/NCI_Core.py#L1230) | byte0 Transition ID（[`tbl_rf_trans_id`](Tables.md#tbl_rf_trans_id)）；byte1 CLIF register offset（[`tbl_register`](Tables.md#tbl_register)）；其後為 register value：任意長度，以 LE 組成 bit 字串（`Register Val` 行印實際位數），拆 bit field 時補零擴成 32-bit。依 register offset 再拆 bit field（見下方子表） |
| `A09E` | RX_CTRL_CFG | [1278](../../nci_decoder/Nxp_pkg/NCI_Core.py#L1278) | byte0 Config：b2 Rx improvements for GreenCar、b3 Clock-less CeB field strength RSSI conversion；byte1..2 LE / 2048 mV Ref Interpolated RSSI @ 8 A/m；byte3..4 LE LPDET mA/m；byte5..6 LE NFCLD ON mA/m；byte7 NFCLD ON/OFF ratio %；byte8..9 LE Green Car threshold mA/m；byte10..11 LE Clock-less CeB mA/m |
| `A17E` | ADVANCED_HYBRID_LPCD_CFG | [1307](../../nci_decoder/Nxp_pkg/NCI_Core.py#L1307) | 16-bit 字串 = byte0 bits + byte1 bits（byte0 在前）。byte1 b0 POLL_TYPE_A、b1 POLL_TYPE_B、b2 POLL_TYPE_F、b3 POLL_TYPE_V；byte0 b7 Advanced Hybrid LPCD |
| `A12E` | FDT_CFG | [1317](../../nci_decoder/Nxp_pkg/NCI_Core.py#L1317) | byte0 Tx BitPhase Ext Clock、byte1 Tx BitPhase Clock-less、byte2 Tx BitPhase Bpsk Delay（hex），附 "+1 = +1/13.56MHz" 說明 |

`A00D` RF_TRANSITION_CFG register bit field（補零成 32-bit 字串，index `i` ↔ bit `31-i`）：

| Register offset | 欄位（bit 範圍） |
|---|---|
| `50` | GSP_DEFAULT_TX2 b29–25、GSP_DEFAULT_TX1 b24–20、GSP_CM_TX2 b19–15、GSP_CM_TX1 b14–10、GSP_RM_TX2 b9–5、GSP_RM_TX1 b4–0 |
| `4E` / `4F`（TX1 / TX2） | GSN_DEFAULT b24–20、GSN_MOD_CM b19–15、GSN_CW_CM b14–10、GSN_MOD_RM b9–5、GSN_CW_RM b4–0 |
| `AB` | TX1_SS_TARGET_SCALE = register value byte0、TX2_SS_TARGET_SCALE = register value byte1（十進位；不足時以 `00` 補） |
| `32` | TX_UNDERSHOOT_PATTERN b31–16、TX_EXTENDED_TRANSMISSION b7–6、TX_UNDERSHOOT_PATTERN_LEN b4–1、TX_UNDERSHOOT_PROT_ENABLE b0 |
| `40` | DGRM_RSSI_TARGET b16–7、DGRM_SIGNAL_DETECT_TH_OVR_VAL b6–0 |
| 其他 | 只印 Transition ID / offset / Register Val |

### Table 108. GPIO configuration parameters

| Tag | 名稱 | 行 | Value 解析方式 |
|---|---|---|---|
| `A196` | GPIO_SELECTION | — | 無專屬分支，印 raw |

### SN220 RF Register Setting Guidelines / AN13076（DLMA）

| Tag | 名稱 | 行 | Value 解析方式 |
|---|---|---|---|
| `A06A` | RF_CLK_PLL_DPLL3 | [1326](../../nci_decoder/Nxp_pkg/NCI_Core.py#L1326) | 8 個 2B LE 值 / 4 → 度：Sys/Xtal clk 的 RF ON、A、B、F；Clock-less 的 RF ON、A、B、F（共 16B） |
| `A0A4` | HFatt. Phase Correction | [1343](../../nci_decoder/Nxp_pkg/NCI_Core.py#L1343) | 跳過 byte0–4；64 筆 × 2B LE × 0.125（HFatt_code 0–63） |
| `A0A5` | HF attenuator phase correction | — | 無專屬分支，印 raw |
| `A0AF` | DLMA_CTRL | [1352](../../nci_decoder/Nxp_pkg/NCI_Core.py#L1352) | cfg_ab = byte0、cfg_f = byte4、Ref VDDPA AB = byte3、Ref VDDPA F = byte7（皆 1.5 + 0.05·x V；value 不足 8B 時只印 AB）。cfg_ab 與 cfg_f 的低 nibble 皆為 0 → "DLMA: Disabled" + Ref VDDPA AB/F；否則 "DLMA: Enable" + 兩組 b0 APC TX、b1 BPSK (m3)、b2 Single Driver (m1)、b3 APC Arbitrary Phase；最後一律印 b4 APC uses RSSI（0 Raw / 1 Interpolated） |
| `A0A7` | RM_GLOBAL_TX_SHAPING | [1382](../../nci_decoder/Nxp_pkg/NCI_Core.py#L1382) | byte4/5/6 低 5 bits → GSN_MOD_RM / GSN_CW_RM / GSP_RM；byte8 TX_SS_TARGET_SCALE；byte9 × 9 ° TX_PH_SHIFT_DIV10；byte10 × 0.9 ° TX_PH_SHIFT_MOD10 |
| `A0A8` | RM_TECHNO_TX_SHAPING | [1391](../../nci_decoder/Nxp_pkg/NCI_Core.py#L1391) | 64B 分段：Type A byte0–15、Type B 16–31、Type F 32–39、Type V 40–63。每段內 4B 一組，組內 byte2 = Time const cfg（falling/rising edge）、byte0 = RESIDUAL carrier（Type B/F 與 V10_xx 才印）。A：A106/A212/A424/A848；B：B106/B212/B424/B848；F：F212/F424；V：V100_26、V10_26、V100_53、V10_53、V100_106、V100_212 |
| `A098` | MEASURED_LMA_RSSI | [1426](../../nci_decoder/Nxp_pkg/NCI_Core.py#L1426) | byte0 Measured LMA phone ON mV；byte1..2 LE Measured RSSI；byte3 Bit[4:7]（高 nibble，依 NXP UM）Ref field strength A/m；byte4 Ref VDDPA DLMA OFF（1.5 + 0.05·x V）；byte5/6/7 Measured LMA Type A/B/F clock-less mV |
| `A0AB` | RSSI_GAIN | [1436](../../nci_decoder/Nxp_pkg/NCI_Core.py#L1436) | 跳過 byte0–1；64 筆 × 2B LE（HFatt code 0–63） |
| `A0A9` | DLMA_TX | [1442](../../nci_decoder/Nxp_pkg/NCI_Core.py#L1442) | 每 3B 一筆（筆數 = Len/3），與前一筆完全相同則略過不印。byte0 b5–0 ID、b6 Mode 3、b7 → DriNum = 2 − b7；byte1 VDDPA = 1.5 + 0.05·x V；byte2 TxScaling；Equiv TX (Vpp) = VDDPA × TxScaling/255 × DriNum × (1 + Mode3) |

<a id="value_of_register"></a><a id="VALUE_OF_REGISTER"></a>
### VALUE_OF_REGISTER 實作備註

以下皆經實際執行驗證：

- ✅ 已修正（2026-10）：**`A017` RF_CUST_PHASE_COMPENSATION** 改以 base 16 解析 2B LE signed 值（例：`A0 17 02 FC FF` → `* Phase: -1.0 °`），不再丟 `ValueError`。此分支仍不印 `* Val:` 行。
- ✅ 已修正（2026-10）：**`A064` EMVCo_PCD_SETTINGS** 運算順序改為 `(byte0 + byte1*256) / 1000`（例：`E8 03` → 1.0 ms）。
- ✅ 已修正（2026-10）：**`A00D` RF_TRANSITION_CFG** 接受任意長度的 register value（LE 組 bit 字串、補零到 32-bit 再切欄位），Len 5 不再 `UnboundLocalError`，offset `AB` + Len 3 也不再 `ValueError`（缺的 byte 以 `00` 顯示）。Transition ID 不在表中時仍印 `RFU`。
- ✅ 已修正（2026-10）：**`A00B` RF_DPC_CFG** 的 ASK100 rise/fall 改取 byte2 高/低 nibble、ASK10 取 byte3 高/低 nibble（例：entry `00 0F 12 F3` → MAL 15、ASK100 "1 / 2"、ASK10 "-1 / 3"）。
- ✅ 已修正（2026-10）：**`A086`/`A087`** UICC usage 改以 `'0' + b7` 查 `tbl_general_status`，正確顯示 Enabled / Disabled。
- ✅ 已修正（2026-10）：**`A0AF` DLMA_CTRL** 的 Ref VDDPA F 改取 byte7（`val[14:16]`），value 不足時只印 AB。DLMA Disabled 判斷仍是比對 cfg_ab / cfg_f 的低 nibble。
- ✅ 已修正（2026-10）：**`A015` DEFAULT_POWER** 在 `01/02/03/05` 以外的值印 `* Val: RFU (xx)`。
- ✅ 已修正（2026-10，依 NXP UM 確認）：**`A094`** Bit[0:3] 為 timeout 值、Bit[7] 為秒單位旗標、Bit[4:6] RFU（例：`85` → 5 s、`95` → 5 s）。（10-15 曾誤改為整個 value 以 little endian 解讀，10-16 依 UM 改回。）
- ✅ 已確認（2026-10，依 NXP UM）：**`A098`** Ref field strength = byte3 Bit[4:7]（高 nibble），即原本的寫法。（10-15 曾誤改為整個 byte，10-16 依 UM 改回。）
- ✅ 已修正（2026-10）：**`A009`** 改為 little endian（例：`E8 03` → 1.0 s），與其他多 byte 欄位一致。
- **`A0CB`/`A0D3`** 結果為未格式化的浮點數（例：`0.22222222222222224 ms`）。
- **`A034`/`A10A`/`A0A4`/`A0AB`/`A00B`** 筆數固定（24/24/64/64/37），不參考 value 內的 NB_ENTRIES 或 Len；value 不足時印空值或丟 `ValueError`。
- `A068`/`A034` 等跳過的 byte 不顯示任何內容；`A00E`/`A0EF` 等也不檢查實際長度。
- **狀態相依**：`A015` 依賴先前 `A10F`；`A08E` 依賴先前 `A007`；`A10B` 依賴 `Proprietary.PWR_MODE_00`（見[模組狀態](#模組狀態跨封包的-global)）。
- ✅ 已修正（2026-10）：`A11B` 未定義值改印 `RFU`。
- 輸出中仍有拼字錯誤 `Uncomplia nt`（`A085`）、`afetr`（`A10B`）（原碼如此）。

---

## 附錄：Register 解析範例

以下皆為 `40 03 <len> 00 01 <tag> <Len> <val>`（GET_CONFIG_RSP，單一 parameter）實際執行結果，只節錄 Param 部分。

`40 03 07 00 01 A1 0F 02 01 07`（ULPDET_CFG）
```text
    * Register: ULPDET_CFG (A10F)
    * Len: 2
    * Val: 0107
      * ULPDET mode: Enabled 
       ~ NFC_GPIO2_AO is high when wake up from ULPDET mode, Low when enter in Standby mode.
       ~ NFC_GPIO2_AO is high when external RF field is ON and low when OFF, in all modes (ULPDET,LPDET).
       ~ NFC_GPIO3_AO is high when card is activated in any RF technology. Set low when NFCC enters standby.
```

`40 03 0A 00 01 A0 11 05 09 80 05 0A 03`（RF_CLOCK_CFG）
```text
    * Register: RF_CLOCK_CFG (A011)
    * Len: 5
    * Val: 0980050A03
      * Input clock freq: Not applicable (09)
      * Reader mode: disable , * Card mode: Clock-less mode
      * Initial delay before check of PLL lock: 5 μs
      * Delay between check of successive check of lock bit: 10 μs
      * Number of successive checks: 3
```

`40 03 07 00 01 A0 1D 02 FF 20`（Lx_DEBUG_CFG）
```text
    * Register: Lx_DEBUG_CFG (A01D)
    * Len: 2
    * Val: FF20
      * Modulation Detected Notification:           Enabled 
      * L1 Events:                                  Enabled 
      * L2 Reader Events:                           Enabled 
      * Felica SystemCode:                          Enabled 
      * Felica RF (all Felica CM events):           Enabled 
      * L2 Events CE:                               Enabled 
      * L2 Events during RF activation ISO14443-3:  Enabled 
       ~ [L1 Events]: {ISO14443-4, ISO18092}
       ~ [L2 Events]: Reader {ROW specific}, CE {ISO14443-3, RF Field ON/OFF}
```

`40 03 06 00 01 A0 44 01 31`（POLL_PROFILE_SEL_CFG）
```text
    * Register: POLL_PROFILE_SEL_CFG (A044)
    * Len: 1
    * Val: 00110001 (31)
      * Bit 0: EMVCo PCD profile
      * Bit 1: Removal on Idle deactivation
      * Bit 2: Removal on discover deactivation
      * Bit 3: RFU
      * Bit 4: Polling Type A first
      * Bit 5: EMVCo PCD polling (analog)
```

`40 03 0B 00 01 A1 0E 06 80 00 A0 00 C0 00`（GUARD_TIMEOUT_Tx2Rx）
```text
    * Register: GUARD_TIMEOUT_Tx2Rx (A10E)
    * Len: 6
    * Val: 8000A000C000
      * FDT 14443-A activ (Tx to Rx): 75.52 µs
      * FDT Mifare trans (Rx to Tx): 94.40 µs
      * FDT Mifare trans (Tx to Rx): 113.27 µs
```

`40 03 26 00 01 A0 EF 21 02 FF 04 11 22 33 44 20 04 00 00 70 00 01 03 03 03 02 FF 04 AA BB CC DD 00 00 00 00 00 00 03 03 03`（RF_PARAM_CE_UICC1）
```text
    * Register: RF_PARAM_CE_UICC1 (A0EF)
    * Len: 33
    * Val: 02FF04112233442004000070000103030302FF04AABBCCDD000000000000030303
     ~ Card Emulation for Type A ~
      * Pipe Status: Open
      * MODE parameter: FF
      * UID: 11223344
      * SAK: 20
      * ATQA: 0400
      * App. Data: 
      * FWI_SFGI: 70
      * CID support: 00
      * CLT support: 01
      * Data Rate Max: 030303
     ~ Card Emulation for Type B ~
      * Pipe Status: Open
      * MODE parameter: FF
      * PUPI: AABBCCDD
      * AFI: 00
      * ATQB: 00000000
      * Higher Layer RSP: 
      * Data Rate Max: 030303
```

`40 03 2F 00 01 A0 68 2A 00×9 82 10 03 E8 03 00×22 7C 01 00×4`（RF_LPCD_CFG，Enabled）
```text
    * Register: RF_LPCD_CFG (A068)
    * Len: 42
    * Val: 000000000000000000821003E803000000000000000000000000000000000000000000007C0100000000
      * LPCD: Enabled (8210)
      * Mode: Advanced Hybrid LPCD
      * Fall-back Counter: 3 (03)
      * Threshold coarse: 1000 (E803)
      * LPCD Period: 999.40 ms
```

`40 03 0B 00 01 A0 0D 06 01 50 FF FF FF FF`（RF_TRANSITION_CFG，offset 50）
```text
    * Register: RF_TRANSITION_CFG (A00D)
    * Len: 6
    * Val: 0150FFFFFFFF
      * Transition ID: RFU (01)
      * CLIF register offset: CLIF_ANACTRL_TX_GSP_REG (50)
      * Register Val: FFFFFFFF ( 11111111111111111111111111111111 )
        * GSP_DEFAULT_TX2: 11111
        * GSP_DEFAULT_TX1: 11111
        * GSP_CM_TX2: 11111
        * GSP_CM_TX1: 11111
        * GSP_RM_TX2: 11111
        * GSP_RM_TX1: 11111
```

`40 03 11 00 01 A0 9E 0C 0C 00 10 64 00 C8 00 32 2C 01 F4 01`（RX_CTRL_CFG）
```text
    * Register: RX_CTRL_CFG (A09E)
    * Len: 12
    * Val: 0C00106400C800322C01F401
      * Config: 00001100
        * Rx improvements for GreenCar: Enabled 
        * Clock-less CeB field strength RSSI conversion: Enabled 
      * Ref Interpolated RSSI measured at 8 A/m: 2.00 mV
      * LPDET: 100 mA/m
      * NFCLD ON: 200 mA/m
      * NFCLD ON/OFF ratio: 50 %
      * Green Car threshold: 300 mA/m
      * Clock-less CeB: 500 mA/m
```

`40 03 15 00 01 A0 6A 10 00 01 68 01 B4 00 10 00 00 02 68 02 B4 02 10 02`（RF_CLK_PLL_DPLL3）
```text
    * Register: RF_CLK_PLL_DPLL3 (A06A)
    * Len: 16
    * Val: 00016801B400100000026802B4021002
     ~ Sys / Xtal clk:
      * RF ON: 64.00 °  * A: 90.00 °  * B: 45.00 °  * F: 4.00 °
     ~ Clock-less:
      * RF ON: 128.00 °  * A: 154.00 °  * B: 173.00 °  * F: 132.00 °
```

`40 03 0A 00 01 A0 AF 05 0F 00 00 14 0F`（DLMA_CTRL）
```text
    * Register: DLMA_CTRL (A0AF)
    * Len: 5
    * Val: 0F0000140F
      * DLMA: Enable
      * APC TX AB:                Enabled     * APC TX F:                Enabled    
      * BPSK AB (m3):             Enabled     * BPSK F (m3):             Enabled    
      * Single Driver AB (m1):    Enabled     * Single Driver F (m1):    Enabled    
      * APC Arbitrary Phase AB:   Enabled     * APC Arbitrary Phase F:   Enabled    
      * APC AB uses RSSI:         Raw         * APC F uses RSSI:         Raw         
```

`40 03 0E 00 01 A0 A9 09 42 1E 80 42 1E 80 C2 28 FF`（DLMA_TX，第 2 筆與第 1 筆相同而被略過）
```text
    * Register: DLMA_TX (A0A9)
    * Len: 9
    * Val: 421E80421E80C228FF
     ~  Entry  ~  ID  ~  Equiv TX (Vpp)  ~  VDDPA (V)  ~  TxScaling  ~  Mode 3  ~  DriNum  ~  NCIcmd  ~
           0       2         6.02            3.00            128           1          2       421E80
           2       2         7.00            3.50            255           1          1       C228FF
```

`40 03 07 00 01 A0 17 02 FC FF`（RF_CUST_PHASE_COMPENSATION，修正前的失敗案例）
```text
    * Register: RF_CUST_PHAS E_COMPENSATI ON (A017)
    * Len: 2
```
上方輸出為修正前的紀錄；✅ 已修正（2026-10）後，同一封包會再印 `* Phase: -1.0 °` 並正常結束（`#end`）。
