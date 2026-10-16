# nfc_forum_2_0_pkg 對照表（Tables）

本文件完整列出 `nci_decoder/nfc_forum_2_0_pkg/__table__.py` 中所有 `tbl_*` 對照表（共 34 張），以及 `Decoder_Main.py` 內的 `tbl_mt_val`、`tbl_gid_val`。內容以程式碼為準；spec Table 編號取自程式中的 `'name'` 欄位或註解，頁碼參考 `NCI_ref/NCI_commands_table_ref.md`（無頁碼者表示該文件未記錄）。

「使用的 handler」以 grep `NFC_table.tbl_xxx` 搜尋 `nfc_forum_2_0_pkg` 下的 `NCI_Core.py`、`RF_Management.py`、`NFCEE_Management.py` 取得（已排除註解行）；若使用處位於共用 helper（`LISTEN_MODE_ROUTING_INFO`、`RF_TECH_SPEC_PARA`、`VALUE_OF_CFG_PARA`），另列出呼叫該 helper 的 handler。

共通說明：

- 每張表都有一個 `'name'` key（表的說明字串），屬於 metadata，不是可查的值，以下值表中不列出（另列於各表資訊欄）。
- 查表大多為 `range_lookup.lookup(NFC_table.tbl_xxx, value)`：先精確 key，再找涵蓋該值的 `'XX-YY'` 範圍 key，皆無則 `"RFU"`，因此範圍 key 可以命中。少數呼叫端仍使用 `.get(value, <fallback>)`（例如 RF Discovery ID、NFCEE ID 的精確部分、`NFCEE_Management.py` 的 Status / NFCEE Status），此時範圍 key 只有在先呼叫 `range_lookup.find_range_key(table, int_value)` 時才會命中（各表「實作備註」逐一說明）。
- 未以 dict 實作、只寫成 docstring 結構說明的規範表（Table 52、54~58、68~76）不在本文件範圍，其解析邏輯寫在 handler 內。被註解掉的 `tbl_rst_msg`（Table 5）不生效，亦不列入（舊版 `tbl_tlv_type`（Table 119）的註解區塊已於 2026-10 刪除）。

## 總覽

| # | 表名 | Spec Table | 定義位置 | 項目數（不含 `name`） | 使用的 handler |
|---|---|---|---|---|---|
| 1 | [`tbl_status_codes`](#tbl_status_codes) | Table 129 | [`__table__.py:8`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L8) | 27 | `CORE_RESET_RSP`, `CORE_INIT_RSP`, `CORE_SET_CONFIG_RSP`, `CORE_GET_CONFIG_RSP`, `CORE_CONN_CREATE_RSP`, `CORE_CONN_CLOSE_RSP`, `CORE_GENERIC_ERROR_NTF`, `CORE_INTERFACE_ERROR_NTF`, `CORE_SET_POWER_SUB_STATE_RSP`, `RF_DISCOVER_MAP_RSP`, `RF_SET_LISTEN_MODE_ROUTING_RSP`, `RF_GET_LISTEN_MODE_ROUTING_RSP`, `RF_DISCOVER_RSP`, `RF_DISCOVER_SELECT_RSP`, `RF_DEACTIVATE_RSP`, `RF_T3T_POLLING_RSP`, `RF_T3T_POLLING_NTF`, `RF_PARAMETER_UPDATE_RSP`, `RF_INTF_EXT_START_RSP`, `RF_INTF_EXT_STOP_RSP`, `RF_EXT_AGG_ABORT_RSP`, `RF_NDEF_ABORT_RSP`, `RF_ISO_DEP_NAK_PRESENCE_RSP`, `RF_ISO_DEP_NAK_PRESENCE_NTF`, `RF_SET_FORCED_NFCEE_ROUTING_RSP`, `NFCEE_DISCOVER_RSP`, `NFCEE_MODE_SET_RSP`, `NFCEE_MODE_SET_NTF`, `NFCEE_POWER_AND_LINK_CNTRL_RSP` |
| 2 | [`tbl_bit_rates`](#tbl_bit_rates) | Table 132 | [`__table__.py:46`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L46) | 9 | `CORE_SET_CONFIG_CMD`, `CORE_GET_CONFIG_RSP`, `RF_INTF_ACTIVATED_NTF`, `RF_PARAMETER_UPDATE_CMD` |
| 3 | [`tbl_rf_proto`](#tbl_rf_proto) | Table 133 | [`__table__.py:60`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L60) | 9 | `CORE_CONN_CREATE_CMD`, `RF_DISCOVER_MAP_CMD`, `RF_SET_LISTEN_MODE_ROUTING_CMD`, `RF_GET_LISTEN_MODE_ROUTING_NTF`, `RF_DISCOVER_NTF`, `RF_DISCOVER_SELECT_CMD`, `RF_INTF_ACTIVATED_NTF`, `RF_NFCEE_ACTION_NTF`, `RF_NFCEE_DISCOVERY_REQ_NTF` |
| 4 | [`tbl_nfcee_proto`](#tbl_nfcee_proto) | Table 136 | [`__table__.py:74`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L74) | 7 | `CORE_CONN_CREATE_CMD`, `NFCEE_DISCOVER_NTF` |
| 5 | [`tbl_nfcee_id`](#tbl_nfcee_id) | Table 116 | [`__table__.py:86`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L86) | 6 | `CORE_CONN_CREATE_CMD`, `RF_SET_LISTEN_MODE_ROUTING_CMD`, `RF_GET_LISTEN_MODE_ROUTING_NTF`, `RF_NFCEE_ACTION_NTF`, `RF_NFCEE_DISCOVERY_REQ_NTF`, `RF_SET_FORCED_NFCEE_ROUTING_CMD`, `NFCEE_DISCOVER_NTF`, `NFCEE_MODE_SET_CMD`, `NFCEE_STATUS_NTF`, `NFCEE_POWER_AND_LINK_CNTRL_CMD` |
| 6 | [`tbl_rf_if`](#tbl_rf_if) | Table 134 | [`__table__.py:97`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L97) | 6 | `CORE_INIT_RSP`, `RF_DISCOVER_MAP_CMD`, `RF_DISCOVER_SELECT_CMD`, `RF_INTF_ACTIVATED_NTF` |
| 7 | [`tbl_rf_if_exten`](#tbl_rf_if_exten) | Table 135 | [`__table__.py:108`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L108) | 2 | `CORE_INIT_RSP`, `RF_INTF_EXT_START_CMD`, `RF_INTF_EXT_STOP_CMD` |
| 8 | [`tbl_conn_id`](#tbl_conn_id) | Table 4 | [`__table__.py:121`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L121) | 3 | `CORE_CONN_CREATE_RSP`, `CORE_CONN_CLOSE_CMD`, `CORE_CONN_CREDITS_NTF`, `CORE_INTERFACE_ERROR_NTF` |
| 9 | [`tbl_rst_trig`](#tbl_rst_trig) | Table 5 | [`__table__.py:134`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L134) | 3 | `CORE_RESET_NTF` |
| 10 | [`tbl_nci_ver`](#tbl_nci_ver) | Table 6 | [`__table__.py:142`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L142) | 3 | `CORE_RESET_NTF` |
| 11 | [`tbl_cfg_status`](#tbl_cfg_status) | Table 7 | [`__table__.py:150`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L150) | 2 | `CORE_RESET_CMD`, `CORE_RESET_NTF` |
| 12 | [`tbl_nfcc_feat_oct1`](#tbl_nfcc_feat_oct1) | Table 10 | [`__table__.py:157`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L157) | 6 | `CORE_INIT_RSP` |
| 13 | [`tbl_nfcc_feat_oct2`](#tbl_nfcc_feat_oct2) | Table 10 | [`__table__.py:168`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L168) | 4 | `CORE_INIT_RSP` |
| 14 | [`tbl_dest_type`](#tbl_dest_type) | Table 13 | [`__table__.py:177`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L177) | 3 | `CORE_CONN_CREATE_CMD` |
| 15 | [`tbl_init_credits`](#tbl_init_credits) | Table 15 | [`__table__.py:185`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L185) | 1 | `CORE_CONN_CREATE_RSP` |
| 16 | [`tbl_d_spec_type`](#tbl_d_spec_type) | Table 16 | [`__table__.py:191`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L191) | 2 | `CORE_CONN_CREATE_CMD` |
| 17 | [`tbl_cfg_para`](#tbl_cfg_para) | Table 138 | [`__table__.py:198`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L198) | 83 | `CORE_SET_CONFIG_CMD`, `CORE_SET_CONFIG_RSP`, `CORE_GET_CONFIG_CMD`, `CORE_GET_CONFIG_RSP` |
| 18 | [`tbl_rf_field_status`](#tbl_rf_field_status) | Table 22 | [`__table__.py:311`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L311) | 2 | `RF_FIELD_INFO_NTF` |
| 19 | [`tbl_mode`](#tbl_mode) | Table 49 | [`__table__.py:318`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L318) | 4 | `RF_DISCOVER_MAP_CMD` |
| 20 | [`tbl_more`](#tbl_more) | Table 51 | [`__table__.py:327`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L327) | 2 | `RF_SET_LISTEN_MODE_ROUTING_CMD`, `RF_GET_LISTEN_MODE_ROUTING_NTF` |
| 21 | [`tbl_L_mode_routing_entry_type`](#tbl_l_mode_routing_entry_type) | Table 53 | [`__table__.py:344`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L344) | 5 | `RF_SET_LISTEN_MODE_ROUTING_CMD`, `RF_GET_LISTEN_MODE_ROUTING_NTF` |
| 22 | [`tbl_pwr_state`](#tbl_pwr_state) | Table 59 | [`__table__.py:400`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L400) | 6 | `RF_SET_LISTEN_MODE_ROUTING_CMD`, `RF_GET_LISTEN_MODE_ROUTING_NTF`, `RF_SET_FORCED_NFCEE_ROUTING_CMD`, `NFCEE_DISCOVER_NTF` |
| 23 | [`tbl_rf_dis_id`](#tbl_rf_dis_id) | Table 67 | [`__table__.py:413`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L413) | 3 | `CORE_CONN_CREATE_CMD`, `RF_DISCOVER_NTF`, `RF_DISCOVER_SELECT_CMD`, `RF_INTF_ACTIVATED_NTF` |
| 24 | [`tbl_deactivate_type`](#tbl_deactivate_type) | Table 80 | [`__table__.py:498`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L498) | 5 | `RF_DEACTIVATE_CMD`, `RF_DEACTIVATE_NTF` |
| 25 | [`tbl_deactivate_reason`](#tbl_deactivate_reason) | Table 81 | [`__table__.py:508`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L508) | 6 | `RF_DEACTIVATE_NTF` |
| 26 | [`tbl_nfcee_disc_req_type`](#tbl_nfcee_disc_req_type) | Table 85 | [`__table__.py:519`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L519) | 4 | `RF_NFCEE_DISCOVERY_REQ_NTF` |
| 27 | [`tbl_nfcee_ntf_trig`](#tbl_nfcee_ntf_trig) | Table 88 | [`__table__.py:528`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L528) | 9 | `RF_NFCEE_ACTION_NTF` |
| 28 | [`tbl_rf_commu_para_id`](#tbl_rf_commu_para_id) | Table 91 | [`__table__.py:543`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L543) | 5 | `RF_PARAMETER_UPDATE_CMD`, `RF_PARAMETER_UPDATE_RSP` |
| 29 | [`tbl_rf_tech`](#tbl_rf_tech) | Table 130 | [`__table__.py:553`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L553) | 4 | `RF_SET_LISTEN_MODE_ROUTING_CMD`, `RF_GET_LISTEN_MODE_ROUTING_NTF`, `RF_NFCEE_ACTION_NTF` |
| 30 | [`tbl_rf_tech_mode`](#tbl_rf_tech_mode) | Table 131 | [`__table__.py:563`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L563) | 14 | `RF_DISCOVER_CMD`, `RF_DISCOVER_NTF`, `RF_INTF_ACTIVATED_NTF`, `RF_NFCEE_DISCOVERY_REQ_NTF`, `RF_PARAMETER_UPDATE_CMD` |
| 31 | [`tbl_len_rdu_val`](#tbl_len_rdu_val) | Table 137 | [`__table__.py:582`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L582) | 6 | `RF_INTF_ACTIVATED_NTF` |
| 32 | [`tbl_tlv_type`](#tbl_tlv_type) | Table 118 | [`__table__.py:599`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L599) | 7 | `NFCEE_DISCOVER_NTF` |
| 33 | [`tbl_nfcee_disc_status`](#tbl_nfcee_disc_status) | Table 117 | [`__table__.py:611`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L611) | 4 | `NFCEE_DISCOVER_NTF` |
| 34 | [`tbl_nfcee_status`](#tbl_nfcee_status) | Table 122 | [`__table__.py:133`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L133) | 5 | `NFCEE_STATUS_NTF` |

## Decoder_Main.py 內的表：tbl_mt_val / tbl_gid_val

這兩張表定義在 [`Decoder_Main.py`](../../nci_decoder/Decoder_Main.py#L10) 的 `NFC_NCI_DECODER()` 函式內（區域變數），不屬於任何 vendor package，所有 vendor 共用。用途是解析 3-byte header 的 Octet 0：先把第一個 byte 轉成 8-bit 二進位字串 `first_oct_b`，`first_oct_b[0:3]` 查 `tbl_mt_val` 得到 MT，`first_oct_b[3:4]` 為 PBF，`first_oct_b[4:]` 查 `tbl_gid_val` 得到 GID 群組名稱；之後以 `pkg.tbl_nci_ctrl[gid_val][oid][mt_val]`（`__ctrl__.py`）取得 handler 並以 `raw[6:]`（header 之後的 payload）呼叫。

<a id="tbl_mt_val"></a>
### tbl_mt_val

Spec：Table 2: MT Values（p.23）。定義於 [`Decoder_Main.py:10`](../../nci_decoder/Decoder_Main.py#L10)。key 為 **3-bit 二進位字串**。查表為 `tbl_mt_val.get(first_oct_b[0:3], "RFU")`。

| 值 (bin) | 對應首 byte 範圍 | 意義 |
|---|---|---|
| `000` | `0x00`~`0x1F` | DATA |
| `001` | `0x20`~`0x3F` | CMD |
| `010` | `0x40`~`0x5F` | RSP |
| `011` | `0x60`~`0x7F` | NTF |

實作備註：

- MT = DATA 且 Octet 1 高 6 bits 為 0 時走 DATA packet 分支（Conn ID / Credits 由程式硬編碼解析，不使用 `tbl_conn_id`）；其餘都當作 Control packet 進行 dispatch。
- `100`~`111` 查無時得到 `"RFU"`，接著 `tbl_nci_ctrl[...][oid]["RFU"]` 會 `KeyError`，程式印出 `<< ERROR_NOT_FOUND >>` 後重新拋出例外。

<a id="tbl_gid_val"></a>
### tbl_gid_val

Spec：Table 139（程式註解 `#table 139`；p.191）。定義於 [`Decoder_Main.py:18`](../../nci_decoder/Decoder_Main.py#L18)。key 為 **4-bit 二進位字串**。查表為 `tbl_gid_val.get(first_oct_b[4:])`（**無 fallback**，查無時為 `None`）。

| 值 (bin) | GID (hex) | 意義 | nfc_forum_2_0_pkg `__ctrl__.py` 是否有此群組 |
|---|---|---|---|
| `0000` | 0x0 | NCI Core | 有 |
| `0001` | 0x1 | RF Management | 有 |
| `0010` | 0x2 | NFCEE Management | 有 |
| `0011` | 0x3 | NFCC Management | 無 |
| `0100` | 0x4 | Test Management | 無 |
| `1111` | 0xF | Proprietary | 無 |

實作備註（vendor = `'None'` 實測）：

- GID 為 `0x3`/`0x4`/`0xF` 時 `tbl_nci_ctrl` 沒有對應群組：例如 `23 00 00` 印出 `<< ERROR_NOT_FOUND >>` 並拋出 `KeyError: 'NFCC Management'`；`2F 00 00` 拋出 `KeyError: 'Proprietary'`。
- 表中未列出的 GID（如 `0x5`）查表得 `None`，`25 00 00` 拋出 `KeyError: None`。

<a id="tbl_status_codes"></a>
## tbl_status_codes

| 項目 | 值 |
|---|---|
| Spec Table | Table 129: Status Codes（p.182） |
| 程式 `name` | `Table 129: Status Codes:` |
| 定義位置 | [`__table__.py:8`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L8)（Global Table 區段） |
| key 型別 | hex 字串（2 字元，或 `XX-YY` 範圍） |

使用的 handler：

| 檔案 | 函式 | 行號 | 經由 helper 呼叫的 handler |
|---|---|---|---|
| `NCI_Core.py` | `CORE_RESET_RSP` | [L30](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L30) | — |
| `NCI_Core.py` | `CORE_INIT_RSP` | [L118](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L118) | — |
| `NCI_Core.py` | `CORE_SET_CONFIG_RSP` | [L286](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L286) | — |
| `NCI_Core.py` | `CORE_GET_CONFIG_RSP` | [L345](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L345) | — |
| `NCI_Core.py` | `CORE_CONN_CREATE_RSP` | [L466](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L466) | — |
| `NCI_Core.py` | `CORE_CONN_CLOSE_RSP` | [L513](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L513) | — |
| `NCI_Core.py` | `CORE_GENERIC_ERROR_NTF` | [L564](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L564) | — |
| `NCI_Core.py` | `CORE_INTERFACE_ERROR_NTF` | [L581](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L581) | — |
| `NCI_Core.py` | `CORE_SET_POWER_SUB_STATE_RSP` | [L634](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L634) | — |
| `RF_Management.py` | `RF_DISCOVER_MAP_RSP` | [L56](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L56) | — |
| `RF_Management.py` | `RF_SET_LISTEN_MODE_ROUTING_RSP` | [L198](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L198) | — |
| `RF_Management.py` | `RF_GET_LISTEN_MODE_ROUTING_RSP` | [L227](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L227) | — |
| `RF_Management.py` | `RF_DISCOVER_RSP` | [L295](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L295) | — |
| `RF_Management.py` | `RF_DISCOVER_SELECT_RSP` | [L562](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L562) | — |
| `RF_Management.py` | `RF_DEACTIVATE_RSP` | [L753](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L753) | — |
| `RF_Management.py` | `RF_T3T_POLLING_RSP` | [L822](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L822) | — |
| `RF_Management.py` | `RF_T3T_POLLING_NTF` | [L842](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L842) | — |
| `RF_Management.py` | `RF_PARAMETER_UPDATE_RSP` | [L1038](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L1038) | — |
| `RF_Management.py` | `RF_INTF_EXT_START_RSP` | [L1092](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L1092) | — |
| `RF_Management.py` | `RF_INTF_EXT_STOP_RSP` | [L1135](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L1135) | — |
| `RF_Management.py` | `RF_EXT_AGG_ABORT_RSP` | [L1164](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L1164) | — |
| `RF_Management.py` | `RF_NDEF_ABORT_RSP` | [L1193](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L1193) | — |
| `RF_Management.py` | `RF_ISO_DEP_NAK_PRESENCE_RSP` | [L1222](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L1222) | — |
| `RF_Management.py` | `RF_ISO_DEP_NAK_PRESENCE_NTF` | [L1238](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L1238) | — |
| `RF_Management.py` | `RF_SET_FORCED_NFCEE_ROUTING_RSP` | [L1295](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L1295) | — |
| `NFCEE_Management.py` | `NFCEE_DISCOVER_RSP` | [L30](../../nci_decoder/nfc_forum_2_0_pkg/NFCEE_Management.py#L30) | — |
| `NFCEE_Management.py` | `NFCEE_MODE_SET_RSP` | [L190](../../nci_decoder/nfc_forum_2_0_pkg/NFCEE_Management.py#L190) | — |
| `NFCEE_Management.py` | `NFCEE_MODE_SET_NTF` | [L206](../../nci_decoder/nfc_forum_2_0_pkg/NFCEE_Management.py#L206) | — |
| `NFCEE_Management.py` | `NFCEE_POWER_AND_LINK_CNTRL_RSP` | [L275](../../nci_decoder/nfc_forum_2_0_pkg/NFCEE_Management.py#L275) | — |

| 值 (hex) | 意義 |
|---|---|
| `00` | STATUS_OK |
| `01` | STATUS_REJECTED |
| `03` | STATUS_FAILED |
| `04` | STATUS_NOT_INITIALIZED |
| `05` | STATUS_SYNTAX_ERROR |
| `06` | STATUS_SEMANTIC_ERROR |
| `09` | STATUS_INVALID_PARAM |
| `0A` | STATUS_MESSAGE_SIZE_EXCEEDED |
| `11` | STATUS_OK_1_BIT |
| `12` | STATUS_OK_2_BIT |
| `13` | STATUS_OK_3_BIT |
| `14` | STATUS_OK_4_BIT |
| `15` | STATUS_OK_5_BIT |
| `16` | STATUS_OK_6_BIT |
| `17` | STATUS_OK_7_BIT |
| `A0` | DISCOVERY_ALREADY_STARTED |
| `A1` | DISCOVERY_TARGET_ACTIVATION_FAILED |
| `A2` | DISCOVERY_TEAR_DOWN |
| `02` | RF_FRAME_CORRUPTED |
| `B0` | RF_TRANSMISSION_EXCEPTION |
| `B1` | RF_PROTOCOL_EXCEPTION |
| `B2` | RF_TIMEOUT_EXCEPTION |
| `B3` | RF_UNEXPECTED_DATA |
| `C0` | NFCEE_INTERFACE_ACTIVATION_FAILED |
| `C1` | NFCEE_TRANSMISSION_ERROR |
| `C2` | NFCEE_PROTOCOL_ERROR |
| `C3` | NFCEE_TIMEOUT_ERROR |

實作備註：

- `NCI_Core.py` / `RF_Management.py` 的呼叫端已改用 `lookup`，`NFCEE_Management.py` 仍為 `.get(status, "RFU")`；但 `0xE0`~`0xFF`（Proprietary Status Codes）只以註解出現在表中、沒有對應 key，查表結果仍為 `RFU`。
- `02 RF_FRAME_CORRUPTED` 在原始碼中放在「RF Interface Specific Status Codes」區段；`B2`、`B3` 後方有 `# 'DISCOVERY_TEAR_DOWN'` 註解，但實際值以 dict 內容為準。

<a id="tbl_bit_rates"></a>
## tbl_bit_rates

| 項目 | 值 |
|---|---|
| Spec Table | Table 132: Bit Rates（p.184） |
| 程式 `name` | `Table 132: Bit Rates:` |
| 定義位置 | [`__table__.py:46`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L46)（Global Table 區段） |
| key 型別 | hex 字串（2 字元，或 `XX-YY` 範圍） |

使用的 handler：

| 檔案 | 函式 | 行號 | 經由 helper 呼叫的 handler |
|---|---|---|---|
| `NCI_Core.py` | `VALUE_OF_CFG_PARA` | [L690](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L690) | `CORE_SET_CONFIG_CMD`, `CORE_GET_CONFIG_RSP` |
| `RF_Management.py` | `RF_INTF_ACTIVATED_NTF` | [L631](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L631), [L635](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L635) | — |
| `RF_Management.py` | `RF_PARAMETER_UPDATE_CMD` | [L1001](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L1001), [L1003](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L1003) | — |

| 值 (hex) | 意義 |
|---|---|
| `00` | 106 Kbit/s |
| `01` | 212 Kbit/s |
| `02` | 424 Kbit/s |
| `03` | 848 Kbit/s |
| `04` | 1695 Kbit/s |
| `05` | 3390 Kbit/s |
| `06` | 6780 Kbit/s |
| `20` | 26 Kbit/s |
| `80-FE` | For proprietary use |

實作備註：

- ✅ 已修正（2026-10）：`RF_INTF_ACTIVATED_NTF`、`RF_PARAMETER_UPDATE_CMD` 與 `VALUE_OF_CFG_PARA`（經 `BIT_RATE_TEXT`）都以 `lookup` 查表，`80-FE` 範圍 key 可命中。
- ✅ 已修正（2026-10）：`VALUE_OF_CFG_PARA` 改用 `BIT_RATE_TEXT`，只有 `80`~`FE` 顯示 `For proprietary use`，其他未列出值（如 `07`）顯示 `RFU`，與 RF_Management 一致。
- `VALUE_OF_CFG_PARA` 只對 `PF_BIT_RATE`(18)、`PI_BIT_RATE`(21)、`LB_BIT_RATE`(3E)、`LI_A_BIT_RATE`(5B)、`PACM_BIT_RATE`(68) 使用此表。

<a id="tbl_rf_proto"></a>
## tbl_rf_proto

| 項目 | 值 |
|---|---|
| Spec Table | Table 133: RF Protocols（p.185） |
| 程式 `name` | `Table 133: RF Protocols:` |
| 定義位置 | [`__table__.py:60`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L60)（Global Table 區段） |
| key 型別 | hex 字串（2 字元，或 `XX-YY` 範圍） |

使用的 handler：

| 檔案 | 函式 | 行號 | 經由 helper 呼叫的 handler |
|---|---|---|---|
| `NCI_Core.py` | `CORE_CONN_CREATE_CMD` | [L421](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L421) | — |
| `RF_Management.py` | `RF_DISCOVER_MAP_CMD` | [L29](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L29) | — |
| `RF_Management.py` | `LISTEN_MODE_ROUTING_INFO` | [L141](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L141), [L142](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L142) | `RF_SET_LISTEN_MODE_ROUTING_CMD`, `RF_GET_LISTEN_MODE_ROUTING_NTF` |
| `RF_Management.py` | `RF_DISCOVER_NTF` | [L496](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L496) | — |
| `RF_Management.py` | `RF_DISCOVER_SELECT_CMD` | [L542](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L542) | — |
| `RF_Management.py` | `RF_INTF_ACTIVATED_NTF` | [L598](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L598) | — |
| `RF_Management.py` | `RF_NFCEE_ACTION_NTF` | [L900](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L900) | — |
| `RF_Management.py` | `RF_NFCEE_DISCOVERY_REQ_NTF` | [L954](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L954) | — |

| 值 (hex) | 意義 |
|---|---|
| `00` | UNDETERMINED |
| `01` | T1T |
| `02` | T2T |
| `03` | T3T |
| `04` | ISO-DEP |
| `05` | NFC-DEP |
| `06` | T5T |
| `07` | NDEF |
| `80-FE` | For proprietary use |

實作備註：

- ✅ 已修正（2026-10）：所有呼叫端改用 `lookup`，`0x80`~`0xFE` 顯示 `For proprietary use`。

<a id="tbl_nfcee_proto"></a>
## tbl_nfcee_proto

| 項目 | 值 |
|---|---|
| Spec Table | Table 136: NFCEE Protocols / Interfaces（p.186） |
| 程式 `name` | `Table 136: NFCEE Protocols / Interfaces:` |
| 定義位置 | [`__table__.py:74`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L74)（Global Table 區段） |
| key 型別 | hex 字串（2 字元，或 `XX-YY` 範圍） |

使用的 handler：

| 檔案 | 函式 | 行號 | 經由 helper 呼叫的 handler |
|---|---|---|---|
| `NCI_Core.py` | `CORE_CONN_CREATE_CMD` | [L439](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L439) | — |
| `NFCEE_Management.py` | `NFCEE_DISCOVER_NTF` | [L80](../../nci_decoder/nfc_forum_2_0_pkg/NFCEE_Management.py#L80) | — |

| 值 (hex) | 意義 |
|---|---|
| `00` | APDU |
| `01` | RFU |
| `02` | Type 3 Tag Command Set |
| `03` | Transparent |
| `04-7F` | RFU |
| `80-FE` | For proprietary use |
| `FF` | RFU |

實作備註：

- ✅ 已修正（2026-10）：`CORE_CONN_CREATE_CMD`、`NFCEE_DISCOVER_NTF` 改用 `lookup`，`04-7F` 顯示 `RFU`、`80-FE` 顯示 `For proprietary use`（`62 00 06 00 00 01 80 00 00` 輸出 `For proprietary use (80)`）。

<a id="tbl_nfcee_id"></a>
## tbl_nfcee_id

| 項目 | 值 |
|---|---|
| Spec Table | Table 116: NFCEE IDs（p.155） |
| 程式 `name` | `Table 116: NFCEE IDs:` |
| 定義位置 | [`__table__.py:86`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L86)（Global Table 區段） |
| key 型別 | hex 字串（2 字元，或 `XX-YY` 範圍） |

使用的 handler：

| 檔案 | 函式 | 行號 | 經由 helper 呼叫的 handler |
|---|---|---|---|
| `NCI_Core.py` | `CORE_CONN_CREATE_CMD` | [L427](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L427) | — |
| `RF_Management.py` | `LISTEN_MODE_ROUTING_INFO` | [L111](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L111), [L112](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L112) | `RF_SET_LISTEN_MODE_ROUTING_CMD`, `RF_GET_LISTEN_MODE_ROUTING_NTF` |
| `RF_Management.py` | `RF_NFCEE_ACTION_NTF` | [L881](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L881), [L882](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L882) | — |
| `RF_Management.py` | `RF_NFCEE_DISCOVERY_REQ_NTF` | [L948](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L948), [L949](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L949) | — |
| `RF_Management.py` | `RF_SET_FORCED_NFCEE_ROUTING_CMD` | [L1264](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L1264), [L1265](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L1265) | — |
| `NFCEE_Management.py` | `NFCEE_DISCOVER_NTF` | [L60](../../nci_decoder/nfc_forum_2_0_pkg/NFCEE_Management.py#L60), [L61](../../nci_decoder/nfc_forum_2_0_pkg/NFCEE_Management.py#L61) | — |
| `NFCEE_Management.py` | `NFCEE_MODE_SET_CMD` | [L164](../../nci_decoder/nfc_forum_2_0_pkg/NFCEE_Management.py#L164), [L165](../../nci_decoder/nfc_forum_2_0_pkg/NFCEE_Management.py#L165) | — |
| `NFCEE_Management.py` | `NFCEE_STATUS_NTF` | [L223](../../nci_decoder/nfc_forum_2_0_pkg/NFCEE_Management.py#L223), [L224](../../nci_decoder/nfc_forum_2_0_pkg/NFCEE_Management.py#L224) | — |
| `NFCEE_Management.py` | `NFCEE_POWER_AND_LINK_CNTRL_CMD` | [L245](../../nci_decoder/nfc_forum_2_0_pkg/NFCEE_Management.py#L245), [L246](../../nci_decoder/nfc_forum_2_0_pkg/NFCEE_Management.py#L246) | — |

| 值 (hex) | 意義 |
|---|---|
| `00` | DH-NFCEE |
| `01` | HCI-NTWK-NFCEE (RFU) |
| `02-0F` | (Static IDs) |
| `10-7F` | (NFCEE) |
| `80-FE` | (HCI-NFCEE) |
| `FF` | (RFU) |

實作備註：

- RF_Management / NFCEE_Management 的呼叫端都同時做「精確 key 查表」與「`find_range_key` 範圍查表」，兩個結果並列輸出（查不到者為空字串）。`LISTEN_MODE_ROUTING_INFO` 的精確查表 fallback 為原始 hex 值；`RF_SET_FORCED_NFCEE_ROUTING_CMD` 也是精確 + 範圍並列。
- ✅ 已修正（2026-10）：`CORE_CONN_CREATE_CMD` 的 NFCEE ID 改用此表（`lookup`，並去掉表值外層括號，如 `HCI-NFCEE (80)`），不再以 if/elif 硬寫。

<a id="tbl_rf_if"></a>
## tbl_rf_if

| 項目 | 值 |
|---|---|
| Spec Table | Table 134: RF Interfaces（p.185） |
| 程式 `name` | `Table 134: RF Interfaces:` |
| 定義位置 | [`__table__.py:97`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L97)（Global Table 區段） |
| key 型別 | hex 字串（2 字元，或 `XX-YY` 範圍） |

使用的 handler：

| 檔案 | 函式 | 行號 | 經由 helper 呼叫的 handler |
|---|---|---|---|
| `NCI_Core.py` | `CORE_INIT_RSP` | [L215](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L215) | — |
| `RF_Management.py` | `RF_DISCOVER_MAP_CMD` | [L37](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L37) | — |
| `RF_Management.py` | `RF_DISCOVER_SELECT_CMD` | [L546](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L546) | — |
| `RF_Management.py` | `RF_INTF_ACTIVATED_NTF` | [L594](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L594), [L643](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L643) | — |

| 值 (hex) | 意義 |
|---|---|
| `00` | NFCEE Direct |
| `01` | Frame |
| `02` | ISO-DEP |
| `03` | NFC-DEP |
| `06` | NDEF |
| `80-FE` | For proprietary use |

實作備註：

- ✅ 已修正（2026-10）：所有呼叫端改用 `lookup`，`0x80`~`0xFE` 顯示 `For proprietary use`。
- ✅ 已修正（2026-10）：`RF_DISCOVER_SELECT_CMD` 印 RF Interface 時，括號內改印 `rf_if` 本身。
- ✅ 已修正（2026-10）：`RF_INTF_ACTIVATED_NTF` 改以 RF Interface 的 hex code（而非查表結果字串）判斷 Activation Parameters 的解析分支。

<a id="tbl_rf_if_exten"></a>
## tbl_rf_if_exten

| 項目 | 值 |
|---|---|
| Spec Table | Table 135: RF Interface Extensions（p.186） |
| 程式 `name` | `Table 135: RF Interface Extensions:` |
| 定義位置 | [`__table__.py:108`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L108)（Global Table 區段） |
| key 型別 | hex 字串（2 字元，或 `XX-YY` 範圍） |

使用的 handler：

| 檔案 | 函式 | 行號 | 經由 helper 呼叫的 handler |
|---|---|---|---|
| `NCI_Core.py` | `CORE_INIT_RSP` | [L221](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L221) | — |
| `RF_Management.py` | `RF_INTF_EXT_START_CMD` | [L1067](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L1067) | — |
| `RF_Management.py` | `RF_INTF_EXT_STOP_CMD` | [L1110](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L1110) | — |

| 值 (hex) | 意義 |
|---|---|
| `00` | Frame Aggregated RF Interface Extension |
| `01` | LLCP Symmetry RF Interface Extension |

實作備註：

- 精確查表，未列出的值顯示 `RFU`。

<a id="tbl_conn_id"></a>
## tbl_conn_id

| 項目 | 值 |
|---|---|
| Spec Table | Table 4: Conn ID（p.28） |
| 程式 `name` | `Table 4: Conn ID` |
| 定義位置 | [`__table__.py:121`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L121)（NCI_Core Table 區段） |
| key 型別 | 4-bit 二進位字串 |

使用的 handler：

| 檔案 | 函式 | 行號 | 經由 helper 呼叫的 handler |
|---|---|---|---|
| `NCI_Core.py` | `CORE_CONN_CREATE_RSP` | [L481](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L481) | — |
| `NCI_Core.py` | `CORE_CONN_CLOSE_CMD` | [L497](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L497) | — |
| `NCI_Core.py` | `CORE_CONN_CREDITS_NTF` | [L541](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L541) | — |
| `NCI_Core.py` | `CORE_INTERFACE_ERROR_NTF` | [L585](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L585) | — |

| 值 (bin) | 意義 |
|---|---|
| `0000` | Static: DH -- Remote NFC Endpoint |
| `0001` | Static: DH -- HCI Network |
| `0010-1111` | Dynamically assigned |

實作備註：

- key 為 **4-bit 二進位字串**（非 hex）。呼叫端把 Conn ID byte 轉成 8-bit 二進位後取低 4 bits 查表；`0010-1111` 這個 key 不會被 `.get` 命中，實際由 fallback 字串 `"Dynamically assigned by the NFCC"` 呈現。
- DATA packet 的 Conn ID 由 `Decoder_Main.py` 以 if/else 硬編碼處理，不使用此表。

<a id="tbl_rst_trig"></a>
## tbl_rst_trig

| 項目 | 值 |
|---|---|
| Spec Table | Table 5: Control Messages to Reset the NFCC（其中 CORE_RESET_NTF 的 Reset Trigger 欄位）（p.29） |
| 程式 `name` | `Table 5: Control Messages to Reset the NFCC:` |
| 定義位置 | [`__table__.py:134`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L134)（NCI_Core Table 區段） |
| key 型別 | hex 字串（2 字元，或 `XX-YY` 範圍） |

使用的 handler：

| 檔案 | 函式 | 行號 | 經由 helper 呼叫的 handler |
|---|---|---|---|
| `NCI_Core.py` | `CORE_RESET_NTF` | [L51](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L51) | — |

| 值 (hex) | 意義 |
|---|---|
| `00` | Unrecoverable error occurred in the NFCC |
| `01` | NFCC was powered on |
| `02` | CORE_RESET_CMD |

實作備註：

- 精確查表，未列出值（spec 的 RFU / proprietary 範圍）顯示 `RFU`。原始碼中另有被註解掉的 `tbl_rst_msg`（內容與 `tbl_cfg_status` 相同），未生效。

<a id="tbl_nci_ver"></a>
## tbl_nci_ver

| 項目 | 值 |
|---|---|
| Spec Table | Table 6: NCI Version（p.30） |
| 程式 `name` | `Table 6: NCI Version:` |
| 定義位置 | [`__table__.py:142`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L142)（NCI_Core Table 區段） |
| key 型別 | hex 字串（2 字元，或 `XX-YY` 範圍） |

使用的 handler：

| 檔案 | 函式 | 行號 | 經由 helper 呼叫的 handler |
|---|---|---|---|
| `NCI_Core.py` | `CORE_RESET_NTF` | [L59](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L59) | — |

| 值 (hex) | 意義 |
|---|---|
| `10` | 1.0 |
| `11` | 1.1 |
| `20` | 2.0 |

實作備註：

- 精確查表，未列出值顯示 `RFU`。

<a id="tbl_cfg_status"></a>
## tbl_cfg_status

| 項目 | 值 |
|---|---|
| Spec Table | Table 7: Configuration Status（p.30） |
| 程式 `name` | `Table 7: Configuration Status:` |
| 定義位置 | [`__table__.py:150`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L150)（NCI_Core Table 區段） |
| key 型別 | hex 字串（2 字元，或 `XX-YY` 範圍） |

使用的 handler：

| 檔案 | 函式 | 行號 | 經由 helper 呼叫的 handler |
|---|---|---|---|
| `NCI_Core.py` | `CORE_RESET_CMD` | [L15](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L15) | — |
| `NCI_Core.py` | `CORE_RESET_NTF` | [L55](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L55) | — |

| 值 (hex) | 意義 |
|---|---|
| `00` | Keep Config |
| `01` | Reset Config |

實作備註：

- `CORE_RESET_CMD` 用它解讀 Reset Type，`CORE_RESET_NTF` 用它解讀 Configuration Status（原始碼註解「same as table 7」）。

<a id="tbl_nfcc_feat_oct1"></a>
## tbl_nfcc_feat_oct1

| 項目 | 值 |
|---|---|
| Spec Table | Table 10: NFCC Features（Octet 1）（p.34） |
| 程式 `name` | `Table 10: NFCC Features:` |
| 定義位置 | [`__table__.py:157`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L157)（NCI_Core Table 區段） |
| key 型別 | int（bit 位置） |

使用的 handler：

| 檔案 | 函式 | 行號 | 經由 helper 呼叫的 handler |
|---|---|---|---|
| `NCI_Core.py` | `CORE_INIT_RSP` | [L152](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L152) | — |

| Bit | 意義 |
|---|---|
| bit 6 | Forced NFCEE routing |
| bit 5 | APDU Pattern based routing |
| bit 4 | System Code based routing |
| bit 3 | AID based routing |
| bit 2 | Protocol based routing |
| bit 1 | Technology based routing |

實作備註：

- key 為 **int bit 位置**。`CORE_INIT_RSP` 對 NFCC Features 第 2 個 byte（輸出標示 `Octet 1`）由 bit 6 往 bit 1 逐一查表，bit = 1 印 `Support`，否則 `Not support`。bit 7 與 bit 0 不解析。

<a id="tbl_nfcc_feat_oct2"></a>
## tbl_nfcc_feat_oct2

| 項目 | 值 |
|---|---|
| Spec Table | Table 10: NFCC Features（Octet 2）（p.34） |
| 程式 `name` | `Table 10: NFCC Features:` |
| 定義位置 | [`__table__.py:168`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L168)（NCI_Core Table 區段） |
| key 型別 | int（bit 位置） |

使用的 handler：

| 檔案 | 函式 | 行號 | 經由 helper 呼叫的 handler |
|---|---|---|---|
| `NCI_Core.py` | `CORE_INIT_RSP` | [L161](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L161) | — |

| Bit | 意義 |
|---|---|
| bit 3 | RF Cfg in Switched Off State |
| bit 2 | Switched On Sub-Mode States |
| bit 1 | Switched Off State |
| bit 0 | Battery Off State |

實作備註：

- key 為 **int bit 位置**。`CORE_INIT_RSP` 對 NFCC Features 第 3 個 byte（輸出標示 `Octet 2`）由 bit 3 往 bit 0 逐一查表，bit = 1 印 `Support`，否則 `Not support`。bit 7~4 不解析。

<a id="tbl_dest_type"></a>
## tbl_dest_type

| 項目 | 值 |
|---|---|
| Spec Table | Table 13: Destination Types（p.39） |
| 程式 `name` | `Table 13: Destination Types:` |
| 定義位置 | [`__table__.py:177`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L177)（NCI_Core Table 區段） |
| key 型別 | hex 字串（2 字元，或 `XX-YY` 範圍） |

使用的 handler：

| 檔案 | 函式 | 行號 | 經由 helper 呼叫的 handler |
|---|---|---|---|
| `NCI_Core.py` | `CORE_CONN_CREATE_CMD` | [L392](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L392) | — |

| 值 (hex) | 意義 |
|---|---|
| `01` | NFCC Loopback |
| `02` | Remote NFC Endpoint |
| `03` | NFCEE |

實作備註：

- 精確查表，未列出值顯示 `RFU`。

<a id="tbl_init_credits"></a>
## tbl_init_credits

| 項目 | 值 |
|---|---|
| Spec Table | Table 15: Initial Number of Credits |
| 程式 `name` | `Table 15: Initial Number of Credits:` |
| 定義位置 | [`__table__.py:185`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L185)（NCI_Core Table 區段） |
| key 型別 | hex 字串（2 字元，或 `XX-YY` 範圍） |

使用的 handler：

| 檔案 | 函式 | 行號 | 經由 helper 呼叫的 handler |
|---|---|---|---|
| `NCI_Core.py` | `CORE_CONN_CREATE_RSP` | [L474](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L474), [L475](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L475) | — |

| 值 (hex) | 意義 |
|---|---|
| `FF` | Data flow control is not used |

實作備註：

- 以 `num_credits in tbl_init_credits` 判斷：命中（`FF`）印表中字串，否則印十進位數值。

<a id="tbl_d_spec_type"></a>
## tbl_d_spec_type

| 項目 | 值 |
|---|---|
| Spec Table | Table 16: Destination-specific Parameters（p.40） |
| 程式 `name` | `Table 16: Destination-specific Parameters:` |
| 定義位置 | [`__table__.py:191`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L191)（NCI_Core Table 區段） |
| key 型別 | hex 字串（2 字元，或 `XX-YY` 範圍） |

使用的 handler：

| 檔案 | 函式 | 行號 | 經由 helper 呼叫的 handler |
|---|---|---|---|
| `NCI_Core.py` | `CORE_CONN_CREATE_CMD` | [L405](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L405) | — |

| 值 (hex) | 意義 |
|---|---|
| `00` | RF Discovery ID + RF Protocol |
| `01` | NFCEE ID + NFCEE Interface Protocol |

實作備註：

- 精確查表，未列出值顯示 `RFU`。

<a id="tbl_cfg_para"></a>
## tbl_cfg_para

| 項目 | 值 |
|---|---|
| Spec Table | Table 138: Configuration Parameter Tags（p.187） |
| 程式 `name` | `Table 138: Configuration Parameter Tags:` |
| 定義位置 | [`__table__.py:198`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L198)（NCI_Core Table 區段） |
| key 型別 | hex 字串（2 字元，或 `XX-YY` 範圍） |

使用的 handler：

| 檔案 | 函式 | 行號 | 經由 helper 呼叫的 handler |
|---|---|---|---|
| `NCI_Core.py` | `CORE_SET_CONFIG_CMD` | [L254](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L254) | — |
| `NCI_Core.py` | `CORE_SET_CONFIG_RSP` | [L299](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L299) | — |
| `NCI_Core.py` | `CORE_GET_CONFIG_CMD` | [L324](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L324) | — |
| `NCI_Core.py` | `CORE_GET_CONFIG_RSP` | [L358](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L358) | — |

| 值 (hex) | 意義 |
|---|---|
| `00` | TOTAL_DURATION |
| `01` | RFU |
| `02` | CON_DISCOVERY_PARAM |
| `03` | POWER_STATE |
| `04-07` | RFU |
| `08` | PA_BAIL_OUT |
| `09` | PA_DEVICES_LIMIT |
| `0A-0F` | RFU |
| `10` | PB_AFI |
| `11` | PB_BAIL_OUT |
| `12` | PB_ATTRIB_PARAM1 |
| `13` | PB_SENSB_REQ_PARAM |
| `14` | PB_DEVICES_LIMIT |
| `15-17` | RFU |
| `18` | PF_BIT_RATE |
| `19` | PF_BAIL_OUT |
| `1A` | PF_DEVICES_LIMIT |
| `1B-1F` | RFU |
| `20` | PI_B_H_INFO |
| `21` | PI_BIT_RATE |
| `22-27` | RFU |
| `28` | PN_NFC_DEP_PSL |
| `29` | PN_ATR_REQ_GEN_BYTES |
| `2A` | PN_ATR_REQ_CONFIG |
| `2B-2E` | RFU |
| `2F` | PV_DEVICES_LIMIT |
| `30` | LA_BIT_FRAME_SDD |
| `31` | LA_PLATFORM_CONFIG |
| `32` | LA_SEL_INFO |
| `33` | LA_NFCID1 |
| `34-37` | RFU |
| `38` | LB_SENSB_INFO |
| `39` | LB_NFCID0 |
| `3A` | LB_APPLICATION_DATA |
| `3B` | LB_SFGI |
| `3C` | LB_FWI_ADC_FO |
| `3D` | RFU |
| `3E` | LB_BIT_RATE |
| `3F` | RFU |
| `40` | LF_T3T_IDENTIFIERS_1 |
| `41` | LF_T3T_IDENTIFIERS_2 |
| `42` | LF_T3T_IDENTIFIERS_3 |
| `43` | LF_T3T_IDENTIFIERS_4 |
| `44` | LF_T3T_IDENTIFIERS_5 |
| `45` | LF_T3T_IDENTIFIERS_6 |
| `46` | LF_T3T_IDENTIFIERS_7 |
| `47` | LF_T3T_IDENTIFIERS_8 |
| `48` | LF_T3T_IDENTIFIERS_9 |
| `49` | LF_T3T_IDENTIFIERS_10 |
| `4A` | LF_T3T_IDENTIFIERS_11 |
| `4B` | LF_T3T_IDENTIFIERS_12 |
| `4C` | LF_T3T_IDENTIFIERS_13 |
| `4D` | LF_T3T_IDENTIFIERS_14 |
| `4E` | LF_T3T_IDENTIFIERS_15 |
| `4F` | LF_T3T_IDENTIFIERS_16 |
| `51` | RFU |
| `52` | LF_T3T_MAX |
| `53` | LF_T3T_FLAGS |
| `55` | LF_T3T_RD_ALLOWED |
| `50` | LF_PROTOCOL_TYPE |
| `54` | RFU |
| `56-57` | RFU |
| `58` | LI_A_RATS_TB1 |
| `59` | LI_A_HIST_BY |
| `5A` | LI_B_H_INFO_RESP |
| `5B` | LI_A_BIT_RATE |
| `5C` | LI_A_RATS_TC1 |
| `5D-5F` | RFU |
| `60` | LN_WT |
| `61` | LN_ATR_RES_GEN_BYTES |
| `62` | LN_ATR_RES_CONFIG |
| `63-67` | RFU |
| `68` | PACM_BIT_RATE |
| `69-7F` | RFU |
| `80` | RF_FIELD_INFO |
| `81` | RF_NFCEE_ACTION |
| `82` | NFCDEP_OP |
| `83` | LLCP_VERSION |
| `84` | RFU |
| `85` | NFCC_CONFIG_CONTROL |
| `86-9F` | RFU |
| `A0-FE` | Reserved |
| `FF` | RFU |

實作備註：

- ✅ 已修正（2026-10）：所有呼叫端改用 `lookup`，範圍 key（如 `04-07`、`A0-FE`）可命中（例如 `A0` 顯示 `Reserved`）。
- `LF_T3T_*` 區段的 `51`/`52`/`53`/`55` 與 NFC-F 區段的 `50`/`54`/`56-57` 在原始碼中交錯排列，但 key 值各自唯一。

<a id="tbl_rf_field_status"></a>
## tbl_rf_field_status

| 項目 | 值 |
|---|---|
| Spec Table | Table 22: RF Field Status |
| 程式 `name` | `Table 22: RF Field Status:` |
| 定義位置 | [`__table__.py:311`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L311)（RF_Management Table 區段） |
| key 型別 | hex 字串（2 字元，或 `XX-YY` 範圍） |

使用的 handler：

| 檔案 | 函式 | 行號 | 經由 helper 呼叫的 handler |
|---|---|---|---|
| `RF_Management.py` | `RF_FIELD_INFO_NTF` | [L790](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L790) | — |

| 值 (hex) | 意義 |
|---|---|
| `00` | No Operating field generated by Remote NFC Endpoint. |
| `01` | Operating field generated by Remote NFC Endpoint. |

實作備註：

- ✅ 已修正（2026-10）：查無時改印 `RFU (xx)`，不再 fallback 成 `00` 的文字。

<a id="tbl_mode"></a>
## tbl_mode

| 項目 | 值 |
|---|---|
| Spec Table | Table 49: Value Field for Mode（p.74） |
| 程式 `name` | `Table 49: Value Field for Mode:` |
| 定義位置 | [`__table__.py:318`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L318)（RF_Management Table 區段） |
| key 型別 | hex 字串（2 字元，或 `XX-YY` 範圍） |

使用的 handler：

| 檔案 | 函式 | 行號 | 經由 helper 呼叫的 handler |
|---|---|---|---|
| `RF_Management.py` | `RF_DISCOVER_MAP_CMD` | [L33](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L33) | — |

| 值 (hex) | 意義 |
|---|---|
| `00` | Error |
| `01` | Polling |
| `02` | Listen |
| `03` | Listen/Polling |

實作備註：

- 精確查表，未列出值顯示 `RFU`。

<a id="tbl_more"></a>
## tbl_more

| 項目 | 值 |
|---|---|
| Spec Table | Table 51: More field values（p.78） |
| 程式 `name` | `Table 51: More field values:` |
| 定義位置 | [`__table__.py:327`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L327)（RF_Management Table 區段） |
| key 型別 | hex 字串（2 字元，或 `XX-YY` 範圍） |

使用的 handler：

| 檔案 | 函式 | 行號 | 經由 helper 呼叫的 handler |
|---|---|---|---|
| `RF_Management.py` | `LISTEN_MODE_ROUTING_INFO` | [L77](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L77) | `RF_SET_LISTEN_MODE_ROUTING_CMD`, `RF_GET_LISTEN_MODE_ROUTING_NTF` |

| 值 (hex) | 意義 |
|---|---|
| `00` | Last Message |
| `01` | More Message(s) to follow |

實作備註：

- 精確查表，未列出值顯示 `RFU`。

<a id="tbl_l_mode_routing_entry_type"></a><a id="tbl_L_mode_routing_entry_type"></a>
## tbl_L_mode_routing_entry_type

| 項目 | 值 |
|---|---|
| Spec Table | Table 53: Listen Mode Routing Entry Types（p.79） |
| 程式 `name` | `Table 53: Listen Mode Routing Entry Types:` |
| 定義位置 | [`__table__.py:344`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L344)（RF_Management Table 區段） |
| key 型別 | 單一 hex 字元 |

使用的 handler：

| 檔案 | 函式 | 行號 | 經由 helper 呼叫的 handler |
|---|---|---|---|
| `RF_Management.py` | `LISTEN_MODE_ROUTING_INFO` | [L90](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L90) | `RF_SET_LISTEN_MODE_ROUTING_CMD`, `RF_GET_LISTEN_MODE_ROUTING_NTF` |

| 值 (hex) | 意義 |
|---|---|
| `0` | Technology-based routing entry |
| `1` | Protocol-based routing entry |
| `2` | AID-based routing entry |
| `3` | System Code-based routing entry |
| `4` | APDU Pattern-based routing entry |

實作備註：

- key 為**單一 hex 字元**。呼叫端取 Qualifier-Type byte 的低 4 bits（`q_type[1:2]`）查表；高 4 bits 的 Qualifier（Table 52）由程式以 bit 判斷硬編碼處理。

<a id="tbl_pwr_state"></a>
## tbl_pwr_state

| 項目 | 值 |
|---|---|
| Spec Table | Table 59: Value Field for Power State（p.81） |
| 程式 `name` | `Table 59: Value Field for Power State:` |
| 定義位置 | [`__table__.py:400`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L400)（RF_Management Table 區段） |
| key 型別 | int（bit 位置） |

使用的 handler：

| 檔案 | 函式 | 行號 | 經由 helper 呼叫的 handler |
|---|---|---|---|
| `RF_Management.py` | `LISTEN_MODE_ROUTING_INFO` | [L119](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L119) | `RF_SET_LISTEN_MODE_ROUTING_CMD`, `RF_GET_LISTEN_MODE_ROUTING_NTF` |
| `RF_Management.py` | `RF_SET_FORCED_NFCEE_ROUTING_CMD` | [L1272](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L1272) | — |
| `NFCEE_Management.py` | `NFCEE_DISCOVER_NTF` | [L124](../../nci_decoder/nfc_forum_2_0_pkg/NFCEE_Management.py#L124) | — |

| Bit | 意義 |
|---|---|
| bit 5 | Screen Off lock (Sub-State 3) |
| bit 4 | Screen On lock (Sub-State 2) |
| bit 3 | Screen off unlock (Sub-State 1) |
| bit 2 | Battery Off State |
| bit 1 | Switch Off State |
| bit 0 | Switch On State |

實作備註：

- key 為 **int bit 位置**（bit 7、6 在原始碼中被註解為 RFU）。呼叫端由 bit 5 往 bit 0 逐一查表，bit = 1 印 `Apply`，否則 `Not apply`。

<a id="tbl_rf_dis_id"></a>
## tbl_rf_dis_id

| 項目 | 值 |
|---|---|
| Spec Table | Table 67: RF Discovery ID（p.95） |
| 程式 `name` | `Table 67: RF Discovery ID: ` |
| 定義位置 | [`__table__.py:413`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L413)（RF_Management Table 區段） |
| key 型別 | hex 字串（2 字元，或 `XX-YY` 範圍） |

使用的 handler：

| 檔案 | 函式 | 行號 | 經由 helper 呼叫的 handler |
|---|---|---|---|
| `NCI_Core.py` | `CORE_CONN_CREATE_CMD` | [L418](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L418) | — |
| `RF_Management.py` | `RF_DISCOVER_NTF` | [L492](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L492) | — |
| `RF_Management.py` | `RF_DISCOVER_SELECT_CMD` | [L538](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L538) | — |
| `RF_Management.py` | `RF_INTF_ACTIVATED_NTF` | [L590](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L590) | — |

| 值 (hex) | 意義 |
|---|---|
| `00` | RFU |
| `01-FF` | Dynamically assigned by the NFCC |
| `FF` | RFU |

實作備註：

- ✅ 已修正（2026-10）：`CORE_CONN_CREATE_CMD` 改用 `lookup`，`01`~`FE` 命中 `01-FF` 顯示 `Dynamically assigned by the NFCC`（`FF` 精確 key 優先，仍為 `RFU`）。
- `RF_DISCOVER_NTF`、`RF_DISCOVER_SELECT_CMD`、`RF_INTF_ACTIVATED_NTF` 仍為 `.get(rf_dis_id, rf_dis_id)`：只有 `00`、`FF` 會命中，其餘值（`01`~`FE`）直接印原始 hex。`01-FF` 與 `FF` 兩個 key 範圍重疊。

<a id="tbl_deactivate_type"></a>
## tbl_deactivate_type

| 項目 | 值 |
|---|---|
| Spec Table | Table 80: Deactivation Types（p.104） |
| 程式 `name` | `Table 80: Deactivation Types:` |
| 定義位置 | [`__table__.py:498`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L498)（RF_Management Table 區段） |
| key 型別 | hex 字串（2 字元，或 `XX-YY` 範圍） |

使用的 handler：

| 檔案 | 函式 | 行號 | 經由 helper 呼叫的 handler |
|---|---|---|---|
| `RF_Management.py` | `RF_DEACTIVATE_CMD` | [L737](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L737) | — |
| `RF_Management.py` | `RF_DEACTIVATE_NTF` | [L770](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L770) | — |

| 值 (hex) | 意義 |
|---|---|
| `00` | Idle Mode |
| `01` | Sleep Mode |
| `02` | Sleep_AF Mode |
| `03` | Discovery |
| `04-FF` | RFU |

實作備註：

- ✅ 已修正（2026-10）：改用 `lookup`，`04-FF` 範圍 key 可命中（輸出同為 `RFU`）。

<a id="tbl_deactivate_reason"></a>
## tbl_deactivate_reason

| 項目 | 值 |
|---|---|
| Spec Table | Table 81: Deactivation Reasons（p.105） |
| 程式 `name` | `Table 81: Deactivation Reasons:` |
| 定義位置 | [`__table__.py:508`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L508)（RF_Management Table 區段） |
| key 型別 | hex 字串（2 字元，或 `XX-YY` 範圍） |

使用的 handler：

| 檔案 | 函式 | 行號 | 經由 helper 呼叫的 handler |
|---|---|---|---|
| `RF_Management.py` | `RF_DEACTIVATE_NTF` | [L774](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L774) | — |

| 值 (hex) | 意義 |
|---|---|
| `00` | DH_Request |
| `01` | Endpoint_Request |
| `02` | RF_Link_Loss |
| `03` | NFC-B_Bad_AFI |
| `04` | DH request failed due to error |
| `05-FF` | RFU |

實作備註：

- ✅ 已修正（2026-10）：改用 `lookup`，`05-FF` 範圍 key 可命中（輸出同為 `RFU`）。

<a id="tbl_nfcee_disc_req_type"></a>
## tbl_nfcee_disc_req_type

| 項目 | 值 |
|---|---|
| Spec Table | Table 85: TLV Coding for RF Discovery Request from NFCEE（p.108） |
| 程式 `name` | `Table 85: TLV Coding for RF Discovery Request from NFCEE:` |
| 定義位置 | [`__table__.py:519`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L519)（RF_Management Table 區段） |
| key 型別 | hex 字串（2 字元，或 `XX-YY` 範圍） |

使用的 handler：

| 檔案 | 函式 | 行號 | 經由 helper 呼叫的 handler |
|---|---|---|---|
| `RF_Management.py` | `RF_NFCEE_DISCOVERY_REQ_NTF` | [L935](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L935), [L936](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L936) | — |

| 值 (hex) | 意義 |
|---|---|
| `00` | Added to list |
| `01` | Removed from list |
| `02-7F` | RFU |
| `80-FF` | For proprietary use |

實作備註：

- `RF_NFCEE_DISCOVERY_REQ_NTF` 先 `find_range_key` 再查表，範圍 key 可正確命中；輸出不附原始 hex。

<a id="tbl_nfcee_ntf_trig"></a>
## tbl_nfcee_ntf_trig

| 項目 | 值 |
|---|---|
| Spec Table | Table 88: Trigger in NFCEE Action Notification（p.109） |
| 程式 `name` | `Table 88: Trigger in NFCEE Action Notification:` |
| 定義位置 | [`__table__.py:528`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L528)（RF_Management Table 區段） |
| key 型別 | hex 字串（2 字元，或 `XX-YY` 範圍） |

使用的 handler：

| 檔案 | 函式 | 行號 | 經由 helper 呼叫的 handler |
|---|---|---|---|
| `RF_Management.py` | `RF_NFCEE_ACTION_NTF` | [L886](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L886), [L887](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L887) | — |

| 值 (hex) | 意義 |
|---|---|
| `00` | [ISO/IEC_7816-4] SELECT command with an AID |
| `01` | Protocol-based Route Selection Process (ref to Table 133) |
| `02` | Technology-based Route Selection Process (ref to Table 130) |
| `03` | System Code-based Route Selection Process |
| `04` | TAPDU Pattern-based Route Selection Process (as defined in Table 58) |
| `05` | Forced NFCEE Routing is used (See Table 130) |
| `06-0F` | RFU |
| `10-7F` | Application specific |
| `80-FF` | RFU |

實作備註：

- `RF_NFCEE_ACTION_NTF` 先 `find_range_key` 再查表，範圍 key 可正確命中。

<a id="tbl_rf_commu_para_id"></a>
## tbl_rf_commu_para_id

| 項目 | 值 |
|---|---|
| Spec Table | Table 91: TLV Coding for RF Communication Parameter ID（p.117） |
| 程式 `name` | `Table 91: TLV Coding for RF Communication Parameter ID:` |
| 定義位置 | [`__table__.py:543`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L543)（RF_Management Table 區段） |
| key 型別 | hex 字串（2 字元，或 `XX-YY` 範圍） |

使用的 handler：

| 檔案 | 函式 | 行號 | 經由 helper 呼叫的 handler |
|---|---|---|---|
| `RF_Management.py` | `RF_PARAMETER_UPDATE_CMD` | [L985](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L985) | — |
| `RF_Management.py` | `RF_PARAMETER_UPDATE_RSP` | [L1049](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L1049) | — |

| 值 (hex) | 意義 |
|---|---|
| `00` | RF Technology and Mode (coded as defined in Table 131) |
| `01` | Transmit Bit Rate (coded as defined in Table 132) |
| `02` | Receive Bit Rate (coded as defined in Table 132) |
| `03` | NFC-B Data Exchange Configuration (coded as defined in Table 92) |
| `80-FF` | Proprietary |

實作備註：

- ✅ 已修正（2026-10）：改用 `lookup`，`80`~`FF` 顯示 `Proprietary`。
- ✅ 已修正（2026-10）：`02` 的說明字串已改為「coded as defined in Table 132」，與 `RF_PARAMETER_UPDATE_CMD` 實際以 `tbl_bit_rates` 解讀 Rx 值一致。

<a id="tbl_rf_tech"></a>
## tbl_rf_tech

| 項目 | 值 |
|---|---|
| Spec Table | Table 130: RF Technologies（p.183） |
| 程式 `name` | `Table 130: RF Technologies:` |
| 定義位置 | [`__table__.py:553`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L553)（RF_Management Table 區段） |
| key 型別 | hex 字串（2 字元，或 `XX-YY` 範圍） |

使用的 handler：

| 檔案 | 函式 | 行號 | 經由 helper 呼叫的 handler |
|---|---|---|---|
| `RF_Management.py` | `LISTEN_MODE_ROUTING_INFO` | [L132](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L132) | `RF_SET_LISTEN_MODE_ROUTING_CMD`, `RF_GET_LISTEN_MODE_ROUTING_NTF` |
| `RF_Management.py` | `RF_NFCEE_ACTION_NTF` | [L902](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L902) | — |

| 值 (hex) | 意義 |
|---|---|
| `00` | NFC_RF_TECHNOLOGY_A |
| `01` | NFC_RF_TECHNOLOGY_B |
| `02` | NFC_RF_TECHNOLOGY_F |
| `03` | NFC_RF_TECHNOLOGY_V |

實作備註：

- 精確查表；`80-FE` 只以註解形式存在，查表結果為 `RFU`。

<a id="tbl_rf_tech_mode"></a>
## tbl_rf_tech_mode

| 項目 | 值 |
|---|---|
| Spec Table | Table 131: RF Technology and Mode（p.184） |
| 程式 `name` | `Table 131: RF Technology and Mode:` |
| 定義位置 | [`__table__.py:563`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L563)（RF_Management Table 區段） |
| key 型別 | hex 字串（2 字元，或 `XX-YY` 範圍） |

使用的 handler：

| 檔案 | 函式 | 行號 | 經由 helper 呼叫的 handler |
|---|---|---|---|
| `RF_Management.py` | `RF_DISCOVER_CMD` | [L261](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L261) | — |
| `RF_Management.py` | `RF_TECH_SPEC_PARA` | [L308](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L308) | `RF_DISCOVER_NTF`, `RF_INTF_ACTIVATED_NTF` |
| `RF_Management.py` | `RF_DISCOVER_NTF` | [L500](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L500) | — |
| `RF_Management.py` | `RF_INTF_ACTIVATED_NTF` | [L601](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L601), [L627](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L627), [L644](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L644) | — |
| `RF_Management.py` | `RF_NFCEE_DISCOVERY_REQ_NTF` | [L951](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L951), [L952](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L952) | — |
| `RF_Management.py` | `RF_PARAMETER_UPDATE_CMD` | [L997](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L997) | — |

| 值 (hex) | 意義 |
|---|---|
| `00` | A_PASSIVE_POLL |
| `01` | B_PASSIVE_POLL |
| `02` | F_PASSIVE_POLL |
| `03` | ACTIVE_POLL |
| `04-05` | RFU |
| `06` | V_PASSIVE_POLL |
| `07-6F` | RFU |
| `70-7F` | Reserved for Proprietary Technologies in Poll Mode |
| `80` | A_PASSIVE_LISTEN |
| `81` | B_PASSIVE_LISTEN |
| `82` | F_PASSIVE_LISTEN |
| `83` | ACTIVE_LISTEN |
| `84-EF` | RFU |
| `F0-FF` | Reserved for Proprietary Technologies in Listen Mode |

實作備註：

- ✅ 已修正（2026-10）：所有呼叫端改用 `lookup`，範圍 key（如 `70-7F`、`F0-FF`）可命中。
- ✅ 已修正（2026-10）：`RF_TECH_SPEC_PARA` 與 `RF_INTF_ACTIVATED_NTF` 改以 RF Technology and Mode 的 hex code 判斷後續參數格式的分支（不受各 vendor 表名稱字串影響）。

<a id="tbl_len_rdu_val"></a>
## tbl_len_rdu_val

| 項目 | 值 |
|---|---|
| Spec Table | Table 137: Length Reduction Values（p.186） |
| 程式 `name` | `Table 137: Length Reduction Value` |
| 定義位置 | [`__table__.py:582`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L582)（RF_Management Table 區段） |
| key 型別 | hex 字串（2 字元，或 `XX-YY` 範圍） |

使用的 handler：

| 檔案 | 函式 | 行號 | 經由 helper 呼叫的 handler |
|---|---|---|---|
| `RF_Management.py` | `RF_INTF_ACTIVATED_NTF` | [L709](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L709) | — |

| 值 (hex) | 意義 |
|---|---|
| `00` | No PSL_REQ and PSL_RES were exchanged |
| `01` | 254 Bytes |
| `02` | 192 Bytes |
| `03` | 128 Bytes |
| `04` | 64 Bytes |
| `05-FF` | RFU |

實作備註：

- ✅ 已修正（2026-10）：改用 `lookup`，`05-FF` 範圍 key 可命中（輸出同為 `RFU`）；NFC-DEP Poll（Table 102）與 Listen（Table 103）兩個分支現在都會讀 Data Exchange Length Reduction 並查此表。

<a id="tbl_tlv_type"></a>
## tbl_tlv_type

| 項目 | 值 |
|---|---|
| Spec Table | Table 118: TLV Coding for NFCEE Discovery（p.158） |
| 程式 `name` | `Table 118: TLV Coding for NFCEE Discovery:` |
| 定義位置 | [`__table__.py:599`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L599)（NFCEE_Management Table 區段） |
| key 型別 | hex 字串（2 字元，或 `XX-YY` 範圍） |

使用的 handler：

| 檔案 | 函式 | 行號 | 經由 helper 呼叫的 handler |
|---|---|---|---|
| `NFCEE_Management.py` | `NFCEE_DISCOVER_NTF` | [L96](../../nci_decoder/nfc_forum_2_0_pkg/NFCEE_Management.py#L96), [L97](../../nci_decoder/nfc_forum_2_0_pkg/NFCEE_Management.py#L97) | — |

| 值 (hex) | 意義 |
|---|---|
| `00` | Hardware / Registration Identification |
| `01` | ATR Bytes |
| `02` | T3T Command Set Interface Supplementary Information |
| `03` | Host ID in the HCI Network |
| `04` | NDEF |
| `05-9F` | RFU |
| `A0-FF` | For proprietary use |

實作備註：

- `NFCEE_DISCOVER_NTF` 先 `find_range_key` 再查表，範圍 key 可正確命中。
- ✅ 已修正（2026-10）：原始碼中被註解掉、標為 Table 119 的舊版 `tbl_tlv_type` 已刪除。

<a id="tbl_nfcee_disc_status"></a>
## tbl_nfcee_disc_status

| 項目 | 值 |
|---|---|
| Spec Table | Table 117: NFCEE_DISCOVER_NTF 的 NFCEE Status 欄位（p.156） |
| 程式 `name` | `Table 117: NFCEE_DISCOVER_NTF NFCEE Status:` |
| 定義位置 | [`__table__.py:611`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L611)（NFCEE_Management Table 區段） |
| key 型別 | hex 字串（2 字元，或 `XX-YY` 範圍） |

使用的 handler：

| 檔案 | 函式 | 行號 | 經由 helper 呼叫的 handler |
|---|---|---|---|
| `NFCEE_Management.py` | `NFCEE_DISCOVER_NTF` | [L65](../../nci_decoder/nfc_forum_2_0_pkg/NFCEE_Management.py#L65) | — |

| 值 (hex) | 意義 |
|---|---|
| `00` | Enabled |
| `01` | Disabled |
| `02` | Unresponsive |
| `03-FF` | RFU |

實作備註：

- 精確查表；`03-FF` 範圍 key 不被範圍查詢，但 fallback 同為 `RFU`。與 `tbl_nfcee_status`（Table 122）是不同欄位，勿混用。

<a id="tbl_nfcee_status"></a>
## tbl_nfcee_status

| 項目 | 值 |
|---|---|
| Spec Table | Table 122: NFCEE_STATUS_NTF 的 NFCEE Status 欄位（p.165） |
| 程式 `name` | `Table 122: NFCEE_STATUS_NTF NFCEE Status:` |
| 定義位置 | [`__table__.py:620`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py#L620)（NFCEE_Management Table 區段） |
| key 型別 | hex 字串（2 字元，或 `XX-YY` 範圍） |

使用的 handler：

| 檔案 | 函式 | 行號 | 經由 helper 呼叫的 handler |
|---|---|---|---|
| `NFCEE_Management.py` | `NFCEE_STATUS_NTF` | [L228](../../nci_decoder/nfc_forum_2_0_pkg/NFCEE_Management.py#L228) | — |

| 值 (hex) | 意義 |
|---|---|
| `00` | Unrecoverable error |
| `01` | NFCEE Initialization sequence started |
| `02` | NFCEE Initialization sequence completed |
| `03-7F` | RFU |
| `80-FF` | Proprietary |

實作備註：

- ✅ 已修正（2026-10）：`NFCEE_STATUS_NTF` 改用 `lookup`，`0x80`~`0xFF` 顯示 `Proprietary`（`62 02 02 82 81` 輸出 `NFCEE Status: Proprietary (81)`）。
