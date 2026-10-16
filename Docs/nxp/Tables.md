# NXP 對照表（`Nxp_pkg/__table__.py`）

本文件完整列出 [`Nxp_pkg/__table__.py`](../../nci_decoder/Nxp_pkg/__table__.py) 中所有模組層級的 `tbl_*` 對照表（共 39 張）。NXP 套件的 handler 以 `import Nxp_pkg.__table__ as NFC_table` 引入，多數 handler 以 `range_lookup.lookup(NFC_table.tbl_xxx, value)` 查表：先查精確鍵，再查涵蓋該值的 range 型鍵（如 `'80-FE'`、`'A0-FE'`），都查不到才回傳 `RFU`（部分 handler 仍直接用 `.get(value, "RFU")`）。

> ✅ 已修正（2026-10）：先前多數 handler 直接以 `.get(value, "RFU")` 查表，range 型鍵永遠不會命中（例如 `tbl_cfg_para` 的 `A0-FE`、`tbl_nfcee_proto` 的 `80-FE`、`tbl_nfcee_status` 的 `03-7F` 會顯示為 `RFU`）；現已改用 `range_lookup.lookup()`，表中的 range 鍵皆可正確對應。

每張表標示它與 [`nfc_forum_2_0_pkg/__table__.py`](../../nci_decoder/nfc_forum_2_0_pkg/__table__.py) 同名表的差異：
- **相同**：鍵與值完全一致（`'name'` 鍵亦一致）。
- **NXP 新增值**：forum 表的所有鍵值都保留，NXP 另外增加鍵（多為 SN2x0 專有值）。
- **有差異**：有鍵被移除或同鍵文字不同（逐項列出）。
- **NXP 獨有表**：forum 無同名表。

「直接使用的 handler」以 AST 掃描 `Nxp_pkg/*.py`（不含 `__table__.py`）中所有 `NFC_table.<表名>` 屬性存取，列出所在函式；handler 內自行定義的同名區域變數表（例如 `HDLL.py` 的 `tbl_ssta`、`tbl_status`）不屬於本檔範圍，不列入。

「間接使用」：許多 NXP handler 只是包裝層，呼叫 `Origin.<handler>(raw, "nxp")`（`Origin` = `nfc_forum_2_0_pkg` 的同名模組）。forum handler 內以 `NFC_table = pkg_import.tbl_import(vendor, model)` 取表，`vendor_registry.resolve("nxp")` 會回傳 `Nxp_pkg.__table__`，因此這些 forum handler 在 NXP 路徑下查的是**本檔的 NXP 表**。間接使用欄位列出「NXP 包裝 handler → 被呼叫的 forum handler」，已包含 forum handler 內部再呼叫的同模組 helper（例如 `LISTEN_MODE_ROUTING_INFO`）所用到的表。

統計：相同 25 張、NXP 新增值 3 張、有差異 6 張、NXP 獨有表 5 張。forum 有而 NXP 沒有的同名表：無。

另外 `__table__.py` 中以三引號字串註記的 Table 52、54–58、68–76（routing value 欄位、RF Technology Specific Parameters 結構）不是 dict，未在本檔列出；其解析直接實作在 handler 中。

## 總覽

| 表名 | NCI spec Table / 來源 | 項目數 | 與 nfc_forum_2_0 差異 | 使用 handler 數（直接 / 間接） |
|---|---|---|---|---|
| [`tbl_general_status`](#tbl_general_status) | — | 2 | NXP 獨有表 | 2 / 0 |
| [`tbl_general_status_n`](#tbl_general_status_n) | — | 2 | NXP 獨有表 | 2 / 0 |
| [`tbl_status_codes`](#tbl_status_codes) | Table 129: Status Codes | 38 | NXP 新增值 | 18 / 21 |
| [`tbl_bit_rates`](#tbl_bit_rates) | Table 132: Bit Rates | 9 | 有差異 | 2 / 2 |
| [`tbl_rf_proto`](#tbl_rf_proto) | Table 133: RF Protocols | 9 | 有差異 | 0 / 9 |
| [`tbl_nfcee_proto`](#tbl_nfcee_proto) | Table 136: NFCEE Protocols / Interfaces | 7 | 相同 | 0 / 2 |
| [`tbl_nfcee_id`](#tbl_nfcee_id) | Table 116: NFCEE IDs | 12 | NXP 新增值 | 0 / 8 |
| [`tbl_rf_if`](#tbl_rf_if) | Table 134: RF Interfaces | 8 | 有差異 | 0 / 4 |
| [`tbl_rf_if_exten`](#tbl_rf_if_exten) | Table 135: RF Interface Extensions | 2 | 相同 | 0 / 1 |
| [`tbl_conn_id`](#tbl_conn_id) | Table 4: Conn ID | 3 | 相同 | 1 / 3 |
| [`tbl_rst_trig`](#tbl_rst_trig) | Table 5: Control Messages to Reset the NFCC | 10 | NXP 新增值 | 1 / 0 |
| [`tbl_nci_ver`](#tbl_nci_ver) | Table 6: NCI Version | 3 | 相同 | 1 / 0 |
| [`tbl_cfg_status`](#tbl_cfg_status) | Table 7: Configuration Status | 2 | 相同 | 1 / 1 |
| [`tbl_nfcc_feat_oct1`](#tbl_nfcc_feat_oct1) | Table 10: NFCC Features | 6 | 相同 | 0 / 1 |
| [`tbl_nfcc_feat_oct2`](#tbl_nfcc_feat_oct2) | Table 10: NFCC Features | 4 | 相同 | 0 / 1 |
| [`tbl_dest_type`](#tbl_dest_type) | Table 13: Destination Types | 3 | 相同 | 0 / 1 |
| [`tbl_init_credits`](#tbl_init_credits) | Table 15: Initial Number of Credits | 1 | 相同 | 1 / 0 |
| [`tbl_d_spec_type`](#tbl_d_spec_type) | Table 16: Destination-specific Parameters | 2 | 相同 | 0 / 1 |
| [`tbl_cfg_para`](#tbl_cfg_para) | Table 138: Configuration Parameter Tags | 168 | 有差異 | 4 / 0 |
| [`tbl_rf_field_status`](#tbl_rf_field_status) | Table 22: RF Field Status | 2 | 相同 | 0 / 1 |
| [`tbl_mode`](#tbl_mode) | Table 49: Value Field for Mode | 4 | 相同 | 0 / 1 |
| [`tbl_more`](#tbl_more) | Table 51: More field values | 2 | 相同 | 0 / 2 |
| [`tbl_L_mode_routing_entry_type`](#tbl_l_mode_routing_entry_type) | Table 53: Listen Mode Routing Entry Types | 5 | 相同 | 0 / 2 |
| [`tbl_pwr_state`](#tbl_pwr_state) | Table 59: Value Field for Power State | 6 | 相同 | 0 / 3 |
| [`tbl_rf_dis_id`](#tbl_rf_dis_id) | Table 67: RF Discovery ID: | 3 | 相同 | 0 / 4 |
| [`tbl_deactivate_type`](#tbl_deactivate_type) | Table 80: Deactivation Types | 5 | 相同 | 0 / 2 |
| [`tbl_deactivate_reason`](#tbl_deactivate_reason) | Table 81: Deactivation Reasons | 6 | 相同 | 0 / 1 |
| [`tbl_nfcee_disc_req_type`](#tbl_nfcee_disc_req_type) | Table 85: TLV Coding for RF Discovery Request from NFCEE | 4 | 相同 | 0 / 1 |
| [`tbl_nfcee_ntf_trig`](#tbl_nfcee_ntf_trig) | Table 88: Trigger in NFCEE Action Notification | 9 | 相同 | 0 / 1 |
| [`tbl_rf_commu_para_id`](#tbl_rf_commu_para_id) | Table 91: TLV Coding for RF Communication Parameter ID | 5 | 相同 | 0 / 2 |
| [`tbl_rf_tech`](#tbl_rf_tech) | Table 130: RF Technologies | 4 | 相同 | 0 / 3 |
| [`tbl_rf_tech_mode`](#tbl_rf_tech_mode) | Table 131: RF Technology and Mode | 10 | 有差異 | 0 / 5 |
| [`tbl_len_rdu_val`](#tbl_len_rdu_val) | Table 137: Length Reduction Value | 6 | 相同 | 0 / 1 |
| [`tbl_tlv_type`](#tbl_tlv_type) | Table 118: TLV Coding for NFCEE Discovery | 7 | 相同 | 0 / 1 |
| [`tbl_nfcee_disc_status`](#tbl_nfcee_disc_status) | Table 117: NFCEE_DISCOVER_NTF NFCEE Status | 4 | 相同 | 0 / 1 |
| [`tbl_nfcee_status`](#tbl_nfcee_status) | Table 122: NFCEE_STATUS_NTF NFCEE Status | 17 | 有差異 | 0 / 1 |
| [`tbl_in_clk_freq`](#tbl_in_clk_freq) | p.87 | 9 | NXP 獨有表 | 1 / 0 |
| [`tbl_rf_trans_id`](#tbl_rf_trans_id) | Table 1 | 63 | NXP 獨有表 | 2 / 0 |
| [`tbl_register`](#tbl_register) | Table 3 | 11 | NXP 獨有表 | 1 / 0 |

<a id="tbl_general_status"></a>
## tbl_general_status

| 項目 | 值 |
|---|---|
| 定義 | [`__table__.py:9`](../../nci_decoder/Nxp_pkg/__table__.py#L9) |
| NCI spec / 來源 | — |
| 直接使用的 handler | [`NCI_Core.py:664`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L664) `VALUE_OF_REGISTER`<br>[`Proprietary.py:551`](../../nci_decoder/Nxp_pkg/Proprietary.py#L551) `TEST_PRBS_CARD_CMD` |
| 間接使用（經 `Origin.*`） | — |
| 與 nfc_forum_2_0 差異 | **NXP 獨有表** — nfc_forum_2_0_pkg/__table__.py 無同名表。 |

| 值 (hex) | 意義 |
|---|---|
| `00` | Disabled |
| `01` | Enabled  |

<a id="tbl_general_status_n"></a>
## tbl_general_status_n

| 項目 | 值 |
|---|---|
| 定義 | [`__table__.py:14`](../../nci_decoder/Nxp_pkg/__table__.py#L14) |
| NCI spec / 來源 | — |
| 直接使用的 handler | [`NCI_Core.py:664`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L664) `VALUE_OF_REGISTER`<br>[`Proprietary.py:321`](../../nci_decoder/Nxp_pkg/Proprietary.py#L321) `COLD_RESET_CMD` |
| 間接使用（經 `Origin.*`） | — |
| 與 nfc_forum_2_0 差異 | **NXP 獨有表** — nfc_forum_2_0_pkg/__table__.py 無同名表。 |

| 值 (hex) | 意義 |
|---|---|
| `00` | Enabled  |
| `01` | Disabled |

<a id="tbl_status_codes"></a>
## tbl_status_codes

| 項目 | 值 |
|---|---|
| 定義 | [`__table__.py:20`](../../nci_decoder/Nxp_pkg/__table__.py#L20) |
| NCI spec / 來源 | Table 129: Status Codes |
| `'name'` 鍵 | `Table 129: Status Codes:`（表內含 `'name'` 鍵，非對照值，下表未列） |
| 直接使用的 handler | [`NCI_Core.py:177`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L177) `CORE_SET_CONFIG_RSP`<br>[`NCI_Core.py:237`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L237) `CORE_GET_CONFIG_RSP`<br>[`NCI_Core.py:307`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L307) `CORE_CONN_CREATE_RSP`<br>[`Proprietary.py:46`](../../nci_decoder/Nxp_pkg/Proprietary.py#L46) `CORE_SET_POWER_MODE_RSP`<br>[`Proprietary.py:79`](../../nci_decoder/Nxp_pkg/Proprietary.py#L79) `SET_NFC_SERVICE_STATUS_RSP`<br>[`Proprietary.py:106`](../../nci_decoder/Nxp_pkg/Proprietary.py#L106) `NCI_PROPRIETARY_ACT_RSP`<br>[`Proprietary.py:204`](../../nci_decoder/Nxp_pkg/Proprietary.py#L204) `RF_GET_TRANSITION_RSP`<br>[`Proprietary.py:258`](../../nci_decoder/Nxp_pkg/Proprietary.py#L258) `LOW_POWER_TAG_REMOVAL_RSP`<br>[`Proprietary.py:303`](../../nci_decoder/Nxp_pkg/Proprietary.py#L303) `SYSTEM_ESE_POWER_CYCLE_RSP`<br>[`Proprietary.py:335`](../../nci_decoder/Nxp_pkg/Proprietary.py#L335) `COLD_RESET_RSP`<br>[`Proprietary.py:379`](../../nci_decoder/Nxp_pkg/Proprietary.py#L379) `FLUSH_SRAM_AO_TO_FLASH_RSP`<br>[`Proprietary.py:456`](../../nci_decoder/Nxp_pkg/Proprietary.py#L456) `TEST_PRBS_RSP`<br>[`Proprietary.py:508`](../../nci_decoder/Nxp_pkg/Proprietary.py#L508) `READ_OPTION_RSP`<br>[`Proprietary.py:594`](../../nci_decoder/Nxp_pkg/Proprietary.py#L594) `TEST_PRBS_CARD_RSP`<br>[`Proprietary.py:952`](../../nci_decoder/Nxp_pkg/Proprietary.py#L952) `RF_SPC_RSP`<br>[`Proprietary.py:1032`](../../nci_decoder/Nxp_pkg/Proprietary.py#L1032) `TEST_SWP_RSP`<br>[`Proprietary.py:1049`](../../nci_decoder/Nxp_pkg/Proprietary.py#L1049) `TEST_SWP_NTF`<br>[`Proprietary.py:1135`](../../nci_decoder/Nxp_pkg/Proprietary.py#L1135) `OPTIONAL_RSP` |
| 間接使用（經 `Origin.*`） | [`NCI_Core.py:22`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L22) `CORE_RESET_RSP` → [`NCI_Core.CORE_RESET_RSP`](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L22)<br>[`NCI_Core.py:105`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L105) `CORE_INIT_RSP` → [`NCI_Core.CORE_INIT_RSP`](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L97)<br>[`NCI_Core.py:351`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L351) `CORE_CONN_CLOSE_RSP` → [`NCI_Core.CORE_CONN_CLOSE_RSP`](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L498)<br>[`NCI_Core.py:374`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L374) `CORE_GENERIC_ERROR_NTF` → [`NCI_Core.CORE_GENERIC_ERROR_NTF`](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L549)<br>[`NCI_Core.py:384`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L384) `CORE_INTERFACE_ERROR_NTF` → [`NCI_Core.CORE_INTERFACE_ERROR_NTF`](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L565)<br>[`NCI_Core.py:405`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L405) `CORE_SET_POWER_SUB_STATE_RSP` → [`NCI_Core.CORE_SET_POWER_SUB_STATE_RSP`](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L619)<br>[`NFCEE_Management.py:17`](../../nci_decoder/Nxp_pkg/NFCEE_Management.py#L17) `NFCEE_DISCOVER_RSP` → [`NFCEE_Management.NFCEE_DISCOVER_RSP`](../../nci_decoder/nfc_forum_2_0_pkg/NFCEE_Management.py#L19)<br>[`NFCEE_Management.py:58`](../../nci_decoder/Nxp_pkg/NFCEE_Management.py#L58) `NFCEE_MODE_SET_RSP` → [`NFCEE_Management.NFCEE_MODE_SET_RSP`](../../nci_decoder/nfc_forum_2_0_pkg/NFCEE_Management.py#L180)<br>[`NFCEE_Management.py:68`](../../nci_decoder/Nxp_pkg/NFCEE_Management.py#L68) `NFCEE_MODE_SET_NTF` → [`NFCEE_Management.NFCEE_MODE_SET_NTF`](../../nci_decoder/nfc_forum_2_0_pkg/NFCEE_Management.py#L196)<br>[`NFCEE_Management.py:100`](../../nci_decoder/Nxp_pkg/NFCEE_Management.py#L100) `NFCEE_POWER_AND_LINK_CNTRL_RSP` → [`NFCEE_Management.NFCEE_POWER_AND_LINK_CNTRL_RSP`](../../nci_decoder/nfc_forum_2_0_pkg/NFCEE_Management.py#L265)<br>[`RF_Management.py:21`](../../nci_decoder/Nxp_pkg/RF_Management.py#L21) `RF_DISCOVER_MAP_RSP` → [`RF_Management.RF_DISCOVER_MAP_RSP`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L82)<br>[`RF_Management.py:158`](../../nci_decoder/Nxp_pkg/RF_Management.py#L158) `RF_SET_LISTEN_MODE_ROUTING_RSP` → [`RF_Management.RF_SET_LISTEN_MODE_ROUTING_RSP`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L216)<br>[`RF_Management.py:178`](../../nci_decoder/Nxp_pkg/RF_Management.py#L178) `RF_GET_LISTEN_MODE_ROUTING_RSP` → [`RF_Management.RF_GET_LISTEN_MODE_ROUTING_RSP`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L245)<br>[`RF_Management.py:207`](../../nci_decoder/Nxp_pkg/RF_Management.py#L207) `RF_DISCOVER_RSP` → [`RF_Management.RF_DISCOVER_RSP`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L313)<br>[`RF_Management.py:419`](../../nci_decoder/Nxp_pkg/RF_Management.py#L419) `RF_DISCOVER_SELECT_RSP` → [`RF_Management.RF_DISCOVER_SELECT_RSP`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L577)<br>[`RF_Management.py:461`](../../nci_decoder/Nxp_pkg/RF_Management.py#L461) `RF_DEACTIVATE_RSP` → [`RF_Management.RF_DEACTIVATE_RSP`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L691)<br>[`RF_Management.py:502`](../../nci_decoder/Nxp_pkg/RF_Management.py#L502) `RF_T3T_POLLING_RSP` → [`RF_Management.RF_T3T_POLLING_RSP`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L763)<br>[`RF_Management.py:512`](../../nci_decoder/Nxp_pkg/RF_Management.py#L512) `RF_T3T_POLLING_NTF` → [`RF_Management.RF_T3T_POLLING_NTF`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L779)<br>[`RF_Management.py:568`](../../nci_decoder/Nxp_pkg/RF_Management.py#L568) `RF_PARAMETER_UPDATE_RSP` → [`RF_Management.RF_PARAMETER_UPDATE_RSP`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L984)<br>[`RF_Management.py:679`](../../nci_decoder/Nxp_pkg/RF_Management.py#L679) `RF_ISO_DEP_NAK_PRESENCE_RSP` → [`RF_Management.RF_ISO_DEP_NAK_PRESENCE_RSP`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L1170)<br>[`RF_Management.py:689`](../../nci_decoder/Nxp_pkg/RF_Management.py#L689) `RF_ISO_DEP_NAK_PRESENCE_NTF` → [`RF_Management.RF_ISO_DEP_NAK_PRESENCE_NTF`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L1186) |
| 與 nfc_forum_2_0 差異 | **NXP 新增值** — NXP 新增：`E3`、`E4`、`E5`、`E6`、`E7`、`EA`、`ED`、`EE`、`EF`、`F0`、`FA`。其餘值與 nfc_forum_2_0_pkg 相同。 |

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
| `B2` | RF_TIMEOUT_EXCEPTION（註解：'DISCOVERY_TEAR_DOWN'） |
| `B3` | RF_UNEXPECTED_DATA（註解：'DISCOVERY_TEAR_DOWN'） |
| `C0` | NFCEE_INTERFACE_ACTIVATION_FAILED |
| `C1` | NFCEE_TRANSMISSION_ERROR |
| `C2` | NFCEE_PROTOCOL_ERROR |
| `C3` | NFCEE_TIMEOUT_ERROR |
| `E3` | STATUS_PMU_TXLDO_OVERCURRENT |
| `E4` | STATUS_EMVCO_PCD_COLLISION |
| `E5` | STATUS_MININV_AUTOLOAD_FAIL |
| `E6` | STATUS_TRIM_AUTOLOAD_FAIL |
| `E7` | STATUS_GPADC_ERROR |
| `EA` | STATUS_WDG_PAGE_CORRUPTED |
| `ED` | STATUS_CORRUPTED_TRIM |
| `EE` | STATUS_PROTECTED_USER_AREA_CRC_MISMATCH |
| `EF` | STATUS_PROTECTED_MIR_USER_AREA_CRC_MISMATCH |
| `F0` | STATUS_CUSTOMER_AREA_CRC_MISMATCH |
| `FA` | STATUS_HIGH_TEMPERATURE_NFC_ANTENNA |

<a id="tbl_bit_rates"></a>
## tbl_bit_rates

| 項目 | 值 |
|---|---|
| 定義 | [`__table__.py:68`](../../nci_decoder/Nxp_pkg/__table__.py#L68) |
| NCI spec / 來源 | Table 132: Bit Rates |
| `'name'` 鍵 | `Table 132: Bit Rates:`（表內含 `'name'` 鍵，非對照值，下表未列） |
| 直接使用的 handler | [`NCI_Core.py:417`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L417) `VALUE_OF_CFG_PARA`<br>[`Proprietary.py:397`](../../nci_decoder/Nxp_pkg/Proprietary.py#L397) `TEST_PRBS_CMD` |
| 間接使用（經 `Origin.*`） | [`RF_Management.py:429`](../../nci_decoder/Nxp_pkg/RF_Management.py#L429) `RF_INTF_ACTIVATED_NTF` → [`RF_Management.RF_INTF_ACTIVATED_NTF`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L593)<br>[`RF_Management.py:553`](../../nci_decoder/Nxp_pkg/RF_Management.py#L553) `RF_PARAMETER_UPDATE_CMD` → [`RF_Management.RF_PARAMETER_UPDATE_CMD`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L919) |
| 與 nfc_forum_2_0 差異 | **有差異** — NXP 新增：`80`；NXP 缺少（forum 有）：`80-FE`=`For proprietary use`。 |

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
| `80` | 212 Kbit/s & 424 Kbit/s（註解：SN2x0） |

<a id="tbl_rf_proto"></a>
## tbl_rf_proto

| 項目 | 值 |
|---|---|
| 定義 | [`__table__.py:82`](../../nci_decoder/Nxp_pkg/__table__.py#L82) |
| NCI spec / 來源 | Table 133: RF Protocols |
| `'name'` 鍵 | `Table 133: RF Protocols:`（表內含 `'name'` 鍵，非對照值，下表未列） |
| 直接使用的 handler | （Nxp_pkg 中無 `NFC_table.tbl_rf_proto` 直接引用） |
| 間接使用（經 `Origin.*`） | [`NCI_Core.py:292`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L292) `CORE_CONN_CREATE_CMD` → [`NCI_Core.CORE_CONN_CREATE_CMD`](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L378)<br>[`RF_Management.py:7`](../../nci_decoder/Nxp_pkg/RF_Management.py#L7) `RF_DISCOVER_MAP_CMD` → [`RF_Management.RF_DISCOVER_MAP_CMD`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L42)<br>[`RF_Management.py:152`](../../nci_decoder/Nxp_pkg/RF_Management.py#L152) `RF_SET_LISTEN_MODE_ROUTING_CMD` → [`RF_Management.RF_SET_LISTEN_MODE_ROUTING_CMD`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L209)<br>[`RF_Management.py:188`](../../nci_decoder/Nxp_pkg/RF_Management.py#L188) `RF_GET_LISTEN_MODE_ROUTING_NTF` → [`RF_Management.RF_GET_LISTEN_MODE_ROUTING_NTF`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L261)<br>[`RF_Management.py:392`](../../nci_decoder/Nxp_pkg/RF_Management.py#L392) `RF_DISCOVER_NTF` → [`RF_Management.RF_DISCOVER_NTF`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L502)<br>[`RF_Management.py:407`](../../nci_decoder/Nxp_pkg/RF_Management.py#L407) `RF_DISCOVER_SELECT_CMD` → [`RF_Management.RF_DISCOVER_SELECT_CMD`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L551)<br>[`RF_Management.py:429`](../../nci_decoder/Nxp_pkg/RF_Management.py#L429) `RF_INTF_ACTIVATED_NTF` → [`RF_Management.RF_INTF_ACTIVATED_NTF`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L593)<br>[`RF_Management.py:526`](../../nci_decoder/Nxp_pkg/RF_Management.py#L526) `RF_NFCEE_ACTION_NTF` → [`RF_Management.RF_NFCEE_ACTION_NTF`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L819)<br>[`RF_Management.py:539`](../../nci_decoder/Nxp_pkg/RF_Management.py#L539) `RF_NFCEE_DISCOVERY_REQ_NTF` → [`RF_Management.RF_NFCEE_DISCOVERY_REQ_NTF`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L868) |
| 與 nfc_forum_2_0 差異 | **有差異** — NXP 新增：`80`；NXP 缺少（forum 有）：`80-FE`=`For proprietary use`。 |

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
| `80` | MIFARE_CLASSIC（註解：SN2x0） |

<a id="tbl_nfcee_proto"></a>
## tbl_nfcee_proto

| 項目 | 值 |
|---|---|
| 定義 | [`__table__.py:96`](../../nci_decoder/Nxp_pkg/__table__.py#L96) |
| NCI spec / 來源 | Table 136: NFCEE Protocols / Interfaces |
| `'name'` 鍵 | `Table 136: NFCEE Protocols / Interfaces:`（表內含 `'name'` 鍵，非對照值，下表未列） |
| 直接使用的 handler | （Nxp_pkg 中無 `NFC_table.tbl_nfcee_proto` 直接引用） |
| 間接使用（經 `Origin.*`） | [`NCI_Core.py:292`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L292) `CORE_CONN_CREATE_CMD` → [`NCI_Core.CORE_CONN_CREATE_CMD`](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L378)<br>[`NFCEE_Management.py:28`](../../nci_decoder/Nxp_pkg/NFCEE_Management.py#L28) `NFCEE_DISCOVER_NTF` → [`NFCEE_Management.NFCEE_DISCOVER_NTF`](../../nci_decoder/nfc_forum_2_0_pkg/NFCEE_Management.py#L41) |
| 與 nfc_forum_2_0 差異 | **相同** — 與 nfc_forum_2_0_pkg 同名表內容完全相同。 |

| 值 (hex) | 意義 |
|---|---|
| `00` | APDU |
| `01` | RFU |
| `02` | Type 3 Tag Command Set |
| `03` | Transparent |
| `04-7F` | RFU |
| `80-FE` | For proprietary use |
| `FF` | RFU |

<a id="tbl_nfcee_id"></a>
## tbl_nfcee_id

| 項目 | 值 |
|---|---|
| 定義 | [`__table__.py:108`](../../nci_decoder/Nxp_pkg/__table__.py#L108) |
| NCI spec / 來源 | Table 116: NFCEE IDs |
| `'name'` 鍵 | `Table 116: NFCEE IDs:`（表內含 `'name'` 鍵，非對照值，下表未列） |
| 直接使用的 handler | （Nxp_pkg 中無 `NFC_table.tbl_nfcee_id` 直接引用） |
| 間接使用（經 `Origin.*`） | [`NFCEE_Management.py:28`](../../nci_decoder/Nxp_pkg/NFCEE_Management.py#L28) `NFCEE_DISCOVER_NTF` → [`NFCEE_Management.NFCEE_DISCOVER_NTF`](../../nci_decoder/nfc_forum_2_0_pkg/NFCEE_Management.py#L41)<br>[`NFCEE_Management.py:47`](../../nci_decoder/Nxp_pkg/NFCEE_Management.py#L47) `NFCEE_MODE_SET_CMD` → [`NFCEE_Management.NFCEE_MODE_SET_CMD`](../../nci_decoder/nfc_forum_2_0_pkg/NFCEE_Management.py#L153)<br>[`NFCEE_Management.py:78`](../../nci_decoder/Nxp_pkg/NFCEE_Management.py#L78) `NFCEE_STATUS_NTF` → [`NFCEE_Management.NFCEE_STATUS_NTF`](../../nci_decoder/nfc_forum_2_0_pkg/NFCEE_Management.py#L212)<br>[`NFCEE_Management.py:89`](../../nci_decoder/Nxp_pkg/NFCEE_Management.py#L89) `NFCEE_POWER_AND_LINK_CNTRL_CMD` → [`NFCEE_Management.NFCEE_POWER_AND_LINK_CNTRL_CMD`](../../nci_decoder/nfc_forum_2_0_pkg/NFCEE_Management.py#L234)<br>[`RF_Management.py:152`](../../nci_decoder/Nxp_pkg/RF_Management.py#L152) `RF_SET_LISTEN_MODE_ROUTING_CMD` → [`RF_Management.RF_SET_LISTEN_MODE_ROUTING_CMD`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L209)<br>[`RF_Management.py:188`](../../nci_decoder/Nxp_pkg/RF_Management.py#L188) `RF_GET_LISTEN_MODE_ROUTING_NTF` → [`RF_Management.RF_GET_LISTEN_MODE_ROUTING_NTF`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L261)<br>[`RF_Management.py:526`](../../nci_decoder/Nxp_pkg/RF_Management.py#L526) `RF_NFCEE_ACTION_NTF` → [`RF_Management.RF_NFCEE_ACTION_NTF`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L819)<br>[`RF_Management.py:539`](../../nci_decoder/Nxp_pkg/RF_Management.py#L539) `RF_NFCEE_DISCOVERY_REQ_NTF` → [`RF_Management.RF_NFCEE_DISCOVERY_REQ_NTF`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L868) |
| 與 nfc_forum_2_0 差異 | **NXP 新增值** — NXP 新增：`10`、`80`、`81`、`C0`、`C1`、`C2`。其餘值與 nfc_forum_2_0_pkg 相同。 |

| 值 (hex) | 意義 |
|---|---|
| `00` | DH-NFCEE |
| `01` | HCI-NTWK-NFCEE (RFU) |
| `02-0F` | (Static IDs) |
| `10-7F` | (NFCEE) |
| `80-FE` | (HCI-NFCEE) |
| `FF` | (RFU) |
| `10` | NFCEE_NDEF |
| `80` | NFCEE_UICC1 |
| `81` | NFCEE_UICC2 |
| `C0` | NFCEE_eSE |
| `C1` | NFCEE_eUICC Profile 1 (SEP/MEP Mode) |
| `C2` | NFCEE_eUICC Profile 2 (MEP Mode) |

<a id="tbl_rf_if"></a>
## tbl_rf_if

| 項目 | 值 |
|---|---|
| 定義 | [`__table__.py:126`](../../nci_decoder/Nxp_pkg/__table__.py#L126) |
| NCI spec / 來源 | Table 134: RF Interfaces |
| `'name'` 鍵 | `Table 134: RF Interfaces:`（表內含 `'name'` 鍵，非對照值，下表未列） |
| 直接使用的 handler | （Nxp_pkg 中無 `NFC_table.tbl_rf_if` 直接引用） |
| 間接使用（經 `Origin.*`） | [`NCI_Core.py:105`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L105) `CORE_INIT_RSP` → [`NCI_Core.CORE_INIT_RSP`](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L97)<br>[`RF_Management.py:7`](../../nci_decoder/Nxp_pkg/RF_Management.py#L7) `RF_DISCOVER_MAP_CMD` → [`RF_Management.RF_DISCOVER_MAP_CMD`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L42)<br>[`RF_Management.py:407`](../../nci_decoder/Nxp_pkg/RF_Management.py#L407) `RF_DISCOVER_SELECT_CMD` → [`RF_Management.RF_DISCOVER_SELECT_CMD`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L551)<br>[`RF_Management.py:429`](../../nci_decoder/Nxp_pkg/RF_Management.py#L429) `RF_INTF_ACTIVATED_NTF` → [`RF_Management.RF_INTF_ACTIVATED_NTF`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L593) |
| 與 nfc_forum_2_0 差異 | **有差異** — NXP 新增：`80`、`81`、`83`；NXP 缺少（forum 有）：`80-FE`=`For proprietary use`。 |

| 值 (hex) | 意義 |
|---|---|
| `00` | NFCEE Direct |
| `01` | Frame |
| `02` | ISO-DEP |
| `03` | NFC-DEP |
| `06` | NDEF |
| `80` | TAG-CMD（註解：SN2x0） |
| `81` | WLC_RF（註解：SN2x0 WireLess Charging） |
| `83` | NFCEE_DEP_RF_eSE（註解：SN2x0） |

<a id="tbl_rf_if_exten"></a>
## tbl_rf_if_exten

| 項目 | 值 |
|---|---|
| 定義 | [`__table__.py:139`](../../nci_decoder/Nxp_pkg/__table__.py#L139) |
| NCI spec / 來源 | Table 135: RF Interface Extensions |
| `'name'` 鍵 | `Table 135: RF Interface Extensions:`（表內含 `'name'` 鍵，非對照值，下表未列） |
| 直接使用的 handler | （Nxp_pkg 中無 `NFC_table.tbl_rf_if_exten` 直接引用） |
| 間接使用（經 `Origin.*`） | [`NCI_Core.py:105`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L105) `CORE_INIT_RSP` → [`NCI_Core.CORE_INIT_RSP`](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L97) |
| 與 nfc_forum_2_0 差異 | **相同** — 與 nfc_forum_2_0_pkg 同名表內容完全相同。 |

| 值 (hex) | 意義 |
|---|---|
| `00` | Frame Aggregated RF Interface Extension |
| `01` | LLCP Symmetry RF Interface Extension |

<a id="tbl_conn_id"></a>
## tbl_conn_id

| 項目 | 值 |
|---|---|
| 定義 | [`__table__.py:152`](../../nci_decoder/Nxp_pkg/__table__.py#L152) |
| NCI spec / 來源 | Table 4: Conn ID |
| `'name'` 鍵 | `Table 4: Conn ID`（表內含 `'name'` 鍵，非對照值，下表未列） |
| 直接使用的 handler | [`NCI_Core.py:307`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L307) `CORE_CONN_CREATE_RSP` |
| 間接使用（經 `Origin.*`） | [`NCI_Core.py:341`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L341) `CORE_CONN_CLOSE_CMD` → [`NCI_Core.CORE_CONN_CLOSE_CMD`](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L482)<br>[`NCI_Core.py:361`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L361) `CORE_CONN_CREDITS_NTF` → [`NCI_Core.CORE_CONN_CREDITS_NTF`](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L514)<br>[`NCI_Core.py:384`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L384) `CORE_INTERFACE_ERROR_NTF` → [`NCI_Core.CORE_INTERFACE_ERROR_NTF`](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L565) |
| 與 nfc_forum_2_0 差異 | **相同** — 與 nfc_forum_2_0_pkg 同名表內容完全相同。 |

| 值 (hex) | 意義 |
|---|---|
| `0000` | Static: DH -- Remote NFC Endpoint |
| `0001` | Static: DH -- HCI Network |
| `0010-1111` | Dynamically assigned |

<a id="tbl_rst_trig"></a>
## tbl_rst_trig

| 項目 | 值 |
|---|---|
| 定義 | [`__table__.py:165`](../../nci_decoder/Nxp_pkg/__table__.py#L165) |
| NCI spec / 來源 | Table 5: Control Messages to Reset the NFCC |
| `'name'` 鍵 | `Table 5: Control Messages to Reset the NFCC:`（表內含 `'name'` 鍵，非對照值，下表未列） |
| 直接使用的 handler | [`NCI_Core.py:32`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L32) `CORE_RESET_NTF` |
| 間接使用（經 `Origin.*`） | — |
| 與 nfc_forum_2_0 差異 | **NXP 新增值** — NXP 新增：`A0`、`A1`、`A3`、`A4`、`A5`、`A6`、`A7`。其餘值與 nfc_forum_2_0_pkg 相同。 |

| 值 (hex) | 意義 |
|---|---|
| `00` | Unrecoverable error occurred in the NFCC |
| `01` | NFCC was powered on |
| `02` | CORE_RESET_CMD |
| `A0` | An assert has triggered SN2x0 NFCC reset/reboot |
| `A1` | An over temperature has triggered the reset of SN2x0 NFCC |
| `A3` | The watchdog has triggered SN2x0 NFCC reset/reboot |
| `A4` | External Clock Input has been lost and triggered a protection |
| `A5` | RFU |
| `A6` | Unexpected boot sequence detected (eg RSTN pulse too short) |
| `A7` | Unexpected boot reason reported by hw |

<a id="tbl_nci_ver"></a>
## tbl_nci_ver

| 項目 | 值 |
|---|---|
| 定義 | [`__table__.py:181`](../../nci_decoder/Nxp_pkg/__table__.py#L181) |
| NCI spec / 來源 | Table 6: NCI Version |
| `'name'` 鍵 | `Table 6: NCI Version:`（表內含 `'name'` 鍵，非對照值，下表未列） |
| 直接使用的 handler | [`NCI_Core.py:32`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L32) `CORE_RESET_NTF` |
| 間接使用（經 `Origin.*`） | — |
| 與 nfc_forum_2_0 差異 | **相同** — 與 nfc_forum_2_0_pkg 同名表內容完全相同。 |

| 值 (hex) | 意義 |
|---|---|
| `10` | 1.0 |
| `11` | 1.1 |
| `20` | 2.0 |

<a id="tbl_cfg_status"></a>
## tbl_cfg_status

| 項目 | 值 |
|---|---|
| 定義 | [`__table__.py:189`](../../nci_decoder/Nxp_pkg/__table__.py#L189) |
| NCI spec / 來源 | Table 7: Configuration Status |
| `'name'` 鍵 | `Table 7: Configuration Status:`（表內含 `'name'` 鍵，非對照值，下表未列） |
| 直接使用的 handler | [`NCI_Core.py:32`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L32) `CORE_RESET_NTF` |
| 間接使用（經 `Origin.*`） | [`NCI_Core.py:12`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L12) `CORE_RESET_CMD` → [`NCI_Core.CORE_RESET_CMD`](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L6) |
| 與 nfc_forum_2_0 差異 | **相同** — 與 nfc_forum_2_0_pkg 同名表內容完全相同。 |

| 值 (hex) | 意義 |
|---|---|
| `00` | Keep Config（註解：Reset the NFCC and keep the NCI RF Configuration (if supported).） |
| `01` | Reset Config（註解：Reset the NFCC including the NCI RF Configuration.） |

<a id="tbl_nfcc_feat_oct1"></a>
## tbl_nfcc_feat_oct1

| 項目 | 值 |
|---|---|
| 定義 | [`__table__.py:196`](../../nci_decoder/Nxp_pkg/__table__.py#L196) |
| NCI spec / 來源 | Table 10: NFCC Features（程式註解：Table 10: NFCC Features (Octet 1)） |
| `'name'` 鍵 | `Table 10: NFCC Features:`（表內含 `'name'` 鍵，非對照值，下表未列） |
| 直接使用的 handler | （Nxp_pkg 中無 `NFC_table.tbl_nfcc_feat_oct1` 直接引用） |
| 間接使用（經 `Origin.*`） | [`NCI_Core.py:105`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L105) `CORE_INIT_RSP` → [`NCI_Core.CORE_INIT_RSP`](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L97) |
| 與 nfc_forum_2_0 差異 | **相同** — 與 nfc_forum_2_0_pkg 同名表內容完全相同。 |

| Bit | 意義 |
|---|---|
| bit 6 | Forced NFCEE routing |
| bit 5 | APDU Pattern based routing |
| bit 4 | System Code based routing |
| bit 3 | AID based routing |
| bit 2 | Protocol based routing |
| bit 1 | Technology based routing |

<a id="tbl_nfcc_feat_oct2"></a>
## tbl_nfcc_feat_oct2

| 項目 | 值 |
|---|---|
| 定義 | [`__table__.py:207`](../../nci_decoder/Nxp_pkg/__table__.py#L207) |
| NCI spec / 來源 | Table 10: NFCC Features（程式註解：Table 10: NFCC Features (Octet 2)） |
| `'name'` 鍵 | `Table 10: NFCC Features:`（表內含 `'name'` 鍵，非對照值，下表未列） |
| 直接使用的 handler | （Nxp_pkg 中無 `NFC_table.tbl_nfcc_feat_oct2` 直接引用） |
| 間接使用（經 `Origin.*`） | [`NCI_Core.py:105`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L105) `CORE_INIT_RSP` → [`NCI_Core.CORE_INIT_RSP`](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L97) |
| 與 nfc_forum_2_0 差異 | **相同** — 與 nfc_forum_2_0_pkg 同名表內容完全相同。 |

| Bit | 意義 |
|---|---|
| bit 3 | RF Cfg in Switched Off State |
| bit 2 | Switched On Sub-Mode States |
| bit 1 | Switched Off State |
| bit 0 | Battery Off State |

<a id="tbl_dest_type"></a>
## tbl_dest_type

| 項目 | 值 |
|---|---|
| 定義 | [`__table__.py:216`](../../nci_decoder/Nxp_pkg/__table__.py#L216) |
| NCI spec / 來源 | Table 13: Destination Types |
| `'name'` 鍵 | `Table 13: Destination Types:`（表內含 `'name'` 鍵，非對照值，下表未列） |
| 直接使用的 handler | （Nxp_pkg 中無 `NFC_table.tbl_dest_type` 直接引用） |
| 間接使用（經 `Origin.*`） | [`NCI_Core.py:292`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L292) `CORE_CONN_CREATE_CMD` → [`NCI_Core.CORE_CONN_CREATE_CMD`](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L378) |
| 與 nfc_forum_2_0 差異 | **相同** — 與 nfc_forum_2_0_pkg 同名表內容完全相同。 |

| 值 (hex) | 意義 |
|---|---|
| `01` | NFCC Loopback |
| `02` | Remote NFC Endpoint |
| `03` | NFCEE |

<a id="tbl_init_credits"></a>
## tbl_init_credits

| 項目 | 值 |
|---|---|
| 定義 | [`__table__.py:224`](../../nci_decoder/Nxp_pkg/__table__.py#L224) |
| NCI spec / 來源 | Table 15: Initial Number of Credits |
| `'name'` 鍵 | `Table 15: Initial Number of Credits:`（表內含 `'name'` 鍵，非對照值，下表未列） |
| 直接使用的 handler | [`NCI_Core.py:307`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L307) `CORE_CONN_CREATE_RSP` |
| 間接使用（經 `Origin.*`） | — |
| 與 nfc_forum_2_0 差異 | **相同** — 與 nfc_forum_2_0_pkg 同名表內容完全相同。 |

| 值 (hex) | 意義 |
|---|---|
| `FF` | Data flow control is not used |

<a id="tbl_d_spec_type"></a>
## tbl_d_spec_type

| 項目 | 值 |
|---|---|
| 定義 | [`__table__.py:230`](../../nci_decoder/Nxp_pkg/__table__.py#L230) |
| NCI spec / 來源 | Table 16: Destination-specific Parameters |
| `'name'` 鍵 | `Table 16: Destination-specific Parameters:`（表內含 `'name'` 鍵，非對照值，下表未列） |
| 直接使用的 handler | （Nxp_pkg 中無 `NFC_table.tbl_d_spec_type` 直接引用） |
| 間接使用（經 `Origin.*`） | [`NCI_Core.py:292`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L292) `CORE_CONN_CREATE_CMD` → [`NCI_Core.CORE_CONN_CREATE_CMD`](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L378) |
| 與 nfc_forum_2_0 差異 | **相同** — 與 nfc_forum_2_0_pkg 同名表內容完全相同。 |

| 值 (hex) | 意義 |
|---|---|
| `00` | RF Discovery ID + RF Protocol |
| `01` | NFCEE ID + NFCEE Interface Protocol |

<a id="tbl_cfg_para"></a>
## tbl_cfg_para

| 項目 | 值 |
|---|---|
| 定義 | [`__table__.py:237`](../../nci_decoder/Nxp_pkg/__table__.py#L237) |
| NCI spec / 來源 | Table 138: Configuration Parameter Tags |
| `'name'` 鍵 | `Table 138: Configuration Parameter Tags:`（表內含 `'name'` 鍵，非對照值，下表未列） |
| 直接使用的 handler | [`NCI_Core.py:127`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L127) `CORE_SET_CONFIG_CMD`<br>[`NCI_Core.py:177`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L177) `CORE_SET_CONFIG_RSP`<br>[`NCI_Core.py:208`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L208) `CORE_GET_CONFIG_CMD`<br>[`NCI_Core.py:237`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L237) `CORE_GET_CONFIG_RSP` |
| 間接使用（經 `Origin.*`） | — |
| 與 nfc_forum_2_0 差異 | **有差異** — NXP 新增：`A001`、`A015`、`A00A`、`A010`、`A011`、`A00E`、`A007`、`A08E`、`A009`、`A01D`、`A00F`、`A0FB`、`A064`、`A044`、`A04D`、`A04E`、`A04F`、`A050`、`A051`、`A052`、`A053`、`A054`、`A055`、`A056`、`A057`、`A058`、`A059`、`A05A`、`A05B`、`A05C`、`A05D`、`A106`、`A148`、`A14B`、`A080`、`A062`、`A085`、`A10E`、`A095`、`A110`、`A10B`、`A10F`、`A096`、`A111`、`A086`、`A087`、`A11B`、`A136`、`A155`、`A158`、`A0C0`、`A0CB`、`A0EC`、`A0F1`、`A0D1`、`A0D3`、`A0D4`、`A0F8`、`A0C5`、`A11C`、`A0B8`、`A0ED`、`A0F9`、`A08A`、`A08C`、`A08D`、`A089`、`A08B`、`A082`、`A094`、`A084`、`A0EA`、`A01E`、`A0EB`、`A0EF`、`A0E8`、`A0F0`、`A11A`、`A022`、`A023`、`A024`、`A025`、`A0E9`、`A012`、`A017`、`A068`、`A149`、`A034`、`A10A`、`A00B`、`A00D`、`A09E`、`A17E`、`A12E`、`A196`、`A06A`、`A0A4`、`A0A5`、`A0AF`、`A0A7`、`A0A8`、`A098`、`A0AB`、`A0A9`；NXP 缺少（forum 有）：`01`=`RFU`、`03`=`POWER_STATE`、`04-07`=`RFU`、`0A-0F`=`RFU`、`15-17`=`RFU`、`1B-1F`=`RFU`、`22-27`=`RFU`、`2B-2E`=`RFU`、`34-37`=`RFU`、`3D`=`RFU`、`3F`=`RFU`、`51`=`RFU`、`54`=`RFU`、`56-57`=`RFU`、`5D-5F`=`RFU`、`63-67`=`RFU`、`69-7F`=`RFU`、`84`=`RFU`、`86-9F`=`RFU`。 |

| 值 (hex) | 意義 |
|---|---|
| `00` | TOTAL_DURATION |
| `02` | CON_DISCOVERY_PARAM |
| `08` | PA_BAIL_OUT |
| `09` | PA_DEVICES_LIMIT |
| `10` | PB_AFI |
| `11` | PB_BAIL_OUT |
| `12` | PB_ATTRIB_PARAM1 |
| `13` | PB_SENSB_REQ_PARAM |
| `14` | PB_DEVICES_LIMIT |
| `18` | PF_BIT_RATE |
| `19` | PF_BAIL_OUT |
| `1A` | PF_DEVICES_LIMIT |
| `20` | PI_B_H_INFO |
| `21` | PI_BIT_RATE |
| `28` | PN_NFC_DEP_PSL |
| `29` | PN_ATR_REQ_GEN_BYTES |
| `2A` | PN_ATR_REQ_CONFIG |
| `2F` | PV_DEVICES_LIMIT |
| `30` | LA_BIT_FRAME_SDD |
| `31` | LA_PLATFORM_CONFIG |
| `32` | LA_SEL_INFO |
| `33` | LA_NFCID1 |
| `38` | LB_SENSB_INFO |
| `39` | LB_NFCID0 |
| `3A` | LB_APPLICATION_DATA |
| `3B` | LB_SFGI |
| `3C` | LB_FWI_ADC_FO |
| `3E` | LB_BIT_RATE |
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
| `52` | LF_T3T_MAX |
| `53` | LF_T3T_FLAGS |
| `55` | LF_T3T_RD_ALLOWED |
| `50` | LF_PROTOCOL_TYPE |
| `58` | LI_A_RATS_TB1 |
| `59` | LI_A_HIST_BY |
| `5A` | LI_B_H_INFO_RESP |
| `5B` | LI_A_BIT_RATE |
| `5C` | LI_A_RATS_TC1 |
| `60` | LN_WT |
| `61` | LN_ATR_RES_GEN_BYTES |
| `62` | LN_ATR_RES_CONFIG |
| `68` | PACM_BIT_RATE |
| `80` | RF_FIELD_INFO |
| `81` | RF_NFCEE_ACTION |
| `82` | NFCDEP_OP |
| `83` | LLCP_VERSION |
| `85` | NFCC_CONFIG_CONTROL |
| `A0-FE` | Reserved |
| `FF` | RFU |
| `A001` | NFCC_DIE_ID |
| `A015` | DEFAULT_POWER |
| `A00A` | WAIT_FOR_STABLE_SYSCLOCK |
| `A010` | CLKGEN |
| `A011` | RF_CLOCK_CFG |
| `A00E` | PMU_CFG |
| `A007` | RSTN_CFG |
| `A08E` | PHONE_OFF_ALLOWED |
| `A009` | TO_BEFORE_STDBY_CFG |
| `A01D` | Lx_DEBUG_CFG |
| `A00F` | MW_AREA |
| `A0FB` | HW_RESET_NTF |
| `A064` | EMVCo_PCD_SETTINGS |
| `A044` | POLL_PROFILE_SEL_CFG |
| `A04D` | MFC_KEY-0_CFG |
| `A04E` | MFC_KEY-1_CFG |
| `A04F` | MFC_KEY-2_CFG |
| `A050` | MFC_KEY-3_CFG |
| `A051` | MFC_KEY-4_CFG |
| `A052` | MFC_KEY-5_CFG |
| `A053` | MFC_KEY-6_CFG |
| `A054` | MFC_KEY-7_CFG |
| `A055` | MFC_KEY-8_CFG |
| `A056` | MFC_KEY-9_CFG |
| `A057` | MFC_KEY-10_CFG |
| `A058` | MFC_KEY-11_CFG |
| `A059` | MFC_KEY-12_CFG |
| `A05A` | MFC_KEY-13_CFG |
| `A05B` | MFC_KEY-14_CFG |
| `A05C` | MFC_KEY-15_CFG |
| `A05D` | FSDI_CFG |
| `A106` | LPCD_FPC |
| `A148` | RF_PATTERN_CHK |
| `A14B` | PLL_FREQ_CHECK |
| `A080` | TO_RF_OFF_CFG |
| `A062` | SLOW_HOST_CFG |
| `A085` | RF_MISC_SETTINGS |
| `A10E` | GUARD_TIMEOUT_Tx2Rx |
| `A095` | NDEF_NFCEE |
| `A110` | NDEF_NFCEE_CFG2 |
| `A10B` | AUTONOMOUS_START_TIMEOUT |
| `A10F` | ULPDET_CFG |
| `A096` | NOTIFY_ALL_AID |
| `A111` | NOTIFY_ALL_FID |
| `A086` | RF_BITRATE_LIMIT_A_CFG |
| `A087` | RF_BITRATE_LIMIT_B_CFG |
| `A11B` | MERGE_SAK |
| `A136` | AUTOMATIC_CARD_SELECTION |
| `A155` | RSSI_CONTINUOUS_NTF |
| `A158` | NFCLD_THRESHOLD_FIELD_DETECT |
| `A0C0` | SWP_BITRATE_UICC1 |
| `A0CB` | SWP_TS1_HIGHV_UICC1 |
| `A0EC` | SWP_UICC1_IF_EN_CFG |
| `A0F1` | SWP_UICC1_SPECIAL_PWR_MODE_CFG |
| `A0D1` | SWP_BITRATE_UICC2 |
| `A0D3` | SWP_TS1_HIGHV_UICC2 |
| `A0D4` | SWP_UICC2_IF_EN_CFG |
| `A0F8` | SWP_UICC2_SPECIAL_PWR_MODE_CFG |
| `A0C5` | SWP_UICC1_ACT_RSET_WAIT |
| `A11C` | SWP_EXT_RESUME |
| `A0B8` | SE_APDU_LOGGING_EN_CFG |
| `A0ED` | NFCEE_eSE_IF_EN_CFG |
| `A0F9` | SE_COLD_RESET_NTF |
| `A08A` | SE_POWER_ON_TO_WAKE_UP_GUARD_TIME |
| `A08C` | SE_POWER_OFF_TO_SW_RESET_DELAY_TIME |
| `A08D` | WAKE_UP_SE_TO_ACT_FRAME_DELAY_TIME |
| `A089` | ACT_RESPONSE_GUARD_TIME |
| `A08B` | CLT_F_TIMEOUT |
| `A082` | CLT_A_TIMEOUT |
| `A094` | SE_TEMP_ERROR_DELAY_TIME |
| `A084` | VBAT_THRESHOLD_PHONE_OFF |
| `A0EA` | UICC1_SESSIONID |
| `A01E` | UICC2_SESSIONID |
| `A0EB` | eSE_SESSIONID |
| `A0EF` | RF_PARAM_CE_UICC1 |
| `A0E8` | RF_PARAM_CE_UICC2 |
| `A0F0` | RF_PARAM_CE_eSE |
| `A11A` | PHONEOFF_TECH_CFG |
| `A022` | HCI pipe status of Connectivity gate for NFCEE_eSE |
| `A023` | HCI pipe status of APDU gate for NFCEE_eSE |
| `A024` | HCI pipe status of connectivity gate for NFCEE_UICC1 |
| `A025` | HCI pipe status of APDU gate for NFCEE_UICC1 |
| `A0E9` | HCI pipe status of connectivity gate for NFCEE_UICC2 |
| `A012` | HCI pipe status of APDU gate for NFCEE_eUICC |
| `A017` | RF_CUST_PHAS E_COMPENSATI ON |
| `A068` | RF_LPCD_CFG |
| `A149` | RF_ADV_LPCD_CFG |
| `A034` | RF_DLMA_CFG |
| `A10A` | RF_DLMA_CLOCK_LESS_CEF_CFG |
| `A00B` | RF_DPC_CFG |
| `A00D` | RF_TRANSITION_CFG |
| `A09E` | RX_CTRL_CFG |
| `A17E` | ADVANCED_HYBRID_LPCD_CFG |
| `A12E` | FDT_CFG |
| `A196` | GPIO_SELECTION |
| `A06A` | RF_CLK_PLL_DPLL3 |
| `A0A4` | HFatt. Phase Correction |
| `A0A5` | HF attenuator phase correction |
| `A0AF` | DLMA_CTRL |
| `A0A7` | RM_GLOBAL_TX_SHAPING |
| `A0A8` | RM_TECHNO_TX_SHAPING |
| `A098` | MEASURED_LMA_RSSI |
| `A0AB` | RSSI_GAIN |
| `A0A9` | DLMA_TX |

<a id="tbl_rf_field_status"></a>
## tbl_rf_field_status

| 項目 | 值 |
|---|---|
| 定義 | [`__table__.py:451`](../../nci_decoder/Nxp_pkg/__table__.py#L451) |
| NCI spec / 來源 | Table 22: RF Field Status |
| `'name'` 鍵 | `Table 22: RF Field Status:`（表內含 `'name'` 鍵，非對照值，下表未列） |
| 直接使用的 handler | （Nxp_pkg 中無 `NFC_table.tbl_rf_field_status` 直接引用） |
| 間接使用（經 `Origin.*`） | [`RF_Management.py:482`](../../nci_decoder/Nxp_pkg/RF_Management.py#L482) `RF_FIELD_INFO_NTF` → [`RF_Management.RF_FIELD_INFO_NTF`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L728) |
| 與 nfc_forum_2_0 差異 | **相同** — 與 nfc_forum_2_0_pkg 同名表內容完全相同。 |

| 值 (hex) | 意義 |
|---|---|
| `00` | No Operating field generated by Remote NFC Endpoint. |
| `01` | Operating field generated by Remote NFC Endpoint. |

<a id="tbl_mode"></a>
## tbl_mode

| 項目 | 值 |
|---|---|
| 定義 | [`__table__.py:458`](../../nci_decoder/Nxp_pkg/__table__.py#L458) |
| NCI spec / 來源 | Table 49: Value Field for Mode |
| `'name'` 鍵 | `Table 49: Value Field for Mode:`（表內含 `'name'` 鍵，非對照值，下表未列） |
| 直接使用的 handler | （Nxp_pkg 中無 `NFC_table.tbl_mode` 直接引用） |
| 間接使用（經 `Origin.*`） | [`RF_Management.py:7`](../../nci_decoder/Nxp_pkg/RF_Management.py#L7) `RF_DISCOVER_MAP_CMD` → [`RF_Management.RF_DISCOVER_MAP_CMD`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L42) |
| 與 nfc_forum_2_0 差異 | **相同** — 與 nfc_forum_2_0_pkg 同名表內容完全相同。 |

| 值 (hex) | 意義 |
|---|---|
| `00` | Error |
| `01` | Polling |
| `02` | Listen |
| `03` | Listen/Polling |

<a id="tbl_more"></a>
## tbl_more

| 項目 | 值 |
|---|---|
| 定義 | [`__table__.py:467`](../../nci_decoder/Nxp_pkg/__table__.py#L467) |
| NCI spec / 來源 | Table 51: More field values |
| `'name'` 鍵 | `Table 51: More field values:`（表內含 `'name'` 鍵，非對照值，下表未列） |
| 直接使用的 handler | （Nxp_pkg 中無 `NFC_table.tbl_more` 直接引用） |
| 間接使用（經 `Origin.*`） | [`RF_Management.py:152`](../../nci_decoder/Nxp_pkg/RF_Management.py#L152) `RF_SET_LISTEN_MODE_ROUTING_CMD` → [`RF_Management.RF_SET_LISTEN_MODE_ROUTING_CMD`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L209)<br>[`RF_Management.py:188`](../../nci_decoder/Nxp_pkg/RF_Management.py#L188) `RF_GET_LISTEN_MODE_ROUTING_NTF` → [`RF_Management.RF_GET_LISTEN_MODE_ROUTING_NTF`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L261) |
| 與 nfc_forum_2_0 差異 | **相同** — 與 nfc_forum_2_0_pkg 同名表內容完全相同。 |

| 值 (hex) | 意義 |
|---|---|
| `00` | Last Message |
| `01` | More Message(s) to follow |

<a id="tbl_l_mode_routing_entry_type"></a><a id="tbl_L_mode_routing_entry_type"></a>
## tbl_L_mode_routing_entry_type

| 項目 | 值 |
|---|---|
| 定義 | [`__table__.py:484`](../../nci_decoder/Nxp_pkg/__table__.py#L484) |
| NCI spec / 來源 | Table 53: Listen Mode Routing Entry Types |
| `'name'` 鍵 | `Table 53: Listen Mode Routing Entry Types:`（表內含 `'name'` 鍵，非對照值，下表未列） |
| 直接使用的 handler | （Nxp_pkg 中無 `NFC_table.tbl_L_mode_routing_entry_type` 直接引用） |
| 間接使用（經 `Origin.*`） | [`RF_Management.py:152`](../../nci_decoder/Nxp_pkg/RF_Management.py#L152) `RF_SET_LISTEN_MODE_ROUTING_CMD` → [`RF_Management.RF_SET_LISTEN_MODE_ROUTING_CMD`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L209)<br>[`RF_Management.py:188`](../../nci_decoder/Nxp_pkg/RF_Management.py#L188) `RF_GET_LISTEN_MODE_ROUTING_NTF` → [`RF_Management.RF_GET_LISTEN_MODE_ROUTING_NTF`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L261) |
| 與 nfc_forum_2_0 差異 | **相同** — 與 nfc_forum_2_0_pkg 同名表內容完全相同。 |

| 值 (hex) | 意義 |
|---|---|
| `0` | Technology-based routing entry（註解：ref to Table 54） |
| `1` | Protocol-based routing entry（註解：ref to Table 55） |
| `2` | AID-based routing entry（註解：ref to Table 56） |
| `3` | System Code-based routing entry（註解：ref to Table 57） |
| `4` | APDU Pattern-based routing entry（註解：ref to Table 58） |

<a id="tbl_pwr_state"></a>
## tbl_pwr_state

| 項目 | 值 |
|---|---|
| 定義 | [`__table__.py:540`](../../nci_decoder/Nxp_pkg/__table__.py#L540) |
| NCI spec / 來源 | Table 59: Value Field for Power State |
| `'name'` 鍵 | `Table 59: Value Field for Power State:`（表內含 `'name'` 鍵，非對照值，下表未列） |
| 直接使用的 handler | （Nxp_pkg 中無 `NFC_table.tbl_pwr_state` 直接引用） |
| 間接使用（經 `Origin.*`） | [`NFCEE_Management.py:28`](../../nci_decoder/Nxp_pkg/NFCEE_Management.py#L28) `NFCEE_DISCOVER_NTF` → [`NFCEE_Management.NFCEE_DISCOVER_NTF`](../../nci_decoder/nfc_forum_2_0_pkg/NFCEE_Management.py#L41)<br>[`RF_Management.py:152`](../../nci_decoder/Nxp_pkg/RF_Management.py#L152) `RF_SET_LISTEN_MODE_ROUTING_CMD` → [`RF_Management.RF_SET_LISTEN_MODE_ROUTING_CMD`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L209)<br>[`RF_Management.py:188`](../../nci_decoder/Nxp_pkg/RF_Management.py#L188) `RF_GET_LISTEN_MODE_ROUTING_NTF` → [`RF_Management.RF_GET_LISTEN_MODE_ROUTING_NTF`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L261) |
| 與 nfc_forum_2_0 差異 | **相同** — 與 nfc_forum_2_0_pkg 同名表內容完全相同。 |

| Bit | 意義 |
|---|---|
| bit 5 | Screen Off lock (Sub-State 3)（註解：1: Apply, 0: Not apply） |
| bit 4 | Screen On lock (Sub-State 2)（註解：1: Apply, 0: Not apply） |
| bit 3 | Screen off unlock (Sub-State 1)（註解：1: Apply, 0: Not apply） |
| bit 2 | Battery Off State（註解：1: Apply, 0: Not apply） |
| bit 1 | Switch Off State（註解：1: Apply, 0: Not apply） |
| bit 0 | Switch On State（註解：1: Apply, 0: Not apply） |

<a id="tbl_rf_dis_id"></a>
## tbl_rf_dis_id

| 項目 | 值 |
|---|---|
| 定義 | [`__table__.py:553`](../../nci_decoder/Nxp_pkg/__table__.py#L553) |
| NCI spec / 來源 | Table 67: RF Discovery ID:（程式註解：Table 67: RF Discovery ID） |
| `'name'` 鍵 | `Table 67: RF Discovery ID: `（表內含 `'name'` 鍵，非對照值，下表未列） |
| 直接使用的 handler | （Nxp_pkg 中無 `NFC_table.tbl_rf_dis_id` 直接引用） |
| 間接使用（經 `Origin.*`） | [`NCI_Core.py:292`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L292) `CORE_CONN_CREATE_CMD` → [`NCI_Core.CORE_CONN_CREATE_CMD`](../../nci_decoder/nfc_forum_2_0_pkg/NCI_Core.py#L378)<br>[`RF_Management.py:392`](../../nci_decoder/Nxp_pkg/RF_Management.py#L392) `RF_DISCOVER_NTF` → [`RF_Management.RF_DISCOVER_NTF`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L502)<br>[`RF_Management.py:407`](../../nci_decoder/Nxp_pkg/RF_Management.py#L407) `RF_DISCOVER_SELECT_CMD` → [`RF_Management.RF_DISCOVER_SELECT_CMD`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L551)<br>[`RF_Management.py:429`](../../nci_decoder/Nxp_pkg/RF_Management.py#L429) `RF_INTF_ACTIVATED_NTF` → [`RF_Management.RF_INTF_ACTIVATED_NTF`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L593) |
| 與 nfc_forum_2_0 差異 | **相同** — 與 nfc_forum_2_0_pkg 同名表內容完全相同。 |

| 值 (hex) | 意義 |
|---|---|
| `00` | RFU |
| `01-FF` | Dynamically assigned by the NFCC |
| `FF` | RFU |

<a id="tbl_deactivate_type"></a>
## tbl_deactivate_type

| 項目 | 值 |
|---|---|
| 定義 | [`__table__.py:638`](../../nci_decoder/Nxp_pkg/__table__.py#L638) |
| NCI spec / 來源 | Table 80: Deactivation Types |
| `'name'` 鍵 | `Table 80: Deactivation Types:`（表內含 `'name'` 鍵，非對照值，下表未列） |
| 直接使用的 handler | （Nxp_pkg 中無 `NFC_table.tbl_deactivate_type` 直接引用） |
| 間接使用（經 `Origin.*`） | [`RF_Management.py:451`](../../nci_decoder/Nxp_pkg/RF_Management.py#L451) `RF_DEACTIVATE_CMD` → [`RF_Management.RF_DEACTIVATE_CMD`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L675)<br>[`RF_Management.py:471`](../../nci_decoder/Nxp_pkg/RF_Management.py#L471) `RF_DEACTIVATE_NTF` → [`RF_Management.RF_DEACTIVATE_NTF`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L707) |
| 與 nfc_forum_2_0 差異 | **相同** — 與 nfc_forum_2_0_pkg 同名表內容完全相同。 |

| 值 (hex) | 意義 |
|---|---|
| `00` | Idle Mode |
| `01` | Sleep Mode |
| `02` | Sleep_AF Mode |
| `03` | Discovery |
| `04-FF` | RFU |

<a id="tbl_deactivate_reason"></a>
## tbl_deactivate_reason

| 項目 | 值 |
|---|---|
| 定義 | [`__table__.py:648`](../../nci_decoder/Nxp_pkg/__table__.py#L648) |
| NCI spec / 來源 | Table 81: Deactivation Reasons |
| `'name'` 鍵 | `Table 81: Deactivation Reasons:`（表內含 `'name'` 鍵，非對照值，下表未列） |
| 直接使用的 handler | （Nxp_pkg 中無 `NFC_table.tbl_deactivate_reason` 直接引用） |
| 間接使用（經 `Origin.*`） | [`RF_Management.py:471`](../../nci_decoder/Nxp_pkg/RF_Management.py#L471) `RF_DEACTIVATE_NTF` → [`RF_Management.RF_DEACTIVATE_NTF`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L707) |
| 與 nfc_forum_2_0 差異 | **相同** — 與 nfc_forum_2_0_pkg 同名表內容完全相同。 |

| 值 (hex) | 意義 |
|---|---|
| `00` | DH_Request |
| `01` | Endpoint_Request |
| `02` | RF_Link_Loss |
| `03` | NFC-B_Bad_AFI |
| `04` | DH request failed due to error |
| `05-FF` | RFU |

<a id="tbl_nfcee_disc_req_type"></a>
## tbl_nfcee_disc_req_type

| 項目 | 值 |
|---|---|
| 定義 | [`__table__.py:659`](../../nci_decoder/Nxp_pkg/__table__.py#L659) |
| NCI spec / 來源 | Table 85: TLV Coding for RF Discovery Request from NFCEE |
| `'name'` 鍵 | `Table 85: TLV Coding for RF Discovery Request from NFCEE:`（表內含 `'name'` 鍵，非對照值，下表未列） |
| 直接使用的 handler | （Nxp_pkg 中無 `NFC_table.tbl_nfcee_disc_req_type` 直接引用） |
| 間接使用（經 `Origin.*`） | [`RF_Management.py:539`](../../nci_decoder/Nxp_pkg/RF_Management.py#L539) `RF_NFCEE_DISCOVERY_REQ_NTF` → [`RF_Management.RF_NFCEE_DISCOVERY_REQ_NTF`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L868) |
| 與 nfc_forum_2_0 差異 | **相同** — 與 nfc_forum_2_0_pkg 同名表內容完全相同。 |

| 值 (hex) | 意義 |
|---|---|
| `00` | Added to list |
| `01` | Removed from list |
| `02-7F` | RFU |
| `80-FF` | For proprietary use |

<a id="tbl_nfcee_ntf_trig"></a>
## tbl_nfcee_ntf_trig

| 項目 | 值 |
|---|---|
| 定義 | [`__table__.py:668`](../../nci_decoder/Nxp_pkg/__table__.py#L668) |
| NCI spec / 來源 | Table 88: Trigger in NFCEE Action Notification |
| `'name'` 鍵 | `Table 88: Trigger in NFCEE Action Notification:`（表內含 `'name'` 鍵，非對照值，下表未列） |
| 直接使用的 handler | （Nxp_pkg 中無 `NFC_table.tbl_nfcee_ntf_trig` 直接引用） |
| 間接使用（經 `Origin.*`） | [`RF_Management.py:526`](../../nci_decoder/Nxp_pkg/RF_Management.py#L526) `RF_NFCEE_ACTION_NTF` → [`RF_Management.RF_NFCEE_ACTION_NTF`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L819) |
| 與 nfc_forum_2_0 差異 | **相同** — 與 nfc_forum_2_0_pkg 同名表內容完全相同。 |

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

<a id="tbl_rf_commu_para_id"></a>
## tbl_rf_commu_para_id

| 項目 | 值 |
|---|---|
| 定義 | [`__table__.py:683`](../../nci_decoder/Nxp_pkg/__table__.py#L683) |
| NCI spec / 來源 | Table 91: TLV Coding for RF Communication Parameter ID |
| `'name'` 鍵 | `Table 91: TLV Coding for RF Communication Parameter ID:`（表內含 `'name'` 鍵，非對照值，下表未列） |
| 直接使用的 handler | （Nxp_pkg 中無 `NFC_table.tbl_rf_commu_para_id` 直接引用） |
| 間接使用（經 `Origin.*`） | [`RF_Management.py:553`](../../nci_decoder/Nxp_pkg/RF_Management.py#L553) `RF_PARAMETER_UPDATE_CMD` → [`RF_Management.RF_PARAMETER_UPDATE_CMD`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L919)<br>[`RF_Management.py:568`](../../nci_decoder/Nxp_pkg/RF_Management.py#L568) `RF_PARAMETER_UPDATE_RSP` → [`RF_Management.RF_PARAMETER_UPDATE_RSP`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L984) |
| 與 nfc_forum_2_0 差異 | **相同** — 與 nfc_forum_2_0_pkg 同名表內容完全相同。 |

| 值 (hex) | 意義 |
|---|---|
| `00` | RF Technology and Mode (coded as defined in Table 131) |
| `01` | Transmit Bit Rate (coded as defined in Table 132) |
| `02` | Receive Bit Rate (coded as defined in Table 131) |
| `03` | NFC-B Data Exchange Configuration (coded as defined in Table 92) |
| `80-FF` | Proprietary |

<a id="tbl_rf_tech"></a>
## tbl_rf_tech

| 項目 | 值 |
|---|---|
| 定義 | [`__table__.py:693`](../../nci_decoder/Nxp_pkg/__table__.py#L693) |
| NCI spec / 來源 | Table 130: RF Technologies |
| `'name'` 鍵 | `Table 130: RF Technologies:`（表內含 `'name'` 鍵，非對照值，下表未列） |
| 直接使用的 handler | （Nxp_pkg 中無 `NFC_table.tbl_rf_tech` 直接引用） |
| 間接使用（經 `Origin.*`） | [`RF_Management.py:152`](../../nci_decoder/Nxp_pkg/RF_Management.py#L152) `RF_SET_LISTEN_MODE_ROUTING_CMD` → [`RF_Management.RF_SET_LISTEN_MODE_ROUTING_CMD`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L209)<br>[`RF_Management.py:188`](../../nci_decoder/Nxp_pkg/RF_Management.py#L188) `RF_GET_LISTEN_MODE_ROUTING_NTF` → [`RF_Management.RF_GET_LISTEN_MODE_ROUTING_NTF`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L261)<br>[`RF_Management.py:526`](../../nci_decoder/Nxp_pkg/RF_Management.py#L526) `RF_NFCEE_ACTION_NTF` → [`RF_Management.RF_NFCEE_ACTION_NTF`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L819) |
| 與 nfc_forum_2_0 差異 | **相同** — 與 nfc_forum_2_0_pkg 同名表內容完全相同。 |

| 值 (hex) | 意義 |
|---|---|
| `00` | NFC_RF_TECHNOLOGY_A |
| `01` | NFC_RF_TECHNOLOGY_B |
| `02` | NFC_RF_TECHNOLOGY_F |
| `03` | NFC_RF_TECHNOLOGY_V |

<a id="tbl_rf_tech_mode"></a>
## tbl_rf_tech_mode

| 項目 | 值 |
|---|---|
| 定義 | [`__table__.py:703`](../../nci_decoder/Nxp_pkg/__table__.py#L703) |
| NCI spec / 來源 | Table 131: RF Technology and Mode |
| `'name'` 鍵 | `Table 131: RF Technology and Mode:`（表內含 `'name'` 鍵，非對照值，下表未列） |
| 直接使用的 handler | （Nxp_pkg 中無 `NFC_table.tbl_rf_tech_mode` 直接引用） |
| 間接使用（經 `Origin.*`） | [`RF_Management.py:194`](../../nci_decoder/Nxp_pkg/RF_Management.py#L194) `RF_DISCOVER_CMD` → [`RF_Management.RF_DISCOVER_CMD`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L268)<br>[`RF_Management.py:392`](../../nci_decoder/Nxp_pkg/RF_Management.py#L392) `RF_DISCOVER_NTF` → [`RF_Management.RF_DISCOVER_NTF`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L502)<br>[`RF_Management.py:429`](../../nci_decoder/Nxp_pkg/RF_Management.py#L429) `RF_INTF_ACTIVATED_NTF` → [`RF_Management.RF_INTF_ACTIVATED_NTF`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L593)<br>[`RF_Management.py:539`](../../nci_decoder/Nxp_pkg/RF_Management.py#L539) `RF_NFCEE_DISCOVERY_REQ_NTF` → [`RF_Management.RF_NFCEE_DISCOVERY_REQ_NTF`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L868)<br>[`RF_Management.py:553`](../../nci_decoder/Nxp_pkg/RF_Management.py#L553) `RF_PARAMETER_UPDATE_CMD` → [`RF_Management.RF_PARAMETER_UPDATE_CMD`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L919) |
| 與 nfc_forum_2_0 差異 | **有差異** — NXP 新增：`71`；NXP 缺少（forum 有）：`04-05`=`RFU`、`07-6F`=`RFU`、`70-7F`=`Reserved for Proprietary Technologies in Poll Mode`、`84-EF`=`RFU`、`F0-FF`=`Reserved for Proprietary Technologies in Listen Mode`；文字不同：`03`（forum=`ACTIVE_POLL`）、`83`（forum=`ACTIVE_LISTEN`）。 |

| 值 (hex) | 意義 |
|---|---|
| `00` | A_PASSIVE_POLL |
| `01` | B_PASSIVE_POLL |
| `02` | F_PASSIVE_POLL |
| `03` | ACTIVE_POLL ( Not supported ) |
| `06` | V_PASSIVE_POLL |
| `71` | SILENT_PASSIVE_POLL |
| `80` | A_PASSIVE_LISTEN |
| `81` | B_PASSIVE_LISTEN |
| `82` | F_PASSIVE_LISTEN |
| `83` | ACTIVE_LISTEN ( Not supported ) |

<a id="tbl_len_rdu_val"></a>
## tbl_len_rdu_val

| 項目 | 值 |
|---|---|
| 定義 | [`__table__.py:718`](../../nci_decoder/Nxp_pkg/__table__.py#L718) |
| NCI spec / 來源 | Table 137: Length Reduction Value（程式註解：Table 137: Length Reduction Values） |
| `'name'` 鍵 | `Table 137: Length Reduction Value`（表內含 `'name'` 鍵，非對照值，下表未列） |
| 直接使用的 handler | （Nxp_pkg 中無 `NFC_table.tbl_len_rdu_val` 直接引用） |
| 間接使用（經 `Origin.*`） | [`RF_Management.py:429`](../../nci_decoder/Nxp_pkg/RF_Management.py#L429) `RF_INTF_ACTIVATED_NTF` → [`RF_Management.RF_INTF_ACTIVATED_NTF`](../../nci_decoder/nfc_forum_2_0_pkg/RF_Management.py#L593) |
| 與 nfc_forum_2_0 差異 | **相同** — 與 nfc_forum_2_0_pkg 同名表內容完全相同。 |

| 值 (hex) | 意義 |
|---|---|
| `00` | No PSL_REQ and PSL_RES were exchanged |
| `01` | 254 Bytes |
| `02` | 192 Bytes |
| `03` | 128 Bytes |
| `04` | 64 Bytes |
| `05-FF` | RFU |

<a id="tbl_tlv_type"></a>
## tbl_tlv_type

| 項目 | 值 |
|---|---|
| 定義 | [`__table__.py:735`](../../nci_decoder/Nxp_pkg/__table__.py#L735) |
| NCI spec / 來源 | Table 118: TLV Coding for NFCEE Discovery |
| `'name'` 鍵 | `Table 118: TLV Coding for NFCEE Discovery:`（表內含 `'name'` 鍵，非對照值，下表未列） |
| 直接使用的 handler | （Nxp_pkg 中無 `NFC_table.tbl_tlv_type` 直接引用） |
| 間接使用（經 `Origin.*`） | [`NFCEE_Management.py:28`](../../nci_decoder/Nxp_pkg/NFCEE_Management.py#L28) `NFCEE_DISCOVER_NTF` → [`NFCEE_Management.NFCEE_DISCOVER_NTF`](../../nci_decoder/nfc_forum_2_0_pkg/NFCEE_Management.py#L41) |
| 與 nfc_forum_2_0 差異 | **相同** — 與 nfc_forum_2_0_pkg 同名表內容完全相同。 |

| 值 (hex) | 意義 |
|---|---|
| `00` | Hardware / Registration Identification |
| `01` | ATR Bytes |
| `02` | T3T Command Set Interface Supplementary Information |
| `03` | Host ID in the HCI Network |
| `04` | NDEF |
| `05-9F` | RFU |
| `A0-FF` | For proprietary use |

<a id="tbl_nfcee_disc_status"></a>
## tbl_nfcee_disc_status

| 項目 | 值 |
|---|---|
| 定義 | [`__table__.py:747`](../../nci_decoder/Nxp_pkg/__table__.py#L747) |
| NCI spec / 來源 | Table 117: NFCEE_DISCOVER_NTF NFCEE Status（程式註解：Table 117: NFCEE_DISCOVER_NTF NFCEE Status (NOT the same field as tbl_nfcee_status / Table 122 below)） |
| `'name'` 鍵 | `Table 117: NFCEE_DISCOVER_NTF NFCEE Status:`（表內含 `'name'` 鍵，非對照值，下表未列） |
| 直接使用的 handler | （Nxp_pkg 中無 `NFC_table.tbl_nfcee_disc_status` 直接引用） |
| 間接使用（經 `Origin.*`） | [`NFCEE_Management.py:28`](../../nci_decoder/Nxp_pkg/NFCEE_Management.py#L28) `NFCEE_DISCOVER_NTF` → [`NFCEE_Management.NFCEE_DISCOVER_NTF`](../../nci_decoder/nfc_forum_2_0_pkg/NFCEE_Management.py#L41) |
| 與 nfc_forum_2_0 差異 | **相同** — 與 nfc_forum_2_0_pkg 同名表內容完全相同。 |

| 值 (hex) | 意義 |
|---|---|
| `00` | Enabled |
| `01` | Disabled |
| `02` | Unresponsive |
| `03-FF` | RFU |

<a id="tbl_nfcee_status"></a>
## tbl_nfcee_status

| 項目 | 值 |
|---|---|
| 定義 | [`__table__.py:756`](../../nci_decoder/Nxp_pkg/__table__.py#L756) |
| NCI spec / 來源 | Table 122: NFCEE_STATUS_NTF NFCEE Status（程式註解：Table 122: NFCEE_STATUS_NTF NFCEE Status (NOT the same field as tbl_nfcee_disc_status / Table 117 above)） |
| `'name'` 鍵 | `Table 122: NFCEE_STATUS_NTF NFCEE Status:`（表內含 `'name'` 鍵，非對照值，下表未列） |
| 直接使用的 handler | （Nxp_pkg 中無 `NFC_table.tbl_nfcee_status` 直接引用） |
| 間接使用（經 `Origin.*`） | [`NFCEE_Management.py:78`](../../nci_decoder/Nxp_pkg/NFCEE_Management.py#L78) `NFCEE_STATUS_NTF` → [`NFCEE_Management.NFCEE_STATUS_NTF`](../../nci_decoder/nfc_forum_2_0_pkg/NFCEE_Management.py#L212) |
| 與 nfc_forum_2_0 差異 | **有差異** — NXP 新增：`80`、`81`、`91`、`92`、`93`、`94`、`95`、`96`、`97`、`98`、`99`、`9A`、`9B`；NXP 缺少（forum 有）：`80-FF`=`Proprietary`。 |

| 值 (hex) | 意義 |
|---|---|
| `00` | Unrecoverable error |
| `01` | NFCEE Initialization sequence started |
| `02` | NFCEE Initialization sequence completed |
| `03-7F` | RFU |
| `80` | eSE has detected a temperature error. NFCC has switched off the eSE and notifies DH that it is unresponsive. |
| `81` | NFCC has detected an unexpected UICC power lost whereas NFC_SIM_SWIOx line was active |
| `91` | NFCC has detected an internal eSE reboot |
| `92` | NFCC got a timeout during eSE activation request |
| `93` | NFCC got a timeout during eSE activation request |
| `94` | NFCC has received an internal eSE temperature error |
| `95` | NFCC has detected an internal eSE Mailbox Reset during an unexpected state |
| `96` | NFCC has received an unknown message from eSE |
| `97` | NFCC has received an unknown message from eSE |
| `98` | NFCC has detected an issue during eSE activation |
| `99` | NFCC has detected an issue during eSE deactivation |
| `9A` | NFCC has received a valid activation response in an unexpected state |
| `9B` | NFCC has received a valid deactivation response in an unexpected state |

<a id="tbl_in_clk_freq"></a>
## tbl_in_clk_freq

| 項目 | 值 |
|---|---|
| 定義 | [`__table__.py:784`](../../nci_decoder/Nxp_pkg/__table__.py#L784) |
| NCI spec / 來源 | p.87 |
| 直接使用的 handler | [`NCI_Core.py:664`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L664) `VALUE_OF_REGISTER` |
| 間接使用（經 `Origin.*`） | — |
| 與 nfc_forum_2_0 差異 | **NXP 獨有表** — nfc_forum_2_0_pkg/__table__.py 無同名表。 |

| 值 (hex) | 意義 |
|---|---|
| `01` | 19.2 MHz |
| `02` | 24 MHz |
| `03` | 26 MHz |
| `04` | 38.4 MHz |
| `06` | 32 MHz |
| `07` | HFO |
| `08` | XTAL 27.12 MHz |
| `09` | Not applicable |
| `0A` | 48 MHz |

<a id="tbl_rf_trans_id"></a>
## tbl_rf_trans_id

| 項目 | 值 |
|---|---|
| 定義 | [`__table__.py:797`](../../nci_decoder/Nxp_pkg/__table__.py#L797) |
| NCI spec / 來源 | Table 1 |
| 直接使用的 handler | [`NCI_Core.py:664`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L664) `VALUE_OF_REGISTER`<br>[`Proprietary.py:185`](../../nci_decoder/Nxp_pkg/Proprietary.py#L185) `RF_GET_TRANSITION_CMD` |
| 間接使用（經 `Origin.*`） | — |
| 與 nfc_forum_2_0 差異 | **NXP 獨有表** — nfc_forum_2_0_pkg/__table__.py 無同名表。 |

| 值 (hex) | 意義 |
|---|---|
| `10` | RF_CLIF_CFG_BOOT |
| `11` | RF_CLIF_CFG_IDLE_RX |
| `12` | RF_CLIF_CFG_IDLE_TX |
| `20` | RF_RM_TX |
| `22` | RF_RM_TX_A106 |
| `23` | RF_RM_TX_A212 |
| `24` | RF_RM_TX_A424 |
| `25` | RF_RM_TX_A848 |
| `40` | RF_RM_RX |
| `41` | RF_RM_RX_TECHNO_A |
| `42` | RF_RM_RX_A106 |
| `43` | RF_RM_RX_A212 |
| `44` | RF_RM_RX_A424 |
| `45` | RF_RM_RX_A848 |
| `46` | RF_RM_RX_TECHNO_B |
| `47` | RF_RM_RX_B106 |
| `48` | RF_RM_RX_B212 |
| `49` | RF_RM_RX_B424 |
| `4A` | RF_RM_RX_B848 |
| `4B` | RF_RM_RX_TECHNO_F |
| `4C` | RF_RM_RX_F424 |
| `4D` | RF_RM_RX_F848 |
| `4E` | RF_RM_RX_TECHNO_V |
| `4F` | RF_RM_RX_V26 |
| `50` | RF_RM_RX_V53 |
| `51` | RF_RM_RX_A106_MFC |
| `60` | RF_CM_TX |
| `61` | RF_CM_TX_TECHNO_A |
| `62` | RF_CM_TX_A106 |
| `63` | RF_CM_TX_A212 |
| `64` | RF_CM_TX_A424 |
| `65` | RF_CM_TX_A848 |
| `66` | RF_CM_TX_TECHNO_B |
| `67` | RF_CM_TX_B106 |
| `68` | RF_CM_TX_B212 |
| `69` | RF_CM_TX_B424 |
| `6A` | RF_CM_TX_B848 |
| `6B` | RF_CM_TX_TECHNO_F |
| `80` | RF_CM_RX |
| `82` | RF_CM_RX_A106 |
| `83` | RF_CM_RX_A212 |
| `84` | RF_CM_RX_A424 |
| `85` | RF_CM_RX_A848 |
| `87` | RF_CM_RX_B106 |
| `88` | RF_CM_RX_B212 |
| `89` | RF_CM_RX_B424 |
| `8A` | RF_CM_RX_B848 |
| `8C` | RF_CM_RX_F212 |
| `8D` | RF_CM_RX_F424 |
| `90` | RF_CM_TXRX |
| `91` | RF_CM_TXRX_A106 |
| `92` | RF_CM_TXRX_A212 |
| `93` | RF_CM_TXRX_A424 |
| `94` | RF_CM_TXRX_A848 |
| `95` | RF_CM_TXRX_B106 |
| `96` | RF_CM_TXRX_B212 |
| `97` | RF_CM_TXRX_B424 |
| `98` | RF_CM_TXRX_B848 |
| `99` | RF_CM_TXRX_F212 |
| `9A` | RF_CM_TXRX_F424 |
| `9B` | RF_CM_TXRX_TECHNO_A |
| `9C` | RF_CM_TXRX_TECHNO_B |
| `9D` | RF_CM_TXRX_TECHNO_F |

<a id="tbl_register"></a>
## tbl_register

| 項目 | 值 |
|---|---|
| 定義 | [`__table__.py:873`](../../nci_decoder/Nxp_pkg/__table__.py#L873) |
| NCI spec / 來源 | Table 3 |
| 直接使用的 handler | [`NCI_Core.py:664`](../../nci_decoder/Nxp_pkg/NCI_Core.py#L664) `VALUE_OF_REGISTER` |
| 間接使用（經 `Origin.*`） | — |
| 與 nfc_forum_2_0 差異 | **NXP 獨有表** — nfc_forum_2_0_pkg/__table__.py 無同名表。 |

| 值 (hex) | 意義 |
|---|---|
| `32` | CLIF_TX_UNDERSHOOT_CONFIG_REG |
| `3A` | CLIF_GCM_CONFIG2_REG |
| `40` | CLIF_DGRM_RSSI_REG |
| `4C` | CLIF_ANACTRL_TX_CONFIG_REG |
| `4E` | CLIF_ANACTRL_TX1_GSN_REG |
| `4F` | CLIF_ANACTRL_TX2_GSN_REG |
| `50` | CLIF_ANACTRL_TX_GSP_REG |
| `82` | CLIF_SIGPRO_CM_FILT128A_REG |
| `95` | CLIF_SS_TX1_CMCFG_REG |
| `97` | CLIF_SS_TX2_CMCFG_REG |
| `AB` | CLIF_SS_TX_SCALE_CFG_REG |
