import nfc_forum_2_3_pkg.__table__ as NFC_table
import __pkg_import__ as pkg_import

# 20 00
def CORE_RESET_CMD(raw, vendor="None", model="None"):
	"""""""""""""""
		[CORE_RESET_CMD]
	Reset Type: 1 Octet
	"""""""""""""""
	# print("CORE_RESET_CMD")
	# NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0

	reset_type = raw[p_payload:(p_payload + 2*1)]
	print("  * Reset Type: "+NFC_table.tbl_cfg_status.get(reset_type,"RFU ("+reset_type+")"))
	p_payload = p_payload + 2*1
	# print("")
	return p_payload

# 40 00
def CORE_RESET_RSP(raw, vendor="None", model="None"):
	"""""""""""""""
		[CORE_RESET_RSP]
    Status: 1 Octet
	"""""""""""""""
	# print("CORE_RESET_RSP")
	# NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0
	status = raw[p_payload:(p_payload+2*1)]
	print("  * Status: "+NFC_table.tbl_status_codes.get(status, "RFU ("+status+")"))
	p_payload = p_payload + 2*1
	# print("")
	return p_payload

# 60 00
def CORE_RESET_NTF(raw, vendor="None", model="None"):
	"""""""""""""""
		[CORE_RESET_NTF]
    Reset Trigger: 								1 Octet
    Configuration Status: 						1 Octet
    NCI Version: 								1 Octet
    Manufacturer ID: 							1 Octet
    Manufacturer Specific Information Length: 	1 Octet
    Manufacturer Specific Information: 			n Octets
	"""""""""""""""
	# print("CORE_RESET_NTF")
	# NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0

	rst_trig = raw[p_payload:(p_payload+2*1)]
	print("  * Rest Trigger: "+NFC_table.tbl_rst_trig.get(rst_trig, "RFU ("+rst_trig+")"))
	p_payload = p_payload + 2*1

	cfg_status = raw[p_payload:(p_payload+2*1)]
	print("  * Config Status: "+NFC_table.tbl_cfg_status.get(cfg_status, "RFU ("+cfg_status+")"))
	p_payload = p_payload + 2*1

	nci_ver = raw[p_payload:(p_payload+2*1)]
	print("  * NCI Version: ", end="")
	major = int(nci_ver[0:1], 16)
	minor = int(nci_ver[1:2], 16)
	print(str(major)+"."+str(minor), "("+nci_ver+")")
	p_payload = p_payload + 2*1

	mfg_id = raw[p_payload:(p_payload+2*1)]
	if(mfg_id == "00"):
		print("  * Manufacturer ID: Info is not available.")
	else:
		print("  * Manufacturer ID:", mfg_id)
	p_payload = p_payload + 2*1

	mfg_spec_info_len = raw[p_payload:(p_payload+2*1)]
	n = int(mfg_spec_info_len, 16)
	p_payload = p_payload + 2*1
	if(mfg_spec_info_len != 0):
		print("  * Manufacturer Specific Info: "+raw[p_payload:(p_payload+2*n)])
		p_payload = p_payload + 2*n
	# print("")
	return p_payload

# 20 01
def CORE_INIT_CMD(raw, vendor="None", model="None"):
	"""""""""""""""
		[CORE_INIT_CMD]
	Feature Enable: 2 Octets
	"""""""""""""""
	# print("CORE_INIT_CMD")
	# NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0
	feature = raw[p_payload:(p_payload+2*2)]
	print("  * Feature Enable: "+feature+" --refer to Table 9")
	# print("    * octet0: "+bin(int(feature[0:2],16))[2::].zfill(8)+" ("+feature[0:2]+")")
	# print("    * octet1: "+bin(int(feature[2:4],16))[2::].zfill(8)+" ("+feature[2:4]+")")
	p_payload = p_payload + 2*2
	# print("")
	return p_payload

# 40 01
def CORE_INIT_RSP(raw, vendor="None", model="None"):
	"""""""""""""""
		[CORE_INIT_RSP]
	Status:														1 Octet
	NFCC Features:												4 Octets
	Max Logical Connections:									1 Octet
	Max Routing Table Size:										2 Octets
	Max Control Packet Payload Size:							1 Octet
	Max Data Packet Payload Size of the Static HCI Connection:	1 Octet
	Number of Credits of the Static HCI Connection:				1 Octet
	Max NFC-V RF Frame Size: 									2 Octets
	Number of Supported RF Interfaces: 							1 Octet (n)
	Supported RF Interface [1..n]:								x+2 Octets
	﹂	Interface: 												﹂	1 Octet
	﹂	Number of Extensions: 									﹂	1 Octet (x)
	﹂	Extension List [0..x]:									﹂	x Octet(s)
	"""""""""""""""
	# print("CORE_INIT_RSP")
	# NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0

	status = raw[p_payload:(p_payload+2*1)]	
	print("  * Status: "+NFC_table.tbl_status_codes.get(status,"RFU ("+status+")"))
	p_payload = p_payload + 2*1

	nfcc_feature = raw[p_payload:(p_payload+2*4)]
	print("  * NFCC Features: "+nfcc_feature) # +" --refer to table 10"

	oct_0 = bin(int(nfcc_feature[0:2],16))[2::].zfill(8)
	print("    * octet0: "+oct_0)
	print('{0:<40}'.format("     ~ "+"Removal Detection in Poll Mode: "), end="") # new
	if(oct_0[2:3] == "1"):
		print("Support")
	else:
		print("Not support")
	print('{0:<40}'.format("     ~ "+"Active Communication Mode: "), end="")
	if(oct_0[3:4] == "1"):
		print("Support")
	else:
		print("Not support")
	print('{0:<40}'.format("     ~ "+"HCI Network Support: "), end="")
	if(oct_0[4:5] == "1"):
		print("As defined in [ETSI_102622]")
	else:
		print("Not implement")
	print('{0:<40}'.format("     ~ "+"Discovery Cfg Mode: "), end="")
	if(oct_0[5:7] == "00"):
		print("The DH is the only entity that configs the NFCC.")
	elif(oct_0[5:7] == "01"):
		print("The NFCC can receive configs from the DH and other NFCEEs.")
	else:
		print("RFU")
	print('{0:<40}'.format("     ~ "+"Discovery Freq Cfg: "), end="")
	if(oct_0[7:] == "1"):
		print("Supported in RF_DISCOVER_CMD")
	else:
		print("Ignored in RF_DISCOVER_CMD")

	oct_1 = bin(int(nfcc_feature[2:4],16))[2::].zfill(8)
	print("    * octet1: "+oct_1)
	for i in range(6,0,-1):
		print('{0:<40}'.format("     ~ "+NFC_table.tbl_nfcc_feat_oct1.get(i,"RFU")+": "), end="")
		if(oct_1[7-i:8-i] == "1"):
			print("Support")
		else:
			print("Not support")
	
	oct_2 = bin(int(nfcc_feature[4:6],16))[2::].zfill(8)
	print("    * octet2: "+oct_2)
	for i in range(3,-1,-1):
		print('{0:<40}'.format("     ~ "+NFC_table.tbl_nfcc_feat_oct2.get(i,"RFU")+": "), end="")
		if(oct_2[7-i:8-i] == "1"):
			print("Support")
		else:
			print("Not support")
	
	oct_3 = bin(int(nfcc_feature[6:8],16))[2::].zfill(8)
	print("    * octet3: "+oct_3)
	print('{0:<40}'.format("     ~ "+"Octet_3 is reserved for proprietary capabilities"))
	p_payload = p_payload + 2*4
	
	max_logical_conn = raw[p_payload:(p_payload+2*1)]
	if(int(max_logical_conn, 16) >= 15 and vendor == "None"): # 0x0F - 0xFF
		print("  * Max Logical Connections: RFU ("+max_logical_conn+")")
	else: # 0x00 - 0x0E
		print("  * Max Logical Connections:", int(max_logical_conn, 16))
	p_payload = p_payload + 2*1

	max_router_tbl_size = raw[p_payload:(p_payload+2*2)]
	print("  * Max Routing Table Size:", int(max_router_tbl_size, 16))
	p_payload = p_payload + 2*2

	max_ctl_pkg_size = raw[p_payload:(p_payload+2*1)]
	if(int(max_ctl_pkg_size, 16) < 32): # Invalid
		print("  * Max Control Packet Payload Size: Invalid size ("+max_ctl_pkg_size+")")
	else: # 32 - 255
		print("  * Max Control Packet Payload Size:", int(max_ctl_pkg_size, 16))
	p_payload = p_payload + 2*1
	
	max_static_hci_conn_pkg_size = raw[p_payload:(p_payload+2*1)]
	print("  * Max Data Packet Payload Size of the Static HCI Connection:", int(max_static_hci_conn_pkg_size, 16))
	p_payload = p_payload + 2*1

	static_hci_conn_cr_num = raw[p_payload:(p_payload+2*1)]
	print("  * Number of Credits of the Static HCI Connection:", int(static_hci_conn_cr_num, 16))
	p_payload = p_payload + 2*1
	
	max_nfc_v_size = raw[p_payload:(p_payload+2*2)]
	print("  * Max NFC-V RF Frame Size:", int(max_nfc_v_size, 16))
	p_payload = p_payload + 2*2

	num_of_support_rf_if = raw[p_payload:(p_payload+2*1)]
	n = int(num_of_support_rf_if, 16)
	print("  * Number of Supported RF Interfaces:", n)
	p_payload = p_payload + 2*1	
	
	rf_if = raw[p_payload:]
	print("  * Supported RF Interface: "+rf_if)
	list_payload = 0
	for i in range(n):
		print("   ~ [RF_IF_"+str(i)+"] ~  ")
		if_val = rf_if[list_payload:(list_payload+2*1)]
		print("    * Interface: "+NFC_table.tbl_rf_if.get(if_val,"RFU ("+if_val+")"))
		list_payload = list_payload + 2*1
		x = int(rf_if[list_payload:(list_payload+2*1)], 16)
		print("    * Number of Extensions:", x)
		list_payload = list_payload + 2*1
		for j in range(x):
			print("    * Extension "+str(j)+": "+NFC_table.tbl_rf_if_exten.get(rf_if[list_payload:(list_payload+2*1)],"RFU ("+rf_if[list_payload:(list_payload+2*1)]+")"))
			list_payload = list_payload + 2*1
		# print("")
	p_payload = p_payload + list_payload
	# print("#end")
	return p_payload

# 20 02
def CORE_SET_CONFIG_CMD(raw, vendor="None", model="None"):
	"""""""""""""""
		[CORE_SET_CONFIG_CMD]
	Number of Parameters: 	1 Octet (n)
	Parameter [1..n]: 		m+2 Octets
	﹂	ID:					﹂	1 Octet
	﹂	Len: 				﹂	1 Octet (m)
	﹂	Val:				﹂	m Octet(s)
	"""""""""""""""
	# print("CORE_SET_CONFIG_CMD")
	# NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0

	num_of_parameter = raw[p_payload:(p_payload+2*1)]
	n = int(num_of_parameter, 16)
	print("  * Number of Params:", n)
	p_payload = p_payload + 2*1
	
	# print("  * Parameter:")
	for i in range(n):
		print("   ~ [Param_"+str(i)+"] ~  ")
		para_id = raw[p_payload:(p_payload+2*1)]
		print("    * ID: "+NFC_table.tbl_cfg_para.get(para_id,"RFU ("+para_id+")"))
		p_payload = p_payload + 2*1
		
		para_len = raw[p_payload:(p_payload+2*1)]
		m = int(para_len, 16)
		print("    * Len:", m)
		p_payload = p_payload + 2*1
		
		if (m != 0):
			para_val = raw[p_payload:(p_payload+2*m)]
			# print("    * Val: "+para_val)
			VALUE_OF_CFG_PARA(para_id, para_val, NFC_table)
			p_payload = p_payload + 2*m
		# print("")
	# print("#end")
	return p_payload

# 40 02
def CORE_SET_CONFIG_RSP(raw, vendor="None", model="None"):
	"""""""""""""""
		[CORE_SET_CONFIG_RSP]
	Status: 				1 Octet
	Number of Parameters: 	1 Octet (n)
	Parameter ID [0..n]: 	1 Octet
	"""""""""""""""
	# print("CORE_SET_CONFIG_RSP")
	# NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]	
	print("  * Status: "+NFC_table.tbl_status_codes.get(status,"RFU ("+status+")"))
	p_payload = p_payload + 2*1
	
	num_of_parameter=raw[p_payload:(p_payload+2*1)]
	n = int(num_of_parameter, 16)
	print("  * Number of Params:", n)
	p_payload = p_payload + 2*1
	
	if(n != 0):
		print("  * Param ID:")
		for i in range(n):
			para_id = raw[p_payload:(p_payload+2*1)]
			print("    * ID "+str(i)+":", end=" ")
			print(NFC_table.tbl_cfg_para.get(para_id,"RFU ("+para_id+")"))
			p_payload = p_payload + 2*1
	# print("")
	return p_payload

# 20 03
def CORE_GET_CONFIG_CMD(raw, vendor="None", model="None"):
	"""""""""""""""
		[CORE_GET_CONFIG_CMD]
	Number of Parameters: 	1 Octet (n)
	Parameter ID [0..n]: 	1 Octet
	"""""""""""""""
	# print("CORE_GET_CONFIG_CMD")
	# NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0

	num_of_parameter = raw[p_payload:(p_payload+2*1)]
	n = int(num_of_parameter, 16)
	print("  * Number of Params:", n)
	p_payload = p_payload + 2*1
	
	print("  * Param ID:")
	for i in range(n):
		para_id = raw[p_payload:(p_payload+2*1)]
		print("    * ID "+str(i)+":", end=" ")
		print(NFC_table.tbl_cfg_para.get(para_id,"RFU ("+para_id+")"))
		p_payload = p_payload + 2*1
	# print("")
	return p_payload

# 40 03
def CORE_GET_CONFIG_RSP(raw, vendor="None", model="None"):
	"""""""""""""""
		[CORE_GET_CONFIG_RSP]
	Status: 				1 Octet
	Number of Parameters: 	1 Octet (n)
	Parameter [1..n]: 		m+2 Octets
	﹂	ID:					﹂	1 Octet
	﹂	Len: 				﹂	1 Octet (m)
	﹂	Val:				﹂	m Octet(s)
	"""""""""""""""
	# print("CORE_GET_CONFIG_RSP")
	# NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]	
	print("  * Status: "+NFC_table.tbl_status_codes.get(status,"RFU ("+status+")"))
	p_payload = p_payload + 2*1
	
	num_of_parameter = raw[p_payload:(p_payload+2*1)]
	n = int(num_of_parameter, 16)
	print("  * Number of Params:", n)
	p_payload = p_payload + 2*1
	
	# print("  * Parameter:")
	for i in range(n):
		print("   ~ [Param_"+str(i)+"] ~  ")
		para_id = raw[p_payload:(p_payload+2*1)]
		print("    * ID: "+NFC_table.tbl_cfg_para.get(para_id,"RFU ("+para_id+")"))
		p_payload = p_payload + 2*1
		
		id_len = raw[p_payload:(p_payload+2*1)]
		m = int(id_len, 16)
		print("    * Len:", m)
		p_payload = p_payload + 2*1
		
		if (m != 0):
			id_val = raw[p_payload:(p_payload+2*m)]
			# print("    * Val: "+id_val)
			VALUE_OF_CFG_PARA(para_id, id_val, NFC_table)
			p_payload = p_payload + 2*m
		# print("")
	return p_payload

# 20 04
def CORE_CONN_CREATE_CMD(raw, vendor="None", model="None"):
	"""""""""""""""
		[CORE_CONN_CREATE_CMD]
	Destination Type: 							1 Octet
	Number of Destination-specific Parameters: 	1 Octet (n)
	Destination-specific Parameter [0..n]: 		m+2 Octets
	﹂	Type:									﹂	1 Octet
	﹂	Len: 									﹂	1 Octet (m)
	﹂	Val:									﹂	m Octet(s)
	"""""""""""""""
	# print("CORE_CONN_CREATE_CMD")
	# NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0

	d_type = raw[p_payload:(p_payload+2*1)]	
	print("  * Destination Type: "+NFC_table.tbl_dest_type.get(d_type,"RFU")+" ("+d_type+")")
	p_payload = p_payload + 2*1

	num_of_parameter = raw[p_payload:(p_payload+2*1)]
	n = int(num_of_parameter, 16)
	print("  * Number of Destination-specific Params:", n)
	p_payload = p_payload + 2*1
	
	# print("  * Destination-specific Parameter:")
	for i in range(n):
		print("   ~ [Dest-spec Parameter_"+str(i)+"] ~  ")
		ds_type = raw[p_payload:(p_payload+2*1)]	
		print("    * Type: "+NFC_table.tbl_d_spec_type.get(ds_type,"RFU ("+ds_type+")"))
		p_payload = p_payload + 2*1
		
		ds_len = raw[p_payload:(p_payload+2*1)]
		m = int(ds_len, 16)
		print("    * Len:", m)
		p_payload = p_payload + 2*1
		
		ds_val = raw[p_payload:(p_payload+2*m)]
		print("    * Val: "+ds_val)
		# RF Discovery ID(Table 67) + RF Protocol(Table 133)
		if(ds_type == "00"):
			type_val_octet0 = ds_val[0:2]
			print("      * RF Discovery ID:", NFC_table.tbl_rf_dis_id.get(type_val_octet0, type_val_octet0))
			
			type_val_octet1=ds_val[2:4]
			print("      * RF Protocol: "+NFC_table.tbl_rf_proto.get(type_val_octet1,"RFU ("+type_val_octet1+")"))			
		
		# NFCEE ID(Table 116) + NFCEE Interface Protocol(Table 136)
		elif(ds_type == "01"):
			type_val_octet0 = ds_val[0:2]
			if(type_val_octet0 == "00"):
				print("      * NFCEE ID: "+"DH NFCEE ID")
			elif(type_val_octet0 == "01"):
				print("      * NFCEE ID: "+"HCI Network NFCEE ID")
			elif(type_val_octet0 == "FF"):
				print("      * NFCEE ID: "+"RFU"+" ("+type_val_octet0+")")
			else:
				print("      * NFCEE ID: "+type_val_octet0)
				print("0x02-0x0F: Reserved for further static IDs.")
				print("0x10-0x7F: NFCEE IDs, for NFCEEs that are outside of the HCI Network. Dynamically assigned by the NFCC.")
				print("0x80-0xFE: HCI-NFCEE IDs, for HCI-NFCEEs that are inside of the HCI Network. Dynamically assigned by the NFCC.")
			
			type_val_octet1 = ds_val[2:4]
			print("      * NFCEE Interface Protocol: "+NFC_table.tbl_nfcee_proto.get(type_val_octet1,"RFU ("+type_val_octet1+")"))
		
		else:
			print("    * Val: "+ds_val)
			print("0x02-0x9F: RFU")
			print("0xA0-0xFF: For proprietary use")
		p_payload = p_payload + 2*m
		# print("")
	# print("#end")
	return p_payload

# 40 04
def CORE_CONN_CREATE_RSP(raw, vendor="None", model="None"):
	"""""""""""""""
		[CORE_CONN_CREATE_RSP]
	Status: 						1 Octet
	Max Data Packet Payload Size:	1 Octet
	Initial Number of Credits:		1 Octet
	Conn ID:						1 Octet
	"""""""""""""""
	# print("CORE_CONN_CREATE_RSP")
	# NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]	
	print("  * Status: "+NFC_table.tbl_status_codes.get(status,"RFU ("+status+")"))
	p_payload = p_payload + 2*1
	
	max_data_size = raw[p_payload:(p_payload+2*1)]	
	print("  * Max Data Packet Payload Size:", int(max_data_size, 16))
	p_payload = p_payload + 2*1

	num_credits = raw[p_payload:(p_payload+2*1)]
	if(num_credits == "FF"):
		print("  * Initial Number of Credits: "+"Data flow control is not used")
	else:
		print("  * Initial Number of Credits:", int(num_credits, 16))
	p_payload = p_payload + 2*1

	conn_id = raw[p_payload:(p_payload+2*1)]
	print("  * Conn ID:", int(conn_id, 16), "("+NFC_table.tbl_conn_id.get(bin(int(conn_id, 16))[2::].zfill(8)[4::],"Dynamically assigned by the NFCC"))
	p_payload = p_payload + 2*1
	# print("")
	return p_payload

# 20 05
def CORE_CONN_CLOSE_CMD(raw, vendor="None", model="None"):
	"""""""""""""""
		[CORE_CONN_CLOSE_CMD]
	Conn ID:	1 Octet
	"""""""""""""""
	# print("CORE_CONN_CLOSE_CMD")
	# NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0
	
	conn_id = raw[p_payload:(p_payload+2*1)]
	print("  * Conn ID:", int(conn_id, 16), "("+NFC_table.tbl_conn_id.get(bin(int(conn_id, 16))[2::].zfill(8)[4::],"Dynamically assigned by the NFCC"))
	p_payload = p_payload + 2*1
	# print("")
	return p_payload

# 40 05
def CORE_CONN_CLOSE_RSP(raw, vendor="None", model="None"):
	"""""""""""""""
		[CORE_CONN_CLOSE_RSP]
	Status:		1 Octet
	"""""""""""""""
	# print("CORE_CONN_CLOSE_RSP")
	# NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]	
	print("  * Status: "+NFC_table.tbl_status_codes.get(status,"RFU ("+status+")"))
	p_payload = p_payload + 2*1
	# print("")
	return p_payload

# 60 06
def CORE_CONN_CREDITS_NTF(raw, vendor="None", model="None"):
	"""""""""""""""
		[CORE_CONN_CREDITS_NTF]
	Number of Entries:	1 Octet (n)
	Entry [1..n]: 		2 Octets
	﹂	Conn ID:		﹂	1 Octet
	﹂	Credits: 		﹂	1 Octet
	"""""""""""""""
	# print("CORE_CONN_CREDITS_NTF")
	# NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0
	
	num_of_entries = raw[p_payload:(p_payload+2*1)]
	n = int(num_of_entries, 16)
	print("  * Number of Entries:", n)
	p_payload = p_payload + 2*1
	
	# print("  * Entry:")
	for i in range(n):
		print("   ~ [Entry_"+str(i)+"] ~  ")
		conn_id = raw[p_payload:(p_payload+2*1)]
		print("    * Conn ID:", int(conn_id, 16), "("+NFC_table.tbl_conn_id.get(bin(int(conn_id, 16))[2::].zfill(8)[4::],"Dynamically assigned by the NFCC"))
		p_payload = p_payload + 2*1

		credits = raw[p_payload:(p_payload+2*1)]	
		print("    * Credits:", int(credits, 16))
		p_payload = p_payload + 2*1
		# print("")
	# print("#end")
	return p_payload

# 60 07
def CORE_GENERIC_ERROR_NTF(raw, vendor="None", model="None"):
	"""""""""""""""
		[CORE_GENERIC_ERROR_NTF]
	Status:		1 Octet
	"""""""""""""""
	# print("CORE_GENERIC_ERROR_NTF")
	# NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]	
	print("  * Status: "+NFC_table.tbl_status_codes.get(status,"RFU ("+status+")"))
	p_payload = p_payload + 2*1
	# print("")
	return p_payload

# 60 08
def CORE_INTERFACE_ERROR_NTF(raw, vendor="None", model="None"):
	"""""""""""""""
		[CORE_INTERFACE_ERROR_NTF]
	Status:		1 Octet
	Conn ID:	1 Octet
	"""""""""""""""
	# print("CORE_INTERFACE_ERROR_NTF")
	# NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]	
	print("  * Status: "+NFC_table.tbl_status_codes.get(status,"RFU ("+status+")"))
	p_payload = p_payload + 2*1

	conn_id = raw[p_payload:(p_payload+2*1)]	
	print("  * Conn ID: ", int(conn_id, 16),"("+NFC_table.tbl_conn_id.get(bin(int(conn_id, 16))[2::].zfill(8)[4::],"Dynamically assigned by the NFCC"))
	p_payload = p_payload + 2*1
	# print("")
	return p_payload

# 20 09
def CORE_SET_POWER_SUB_STATE_CMD(raw, vendor="None", model="None"):
	"""""""""""""""
		[CORE_SET_POWER_SUB_STATE_CMD]
	Power State:	1 Octet
	"""""""""""""""
	# print("CORE_SET_POWER_SUB_STATE_CMD")
	# NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0

	pwr_state = raw[p_payload:(p_payload+2*1)]
	if(pwr_state == "00"):
		print("  * Power State: "+"Switched On State")
	elif(pwr_state == "01"):
		print("  * Power State: "+"Switched On Sub-State 1")
	elif(pwr_state == "02"):
		print("  * Power State: "+"Switched On Sub-State 2")
	elif(pwr_state == "03"):
		print("  * Power State: "+"Switched On Sub-State 3")
	else:
		print("  * Power State: "+"RFU"+" ("+pwr_state+")")
	p_payload = p_payload + 2*1
	# print("")
	return p_payload

# 40 09
def CORE_SET_POWER_SUB_STATE_RSP(raw, vendor="None", model="None"):
	"""""""""""""""
		[CORE_SET_POWER_SUB_STATE_RSP]
    Status: 1 Octet
	"""""""""""""""
	# print("CORE_SET_POWER_SUB_STATE_RSP")
	# NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0

	status = raw[p_payload:(p_payload+2*1)]	
	print("  * Status: "+NFC_table.tbl_status_codes.get(status, "RFU ("+status+")"))
	p_payload = p_payload + 2*1
	# print("")
	return p_payload


def VALUE_OF_CFG_PARA(id, val, NFC_table):
	# Common Discovery Parameters
	if(id == '00'): # TOTAL_DURATION
		print("    * Val:", int(val, 16), "ms")
	elif(id == '02'): # CON_DISCOVERY_PARAM
		val_b = bin(int(val, 16))[2::].zfill(8)
		print("    * Val:", val_b, "("+val+")")
		print('{0:<20}'.format("     ~ Polling Mode:"), end=" ")
		if(val_b[7:8] == '1'):
			print("Enabled")
		else:
			print("Disabled")
		print('{0:<20}'.format("     ~ DH-NFCEE:"), end=" ")
		if(val_b[6:7] == '1'):
			print("Disabled")
		else:
			print("Enabled")
	elif(id == '03'): # POWER_STATE
		print("    * Val:", val)
		if(val == '02'):
			print("     ~ The config params of the current CORE_GET_CONFIG_CMD apply for Switched Off State")
		else:
			print("     ~ RFU")
	# Poll Mode – Discovery Parameters (NFC-A, NFC-B, NFC-F, ISO-DEP, NFC-V)
	elif(id == '08' or id == '11' or id == '19'): # PA_BAIL_OUT, PB_BAIL_OUT, PF_BAIL_OUT
		print("    * Val: "+val)
		if(val == '00'):
			print("     ~ No bail out during Poll Mode in Discovery activity.")
		elif(val == '01'):
			print("     ~ Bail out Poll Mode when NFC Technology has been detected.")
		else:
			print("     ~ RFU")
	elif(id == '09' or id == '14' or id == '1A' or id == '2F'): # PA_DEVICES_LIMIT, PB_DEVICES_LIMIT, PF_DEVICES_LIMIT, PV_DEVICES_LIMIT
		print("    * Val:", val)
		print("     ~ As defined in [ACTIVITY] for the Collision Resolution Activity.")
	elif(id == '10'): # PB_AFI
		print("    * Val: ", val)
		print("     ~ Application family identifier (as defined in [DIGITAL]).")
	elif(id == '12'): # PB_ATTRIB_PARAM1
		print("    * Val:", val)
		print("     ~ The values and coding of this parameter SHALL be as defined in [DIGITAL] for Param 1 of the ATTRIB command.")
	elif(id == '13'): # PB_SENSB_REQ_PARAM
		val_b = bin(int(val, 16))[2::].zfill(8)
		print("    * Val:", val_b, "("+val+")")
		if(val_b[3:4] == '1'):
			print("     ~ Extended SENSB_RES: Support")
		else:
			print("     ~ Extended SENSB_RES: Not support")
	elif(id == '18' or id == '21' or id == '3E' or id == '5B' or id == '68'): # PF_BIT_RATE, PI_BIT_RATE, LB_BIT_RATE, LI_A_BIT_RATE, PACM_BIT_RATE
		print("    * Val:", NFC_table.tbl_bit_rates.get(val, "For proprietary use ("+val+")"))
	elif(id == '20'):
		print("    * Val:", val)
		print("     ~ Higher layer INF field of the ATTRIB Command (as defined in [DIGITAL]).")
	# Poll Mode – NFC-DEP Discovery Parameters
	elif(id == '28'): # PN_NFC_DEP_PSL
		print("    * Val:", val)
		if(val == '00'):
			print("     ~ Highest available Bit Rates and highest available Length Reduction.")
		elif(val == '01'):
			print("     ~ Maintain the Bit Rates and Length Reduction.")
		else: 
			print("     ~ RFU")
	elif(id == '29'): # PN_ATR_REQ_GEN_BYTES
		print("    * Val:", val)
		print("     ~ General Bytes for ATR_REQ.")
	elif(id == '2A' or id == '62'): # PN_ATR_REQ_CONFIG, LN_ATR_RES_CONFIG
		val_b = bin(int(val, 16))[2::].zfill(8)
		print("    * Val:", val_b, "("+val+")")
		print("     ~ Value for LR (as defined in [DIGITAL])")
		print("     ~ NOTE: Needs to be always set to 0x30 for LLCP")
	# Listen Mode – NFC-A Discovery Parameters
	elif(id == '30'): # LA_BIT_FRAME_SDD
		val_b = bin(int(val, 16))[2::].zfill(8)
		print("    * Val:", val_b, "("+val+")")
		print("     ~ Bit Frame SDD value to be sent in Byte 1 of SENS_RES. This is a 5-bit value.")
	elif(id == '31'): # LA_PLATFORM_CONFIG
		val_b = bin(int(val, 16))[2::].zfill(8)
		print("    * Val:", val_b, "("+val+")")
		print("     ~ Bit Frame SDD value to be sent in Byte 2 of SENS_RES. This is a 4-bit value.")
	elif(id == '32'): # LA_SEL_INFO
		val_b = bin(int(val, 16))[2::].zfill(8)
		print("    * Val:", val_b, "("+val+")")
		if(val_b[1:2] == '1'):
			print("     ~ NFC-DEP Protocol: Supported")
		else:
			print("     ~ NFC-DEP Protocol: Not supported")
		if(val_b[2:3] == '1'):
			print("     ~ ISO-DEP Protocol: Supported")
		else:
			print("     ~ ISO-DEP Protocol: Not supported")
	elif(id == '33'): # LA_NFCID1
		print("    * Val:", val)
		print("     ~ NFCID1 as defined in [DIGITAL].")
	# Listen Mode – NFC-B Discovery Parameters
	elif(id == '38'): # LB_SENSB_INFO
		val_b = bin(int(val, 16))[2::].zfill(8)
		print("    * Val:", val_b, "("+val+")")
		if(val_b[7:8] == '1'):
			print("     ~ ISO-DEP Protocol: Supported")
		else:
			print("     ~ ISO-DEP Protocol: Not supported")
	elif(id == '39'): # LB_NFCID0
		print("    * Val:", val)
		print("     ~ NFCID0 as defined in [DIGITAL].")
	elif(id == '3A'): # LB_APPLICATION_DATA
		print("    * Val:", val)
		print("     ~ Application Data (Bytes 6-9) of SENSB_RES (as defined in [DIGITAL]).")
	elif(id == '3B'): # LB_SFGI
		print("    * Val:", val)
		print("     ~ Start-Up Frame Guard Time, as defined in [DIGITAL].")
	elif(id == '3C'): # LB_FWI_ADC_FO
		val_b = bin(int(val, 16))[2::].zfill(8)
		print("    * Val:", val_b, "("+val+")")
		print("     ~ Frame Waiting time Integer:", int(val_b[0:4], 2), "("+val_b[0:4]+")")
		print("     ~ b3 of ADC Coding field of SENSB_RES (Byte 12) as defined in [DIGITAL]", "("+val_b[5:6]+")")
		print("     ~ If set to 1b DID MAY be used. Otherwise it SHALL NOT be used.", "("+val_b[7:8]+")")
	# Listen Mode – T3T Discovery Parameters
	elif(int(id, 16) >= 64 and int(id, 16) <= 79): # LF_T3T_IDENTIFIERS_1~16 (0x40~0x4F)
		print("    * Val:", val)
		print("     ~ System Code of T3T Emulation:", val[0:4])
		print("     ~ NFCID2 for the T3T Platform:", val[4:20])
		print("     ~ PAD0, PAD1, MRTI_check, MRTI_update and PAD2 of SENSF_RES:", val[20:36])
	elif(id == '52'): # LF_T3T_MAX
		if(int(val, 16) <= 16):
			print("    * Val:", int(val, 16))
		else:
			print("    * Val:", "RFU", "("+val+")")
	elif(id == '53'): # LF_T3T_FLAGS
		val_oct0_b = bin(int(val[0:2], 16))[2::].zfill(8)
		val_oct0_b_r = val_oct0_b[8::-1]
		val_oct1_b = bin(int(val[2:4], 16))[2::].zfill(8)
		val_oct1_b_r = val_oct1_b[8::-1]
		val_b_r = val_oct0_b_r + val_oct1_b_r
		print("    * Val:", val_oct0_b, val_oct1_b, "("+val+")")
		for i in range (1, 17):
			print('{0:<30}'.format("     ~ LF_T3T_IDENTIFIERS_"+str(i)+":"), end=" ")
			if(val_b_r[i-1] == '1'):
				print("Enabled")
			else:
				print("Disabled")
	elif(id == '55'): # LF_T3T_RD_ALLOWED
		if(val == '00'):
			print("    * Val:", val)
			print("     ~ The NFCC SHALL NOT include RD bytes in its SENSF_RES if it receives a SENSF_REQ with RC set to 0x02.")
		elif(val == '01'):
			print("    * Val:", val)
			print("     ~ The NFCC MAY include RD bytes in its SENSF_RES if it receives a SENSF_REQ with RC set to 0x02.")
		else:
			print("    * Val:", "RFU", "("+val+")")
	# Listen Mode – NFC-F Discovery Parameters
	elif(id == '50'): # LF_PROTOCOL_TYPE
		val_b = bin(int(val, 16))[2::].zfill(8)
		print("    * Val:", val_b, "("+val+")")
		if(val_b[6:7] == '1'):
			print("     ~ NFC-DEP Protocol: Supported")
		else:
			print("     ~ NFC-DEP Protocol: Not supported")
	# Listen Mode – ISO-DEP Discovery Parameters
	elif(id == '58'): # LI_A_RATS_TB1
		print("    * Val:", val)
		print("     ~ RATS Response Interface Byte TB(1) (defined in [DIGITAL]).")
	elif(id == '59'): # LI_A_HIST_BY
		print("    * Val:", val)
		print("     ~ Historical Bytes (only applicable for Type 4A Tag) (defined in [DIGITAL]).")
	elif(id == '5A'): # LI_B_H_INFO_RESP
		print("    * Val:", val)
		print("     ~ Higher Layer – Response field of the ATTRIB response (defined in [DIGITAL]).")
	elif(id == '5C'): # LI_A_RATS_TC1
		val_b = bin(int(val, 16))[2::].zfill(8)
		print("    * Val:", val_b, "("+val+")")
		print("     ~ If set to 1b DID MAY be used. Otherwise it SHALL NOT be used.", "("+val_b[6:7]+")")
	elif(id == '60'): # LN_WT
		print("    * Val:", int(val, 16), "ms ("+val+")")
		print("     ~ Waiting Time defined in [DIGITAL].")
	elif(id == '61'): # LN_ATR_RES_GEN_BYTES
		print("    * Val:", val)
		print("     ~ General Bytes in ATR_RES (defined in [DIGITAL]).")
	# POLL WLC-P–WLC Parameters (new)
	elif(id == '69'): # WLC-P_CAP_POWER_CLASS
		val_b = bin(int(val, 16))[2::].zfill(8)
		print("    * Val:", val_b, "("+val+")")
	elif(id == '6A'): # TOT_POWER_STEPS
		print("    * Val:", int(val, 16), "step ("+val+")")
	elif(id == '6B'): # WLC_AUTO_CAPABILITIES
		val_b = bin(int(val, 16))[2::].zfill(8)
		print("    * Val:", int(val, 16), "step ("+val+")")
		if(val_b[3:4] == '1'):
			print("     ~ NFCC as Wireless Charging Poller supports the WLC protocol for T5T.")
		if(val_b[4:5] == '1'):
			print("     ~ NFCC as Wireless Charging Poller supports the WLC protocol for T4BT.")
		if(val_b[5:6] == '1'):
			print("     ~ NFCC as Wireless Charging Poller supports the WLC protocol for T4AT.")
		if(val_b[6:7] == '1'):
			print("     ~ NFCC as Wireless Charging Poller supports the WLC protocol for T3T.")
		if(val_b[7:8] == '1'):
			print("     ~ NFCC as Wireless Charging Poller supports the WLC protocol for T2T.")
	# Other Parameters
	elif(id == '80'): # RF_FIELD_INFO
		if(val == '00'):
			print("    * Val:", val)
			print("     ~ The NFCC is not allowed to send RF Field Info NTF to the DH.")
		elif(val == '01'):
			print("    * Val:", val)
			print("     ~ The NFCC is allowed to send RF Field Info NTF to the DH.")
		else:
			print("    * Val:", "RFU", "("+val+")")
	elif(id == '81'): # RF_NFCEE_ACTION
		if(val == '00'):
			print("    * Val:", val)
			print("     ~ The NFCC SHALL NOT send RF_NFCEE_ACTION_NTF to the DH.")
		elif(val == '01'):
			print("    * Val:", val)
			print("     ~ The NFCC SHALL send RF_NFCEE_ACTION_NTF to the DH upon the triggers described in this section.")
		else:
			print("    * Val:", "RFU", "("+val+")")
	elif(id == '82'): # NFCDEP_OP
		val_b = bin(int(val, 16))[2::].zfill(8)
		print("    * Val:", val_b, "("+val+")")
		if(val_b[3:4] == '1'):
			print("     ~ Waiting Time:", "10 or less")
		else:
			print("     ~ Waiting Time:", "WT_(NFCDEP,MAX) or less")
		if(val_b[4:5] == '1'):
			print("     ~ All PDUs indicating chaining (MI bit set) SHALL use the maximum number of Transport Data Bytes.")
		if(val_b[5:6] == '1'):
			print("     ~ Info PDU with no Transport Data Bytes SHALL NOT be sent.")
		if(val_b[6:7] == '1'):
			print("     ~ NFC-DEP Initiator SHALL use the ATTENTION command only as the error recovery procedure described in [DIGITAL].")
		if(val_b[7:8] == '1'):
			print("     ~ NFC-DEP Target SHALL NOT send RTOX requests.")
	elif(id == '83'): # LLCP_VERSION
		major = int(val[0:1], 16)
		minor = int(val[1:2], 16)
		print("    * Val:", str(major)+"."+str(minor), "("+val+")")
	elif(id == '85'): # NFCC_CONFIG_CONTROL
		val_b = bin(int(val, 16))[2::].zfill(8)
		print("    * Val:", val_b, "("+val+")")
		if(val_b[7:8] == '0'):
			print("     ~ NFCC is not allowed to manage RF config.")
		elif(val_b[7:8] == '1'):
			print("     ~ NFCC is allowed to manage RF config.")
	elif(id == '86'): # RF_WLC_STATUS_CONFIG
		print("    * Val:", val)
		if(val == '00'):
			print("     ~ The NFCC is not allowed to send RF_WLC_STATUS_NTF Notifications to the DH.")
		elif(val == '01'):
			print("     ~ The NFCC is allowed to send RF_WLC_STATUS_NTF Notifications to the DH.")
		else:
			print("     ~ 0x02-0x7F RFU, 0x80-0xFF Proprietary")
	else:
		print("    * Val: "+val)