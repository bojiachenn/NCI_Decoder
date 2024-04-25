import Nxp_pkg.__table__ as NFC_table
from Nxp_pkg import Proprietary
from nfc_forum_2_0_pkg import NCI_Core as Origin

#       Nxp SN2X0       #

a007 = '0'

# 20 00
def CORE_RESET_CMD(raw):
	"""""""""""""""
		[CORE_RESET_CMD]
	Reset Type: 1 Octet
	"""""""""""""""
	# print("CORE_RESET_CMD")
	p_payload = Origin.CORE_RESET_CMD(raw, "nxp")
	return p_payload

# 40 00
def CORE_RESET_RSP(raw):
	"""""""""""""""
		[CORE_RESET_RSP]
    Status: 1 Octet
	"""""""""""""""
	# print("CORE_RESET_RSP")
	p_payload = Origin.CORE_RESET_RSP(raw, "nxp")
	return p_payload

# 60 00
def CORE_RESET_NTF(raw):
	"""""""""""""""
		[CORE_RESET_NTF]
    Reset Trigger: 								1 Octet
    Configuration Status: 						1 Octet
    NCI Version: 								1 Octet
    Manufacturer ID: 							1 Octet
    Manufacturer Specific Information Length: 	1 Octet
    Manufacturer Specific Information: 			5 Octets
	﹂	Model ID: 								﹂	1 Octet
	﹂	Hw Ver nb: 								﹂	1 Octet
	﹂	ROM Code Ver nb: 						﹂	1 Octet
	﹂	FLASH Ver: 								﹂	2 Octet
	"""""""""""""""
	# print("CORE_RESET_NTF")
	p_payload = 0

	rst_trig = raw[p_payload:(p_payload+2*1)]
	print("  * Rest Trigger:", NFC_table.tbl_rst_trig.get(rst_trig, "RFU ("+rst_trig+")"))
	p_payload = p_payload + 2*1

	cfg_status = raw[p_payload:(p_payload+2*1)]
	print("  * Config Status:", NFC_table.tbl_cfg_status.get(cfg_status, "RFU ("+cfg_status+")"))
	p_payload = p_payload + 2*1

	if(rst_trig == 'A0'):
		program_counter = raw[p_payload:(p_payload+2*4)]
		print("  * dw Assertion Program Counter: "+program_counter)
		p_payload = p_payload + 2*4
	else:
		nci_ver = raw[p_payload:(p_payload+2*1)]
		print("  * NCI Version:", NFC_table.tbl_nci_ver.get(nci_ver, "RFU ("+nci_ver+")"))
		p_payload = p_payload + 2*1

		mfg_id = raw[p_payload:(p_payload+2*1)]
		if(mfg_id == "00"):
			print("  * Manufacturer ID: Info is not available.")
		else:
			print("  * Manufacturer ID:", mfg_id)
		p_payload = p_payload + 2*1

		# mfg_spec_info_len = raw[p_payload:(p_payload+2*1)]
		# n = int(mfg_spec_info_len, 16)
		p_payload = p_payload + 2*1
		print("  * Model ID: "+raw[p_payload:(p_payload+2*1)])
		p_payload = p_payload + 2*1
		print("  * Hw Ver nb: "+raw[p_payload:(p_payload+2*1)])
		p_payload = p_payload + 2*1
		print("  * ROM Code Ver nb: "+raw[p_payload:(p_payload+2*1)])
		p_payload = p_payload + 2*1
		print("  * FLASH Ver: "+str(int(raw[p_payload:(p_payload+2*1)], 16))+"."+str(int(raw[(p_payload+2*1):(p_payload+2*2)], 16)))
		p_payload = p_payload + 2*2
		# print("")
	return p_payload

# 20 01
def CORE_INIT_CMD(raw):
	"""""""""""""""
		[CORE_INIT_CMD]
	Feature Enable: 2 Octets
	"""""""""""""""
	# print("CORE_INIT_CMD")
	p_payload = Origin.CORE_INIT_CMD(raw, "nxp")
	return p_payload

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
	p_payload = Origin.CORE_INIT_RSP(raw, "nxp")
	return p_payload

# 20 02
def CORE_SET_CONFIG_CMD(raw):
	"""""""""""""""
		[CORE_SET_CONFIG_CMD]
	Number of Parameters: 	1 Octet (n)
	Parameter [1..n]: 		m+2 Octets
	﹂	ID:					﹂	1 Octet		(﹂	Register:	        ﹂	2 Octets) # Nxp Prop
	﹂	Len: 				﹂	1 Octet (m)
	﹂	Val:				﹂	m Octet(s)
	"""""""""""""""
	# print("CORE_SET_CONFIG_CMD")
	p_payload = 0

	num_of_parameter = raw[p_payload:(p_payload+2*1)]
	n = int(num_of_parameter, 16)
	print("  * Number of Params:", n)
	p_payload = p_payload + 2*1
	
	# print("  * Parameter:")
	for i in range(n):
		print("   ~ [Param_"+str(i)+"] ~  ")
		para_id = raw[p_payload:(p_payload+2*1)]
		if(para_id == 'A0' or para_id == 'A1'):
			reg = raw[p_payload:(p_payload+2*2)]
			print("    * Register:", NFC_table.tbl_cfg_para.get(reg,"RFU ("+reg+")"), "("+reg+")")
			p_payload = p_payload + 2*2
		else:
			print("    * ID:", NFC_table.tbl_cfg_para.get(para_id,"RFU ("+para_id+")"), "("+para_id+")")
			p_payload = p_payload + 2*1
		
		para_len = raw[p_payload:(p_payload+2*1)]
		m = int(para_len, 16)
		print("    * Len:", m)
		p_payload = p_payload + 2*1
		
		if (m != 0):
			para_val = raw[p_payload:(p_payload+2*m)]
			# print("    * Val: "+para_val)
			if(para_id == 'A0' or para_id == 'A1'):
				VALUE_OF_REGISTER(reg, para_val, m)
			else:
				VALUE_OF_CFG_PARA(para_id, para_val)
			p_payload = p_payload + 2*m
		print("")
	# print("#end")
	return p_payload

# 40 02
def CORE_SET_CONFIG_RSP(raw):
	"""""""""""""""
		[CORE_SET_CONFIG_RSP]
	Status: 				1 Octet
	Number of Parameters: 	1 Octet (n)
	Parameter ID [0..n]: 	1 Octet
	"""""""""""""""
	# print("CORE_SET_CONFIG_RSP")
	p_payload = Origin.CORE_SET_CONFIG_RSP(raw, "nxp")
	return p_payload

# 20 03
def CORE_GET_CONFIG_CMD(raw):
	"""""""""""""""
		[CORE_GET_CONFIG_CMD]
	Number of Parameters: 	1 Octet (n)
	Parameter ID [0..n]: 	1 Octet		(﹂	Register:	        ﹂	2 Octets) # Nxp Prop
	"""""""""""""""
	# print("CORE_GET_CONFIG_CMD")
	p_payload = 0

	num_of_parameter = raw[p_payload:(p_payload+2*1)]
	n = int(num_of_parameter, 16)
	print("  * Number of Params:", n)
	p_payload = p_payload + 2*1
	
	print("  * Param ID:")
	for i in range(n):
		para_id = raw[p_payload:(p_payload+2*1)]
		if(para_id == 'A0' or para_id == 'A1'):
			para_id = raw[p_payload:(p_payload+2*2)]
			print("    * Register:", NFC_table.tbl_cfg_para.get(para_id,"RFU ("+para_id+")"), "("+para_id+")")
			p_payload = p_payload + 2*2
		else:
			print("    * ID "+str(i)+":", end=" ")
			print(NFC_table.tbl_cfg_para.get(para_id,"RFU ("+para_id+")"), "("+para_id+")")
			p_payload = p_payload + 2*1
	# print("")
	return p_payload

# 40 03
def CORE_GET_CONFIG_RSP(raw):
	"""""""""""""""
		[CORE_GET_CONFIG_RSP]
	Status: 				1 Octet
	Number of Parameters: 	1 Octet (n)
	Parameter [1..n]: 		m+2 Octets
	﹂	ID:					﹂	1 Octet		(﹂	Register:	        ﹂	2 Octets) # Nxp Prop
	﹂	Len: 				﹂	1 Octet (m)
	﹂	Val:				﹂	m Octet(s)
	"""""""""""""""
	# print("CORE_GET_CONFIG_RSP")
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]	
	print("  * Status:", NFC_table.tbl_status_codes.get(status,"RFU ("+status+")"))
	p_payload = p_payload + 2*1
	
	num_of_parameter = raw[p_payload:(p_payload+2*1)]
	n = int(num_of_parameter, 16)
	print("  * Number of Params:", n)
	p_payload = p_payload + 2*1
	
	# print("  * Parameter:")
	for i in range(n):
		print("   ~ [Param_"+str(i)+"] ~  ")
		para_id = raw[p_payload:(p_payload+2*1)]
		
		if(para_id == 'A0' or para_id == 'A1'):
			reg = raw[p_payload:(p_payload+2*2)]
			print("    * Register:", NFC_table.tbl_cfg_para.get(reg,"RFU ("+reg+")"), "("+reg+")")
			p_payload = p_payload + 2*2
		else:
			print("    * ID:", NFC_table.tbl_cfg_para.get(para_id,"RFU ("+para_id+")"), "("+para_id+")")
			p_payload = p_payload + 2*1

		id_len = raw[p_payload:(p_payload+2*1)]
		m = int(id_len, 16)
		print("    * Len:", m)
		p_payload = p_payload + 2*1
		
		if (m != 0):
			para_val = raw[p_payload:(p_payload+2*m)]
			# print("    * Val: "+para_val)
			if(para_id == 'A0' or para_id == 'A1'):
				VALUE_OF_REGISTER(reg, para_val, m)
			else:
				VALUE_OF_CFG_PARA(para_id, para_val)
			p_payload = p_payload + 2*m
		# print("")
	return p_payload

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
	p_payload = Origin.CORE_CONN_CREATE_CMD(raw, "nxp")
	return p_payload

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
	print("  * Status:", NFC_table.tbl_status_codes.get(status,"RFU ("+status+")"))
	p_payload = p_payload + 2*1
	
	if(status == '00'):
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
def CORE_CONN_CLOSE_CMD(raw):
	"""""""""""""""
		[CORE_CONN_CLOSE_CMD]
	Conn ID:	1 Octet
	"""""""""""""""
	# print("CORE_CONN_CLOSE_CMD")
	p_payload = Origin.CORE_CONN_CLOSE_CMD(raw, "nxp")
	return p_payload

# 40 05
def CORE_CONN_CLOSE_RSP(raw):
	"""""""""""""""
		[CORE_CONN_CLOSE_RSP]
	Status:		1 Octet
	"""""""""""""""
	# print("CORE_CONN_CLOSE_RSP")
	p_payload = Origin.CORE_CONN_CLOSE_RSP(raw, "nxp")
	return p_payload

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
	p_payload = Origin.CORE_CONN_CREDITS_NTF(raw, "nxp")
	return p_payload

# 60 07
def CORE_GENERIC_ERROR_NTF(raw):
	"""""""""""""""
		[CORE_GENERIC_ERROR_NTF]
	Status:		1 Octet
	"""""""""""""""
	# print("CORE_GENERIC_ERROR_NTF")
	p_payload = Origin.CORE_GENERIC_ERROR_NTF(raw, "nxp")
	return p_payload

# 60 08
def CORE_INTERFACE_ERROR_NTF(raw):
	"""""""""""""""
		[CORE_INTERFACE_ERROR_NTF]
	Status:		1 Octet
	Conn ID:	1 Octet
	"""""""""""""""
	# print("CORE_INTERFACE_ERROR_NTF")
	p_payload = Origin.CORE_INTERFACE_ERROR_NTF(raw, "nxp")
	return p_payload

# 20 09
def CORE_SET_POWER_SUB_STATE_CMD(raw):
	"""""""""""""""
		[CORE_SET_POWER_SUB_STATE_CMD]
	Power State:	1 Octet
	"""""""""""""""
	# print("CORE_SET_POWER_SUB_STATE_CMD")
	p_payload = Origin.CORE_SET_POWER_SUB_STATE_CMD(raw, "nxp")
	return p_payload

# 40 09
def CORE_SET_POWER_SUB_STATE_RSP(raw):
	"""""""""""""""
		[CORE_SET_POWER_SUB_STATE_RSP]
    Status: 1 Octet
	"""""""""""""""
	# print("CORE_SET_POWER_SUB_STATE_RSP")
	p_payload = Origin.CORE_SET_POWER_SUB_STATE_RSP(raw, "nxp")
	return p_payload

def VALUE_OF_CFG_PARA(id, val):
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
	else:
		print("    * Val: "+val)

def VALUE_OF_REGISTER(tag, val, val_len):
	val_payload = 0
	# Table 97. Core configuration parameters
	if(tag == 'A015'): # DEFAULT_POWER
		if(val == '01'):
			print("    * Val:", "standby state")
		elif(val == '02'):
			print("    * Val:", "autonomous mode")
		elif(val == '03'):
			print("    * Val:", "autonomous mode + ULPDET")
		elif(val == '05'):
			print("    * Val:", "autonomous mode + ULPDET With Notification")

	elif(tag == 'A00A'): # WAIT_FOR_STABLE_SYSCLOCK
		wait_for_stable = 18.8 * int(val, 16)
		print("    * Val:", val)
		print("      * Guard Time:", wait_for_stable, "μs")

	elif(tag == 'A010'): # CLKGEN
		XtalConfig_b = bin(int(val[2:4], 16))[2::].zfill(8) # 文件 p.87
		print("    * Val:", val)
		print("      * Calibration Restart on Wake-up:", NFC_table.tbl_general_status.get('0'+XtalConfig_b[7:8]))
		if(XtalConfig_b[7:8] == '1'):
			tbl_cap_val = {0: 'no internal cap (2 pF parasitic cap) (default)', 1: '4 pF', 2: '5 pF', 3: '6 pF', 4: '7 pF', 5: '8 pF', 6: '9 pF', 7: '10 pF'}
			print("      * Internal Cap Val:", tbl_cap_val.get(int(XtalConfig_b[4:7], 2)))

	elif(tag == 'A011'): # RF_CLOCK_CFG
		print("    * Val:", val)
		print("      * Input clock freq:", NFC_table.tbl_in_clk_freq.get(val[0:2], "RFU ("+val[0:2]+")"))
		if(bin(int(val[2:4], 16))[2::].zfill(8)[0:1] == '1' and val[0:2] == '09'):
			print("      * Reader mode: disable , * Card mode: Clock-less mode")
		elif(bin(int(val[2:4], 16))[2::].zfill(8)[0:1] == '1'):
			print("      * Reader mode: NFC_CLK_XTAL1 / NFC_XTAL2 , * Card mode: Clock-less mode")
		else:
			print("      * Reader mode: NFC_CLK_XTAL1 / NFC_XTAL2 , * Card mode: NFC_CLK_XTAL1 / NFC_XTAL2")
		if(bin(int(val[2:4], 16))[2::].zfill(8)[2:3] == '1'):
			print("       ~ Force XTAL to be used in Phone off")
		print("      * Initial delay before check of PLL lock:", int(val[4:6], 16), "μs")
		print("      * Delay between check of successive check of lock bit:", int(val[6:8], 16), "μs")
		print("      * Number of successive checks:", int(val[8:10], 16))

	elif(tag == 'A00E'): # PMU_CFG 文件 p.88 
		print("    * Val:", val)
		print("      * IRQ Enable:", val[val_payload:val_payload+2*4])
		val_payload = val_payload + 2*4
		print("      * Power Cfg:", val[val_payload:val_payload+2*3])
		val_payload = val_payload + 2*3
		print("      * DCDC Cfg:", val[val_payload:val_payload+2*5])
		val_payload = val_payload + 2*5
		print("      * TxLdo Cfg:", val[val_payload:val_payload+2*4])
		val_payload = val_payload + 2*4
		print("      * TxLdo Cfg2:", val[val_payload:val_payload+2*4])
		val_payload = val_payload + 2*4
		print("      * TxLdo Vddpa Cfg:", val[val_payload:val_payload+2*4])
		val_payload = val_payload + 2*4
		print("      * TxLdo delay:", val[val_payload:val_payload+2*4])
		val_payload = val_payload + 2*4
		print("      * Startup Wait:", val[val_payload:val_payload+2*4])
		val_payload = val_payload + 2*4

	elif(tag == 'A007'): # RSTN_CFG
		print("    * Val:", val)
		global a007
		a007 = bin(int(val, 16))[2::].zfill(8)[7:8]
		if(a007 == '1'):
			print("    * RSTN_internal:", "Disabled")
		else:
			print("    * RSTN_internal:", "Enabled")

	elif(tag == 'A08E'): # PHONE_OFF_ALLOWED
		print("    * Val:", val)
		if(val == '01'):
			# print("     ~ If A007 = 0x01 ~")
			if(a007 == '1'):
				print("      * Card Emulation in phone off:", "Enabled")
			# print("     ~ If A007 = 0x00 ~")
			else:
				print("      * Card Emulation in phone off:", "Disabled")
		else:
			print("      * Card Emulation in phone off:", "Disabled")

	elif(tag == 'A009'): # TO_BEFORE_STDBY_CFG
		print("    * Val:", val)
		print("      * Time:", int(val, 16)/1000, "s")
		print("       ~ Time-out used to wait after last DH/NFCEE communication before going into standby.")

	elif(tag == 'A01D'): # Lx_DEBUG_CFG
		print("    * Val:", val)
		print("     ~ L1 Events: {ISO14443-4, ISO18092}    ~ L2 Event: {ISO14443-3, Modulation detected, RF Field ON/OFF}")
		val_b_oct0 = bin(int(val[0:2], 16))[2::].zfill(8)
		val_b_oct1 = bin(int(val[2:4], 16))[2::].zfill(8)
		print("      "+"{0:<38}".format("* L1 Events:"), 							NFC_table.tbl_general_status.get('0'+val_b_oct0[3:4]))
		print("      "+"{0:<38}".format("* L2 Events in Reader Mode:"), 			NFC_table.tbl_general_status.get('0'+val_b_oct0[4:5]))
		print("      "+"{0:<38}".format("* Felica SystemCode:"), 					NFC_table.tbl_general_status.get('0'+val_b_oct0[5:6]))
		print("      "+"{0:<38}".format("* Felica RF (all Felica CM events):"), 	NFC_table.tbl_general_status.get('0'+val_b_oct0[6:7]))
		print("      "+"{0:<38}".format("* L2 Events:"), 							NFC_table.tbl_general_status.get('0'+val_b_oct0[7:8]))
		print("      "+"{0:<38}".format("* L2 Events during RF CMA ISO14443-3:"), 	NFC_table.tbl_general_status.get('0'+val_b_oct1[2:3]))

	elif(tag == 'A0FB'): # HW_RESET_NTF
		print("    * Val:", val)
		print("     ~ If set to 0x04 (and DH did not send SET_NFC_SERVICE_STATUS with 0x00),")
		print("     ~ It enables the sent of CORE_RESET_NTF on each HW reset (Power On Reset) received.")
	
	# Table 98. Poll Mode configuration
	elif(tag == 'A064'): # EMVCo_PCD_SETTINGS Val 顛倒 (little endian)
		print("    * Val:", val)
		print("      * Polling delay between 2 phases:", int(val[0:2], 16) + int(val[2:4], 16) * 256 / 1000, "ms")
		print("      * Max nb of WupA/WupB when LPCD is triggered:", int(val[4:6], 16))

	elif(tag == 'A044'): # POLL_PROFILE_SEL_CFG
		print("    * Val:", val)
		val_b = bin(int(val, 16))[2::].zfill(8)
		tbl_bit_0 = {'0': 'NFC FORUM profile', '1': 'EMVCo PCD profile'}
		print("      * Bit 0:", tbl_bit_0.get(val_b[7:8]))
		tbl_bit_1 = {'0': 'Removal on Idle deactivation', '1': 'Power OFF on Idle deactivation'}
		print("      * Bit 1:", tbl_bit_1.get(val_b[6:7]))
		tbl_bit_2 = {'0': 'Removal on discover deactivation', '1': ' Power OFF on discover deactivation'}
		print("      * Bit 2:", tbl_bit_2.get(val_b[5:6]))
		tbl_bit_4 = {'0': 'Polling Type B first', '1': 'Polling Type A first'}
		print("      * Bit 4:", tbl_bit_4.get(val_b[3:4]))
		tbl_bit_5 = {'0': 'EMVCo PCD polling (digital)', '1': 'EMVCo PCD polling (analog)'}
		print("      * Bit 5:", tbl_bit_5.get(val_b[2:3]))

	elif(tag == 'A05D'): # FSDI_CFG
		print("    * Val:", val)
		print("      * Frame Size display in RATS / ATTRIB:", int(val, 16))

	elif(tag == 'A106'): # LPCD_FPC Val 顛倒 (little endian)
		print("    * Val:", val)
		print("      * Threshold val:", int(val[0:2], 16) + int(val[2:4], 16) * 256)

	elif(tag == 'A148'): # RF_PATTERN_CHK
		print("    * Val:", val)
		val_b = bin(int(val[0:2], 16))[2::].zfill(8)
		print("      * Short RF guard time check feature:", NFC_table.tbl_general_status.get('0'+val_b[7:8]))
		
	elif(tag == 'A14B'): # PLL_FREQ_CHECK
		print("    * Val:", val)
		print("      * RF output freq check:", NFC_table.tbl_general_status.get(val, 'RFU'))

	# Table 99. Listen Mode Configuration
	elif(tag == 'A080'): # TO_RF_OFF_CFG Val 顛倒 (little endian)
		print("    * Val:", val)
		print("      * Time:", int(val[0:2], 16) + int(val[2:4], 16) * 256, "ms")
		print("       ~ Time-out before restarts a Polling sequence, after it has detected a Field-OFF in Listen Mode.")

	elif(tag == 'A062'): # SLOW_HOST_CFG
		print("    * Val:", val)
		if(val == '00'):
			print("     ~ SN2x0 keeps sending the RF_FIELD_INFO_NTFs in screen Off power mode.")
		elif(val == '01'):
			print("     ~ SN2x0 stops sending the RF_FIELD_INFO_NTFs in screen Off power mode.")
			print("     ~ Unless there is a successful activation by an external reader.")
		else:
			print("     ~ RFU")

	elif(tag == 'A085'): # RF_MISC_SETTINGS Val 顛倒 4003 09 00 01 A085 04 7888AA2C -> 2CAA8878 (little endian) lsb ---> msb
		print("    * Val:", val)
		b_val = bin(int(val[6:8], 16))[2::].zfill(8) + bin(int(val[4:6], 16))[2::].zfill(8) + bin(int(val[2:4], 16))[2::].zfill(8) + bin(int(val[0:2], 16))[2::].zfill(8)
		print("      * b_val:", b_val)
		print("      "+"{0:<42}".format("* Uncomplia nt 13.5MHz readers:"), 			NFC_table.tbl_general_status.get('0'+b_val[28:29]))
		print("      "+"{0:<42}".format("* SFGT Early Exchange:"), 						NFC_table.tbl_general_status.get('0'+b_val[27:28]))
		print("      "+"{0:<42}".format("* PCD Block nb Check:"), 						NFC_table.tbl_general_status.get('0'+b_val[25:26]))
		print("      "+"{0:<42}".format("* Mute To RATS with non ISO-DEP SAK:"), 		NFC_table.tbl_general_status.get('0'+b_val[22:23]))
		print("      "+"{0:<42}".format("* Multiple Tag during collision:"), 			NFC_table.tbl_general_status.get('0'+b_val[19:20]))
		print("      "+"{0:<42}".format("* NAK To RATS:"), 								NFC_table.tbl_general_status.get('0'+b_val[18:19]))
		tbl_A085 = {'0': 'Not support', '1': 'Support'}
		print("      "+"{0:<42}".format("* Illegal Uid 0 (Yangchengtong):"), 			tbl_A085.get(b_val[14:15]))
		print("      "+"{0:<42}".format("* Non Compliant Mifare Reader:"), 				tbl_A085.get(b_val[13:14]))
		print("      "+"{0:<42}".format("* Non Compliant Mifare Reader (Changchun):"),	tbl_A085.get(b_val[1:2]))

	elif(tag == 'A10E'): # GUARD_TIMEOUT_Tx2Rx
		print("    * Val:", val)
		print("      * FDT 14443-A activ (Tx to Rx):", 	"{0:.2f}".format((int(val[0:2], 16) + int(val[2:4], 16) * 256) * (8/13.56)), 	"µs")
		print("      * FDT Mifare trans (Rx to Tx):", 	"{0:.2f}".format((int(val[4:6], 16) + int(val[6:8], 16) * 256) * (8/13.56)), 	"µs")
		print("      * FDT Mifare trans (Tx to Rx):", 	"{0:.2f}".format((int(val[8:10], 16) + int(val[10:12], 16) * 256) * (8/13.56)), "µs")

	elif(tag == 'A095'): # NDEF_NFCEE
		print("    * Val:", val)
		val_b = bin(int(val[0:2], 16))[2::].zfill(8)
		print("      "+"{0:<30}".format("* NDEF NFCEE:"), 							NFC_table.tbl_general_status.get('0'+val_b[7:8]))
		print("      "+"{0:<30}".format("* FID E108 write from RF IF:"), 			NFC_table.tbl_general_status.get('0'+val_b[5:6]))
		print("      "+"{0:<30}".format("* FID E107 write from RF IF:"), 			NFC_table.tbl_general_status.get('0'+val_b[4:5]))
		print("      "+"{0:<30}".format("* FID E106 write from RF IF:"), 			NFC_table.tbl_general_status.get('0'+val_b[3:4]))
		print("      "+"{0:<30}".format("* FID E105 write from RF IF:"), 			NFC_table.tbl_general_status.get('0'+val_b[2:3]))
		print("      "+"{0:<30}".format("* FID E104 write from RF IF:"), 			NFC_table.tbl_general_status.get('0'+val_b[1:2]))
		print("      "+"{0:<30}".format("* Additional proprietary TLV:"), 			NFC_table.tbl_general_status.get('0'+val_b[0:1]))

	elif(tag == 'A110'): # NDEF_NFCEE_CFG2
		print("    * Val:", val)
		val_b = bin(int(val[0:2], 16))[2::].zfill(8)
		print("      "+"{0:<31}".format("* FID E108 write from Host IF:"), 			NFC_table.tbl_general_status.get('0'+val_b[5:6]))
		print("      "+"{0:<31}".format("* FID E107 write from Host IF:"), 			NFC_table.tbl_general_status.get('0'+val_b[4:5]))
		print("      "+"{0:<31}".format("* FID E106 write from Host IF:"), 			NFC_table.tbl_general_status.get('0'+val_b[3:4]))
		print("      "+"{0:<31}".format("* FID E105 write from Host IF:"), 			NFC_table.tbl_general_status.get('0'+val_b[2:3]))
		print("      "+"{0:<31}".format("* FID E104 write from Host IF:"), 			NFC_table.tbl_general_status.get('0'+val_b[1:2]))

	elif(tag == 'A10B'): # AUTONOMOUS_START_TIMEOUT
		print("    * Val:", val)
		if(val == '00' and Proprietary.PWR_MODE_00 != '02'):
			print("      * Autonomous Mode: Disabled")
		else:
			print("      * Autonomous Mode:", "starts afetr guard time", int(val, 16), "seconds.")

	elif(tag == 'A10F'): # ULPDET_CFG
		print("    * Val:", val)
		if(val[0:2] == '01'):
			val_b_oct1 = bin(int(val[2:4], 16))[2::].zfill(8)
			print("      * Default Platform Cfg: ULPDET mode")
			gpio2_ao_status1 = {'0': 'is not used during ULPDET mode', '1': 'is high when wake up from ULPDET mode, Low when enter in Standby mode.'}
			print("       ~ NFC_GPIO2_AO", gpio2_ao_status1.get(val_b_oct1[7:8]))
			if(val_b_oct1[6:7] == '1'):
				print("       ~ NFC_GPIO2_AO is high when external RF field is ON and low when OFF, in all modes (ULPDET,LPDET).")
			if(val_b_oct1[5:6] == '1'):
				print("       ~ NFC_GPIO3_AO is high when card is activated in any RF technology. Set low when NFCC enters standby.")

	elif(tag == 'A096' or tag == 'A111'): # NOTIFY_ALL_AID NOTIFY_ALL_FID
		print("    * Val:", val)
		val_b = bin(int(val, 16))[2::].zfill(8)
		print("      "+"{0:<30}".format("* Action Notification:"), 			NFC_table.tbl_general_status.get('0'+val_b[3:4]))
		print("      "+"{0:<30}".format("* Notification in Screen OFF:"), 	NFC_table.tbl_general_status.get('0'+val_b[4:5]))
		
	elif(tag == 'A086' or tag == 'A087'): # RF_BITRATE_LIMIT_A_CFG RF_BITRATE_LIMIT_B_CFG
		print("    * Val:", val)
		val_b = bin(int(val, 16))[2::].zfill(8)
		print("      * Bit Rate Cfg1:", NFC_table.tbl_general_status.get('0'+val_b[5:6]), NFC_table.tbl_general_status.get('0'+val_b[6:7]), NFC_table.tbl_general_status.get('0'+val_b[7:8]))
		print("      * Bit Rate Cfg2:", NFC_table.tbl_general_status.get('0'+val_b[1:2]), NFC_table.tbl_general_status.get('0'+val_b[2:3]), NFC_table.tbl_general_status.get('0'+val_b[3:4]))
		print("      * UICC usage:", NFC_table.tbl_general_status.get(val_b[0:1]))

	elif(tag == 'A11B'): # MERGE_SAK
		print("    * Val:", val)
		tbl_merge_sak = {'01': 'Merge between different NFCEE requests.',
				   		 '02': 'Force clear',
				   		 '03': 'Force merge',
						}
		print("      * Handle SAK merge:", tbl_merge_sak.get(val))

	elif(tag == 'A155'): # RSSI_CONTINUOUS_NTF
		print("    * Val:", val)
		print("      * Byte:", NFC_table.tbl_general_status.get(val[0:2], 'RFU'))
		print("      * Interval between NTFs:", int(val[2:4], 16) * 10, "ms")

	# Table 100. SWP configuration parameters for UICC1 interface
	elif(tag == 'A0C0' or tag == 'A0D1'): # SWP_BITRATE_UICC1 SWP_BITRATE_UICC2
		print("    * Val:", val)
		tbl_swp_baud = {'01': '200',		'02': '416.7',		'03': '833.3',
				  		'04': '910',		'05': '1000',		'06': '1250',
						'07': '1667',
				  	   }
		print("      * Req SWP baud rate:", tbl_swp_baud.get(val, 'RFU'), "kb/s")

	elif(tag == 'A0CB' or tag == 'A0D3'): # SWP_TS1_HIGHV_UICC1 SWP_TS1_HIGHV_UICC2 Val 顛倒 (little endian)
		print("    * Val:", val)
		timeout = (int(val[0:2], 16) + int(val[2:4], 16)*256 + int(val[4:6], 16)*65536 + int(val[6:8], 16)*16777216)
		print("      * Time-out between SIMVCC HIGH and NFC_SIM_SWIO1 HIGH:", timeout / 45 / 1000, "ms")
		
	elif(tag == 'A0EC' or tag == 'A0D4'): # SWP_UICC1_IF_EN_CFG SWP_UICC2_IF_EN_CFG
		print("    * Val:", val)
		print("      * UICC1 IF:", NFC_table.tbl_general_status.get(val, 'RFU'))

	elif(tag == 'A0F1' or tag == 'A0F8'): # SWP_UICC1_SPECIAL_PWR_MODE_CFG SWP_UICC2_SPECIAL_PWR_MODE_CFG
		print("    * Val:", val)
		tbl_uicc1_pwr_mode = {'00': 'Low', '01': 'Full'}
		print("      * UICC1 Power Mode:", tbl_uicc1_pwr_mode.get(val, 'RFU'))

	elif(tag == 'A0C5'): # SWP_UICC1_ACT_RSET_WAIT
		print("    * Val:", val)
		print("      * Delay before RSET frame:", int(val, 16) * 128, "μs")

	elif(tag == 'A11C'): # SWP_EXT_RESUME
		print("    * Val:", val)
		val_b = bin(int(val, 16))[2::].zfill(8)
		tbl_ext_resume = {'0': 'Extended resume not used.', '1': 'Extended resume may be used, if also supported by UICC.'}
		print("      * UICC1:", tbl_ext_resume.get(val_b[7:8]))		
		print("      * UICC2:", tbl_ext_resume.get(val_b[6:7]))		

	# Table 101. Mailbox configuration parameters
	elif(tag == 'A0B8'): # SE_APDU_LOGGING_EN_CFG
		print("    * Val:", val)
		val_b = bin(int(val, 16))[2::].zfill(8)
		print("      * APDU Logging:                  ", NFC_table.tbl_general_status.get('0'+val_b[7:8]))
		print("      * APDU Logging during Mifare CLT:", NFC_table.tbl_general_status_n.get('0'+val_b[5:6]))

	elif(tag == 'A0ED'): # NFCEE_eSE_IF_EN_CFG
		print("    * Val:", val)
		tbl_ese_if = {'00': 'Disabled', '01': 'NFCEE_eSE Enabled', '02': 'NFCEE_eUICC Enabled', '03': 'NFCEE_eSE and NFCEE_eUICC Enable'}
		print("      * NFCEE_eSE IF:", tbl_ese_if.get(val, 'RFU'))

	elif(tag == 'A0F9'): # SE_COLD_RESET_NTF
		print("    * Val:", val)
		print("      * eSE cold reset NTF through NFC_GPIO0 pin:", NFC_table.tbl_general_status.get(val))

	elif(tag == 'A08A'): # SE_POWER_ON_TO_WAKE_UP_GUARD_TIME
		print("    * Val:", val)
		print("      * Delay before waking-up the eSE:", int(val[0:2], 16) + int(val[2:4], 16) * 256, "µs")
		
	elif(tag == 'A08C'): # SE_POWER_OFF_TO_SW_RESET_DELAY_TIME
		print("    * Val:", val)
		print("      * Delay before resetting the mailbox:", int(val[0:2], 16) + int(val[2:4], 16) * 256, "µs")
		
	elif(tag == 'A08D'): # WAKE_UP_SE_TO_ACT_FRAME_DELAY_TIME
		print("    * Val:", val)
		print("      * Delay before sensing an ACT frame:", int(val[0:2], 16) + int(val[2:4], 16) * 256, "µs")

	elif(tag == 'A089'): # ACT_RESPONSE_GUARD_TIME
		print("    * Val:", val)
		print("      * Max time to send ACK:", int(val[0:2], 16) + int(val[2:4], 16) * 256, "ms")

	elif(tag == 'A08B' or tag == 'A082'): # CLT_F_TIMEOUT CLT_A_TIMEOUT
		print("    * Val:", val)
		print("      * Time-out to abort:", int(val[0:2], 16) + int(val[2:4], 16) * 256, "ms")

	elif(tag == 'A094'): # SE_TEMP_ERROR_DELAY_TIME
		print("    * Val:", val)
		val_b = bin(int(val, 16))[2::].zfill(8)
		print("      * Delay after TEMP_ERROR:", int(val[1:2], 16), end="")
		if(val_b[0:1] == '1'):
			print(" s")
		else:
			print(" (No unit defined)")
	
	elif(tag == 'A084'): # VBAT_THRESHOLD_PHONE_OFF
		print("    * Val:", val)
		print("      * VBAT threshold:", int(val[0:2], 16) + int(val[2:4], 16) * 256, "mV")

	# Table 102. HCI configuration parameters
	elif(tag == 'A0EF' or tag == 'A0E8' or tag == 'A0F0'): # RF_PARAM_CE_UICC1 RF_PARAM_CE_UICC2 RF_PARAM_CE_eSE
		print("    * Val:", val)
		tbl_pip_status = {'00': 'Not created', '01': 'Created & Closed', '02': 'Open'}
		
		# Type A
		print("     ~ Card Emulation for Type A ~")
		print("      * Pipe Status:", tbl_pip_status.get(val[val_payload:(val_payload+2*1)]))
		val_payload = val_payload + 2*1

		print("      * MODE parameter:", val[val_payload:(val_payload+2*1)])
		val_payload = val_payload + 2*1

		nid_size = int(val[val_payload:(val_payload+2*1)], 16)
		val_payload = val_payload + 2*1

		print("      * UID:", val[val_payload:(val_payload+2*nid_size)])
		val_payload = val_payload + 2*nid_size

		print("      * SAK:", val[val_payload:(val_payload+2*1)])
		val_payload = val_payload + 2*1

		print("      * ATQA:", val[val_payload:(val_payload+2*2)])
		val_payload = val_payload + 2*2

		app_data_size = int(val[val_payload:(val_payload+2*1)], 16)
		val_payload = val_payload + 2*1

		print("      * App. Data:", val[val_payload:(val_payload+2*app_data_size)])
		val_payload = val_payload + 2*app_data_size

		print("      * FWI_SFGI:", val[val_payload:(val_payload+2*1)])
		val_payload = val_payload + 2*1

		print("      * CID support:", val[val_payload:(val_payload+2*1)])
		val_payload = val_payload + 2*1

		print("      * CLT support:", val[val_payload:(val_payload+2*1)])
		val_payload = val_payload + 2*1

		print("      * Data Rate Max:", val[val_payload:(val_payload+2*3)])
		val_payload = val_payload + 2*3

		# Type B
		print("     ~ Card Emulation for Type B ~")
		print("      * Pipe Status:", tbl_pip_status.get(val[val_payload:(val_payload+2*1)]))
		val_payload = val_payload + 2*1

		print("      * MODE parameter:", val[val_payload:(val_payload+2*1)])
		val_payload = val_payload + 2*1

		pupi_size = int(val[val_payload:(val_payload+2*1)], 16)
		val_payload = val_payload + 2*1

		print("      * PUPI:", val[val_payload:(val_payload+2*pupi_size)])
		val_payload = val_payload + 2*pupi_size

		print("      * AFI:", val[val_payload:(val_payload+2*1)])
		val_payload = val_payload + 2*1

		print("      * ATQB:", val[val_payload:(val_payload+2*4)])
		val_payload = val_payload + 2*4

		hl_rsp_size = int(val[val_payload:(val_payload+2*1)], 16)
		val_payload = val_payload + 2*1

		print("      * Higher Layer RSP:", val[val_payload:(val_payload+2*hl_rsp_size)])
		val_payload = val_payload + 2*hl_rsp_size

		print("      * Data Rate Max:", val[val_payload:(val_payload+2*3)])
		val_payload = val_payload + 2*3

	elif(tag == 'A11A'): # PHONEOFF_TECH_CONFIG
		print("    * Val:", val)
		val_b = bin(int(val, 16))[2::].zfill(8)
		print("      * CE A: ", NFC_table.tbl_general_status_n.get('0'+val_b[7:8]))
		print("      * CE B: ", NFC_table.tbl_general_status_n.get('0'+val_b[6:7]))
		print("      * CE F: ", NFC_table.tbl_general_status_n.get('0'+val_b[5:6]))

	elif(tag == 'A022' or tag == 'A023' or tag == 'A024' or tag == 'A025' or tag == 'A0E9' or tag == 'A012'): 
		# HCI pipe status of Connectivity gate for NFCEE_eSE
		# HCI pipe status of APDU gate for NFCEE_eSE
		# HCI pipe status of connectivity gate for NFCEE_UICC1
		# HCI pipe status of APDU gate for NFCEE_UICC1
		# HCI pipe status of connectivity gate for NFCEE_UICC2
		# HCI pipe status of APDU gate for NFCEE_eUICC
		print("    * Val:", val)
		tbl_pipe = {
			'A022': '      * Connectivity Pipe from NFCEE_eSE:', 
			'A023': '      * APDU Pipe from NFCEE_eSE:', 
			'A024': '      * Connectivity Pipe from NFCEE_UICC1:', 
			'A025': '      * APDU Pipe from NFCEE_UICC1:', 
			'A0E9': '      * Connectivity Pipe from NFCEE_UICC2:', 
			'A012': '      * APDU Pipe from NFCEE_eUICC:',}
		tbl_pipe_status = {'00': 'Deleted', '01': 'Closed', '02': 'Open'}
		print(tbl_pipe.get(tag), tbl_pipe_status.get(val, 'RFU'))

	# Table 103. Mechanism to configure the RF transitions:
	elif(tag == 'A017'): # RF_CUST_PHASE_COMPENSATION
		# print("    * Val:", val)
		val = int(val[2:4] + val[0:2])
		if(val & 0x8000):
			val = -((val ^ 0xFFFF) + 1)
		
		degrees = val * 0.25
		print("    * Phase:", degrees, "°")

	elif(tag == 'A068'): # RF_LPCD_CFG
		print("    * Val:", val)
		val_payload = val_payload + 2*9

		tbl_lpcd_cfg = {'8224': 'Enable LPCD', '0224': 'Disable LPCD', '8234': 'Enable Advanced LPCD', 'AA24': 'Enable LPCD with retry poll'}
		print("      * Config:", tbl_lpcd_cfg.get(val[val_payload:(val_payload+2*2)]), "("+val[val_payload:(val_payload+2*2)]+")")
		val_payload = val_payload + 2*2

		print("      * Fall-back Counter:", val[val_payload:(val_payload+2*1)])
		val_payload = val_payload + 2*1
		
		print("      * Threshold coarse:", val[val_payload:(val_payload+2*4)])
		val_payload = val_payload + 2*4

		val_payload = val_payload + 2*20
		
		print("      * LPCD Period:", (int(val[val_payload:(val_payload+2*1)], 16) + int(val[(val_payload+2*1):(val_payload+2*2)], 16) * 256) * 2.63, "ms")
		val_payload = val_payload + 2*4

	elif(tag == 'A034'): # RF_DLMA_CFG
		print("    * Val:", val)
		rssi_thres_ab = val[12:204]
		rssi_thres_f = 	val[208:400]
		print("      * APC_ID_REF_AB:", int(val[8:10], 16))
		print("      * NB_ENTRIES_AB:", int(val[10:12], 16))
		print("      * Type A&B RSSI threshold:") # 96 bytes
		for i in range(24):
			rssi_entry = rssi_thres_ab[i*8:i*8+8]
			print("        * No.{0:>2}:".format(i), "{0:>5}".format(int(rssi_entry[0:2], 16) + int(rssi_entry[2:4], 16) * 256), "("+rssi_entry[0:4]+")")
		print("      * APC_ID_REF_F:", int(val[204:206], 16))
		print("      * NB_ENTRIES_F:", int(val[206:208], 16))
		print("      * Type F RSSI threshold:") # 96 bytes
		for i in range(24):
			rssi_entry = rssi_thres_f[i*8:i*8+8]
			print("        * No.{0:>2}:".format(i), "{0:>5}".format(int(rssi_entry[0:2], 16) + int(rssi_entry[2:4], 16) * 256), "("+rssi_entry[0:4]+")")
		# print("[AN13076] for more details.")
  
	elif(tag == 'A10A'): # RF_DLMA_CLOCK_LESS_CEF_CFG
		print("    * Val:", val)
		rssi_thres_f = 	val[4:196]
		print("      * APC_ID_REF_F:", int(val[0:2], 16))
		print("      * NB_ENTRIES_F:", int(val[2:4], 16))
		print("      * Type F RSSI threshold:") # 96 bytes
		for i in range(24):
			rssi_entry = rssi_thres_f[i*8:i*8+8]
			print("        * No.{0:>2}:".format(i), "{0:>5}".format(int(rssi_entry[0:2], 16) + int(rssi_entry[2:4], 16) * 256), "("+rssi_entry[0:4]+")")

	elif(tag == 'A00B'): # RF_DPC_CFG
		print("    * Val:", val)
		b_cfg = bin(int(val[val_payload:(val_payload+2*1)], 16))[2::].zfill(8)
		print("      * bConfig:", b_cfg)
		print("        "+"{0:<29}".format("* DPC in Reader:"), 				NFC_table.tbl_general_status.get('0'+b_cfg[7:8]))
		print("        "+"{0:<29}".format("* Overcurrent prevention:"), 	NFC_table.tbl_general_status_n.get('0'+b_cfg[4:5]))
		print("        "+"{0:<29}".format("* GPADC threshold detection:"), 	NFC_table.tbl_general_status.get('0'+b_cfg[3:4]))
		print("        "+"{0:<29}".format("* Periodic Timer:"), 			NFC_table.tbl_general_status.get('0'+b_cfg[2:3]))
		val_payload = val_payload + 2*1
		
		print("      * Target Current:", int(val[val_payload:(val_payload+2*1)], 16) + int(val[(val_payload+2*1):(val_payload+2*2)], 16) * 256, "mA")
		val_payload = val_payload + 2*2

		print("      * Hysteresis:", int(val[val_payload:(val_payload+2*1)], 16), "mA")
		val_payload = val_payload + 2*1
		
		val_payload = val_payload + 2*2
		
		print("     ~  #  ~  VDDPA  ~  Target I reduct  ~  MAL change  ~  ASK100 rise/fall  ~  ASK10 rise/fall  ~")
		for i in range(37):
			dpc_entry = val[val_payload:(val_payload+2*4)]
			print("      {0:^5} {1:>6.2f} V  {2:>10} mA       {3:^14} {4:^20} {5:^19}".format(i, i * 0.05 + 1.5, int(dpc_entry[0:2], 16), (int(dpc_entry[2:4], 16) ^ 0x80) - 0x80, 
																	  str((int(dpc_entry[2:4], 16) ^ 0x80) - 0x80)+" / "+str((int(dpc_entry[5:6], 16) ^ 0x8) - 0x8), 
																	  str((int(dpc_entry[6:7], 16) ^ 0x8) - 0x8)+" / "+str((int(dpc_entry[7:8], 16) ^ 0x8) - 0x8)))
			# print("")
			# print("     ~ DPC Entry {} ~".format(i))
			# # byte 0
			# print("      * Target current reduction:", int(dpc_entry[0:2], 16), "mA")
			# # byte 1
			# print("      * Relative change of modulated amplitude level:", (int(dpc_entry[2:4], 16) ^ 0x80) - 0x80) # signed number (2's complement)
			# # byte 2
			# print("      * ASK100, Relative change of rising edge time const:", "{0:<2}".format((int(dpc_entry[4:5], 16) ^ 0x8) - 0x8), end="") # signed number (2's complement)
			# print("      * falling edge time const:", (int(dpc_entry[5:6], 16) ^ 0x8) - 0x8) # signed number (2's complement)
			# # byte 3 (MSB)
			# print("      * ASK 10, Relative change of rising edge time const:", "{0:<2}".format((int(dpc_entry[6:7], 16) ^ 0x8) - 0x8), end="") # signed number (2's complement)
			# print("      * falling edge time const:", (int(dpc_entry[7:8], 16) ^ 0x8) - 0x8) # signed number (2's complement)
			val_payload = val_payload + 2*4

	elif(tag == 'A00D'): # RF_TRANSITION_CFG # 之後擴充~~
		print("    * Val:", val)
		trans_id = val[0:2]
		regi_addr = val[2:4]
		regi_val = val[4:]

		if(val_len == 6):
			b_regi_val = bin(int(regi_val[6:8], 16))[2::].zfill(8) + bin(int(regi_val[4:6], 16))[2::].zfill(8) + bin(int(regi_val[2:4], 16))[2::].zfill(8) + bin(int(regi_val[0:2], 16))[2::].zfill(8)
		elif(val_len == 4):
			b_regi_val = bin(int(regi_val[2:4], 16))[2::].zfill(8) + bin(int(regi_val[0:2], 16))[2::].zfill(8)
		elif(val_len == 3):
			b_regi_val = bin(int(regi_val[0:2], 16))[2::].zfill(8)

		print("      * Transition ID:", 		NFC_table.tbl_rf_trans_id.get(trans_id, "RFU ("+trans_id+")"), "("+trans_id+")")
		print("      * CLIF register offset:", 	NFC_table.tbl_register.get(regi_addr, "RFU"), "("+regi_addr+")")
		print("      * Register Val:", b_regi_val, "( "+ regi_val +" )")

		if(regi_addr == '50'): # 6
			print("        * GSP_DEFAULT_TX2:", b_regi_val[2:7])
			print("        * GSP_DEFAULT_TX1:", b_regi_val[7:12])
			print("        * GSP_CM_TX2:", 		b_regi_val[12:17])
			print("        * GSP_CM_TX1:", 		b_regi_val[17:22])
			print("        * GSP_RM_TX2:", 		b_regi_val[22:27])
			print("        * GSP_RM_TX1:", 		b_regi_val[27:32])

		elif(regi_addr == '4E' or regi_addr == '4F'): # 6
			tbl_symbol = {'4E': 'TX1', '4F': 'TX2'}
			print("        * GSN_DEFAULT_"+tbl_symbol.get(regi_addr)+":", 	b_regi_val[7:12])
			print("        * GSN_MOD_CM_"+tbl_symbol.get(regi_addr)+":", 	b_regi_val[12:17])
			print("        * GSN_CW_CM_"+tbl_symbol.get(regi_addr)+":", 	b_regi_val[17:22])
			print("        * GSN_MOD_RM_"+tbl_symbol.get(regi_addr)+":", 	b_regi_val[22:27])
			print("        * GSN_CW_RM_"+tbl_symbol.get(regi_addr)+":", 	b_regi_val[27:32])

		elif(regi_addr == 'AB'): # 6
			print("        * TX1_SS_TARGET_SCALE:", int(regi_val[0:2], 16))
			print("        * TX2_SS_TARGET_SCALE:", int(regi_val[2:4], 16))

		elif(regi_addr == '32'): # 6
			print("        * TX_UNDERSHOOT_PATTERN:", b_regi_val[0:16])
			print("        * TX_EXTENDED_TRANSMISSION:", b_regi_val[24:26])
			print("        * TX_UNDERSHOOT_PATTERN_LEN:", b_regi_val[27:31])
			print("        * TX_UNDERSHOOT_PROT_ENABLE:", NFC_table.tbl_general_status.get('0'+b_regi_val[31:32]))

		elif(regi_addr == '40'): # 6
			print("        * DGRM_RSSI_TARGET:", b_regi_val[15:25])
			print("        * DGRM_SIGNAL_DETECT_TH_OVR_VAL:", b_regi_val[25:32])


	elif(tag == 'A09E'): # RX_CTRL_CFG
		print("    * Val:", val)
		b_cfg = bin(int(val[val_payload:(val_payload+2*1)], 16))[2::].zfill(8)
		print("      * Config:", b_cfg)
		print("        * Rx improvements for GreenCar:", NFC_table.tbl_general_status.get('0'+b_cfg[5:6]))
		print("        * Clock-less CeB field strength RSSI conversion:", NFC_table.tbl_general_status.get('0'+b_cfg[4:5]))
		val_payload = val_payload + 2*1

		# print("      * Ref Interpolated RSSI measured at 8 A/m:", "{0:.2f}".format(int(val[val_payload:(val_payload+2*2)], 16) / 2048), "mV (Big Endian)")
		print("      * Ref Interpolated RSSI measured at 8 A/m:", "{0:.2f}".format((int(val[val_payload:(val_payload+2*1)], 16) + int(val[(val_payload+2*1):(val_payload+2*2)], 16) * 256) / 2048), "mV")
		val_payload = val_payload + 2*2
		
		# print("      * LPDET level:", int(val[val_payload:(val_payload+2*2)], 16), "mA (Big Endian)")
		print("      * LPDET:", int(val[val_payload:(val_payload+2*1)], 16) + int(val[(val_payload+2*1):(val_payload+2*2)], 16) * 256, "mA/m")
		val_payload = val_payload + 2*2
		
		# print("      * NFCLD level:", int(val[val_payload:(val_payload+2*2)], 16), "mA (Big Endian)")
		print("      * NFCLD ON:", int(val[val_payload:(val_payload+2*1)], 16) + int(val[(val_payload+2*1):(val_payload+2*2)], 16) * 256, "mA/m")
		val_payload = val_payload + 2*2
		
		print("      * NFCLD ON/OFF ratio:", int(val[val_payload:(val_payload+2*1)], 16), "%")
		val_payload = val_payload + 2*1
		
		print("      * Green Car threshold:", int(val[val_payload:(val_payload+2*1)], 16) + int(val[(val_payload+2*1):(val_payload+2*2)], 16) * 256, "mA/m")
		val_payload = val_payload + 2*2
		
		print("      * Clock-less CeB:", int(val[val_payload:(val_payload+2*1)], 16) + int(val[(val_payload+2*1):(val_payload+2*2)], 16) * 256, "mA/m")
		val_payload = val_payload + 2*2
	
	elif(tag == 'A17E'): # ADVANCED_HYBRID_LPCD_CFG
		print("    * Val:", val)
		b_cfg = bin(int(val[0:2], 16))[2::].zfill(8) + bin(int(val[2:4], 16))[2::].zfill(8)
		print("      * Config:", b_cfg)
		print("        * POLL_TYPE_A:          ", NFC_table.tbl_general_status.get('0'+b_cfg[15:16]))
		print("        * POLL_TYPE_B:          ", NFC_table.tbl_general_status.get('0'+b_cfg[14:15]))
		print("        * POLL_TYPE_F:          ", NFC_table.tbl_general_status.get('0'+b_cfg[13:14]))
		print("        * POLL_TYPE_V:          ", NFC_table.tbl_general_status.get('0'+b_cfg[12:13]))
		print("        * Advanced Hybrid LPCD: ", NFC_table.tbl_general_status.get('0'+b_cfg[0:1]))

	elif(tag == 'A12E'): # FDT_CONFIG
		print("    * Val:", val)
		print("      * Tx BitPhase Ext Clock:  ", val[0:2])
		print("      * Tx BitPhase Clock-less: ", val[2:4])
		print("      * Tx BitPhase Bpsk Delay: ", val[4:6])
		print("       ~ A variation of +1 in the register means a shift of +1/13.56Mhz s on the FDT time")

# --------------------------------------------------------------------------------

	elif(tag == 'A06A'): # RF_CLK_PLL_DPLL3
		print("    * Val:", val)
		sys_xtal = val[0:2*8]
		clk_less = val[2*8:2*16]
		print("      * Sys / Xtal clk:")
		sxc_rf_on = (int(sys_xtal[0:2], 16) + int(sys_xtal[2:4], 16) * 256) / 4
		sxc_a = (int(sys_xtal[4:6], 16) + int(sys_xtal[6:8], 16) * 256) / 4
		sxc_b = (int(sys_xtal[8:10], 16) + int(sys_xtal[10:12], 16) * 256) / 4
		sxc_f = (int(sys_xtal[12:14], 16) + int(sys_xtal[14:16], 16) * 256) / 4
		print("      * RF ON:", "{0:.2f} °".format(sxc_rf_on), " * A:", "{0:.2f} °".format(sxc_a), " * B:", "{0:.2f} °".format(sxc_b), " * F:", "{0:.2f} °".format(sxc_f))
		print("      * Clock-less:")
		cl_rf_on = (int(clk_less[0:2], 16) + int(clk_less[2:4], 16) * 256) / 4
		cl_a = (int(clk_less[4:6], 16) + int(clk_less[6:8], 16) * 256) / 4
		cl_b = (int(clk_less[8:10], 16) + int(clk_less[10:12], 16) * 256) / 4
		cl_f = (int(clk_less[12:14], 16) + int(clk_less[14:16], 16) * 256) / 4
		print("      * RF ON:", "{0:.2f} °".format(cl_rf_on), " * A:", "{0:.2f} °".format(cl_a), " * B:", "{0:.2f} °".format(cl_b), " * F:", "{0:.2f} °".format(cl_f))

	elif(tag == 'A0AF'): # 2.7 Card Mode Cfg
		print("    * Val:", val)
		cfg_ab = val[0:2]
		ref_vddpa_ab = val[6:8]
		cfg_f = val[8:10]
		ref_vddpa_f = val[6:8]
		b_cfg_ab = bin(int(cfg_ab, 16))[2::].zfill(8)
		b_cfg_f = bin(int(cfg_f, 16))[2::].zfill(8)
		if(cfg_ab[1:2] == '0' and cfg_f[1:2] == '0'):
			print("      * DLMA:", "Disabled")
			print("      * Ref. VDDPA AB:           ", 1.5 + int(ref_vddpa_ab, 16) * 0.05, "V", "      * Ref. VDDPA F:           ", 1.5 + int(ref_vddpa_f, 16) * 0.05, "V", )
		else:
			print("      * DLMA:", "Enable")
			print("      * APC TX AB:               ", "{0:<11}".format(NFC_table.tbl_general_status.get('0'+b_cfg_ab[7:8])), "* APC TX F:               ", "{0:<11}".format(NFC_table.tbl_general_status.get('0'+b_cfg_f[7:8])))
			print("      * BPSK AB (m3):            ", "{0:<11}".format(NFC_table.tbl_general_status.get('0'+b_cfg_ab[6:7])), "* BPSK F (m3):            ", "{0:<11}".format(NFC_table.tbl_general_status.get('0'+b_cfg_f[6:7])))
			print("      * Single Driver AB (m1):   ", "{0:<11}".format(NFC_table.tbl_general_status.get('0'+b_cfg_ab[5:6])), "* Single Driver F (m1):   ", "{0:<11}".format(NFC_table.tbl_general_status.get('0'+b_cfg_f[5:6])))
			print("      * APC Arbitrary Phase AB:  ", "{0:<11}".format(NFC_table.tbl_general_status.get('0'+b_cfg_ab[4:5])), "* APC Arbitrary Phase F:  ", "{0:<11}".format(NFC_table.tbl_general_status.get('0'+b_cfg_f[4:5])))

			# print("      "+"{0:<40}".format("* APC TX F: "+NFC_table.tbl_general_status.get(b_cfg_f[7:8])))
			# print("      "+"{0:<40}".format("* BPSK F: "+NFC_table.tbl_general_status.get(b_cfg_f[6:7])))
			# print("      "+"{0:<40}".format("* Single Driver F: "+NFC_table.tbl_general_status.get(b_cfg_f[5:6])))
			# print("      "+"{0:<40}".format("* APC Arbitrary Phase F: "+NFC_table.tbl_general_status.get(b_cfg_f[4:5])))
		tbl_rssi = {'0': 'Raw', '1': 'Interpolated'}
		print("      "+"{0:<20}".format("* APC AB uses RSSI:")+"{0:^20}".format(tbl_rssi.get(b_cfg_ab[3:4]))+"{0:<19}".format("* APC F uses RSSI:")+"{0:^20}".format(tbl_rssi.get(b_cfg_f[3:4])))
		# print(b_cfg_ab)
		# print(b_cfg_f)
	
	elif(tag == 'A0A7'):
		print("    * Val:", val)
		print("      * GSN_MOD_RM:", bin(int(val[8:10], 16))[2::].zfill(8)[3:])
		print("      * GSN_CW_RM:", bin(int(val[10:12], 16))[2::].zfill(8)[3:])
		print("      * GSP_RM:", bin(int(val[12:14], 16))[2::].zfill(8)[3:])
		print("      * TX_SS_TARGET_SCALE:", int(val[16:18], 16))
		print("      * TX_PH_SHIFT_DIV10:", "{0:d} °".format(int(val[18:20], 16) * 9))
		print("      * TX_PH_SHIFT_MOD10:", "{0:.1f} °".format(int(val[20:22], 16) * 0.9))

	elif(tag == 'A0A8'):
		print("    * Val:", val)
		val_type_a = val[0:32]
		val_type_b = val[32:64]
		val_type_f = val[64:80]
		val_type_v = val[80:128]
		print("     ~ Type A ~")
		print("      * A106, Time const cfg of falling / rising edge:", val_type_a[4:6])
		print("      * A212, Time const cfg of falling / rising edge:", val_type_a[12:14])
		print("      * A424, Time const cfg of falling / rising edge:", val_type_a[20:22])
		print("      * A848, Time const cfg of falling / rising edge:", val_type_a[28:30])
		print("     ~ Type B ~")
		print("      * B106, Time const cfg of falling / rising edge:", val_type_b[4:6], end = "")
		print("      * B106, RESIDUAL carrier:", val_type_b[0:2])
		print("      * B212, Time const cfg of falling / rising edge:", val_type_b[12:14], end = "")
		print("      * B212, RESIDUAL carrier:", val_type_b[8:10])
		print("      * B424, Time const cfg of falling / rising edge:", val_type_b[20:22], end = "")
		print("      * B424, RESIDUAL carrier:", val_type_b[16:18])
		print("      * B848, Time const cfg of falling / rising edge:", val_type_b[28:30], end = "")
		print("      * B848, RESIDUAL carrier:", val_type_b[24:26])
		print("     ~ Type F ~")
		print("      * F212, Time const cfg of falling / rising edge:", val_type_f[4:6], end = "")
		print("      * F212, RESIDUAL carrier:", val_type_f[0:2])
		print("      * F424, Time const cfg of falling / rising edge:", val_type_f[12:14], end = "")
		print("      * F424, RESIDUAL carrier:", val_type_f[8:10])
		print("     ~ Type V ~")
		print("      * V100_26, Time const cfg of falling / rising edge:", val_type_v[4:6])
		print("      * V10_26, Time const cfg of falling / rising edge:", val_type_v[12:14], end = "")
		print("      * V10_26, RESIDUAL carrier:", val_type_v[8:10])
		print("      * V100_53, Time const cfg of falling / rising edge:", val_type_v[20:22])
		print("      * V10_53, Time const cfg of falling / rising edge:", val_type_v[28:30], end = "")
		print("      * V10_53, RESIDUAL carrier:", val_type_v[24:26])
		print("      * V100_106, Time const cfg of falling / rising edge:", val_type_v[36:38])
		print("      * V100_212, Time const cfg of falling / rising edge:", val_type_v[44:46])

	elif(tag == 'A098'):
		print("    * Val:", val)
		print("      * Measured LMA phone ON:", int(val[0:2], 16), "mV")
		print("      * Measured RSSI:", int(val[2:4], 16) + int(val[4:6], 16) * 256)
		print("      * Ref. field strength:", int(val[6:7], 16), "A/m")
		print("      * Ref. VDDPA DLMA OFF:", 1.5 + int(val[8:10], 16) * 0.05, "V")
		print("      * Measured LMA Type A clock-less mode:",int(val[10:12], 16), "mV")
		print("      * Measured LMA Type B clock-less mode:",int(val[12:14], 16), "mV")
		print("      * Measured LMA Type F clock-less mode:",int(val[14:16], 16), "mV")

	elif(tag == 'A0AB'):
		print("    * Val:", val)
		for i in range(1, 65):
			val_set = val[i*4:i*4+4]
			print("      * HFatt code {0:>2}:".format(i-1), "{0:>5}".format(int(val_set[0:2], 16) + int(val_set[2:4], 16) * 256), "set", "("+val_set+")")

	elif(tag == 'A0A9'):
		print("    * Val:", val)
		# print(val_len)
		pre = '0'
		print("     ~  Entry  ~  ID  ~  Equiv TX (Vpp)  ~  VDDPA (V)  ~  TxScaling  ~  Mode 3  ~  DriNum  ~  NCIcmd  ~")
		for i in range(int(val_len/3)):
			entry_val = val[i*6:i*6+6]
			if(entry_val != pre):
				entry_vddpa = int(entry_val[2:4], 16) * 0.05 + 1.5
				entry_tx_scaling = int(entry_val[4:6], 16)
				entry_mode_3 = int(bin(int(entry_val[0:1], 16))[2::].zfill(4)[1:2], 2)
				entry_dv_num = 2 - int(bin(int(entry_val[0:1], 16))[2::].zfill(4)[0:1], 2)
				# print("      * Entry_{0:<2}".format(i), end="")
				print("          {0:>2}".format(i), end="")
				# print("      * ID: {0:<2}".format(int(bin(int(entry_val[0:2], 16))[2::].zfill(8)[2:], 2)), end="")
				print("      {0:>2}".format(int(bin(int(entry_val[0:2], 16))[2::].zfill(8)[2:], 2)), end="")
				# print("      * Equiv TX (Vpp):", "{0:.2f}".format((int(entry_val[2:4], 16) * 0.05 + 1.5) * (int(entry_val[4:6], 16) / 255) * (2 - int(bin(int(entry_val[0:1], 16))[2::].zfill(4)[0:1], 2)) * (1 + int(bin(int(entry_val[0:1], 16))[2::].zfill(4)[1:2], 2))))
				print("        {0:>5.2f}".format((entry_vddpa) * (entry_tx_scaling / 255) * entry_dv_num * (1 + entry_mode_3)), end="")
				print("            {0:>4.2f}".format(entry_vddpa), end="")
				print("            {0:>3}".format(entry_tx_scaling), end="")
				print("           {}".format(entry_mode_3), end="")
				print("          {}".format(entry_dv_num), end="")
				print("       {}".format(entry_val))
				pre = entry_val
			# print(i)

	else:
		print("    * Val:", val)