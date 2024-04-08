from nfc_forum_2_0_pkg import NCI_Core
from nfc_forum_2_0_pkg import RF_Management
from nfc_forum_2_0_pkg import NFCEE_Management



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
		# 12 ~ 63 RFU
	},
	"NFCEE Management": {
		'00':  {"CMD": NFCEE_Management.NFCEE_DISCOVER_CMD, 			"RSP": NFCEE_Management.NFCEE_DISCOVER_RSP, 				"NTF": NFCEE_Management.NFCEE_DISCOVER_NTF},
		'01':  {"CMD": NFCEE_Management.NFCEE_MODE_SET_CMD, 			"RSP": NFCEE_Management.NFCEE_MODE_SET_RSP, 				"NTF": NFCEE_Management.NFCEE_MODE_SET_NTF},
		'02':  {																													"NTF": NFCEE_Management.NFCEE_STATUS_NTF},
		'03':  {"CMD": NFCEE_Management.NFCEE_POWER_AND_LINK_CNTRL_CMD, "RSP": NFCEE_Management.NFCEE_POWER_AND_LINK_CNTRL_RSP},
		# 4 ~ 63 RFU
	},
}