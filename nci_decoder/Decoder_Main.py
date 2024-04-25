def NFC_NCI_DECODER(len, string, vendor, model, mode):
	# NCI_Core, RF_Management, NFCEE_Management, Proprietary = pkg_import.ctrl_import(vendor, model)
	if(vendor.lower() == "nxp"):
		from Nxp_pkg import __ctrl__ as pkg
	else:
		from nfc_forum_2_0_pkg import  __ctrl__ as pkg
	
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

	# tbl_nci_ctrl = {
	# 	"NCI Core": {
	# 		"000000":  {"CMD": NCI_Core.CORE_RESET_CMD, 				"RSP": NCI_Core.CORE_RESET_RSP, 					"NTF": NCI_Core.CORE_RESET_NTF},
	# 		"000001":  {"CMD": NCI_Core.CORE_INIT_CMD, 					"RSP": NCI_Core.CORE_INIT_RSP},
	# 		"000010":  {"CMD": NCI_Core.CORE_SET_CONFIG_CMD, 			"RSP": NCI_Core.CORE_SET_CONFIG_RSP},
	# 		"000011":  {"CMD": NCI_Core.CORE_GET_CONFIG_CMD, 			"RSP": NCI_Core.CORE_GET_CONFIG_RSP},
	# 		"000100":  {"CMD": NCI_Core.CORE_CONN_CREATE_CMD, 			"RSP": NCI_Core.CORE_CONN_CREATE_RSP},
	# 		"000101":  {"CMD": NCI_Core.CORE_CONN_CLOSE_CMD, 			"RSP": NCI_Core.CORE_CONN_CLOSE_RSP},
	# 		"000110":  {																				                    "NTF": NCI_Core.CORE_CONN_CREDITS_NTF},
	# 		"000111":  {																				                    "NTF": NCI_Core.CORE_GENERIC_ERROR_NTF},
	# 		"001000":  {																				                    "NTF": NCI_Core.CORE_INTERFACE_ERROR_NTF},
	# 		"001001":  {"CMD": NCI_Core.CORE_SET_POWER_SUB_STATE_CMD,	"RSP": NCI_Core.CORE_SET_POWER_SUB_STATE_RSP},
	# 		# 10 ~ 63 RFU
	# 	},
	# 	"RF Management": {
	# 		"000000":  {"CMD": RF_Management.RF_DISCOVER_MAP_CMD,			    "RSP": RF_Management.RF_DISCOVER_MAP_RSP},
	# 		"000001":  {"CMD": RF_Management.RF_SET_LISTEN_MODE_ROUTING_CMD,   	"RSP": RF_Management.RF_SET_LISTEN_MODE_ROUTING_RSP},
	# 		"000010":  {"CMD": RF_Management.RF_GET_LISTEN_MODE_ROUTING_CMD,   	"RSP": RF_Management.RF_GET_LISTEN_MODE_ROUTING_RSP, 	"NTF": RF_Management.RF_GET_LISTEN_MODE_ROUTING_NTF},
	# 		"000011":  {"CMD": RF_Management.RF_DISCOVER_CMD, 				    "RSP": RF_Management.RF_DISCOVER_RSP, 				    "NTF": RF_Management.RF_DISCOVER_NTF},
	# 		"000100":  {"CMD": RF_Management.RF_DISCOVER_SELECT_CMD, 		    "RSP": RF_Management.RF_DISCOVER_SELECT_RSP},
	# 		"000101":  {																				                                "NTF": RF_Management.RF_INTF_ACTIVATED_NTF},
	# 		"000110":  {"CMD": RF_Management.RF_DEACTIVATE_CMD, 				"RSP": RF_Management.RF_DEACTIVATE_RSP, 				"NTF": RF_Management.RF_DEACTIVATE_NTF},
	# 		"000111":  {																				                                "NTF": RF_Management.RF_FIELD_INFO_NTF},
	# 		"001000":  {"CMD": RF_Management.RF_T3T_POLLING_CMD, 			    "RSP": RF_Management.RF_T3T_POLLING_RSP, 				"NTF": RF_Management.RF_T3T_POLLING_NTF},
	# 		"001001":  {																				                                "NTF": RF_Management.RF_NFCEE_ACTION_NTF},
	# 		"001010":  {																				                                "NTF": RF_Management.RF_NFCEE_DISCOVERY_REQ_NTF},
	# 		"001011":  {"CMD": RF_Management.RF_PARAMETER_UPDATE_CMD, 		    "RSP": RF_Management.RF_PARAMETER_UPDATE_RSP},
	# 		"001100":  {"CMD": RF_Management.RF_INTF_EXT_START_CMD, 			"RSP": RF_Management.RF_INTF_EXT_START_RSP},
	# 		"001101":  {"CMD": RF_Management.RF_INTF_EXT_STOP_CMD, 				"RSP": RF_Management.RF_INTF_EXT_STOP_RSP},
	# 		"001110":  {"CMD": RF_Management.RF_EXT_AGG_ABORT_CMD, 				"RSP": RF_Management.RF_EXT_AGG_ABORT_RSP},
	# 		"001111":  {"CMD": RF_Management.RF_NDEF_ABORT_CMD, 				"RSP": RF_Management.RF_NDEF_ABORT_RSP},
	# 		"010000":  {"CMD": RF_Management.RF_ISO_DEP_NAK_PRESENCE_CMD, 		"RSP": RF_Management.RF_ISO_DEP_NAK_PRESENCE_RSP, 		"NTF": RF_Management.RF_ISO_DEP_NAK_PRESENCE_NTF},
	# 		"010001":  {"CMD": RF_Management.RF_SET_FORCED_NFCEE_ROUTING_CMD,	"RSP": RF_Management.RF_SET_FORCED_NFCEE_ROUTING_RSP},
	# 		# 18 ~ 63 RFU
	# 	},
	# 	"NFCEE Management": {
	# 		"000000":  {"CMD": NFCEE_Management.NFCEE_DISCOVER_CMD, 			"RSP": NFCEE_Management.NFCEE_DISCOVER_RSP, 				"NTF": NFCEE_Management.NFCEE_DISCOVER_NTF},
	# 		"000001":  {"CMD": NFCEE_Management.NFCEE_MODE_SET_CMD, 			"RSP": NFCEE_Management.NFCEE_MODE_SET_RSP, 				"NTF": NFCEE_Management.NFCEE_MODE_SET_NTF},
	# 		"000010":  {																													"NTF": NFCEE_Management.NFCEE_STATUS_NTF},
	# 		"000011":  {"CMD": NFCEE_Management.NFCEE_POWER_AND_LINK_CNTRL_CMD, "RSP": NFCEE_Management.NFCEE_POWER_AND_LINK_CNTRL_RSP},
	# 		# 4 ~ 63 RFU
	# 	},
	# }
	raw = string.replace(" ", "")
	raw = raw.upper()
	# print("")
	first_oct_hex = raw[0:2]
	first_oct_b = bin(int(first_oct_hex,16))[2::].zfill(8)
	mt_val = tbl_mt_val.get(first_oct_b[0:3],"RFU")
	pbf = first_oct_b[3:4]

	payload_len = raw[4:6]

	# if(mt_val == "RFU"):
	# 	print("* NCI: RFU Data")
	# 	print("")
	if(int(payload_len, 16) == int(len)-3): # 3 Bytes header
		if(mt_val == "DATA" and bin(int(raw[2:4],16))[2::].zfill(8)[:6] == "000000"):
			print("  << NCI: DATA Packet >>  ", end="")
			if(mode == 1):
				print(raw)
			else:
				print("")
			conn_id = first_oct_b[4::]
			cr = bin(int(raw[2:4],16))[2::].zfill(8)[6::]
			print("  * Conn ID:", int(conn_id, 2), end=' ')
			if(conn_id == "0000"): 
				print("(Static: DH -- Remote NFC Endpoint)")
			elif(conn_id == "0001"): 
				print("(Static: DH -- HCI Network)")
			else: 
				print("(Dynamically assigned)")
			print("  * Credits:", int(cr, 2))
			print("  * Payload Length:", int(payload_len,16))
			print("  * data:", raw[6::])
			# Data 封包也有格式需要解析 之後做~~
			# print("")
			if((int(len)-3) != int(payload_len,16)):
				print("Error: Payload error!!")
				print("  Packet Len:", len, "Octet(s)")
				print("  Payload Len:", int(payload_len,16), "Octet(s)")

		else:   # Control Packet	
			gid_val = tbl_gid_val.get(first_oct_b[4::]) # GID
			oid = raw[2:4] # OID
			# if(gid_val != "Proprietary"):
			function = f"{pkg.tbl_nci_ctrl[gid_val][oid][mt_val]}"
			function_name = function.split(" ")[1]
			print("  << "+function_name+" >>  ", end="")
			if(mode == 1):
				print(raw)
			else:
				print("")
			# print("  * Payload Length:", int(payload_len,16))
			check = pkg.tbl_nci_ctrl[gid_val][oid][mt_val](raw[6::]) # 呼叫對應func，輸入rawdata

			if(check != 2*(int(len)-3)):
				print("Error: Payload error!!")
				print("  Packet Len:", len, "Octet(s)")
				print("  Payload Len:", int(payload_len,16), "Octet(s)")
				print("  Check Len:", check/2, "Octet(s)")
		if(pbf == "1"):
			print("PBF: "+pbf)
		print("#end")

	elif(int(first_oct_b[3:] + bin(int(raw[2:4],16))[2::].zfill(8), 2) == int(len)-4): # 2 Bytes header (HDLL) + CRC16 (2 Bytes)
		 # Nxp: Host Data Link Layer (HDLL)
		pkg.HDLL(raw, mode)

	else:
		print("Error: Unknown raw data!")
	

# def main():
# 	raw = input("Input the NCI raw data: ")
# 	NFC_NCI_DECODER(raw)

# if __name__ == '__main__':
# 	main()