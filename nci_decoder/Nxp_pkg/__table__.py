#        Nxp Table         #

############################
#                          #
#       Global Table       #
#                          #
############################

tbl_general_status={
    '00': 'Disabled',
    '01': 'Enabled ',
}

tbl_general_status_n={
    '00': 'Enabled ',
    '01': 'Disabled',
}

# Table 129: Status Codes
tbl_status_codes={
    'name': 'Table 129: Status Codes:',
    # Generic Status Codes
    '00':   'STATUS_OK',
    '01':   'STATUS_REJECTED',
    '03':   'STATUS_FAILED',
    '04':   'STATUS_NOT_INITIALIZED',
    '05':   'STATUS_SYNTAX_ERROR',
    '06':   'STATUS_SEMANTIC_ERROR',
    '09':   'STATUS_INVALID_PARAM',
    '0A':   'STATUS_MESSAGE_SIZE_EXCEEDED',
    '11':   'STATUS_OK_1_BIT',
    '12':   'STATUS_OK_2_BIT',
    '13':   'STATUS_OK_3_BIT',
    '14':   'STATUS_OK_4_BIT',
    '15':   'STATUS_OK_5_BIT',
    '16':   'STATUS_OK_6_BIT',
    '17':   'STATUS_OK_7_BIT',
    # RF Discovery Specific Status Codes
    'A0':   'DISCOVERY_ALREADY_STARTED',
    'A1':   'DISCOVERY_TARGET_ACTIVATION_FAILED',
    'A2':   'DISCOVERY_TEAR_DOWN',
    # RF Interface Specific Status Codes
    '02':   'RF_FRAME_CORRUPTED',
    'B0':   'RF_TRANSMISSION_EXCEPTION',
    'B1':   'RF_PROTOCOL_EXCEPTION',
    'B2':   'RF_TIMEOUT_EXCEPTION',    # 'DISCOVERY_TEAR_DOWN'
    'B3':   'RF_UNEXPECTED_DATA',      # 'DISCOVERY_TEAR_DOWN'
    # NFCEE Interface Specific Status Codes
    'C0':   'NFCEE_INTERFACE_ACTIVATION_FAILED',
    'C1':   'NFCEE_TRANSMISSION_ERROR',
    'C2':   'NFCEE_PROTOCOL_ERROR',
    'C3':   'NFCEE_TIMEOUT_ERROR',
    # Proprietary Status Codes SN2x0
    'E3':   'STATUS_PMU_TXLDO_OVERCURRENT',
    'E4':   'STATUS_EMVCO_PCD_COLLISION',
    'E5':   'STATUS_MININV_AUTOLOAD_FAIL',
    'E6':   'STATUS_TRIM_AUTOLOAD_FAIL',
    'E7':   'STATUS_GPADC_ERROR',
    'EA':   'STATUS_WDG_PAGE_CORRUPTED',
    'ED':   'STATUS_CORRUPTED_TRIM',
    'EE':   'STATUS_PROTECTED_USER_AREA_CRC_MISMATCH',
    'EF':   'STATUS_PROTECTED_MIR_USER_AREA_CRC_MISMATCH',
    'F0':   'STATUS_CUSTOMER_AREA_CRC_MISMATCH',
    'FA':   'STATUS_HIGH_TEMPERATURE_NFC_ANTENNA',
}

# Table 132: Bit Rates
tbl_bit_rates={
    'name': 'Table 132: Bit Rates:',
    '00':   '106 Kbit/s',
    '01':   '212 Kbit/s',
    '02':   '424 Kbit/s',
    '03':   '848 Kbit/s',
    '04':   '1695 Kbit/s',
    '05':   '3390 Kbit/s',
    '06':   '6780 Kbit/s',
    '20':   '26 Kbit/s',
    '80':   '212 Kbit/s & 424 Kbit/s', # SN2x0
}

# Table 133: RF Protocols
tbl_rf_proto={
    'name': 'Table 133: RF Protocols:',
    '00':   'UNDETERMINED',
    '01':   'T1T',
    '02':   'T2T',
    '03':   'T3T',
    '04':   'ISO-DEP',
    '05':   'NFC-DEP',
    '06':   'T5T',
    '07':   'NDEF',
    '80':   'MIFARE_CLASSIC', # SN2x0
}

# Table 136: NFCEE Protocols / Interfaces
tbl_nfcee_proto={
    'name': 'Table 136: NFCEE Protocols / Interfaces:',
    '00':   'APDU',
    '01':   'RFU',
    '02':   'Type 3 Tag Command Set',
    '03':   'Transparent',
    '04-7F':'RFU',
    '80-FE':'For proprietary use',
    'FF':   'RFU',
}

# Table 116: NFCEE IDs
tbl_nfcee_id={
    'name': 'Table 116: NFCEE IDs:',
    '00':   'DH-NFCEE',
    '01':   'HCI-NTWK-NFCEE (RFU)',
    '02-0F':'Reserved for further static IDs',
    '10-7F':'NFCEE',
    '80-FE':'HCI-NFCEE',
    'FF':   'RFU',
}

# Table 134: RF Interfaces
tbl_rf_if={
    'name': 'Table 134: RF Interfaces:',
    '00':   'NFCEE Direct',
    '01':   'Frame',
    '02':   'ISO-DEP',
    '03':   'NFC-DEP',
    '06':   'NDEF',
    '80':   'TAG-CMD', # SN2x0
    '81':   'WLC_RF', # SN2x0 WireLess Charging
    '83':   'NFCEE_DEP_RF_eSE', # SN2x0
}

# Table 135: RF Interface Extensions
tbl_rf_if_exten={
    'name': 'Table 135: RF Interface Extensions:',
    '00':   'Frame Aggregated RF Interface Extension',
    '01':   'LLCP Symmetry RF Interface Extension',
}

############################
#                          #
#      NCI_Core Table      #
#                          #
############################

# Table 4: Conn ID
tbl_conn_id={
    'name': 'Table 4: Conn ID',
    '0000': 'Static: DH -- Remote NFC Endpoint',
    '0001': 'Static: DH -- HCI Network',
    '0010-1111': 'Dynamically assigned',
}

# Table 5: Control Messages to Reset the NFCC  (same as table 7)
# tbl_rst_msg={
#     'name': 'Table 5: Control Messages to Reset the NFCC:',
#     '00':   'Keep Config', # Reset the NFCC and keep the NCI RF Configuration (if supported).
#     '01':   'Reset Config', # Reset the NFCC including the NCI RF Configuration.
# }
tbl_rst_trig={
    'name': 'Table 5: Control Messages to Reset the NFCC:',
    '00':   'Unrecoverable error occurred in the NFCC',
    '01':   'NFCC was powered on',
    '02':   'CORE_RESET_CMD',
    # SN2x0
    'A0':   'An assert has triggered SN2x0 NFCC reset/reboot',
    'A1':   'An over temperature has triggered the reset of SN2x0 NFCC',
    'A3':   'The watchdog has triggered SN2x0 NFCC reset/reboot',
    'A4':   'External Clock Input has been lost and triggered a protection',
    'A5':   'RFU',
    'A6':   'Unexpected boot sequence detected (eg RSTN pulse too short)',
    'A7':   'Unexpected boot reason reported by hw',
}

# Table 6: NCI Version
tbl_nci_ver={
    'name': 'Table 6: NCI Version:',
    '10':   '1.0',
    '11':   '1.1',
    '20':   '2.0',
}

# Table 7: Configuration Status
tbl_cfg_status={
    'name': 'Table 7: Configuration Status:',
    '00':   'Keep Config', # Reset the NFCC and keep the NCI RF Configuration (if supported).
    '01':   'Reset Config', # Reset the NFCC including the NCI RF Configuration.
}

# Table 10: NFCC Features (Octet 1)
tbl_nfcc_feat_oct1={
    'name': 'Table 10: NFCC Features:',
    6:  'Forced NFCEE routing',
    5:  'APDU Pattern based routing',
    4:  'System Code based routing',
    3:  'AID based routing',
    2:  'Protocol based routing',
    1:  'Technology based routing',
}

# Table 10: NFCC Features (Octet 2)
tbl_nfcc_feat_oct2={
    'name': 'Table 10: NFCC Features:',
    3:  'RF Cfg in Switched Off State',
    2:  'Switched On Sub-Mode States',
    1:  'Switched Off State',
    0:  'Battery Off State',
}

# Table 13: Destination Types
tbl_dest_type={
    'name': 'Table 13: Destination Types:',
    '01':   'NFCC Loopback',
    '02':   'Remote NFC Endpoint',
    '03':   'NFCEE',
}

# Table 16: Destination-specific Parameters
tbl_d_spec_type={
    'name': 'Table 16: Destination-specific Parameters:',
    '00':   'RF Discovery ID + RF Protocol',
    '01':   'NFCEE ID + NFCEE Interface Protocol',
}

# Table 138: Configuration Parameter Tags
tbl_cfg_para={
    'name': 'Table 138: Configuration Parameter Tags:',
    # Common Discovery Parameters
    '00':   'TOTAL_DURATION',
    '02':   'CON_DISCOVERY_PARAM',
    # Poll Mode – NFC-A Discovery Parameters
    '08':   'PA_BAIL_OUT',
    '09':   'PA_DEVICES_LIMIT',
    # Poll Mode – NFC-B Discovery Parameters
    '10':   'PB_AFI',
    '11':   'PB_BAIL_OUT',
    '12':   'PB_ATTRIB_PARAM1',
    '13':   'PB_SENSB_REQ_PARAM',
    '14':   'PB_DEVICES_LIMIT',
    # Poll Mode – NFC-F Discovery Parameters
    '18':   'PF_BIT_RATE',
    '19':   'PF_BAIL_OUT',
    '1A':   'PF_DEVICES_LIMIT',
    # Poll Mode – ISO-DEP Discovery Parameters
    '20':   'PI_B_H_INFO',
    '21':   'PI_BIT_RATE',
    # Poll Mode – NFC-DEP Discovery Parameters
    '28':   'PN_NFC_DEP_PSL',
    '29':   'PN_ATR_REQ_GEN_BYTES',
    '2A':   'PN_ATR_REQ_CONFIG',
    # Poll Mode – NFC-V Discovery Parameters
    '2F':   'PV_DEVICES_LIMIT',
    # Listen Mode – NFC-A Discovery Parameters
    '30':   'LA_BIT_FRAME_SDD',
    '31':   'LA_PLATFORM_CONFIG',
    '32':   'LA_SEL_INFO',
    '33':   'LA_NFCID1',
    # Listen Mode – NFC-B Discovery Parameters
    '38':   'LB_SENSB_INFO',
    '39':   'LB_NFCID0',
    '3A':   'LB_APPLICATION_DATA',
    '3B':   'LB_SFGI',
    '3C':   'LB_FWI_ADC_FO',
    '3E':   'LB_BIT_RATE',
    # Listen Mode – T3T Discovery Parameters
    '40':   'LF_T3T_IDENTIFIERS_1',
    '41':   'LF_T3T_IDENTIFIERS_2',
    '42':   'LF_T3T_IDENTIFIERS_3',
    '43':   'LF_T3T_IDENTIFIERS_4',
    '44':   'LF_T3T_IDENTIFIERS_5',
    '45':   'LF_T3T_IDENTIFIERS_6',
    '46':   'LF_T3T_IDENTIFIERS_7',
    '47':   'LF_T3T_IDENTIFIERS_8',
    '48':   'LF_T3T_IDENTIFIERS_9',
    '49':   'LF_T3T_IDENTIFIERS_10',
    '4A':   'LF_T3T_IDENTIFIERS_11',
    '4B':   'LF_T3T_IDENTIFIERS_12',
    '4C':   'LF_T3T_IDENTIFIERS_13',
    '4D':   'LF_T3T_IDENTIFIERS_14',
    '4E':   'LF_T3T_IDENTIFIERS_15',
    '4F':   'LF_T3T_IDENTIFIERS_16',
    '52':   'LF_T3T_MAX',
    '53':   'LF_T3T_FLAGS',
    '55':   'LF_T3T_RD_ALLOWED',
    # Listen Mode – NFC-F Discovery Parameters
    '50':   'LF_PROTOCOL_TYPE',
    # '54':   '???'    SN2x0
    # Listen Mode – ISO-DEP Discovery Parameters
    '58':   'LI_A_RATS_TB1',
    '59':   'LI_A_HIST_BY',
    '5A':   'LI_B_H_INFO_RESP',
    '5B':   'LI_A_BIT_RATE',
    '5C':   'LI_A_RATS_TC1',
    # Listen Mode – NFC-DEP Discovery Parameters
    '60':   'LN_WT',
    '61':   'LN_ATR_RES_GEN_BYTES',
    '62':   'LN_ATR_RES_CONFIG',
    # Active Poll Mode Parameters
    '68':   'PACM_BIT_RATE',
    # Other Parameters
    '80':   'RF_FIELD_INFO',
    '81':   'RF_NFCEE_ACTION',
    '82':   'NFCDEP_OP',
    '83':   'LLCP_VERSION',
    '85':   'NFCC_CONFIG_CONTROL',
    # Reserved for Proprietary Use
    'A0-FE':'Reserved',
    # Reserved for Extension
    'FF':   'RFU',
    # Ext. Tag SN2x0
    # Table 97. Core configuration parameters
    'A001': 'NFCC_DIE_ID',
    'A015': 'DEFAULT_POWER',
    'A00A': 'WAIT_FOR_STABLE_SYSCLOCK',
    'A010': 'CLKGEN',
    'A011': 'RF_CLOCK_CFG',
    'A00E': 'PMU_CFG',
    'A007': 'RSTN_CFG',
    'A08E': 'PHONE_OFF_ALLOWED',
    'A009': 'TO_BEFORE_STDBY_CFG',
    'A01D': 'Lx_DEBUG_CFG',
    'A00F': 'MW_AREA',
    'A0FB': 'HW_RESET_NTF',
    # Table 98. Poll Mode configuration
    'A064': 'EMVCo_PCD_SETTINGS',
    'A044': 'POLL_PROFILE_SEL_CFG',
    'A04D': 'MFC_KEY-0_CFG',
    'A04E': 'MFC_KEY-1_CFG',
    'A04F': 'MFC_KEY-2_CFG',
    'A050': 'MFC_KEY-3_CFG',
    'A051': 'MFC_KEY-4_CFG',
    'A052': 'MFC_KEY-5_CFG',
    'A053': 'MFC_KEY-6_CFG',
    'A054': 'MFC_KEY-7_CFG',
    'A055': 'MFC_KEY-8_CFG',
    'A056': 'MFC_KEY-9_CFG',
    'A057': 'MFC_KEY-10_CFG',
    'A058': 'MFC_KEY-11_CFG',
    'A059': 'MFC_KEY-12_CFG',
    'A05A': 'MFC_KEY-13_CFG',
    'A05B': 'MFC_KEY-14_CFG',
    'A05C': 'MFC_KEY-15_CFG',
    'A05D': 'FSDI_CFG',
    'A106': 'LPCD_FPC',
    'A148': 'RF_PATTERN_CHK',
    'A14B': 'PLL_FREQ_CHECK',
    # Table 99. Listen Mode Configuration
    'A080': 'TO_RF_OFF_CFG',
    'A062': 'SLOW_HOST_CFG',
    'A085': 'RF_MISC_SETTINGS',
    'A10E': 'GUARD_TIMEOUT_Tx2Rx',
    'A095': 'NDEF_NFCEE',
    'A110': 'NDEF_NFCEE_CFG2',
    'A10B': 'AUTONOMOUS_START_TIMEOUT',
    'A10F': 'ULPDET_CFG',
    'A096': 'NOTIFY_ALL_AID',
    'A111': 'NOTIFY_ALL_FID',
    'A086': 'RF_BITRATE_LIMIT_A_CFG',
    'A087': 'RF_BITRATE_LIMIT_B_CFG',
    'A11B': 'MERGE_SAK',
    'A136': 'AUTOMATIC_CARD_SELECTION',
    'A155': 'RSSI_CONTINUOUS_NTF',
    'A158': 'NFCLD_THRESHOLD_FIELD_DETECT',
    # Table 100. SWP configuration parameters for UICC1 interface
    'A0C0': 'SWP_BITRATE_UICC1',
    'A0CB': 'SWP_TS1_HIGHV_UICC1',
    'A0EC': 'SWP_UICC1_IF_EN_CFG',
    'A0F1': 'SWP_UICC1_SPECIAL_PWR_MODE_CFG',
    'A0D1': 'SWP_BITRATE_UICC2',
    'A0D3': 'SWP_TS1_HIGHV_UICC2',
    'A0D4': 'SWP_UICC2_IF_EN_CFG',
    'A0F8': 'SWP_UICC2_SPECIAL_PWR_MODE_CFG',
    'A0C5': 'SWP_UICC1_ACT_RSET_WAIT',
    'A11C': 'SWP_EXT_RESUME',
    # Table 101. Mailbox configuration parameters
    'A0B8': 'SE_APDU_LOGGING_EN_CFG',
    'A0ED': 'NFCEE_eSE_IF_EN_CFG',
    'A0F9': 'SE_COLD_RESET_NTF',
    'A08A': 'SE_POWER_ON_TO_WAKE_UP_GUARD_TIME',
    'A08C': 'SE_POWER_OFF_TO_SW_RESET_DELAY_TIME',
    'A08D': 'WAKE_UP_SE_TO_ACT_FRAME_DELAY_TIME',
    'A089': 'ACT_RESPONSE_GUARD_TIME',
    'A08B': 'CLT_F_TIMEOUT',
    'A082': 'CLT_A_TIMEOUT',
    'A094': 'SE_TEMP_ERROR_DELAY_TIME',
    'A084': 'VBAT_THRESHOLD_PHONE_OFF',
    # Table 102. HCI configuration parameters
    'A0EA': 'UICC1_SESSIONID',
    'A01E': 'UICC2_SESSIONID',
    'A0EB': 'eSE_SESSIONID',
    'A0EF': 'RF_PARAM_CE_UICC1',
    'A0E8': 'RF_PARAM_CE_UICC2',
    'A0F0': 'RF_PARAM_CE_eSE',
    'A11A': 'PHONEOFF_TECH_CFG',
    'A022': 'HCI pipe status of Connectivity gate for NFCEE_eSE',
    'A023': 'HCI pipe status of APDU gate for NFCEE_eSE',
    'A024': 'HCI pipe status of connectivity gate for NFCEE_UICC1',
    'A025': 'HCI pipe status of APDU gate for NFCEE_UICC1',
    'A0E9': 'HCI pipe status of connectivity gate for NFCEE_UICC2',
    'A012': 'HCI pipe status of APDU gate for NFCEE_eUICC',
    # Table 103. Mechanism to configure the RF transitions
    'A017': 'RF_CUST_PHAS E_COMPENSATI ON',
    'A068': 'RF_LPCD_CFG',
    'A034': 'RF_DLMA_CFG',
    'A10A': 'RF_DLMA_CLOCK_LESS_CEF_CFG',
    'A00B': 'RF_DPC_CFG',
    'A00D': 'RF_TRANSITION_CFG',
    'A09E': 'RX_CTRL_CFG',
    'A17E': 'ADVANCED_HYBRID_LPCD_CFG',
    'A12E': 'FDT_CFG',
    # Table 108. GPIO configuration parameters
    'A196': 'GPIO_SELECTION',
    # in SN220 RF Register Setting Guidelines
    # 2.4.2  2.7.4.2
    'A06A': 'RF_CLK_PLL_DPLL3',
    # 2.7.2
    'A0AF': 'DLMA_CTRL',
    # 2.8.2.2
    'A0A7': 'RM_GLOBAL_TX_SHAPING',
    # 2.8.2.3
    'A0A8': 'RM_TECHNO_TX_SHAPING',
    # AN13076-SN220DLMA.pdf
    'A098': 'MEASURED_LMA_RSSI',
    'A0AB': 'RSSI_GAIN',
    'A0A9': 'DLMA_TX'
}



############################
#                          #
#    RF_Management Table   #
#                          #
############################

#Table 49: Value Field for Mode
tbl_mode={
    'name': 'Table 49: Value Field for Mode:',
    '00':   'Error',
    '01':   'Polling',
    '02':   'Listen',
    '03':   'Listen/Polling',
}

# Table 51: More field values
tbl_more={
    'name': 'Table 51: More field values:',
    '00':   'Last Message',
    '01':   'More Message(s) to follow',
}

# Table 52: Qualifier-Type Field values (直接實作在code中)
"""""""""""""""
0   -   -   -   -   -   -   - : RFU
-   x   -   -   -   -   -   - : Routing is blocked for the power modes where it is not supported.
-   -   x   -   -   -   -   - : Match is allowed when the SELECT AID is shorter than the AID in this routing table entry.
-   -   -   x   -   -   -   - : Match is allowed when the SELECT AID is longer than the AID in this routing table entry.
-   -   -   -   x   x   x   x : Ref to Table 53.
"""""""""""""""
# in # RF_SET_LISTEN_MODE_ROUTING_CMD

# Table 53: Listen Mode Routing Entry Types
tbl_L_mode_routing_entry_type={
    'name': 'Table 53: Listen Mode Routing Entry Types:',
    '0':    'Technology-based routing entry', # ref to Table 54
    '1':    'Protocol-based routing entry', # ref to Table 55
    '2':    'AID-based routing entry', # ref to Table 56
    '3':    'System Code-based routing entry', # ref to Table 57
    '4':    'APDU Pattern-based routing entry', # ref to Table 58
}

# Table 54: Value Field for Technology-based Routing
"""""""""""""""
	[Table 54: Value Field for Technology-based Routing]
Route:			1 Octet
Power State:	1 Octet
Technology:		1 Octet
"""""""""""""""
# in # RF_SET_LISTEN_MODE_ROUTING_CMD

# Table 55: Value Field for Protocol-based Routing
"""""""""""""""
	[Table 55: Value Field for Protocol-based Routing]
Route:			1 Octet
Power State:	1 Octet
Protocol:		1 Octet
"""""""""""""""
# in # RF_SET_LISTEN_MODE_ROUTING_CMD

# Table 56: Value Field for AID-based Routing
"""""""""""""""
	[Table 56: Value Field for AID-based Routing]
Route:			1 Octet
Power State:	1 Octet
AID:		    1 Octet
"""""""""""""""
# in # RF_SET_LISTEN_MODE_ROUTING_CMD

# Table 57: Value Field for System Code-based Routing
"""""""""""""""
	[Table 57: Value Field for System Code-based Routing]
Route:			1 Octet
Power State:	1 Octet
SC Route List:  2n Octets
"""""""""""""""
# in # RF_SET_LISTEN_MODE_ROUTING_CMD

# Table 58: Value Field for APDU Pattern-based Routing
"""""""""""""""
	[Table 58: Value Field for APDU Pattern-based Routing]
Route:			1 Octet
Power State:	1 Octet
Reference data:	n Octet(s)
Mask:       	n Octet(s)
"""""""""""""""
# in # RF_SET_LISTEN_MODE_ROUTING_CMD

# Table 59: Value Field for Power State
tbl_pwr_state={
    'name': 'Table 59: Value Field for Power State:',
    # 7:  "RFU",
    # 6:  "RFU",
    5:   "Switched On Sub-State 3",   # 1: Apply, 0: Not apply
    4:   "Switched On Sub-State 2",   # 1: Apply, 0: Not apply
    3:   "Switched On Sub-State 1",   # 1: Apply, 0: Not apply
    2:   "Battery Off State",         # 1: Apply, 0: Not apply
    1:   "Switched Off State",        # 1: Apply, 0: Not apply
    0:   "Switched On State",         # 1: Apply, 0: Not apply
}

# Table 67: RF Discovery ID
tbl_rf_dis_id={
    'name': 'Table 67: RF Discovery ID: ',
    '00':   'RFU',
    '01-FF':'Dynamically assigned by the NFCC',
    'FF':   'RFU',
}

# Table 68: Specific Parameters for NFC-A Poll Mode
"""""""""""""""
	[Table 68: Specific Parameters for NFC-A Poll Mode]
SENS_RES Response: 			2 Octets
NFCID1 Length: 				1 Octet
NFCID1: 					4, 7, or 10 Octets
SEL_RES Response Length:	1 Octet
SEL_RES Response: 			0 or 1 Octet
HRx Length: 				1 Octet
HRx: 						0 or 2 Octet(s)
"""""""""""""""
# in # RF_TECH_SPEC_PARA

# Table 69: Specific Parameters for NFC-A Listen Mode
"""""""""""""""
	[Table 69: Specific Parameters for NFC-A Listen Mode]
(Empty)
"""""""""""""""
# in # RF_TECH_SPEC_PARA

# Table 70: Specific Parameters for NFC-B Poll Mode
"""""""""""""""
	[Table 70: Specific Parameters for NFC-B Poll Mode]
SENSB_RES Response Length: 			1 Octet
SENSB_RES Response: 				11 or 12 Octets
"""""""""""""""
# in # RF_TECH_SPEC_PARA

# Table 71: Specific Parameters for NFC-B Listen Mode
"""""""""""""""
	[Table 71: Specific Parameters for NFC-B Listen Mode]
SENSB_REQ Command:		1 Octet
"""""""""""""""
# in # RF_TECH_SPEC_PARA

# Table 72: Specific Parameters for NFC-F Poll Mode
"""""""""""""""
	[Table 72: Specific Parameters for NFC-F Poll Mode]
Bit Rate: 					1 Octet
SENSF_RES Response Length: 	1 Octet
SENSF_RES Response:			16 or 18 Octets
"""""""""""""""
# in # RF_TECH_SPEC_PARA

# Table 73: Specific Parameters for NFC-F Listen Mode
"""""""""""""""
	[Table 73: Specific Parameters for NFC-F Listen Mode]
Local NFCID2 Length: 	1 Octet
Local NFCID2:			0 or 8 Octet(s)
"""""""""""""""
# in # RF_TECH_SPEC_PARA

# Table 74: Specific Parameters for NFC-V Poll Mode
"""""""""""""""
	[Table 74: Specific Parameters for NFC-V Poll Mode]
RES_FLAG: 	1 Octet
DSFID: 		1 Octet
UID:		8 Octets
"""""""""""""""
# in # RF_TECH_SPEC_PARA

# Table 75: Specific Parameters for NFC-ACM Poll Mode
"""""""""""""""
	[Table 75: Specific Parameters for NFC-ACM Poll Mode]
ATR_RES Response Length: 	1 Octet (n)
ATR_RES Response: 			n Octet(s)
"""""""""""""""
# in # RF_TECH_SPEC_PARA

# Table 76: Specific Parameters for NFC-ACM Listen Mode
"""""""""""""""
	[Table 76: Specific Parameters for NFC-ACM Listen Mode]
ATR_REQ Command Length: 	1 Octet (n)
ATR_REQ Command: 			n Octet(s)
"""""""""""""""
# in # RF_TECH_SPEC_PARA

# Table 80: Deactivation Types
tbl_deactivate_type={
    'name': 'Table 80: Deactivation Types:',
    '00':   'Idle Mode',
    '01':   'Sleep Mode',
    '02':   'Sleep_AF Mode',
    '03':   'Discovery',
    '04-FF':'RFU',
}

#Table 81: Deactivation Reasons
tbl_deactivate_reason={
    'name': 'Table 81: Deactivation Reasons:',
    '00':   'DH_Request',
    '01':   'Endpoint_Request',
    '02':   'RF_Link_Loss',
    '03':   'NFC-B_Bad_AFI',
    '04':   'DH request failed due to error',
    '05-FF':'RFU',
}

# Table 88: Trigger in NFCEE Action Notification
tbl_nfcee_ntf_trig={
    'name': 'Table 88: Trigger in NFCEE Action Notification:',
    '00':   '[ISO/IEC_7816-4] SELECT command with an AID',
    '01':   'Protocol-based Route Selection Process (ref to Table 133)',
    '02':   'Technology-based Route Selection Process (ref to Table 130)',
    '03':   'System Code-based Route Selection Process',
    '04':   'TAPDU Pattern-based Route Selection Process (as defined in Table 58)',
    '05':   'Forced NFCEE Routing is used (See Table 130)',
    '06-0F':'RFU',
    '10-7F':'Application specific',
    '80-FF':'RFU',
    # 10 ~ 7F Application specific.
}

# Table 91: TLV Coding for RF Communication Parameter ID
tbl_rf_commu_para_id={
    'name': 'Table 91: TLV Coding for RF Communication Parameter ID:',
    '00':   'RF Technology and Mode (coded as defined in Table 131)',
    '01':   'Transmit Bit Rate (coded as defined in Table 132)',
    '02':   'Receive Bit Rate (coded as defined in Table 131)',
    '03':   'NFC-B Data Exchange Configuration (coded as defined in Table 92)',
    '80-FF':'Proprietary'
}

# Table 130: RF Technologies
tbl_rf_tech={
    'name': 'Table 130: RF Technologies:',
    '00':   'NFC_RF_TECHNOLOGY_A',
    '01':   'NFC_RF_TECHNOLOGY_B',
    '02':   'NFC_RF_TECHNOLOGY_F',
    '03':   'NFC_RF_TECHNOLOGY_V',
    # 80 ~ FE For proprietary use,
}

# Table 131: RF Technology and Mode
tbl_rf_tech_mode={
    'name': 'Table 131: RF Technology and Mode:',
    '00':   'A_PASSIVE_POLL',
    '01':   'B_PASSIVE_POLL',
    '02':   'F_PASSIVE_POLL',
    '03':   'ACTIVE_POLL ( Not supported )',
    '06':   'V_PASSIVE_POLL',
    '71':   'SILENT_PASSIVE_POLL',
    '80':   'A_PASSIVE_LISTEN',
    '81':   'B_PASSIVE_LISTEN',
    '82':   'F_PASSIVE_LISTEN',
    '83':   'ACTIVE_LISTEN ( Not supported )',
}

# Table 137: Length Reduction Values
tbl_len_rdu_val={
    'name': 'Table 137: Length Reduction Value',
    '00':   'No PSL_REQ and PSL_RES were exchanged',
    '01':   '254 Bytes',
    '02':   '192 Bytes',
    '03':   '128 Bytes',
    '04':   '64 Bytes',
    '05-FF':'RFU',
}

############################
#                          #
#  NFCEE_Management Table  #
#                          #
############################

# Table 118: TLV Coding for NFCEE Discovery
tbl_tlv_type={
    'name': 'Table 118: TLV Coding for NFCEE Discovery:',
    '00':   'Hardware / Registration Identification',
    '01':   'ATR Bytes',
    '02':   'T3T Command Set Interface Supplementary Information',
    '03':   'Host ID in the HCI Network',
    '04':   'Support NDEF storage',
    '05-9F':'RFU',
    'A0-FF':'For proprietary use',
}

# # Table 119: Value Field for T3T Command Set Interface Supplementary Information
# tbl_tlv_type={
#     'name': 'Table 119: Value Field for T3T Command Set Interface Supplementary Information:',
#     '00':   'Hardware / Registration Identification',
#     '01':   'ATR Bytes',
#     '02':   'T3T Command Set Interface Supplementary Information',
#     '03':   'Host ID in the HCI Network',
#     '03':   'Support NDEF storage',
#     '05-9F':'RFU',
#     'A0-FF':'For proprietary use',
# }

# Table 122: NFCEE_STATUS_NTF NFCEE Status
tbl_nfcee_status={
    'name': 'Table 122: NFCEE_STATUS_NTF NFCEE Status:',
    '00':   'Unrecoverable error',
    '01':   'NFCEE Initialization sequence started',
    '02':   'NFCEE Initialization sequence completed',
    '03-7F':'RFU',
    # SN2x0
    '80':   'eSE has detected a temperature error. NFCC has switched off the eSE and notifies DH that it is unresponsive.',
    '81':   'NFCC has detected an unexpected UICC power lost whereas NFC_SIM_SWIOx line was active',
    '91':   'NFCC has detected an internal eSE reboot',
    '92':   'NFCC got a timeout during eSE activation request',
    '93':   'NFCC got a timeout during eSE activation request',
    '94':   'NFCC has received an internal eSE temperature error',
    '95':   'NFCC has detected an internal eSE Mailbox Reset during an unexpected state',
    '96':   'NFCC has received an unknown message from eSE',
    '97':   'NFCC has received an unknown message from eSE',
    '98':   'NFCC has detected an issue during eSE activation',
    '99':   'NFCC has detected an issue during eSE deactivation',
    '9A':   'NFCC has received a valid activation response in an unexpected state',
    '9B':   'NFCC has received a valid deactivation response in an unexpected state',
}

############################
#                          #
#    Prop.  SN2x0 Table    #
#                          #
############################
# p.87
tbl_in_clk_freq={
    '01': '19.2 MHz',
    '02': '24 MHz',
    '03': '26 MHz',
    '04': '38.4 MHz',
    '06': '32 MHz',
    '07': 'HFO',
    '08': 'XTAL 27.12 MHz',
    '09': 'Not applicable',
    '0A': '48 MHz',
}

# Table 1
tbl_rf_trans_id={
    # BOOT
    '10': 'RF_CLIF_CFG_BOOT',
    # IDLE_RX
    '11': 'RF_CLIF_CFG_IDLE_RX',
    # IDLE_TX
    '12': 'RF_CLIF_CFG_IDLE_TX',
    # RM_TX
    '20': 'RF_RM_TX',
    '22': 'RF_RM_TX_A106',
    '23': 'RF_RM_TX_A212',
    '24': 'RF_RM_TX_A424',
    '25': 'RF_RM_TX_A848',
    # RM_RX
    '40': 'RF_RM_RX',
    '41': 'RF_RM_RX_TECHNO_A',
    '42': 'RF_RM_RX_A106',
    '43': 'RF_RM_RX_A212',
    '44': 'RF_RM_RX_A424',
    '45': 'RF_RM_RX_A848',
    '46': 'RF_RM_RX_TECHNO_B',
    '47': 'RF_RM_RX_B106',
    '48': 'RF_RM_RX_B212',
    '49': 'RF_RM_RX_B424',
    '4A': 'RF_RM_RX_B848',
    '4B': 'RF_RM_RX_TECHNO_F',
    '4C': 'RF_RM_RX_F424',
    '4D': 'RF_RM_RX_F848',
    '4E': 'RF_RM_RX_TECHNO_V',
    '4F': 'RF_RM_RX_V26',
    '50': 'RF_RM_RX_V53',
    '51': 'RF_RM_RX_A106_MFC',
    # CM_TX
    '60': 'RF_CM_TX',
    '61': 'RF_CM_TX_TECHNO_A',
    '62': 'RF_CM_TX_A106',
    '63': 'RF_CM_TX_A212',
    '64': 'RF_CM_TX_A424',
    '65': 'RF_CM_TX_A848',
    '66': 'RF_CM_TX_TECHNO_B',
    '67': 'RF_CM_TX_B106',
    '68': 'RF_CM_TX_B212',
    '69': 'RF_CM_TX_B424',
    '6A': 'RF_CM_TX_B848',
    '6B': 'RF_CM_TX_TECHNO_F',
    # CM_RX
    '80': 'RF_CM_RX',
    '82': 'RF_CM_RX_A106',
    '83': 'RF_CM_RX_A212',
    '84': 'RF_CM_RX_A424',
    '85': 'RF_CM_RX_A848',
    '87': 'RF_CM_RX_B106',
    '88': 'RF_CM_RX_B212',
    '89': 'RF_CM_RX_B424',
    '8A': 'RF_CM_RX_B848',
    '8C': 'RF_CM_RX_F212',
    '8D': 'RF_CM_RX_F424',
    # CM_TXRX
    '90': 'RF_CM_TXRX',
    '91': 'RF_CM_TXRX_A106',
    '92': 'RF_CM_TXRX_A212',
    '93': 'RF_CM_TXRX_A424',
    '94': 'RF_CM_TXRX_A848',
    '95': 'RF_CM_TXRX_B106',
    '96': 'RF_CM_TXRX_B212',
    '97': 'RF_CM_TXRX_B424',
    '98': 'RF_CM_TXRX_B848',
    '99': 'RF_CM_TXRX_F212',
    '9A': 'RF_CM_TXRX_F424',
    # RF_CM_TXRX_TECHNO_X
    '9B': 'RF_CM_TXRX_TECHNO_A',
    '9C': 'RF_CM_TXRX_TECHNO_B',
    '9D': 'RF_CM_TXRX_TECHNO_F',
}

# Table 3
tbl_register={
    '32': 'CLIF_TX_UNDERSHOOT_CONFIG_REG',
    '3A': 'CLIF_GCM_CONFIG2_REG',
    '40': 'CLIF_DGRM_RSSI_REG',
    '4C': 'CLIF_ANACTRL_TX_CONFIG_REG',
    '4E': 'CLIF_ANACTRL_TX1_GSN_REG',
    '4F': 'CLIF_ANACTRL_TX2_GSN_REG',
    '50': 'CLIF_ANACTRL_TX_GSP_REG',
    '82': 'CLIF_SIGPRO_CM_FILT128A_REG',
    '95': 'CLIF_SS_TX1_CMCFG_REG',
    '97': 'CLIF_SS_TX2_CMCFG_REG',
    'AB': 'CLIF_SS_TX_SCALE_CFG_REG',
}