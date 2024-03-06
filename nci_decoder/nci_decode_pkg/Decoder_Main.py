from nci_decode_pkg import NCI_Core
from nci_decode_pkg import RF_Management
from nci_decode_pkg import NFCEE_Management

# Message Type
tbl_mt_val = {
	"000":	"DATA",
	"001":	"CMD",
	"010":	"RSP",
	"011":	"NTF",
}

#table 139
tbl_gid_val = {
	"0000":	"NCI Core",
	"0001":	"RF Management",
	"0010":	"NFCEE Management",
	"0011":	"NFCC Management",
	"0100":	"Test Management",
	"1111":	"Proprietary",
}

tbl_nci_cmd = {
	"NCI Core": {
		"000000":  {"CMD": NCI_Core.CORE_RESET_CMD, 				"RSP": NCI_Core.CORE_RESET_RSP, 					"NTF": NCI_Core.CORE_RESET_NTF},
		"000001":  {"CMD": NCI_Core.CORE_INIT_CMD, 					"RSP": NCI_Core.CORE_INIT_RSP},
		"000010":  {"CMD": NCI_Core.CORE_SET_CONFIG_CMD, 			"RSP": NCI_Core.CORE_SET_CONFIG_RSP},
		"000011":  {"CMD": NCI_Core.CORE_GET_CONFIG_CMD, 			"RSP": NCI_Core.CORE_GET_CONFIG_RSP},
		"000100":  {"CMD": NCI_Core.CORE_CONN_CREATE_CMD, 			"RSP": NCI_Core.CORE_CONN_CREATE_RSP},
		"000101":  {"CMD": NCI_Core.CORE_CONN_CLOSE_CMD, 			"RSP": NCI_Core.CORE_CONN_CLOSE_RSP},
		"000110":  {																				                    "NTF": NCI_Core.CORE_CONN_CREDITS_NTF},
		"000111":  {																				                    "NTF": NCI_Core.CORE_GENERIC_ERROR_NTF},
		"001000":  {																				                    "NTF": NCI_Core.CORE_INTERFACE_ERROR_NTF},
		"001001":  {"CMD": NCI_Core.CORE_SET_POWER_SUB_STATE_CMD,	"RSP": NCI_Core.CORE_SET_POWER_SUB_STATE_RSP},
		# 10 ~ 63 RFU
	},
	"RF Management": {
		"000000":  {"CMD": RF_Management.RF_DISCOVER_MAP_CMD,			    "RSP": RF_Management.RF_DISCOVER_MAP_RSP},
		"000001":  {"CMD": RF_Management.RF_SET_LISTEN_MODE_ROUTING_CMD,   	"RSP": RF_Management.RF_SET_LISTEN_MODE_ROUTING_RSP},
		"000010":  {"CMD": RF_Management.RF_GET_LISTEN_MODE_ROUTING_CMD,   	"RSP": RF_Management.RF_GET_LISTEN_MODE_ROUTING_RSP, 	"NTF": RF_Management.RF_GET_LISTEN_MODE_ROUTING_NTF},
		"000011":  {"CMD": RF_Management.RF_DISCOVER_CMD, 				    "RSP": RF_Management.RF_DISCOVER_RSP, 				    "NTF": RF_Management.RF_DISCOVER_NTF},
		"000100":  {"CMD": RF_Management.RF_DISCOVER_SELECT_CMD, 		    "RSP": RF_Management.RF_DISCOVER_SELECT_RSP},
		"000101":  {																				                                "NTF": RF_Management.RF_INTF_ACTIVATED_NTF},
		"000110":  {"CMD": RF_Management.RF_DEACTIVATE_CMD, 				"RSP": RF_Management.RF_DEACTIVATE_RSP, 				"NTF": RF_Management.RF_DEACTIVATE_NTF},
		"000111":  {																				                                "NTF": RF_Management.RF_FIELD_INFO_NTF},
		"001000":  {"CMD": RF_Management.RF_T3T_POLLING_CMD, 			    "RSP": RF_Management.RF_T3T_POLLING_RSP, 				"NTF": RF_Management.RF_T3T_POLLING_NTF},
		"001001":  {																				                                "NTF": RF_Management.RF_NFCEE_ACTION_NTF},
		"001010":  {																				                                "NTF": RF_Management.RF_NFCEE_DISCOVERY_REQ_NTF},
		"001011":  {"CMD": RF_Management.RF_PARAMETER_UPDATE_CMD, 		    "RSP": RF_Management.RF_PARAMETER_UPDATE_RSP},
		"001100":  {"CMD": RF_Management.RF_INTF_EXT_START_CMD, 			"RSP": RF_Management.RF_INTF_EXT_START_RSP},
		"001101":  {"CMD": RF_Management.RF_INTF_EXT_STOP_CMD, 				"RSP": RF_Management.RF_INTF_EXT_STOP_RSP},
		"001110":  {"CMD": RF_Management.RF_EXT_AGG_ABORT_CMD, 				"RSP": RF_Management.RF_EXT_AGG_ABORT_RSP},
		"001111":  {"CMD": RF_Management.RF_NDEF_ABORT_CMD, 				"RSP": RF_Management.RF_NDEF_ABORT_RSP},
		"010000":  {"CMD": RF_Management.RF_ISO_DEP_NAK_PRESENCE_CMD, 		"RSP": RF_Management.RF_ISO_DEP_NAK_PRESENCE_RSP, 		"NTF": RF_Management.RF_ISO_DEP_NAK_PRESENCE_NTF},
		"010001":  {"CMD": RF_Management.RF_SET_FORCED_NFCEE_ROUTING_CMD,	"RSP": RF_Management.RF_SET_FORCED_NFCEE_ROUTING_RSP},
		# 18 ~ 63 RFU
	},
	"NFCEE Management": {
		"000000":  {"CMD": NFCEE_Management.NFCEE_DISCOVER_CMD, 			"RSP": NFCEE_Management.NFCEE_DISCOVER_RSP, 				"NTF": NFCEE_Management.NFCEE_DISCOVER_NTF},
		"000001":  {"CMD": NFCEE_Management.NFCEE_MODE_SET_CMD, 			"RSP": NFCEE_Management.NFCEE_MODE_SET_RSP, 				"NTF": NFCEE_Management.NFCEE_MODE_SET_NTF},
		"000010":  {																													"NTF": NFCEE_Management.NFCEE_STATUS_NTF},
		"000011":  {"CMD": NFCEE_Management.NFCEE_POWER_AND_LINK_CNTRL_CMD, "RSP": NFCEE_Management.NFCEE_POWER_AND_LINK_CNTRL_RSP},
		# 4 ~ 63 RFU
	},
	# "NFCC Management": {
		# 0 ~ 31 RFU
		# 32 ~ 63 For proprietary use
	# },
	# "Test Management": {
		# 0 ~ 31 RFU
		# 32 ~ 63 For proprietary use
	# },
	# "Proprietary": {}
}

# def RFU(raw):
# 	print("RFU")

# def Proprietary(raw):
# 	print("Proprietary")

# direct = {"CMD": "DH ---> NFCC", "RSP": "DH <--- NFCC", "NTF": "DH <--- NFCC"}

# def DATA_PACKET_PROCESS(raw):
# 	print("- data:", raw)

def NFC_NCI_DECODER(string):
	raw = string.replace(" ", "")
	raw = raw.upper()
	# print("")
	first_oct_hex = raw[0:2]
	first_oct_b = bin(int(first_oct_hex,16))[2::].zfill(8)
	mt_val = tbl_mt_val.get(first_oct_b[0:3],"RFU")
	pbf = first_oct_b[3:4]
	if(pbf == "1"):
		print('{0:^25}'.format("PBF: "+pbf))

	payload_len = raw[4:6]
	
	payload_raw = raw[6::] # oct 3 ~ (2+L)

	# if(mt_val == "RFU"):
	# 	print("- NCI: RFU Data")
	# 	print("")

	if(mt_val == "DATA"):
		# print('{0:^25}'.format(direct.get(mt_val,"DH -><- NFCC")))
		print('{0:^25}'.format("NCI: DATA Packet"))
		conn_id = first_oct_b[4::]
		cr = bin(int(raw[2:4],16))[2::].zfill(8)[6::]
		print("- Connection ID: " + conn_id, end=' ')
		if(conn_id == "0000"): 
			print("(Static RF Connection between the DH and a Remote NFC Endpoint)")
		elif(conn_id == "0001"): 
			print("(Static HCI Connection between the DH and the HCI Network)")
		else: 
			print("(Dynamically assigned by the NFCC)")
		print("- Credits:", cr)
		print("- Payload Length:", int(payload_len,16), "("+payload_len+")")
		print("- data:", payload_raw)
		print("#end")

	else:   # Control Packet
		# print('{0:^25}'.format(direct.get(mt_val,"DH -><- NFCC")))
		gid_val = tbl_gid_val.get(first_oct_b[4::]) # GID
		oid = bin(int(raw[2:4],16))[2::].zfill(8)[2::]
		# print(mt_val, "->", gid_val, "->", oid, "("+raw[0:4]+")")
		# if (gid_val == "NFCC Management"):
		# 	print('{0:^25}'.format("NCI CMD: Proprietary"))
		# 	print("")
		# elif (gid_val == "NFCC Management"):
		# 	print('{0:^25}'.format("NCI CMD: Proprietary"))
		# 	print("")
		# else:
		try:
			function = f"{tbl_nci_cmd[gid_val][oid][mt_val]}"
			function_name = function.split(" ")[1]
			print('{0:^25}'.format(function_name))
			tbl_nci_cmd[gid_val][oid][mt_val](payload_raw) # 呼叫對應func，輸入rawdata
		except KeyError as e:
			print("\033[31mError:\033[0m May be \033[33mRFU\033[0m or \033[33mProprietary\033[0m, please check the documentation.\n")
			print("#end")
			# print(e)

# def main():
# 	raw = input("Input the NCI raw data: ")
# 	NFC_NCI_DECODER(raw)

# if __name__ == '__main__':
# 	main()