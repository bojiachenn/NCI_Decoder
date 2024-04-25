from Nxp_pkg import NCI_Core
from Nxp_pkg import RF_Management
from Nxp_pkg import NFCEE_Management
from Nxp_pkg import Proprietary
from Nxp_pkg import HDLL

HDLL_CMD = '00'

tbl_nci_ctrl = {
	"NCI Core": {
		'00':  {"CMD": NCI_Core.CORE_RESET_CMD, 				"RSP": NCI_Core.CORE_RESET_RSP, 					"NTF": NCI_Core.CORE_RESET_NTF},
		'01':  {"CMD": NCI_Core.CORE_INIT_CMD, 					"RSP": NCI_Core.CORE_INIT_RSP},
		'02':  {"CMD": NCI_Core.CORE_SET_CONFIG_CMD, 			"RSP": NCI_Core.CORE_SET_CONFIG_RSP},
		'03':  {"CMD": NCI_Core.CORE_GET_CONFIG_CMD, 			"RSP": NCI_Core.CORE_GET_CONFIG_RSP},
		'04':  {"CMD": NCI_Core.CORE_CONN_CREATE_CMD, 			"RSP": NCI_Core.CORE_CONN_CREATE_RSP},
		'05':  {"CMD": NCI_Core.CORE_CONN_CLOSE_CMD, 			"RSP": NCI_Core.CORE_CONN_CLOSE_RSP},
		'06':  {																				                    "NTF": NCI_Core.CORE_CONN_CREDITS_NTF},
		'07':  {																				                    "NTF": NCI_Core.CORE_GENERIC_ERROR_NTF},
		'08':  {																				                    "NTF": NCI_Core.CORE_INTERFACE_ERROR_NTF},
		'09':  {"CMD": NCI_Core.CORE_SET_POWER_SUB_STATE_CMD,	"RSP": NCI_Core.CORE_SET_POWER_SUB_STATE_RSP},
		# 10 ~ 63 RFU
	},
	"RF Management": {
		'00':  {"CMD": RF_Management.RF_DISCOVER_MAP_CMD,			    "RSP": RF_Management.RF_DISCOVER_MAP_RSP},
		'01':  {"CMD": RF_Management.RF_SET_LISTEN_MODE_ROUTING_CMD,   	"RSP": RF_Management.RF_SET_LISTEN_MODE_ROUTING_RSP},
		'02':  {"CMD": RF_Management.RF_GET_LISTEN_MODE_ROUTING_CMD,   	"RSP": RF_Management.RF_GET_LISTEN_MODE_ROUTING_RSP, 	"NTF": RF_Management.RF_GET_LISTEN_MODE_ROUTING_NTF},
		'03':  {"CMD": RF_Management.RF_DISCOVER_CMD, 				    "RSP": RF_Management.RF_DISCOVER_RSP, 				    "NTF": RF_Management.RF_DISCOVER_NTF},
		'04':  {"CMD": RF_Management.RF_DISCOVER_SELECT_CMD, 		    "RSP": RF_Management.RF_DISCOVER_SELECT_RSP},
		'05':  {																				                                "NTF": RF_Management.RF_INTF_ACTIVATED_NTF},
		'06':  {"CMD": RF_Management.RF_DEACTIVATE_CMD, 				"RSP": RF_Management.RF_DEACTIVATE_RSP, 				"NTF": RF_Management.RF_DEACTIVATE_NTF},
		'07':  {																				                                "NTF": RF_Management.RF_FIELD_INFO_NTF},
		'08':  {"CMD": RF_Management.RF_T3T_POLLING_CMD, 			    "RSP": RF_Management.RF_T3T_POLLING_RSP, 				"NTF": RF_Management.RF_T3T_POLLING_NTF},
		'09':  {																				                                "NTF": RF_Management.RF_NFCEE_ACTION_NTF},
		'0A':  {																				                                "NTF": RF_Management.RF_NFCEE_DISCOVERY_REQ_NTF},
		'0B':  {"CMD": RF_Management.RF_PARAMETER_UPDATE_CMD, 		    "RSP": RF_Management.RF_PARAMETER_UPDATE_RSP},
		'0C':  {"CMD": RF_Management.RF_INTF_EXT_START_CMD, 			"RSP": RF_Management.RF_INTF_EXT_START_RSP},
		'0D':  {"CMD": RF_Management.RF_INTF_EXT_STOP_CMD, 				"RSP": RF_Management.RF_INTF_EXT_STOP_RSP},
		'0E':  {"CMD": RF_Management.RF_EXT_AGG_ABORT_CMD, 				"RSP": RF_Management.RF_EXT_AGG_ABORT_RSP},
		'0F':  {"CMD": RF_Management.RF_NDEF_ABORT_CMD, 				"RSP": RF_Management.RF_NDEF_ABORT_RSP},
		'10':  {"CMD": RF_Management.RF_ISO_DEP_NAK_PRESENCE_CMD, 		"RSP": RF_Management.RF_ISO_DEP_NAK_PRESENCE_RSP, 		"NTF": RF_Management.RF_ISO_DEP_NAK_PRESENCE_NTF},
		'11':  {"CMD": RF_Management.RF_SET_FORCED_NFCEE_ROUTING_CMD,	"RSP": RF_Management.RF_SET_FORCED_NFCEE_ROUTING_RSP},
        # SN2x0
        '18':  {																												"NTF": RF_Management.IOT_RETRY_NTF},
		'20':  {																												"NTF": RF_Management.FIELD_DETECT_NTF},
		'21':  {																												"NTF": RF_Management.PLL_UNLOCKED_NTF},
		'23':  {																												"NTF": RF_Management.TxLDO_ERROR_NTF},
		'28':  {																												"NTF": RF_Management.PLL_LOSTLOCK_NTF},
        '29':  {																												"NTF": RF_Management.SETTINGS_CHANGE_NTF},
		'2A':  {																												"NTF": RF_Management.RF_FREQ_ERROR_NTF},
		'2B':  {																												"NTF": RF_Management.LPDET_ERROR_NTF},
		# 18 ~ 63 RFU
	},
	"NFCEE Management": {
		'00':  {"CMD": NFCEE_Management.NFCEE_DISCOVER_CMD, 			"RSP": NFCEE_Management.NFCEE_DISCOVER_RSP, 				"NTF": NFCEE_Management.NFCEE_DISCOVER_NTF},
		'01':  {"CMD": NFCEE_Management.NFCEE_MODE_SET_CMD, 			"RSP": NFCEE_Management.NFCEE_MODE_SET_RSP, 				"NTF": NFCEE_Management.NFCEE_MODE_SET_NTF},
		'02':  {																													"NTF": NFCEE_Management.NFCEE_STATUS_NTF},
		'03':  {"CMD": NFCEE_Management.NFCEE_POWER_AND_LINK_CNTRL_CMD, "RSP": NFCEE_Management.NFCEE_POWER_AND_LINK_CNTRL_RSP},
		# 4 ~ 63 RFU
	},
    # Table 181. [SN2x0 NFCC-NCI] extensions to Control Messages
    # Table 13. SN2x0 NFCC-NCI additional commands/notifications
    "Proprietary": { 
        # SN2x0
        '00':  {"CMD": Proprietary.CORE_SET_POWER_MODE_CMD,     "RSP": Proprietary.CORE_SET_POWER_MODE_RSP}, # 12.5.1
        '01':  {"CMD": Proprietary.SET_NFC_SERVICE_STATUS_CMD,  "RSP": Proprietary.SET_NFC_SERVICE_STATUS_RSP},
        '02':  {"CMD": Proprietary.NCI_PROPRIETARY_ACT_CMD, 	"RSP": Proprietary.NCI_PROPRIETARY_ACT_RSP}, # 9.2.1
        '04':  {																									"NTF": Proprietary.APDU_LOGGING_NTF},
        '14':  {"CMD": Proprietary.RF_GET_TRANSITION_CMD, 		"RSP": Proprietary.RF_GET_TRANSITION_RSP, }, # 13.6
        '17':  {																									"NTF": Proprietary.WTX_NTF},
        '1C':  {"CMD": Proprietary.LOW_POWER_TAG_REMOVAL_CMD,   "RSP": Proprietary.LOW_POWER_TAG_REMOVAL_RSP},
        '1E':  {"CMD": Proprietary.SYSTEM_ESE_POWER_CYCLE_CMD, 	"RSP": Proprietary.SYSTEM_ESE_POWER_CYCLE_RSP},
        '1F':  {"CMD": Proprietary.COLD_RESET_CMD,              "RSP": Proprietary.COLD_RESET_RSP,					"NTF": Proprietary.COLD_RESET_NTF},
        '21':  {"CMD": Proprietary.FLUSH_SRAM_AO_TO_FLASH_CMD, 	"RSP": Proprietary.FLUSH_SRAM_AO_TO_FLASH_RSP},
        # '25':  {																									"NTF": Proprietary.LPCD_FPC_NTF}, 找不到實作
        '30':  {"CMD": Proprietary.TEST_PRBS_CMD,				"RSP": Proprietary.TEST_PRBS_RSP},			# TEST_PRBS
        '32':  {"CMD": Proprietary.READ_OPTION_CMD,    			"RSP": Proprietary.READ_OPTION_RSP}, # AST 測試的東西 (AST Loop 1)
        # '32':  {"CMD": Proprietary.READ_TXLDO_CURRENT_CMD,    	"RSP": Proprietary.READ_TXLDO_CURRENT_RSP}, # AST 測試的東西 (AST Loop 1)
        # '32':  {"CMD": Proprietary.READ_RSSI_CMD,      			"RSP": Proprietary.READ_RSSI_RSP}, 			# AST 測試的東西 (AST Loop 2)
        # '32':  {"CMD": Proprietary.RF_TEST_API_CMD,      		"RSP": Proprietary.RF_TEST_API_RSP}, 		# RF_TEST_API
        '33':  {"CMD": Proprietary.TEST_PRBS_CARD_CMD,      	"RSP": Proprietary.TEST_PRBS_CARD_RSP},		# TEST_PRBS_CARD
        '35':  {																									"NTF": Proprietary.L1_DEBUG_NTF},
        '36':  {																									"NTF": Proprietary.L2_DEBUG_NTF},
        '3D':  {"CMD": Proprietary.RF_SPC_CMD, 					"RSP": Proprietary.RF_SPC_RSP,						"NTF": Proprietary.RF_SPC_NTF},		# RF_SPC
        '3E':  {"CMD": Proprietary.TEST_SWP_CMD, 				"RSP": Proprietary.TEST_SWP_RSP, 					"NTF": Proprietary.TEST_SWP_NTF}, 	# AST 測試的東西
        '3F':  {"CMD": Proprietary.OPTIONAL_CMD, 				"RSP": Proprietary.OPTIONAL_RSP,}, 		# AST 測試的東西 (AST Loop 1)
        # '3F':  {"CMD": Proprietary.AST_UTILITY_CMD, 			"RSP": Proprietary.AST_UTILITY_RSP,}, 		# AST 測試的東西 (AST Loop 1)
        # '3F':  {"CMD": Proprietary.DPC_HELPER_CMD, 				"RSP": Proprietary.DPC_HELPER_RSP,}, 			# AST 測試的東西 (AST Loop 1)
        # '3F':  {"CMD": Proprietary.SWITCH_RF_FIELD_CMD, 		"RSP": Proprietary.SWITCH_RF_FIELD_RSP,}, 	# AST 測試的東西 (AST Loop 1)
	},
	"HDLL": {
		# CMD OP Codes
		'F0': HDLL.DL_RESET,
		'F1': HDLL.DL_GET_VERSION,
		'F2': HDLL.DL_GET_SESSION_STATE,
		'F4': HDLL.DL_GET_DIE_ID,
		'E0': HDLL.DL_CHECK_INTEGRITY,
		'C0': HDLL.DL_SEC_WRITE,
		'C1': HDLL.DL_CERT_FRAME,
		# RSP OP Codes
		'00': HDLL.DL_OK,
		'01': HDLL.EDL_INVALID_ADDR,
		'02': HDLL.EDL_GENERIC_ERROR,
		'0B': HDLL.EDL_UNKNOW_CMD,
		'0C': HDLL.EDL_ABORTED_CMD,
		'1E': HDLL.EDL_ADDR_RANGE_OFL_ERROR,
		'1F': HDLL.EDL_BUFFER_OFL_ERROR,
		'20': HDLL.EDL_MEM_BSY,
		'21': HDLL.EDL_SIGNATURE_ERROR,
		'24': HDLL.EDL_FIRMWARE_VERSION_ERROR,
		'28': HDLL.EDL_PROTOCOL_ERROR,
		'2D': HDLL.PH_STATUS_DL_FIRST_CHUNK,
		'2E': HDLL.PH_STATUS_DL_NEXT_CHUNK,
		'31': HDLL.PH_STATUS_EDL_CERT_ERROR,
	}
}

def HDLL(raw, mode):
	global HDLL_CMD
	first_oct_hex = raw[0:2]
	first_oct_b = bin(int(first_oct_hex,16))[2::].zfill(8)
	chunk = first_oct_b[2:3]

	hdll_payload = 2
	frame_len = int(first_oct_b[3:] + bin(int(raw[hdll_payload:(hdll_payload+2*1)],16))[2::].zfill(8), 2)
	# print("  * Frame Len:", frame_len)
	hdll_payload = hdll_payload + 2*1

	op_code = raw[hdll_payload:(hdll_payload+2*1)]
	# print("  * Op Code:", op_code)
	hdll_payload = hdll_payload + 2*1

	msg = raw[hdll_payload:(hdll_payload+2*(frame_len-1))]
	# print("  * Payload:", msg)
	hdll_payload = hdll_payload + 2*(frame_len-1)

	function = f"{tbl_nci_ctrl["HDLL"][op_code]}"
	function_name = function.split(" ")[1]
	print("  << Nxp HDLL: "+function_name+" >>  ", end="")
	if(mode == 1):
		print(raw)
	elif(mode == 2):
		print("")

	if(chunk == '01'):
		print("  * Chunk:", chunk)

	check = tbl_nci_ctrl["HDLL"][op_code](frame_len, msg, HDLL_CMD)
	# print("  * Frame Len:", frame_len)
	# print("  * Op Code:", op_code)
	# print("  * Payload:", msg)
	HDLL_CMD = op_code

	crc = raw[hdll_payload:(hdll_payload+2*2)]
	print("  * CRC:", crc, "(CRC-16-CCITT-FALSE)")
	hdll_payload = hdll_payload + 2*2
	
	if(hdll_payload != len(raw) or check+2 != frame_len*2):
		print("")
		print("Error: Payload error!!")
		print("  check:", int(check/2), "Octet(s)")
		print("  Packet Len:", len(raw)/2, "Octet(s)")
		print("  Frame Len:", frame_len, "Octet(s)")
		
	print("#end")
