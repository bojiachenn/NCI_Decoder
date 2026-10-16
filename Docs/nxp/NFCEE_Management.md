# NXP NFCEE Management（GID 0x2）— `Nxp_pkg/NFCEE_Management.py`

本文件說明 vendor = `Nxp` 時，GID `0x2`（NFCEE Management）各 command 的解析方式。Dispatch 表為 [`Nxp_pkg/__ctrl__.py`](../../nci_decoder/Nxp_pkg/__ctrl__.py#L53) 的 `"NFCEE Management"` 群組，handler 位於 [`Nxp_pkg/NFCEE_Management.py`](../../nci_decoder/Nxp_pkg/NFCEE_Management.py)。

**本群組 9 個 handler 全部只是 delegate**：`Origin.<HANDLER>(raw, "nxp")`，`Origin` = `nfc_forum_2_0_pkg.NFCEE_Management`。forum 函式以 `pkg_import.tbl_import("nxp", ...)` → `vendor_registry.resolve()`（不分大小寫）載入 **`Nxp_pkg.__table__`**，因此解析流程與 [forum 版文件](../nfc_forum_2_0/NFCEE_Management.md) 完全相同，唯一差異是查表內容改用 NXP 的表（見 [Tables](Tables.md)）：

| 表 | NXP 版與 forum 版差異（影響輸出） |
|---|---|
| [`tbl_nfcee_id`](Tables.md#tbl_nfcee_id) | 多了 SN2x0 具名 ID：`10` NFCEE_NDEF、`80` NFCEE_UICC1、`81` NFCEE_UICC2、`C0` NFCEE_eSE、`C1` NFCEE_eUICC Profile 1 (SEP/MEP Mode)、`C2` NFCEE_eUICC Profile 2 (MEP Mode) |
| [`tbl_nfcee_status`](Tables.md#tbl_nfcee_status) | 多了 SN2x0 專屬狀態 `80`、`81`、`91`–`9B`（eSE 溫度錯誤、UICC 斷電、eSE reboot / timeout 等） |
| [`tbl_status_codes`](Tables.md#tbl_status_codes) | NXP 版 status code 表 |

（`Nxp_pkg/NFCEE_Management.py` 的 `import Nxp_pkg.__table__ as NFC_table` 在本檔中未被使用。）

## Command 總覽

| OID | CMD | RSP | NTF | Handler（CMD / RSP / NTF） | 實作 |
|---|---|---|---|---|---|
| 0x00 | `22 00` | `42 00` | `62 00` | [NFCEE_DISCOVER_CMD](#nfcee_discover_cmd--22-00) / [NFCEE_DISCOVER_RSP](#nfcee_discover_rsp--42-00) / [NFCEE_DISCOVER_NTF](#nfcee_discover_ntf--62-00) | delegate ×3 |
| 0x01 | `22 01` | `42 01` | `62 01` | [NFCEE_MODE_SET_CMD](#nfcee_mode_set_cmd--22-01) / [NFCEE_MODE_SET_RSP](#nfcee_mode_set_rsp--42-01) / [NFCEE_MODE_SET_NTF](#nfcee_mode_set_ntf--62-01) | delegate ×3 |
| 0x02 | — | — | `62 02` | [NFCEE_STATUS_NTF](#nfcee_status_ntf--62-02) | delegate |
| 0x03 | `22 03` | `42 03` | — | [NFCEE_POWER_AND_LINK_CNTRL_CMD](#nfcee_power_and_link_cntrl_cmd--22-03) / [NFCEE_POWER_AND_LINK_CNTRL_RSP](#nfcee_power_and_link_cntrl_rsp--42-03) | delegate ×2 |

共 **9** 個 handler（OID 0x04–0x3F RFU，未定義）。

> 範例皆以 `NFC_NCI_DECODER(len, raw, 'Nxp', 'None', 2)` 實際執行取得。

### NFCEE ID 欄位的共通解析

NFCEE_DISCOVER_NTF / NFCEE_MODE_SET_CMD / NFCEE_STATUS_NTF / NFCEE_POWER_AND_LINK_CNTRL_CMD 的 NFCEE ID 皆以同一方式輸出：`* NFCEE ID: <hex> <tbl_nfcee_id.get(id, "")> <tbl_nfcee_id.get(range_key, "")>`，其中 `range_key = range_lookup.find_range_key(tbl_nfcee_id, id)`（`02-0F` / `10-7F` / `80-FE` 範圍 bucket）。所以 NXP 具名 ID 會同時印出名稱與範圍說明，例如 `C0 NFCEE_eSE (HCI-NFCEE)`；未具名的 ID 只印範圍，例如 `11  (NFCEE)`。

---

<a id="nfcee_discover_cmd"></a><a id="NFCEE_DISCOVER_CMD"></a>
## NFCEE_DISCOVER_CMD  (`22 00`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NFCEE Management / 0x00 / CMD |
| Handler | [`NFCEE_Management.py:7`](../../nci_decoder/Nxp_pkg/NFCEE_Management.py#L7) `NFCEE_DISCOVER_CMD` |
| 實作 | delegate → forum [`NFCEE_DISCOVER_CMD`](../nfc_forum_2_0/NFCEE_Management.md#nfcee_discover_cmd--22-00) |

### Payload 格式
（Empty）— 印 `(Empty)`，回傳 offset 0。

NXP 差異：無。

### 範例
- Raw：`22 00 00`
```text
  << NFCEE_DISCOVER_CMD >>  
         (Empty)         
#end
```

<a id="nfcee_discover_rsp"></a><a id="NFCEE_DISCOVER_RSP"></a>
## NFCEE_DISCOVER_RSP  (`42 00`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NFCEE Management / 0x00 / RSP |
| Handler | [`NFCEE_Management.py:17`](../../nci_decoder/Nxp_pkg/NFCEE_Management.py#L17) `NFCEE_DISCOVER_RSP` |
| 實作 | delegate → forum [`NFCEE_DISCOVER_RSP`](../nfc_forum_2_0/NFCEE_Management.md#nfcee_discover_rsp--42-00) |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |
| 2 | Number of NFCEEs | 1 | 十進位 |

NXP 差異：僅查表改用 NXP `tbl_status_codes`。

### 範例
- Raw：`42 00 02 00 02`
```text
  << NFCEE_DISCOVER_RSP >>  
  * Status: STATUS_OK (00)
  * Number of NFCEEs: 2
#end
```

<a id="nfcee_discover_ntf"></a><a id="NFCEE_DISCOVER_NTF"></a>
## NFCEE_DISCOVER_NTF  (`62 00`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NFCEE Management / 0x00 / NTF |
| Handler | [`NFCEE_Management.py:28`](../../nci_decoder/Nxp_pkg/NFCEE_Management.py#L28) `NFCEE_DISCOVER_NTF` |
| 實作 | delegate → forum [`NFCEE_DISCOVER_NTF`](../nfc_forum_2_0/NFCEE_Management.md#nfcee_discover_ntf--62-00) |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | NFCEE ID | 1 | `tbl_nfcee_id` 精確值 + range bucket（見 [Tables](Tables.md#tbl_nfcee_id)、[共通解析](#nfcee-id-欄位的共通解析)） |
| 2 | NFCEE Status | 1 | `tbl_nfcee_disc_status`（見 [Tables](Tables.md#tbl_nfcee_disc_status)） |
| 3 | Number of Protocol Information Entries | 1 (n) | 十進位 |
| 4 | Supported NFCEE Protocols [0..n] | n | 每 octet 以 `range_lookup.lookup(tbl_nfcee_proto, v)` 查表（含範圍 key，`80`–`FE` → For proprietary use，見 [Tables](Tables.md#tbl_nfcee_proto)），以 `, ` 串接 |
| 5 | Number of NFCEE Information TLVs | 1 (m) | 十進位 |
| 6 | NFCEE Information TLV [0..m] | x+2 | |
| ﹂ | Type | 1 | 先以 `range_lookup.find_range_key(tbl_tlv_type, type)` 轉成範圍 key（`05-9F` / `A0-FF`），無範圍則用原值，再查 `tbl_tlv_type`（見 [Tables](Tables.md#tbl_tlv_type)） |
| ﹂ | Len | 1 (x) | 十進位 |
| ﹂ | Val | x | 印 raw hex；Type `02` / `04` 另外拆解（見下） |
| 7 | NFCEE Power Supply | 1 | `00` NFCC control power supply for any NFCEE_UICCx；`01` … for NFCEE_eSE and NFCEE_NDEF；其他 RFU |

**TLV Type `02`（T3T Command Set Interface Supplementary Information）Val：**

| # | 欄位 | 長度 (Octets) | 解析 |
|---|---|---|---|
| 1 | PMm | 8 | hex |
| 2 | Number of Entries | 1 (k) | 十進位 |
| 3 | Entry [0..k] | 10 | |
| ﹂ | System Code | 2 | hex |
| ﹂ | Idm | 8 | hex |

**TLV Type `04`（NDEF）Val：**

| # | 欄位 | 長度 (Octets) | 解析 |
|---|---|---|---|
| 1 | NDEF max size | 4 | little endian 十進位 Bytes |
| 2 | Power State | 1 | bit 5..0 依 `tbl_pwr_state`（見 [Tables](Tables.md#tbl_pwr_state)）印 Apply / Not apply |
| 3 | NDEF-NFCEE characteristics | 1 | b0：0 Not persistent / 1 Persistent |

NXP 差異：僅查表內容不同（NFCEE ID 會顯示 SN2x0 名稱）。

### 範例
- Raw：`62 00 0C C0 00 01 00 01 00 04 11 22 33 44 01`（eSE，TLV Type 00）
```text
  << NFCEE_DISCOVER_NTF >>  
  * NFCEE ID: C0 NFCEE_eSE (HCI-NFCEE)
  * NFCEE Status: Enabled (00)
  * Number of Protocol Info Entries: 1
  * Supported NFCEE Protocols: APDU (00), 
  * Number of NFCEE Info TLVs: 1
  * NFCEE Information:

   ~ [NFCEE Info TLV_0] ~  
    * Type: Hardware / Registration Identification (00)
    * Len: 4
    * Val: 11223344

  * NFCEE Power Supply: NFCC control power supply for NFCEE_eSE and NFCEE_NDEF
#end
```
- Raw：`62 00 0E 10 00 01 03 01 04 06 00 10 00 00 01 01 01`（NFCEE_NDEF，TLV Type 04）
```text
  << NFCEE_DISCOVER_NTF >>  
  * NFCEE ID: 10 NFCEE_NDEF (NFCEE)
  * NFCEE Status: Enabled (00)
  * Number of Protocol Info Entries: 1
  * Supported NFCEE Protocols: Transparent (03), 
  * Number of NFCEE Info TLVs: 1
  * NFCEE Information:

   ~ [NFCEE Info TLV_0] ~  
    * Type: NDEF (04)
    * Len: 6
    * Val: 001000000101
      * NDEF max size: 4096 Bytes (00100000)
      * Power State: 00000001 (01)
       ~ Screen Off lock (Sub-State 3):    Not apply 
       ~ Screen On lock (Sub-State 2):     Not apply 
       ~ Screen off unlock (Sub-State 1):  Not apply 
       ~ Battery Off State:                Not apply 
       ~ Switch Off State:                 Not apply 
       ~ Switch On State:                  Apply     
      * NDEF-NFCEE characteristics: Persistent

  * NFCEE Power Supply: NFCC control power supply for NFCEE_eSE and NFCEE_NDEF
#end
```
- Raw：`62 00 1B 11 01 01 02 01 02 13 01 02 03 04 05 06 07 08 01 12 FC 02 FE 00 00 00 00 00 01 00`（TLV Type 02 T3T）
```text
  << NFCEE_DISCOVER_NTF >>  
  * NFCEE ID: 11  (NFCEE)
  * NFCEE Status: Disabled (01)
  * Number of Protocol Info Entries: 1
  * Supported NFCEE Protocols: Type 3 Tag Command Set (02), 
  * Number of NFCEE Info TLVs: 1
  * NFCEE Information:

   ~ [NFCEE Info TLV_0] ~  
    * Type: T3T Command Set Interface Supplementary Information (02)
    * Len: 19
    * Val: 01020304050607080112FC02FE000000000001
      * PMm: 0102030405060708
      * Number of Entries: 1
       ~ [Entry_0] ~   
        * System Code: 12FC
        * Idm: 02FE000000000001

  * NFCEE Power Supply: NFCC control power supply for any NFCEE_UICCx
#end
```
- Raw：`62 00 0E 80 00 01 80 02 00 03 01 02 03 A5 01 FF 00`（UICC1，proprietary protocol / TLV type）
```text
  << NFCEE_DISCOVER_NTF >>  
  * NFCEE ID: 80 NFCEE_UICC1 (HCI-NFCEE)
  * NFCEE Status: Enabled (00)
  * Number of Protocol Info Entries: 1
  * Supported NFCEE Protocols: For proprietary use (80), 
  * Number of NFCEE Info TLVs: 2
  * NFCEE Information:

   ~ [NFCEE Info TLV_0] ~  
    * Type: Hardware / Registration Identification (00)
    * Len: 3
    * Val: 010203

   ~ [NFCEE Info TLV_1] ~  
    * Type: For proprietary use (A5)
    * Len: 1
    * Val: FF

  * NFCEE Power Supply: NFCC control power supply for any NFCEE_UICCx
#end
```

### 實作備註
- ✅ 已修正（2026-10）：Supported NFCEE Protocols 改用 `range_lookup.lookup()`，`80`–`FE` 正確顯示為 `For proprietary use`（見上例 `80`）。
- Supported NFCEE Protocols 清單結尾會多一個 `, `。
- TLV Type `02`/`04` 的子欄位以固定 offset 切 Val，不檢查 Len；Val 不足時子欄位印空字串或 `int('')` 例外。

<a id="nfcee_mode_set_cmd"></a><a id="NFCEE_MODE_SET_CMD"></a>
## NFCEE_MODE_SET_CMD  (`22 01`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NFCEE Management / 0x01 / CMD |
| Handler | [`NFCEE_Management.py:47`](../../nci_decoder/Nxp_pkg/NFCEE_Management.py#L47) `NFCEE_MODE_SET_CMD` |
| 實作 | delegate → forum [`NFCEE_MODE_SET_CMD`](../nfc_forum_2_0/NFCEE_Management.md#nfcee_mode_set_cmd--22-01) |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | NFCEE ID | 1 | `tbl_nfcee_id` 精確值 + range bucket（見 [Tables](Tables.md#tbl_nfcee_id)） |
| 2 | NFCEE Mode | 1 | `00` Disable、`01` Enable，其他 `RFU (xx)` |

NXP 差異：NFCEE ID 顯示 SN2x0 名稱。

### 範例
- Raw：`22 01 02 C0 01`
```text
  << NFCEE_MODE_SET_CMD >>  
  * NFCEE ID: C0 NFCEE_eSE (HCI-NFCEE)
  * NFCEE Mode: Enable
#end
```
- Raw：`22 01 02 81 02`
```text
  << NFCEE_MODE_SET_CMD >>  
  * NFCEE ID: 81 NFCEE_UICC2 (HCI-NFCEE)
  * NFCEE Mode: RFU (02)
#end
```

<a id="nfcee_mode_set_rsp"></a><a id="NFCEE_MODE_SET_RSP"></a>
## NFCEE_MODE_SET_RSP  (`42 01`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NFCEE Management / 0x01 / RSP |
| Handler | [`NFCEE_Management.py:58`](../../nci_decoder/Nxp_pkg/NFCEE_Management.py#L58) `NFCEE_MODE_SET_RSP` |
| 實作 | delegate → forum [`NFCEE_MODE_SET_RSP`](../nfc_forum_2_0/NFCEE_Management.md#nfcee_mode_set_rsp--42-01) |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |

NXP 差異：無（查 NXP 表）。

### 範例
- Raw：`42 01 01 00`
```text
  << NFCEE_MODE_SET_RSP >>  
  * Status: STATUS_OK (00)
#end
```

<a id="nfcee_mode_set_ntf"></a><a id="NFCEE_MODE_SET_NTF"></a>
## NFCEE_MODE_SET_NTF  (`62 01`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NFCEE Management / 0x01 / NTF |
| Handler | [`NFCEE_Management.py:68`](../../nci_decoder/Nxp_pkg/NFCEE_Management.py#L68) `NFCEE_MODE_SET_NTF` |
| 實作 | delegate → forum [`NFCEE_MODE_SET_NTF`](../nfc_forum_2_0/NFCEE_Management.md#nfcee_mode_set_ntf--62-01) |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |

NXP 差異：無（查 NXP 表）。

### 範例
- Raw：`62 01 01 00`
```text
  << NFCEE_MODE_SET_NTF >>  
  * Status: STATUS_OK (00)
#end
```

<a id="nfcee_status_ntf"></a><a id="NFCEE_STATUS_NTF"></a>
## NFCEE_STATUS_NTF  (`62 02`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NFCEE Management / 0x02 / NTF |
| Handler | [`NFCEE_Management.py:78`](../../nci_decoder/Nxp_pkg/NFCEE_Management.py#L78) `NFCEE_STATUS_NTF` |
| 實作 | delegate → forum [`NFCEE_STATUS_NTF`](../nfc_forum_2_0/NFCEE_Management.md#nfcee_status_ntf--62-02) |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | NFCEE ID | 1 | `tbl_nfcee_id` 精確值 + range bucket（見 [Tables](Tables.md#tbl_nfcee_id)） |
| 2 | NFCEE Status | 1 | `range_lookup.lookup(tbl_nfcee_status, v)`（含範圍 key `03-7F` → RFU；查不到亦為 RFU；見 [Tables](Tables.md#tbl_nfcee_status)，含 SN2x0 `80`/`81`/`91`–`9B`） |

NXP 差異：NFCEE ID 顯示 SN2x0 名稱；NFCEE Status 多了 SN2x0 專屬錯誤狀態。

### 範例
- Raw：`62 02 02 C0 02`
```text
  << NFCEE_STATUS_NTF >>  
  * NFCEE ID: C0 NFCEE_eSE (HCI-NFCEE)
  * NFCEE Status: NFCEE Initialization sequence completed (02)
#end
```
- Raw：`62 02 02 C0 94`（SN2x0 專屬狀態）
```text
  << NFCEE_STATUS_NTF >>  
  * NFCEE ID: C0 NFCEE_eSE (HCI-NFCEE)
  * NFCEE Status: NFCC has received an internal eSE temperature error (94)
#end
```
- Raw：`62 02 02 C0 85`（表中未定義）
```text
  << NFCEE_STATUS_NTF >>  
  * NFCEE ID: C0 NFCEE_eSE (HCI-NFCEE)
  * NFCEE Status: RFU (85)
#end
```

### 實作備註
- NXP `tbl_nfcee_status` 中 `92` 與 `93`、`96` 與 `97` 的描述文字相同（以表內容為準，程式未區分）。

<a id="nfcee_power_and_link_cntrl_cmd"></a><a id="NFCEE_POWER_AND_LINK_CNTRL_CMD"></a>
## NFCEE_POWER_AND_LINK_CNTRL_CMD  (`22 03`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NFCEE Management / 0x03 / CMD |
| Handler | [`NFCEE_Management.py:89`](../../nci_decoder/Nxp_pkg/NFCEE_Management.py#L89) `NFCEE_POWER_AND_LINK_CNTRL_CMD` |
| 實作 | delegate → forum [`NFCEE_POWER_AND_LINK_CNTRL_CMD`](../nfc_forum_2_0/NFCEE_Management.md#nfcee_power_and_link_cntrl_cmd--22-03) |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | NFCEE ID | 1 | `tbl_nfcee_id` 精確值 + range bucket（見 [Tables](Tables.md#tbl_nfcee_id)） |
| 2 | NFCEE Power and Link Configuration | 1 | `00` NFCC decides (default state)；`01` NFCEE Power Supply always On；`02` NFCC to NFCEE Communication link always active when the NFCEE is powered on；`03` Power supply 與 communication link 皆 always on；其他 `RFU (xx)` |

NXP 差異：NFCEE ID 顯示 SN2x0 名稱。

### 範例
- Raw：`22 03 02 C0 03`
```text
  << NFCEE_POWER_AND_LINK_CNTRL_CMD >>  
  * NFCEE ID: C0 NFCEE_eSE (HCI-NFCEE)
  * NFCEE Power and Link Cfg: NFCEE Power supply and NFCC to NFCEE communication link are always on.
#end
```
- Raw：`22 03 02 C0 05`
```text
  << NFCEE_POWER_AND_LINK_CNTRL_CMD >>  
  * NFCEE ID: C0 NFCEE_eSE (HCI-NFCEE)
  * NFCEE Power and Link Cfg: RFU (05)
#end
```

<a id="nfcee_power_and_link_cntrl_rsp"></a><a id="NFCEE_POWER_AND_LINK_CNTRL_RSP"></a>
## NFCEE_POWER_AND_LINK_CNTRL_RSP  (`42 03`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | NFCEE Management / 0x03 / RSP |
| Handler | [`NFCEE_Management.py:100`](../../nci_decoder/Nxp_pkg/NFCEE_Management.py#L100) `NFCEE_POWER_AND_LINK_CNTRL_RSP` |
| 實作 | delegate → forum [`NFCEE_POWER_AND_LINK_CNTRL_RSP`](../nfc_forum_2_0/NFCEE_Management.md#nfcee_power_and_link_cntrl_rsp--42-03) |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [Tables](Tables.md#tbl_status_codes)） |

NXP 差異：無（查 NXP 表）。

### 範例
- Raw：`42 03 01 00`
```text
  << NFCEE_POWER_AND_LINK_CNTRL_RSP >>  
  * Status: STATUS_OK (00)
#end
```

### 實作備註
- 函式上方註解寫 `# 22 03`，實際 header 為 `42 03`（僅註解錯誤，dispatch 正確）。
