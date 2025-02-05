############################
#                          #
#       Global Table       #
#                          #
############################

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
    # Proprietary Status Codes
    # 0xE0-0xFF
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
    '80-FE':'For proprietary use',
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
    '80-FE':'For proprietary use',
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
    '02-0F':'(Static IDs)',
    '10-7F':'(NFCEE)',
    '80-FE':'(HCI-NFCEE)',
    'FF':   '(RFU)',
}

# Table 134: RF Interfaces
tbl_rf_if={
    'name': 'Table 134: RF Interfaces:',
    '00':   'NFCEE Direct',
    '01':   'Frame',
    '02':   'ISO-DEP',
    '03':   'NFC-DEP',
    '06':   'NDEF',
    '80-FE':'For proprietary use',
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
    '01':   'RFU',
    '02':   'CON_DISCOVERY_PARAM',
    '03':   'POWER_STATE',
    '04-07':'RFU',
    # Poll Mode – NFC-A Discovery Parameters
    '08':   'PA_BAIL_OUT',
    '09':   'PA_DEVICES_LIMIT',
    '0A-0F':'RFU',
    # Poll Mode – NFC-B Discovery Parameters
    '10':   'PB_AFI',
    '11':   'PB_BAIL_OUT',
    '12':   'PB_ATTRIB_PARAM1',
    '13':   'PB_SENSB_REQ_PARAM',
    '14':   'PB_DEVICES_LIMIT',
    '15-17':'RFU',
    # Poll Mode – NFC-F Discovery Parameters
    '18':   'PF_BIT_RATE',
    '19':   'PF_BAIL_OUT',
    '1A':   'PF_DEVICES_LIMIT',
    '1B-1F':'RFU',
    # Poll Mode – ISO-DEP Discovery Parameters
    '20':   'PI_B_H_INFO',
    '21':   'PI_BIT_RATE',
    '22-27':'RFU',
    # Poll Mode – NFC-DEP Discovery Parameters
    '28':   'PN_NFC_DEP_PSL',
    '29':   'PN_ATR_REQ_GEN_BYTES',
    '2A':   'PN_ATR_REQ_CONFIG',
    '2B-2E':'RFU',
    # Poll Mode – NFC-V Discovery Parameters
    '2F':   'PV_DEVICES_LIMIT',
    # Listen Mode – NFC-A Discovery Parameters
    '30':   'LA_BIT_FRAME_SDD',
    '31':   'LA_PLATFORM_CONFIG',
    '32':   'LA_SEL_INFO',
    '33':   'LA_NFCID1',
    '34-37':'RFU',
    # Listen Mode – NFC-B Discovery Parameters
    '38':   'LB_SENSB_INFO',
    '39':   'LB_NFCID0',
    '3A':   'LB_APPLICATION_DATA',
    '3B':   'LB_SFGI',
    '3C':   'LB_FWI_ADC_FO',
    '3D':   'RFU',
    '3E':   'LB_BIT_RATE',
    '3F':   'RFU',
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
    '51':   'RFU',
    '52':   'LF_T3T_MAX',
    '53':   'LF_T3T_FLAGS',
    '55':   'LF_T3T_RD_ALLOWED',
    # Listen Mode – NFC-F Discovery Parameters
    '50':   'LF_PROTOCOL_TYPE',
    '54':   'RFU',
    '56-57':'RFU',
    # Listen Mode – ISO-DEP Discovery Parameters
    '58':   'LI_A_RATS_TB1',
    '59':   'LI_A_HIST_BY',
    '5A':   'LI_B_H_INFO_RESP',
    '5B':   'LI_A_BIT_RATE',
    '5C':   'LI_A_RATS_TC1',
    '5D-5F':'RFU',
    # Listen Mode – NFC-DEP Discovery Parameters
    '60':   'LN_WT',
    '61':   'LN_ATR_RES_GEN_BYTES',
    '62':   'LN_ATR_RES_CONFIG',
    '63-67':'RFU',
    # Active Poll Mode Parameters
    '68':   'PACM_BIT_RATE',
    '69-7F':'RFU',
    # Other Parameters
    '80':   'RF_FIELD_INFO',
    '81':   'RF_NFCEE_ACTION',
    '82':   'NFCDEP_OP',
    '83':   'LLCP_VERSION',
    '84':   'RFU',
    '85':   'NFCC_CONFIG_CONTROL',
    '86-9F':'RFU',
    # Reserved for Proprietary Use
    'A0-FE':'Reserved',
    # Reserved for Extension
    'FF':   'RFU',
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
    5:   "Screen Off lock (Sub-State 3)",   # 1: Apply, 0: Not apply
    4:   "Screen On lock (Sub-State 2)",    # 1: Apply, 0: Not apply
    3:   "Screen off unlock (Sub-State 1)", # 1: Apply, 0: Not apply
    2:   "Battery Off State",               # 1: Apply, 0: Not apply
    1:   "Switch Off State",                # 1: Apply, 0: Not apply
    0:   "Switch On State",                 # 1: Apply, 0: Not apply
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
    '03':   'ACTIVE_POLL',
    '04-05':'RFU',
    '06':   'V_PASSIVE_POLL',
    '07-6F':'RFU',
    '70-7F':'Reserved for Proprietary Technologies in Poll Mode',
    '80':   'A_PASSIVE_LISTEN',
    '81':   'B_PASSIVE_LISTEN',
    '82':   'F_PASSIVE_LISTEN',
    '83':   'ACTIVE_LISTEN',
    '84-EF':'RFU',
    'F0-FF':'Reserved for Proprietary Technologies in Listen Mode',
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
    '04':   'NDEF',
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
    '80-FF':'Proprietary',
}