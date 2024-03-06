from nci_decode_pkg import __table__ as NFC_table

#	    Jimmt Chen  	#
#	Done on: 2024/2/17	#

# 20 00
def CORE_RESET_CMD(raw):
	"""""""""""""""
		[CORE_RESET_CMD]
	Reset Type: 1 Octet
	"""""""""""""""
	# print("CORE_RESET_CMD")
	p_payload = 0

	reset_type = raw[p_payload:(p_payload + 2*1)]
	print("- Reset Type: "+NFC_table.tbl_rst_msg.get(reset_type,"RFU")+" ("+reset_type+")")
	p_payload = p_payload + 2*1
	print("\n#end")

# 40 00
def CORE_RESET_RSP(raw):
	"""""""""""""""
		[CORE_RESET_RSP]
    Status: 1 Octet
	"""""""""""""""
	# print("CORE_RESET_RSP")
	p_payload = 0

	status = raw[p_payload:(p_payload+2*1)]	
	print("- Status: "+NFC_table.tbl_status_codes.get(status, "RFU (0xE0-0xFF: For proprietary use.)")+" ("+status+")")
	p_payload = p_payload + 2*1
	print("\n#end")

# 60 00
def CORE_RESET_NTF(raw):
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
	p_payload = 0

	rst_trig = raw[p_payload:(p_payload+2*1)]
	print("- Rest Trigger: "+NFC_table.tbl_rst_trig.get(rst_trig, "RFU (0xA0-0xFF: For proprietary use)")+" ("+rst_trig+")")
	p_payload = p_payload + 2*1

	cfg_status = raw[p_payload:(p_payload+2*1)]
	print("- Configuration Status: "+NFC_table.tbl_cfg_status.get(cfg_status, "RFU")+" ("+cfg_status+")")
	p_payload = p_payload + 2*1

	nci_ver = raw[p_payload:(p_payload+2*1)]
	print("- NCI Version: "+NFC_table.tbl_nci_ver.get(nci_ver, "RFU")+" ("+nci_ver+")")
	p_payload = p_payload + 2*1

	mfg_id = raw[p_payload:(p_payload+2*1)]
	if(mfg_id == "00"):
		print("- Manufacturer ID: Information is not available.")
	else:
		print("- Manufacturer ID: "+mfg_id)
	p_payload = p_payload + 2*1

	mfg_spec_info_len = raw[p_payload:(p_payload+2*1)]
	n = int(mfg_spec_info_len, 16)
	if(mfg_spec_info_len == 0):
		print("- Manufacturer Specific Information Length: Information is not available.")
	else:
		print("- Manufacturer Specific Information Length: "+str(n)+" ("+mfg_spec_info_len+")")
		p_payload = p_payload + 2*1

		print("- Manufacturer Specific Information: "+raw[p_payload:(p_payload+2*n)])
		for i in range (n):
			print("  -- octet"+str(i)+": "+bin(int(raw[p_payload:(p_payload+2*1)],16))[2::].zfill(8)+" ("+raw[p_payload:(p_payload+2*1)]+")") # 之後再看看要不要做其他處理
			p_payload = p_payload + 2*1
	print("\n#end")

# 20 01
def CORE_INIT_CMD(raw):
	"""""""""""""""
		[CORE_INIT_CMD]
	Feature Enable: 2 Octets
	"""""""""""""""
	# print("CORE_INIT_CMD")
	feature = raw[0:(2*2)]
	print("- Feature Enable: "+feature+" --refer to Table 9")
	print("  -- octet0: "+bin(int(feature[0:2],16))[2::].zfill(8)+" ("+feature[0:2]+")")
	print("  -- octet1: "+bin(int(feature[2:4],16))[2::].zfill(8)+" ("+feature[2:4]+")")
	print("\n#end")

# 40 01
def CORE_INIT_RSP(raw):
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
	p_payload = 0

	status = raw[p_payload:(p_payload+2*1)]	
	print("- Status: "+NFC_table.tbl_status_codes.get(status,"RFU")+" ("+status+")")
	p_payload = p_payload + 2*1

	nfcc_feature = raw[p_payload:(p_payload+2*4)]
	print("- NFCC Features: "+nfcc_feature+" --refer to table 10")
	oct_0 = bin(int(nfcc_feature[0:2],16))[2::].zfill(8)
	print("  -- octet0: "+oct_0+" ("+nfcc_feature[0:2]+")")
	print('{0:<40}'.format("    * "+"Active Communication Mode: "), end="")
	if(oct_0[3:4] == "1"):
		print("Support")
	else:
		print("Not support")
	print('{0:<40}'.format("    * "+"HCI Network Support: "), end="")
	if(oct_0[4:5] == "1"):
		print("As defined in [ETSI_102622]")
	else:
		print("Not implement")
	print('{0:<40}'.format("    * "+"Discovery Cfg Mode: "), end="")
	if(oct_0[5:7] == "00"):
		print("The DH is the only entity that configures the NFCC.")
	elif(oct_0[5:7] == "01"):
		print("The NFCC can receive configurations from the DH and other NFCEEs.")
	else:
		print("RFU")
	print('{0:<40}'.format("    * "+"Discovery Frequency Cfg: "), end="")
	if(oct_0[7:] == "1"):
		print("Supported.")
	else:
		print("Ignored, the value of 0x01 SHALL be used by the NFCC.")
	oct_1 = bin(int(nfcc_feature[2:4],16))[2::].zfill(8)
	print("  -- octet1: "+oct_1+" ("+nfcc_feature[2:4]+")")
	for i in range(6,0,-1):
		print('{0:<40}'.format("    * "+NFC_table.tbl_nfcc_feat_oct1.get(i,"RFU")+": "), end="")
		if(oct_1[7-i:8-i] == "1"):
			print("Support")
		else:
			print("Not support")
	oct_2 = bin(int(nfcc_feature[4:6],16))[2::].zfill(8)
	print("  -- octet2: "+oct_2+" ("+nfcc_feature[4:6]+")")
	for i in range(3,-1,-1):
		print('{0:<40}'.format("    * "+NFC_table.tbl_nfcc_feat_oct2.get(i,"RFU")+": "), end="")
		if(oct_2[7-i:8-i] == "1"):
			print("Support")
		else:
			print("Not support")
	oct_3 = bin(int(nfcc_feature[6:8],16))[2::].zfill(8)
	print("  -- octet3: "+oct_3+" ("+nfcc_feature[6:8]+")")
	print('{0:<40}'.format("    * "+"Octet 3 is reserved for proprietary capabilities"))
	p_payload = p_payload + 2*4
	
	max_logical_conn = raw[p_payload:(p_payload+2*1)]
	if(int(max_logical_conn, 16) >= 15): # 0x0F - 0xFF
		print("- Max Logical Connections: RFU ("+max_logical_conn+")")
	else: # 0x00 - 0x0E
		print("- Max Logical Connections:", int(max_logical_conn, 16), "("+max_logical_conn+")")
	p_payload = p_payload + 2*1

	max_router_tbl_size = raw[p_payload:(p_payload+2*2)]
	print("- Max Routing Table Size: "+max_router_tbl_size)
	p_payload = p_payload + 2*2

	max_ctl_pkg_size = raw[p_payload:(p_payload+2*1)]
	if(int(max_ctl_pkg_size, 16) < 32): # Invalid
		print("- Max Control Packet Payload Size: Invalid size ("+max_ctl_pkg_size+")")
	else: # 32 - 255
		print("- Max Control Packet Payload Size:", int(max_ctl_pkg_size, 16), "("+max_ctl_pkg_size+")")
	p_payload = p_payload + 2*1
	
	max_static_hci_conn_pkg_size = raw[p_payload:(p_payload+2*1)]
	print("- Max Data Packet Payload Size of the Static HCI Connection:", int(max_static_hci_conn_pkg_size, 16), "("+max_static_hci_conn_pkg_size+")")
	p_payload = p_payload + 2*1

	static_hci_conn_cr_num = raw[p_payload:(p_payload+2*1)]
	print("- Number of Credits of the Static HCI Connection:", int(static_hci_conn_cr_num, 16), "("+static_hci_conn_cr_num+")")
	p_payload = p_payload + 2*1
	
	max_nfc_v_size = raw[p_payload:(p_payload+2*2)]
	print("- Max NFC-V RF Frame Size: "+max_nfc_v_size)
	p_payload = p_payload + 2*2

	num_of_support_rf_if = raw[p_payload:(p_payload+2*1)]
	n = int(num_of_support_rf_if, 16)
	print("- Number of Supported RF Interfaces:", n, "("+num_of_support_rf_if+")")
	p_payload = p_payload + 2*1	
	
	rf_if = raw[p_payload:]
	print("- Supported RF Interface: "+rf_if+"\n")
	list_payload = 0
	for i in range(n):
		print("  -- [RF_IF_"+str(i)+"] --  ")
		if_val = rf_if[list_payload:(list_payload+2*1)]
		if((int(if_val,16) >= 128) & (int(if_val,16) <= 254)):
			if_val = '80-FE'
		print("  -- Interface: "+NFC_table.tbl_rf_if.get(if_val,"RFU")+" ("+rf_if[list_payload:(list_payload+2*1)]+")")
		list_payload = list_payload + 2*1
		x = int(rf_if[list_payload:(list_payload+2*1)], 16)
		print("  -- Number of Extensions:", x, "("+rf_if[list_payload:(list_payload+2*1)]+")")
		list_payload = list_payload + 2*1
		for j in range(x):
			print("  -- Extension "+str(j)+": "+NFC_table.tbl_rf_if_exten.get(rf_if[list_payload:(list_payload+2*1)],"RFU (0x80-0xFE: For proprietary use)")+" ("+rf_if[list_payload:(list_payload+2*1)]+")")
			list_payload = list_payload + 2*1
		print("")
	p_payload = p_payload + list_payload
	print("#end")

# 20 02
def CORE_SET_CONFIG_CMD(raw):
	"""""""""""""""
		[CORE_SET_CONFIG_CMD]
	Number of Parameters: 	1 Octet (n)
	Parameter [1..n]: 		m+2 Octets
	﹂	ID:					﹂	1 Octet
	﹂	Len: 				﹂	1 Octet (m)
	﹂	Val:				﹂	m Octet(s)
	"""""""""""""""
	# print("CORE_SET_CONFIG_CMD")
	p_payload = 0

	num_of_parameter = raw[p_payload:(p_payload+2*1)]
	n = int(num_of_parameter, 16)
	print("- Number of Parameters:", n, "("+num_of_parameter+")\n")
	p_payload = p_payload + 2*1
	
	# print("- Parameter:")
	for i in range(n):
		print("  -- [Parameter_"+str(i)+"] --  ")
		id = raw[p_payload:(p_payload+2*1)]
		if((int(id ,16) >= 160) & (int(id, 16) <= 254)):
			id = 'A0-FE'
		print("  -- ID: "+NFC_table.tbl_cfg_para.get(id,"RFU")+" ("+raw[p_payload:(p_payload+2*1)]+")")
		p_payload = p_payload + 2*1
		
		id_len = raw[p_payload:(p_payload+2*1)]
		m = int(id_len, 16)
		print("  -- Len:", m, "("+id_len+")")
		p_payload = p_payload + 2*1
		
		if (m != 0):
			id_val = raw[p_payload:(p_payload+2*m)]
			print("  -- Val: "+id_val)
			p_payload = p_payload + 2*m
		print("")
	print("#end")

# 40 02
def CORE_SET_CONFIG_RSP(raw):
	"""""""""""""""
		[CORE_SET_CONFIG_RSP]
	Status: 				1 Octet
	Number of Parameters: 	1 Octet (n)
	Parameter ID [0..n]: 	1 Octet
	"""""""""""""""
	# print("CORE_SET_CONFIG_RSP")
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]	
	print("- Status: "+NFC_table.tbl_status_codes.get(status,"RFU")+" ("+status+")")
	p_payload = p_payload + 2*1
	
	num_of_parameter=raw[p_payload:(p_payload+2*1)]
	n = int(num_of_parameter, 16)
	print("- Number of Parameters:", n, "("+num_of_parameter+")")
	p_payload = p_payload + 2*1
	
	if(n != 0):
		print("- Parameter ID:")
		for i in range(n):
			para_id = raw[p_payload:(p_payload+2*1)]
			if((int(para_id ,16) >= 160) & (int(para_id, 16) <= 254)):
				para_id = 'A0-FE'
			print("  -- ID "+str(i)+":", end=" ")
			print(NFC_table.tbl_cfg_para.get(para_id,"RFU")+" ("+raw[p_payload:(p_payload+2*1)]+")")
			p_payload = p_payload + 2*1
	print("\n#end")

# 20 03
def CORE_GET_CONFIG_CMD(raw):
	"""""""""""""""
		[CORE_GET_CONFIG_CMD]
	Number of Parameters: 	1 Octet (n)
	Parameter ID [0..n]: 	1 Octet
	"""""""""""""""
	# print("CORE_GET_CONFIG_CMD")
	p_payload = 0

	num_of_parameter = raw[p_payload:(p_payload+2*1)]
	n = int(num_of_parameter, 16)
	print("- Number of Parameters:", n, "("+num_of_parameter+")")
	p_payload = p_payload + 2*1
	
	print("- Parameter ID:")
	for i in range(n):
		para_id = raw[p_payload:(p_payload+2*1)]
		if((int(para_id ,16) >= 160) & (int(para_id, 16) <= 254)):
			para_id = 'A0-FE'
		print("  -- ID "+str(i)+":", end=" ")
		print(NFC_table.tbl_cfg_para.get(para_id,"RFU")+" ("+raw[p_payload:(p_payload+2*1)]+")")
		p_payload = p_payload + 2*1
	print("\n#end")

# 40 03
def CORE_GET_CONFIG_RSP(raw):
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
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]	
	print("- Status: "+NFC_table.tbl_status_codes.get(status,"RFU")+" ("+status+")")
	p_payload = p_payload + 2*1
	
	num_of_parameter = raw[p_payload:(p_payload+2*1)]
	n = int(num_of_parameter, 16)
	print("- Number of Parameters:", n, "("+num_of_parameter+")\n")
	p_payload = p_payload + 2*1
	
	# print("- Parameter:")
	for i in range(n):
		print("  -- [Parameter_"+str(i)+"] --  ")
		id = raw[p_payload:(p_payload+2*1)]
		if((int(id ,16) >= 160) & (int(id, 16) <= 254)):
			id = 'A0-FE'
		print("  -- ID: "+NFC_table.tbl_cfg_para.get(id,"RFU")+" ("+raw[p_payload:(p_payload+2*1)]+")")
		p_payload = p_payload + 2*1
		
		id_len = raw[p_payload:(p_payload+2*1)]
		m = int(id_len, 16)
		print("  -- Len:", m, "("+id_len+")")
		p_payload = p_payload + 2*1
		
		if (m != 0):
			id_val = raw[p_payload:(p_payload+2*m)]
			print("  -- Val: "+id_val)
			p_payload = p_payload + 2*m
		print("")
	print("#end")

# 20 04
def CORE_CONN_CREATE_CMD(raw):
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
	p_payload = 0

	d_type = raw[p_payload:(p_payload+2*1)]	
	print("- Destination Type: "+NFC_table.tbl_dest_type.get(d_type,"RFU")+" ("+d_type+")")
	p_payload = p_payload + 2*1

	num_of_parameter = raw[p_payload:(p_payload+2*1)]
	n = int(num_of_parameter, 16)
	print("- Number of Destination-specific Parameters:", n, "("+num_of_parameter+")\n")
	p_payload = p_payload + 2*1
	
	# print("- Destination-specific Parameter:")
	for i in range(n):
		print("  -- [Dest-spec Parameter_"+str(i)+"] --  ")
		ds_type = raw[p_payload:(p_payload+2*1)]	
		print("  -- Type: "+NFC_table.tbl_d_spec_type.get(ds_type,"RFU")+" ("+ds_type+")")
		p_payload = p_payload + 2*1
		
		ds_len = raw[p_payload:(p_payload+2*1)]
		m = int(ds_len, 16)
		print("  -- Len:", m, "("+ds_len+")")
		p_payload = p_payload + 2*1
		
		ds_val = raw[p_payload:(p_payload+2*m)]
		print("  -- Val: "+ds_val)
		# RF Discovery ID(Table 67) + RF Protocol(Table 133)
		if(ds_type == "00"):
			type_val_octet0 = ds_val[0:2]
			if(type_val_octet0 == "00" or type_val_octet0 == "FF"):
				print("  ---- RF Discovery ID: "+"RFU"+" ("+type_val_octet0+")")
			else:
				print("  ---- RF Discovery ID: "+"Dynamically assigned by the NFCC"+" ("+type_val_octet0+")")
			
			type_val_octet1=ds_val[2:4]
			print("  ---- RF Protocol: "+NFC_table.tbl_rf_proto.get(type_val_octet1,"0x08-0x7F & 0xFF: RFU, 0x80-0xFE: For proprietary use")+" ("+type_val_octet1+")")			
		
		# NFCEE ID(Table 116) + NFCEE Interface Protocol(Table 136)
		elif(ds_type == "01"):
			type_val_octet0=ds_val[0:2]
			if(type_val_octet0 == "00"):
				print("  ---- NFCEE ID: "+"DH NFCEE ID"+" ("+type_val_octet0+")")
			elif(type_val_octet0 == "01"):
				print("  ---- NFCEE ID: "+"HCI Network NFCEE ID"+" ("+type_val_octet0+")")
			elif(type_val_octet0 == "FF"):
				print("  ---- NFCEE ID: "+"RFU"+" ("+type_val_octet0+")")
			else:
				print("  ---- NFCEE ID: "+type_val_octet0)
				print("0x02-0x0F: Reserved for further static IDs.")
				print("0x10-0x7F: NFCEE IDs, for NFCEEs that are outside of the HCI Network. Dynamically assigned by the NFCC.")
				print("0x80-0xFE: HCI-NFCEE IDs, for HCI-NFCEEs that are inside of the HCI Network. Dynamically assigned by the NFCC.")
			
			type_val_octet1 = ds_val[2:4]
			print("  ---- NFCEE Interface Protocol: "+NFC_table.tbl_nfcee_proto.get(type_val_octet1,"0x04-0x7F:RFU 0x80-0xFE:proprietary use")+" ("+type_val_octet1+")")			
		
		else:
			print("  -- Val: "+ds_val)
			print("0x02-0x9F: RFU")
			print("0xA0-0xFF: For proprietary use")
		p_payload = p_payload + 2*m
		print("")
	print("#end")

# 40 04
def CORE_CONN_CREATE_RSP(raw):
	"""""""""""""""
		[CORE_CONN_CREATE_RSP]
	Status: 						1 Octet
	Max Data Packet Payload Size:	1 Octet
	Initial Number of Credits:		1 Octet
	Conn ID:						1 Octet
	"""""""""""""""
	# print("CORE_CONN_CREATE_RSP")
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]	
	print("- Status: "+NFC_table.tbl_status_codes.get(status,"RFU")+" ("+status+")")
	p_payload = p_payload + 2*1
	
	max_data_size = raw[p_payload:(p_payload+2*1)]	
	print("- Max Data Packet Payload Size: ", int(max_data_size), "("+max_data_size+")")
	p_payload = p_payload + 2*1

	num_credits = raw[p_payload:(p_payload+2*1)]
	if(num_credits == "FF"):
		print("- Initial Number of Credits: "+"Data flow control is not used"+" ("+num_credits+")")
	else:
		print("- Initial Number of Credits: ", int(num_credits), "("+num_credits+")")
	p_payload = p_payload + 2*1

	conn_id = raw[p_payload:(p_payload+2*1)]
	print("- Conn ID: "+NFC_table.tbl_conn_id.get(bin(int(conn_id, 16))[2::].zfill(8)[4::],"Dynamically assigned by the NFCC")+" ("+conn_id+")")
	p_payload = p_payload + 2*1
	print("\n#end")

# 20 05
def CORE_CONN_CLOSE_CMD(raw):
	"""""""""""""""
		[CORE_CONN_CLOSE_CMD]
	Conn ID:	1 Octet
	"""""""""""""""
	# print("CORE_CONN_CLOSE_CMD")
	p_payload = 0
	
	conn_id = raw[p_payload:(p_payload+2*1)]
	print("- Conn ID: "+NFC_table.tbl_conn_id.get(bin(int(conn_id, 16))[2::].zfill(8)[4::],"Dynamically assigned by the NFCC")+" ("+conn_id+")")
	p_payload = p_payload + 2*1
	print("\n#end")

# 40 05
def CORE_CONN_CLOSE_RSP(raw):
	"""""""""""""""
		[CORE_CONN_CLOSE_RSP]
	Status:		1 Octet
	"""""""""""""""
	# print("CORE_CONN_CLOSE_RSP")
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]	
	print("- Status: "+NFC_table.tbl_status_codes.get(status,"RFU")+" ("+status+")")
	p_payload = p_payload + 2*1
	print("\n#end")

# 60 06
def CORE_CONN_CREDITS_NTF(raw):
	"""""""""""""""
		[CORE_CONN_CREDITS_NTF]
	Number of Entries:	1 Octet (n)
	Entry [1..n]: 		2 Octets
	﹂	Conn ID:		﹂	1 Octet
	﹂	Credits: 		﹂	1 Octet
	"""""""""""""""
	# print("CORE_CONN_CREDITS_NTF")
	p_payload = 0
	
	num_of_entries = raw[p_payload:(p_payload+2*1)]
	n = int(num_of_entries, 16)
	print("- Number of Entries:", n, "("+num_of_entries+")\n")
	p_payload = p_payload + 2*1
	
	# print("- Entry:")
	for i in range(n):
		print("  -- [Entry_"+str(i)+"] --  ")
		conn_id = raw[p_payload:(p_payload+2*1)]	
		print("  -- Conn ID: "+NFC_table.tbl_conn_id.get(bin(int(conn_id, 16))[2::].zfill(8)[4::],"Dynamically assigned by the NFCC")+" ("+conn_id+")")
		p_payload = p_payload + 2*1

		credits = raw[p_payload:(p_payload+2*1)]	
		print("  -- Credits: "+credits)
		p_payload = p_payload + 2*1
		print("")
	print("#end")

# 60 07
def CORE_GENERIC_ERROR_NTF(raw):
	"""""""""""""""
		[CORE_GENERIC_ERROR_NTF]
	Status:		1 Octet
	"""""""""""""""
	# print("CORE_GENERIC_ERROR_NTF")
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]	
	print("- Status: "+NFC_table.tbl_status_codes.get(status,"RFU")+" ("+status+")")
	p_payload = p_payload + 2*1
	print("\n#end")

# 60 08
def CORE_INTERFACE_ERROR_NTF(raw):
	"""""""""""""""
		[CORE_INTERFACE_ERROR_NTF]
	Status:		1 Octet
	Conn ID:	1 Octet
	"""""""""""""""
	# print("CORE_INTERFACE_ERROR_NTF")
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]	
	print("- Status: "+NFC_table.tbl_status_codes.get(status,"RFU")+" ("+status+")")
	p_payload = p_payload + 2*1

	conn_id=raw[p_payload:(p_payload+2*1)]	
	print("- Conn ID: "+NFC_table.tbl_conn_id.get(bin(int(conn_id, 16))[2::].zfill(8)[4::],"Dynamically assigned by the NFCC")+" ("+conn_id+")")
	p_payload = p_payload + 2*1
	print("\n#end")

# 20 09
def CORE_SET_POWER_SUB_STATE_CMD(raw):
	"""""""""""""""
		[CORE_SET_POWER_SUB_STATE_CMD]
	Power State:	1 Octet
	"""""""""""""""
	# print("CORE_SET_POWER_SUB_STATE_CMD")
	p_payload = 0

	pwr_state = raw[p_payload:(p_payload+2*1)]
	if(pwr_state == "00"):
		print("- Power State: "+"Switched On State"+" ("+pwr_state+")")
	elif(pwr_state == "01"):
		print("- Power State: "+"Switched On Sub-State 1"+" ("+pwr_state+")")
	elif(pwr_state == "02"):
		print("- Power State: "+"Switched On Sub-State 2"+" ("+pwr_state+")")
	elif(pwr_state == "03"):
		print("- Power State: "+"Switched On Sub-State 3"+" ("+pwr_state+")")
	else:
		print("- Power State: "+"RFU"+" ("+pwr_state+")")
	print("\n#end")

# 40 09
def CORE_SET_POWER_SUB_STATE_RSP(raw):
	"""""""""""""""
		[CORE_SET_POWER_SUB_STATE_RSP]
    Status: 1 Octet
	"""""""""""""""
	# print("CORE_SET_POWER_SUB_STATE_RSP")
	p_payload = 0

	status = raw[p_payload:(p_payload+2*1)]	
	print("- Status: "+NFC_table.tbl_status_codes.get(status, "RFU (0xE0-0xFF: For proprietary use.)")+" ("+status+")")
	p_payload = p_payload + 2*1
	print("\n#end")
