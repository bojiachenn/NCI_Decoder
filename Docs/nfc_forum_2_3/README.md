# NFC Forum NCI 2.3 增量套件（`nfc_forum_2_3_pkg`）

`nci_decoder/nfc_forum_2_3_pkg/` 是 NCI 2.3 相對於基準套件 `nfc_forum_2_0_pkg` 的增量版本：`__ctrl__.py` 多註冊了 RF Management OID `0x12`–`0x15`（Removal Detection、WLC 無線充電相關訊息），`__table__.py` 換成 NCI 2.3 的 Table 編號，並補了 2.3 新增的列舉值。其他 handler 整份是從 2.0 套件複製來的，但複製發生在 2.0 套件後續幾次修正**之前**，所以兩邊的既有 handler 已經不一樣了（詳見[第 2 節](#2-與-nfc_forum_2_0_pkg-的差異總表)）。

本文件只描述 2.3 和 2.0 的**差異**。沒列出的部分，請直接看 [`../nfc_forum_2_0/`](../nfc_forum_2_0/) 的對應文件。

## 指令總覽（2.3 新增）

| OID | CMD | RSP | NTF | Handler |
|---|---|---|---|---|
| 0x12 | `21 12` | `41 12` | `61 12` | [RF_REMOVAL_DETECTION_CMD](#rf_removal_detection_cmd) / [RSP](#rf_removal_detection_rsp) / [NTF](#rf_removal_detection_ntf) |
| 0x13 | – | – | `61 13` | [RF_WLC_STATUS_NTF](#rf_wlc_status_ntf) |
| 0x14 | `21 14` | `41 14` | （`__ctrl__` 中已註解掉） | [GET_WLCP_INFO_PARAM_CMD](#get_wlcp_info_param_cmd) / [RSP](#get_wlcp_info_param_rsp) |
| 0x15 | `21 15` | `41 15` | `61 15` | [WPT_START_CMD](#wpt_start_cmd) / [RSP](#wpt_start_rsp) / [NTF](#wpt_start_ntf) |

所有新增 handler 都放在 `RF_Management.py`，GID = RF Management (1)。

---

## 1. 狀態：刻意未接上 dispatch

依 repo 的 [`CLAUDE.md`](../../CLAUDE.md) 說明：

- `nfc_forum_2_3_pkg` **刻意沒有註冊到** `nci_decoder/vendor_registry.py`。因此 `Decoder_Main.NFC_NCI_DECODER` 不管 vendor 傳什麼，都不會走進這個套件。`vendor="None"` 會落到預設的 `nfc_forum_2_0_pkg`，`"Nxp"` 則走 `Nxp_pkg`。
- 原因：這個套件是「NCI 規範**版本**」的增量，不是新的**廠商**，和 `vendor_registry.py` 建模的維度（vendor）互相正交。如果硬塞進 registry，就得提前做設計決策：是新增一個 `mode`／版本軸，還是重載 vendor key？要讓它可以 dispatch，得另外做後續設計。
- `nci_decoder/__init__.py` 仍然會把 `nfc_forum_2_3_pkg` 加進 `sys.path`，讓它**可以 import 但無法 dispatch**。另外 `NCI_Decoder.spec` 的 `hiddenimports` 是否包含此套件，與本文件無關。

### 如何直接呼叫（本文範例的產生方式）

```python
import sys
sys.path.insert(0, "E:/Project/NCI_Decoder/NCI_Decoder/nci_decoder")
sys.path.insert(0, "E:/Project/NCI_Decoder/NCI_Decoder/nci_decoder/nfc_forum_2_3_pkg")
from nfc_forum_2_3_pkg import RF_Management
RF_Management.RF_WLC_STATUS_NTF("0501E30132015A")   # 傳入 header 之後的 payload
```

> 關於 `__pkg_import__.tbl_import` 的疑慮：2.3 套件的三個 handler 檔都在檔頭寫了 `import nfc_forum_2_3_pkg.__table__ as NFC_table`，並把每個 handler 裡的 `NFC_table = pkg_import.tbl_import(vendor, model)` **註解掉**，所以 handler 用的是 2.3 自己的表，不會解析到 2.0 的表。檔頭仍保留 `import __pkg_import__ as pkg_import`，因此 `sys.path` 一定要包含 `nci_decoder/`。本文所有範例都以上述方式實際執行，輸出照貼。範例中的 `[return x / declared y]` 是腳本另外印出的 handler 回傳值與 header 宣告長度（hex 字元數），用來模擬 `Decoder_Main` 的 `Payload error!!` 檢查，不是 handler 本身的輸出。

---

## 2. 與 `nfc_forum_2_0_pkg` 的差異總表

比對方式：`diff -u nfc_forum_2_0_pkg/<f>.py nfc_forum_2_3_pkg/<f>.py`。

| 檔案 | diff 行數 | 摘要 |
|---|---|---|
| `__ctrl__.py` | 23 | import 改為 2.3 模組；新增 RF OID `12`–`15` |
| `NCI_Core.py` | 689 | 無新增 handler；表來源、輸出格式、CORE_RESET_NTF / CORE_INIT_RSP / VALUE_OF_CFG_PARA 等有語意差異，新增 4 個設定參數 |
| `RF_Management.py` | 1158 | 新增 9 個 handler；既有 handler 有表來源、輸出格式差異，另有數個 2.0 已修好、2.3 沒同步的 bug |
| `NFCEE_Management.py` | 255 | 無新增 handler；表來源、range bucket 寫法、輸出格式、NDEF max size 解析不同 |
| `__table__.py` | 598 | 新增 2 張表；15 張表值有增修；所有表的 Table 編號改成 NCI 2.3 編號 |

> 方向說明：從 git 紀錄看，`nfc_forum_2_3_pkg` 最後一次修改是 `f05d612`。`nfc_forum_2_0_pkg` 之後又有 `5f5cb72`（NFCEE ID range-collapse crash 修正）、`5d073dc`、`7b7964f`（改用 `range_lookup`）等提交，2.3 都沒有同步。下表很多「差異」其實是 **2.0 已修正、2.3 仍是舊寫法**，不是 NCI 2.3 規範本身的變更。下文會在相關處標註「（2.0 已修、2.3 未同步）」。

### 2.1 `__ctrl__.py` 新增的 OID

| GID | OID | CMD | RSP | NTF |
|---|---|---|---|---|
| RF Management | `12` | `RF_REMOVAL_DETECTION_CMD` | `RF_REMOVAL_DETECTION_RSP` | `RF_REMOVAL_DETECTION_NTF` |
| RF Management | `13` | – | – | `RF_WLC_STATUS_NTF` |
| RF Management | `14` | `GET_WLCP_INFO_PARAM_CMD` | `GET_WLCP_INFO_PARAM_RSP` | （`# "NTF": RF_Management.GET_WLCP_INFO_PARAM_NTF` 已註解，函式也不存在） |
| RF Management | `15` | `WPT_START_CMD` | `WPT_START_RSP` | `WPT_START_NTF` |

其他變更：檔頭三行 import 從 `nfc_forum_2_0_pkg` 改成 `nfc_forum_2_3_pkg`。OID `15` 之後的註解仍寫 `# 12 ~ 63 RFU`，沒有更新。NCI Core 和 NFCEE Management 兩個 GID 沒有新增 OID。

### 2.2 各 .py 新增的 handler

全部在 `RF_Management.py`：

| Handler | 行號 | Header |
|---|---|---|
| `RF_REMOVAL_DETECTION_CMD` | [L1318](../../nci_decoder/nfc_forum_2_3_pkg/RF_Management.py#L1318) | `21 12` |
| `RF_REMOVAL_DETECTION_RSP` | [L1334](../../nci_decoder/nfc_forum_2_3_pkg/RF_Management.py#L1334) | `41 12` |
| `RF_REMOVAL_DETECTION_NTF` | [L1349](../../nci_decoder/nfc_forum_2_3_pkg/RF_Management.py#L1349) | `61 12` |
| `RF_WLC_STATUS_NTF` | [L1364](../../nci_decoder/nfc_forum_2_3_pkg/RF_Management.py#L1364) | `61 13` |
| `GET_WLCP_INFO_PARAM_CMD` | [L1434](../../nci_decoder/nfc_forum_2_3_pkg/RF_Management.py#L1434) | `21 14` |
| `GET_WLCP_INFO_PARAM_RSP` | [L1458](../../nci_decoder/nfc_forum_2_3_pkg/RF_Management.py#L1458) | `41 14` |
| `WPT_START_CMD` | [L1500](../../nci_decoder/nfc_forum_2_3_pkg/RF_Management.py#L1500) | `21 15` |
| `WPT_START_RSP` | [L1538](../../nci_decoder/nfc_forum_2_3_pkg/RF_Management.py#L1538) | `41 15` |
| `WPT_START_NTF` | [L1553](../../nci_decoder/nfc_forum_2_3_pkg/RF_Management.py#L1553) | `61 15` |

`NCI_Core.py`、`NFCEE_Management.py` 沒有新增函式。兩個套件的函式集合，除了上面 9 個以外完全一樣。

### 2.3 全檔共通差異（適用於三個 handler 檔的所有既有 handler）

| # | 項目 | 2.0 | 2.3 |
|---|---|---|---|
| C1 | 表來源 | 每個 handler 內呼叫 `NFC_table = pkg_import.tbl_import(vendor, model)` | 檔頭 `import nfc_forum_2_3_pkg.__table__ as NFC_table`，handler 內的 `tbl_import` 已註解。`vendor`/`model` 參數不影響查表 |
| C2 | 查表輸出格式 | `print("...: "+tbl.get(v,"RFU"), "("+v+")")`：不論查得到與否都附 `(xx)` | `tbl.get(v, "RFU ("+v+")")`：查得到只印名稱，查不到印 `RFU (xx)` |
| C3 | 重複結構間的空行 | 每筆 list 項目（`~ [xxx_i] ~`）前會 `print()` | 不印空行 |
| C4 | range bucket | 用 `range_lookup.find_range_key(table, int)`，NFCEE ID 等會同時印精確值與 bucket 說明 | 手寫 `if/elif` 把值收斂成 `'02-0F'`/`'10-7F'`/`'80-FE'` 等 key 再查表（`5f5cb72` 之前的寫法）。檔頭沒有 `import range_lookup`（2.0 已修、2.3 未同步） |

### 2.4 既有 handler 的語意差異（逐一列出）

下表只列 C1–C4 以外的差異。「2.0 文件」欄連到 2.0 版文件的對應章節。

#### NCI_Core.py

| Handler（2.3 行號） | 差異 | 2.0 文件 |
|---|---|---|
| `CORE_RESET_NTF` ([L36](../../nci_decoder/nfc_forum_2_3_pkg/NCI_Core.py#L36)) | NCI Version 不查 `tbl_nci_ver`，改把高/低 nibble 當 major/minor 直接印 `X.Y (xx)`，例如 `23` 印成 `2.3 (23)` | [core_reset_ntf](../nfc_forum_2_0/NCI_Core.md#core_reset_ntf) |
| `CORE_INIT_CMD` ([L82](../../nci_decoder/nfc_forum_2_3_pkg/NCI_Core.py#L82)) | Feature Enable 後綴從 `-- RFU` 改成 `--refer to Table 9`，仍未解析 | [core_init_cmd](../nfc_forum_2_0/NCI_Core.md#core_init_cmd) |
| `CORE_INIT_RSP` ([L99](../../nci_decoder/nfc_forum_2_3_pkg/NCI_Core.py#L99)) | **新增** NFCC Features Octet 0 bit 5「Removal Detection in Poll Mode」（Support/Not support）。Octet 標籤從 `Octet N` 改為 `octetN`。Octet 3 多印一行 `Octet_3 is reserved for proprietary capabilities`。`HCI Network Support` 文字改為 `As defined in [ETSI_102622]`。Max Routing Table Size、Max NFC-V RF Frame Size 印 `int(hex,16)`（以 big-endian 解讀 2 octets；2.0 自 2026-10 起改為 little-endian 十進位並附 raw hex）。Max Logical Connections、Max Control Packet Payload Size 等欄位不再附 `(xx)` | [core_init_rsp](../nfc_forum_2_0/NCI_Core.md#core_init_rsp) |
| `CORE_SET_CONFIG_RSP` ([L275](../../nci_decoder/nfc_forum_2_3_pkg/NCI_Core.py#L275)) | 標籤 `Set Param ID:` 改為 `Param ID:` | [core_set_config_rsp](../nfc_forum_2_0/NCI_Core.md#core_set_config_rsp) |
| `CORE_GET_CONFIG_CMD` ([L306](../../nci_decoder/nfc_forum_2_3_pkg/NCI_Core.py#L306)) | 標籤 `Get Param ID:` 改為 `Param ID:` | [core_get_config_cmd](../nfc_forum_2_0/NCI_Core.md#core_get_config_cmd) |
| `CORE_SET_CONFIG_CMD` / `CORE_GET_CONFIG_RSP` ([L235](../../nci_decoder/nfc_forum_2_3_pkg/NCI_Core.py#L235) / [L331](../../nci_decoder/nfc_forum_2_3_pkg/NCI_Core.py#L331)) | 結構相同，Val 交給 `VALUE_OF_CFG_PARA`，差異見下面 `VALUE_OF_CFG_PARA` 列；ID 查 2.3 的 `tbl_cfg_para`（新增 `69`/`6A`/`6B`/`86`） | [core_set_config_cmd](../nfc_forum_2_0/NCI_Core.md#core_set_config_cmd) / [core_get_config_rsp](../nfc_forum_2_0/NCI_Core.md#core_get_config_rsp) |
| `CORE_CONN_CREATE_RSP` ([L448](../../nci_decoder/nfc_forum_2_3_pkg/NCI_Core.py#L448)) | Conn ID 輸出少了結尾 `)`，例如印成 `* Conn ID: 0 (Static: DH -- Remote NFC Endpoint`（2.0 已修、2.3 未同步） | [core_conn_create_rsp](../nfc_forum_2_0/NCI_Core.md#core_conn_create_rsp) |
| `CORE_CONN_CREDITS_NTF` ([L514](../../nci_decoder/nfc_forum_2_3_pkg/NCI_Core.py#L514)) | 同上，Conn ID 少結尾 `)` | [core_conn_credits_ntf](../nfc_forum_2_0/NCI_Core.md#core_conn_credits_ntf) |
| `CORE_SET_POWER_SUB_STATE_CMD` ([L583](../../nci_decoder/nfc_forum_2_3_pkg/NCI_Core.py#L583)) | 只印 `Power State: Switched On ...`，不印 2.0 額外的 `Screen:` / `Device:` 兩行 | [core_set_power_sub_state_cmd](../nfc_forum_2_0/NCI_Core.md#core_set_power_sub_state_cmd) |
| `VALUE_OF_CFG_PARA` ([L624](../../nci_decoder/nfc_forum_2_3_pkg/NCI_Core.py#L624)，被 SET/GET_CONFIG 呼叫) | **新增參數**：`69` WLC-P_CAP_POWER_CLASS（印 8-bit 二進位 + hex）、`6A` TOT_POWER_STEPS（印 `N step (xx)`）、`6B` WLC_AUTO_CAPABILITIES（印 `N step (xx)`，再依 bit4..bit0 逐行列出支援 T5T/T4BT/T4AT/T3T/T2T 的 WLC 協定）、`86` RF_WLC_STATUS_CONFIG（`00` 不允許 / `01` 允許 NFCC 送 RF_WLC_STATUS_NTF，其他印 `0x02-0x7F RFU, 0x80-0xFF Proprietary`）。<br>**既有參數差異**：`00` TOTAL_DURATION 用 `int(val,16)`（big-endian），2.0 先 byte-swap 成 little-endian 再轉，並附 hex；`53` LF_T3T_FLAGS 的 bit 串接順序是 `oct1_r + oct0_r`，2.0 是 `oct0_r + oct1_r`，兩版對 IDENTIFIERS_1..16 的 Enabled 判讀相反；`31` LA_PLATFORM_CONFIG 的說明文字誤寫成 `Bit Frame SDD value ...`；`2A`/`62` 不印 LR 位元值；`08`/`11`/`19` BAIL_OUT、`28` PN_NFC_DEP_PSL、`03` POWER_STATE、`80`/`81`/`82` 改用規範原文式的長句描述 | [core_set_config_cmd](../nfc_forum_2_0/NCI_Core.md#core_set_config_cmd) |

`CORE_RESET_CMD/RSP`、`CORE_CONN_CREATE_CMD`、`CORE_CONN_CLOSE_CMD/RSP`、`CORE_GENERIC_ERROR_NTF`、`CORE_INTERFACE_ERROR_NTF`、`CORE_SET_POWER_SUB_STATE_RSP` 只有 C1–C3 的差異。

#### RF_Management.py

| Handler（2.3 行號） | 差異 | 2.0 文件 |
|---|---|---|
| `LISTEN_MODE_ROUTING_INFO`（[L57](../../nci_decoder/nfc_forum_2_3_pkg/RF_Management.py#L57)，被 `RF_SET_LISTEN_MODE_ROUTING_CMD` / `RF_GET_LISTEN_MODE_ROUTING_NTF` 呼叫） | Route 用手寫 bucket（C4），印成 `Route: xx (說明)`。Power State 欄寬 35、左對齊。**System Code-based（type 3）/ APDU Pattern-based（type 4）**：✅ 已修正（2026-10）：原本 `(x-2)/2` 是 float，會丟 `TypeError`；現改為 `(x-2)//2`，不再丟例外（`21 01 08 00 01 03 04 01 3B FE FE` 印出 `SC Route 0: FEFE`）。APDU 的 Reference data / Mask 仍只印第 1 octet、AID 仍用 `val_payload < x` 條件（2.0 已修、2.3 未同步） | [rf_set_listen_mode_routing_cmd](../nfc_forum_2_0/RF_Management.md#rf_set_listen_mode_routing_cmd) / [rf_get_listen_mode_routing_ntf](../nfc_forum_2_0/RF_Management.md#rf_get_listen_mode_routing_ntf) |
| `RF_TECH_SPEC_PARA`（[L296](../../nci_decoder/nfc_forum_2_3_pkg/RF_Management.py#L296)，被 `RF_DISCOVER_NTF` / `RF_INTF_ACTIVATED_NTF` 呼叫） | ✅ 已修正（2026-10）：`F_PASSIVE_LISTEN`、`ACTIVE_POLL`、`ACTIVE_LISTEN` 三個分支原本誤用未定義的 `p_payload`，會丟 `UnboundLocalError`；現已改用 `para_payload`，`61 03 06 01 03 82 01 00 02` 可正常解析。2.0 的「以宣告長度為界」解析（`_SubRaw`）、依 hex code 分支等改動 2.3 仍未同步 | [rf_discover_ntf](../nfc_forum_2_0/RF_Management.md#rf_discover_ntf) / [rf_intf_activated_ntf](../nfc_forum_2_0/RF_Management.md#rf_intf_activated_ntf) |
| `RF_DEACTIVATE_NTF`（[L755](../../nci_decoder/nfc_forum_2_3_pkg/RF_Management.py#L755)） | 程式碼只有 C1/C2 差異，但 2.3 `tbl_deactivate_reason` 多了 `05`–`08`，所以 `05` 會印 `RF_REMOTE_ENDPOINT_REMOVED`，不再是 `RFU` | [rf_deactivate_ntf](../nfc_forum_2_0/RF_Management.md#rf_deactivate_ntf) |
| `RF_NFCEE_ACTION_NTF`（[L862](../../nci_decoder/nfc_forum_2_3_pkg/RF_Management.py#L862)） | NFCEE ID、Trigger 用手寫 bucket（C4）。Trigger 只把 `10`–`7F` 收斂成 `'10-7F'`，`06`–`0F`、`80`–`FF` 查表會得到 `RFU (xx)`。✅ 已修正（2026-10）：Trigger `04` 原本以 `n/2`（float）切片會丟例外，現改為 `2*(n//2)` 個 hex 字元切出 Reference data / Mask（`61 09 07 02 04 04 00 A4 FF FF` 印 `00A4` / `FFFF`） | [rf_nfcee_action_ntf](../nfc_forum_2_0/RF_Management.md#rf_nfcee_action_ntf) |
| `RF_NFCEE_DISCOVERY_REQ_NTF`（[L914](../../nci_decoder/nfc_forum_2_3_pkg/RF_Management.py#L914)） | Type、NFCEE ID、RF Technology & Mode 用手寫 bucket（C4）。Mode 只收斂 `70-7F`、`F0-FF` | [rf_nfcee_discovery_req_ntf](../nfc_forum_2_0/RF_Management.md#rf_nfcee_discovery_req_ntf) |
| `RF_SET_FORCED_NFCEE_ROUTING_CMD`（[L1254](../../nci_decoder/nfc_forum_2_3_pkg/RF_Management.py#L1254)） | ✅ 已修正（2026-10）：State = `01` 時最後一行原本寫成 `val_payload = val_payload + 2*1`，會丟 `UnboundLocalError: ... 'val_payload'`；現已改為 `p_payload`，`21 11 03 01 80 3B` 可正常解析 | [rf_set_forced_nfcee_routing_cmd](../nfc_forum_2_0/RF_Management.md#rf_set_forced_nfcee_routing_cmd) |

其餘 RF handler（`RF_DISCOVER_MAP_CMD/RSP`、`RF_SET/GET_LISTEN_MODE_ROUTING_RSP`、`RF_GET_LISTEN_MODE_ROUTING_CMD`、`RF_DISCOVER_CMD/RSP`、`RF_DISCOVER_SELECT_CMD/RSP`、`RF_DEACTIVATE_CMD/RSP`、`RF_FIELD_INFO_NTF`、`RF_T3T_POLLING_*`、`RF_PARAMETER_UPDATE_CMD/RSP`、`RF_INTF_EXT_*`、`RF_EXT_AGG_ABORT_*`、`RF_NDEF_ABORT_*`、`RF_ISO_DEP_NAK_PRESENCE_*`、`RF_SET_FORCED_NFCEE_ROUTING_RSP`）只有 C1–C3 差異。`RF_DISCOVER_SELECT_CMD` 的 RF Interface 查不到時會印 `RFU (<RF Protocol 值>)`（誤用 `rf_proto`），2.3 仍有此錯誤（2.0 已於 2026-10 修正為印 `rf_if`）。

#### NFCEE_Management.py

| Handler（2.3 行號） | 差異 | 2.0 文件 |
|---|---|---|
| `NFCEE_DISCOVER_NTF`（[L40](../../nci_decoder/nfc_forum_2_3_pkg/NFCEE_Management.py#L40)） | NFCEE ID、TLV Type 用手寫 bucket（C4）。Supported NFCEE Protocols 先印原始 hex，再逐行印 `Protocol i:`（2.0 印在同一行，用逗號分隔）。TLV `04` 的 **NDEF max size 只印原始 4 octets hex**（2.0 會 byte-swap 轉成 little-endian 十進位 `N Bytes`）。NDEF-NFCEE characteristics 改用長句。NFCEE Power Supply 文字：`00` = `NFCC no control`，`01` = `NFCC control`（2.0 是較完整的 UICC/eSE 說明） | [nfcee_discover_ntf](../nfc_forum_2_0/NFCEE_Management.md#nfcee_discover_ntf) |
| `NFCEE_MODE_SET_CMD`（[L155](../../nci_decoder/nfc_forum_2_3_pkg/NFCEE_Management.py#L155)） | NFCEE ID 手寫 bucket（C4） | [nfcee_mode_set_cmd](../nfc_forum_2_0/NFCEE_Management.md#nfcee_mode_set_cmd) |
| `NFCEE_STATUS_NTF`（[L220](../../nci_decoder/nfc_forum_2_3_pkg/NFCEE_Management.py#L220)） | NFCEE ID 手寫 bucket（C4） | [nfcee_status_ntf](../nfc_forum_2_0/NFCEE_Management.md#nfcee_status_ntf) |
| `NFCEE_POWER_AND_LINK_CNTRL_CMD`（[L248](../../nci_decoder/nfc_forum_2_3_pkg/NFCEE_Management.py#L248)） | NFCEE ID 手寫 bucket（C4） | [nfcee_power_and_link_cntrl_cmd](../nfc_forum_2_0/NFCEE_Management.md#nfcee_power_and_link_cntrl_cmd) |

`NFCEE_DISCOVER_CMD/RSP`、`NFCEE_MODE_SET_RSP/NTF`、`NFCEE_POWER_AND_LINK_CNTRL_RSP` 只有 C1–C2 差異。

### 2.5 `__table__.py` 差異

| 類別 | 表 |
|---|---|
| **新增表** | [`tbl_wlc_poll_tlv`](#tbl_wlc_poll_tlv)、[`tbl_wpt_start_cmd_tlv`](#tbl_wpt_start_cmd_tlv) |
| **值有增修** | [`tbl_rf_proto`](#tbl_rf_proto)、[`tbl_rf_if`](#tbl_rf_if)、[`tbl_rf_if_exten`](#tbl_rf_if_exten)、[`tbl_nci_ver`](#tbl_nci_ver)、[`tbl_nfcc_feat_oct2`](#tbl_nfcc_feat_oct2)、[`tbl_nfcee_id`](#tbl_nfcee_id)、[`tbl_d_spec_type`](#tbl_d_spec_type)、[`tbl_cfg_para`](#tbl_cfg_para)、[`tbl_pwr_state`](#tbl_pwr_state)、[`tbl_rf_dis_id`](#tbl_rf_dis_id)、[`tbl_deactivate_reason`](#tbl_deactivate_reason)、[`tbl_nfcee_disc_req_type`](#tbl_nfcee_disc_req_type)、[`tbl_nfcee_ntf_trig`](#tbl_nfcee_ntf_trig)、[`tbl_rf_commu_para_id`](#tbl_rf_commu_para_id)、[`tbl_tlv_type`](#tbl_tlv_type) |
| **只改 Table 編號（`name` 欄位與註解），值完全相同** | 見下表 |
| **完全相同** | `tbl_cfg_status`、`tbl_conn_id`、`tbl_dest_type`、`tbl_init_credits`、`tbl_nfcc_feat_oct1`、`tbl_nfcee_disc_status`、`tbl_rf_field_status`、`tbl_rst_trig`（請看 [2.0 Tables](../nfc_forum_2_0/Tables.md)） |

只改 Table 編號的表：

| 表 | 2.0 `name` | 2.3 `name` | 內容 |
|---|---|---|---|
| `tbl_status_codes` | Table 129: Status Codes | Table 140: Status Codes | [2.0 Tables](../nfc_forum_2_0/Tables.md#tbl_status_codes)（`B2`/`B3` 只移除了行尾註解） |
| `tbl_bit_rates` | Table 132: Bit Rates | Table 143: Bit Rates | [2.0 Tables](../nfc_forum_2_0/Tables.md#tbl_bit_rates) |
| `tbl_nfcee_proto` | Table 136: NFCEE Protocols / Interfaces | Table 147: NFCEE Protocols / Interfaces | [2.0 Tables](../nfc_forum_2_0/Tables.md#tbl_nfcee_proto) |
| `tbl_mode` | Table 49: Value Field for Mode | Table 51: Value Field for Mode | [2.0 Tables](../nfc_forum_2_0/Tables.md#tbl_mode) |
| `tbl_more` | Table 51: More field values | Table 53: More field values | [2.0 Tables](../nfc_forum_2_0/Tables.md#tbl_more) |
| `tbl_L_mode_routing_entry_type` | Table 53: Listen Mode Routing Entry Types | Table 55: Listen Mode Routing Entry Types | [2.0 Tables](../nfc_forum_2_0/Tables.md#tbl_l_mode_routing_entry_type) |
| `tbl_deactivate_type` | Table 80: Deactivation Types | Table 82: Deactivation Types | [2.0 Tables](../nfc_forum_2_0/Tables.md#tbl_deactivate_type) |
| `tbl_rf_tech` | Table 130: RF Technologies | Table 141: RF Technologies | [2.0 Tables](../nfc_forum_2_0/Tables.md#tbl_rf_tech) |
| `tbl_rf_tech_mode` | Table 131: RF Technology and Mode | Table 142: RF Technology and Mode | [2.0 Tables](../nfc_forum_2_0/Tables.md#tbl_rf_tech_mode) |
| `tbl_len_rdu_val` | Table 137: Length Reduction Value | Table 148: Length Reduction Value | [2.0 Tables](../nfc_forum_2_0/Tables.md#tbl_len_rdu_val) |
| `tbl_nfcee_status` | Table 122: NFCEE_STATUS_NTF NFCEE Status | Table 132: NFCEE_STATUS_NTF NFCEE Status | [2.0 Tables](../nfc_forum_2_0/Tables.md#tbl_nfcee_status) |

其他註解層級的變更：只出現在 docstring 裡的 Table 52–60、68–76 編號都 +2，例如 `Table 54: Value Field for Technology-based Routing` 改成 `Table 56: Technology-based Routing Field Values`。2.0 原本註解掉的 `Table 119` dict 換成 docstring 形式的 `Table 129: Value Field for T3T Command Set Interface Supplementary Information`（PMm 8 / Number of Entries 1 / System Code 2n / IDm 8n），沒有對應的 dict。

---

## 3. 2.3 新增 command 詳述

<a id="rf_removal_detection_cmd"></a>
<a id="RF_REMOVAL_DETECTION_CMD"></a>
## RF_REMOVAL_DETECTION_CMD  (`21 12`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x12 / CMD |
| Handler | [`RF_Management.py:1318`](../../nci_decoder/nfc_forum_2_3_pkg/RF_Management.py#L1318) `RF_REMOVAL_DETECTION_CMD` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | WAITING_TIME | 1 | 不解析，直接印原始 hex |

### 範例
- Raw：`21 12 01 05`
- Decoder 輸出：
```text
  * WAITING_TIME: 05
[return 2 / declared 2 ]
```

### 實作備註
- WAITING_TIME 沒有換算成時間單位。程式註解是 `# p.207 有點看不懂文件`，表示作者尚未弄清楚規範的定義。

<a id="rf_removal_detection_rsp"></a>
<a id="RF_REMOVAL_DETECTION_RSP"></a>
## RF_REMOVAL_DETECTION_RSP  (`41 12`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x12 / RSP |
| Handler | [`RF_Management.py:1334`](../../nci_decoder/nfc_forum_2_3_pkg/RF_Management.py#L1334) `RF_REMOVAL_DETECTION_RSP` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [2.0 Tables](../nfc_forum_2_0/Tables.md#tbl_status_codes)，2.3 值相同）。查不到印 `RFU (xx)` |

### 範例
- Raw：`41 12 01 00`
- Decoder 輸出：
```text
  * Status: STATUS_OK
[return 2 / declared 2 ]
```

<a id="rf_removal_detection_ntf"></a>
<a id="RF_REMOVAL_DETECTION_NTF"></a>
## RF_REMOVAL_DETECTION_NTF  (`61 12`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x12 / NTF |
| Handler | [`RF_Management.py:1349`](../../nci_decoder/nfc_forum_2_3_pkg/RF_Management.py#L1349) `RF_REMOVAL_DETECTION_NTF` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [2.0 Tables](../nfc_forum_2_0/Tables.md#tbl_status_codes)）。查不到印 `RFU (xx)` |

### 範例
- Raw：`61 12 01 00`
- Decoder 輸出：
```text
  * Status: STATUS_OK
[return 2 / declared 2 ]
```

<a id="rf_wlc_status_ntf"></a>
<a id="RF_WLC_STATUS_NTF"></a>
## RF_WLC_STATUS_NTF  (`61 13`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x13 / NTF |
| Handler | [`RF_Management.py:1364`](../../nci_decoder/nfc_forum_2_3_pkg/RF_Management.py#L1364) `RF_WLC_STATUS_NTF` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | WLC Status Condition | 1 | 寫死在 if/elif 中（見下表） |
| 2 | Length of WPT duration (l₁) | 1 | 十進位長度，不印出 |
| 3 | WPT duration | l₁（0–1） | l₁ ≠ 0 才解析：先轉 8-bit 二進位，取 `[3:]`（bit 4..0，低 5 bits）轉十進位，印 `N (xx)`，不附單位 |
| 4 | Length of Transmit Power level (l₂) | 1 | 不印出 |
| 5 | Transmit Power level | l₂（0–1） | l₂ ≠ 0 才解析：`int(hex,16)` 加 `%`，印 `N% (xx)` |
| 6 | Length of Battery level (l₃) | 1 | 不印出 |
| 7 | Battery level | l₃（0–1） | l₃ ≠ 0 才解析：`int(hex,16)` 加 `%`，印 `N% (xx)` |

WLC Status Condition 對照（程式內寫死，沒有對應的 `tbl_*`）：

| 值 (hex) | 意義 |
|---|---|
| 00 | Static WPT mode Start |
| 01 | Negotiated WPT mode Start |
| 02 | Communication phase start |
| 03 | NEGO wait error |
| 04 | NEGO wait – timer started |
| 05 | Charging phase start |
| 06 | Stop Pattern detected |
| 07 | FO detected |
| 08 | Unspecified error |
| 09 | Remote NFC Endpoint non-responsive |
| 0A-7F | RFU（印 `RFU (xx)`） |
| 80-FF | Proprietary（印 `Proprietary (xx)`） |

### 範例
- Raw：`61 13 07 05 01 E3 01 32 01 5A`
- Decoder 輸出：
```text
  * WLC Status Condition: Charging phase start
  * WPT duration: 3 (E3)
  * Tx Power level:: 50% (32)
  * Battery level:: 90% (5A)
[return 14 / declared 14 ]
```
- Raw（三個長度皆為 0）：`61 13 04 09 00 00 00`
- Decoder 輸出：
```text
  * WLC Status Condition: Remote NFC Endpoint non-responsive
[return 8 / declared 8 ]
```
- Raw（Proprietary 狀態）：`61 13 04 85 00 00 00`
- Decoder 輸出：
```text
  * WLC Status Condition: Proprietary (85)
[return 8 / declared 8 ]
```

### 實作備註
- `Tx Power level::`、`Battery level::` 標籤多了一個冒號（程式字串原文）。
- WPT duration 固定取 `zfill(8)` 後的 `[3:]`，只有長度為 1 時才是「低 5 bits」。bit 7..5 被丟棄、沒有解析，長度 > 1 時結果沒有意義。
- 三個「Length」欄位都必須存在。payload 若在 Status 之後就結束（例如 `61 13 01 09`），`int('',16)` 會丟 `ValueError`（已實測）。

<a id="get_wlcp_info_param_cmd"></a>
<a id="GET_WLCP_INFO_PARAM_CMD"></a>
## GET_WLCP_INFO_PARAM_CMD  (`21 14`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x14 / CMD |
| Handler | [`RF_Management.py:1434`](../../nci_decoder/nfc_forum_2_3_pkg/RF_Management.py#L1434) `GET_WLCP_INFO_PARAM_CMD` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Number of Parameters (n) | 1 | 十進位 |
| 2 | Parameter ID [0..n-1] | 1 × n | 每個 ID 查 `tbl_wlc_poll_tlv`（見 [本文件](#tbl_wlc_poll_tlv)）。查不到印 `RFU (xx)` |

### 範例
- Raw：`21 14 05 04 00 01 02 03`
- Decoder 輸出：
```text
  * Number of Params: 4
  * Param ID:
    * ID 0: P_TX
    * ID 1: CUR_POWER_STEP
    * ID 2: NEXT_MIN_STEP_INC
    * ID 3: NEXT_MIN_STEP_DEC
[return 10 / declared 10 ]
```
- Raw（Proprietary / RFU ID）：`21 14 03 02 80 04`
- Decoder 輸出：
```text
  * Number of Params: 2
  * Param ID:
    * ID 0: RFU (80)
    * ID 1: RFU (04)
[return 6 / declared 6 ]
```

### 實作備註
- `tbl_wlc_poll_tlv` 的 `'04-7F'`、`'80-FF'` 是 range key，但程式直接 `.get(id)`、沒有用 `range_lookup.find_range_key`，所以 0x80–0xFF 印成 `RFU (xx)`，不是表中的 `Proprietary`（見上面第二個範例）。
- `__ctrl__.py` OID `14` 的 `"NTF"` 被註解掉，`GET_WLCP_INFO_PARAM_NTF` 函式也不存在。

<a id="get_wlcp_info_param_rsp"></a>
<a id="GET_WLCP_INFO_PARAM_RSP"></a>
## GET_WLCP_INFO_PARAM_RSP  (`41 14`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x14 / RSP |
| Handler | [`RF_Management.py:1458`](../../nci_decoder/nfc_forum_2_3_pkg/RF_Management.py#L1458) `GET_WLCP_INFO_PARAM_RSP` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [2.0 Tables](../nfc_forum_2_0/Tables.md#tbl_status_codes)） |
| 2 | Number of Parameters (n) | 1 | 十進位 |
| 3 | Parameter [1..n] | (m+2) × n | TLV，每筆印 `~ [Param_i] ~` |
| ﹂ | ID (Type) | 1 | `tbl_wlc_poll_tlv`（見 [本文件](#tbl_wlc_poll_tlv)）。查不到印 `RFU (xx)` |
| ﹂ | Len (m) | 1 | 十進位 |
| ﹂ | Val | m | m ≠ 0 才印原始 hex，不依 ID 解析 |

### 範例
- Raw：`41 14 08 00 02 00 01 05 01 01 32`
- Decoder 輸出：
```text
  * Status: STATUS_OK
  * Number of Params: 2
   ~ [Param_0] ~  
    * ID: P_TX
    * Len: 1
    * Val: 05
   ~ [Param_1] ~  
    * ID: CUR_POWER_STEP
    * Len: 1
    * Val: 32
[return 16 / declared 16 ]
```
- Raw（失敗、無參數）：`41 14 02 03 00`
- Decoder 輸出：
```text
  * Status: STATUS_FAILED
  * Number of Params: 0
[return 4 / declared 4 ]
```

### 實作備註
- Val 一律印原始 hex，P_TX、CUR_POWER_STEP 等都沒有換算。
- 0x80–0xFF 的 ID 同樣印成 `RFU (xx)`，原因同 GET_WLCP_INFO_PARAM_CMD。

<a id="wpt_start_cmd"></a>
<a id="WPT_START_CMD"></a>
## WPT_START_CMD  (`21 15`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x15 / CMD |
| Handler | [`RF_Management.py:1500`](../../nci_decoder/nfc_forum_2_3_pkg/RF_Management.py#L1500) `WPT_START_CMD` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Number of Parameters (n) | 1 | 十進位 |
| 2 | Parameter [1..n] | (m+2) × n | TLV，每筆印 `~ [Param_i] ~` |
| ﹂ | ID (Type) | 1 | `tbl_wpt_start_cmd_tlv`（見 [本文件](#tbl_wpt_start_cmd_tlv)）。查不到印 `RFU (xx)` |
| ﹂ | Len (m) | 1 | 十進位 |
| ﹂ | Val | m | m ≠ 0 才印原始 hex |

### 範例
- Raw：`21 15 07 02 00 01 01 01 01 14`
- Decoder 輸出：
```text
  * Number of Params: 2
   ~ [Param_0] ~  
    * ID: POWER_ADJ_REQ
    * Len: 1
    * Val: 01
   ~ [Param_1] ~  
    * ID: WPT_TIME_INT
    * Len: 1
    * Val: 14
[return 14 / declared 14 ]
```
- Raw（Proprietary ID）：`21 15 04 01 81 01 AA`
- Decoder 輸出：
```text
  * Number of Params: 1
   ~ [Param_0] ~  
    * ID: RFU (81)
    * Len: 1
    * Val: AA
[return 8 / declared 8 ]
```

### 實作備註
- POWER_ADJ_REQ、WPT_TIME_INT 的 Val 沒有解析。
- `'02-7F'`/`'80-FF'` range key 沒有用 `find_range_key` 處理，0x80–0xFF 印成 `RFU (xx)`。

<a id="wpt_start_rsp"></a>
<a id="WPT_START_RSP"></a>
## WPT_START_RSP  (`41 15`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x15 / RSP |
| Handler | [`RF_Management.py:1538`](../../nci_decoder/nfc_forum_2_3_pkg/RF_Management.py#L1538) `WPT_START_RSP` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | Status | 1 | `tbl_status_codes`（見 [2.0 Tables](../nfc_forum_2_0/Tables.md#tbl_status_codes)） |

### 範例
- Raw：`41 15 01 00`
- Decoder 輸出：
```text
  * Status: STATUS_OK
[return 2 / declared 2 ]
```

<a id="wpt_start_ntf"></a>
<a id="WPT_START_NTF"></a>
## WPT_START_NTF  (`61 15`)

| 項目 | 值 |
|---|---|
| GID / OID / MT | RF Management / 0x15 / NTF |
| Handler | [`RF_Management.py:1553`](../../nci_decoder/nfc_forum_2_3_pkg/RF_Management.py#L1553) `WPT_START_NTF` |

### Payload 格式
| # | 欄位 | 長度 (Octets) | 解析方式 / 對照表 |
|---|---|---|---|
| 1 | WPT End Condition | 1 | 寫死在 if/elif 中（見下表） |

| 值 (hex) | 意義 |
|---|---|
| 00 | Time completed |
| 01 | FOD |
| 02 | Stop Pattern |
| 03 | Unspecified error |
| 04-7F | RFU（印 `RFU (xx)`） |
| 80-FF | Proprietary（印 `Proprietary (xx)`） |

### 範例
- Raw：`61 15 01 00`
- Decoder 輸出：
```text
  * WLC Status Condition: Time completed
[return 2 / declared 2 ]
```
- Raw：`61 15 01 85`
- Decoder 輸出：
```text
  * WLC Status Condition: Proprietary (85)
[return 2 / declared 2 ]
```

### 實作備註
- docstring 的欄位名稱是 `WPT End Condition`，但輸出標籤寫成 `WLC Status Condition`（沿用 RF_WLC_STATUS_NTF 的字串）。

---

## 4. 修改過的既有 handler：新增功能的實測輸出

以下輸出用來佐證第 2.4 節描述的 2.3 新行為（同樣以直接 import 方式執行）。

`CORE_RESET_NTF`：NCI Version 改用 nibble 解析
```text
### raw=60 00 05 02 01 23 00 00
  * Rest Trigger: CORE_RESET_CMD
  * Config Status: Reset Config
  * NCI Version: 2.3 (23)
  * Manufacturer ID: Info is not available.
  * Manufacturer Specific Info: 
[return 10 / declared 10 ]
```

`CORE_INIT_RSP`：新增 Removal Detection bit；Max Routing Table Size 以 big-endian 轉十進位（`FF 00` 印成 65280）
```text
### raw=40 00 10 00 20 00 00 00 01 FF 00 FF 01 01 00 01 01 02 00
  * Status: STATUS_OK
  * NFCC Features: 20000000
    * octet0: 00100000
     ~ Removal Detection in Poll Mode:  Support
     ~ Active Communication Mode:       Not support
     ~ HCI Network Support:             Not implement
     ~ Discovery Cfg Mode:              The DH is the only entity that configs the NFCC.
     ~ Discovery Freq Cfg:              Ignored in RF_DISCOVER_CMD
    * octet1: 00000000
     ~ Forced NFCEE routing:            Not support
     ~ APDU Pattern based routing:      Not support
     ~ System Code based routing:       Not support
     ~ AID based routing:               Not support
     ~ Protocol based routing:          Not support
     ~ Technology based routing:        Not support
    * octet2: 00000000
     ~ RF Cfg in Switched Off State:    Not support
     ~ Switched On Substates:           Not support
     ~ Switched Off State:              Not support
     ~ Battery Off State:               Not support
    * octet3: 00000000
     ~ Octet_3 is reserved for proprietary capabilities
  * Max Logical Connections: 1
  * Max Routing Table Size: 65280
  * Max Control Packet Payload Size: 255
  * Max Data Packet Payload Size of the Static HCI Connection: 1
  * Number of Credits of the Static HCI Connection: 1
  * Max NFC-V RF Frame Size: 1
  * Number of Supported RF Interfaces: 1
  * Supported RF Interface: 0200
   ~ [RF_IF_0] ~  
    * Interface: ISO-DEP
    * Number of Extensions: 0
[return 32 / declared 32 ]
```

`CORE_SET_CONFIG_CMD`：新增的 WLC 設定參數
```text
### raw=20 02 0D 04 86 01 01 69 01 0A 6A 01 14 6B 01 1F
  * Number of Params: 4
   ~ [Param_0] ~  
    * ID: RF_WLC_STATUS_CONFIG
    * Len: 1
    * Val: 01
     ~ The NFCC is allowed to send RF_WLC_STATUS_NTF Notifications to the DH.
   ~ [Param_1] ~  
    * ID: WLC-P_CAP_POWER_CLASS
    * Len: 1
    * Val: 00001010 (0A)
   ~ [Param_2] ~  
    * ID: TOT_POWER_STEPS
    * Len: 1
    * Val: 20 step (14)
   ~ [Param_3] ~  
    * ID: WLC_AUTO_CAPABILITIES
    * Len: 1
    * Val: 31 step (1F)
     ~ NFCC as Wireless Charging Poller supports the WLC protocol for T5T.
     ~ NFCC as Wireless Charging Poller supports the WLC protocol for T4BT.
     ~ NFCC as Wireless Charging Poller supports the WLC protocol for T4AT.
     ~ NFCC as Wireless Charging Poller supports the WLC protocol for T3T.
     ~ NFCC as Wireless Charging Poller supports the WLC protocol for T2T.
[return 26 / declared 26 ]
```
備註：`6B` WLC_AUTO_CAPABILITIES 是 bit field，但程式仍印 `31 step`（沿用 `6A` 的字串）。`69` 只印出二進位，沒有逐 bit 解釋。

`RF_DEACTIVATE_NTF`：2.3 新的 Deactivation Reason
```text
### raw=61 06 02 03 05
  * Deactivation Type: Discovery
  * Deactivation Reason: RF_REMOTE_ENDPOINT_REMOVED
[return 4 / declared 4 ]
```

先前實測會丟例外的既有 handler（詳見 2.4 節），已於 2026-10 全數修正：

- ✅ 已修正（2026-10）：`RF_SET_LISTEN_MODE_ROUTING_CMD`（SC-based / APDU-based entry，`21 01 08 00 01 03 04 01 3B FE FE` 原本 → `TypeError`）：`(x-2)/2` 改為整數除法。
- ✅ 已修正（2026-10）：`RF_SET_FORCED_NFCEE_ROUTING_CMD`（`21 11 03 01 80 3B` 原本 → `UnboundLocalError 'val_payload'`）：改為前進 `p_payload`。
- ✅ 已修正（2026-10）：`RF_DISCOVER_NTF` / `RF_INTF_ACTIVATED_NTF` 經 `RF_TECH_SPEC_PARA`（F_PASSIVE_LISTEN / ACTIVE_POLL / ACTIVE_LISTEN，`61 03 06 01 03 82 01 00 02` 原本 → `UnboundLocalError 'p_payload'`）：改用 `para_payload`。
- ✅ 已修正（2026-10）：`RF_NFCEE_ACTION_NTF` Trigger `04`（原本 `n/2` float 切片 → `TypeError`）：改以 `2*(n//2)` 切開 Reference data / Mask。

以上只修正了會丟例外的問題；套件**仍未接上 dispatch**（見第 1 節），2.0 在本輪的其他修正（範圍 key 查表、以宣告長度為界解析等）也尚未同步到 2.3。

---

## 5. 2.3 新增／修改的對照表

標註欄：**新增**＝2.0 沒有此值；**修改**＝值相同但文字改變（括號內是 2.0 原文）；**移除**＝2.0 有、2.3 沒有的 key。

<a id="tbl_wlc_poll_tlv"></a>
## tbl_wlc_poll_tlv

**新增表**。NCI 2.3 Table 121：TLV Coding for WLC Poll Parameter ID。使用者：[GET_WLCP_INFO_PARAM_CMD](#get_wlcp_info_param_cmd)、[GET_WLCP_INFO_PARAM_RSP](#get_wlcp_info_param_rsp)。

| 值 (hex) | 意義 |
|---|---|
| 00 | P_TX |
| 01 | CUR_POWER_STEP |
| 02 | NEXT_MIN_STEP_INC |
| 03 | NEXT_MIN_STEP_DEC |
| 04-7F | RFU |
| 80-FF | Proprietary |

<a id="tbl_wpt_start_cmd_tlv"></a>
## tbl_wpt_start_cmd_tlv

**新增表**。NCI 2.3 Table 123：TLV Coding for WPT_START_CMD Parameter ID。使用者：[WPT_START_CMD](#wpt_start_cmd)。

| 值 (hex) | 意義 |
|---|---|
| 00 | POWER_ADJ_REQ |
| 01 | WPT_TIME_INT |
| 02-7F | RFU |
| 80-FF | Proprietary |

<a id="tbl_rf_proto"></a>
## tbl_rf_proto

Table 144: RF Protocols（2.0 為 Table 133）。使用者：`CORE_CONN_CREATE_CMD`、`LISTEN_MODE_ROUTING_INFO`、`RF_DISCOVER_MAP_CMD`、`RF_DISCOVER_NTF`、`RF_DISCOVER_SELECT_CMD`、`RF_INTF_ACTIVATED_NTF`、`RF_NFCEE_ACTION_NTF`、`RF_NFCEE_DISCOVERY_REQ_NTF`。

| 值 (hex) | 意義 | 標註 |
|---|---|---|
| 00 | UNDETERMINED | |
| 01 | T1T (Deprecated) | 修改（`T1T`） |
| 02 | T2T | |
| 03 | T3T | |
| 04 | ISO-DEP | |
| 05 | NFC-DEP | |
| 06 | T5T | |
| 07 | NDEF | |
| 08 | WLC | 新增 |
| 80-FE | For proprietary use | |

<a id="tbl_rf_if"></a>
## tbl_rf_if

Table 145: RF Interfaces（2.0 為 Table 134）。使用者：`CORE_INIT_RSP`、`RF_DISCOVER_MAP_CMD`、`RF_DISCOVER_SELECT_CMD`、`RF_INTF_ACTIVATED_NTF`。

| 值 (hex) | 意義 | 標註 |
|---|---|---|
| 00 | NFCEE Direct | |
| 01 | Frame | |
| 02 | ISO-DEP | |
| 03 | NFC-DEP | |
| 06 | NDEF | |
| 07 | WLC-P Autonomous | 新增 |
| 80-FE | For proprietary use | |

<a id="tbl_rf_if_exten"></a>
## tbl_rf_if_exten

Table 146: RF Interface Extensions（2.0 為 Table 135）。使用者：`CORE_INIT_RSP`、`RF_INTF_EXT_START_CMD`、`RF_INTF_EXT_STOP_CMD`。

| 值 (hex) | 意義 | 標註 |
|---|---|---|
| 00 | Frame Aggregated RF Interface Extension | |
| 01 | LLCP Symmetry RF Interface Extension | |
| 02 | WLC-P Non-Autonomous RF Interface Extension | 新增 |
| 03 | WLC-P Semi-Autonomous RF Interface Extension | 新增 |

<a id="tbl_nci_ver"></a>
## tbl_nci_ver

Table 6: NCI Version。程式註解為 `# 用不太到的 tbl`。2.3 中**沒有任何 handler 使用**（`CORE_RESET_NTF` 已改成 nibble 解析）。

| 值 (hex) | 意義 | 標註 |
|---|---|---|
| 10 | 1.0 | |
| 11 | 1.1 | |
| 20 | 2.0 | |
| 21 | 2.1 | 新增 |
| 22 | 2.2 | 新增 |
| 23 | 2.3 | 新增 |

<a id="tbl_nfcc_feat_oct2"></a>
## tbl_nfcc_feat_oct2

Table 10: NFCC Features（Octet 2，key 是 bit 位置，型別為 int）。使用者：`CORE_INIT_RSP`。

| bit | 意義 | 標註 |
|---|---|---|
| 3 | RF Cfg in Switched Off State | |
| 2 | Switched On Substates | 修改（`Switched On Sub-Mode States`） |
| 1 | Switched Off State | |
| 0 | Battery Off State | |

<a id="tbl_nfcee_id"></a>
## tbl_nfcee_id

Table 126: NFCEE IDs（2.0 為 Table 116）。使用者：`LISTEN_MODE_ROUTING_INFO`、`NFCEE_DISCOVER_NTF`、`NFCEE_MODE_SET_CMD`、`NFCEE_POWER_AND_LINK_CNTRL_CMD`、`NFCEE_STATUS_NTF`、`RF_NFCEE_ACTION_NTF`、`RF_NFCEE_DISCOVERY_REQ_NTF`、`RF_SET_FORCED_NFCEE_ROUTING_CMD`（range key 由各 handler 手寫 if/elif 收斂）。

| 值 (hex) | 意義 | 標註 |
|---|---|---|
| 00 | DH-NFCEE | |
| 01 | HCI-NTWK-NFCEE (RFU) | |
| 02-0F | Reserved for further static IDs | 修改（`(Static IDs)`） |
| 10-7F | NFCEE | 修改（`(NFCEE)`） |
| 80-FE | HCI-NFCEE | 修改（`(HCI-NFCEE)`） |
| FF | RFU | 修改（`(RFU)`） |

<a id="tbl_d_spec_type"></a>
## tbl_d_spec_type

Table 16: Destination-specific Parameters。使用者：`CORE_CONN_CREATE_CMD`。

| 值 (hex) | 意義 | 標註 |
|---|---|---|
| 00 | RF Discovery ID + RF Protocol | |
| 01 | NFCEE ID + NFCEE Interface / Protocol value | 修改（`NFCEE ID + NFCEE Interface Protocol`） |

<a id="tbl_cfg_para"></a>
## tbl_cfg_para

Table 149: Configuration Parameter Tags（2.0 為 Table 138）。使用者：`CORE_SET_CONFIG_CMD`、`CORE_SET_CONFIG_RSP`、`CORE_GET_CONFIG_CMD`、`CORE_GET_CONFIG_RSP`。以下依 dict 原始順序列出（`50`/`54` 在原始碼中位於 `55` 之後）。

| 值 (hex) | 意義 | 標註 |
|---|---|---|
| 00 | TOTAL_DURATION | |
| 01 | RFU | |
| 02 | CON_DISCOVERY_PARAM | |
| 03 | POWER_STATE | |
| 04-07 | RFU | |
| 08 | PA_BAIL_OUT | |
| 09 | PA_DEVICES_LIMIT | |
| 0A-0F | RFU | |
| 10 | PB_AFI | |
| 11 | PB_BAIL_OUT | |
| 12 | PB_ATTRIB_PARAM1 | |
| 13 | PB_SENSB_REQ_PARAM | |
| 14 | PB_DEVICES_LIMIT | |
| 15-17 | RFU | |
| 18 | PF_BIT_RATE | |
| 19 | PF_BAIL_OUT | |
| 1A | PF_DEVICES_LIMIT | |
| 1B-1F | RFU | |
| 20 | PI_B_H_INFO | |
| 21 | PI_BIT_RATE | |
| 22-27 | RFU | |
| 28 | PN_NFC_DEP_PSL | |
| 29 | PN_ATR_REQ_GEN_BYTES | |
| 2A | PN_ATR_REQ_CONFIG | |
| 2B-2E | RFU | |
| 2F | PV_DEVICES_LIMIT | |
| 30 | LA_BIT_FRAME_SDD | |
| 31 | LA_PLATFORM_CONFIG | |
| 32 | LA_SEL_INFO | |
| 33 | LA_NFCID1 | |
| 34-37 | RFU | |
| 38 | LB_SENSB_INFO | |
| 39 | LB_NFCID0 | |
| 3A | LB_APPLICATION_DATA | |
| 3B | LB_SFGI | |
| 3C | LB_FWI_ADC_FO | |
| 3D | RFU | |
| 3E | LB_BIT_RATE | |
| 3F | RFU | |
| 40 | LF_T3T_IDENTIFIERS_1 | |
| 41 | LF_T3T_IDENTIFIERS_2 | |
| 42 | LF_T3T_IDENTIFIERS_3 | |
| 43 | LF_T3T_IDENTIFIERS_4 | |
| 44 | LF_T3T_IDENTIFIERS_5 | |
| 45 | LF_T3T_IDENTIFIERS_6 | |
| 46 | LF_T3T_IDENTIFIERS_7 | |
| 47 | LF_T3T_IDENTIFIERS_8 | |
| 48 | LF_T3T_IDENTIFIERS_9 | |
| 49 | LF_T3T_IDENTIFIERS_10 | |
| 4A | LF_T3T_IDENTIFIERS_11 | |
| 4B | LF_T3T_IDENTIFIERS_12 | |
| 4C | LF_T3T_IDENTIFIERS_13 | |
| 4D | LF_T3T_IDENTIFIERS_14 | |
| 4E | LF_T3T_IDENTIFIERS_15 | |
| 4F | LF_T3T_IDENTIFIERS_16 | |
| 51 | RFU | |
| 52 | LF_T3T_MAX | |
| 53 | LF_T3T_FLAGS | |
| 55 | LF_T3T_RD_ALLOWED | |
| 50 | LF_PROTOCOL_TYPE | |
| 54 | RFU | |
| 56-57 | RFU | |
| 58 | LI_A_RATS_TB1 | |
| 59 | LI_A_HIST_BY | |
| 5A | LI_B_H_INFO_RESP | |
| 5B | LI_A_BIT_RATE | |
| 5C | LI_A_RATS_TC1 | |
| 5D-5F | RFU | |
| 60 | LN_WT | |
| 61 | LN_ATR_RES_GEN_BYTES | |
| 62 | LN_ATR_RES_CONFIG | |
| 63-67 | RFU | |
| 68 | PACM_BIT_RATE | |
| 69 | WLC-P_CAP_POWER_CLASS | 新增（POLL WLC-P–WLC Parameters） |
| 6A | TOT_POWER_STEPS | 新增 |
| 6B | WLC_AUTO_CAPABILITIES | 新增 |
| 6C-7F | RFU | 新增（取代 2.0 的 `69-7F`） |
| 80 | RF_FIELD_INFO | |
| 81 | RF_NFCEE_ACTION | |
| 82 | NFCDEP_OP | |
| 83 | LLCP_VERSION | |
| 84 | RFU | |
| 85 | NFCC_CONFIG_CONTROL | |
| 86 | RF_WLC_STATUS_CONFIG | 新增 |
| 87-9F | RFU | 新增（取代 2.0 的 `86-9F`） |
| A0-FE | Reserved | |
| FF | RFU | |
| ~~69-7F~~ | RFU | 移除 |
| ~~86-9F~~ | RFU | 移除 |

<a id="tbl_pwr_state"></a>
## tbl_pwr_state

Table 61: Power State Field Values（2.0 為 Table 59: Value Field for Power State）。key 是 bit 位置（int），bit 7–6 為 RFU（已註解）。使用者：`LISTEN_MODE_ROUTING_INFO`、`NFCEE_DISCOVER_NTF`、`RF_SET_FORCED_NFCEE_ROUTING_CMD`。

| bit | 意義 | 標註 |
|---|---|---|
| 5 | Switched On Sub-State 3 | 修改（`Screen Off lock (Sub-State 3)`） |
| 4 | Switched On Sub-State 2 | 修改（`Screen On lock (Sub-State 2)`） |
| 3 | Switched On Sub-State 1 | 修改（`Screen off unlock (Sub-State 1)`） |
| 2 | Battery Off State | |
| 1 | Switched Off State | 修改（`Switch Off State`） |
| 0 | Switched On State | 修改（`Switch On State`） |

<a id="tbl_rf_dis_id"></a>
## tbl_rf_dis_id

Table 69: RF Discovery ID（2.0 為 Table 67）。使用者：`CORE_CONN_CREATE_CMD`、`RF_DISCOVER_NTF`、`RF_DISCOVER_SELECT_CMD`、`RF_INTF_ACTIVATED_NTF`（`.get(v, v)`，range key 不會命中）。

| 值 (hex) | 意義 | 標註 |
|---|---|---|
| 00 | RFU | |
| 01-FE | Dynamically assigned by the NFCC | 新增（取代 2.0 的 `01-FF`） |
| FF | RFU | |
| ~~01-FF~~ | Dynamically assigned by the NFCC | 移除 |

<a id="tbl_deactivate_reason"></a>
## tbl_deactivate_reason

Table 83: Deactivation Reasons（2.0 為 Table 81）。使用者：`RF_DEACTIVATE_NTF`。

| 值 (hex) | 意義 | 標註 |
|---|---|---|
| 00 | DH_Request | |
| 01 | Endpoint_Request | |
| 02 | RF_Link_Loss | |
| 03 | NFC-B_Bad_AFI | |
| 04 | DH request failed due to error | |
| 05 | RF_REMOTE_ENDPOINT_REMOVED | 新增 |
| 06 | RF_TIMEOUT_EXCEPTION | 新增 |
| 07 | RF_PROTOCOL_EXCEPTION | 新增 |
| 08 | RF_FO_DETECTED | 新增 |
| 05-FF | RFU | （未隨新增值改成 `09-FF`。直接 `.get` 查表不會命中，實際上不影響輸出） |

<a id="tbl_nfcee_disc_req_type"></a>
## tbl_nfcee_disc_req_type

Table 85: TLV Coding for RF Discovery Request from NFCEE。使用者：`RF_NFCEE_DISCOVERY_REQ_NTF`。

| 值 (hex) | 意義 | 標註 |
|---|---|---|
| 00 | Added | 修改（`Added to list`） |
| 01 | Removed | 修改（`Removed from list`） |
| 02-7F | RFU | |
| 80-FF | For proprietary use | |

<a id="tbl_nfcee_ntf_trig"></a>
## tbl_nfcee_ntf_trig

Table 88: Trigger in NFCEE Action Notification。使用者：`RF_NFCEE_ACTION_NTF`。

| 值 (hex) | 意義 | 標註 |
|---|---|---|
| 00 | [ISO/IEC_7816-4] SELECT command with an AID | |
| 01 | Protocol-based route selection process (ref to Table 144) | 修改（`Protocol-based Route Selection Process (ref to Table 133)`） |
| 02 | Technology-based route selection process (ref to Table 141) | 修改（`Technology-based Route Selection Process (ref to Table 130)`） |
| 03 | System Code-based route selection process | 修改（`System Code-based Route Selection Process`） |
| 04 | TAPDU Pattern-based route selection process (as defined in Table 60) | 修改（`TAPDU Pattern-based Route Selection Process (as defined in Table 58)`） |
| 05 | Forced NFCEE Routing is used (See Table 141) | 修改（`Forced NFCEE Routing is used (See Table 130)`） |
| 06-0F | RFU | |
| 10-7F | Application specific | |
| 80-FF | RFU | |

<a id="tbl_rf_commu_para_id"></a>
## tbl_rf_commu_para_id

Table 93: TLV Coding for RF Communication Parameter ID（2.0 為 Table 91）。使用者：`RF_PARAMETER_UPDATE_CMD`、`RF_PARAMETER_UPDATE_RSP`。

| 值 (hex) | 意義 | 標註 |
|---|---|---|
| 00 | RF Technology and Mode (coded as defined in Table 142) | 修改（`... Table 131)`） |
| 01 | Transmit Bit Rate (coded as defined in Table 143) | 修改（`... Table 132)`） |
| 02 | Receive Bit Rate (coded as defined in Table 143) | 修改（`... Table 131)`，2.0 原本就引用錯表） |
| 03 | NFC-B Data Exchange Configuration (coded as defined in Table 94) | 修改（`... Table 92)`） |
| 80-FF | Proprietary | |

<a id="tbl_tlv_type"></a>
## tbl_tlv_type

Table 128: TLV Coding for NFCEE Discovery（2.0 為 Table 118）。使用者：`NFCEE_DISCOVER_NTF`。

| 值 (hex) | 意義 | 標註 |
|---|---|---|
| 00 | Hardware / Registration Identification (len = n) | 修改（`Hardware / Registration Identification`） |
| 01 | ATR Bytes (len = n) | 修改（`ATR Bytes`） |
| 02 | T3T Command Set Interface Supplementary Information (len = 9~169) | 修改（`T3T Command Set Interface Supplementary Information`） |
| 03 | Host ID in the HCI Network (len = 1) | 修改（`Host ID in the HCI Network`） |
| 04 | Support NDEF storage (len = 6) | 修改（`NDEF`） |
| 05-9F | RFU | |
| A0-FF | For proprietary use | |
