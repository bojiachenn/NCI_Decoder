import Nxp_pkg.__table__ as NFC_table
from nfc_forum_2_0_pkg import RF_Management as Origin

#       Nxp SN2X0       #

# 21 00
def RF_DISCOVER_MAP_CMD(raw):
	"""""""""""""""
		[RF_DISCOVER_MAP_CMD]
	Number of Mapping Configurations:	1 Octet (n)
	Mapping Configuration [1..n]: 		3 Octets
	﹂	RF Protocol:					﹂	1 Octet
	﹂	Mode: 							﹂	1 Octet
	﹂	RF Interface: 					﹂	1 Octet
	"""""""""""""""
	# print("RF_DISCOVER_MAP_CMD")
	p_payload = Origin.RF_DISCOVER_MAP_CMD(raw, "nxp")
	return p_payload

# 41 00
def RF_DISCOVER_MAP_RSP(raw):
	"""""""""""""""
		[RF_DISCOVER_MAP_RSP]
    Status: 1 Octet
	"""""""""""""""
	# print("RF_DISCOVER_MAP_RSP")
	p_payload = Origin.RF_DISCOVER_MAP_RSP(raw, "nxp")
	return p_payload

# def LISTEN_MODE_ROUTING_INFO(raw):
# 	"""""""""""""""
# 		共用
# 		[RF_SET_LISTEN_MODE_ROUTING_CMD]
# 		[RF_GET_LISTEN_MODE_ROUTING_NTF]
# 	More:						1 Octet
# 	Number of Routing Entries:	1 Octet (n)
# 	Routing Entry [1..n]: 		x+2 Octets
# 	﹂	Qualifier-Type:			﹂	1 Octet
# 	﹂	Length: 				﹂	1 Octet (x)
# 	﹂	Value: 					﹂	x Octet
# 	"""""""""""""""
# 	p_payload = 0

# 	more = raw[p_payload:(p_payload+2*1)]	
# 	print("  * More: "+NFC_table.tbl_more.get(more,"RFU")+" ("+more+")")
# 	p_payload = p_payload + 2*1
	
# 	num_of_router = raw[p_payload:(p_payload+2*1)]
# 	n = int(num_of_router, 16)
# 	print("  * Number of Routing Entries:", n, "("+num_of_router+")")
# 	p_payload = p_payload + 2*1	
	
# 	# print("  * Routing Entry:")
# 	for i in range(n):
# 		print("   ~ [Routing Entry_"+str(i)+"] ~  ")
# 		q_type = raw[p_payload:(p_payload+2*1)]	
# 		print("    * Type: "+NFC_table.tbl_L_mode_routing_entry_type.get(q_type[1:2],"0x5-0x9: RFU, 0xA-0xF: For proprietary use")+" ("+q_type+")")
# 		q_type_b = bin(int(q_type[0:1],16))[2::].zfill(4) # ref to Table 52
# 		if (q_type_b[1:2] == "1"):
# 			print("     ~ Routing is blocked for the power modes where it is not supported.")
# 		if (q_type_b[2:3] == "1"):
# 			print("     ~ Match is allowed when the SELECT AID is shorter than the AID in this routing table entry.")
# 		if (q_type_b[3:4] == "1"):
# 			print("     ~ Match is allowed when the SELECT AID is longer than the AID in this routing table entry.")
# 		p_payload = p_payload + 2*1

# 		len = raw[p_payload:(p_payload+2*1)]	
# 		x = int(len, 16)
# 		print("    * Len:", x, "("+len+")")
# 		p_payload = p_payload + 2*1

# 		val_raw = raw[p_payload:(p_payload+2*x)]
# 		val_payload = 0
# 		p_payload = p_payload + 2*x

# 		print("    * Val: "+val_raw)
# 		route_val = val_raw[val_payload:(val_payload+2*1)]
# 		if((int(route_val,16) >= 2) & (int(route_val,16) <= 15)):
# 			route_val = '02-0F'
# 		elif((int(route_val,16) >= 16) & (int(route_val,16) <= 127)):
# 			route_val = '10-7F'
# 		elif((int(route_val,16) >= 128) & (int(route_val,16) <= 254)):
# 			route_val = '80-FE'
# 		print("      * Route: "+val_raw[val_payload:(val_payload+2*1)]+" ("+NFC_table.tbl_nfcee_id.get(route_val,"RFU")+")")
# 		val_payload = val_payload + 2*1
		
# 		pwr_state = val_raw[val_payload:(val_payload+2*1)]	
# 		pwr_state_b = bin(int(pwr_state,16))[2::].zfill(8)
# 		print("      * Power State: "+pwr_state_b+" ("+pwr_state+")")
# 		for j in range (5,-1,-1):
# 			print('{0:<35}'.format("       ~ "+NFC_table.tbl_pwr_state.get(j,"RFU")+":"), end="")
# 			if(pwr_state_b[7-j:8-j] == "1"):
# 				print('{0:<10}'.format("Apply"))
# 			else:
# 				print('{0:<10}'.format("Not apply"))
# 		val_payload = val_payload + 2*1

# 		if (q_type[1:2] == "0"):
# 			"""""""""""""""
# 				[Table 54: Value Field for Technology-based Routing]
# 			Technology:		1 Octet
# 			"""""""""""""""	
# 			tech = val_raw[val_payload:(val_payload+2*1)]	
# 			print("      * Technology: "+NFC_table.tbl_rf_tech.get(tech,"0x04–0x7F & 0XFF: RFU, 0x80-0xFE: For proprietary use")+" ("+tech+")")
# 			val_payload = val_payload + 2*1
			
# 		elif (q_type[1:2] == "1"):
# 			"""""""""""""""
# 				[Table 55: Value Field for Protocol-based Routing]
# 			Protocol:		1 Octet
# 			"""""""""""""""
# 			proto = val_raw[val_payload:(val_payload+2*1)]
# 			if((int(proto,16) >= 128) & (int(proto,16) <= 254)):
# 				proto = '80-FE'
# 			print("      * Protocol: "+NFC_table.tbl_rf_proto.get(proto,"RFU")+" ("+proto+")")
# 			val_payload = val_payload + 2*1
		
# 		elif (q_type[1:2] == "2"):
# 			"""""""""""""""
# 				[Table 56: Value Field for AID-based Routing]
# 			AID:		    0-16 Octets
# 			"""""""""""""""
# 			# aid_value = val_raw[val_payload:]
# 			if(val_payload < x):
# 				print("      * AID: "+val_raw[val_payload:])
		
# 		elif (q_type[1:2] == "3"):			
# 			"""""""""""""""
# 				[Table 57: Value Field for System Code-based Routing]
# 			SC Route List:  2n Octets
# 			"""""""""""""""
# 			n = (x-2)/2
# 			for j in range(n):
# 				print("      * SC Route "+str(i)+": "+val_raw[val_payload:(val_payload+2*2)])
# 				val_payload = val_payload + 2*2

# 		elif (q_type[1:2] == "4"):			
# 			"""""""""""""""
# 				[Table 58: Value Field for APDU Pattern-based Routing]
# 			Reference data:	n Octet(s)
# 			Mask:       	n Octet(s)
# 			"""""""""""""""
# 			n = (x-2)/2
# 			print("      * Reference data: "+val_raw[val_payload:(val_payload+2*1)])
# 			val_payload = val_payload + 2*n
# 			print("      * Mask: "+val_raw[val_payload:(val_payload+2*1)])
# 			val_payload = val_payload + 2*n
# 		# print("")
# 	return p_payload

# 21 01
def RF_SET_LISTEN_MODE_ROUTING_CMD(raw):
	# print("RF_SET_LISTEN_MODE_ROUTING_CMD")
	p_payload = Origin.RF_SET_LISTEN_MODE_ROUTING_CMD(raw, "nxp")
	return p_payload

# 41 01
def RF_SET_LISTEN_MODE_ROUTING_RSP(raw):
	"""""""""""""""
		[RF_SET_LISTEN_MODE_ROUTING_RSP]
    Status: 1 Octet
	"""""""""""""""
	# print("RF_SET_LISTEN_MODE_ROUTING_RSP")
	p_payload = Origin.RF_SET_LISTEN_MODE_ROUTING_RSP(raw, "nxp")
	return p_payload

# 21 02
def RF_GET_LISTEN_MODE_ROUTING_CMD(raw):
	"""""""""""""""
		[RF_GET_LISTEN_MODE_ROUTING_CMD]
    (Empty)
	"""""""""""""""
	# print("RF_GET_LISTEN_MODE_ROUTING_CMD")
	p_payload = Origin.RF_GET_LISTEN_MODE_ROUTING_CMD(raw, "nxp")
	return p_payload

# 41 02
def RF_GET_LISTEN_MODE_ROUTING_RSP(raw):
	"""""""""""""""
		[RF_SET_LISTEN_MODE_ROUTING_RSP]
    Status: 1 Octet
	"""""""""""""""
	# print("RF_GET_LISTEN_MODE_ROUTING_RSP")
	p_payload = Origin.RF_GET_LISTEN_MODE_ROUTING_RSP(raw, "nxp")
	return p_payload

# 61 02
def RF_GET_LISTEN_MODE_ROUTING_NTF(raw):
	# print("RF_GET_LISTEN_MODE_ROUTING_NTF")
	p_payload = Origin.RF_GET_LISTEN_MODE_ROUTING_NTF(raw, "nxp")
	return p_payload

# 21 03
def RF_DISCOVER_CMD(raw):
	"""""""""""""""
		[RF_DISCOVER_CMD]
	Number of Configurations:		1 Octet (n)
	Configuration [0..n]: 			2 Octets
	﹂	RF Technology and Mode:		﹂	1 Octet
	﹂	Discovery Frequency: 		﹂	1 Octet
	"""""""""""""""
	# print("RF_DISCOVER_CMD")
	p_payload = Origin.RF_DISCOVER_CMD(raw, "nxp")
	return p_payload

# 41 03
def RF_DISCOVER_RSP(raw):
	"""""""""""""""
		[RF_DISCOVER_RSP]
    Status: 1 Octet
	"""""""""""""""
	# print("RF_DISCOVER_RSP")
	p_payload = Origin.RF_DISCOVER_RSP(raw, "nxp")
	return p_payload

# def RF_TECH_SPEC_PARA(rf_tech_mode, para_raw):
# 	"""""""""""""""
# 		部分共用
# 		[RF_DISCOVER_NTF]
# 		[RF_INTF_ACTIVATED_NTF]
# 	"""""""""""""""
# 	para_payload = 0
# 	rf_tech_mode_type = NFC_table.tbl_rf_tech_mode.get(rf_tech_mode,"RFU")
# 	if(rf_tech_mode_type == "A_PASSIVE_POLL"):
# 		"""""""""""""""
# 			[Table 68: Specific Parameters for NFC-A Poll Mode]
#     	SENS_RES Response: 			2 Octets
#     	NFCID1 Length: 				1 Octet
#     	NFCID1: 					4, 7, or 10 Octets
#     	SEL_RES Response Length:	1 Octet
#     	SEL_RES Response: 			0 or 1 Octet
#     	HRx Length: 				1 Octet
#     	HRx: 						0 or 2 Octet(s)
# 		"""""""""""""""
# 		sens_res_rsp = para_raw[para_payload:(para_payload+2*2)]
# 		print("  * SENS_RES Response: "+sens_res_rsp)
# 		para_payload = para_payload + 2*2		
		
# 		id_len = para_raw[para_payload:(para_payload+2*1)]
# 		l = int(id_len,16)
# 		print("  * NFCID1 Len:", l, "("+id_len+")")
# 		para_payload = para_payload + 2*1	

# 		id = para_raw[para_payload:(para_payload+2*l)]
# 		print("  * NFCID1: "+id)
# 		para_payload = para_payload + 2*l	
		
# 		sel_res_rsp_len = para_raw[para_payload:(para_payload+2*1)]	
# 		l = int(sel_res_rsp_len,16)
# 		print("  * SEL_RES Rsp Len:", l, "("+sel_res_rsp_len+")")
# 		para_payload = para_payload + 2*1	

# 		sel_res_rsp = para_raw[para_payload:(para_payload+2*l)]	
# 		print("  * SEL_RES Rsp: "+sel_res_rsp)
# 		para_payload = para_payload + 2*l
	
# 		hrx_len = para_raw[para_payload:(para_payload+2*1)]	
# 		l = int(hrx_len,16)
# 		print("  * HRx Len:", l, "("+hrx_len+")")
# 		para_payload = para_payload + 2*1	
		
# 		if(l != 0):
# 			hrx_val = para_raw[para_payload:(para_payload+2*l)]	
# 			print("  * HRx: "+hrx_val)
# 			para_payload = para_payload + 2*l

# 	elif(rf_tech_mode_type == "A_PASSIVE_LISTEN"):
# 		"""""""""""""""
# 			[Table 69: Specific Parameters for NFC-A Listen Mode]
# 		(Empty)
# 		"""""""""""""""
# 		print("  * There is no RF Technology Specific Parameters")
		
# 	elif(rf_tech_mode_type == "B_PASSIVE_POLL"):
# 		"""""""""""""""
# 			[Table 70: Specific Parameters for NFC-B Poll Mode]
# 		SENSB_RES Response Length: 			1 Octet
# 		SENSB_RES Response: 				11 or 12 Octets
# 		"""""""""""""""
# 		sensb_res_rsp_len = para_raw[para_payload:(para_payload+2*1)]
# 		l = int(sensb_res_rsp_len,16)
# 		print("  * SENSB_RES Rsp Len:", l, "("+sensb_res_rsp_len+")")
# 		para_payload = para_payload + 2*1

# 		sensb_res_rsp = para_raw[para_payload:(para_payload+2*l)]	
# 		print("  * SENSB_RES Rsp: "+sensb_res_rsp)
# 		para_payload = para_payload + 2*l

# 	elif(rf_tech_mode_type == "B_PASSIVE_LISTEN"):
# 		"""""""""""""""
# 			[Table 71: Specific Parameters for NFC-B Listen Mode]
# 		SENSB_REQ Command:		1 Octet
# 		"""""""""""""""
# 		sensb_req_cmd = para_raw[para_payload:(para_payload+2*1)]	
# 		print("  * SENSB_REQ Command:: "+sensb_req_cmd)
# 		para_payload = para_payload + 2*1

# 	elif(rf_tech_mode_type == "F_PASSIVE_POLL"):
# 		"""""""""""""""
# 			[Table 72: Specific Parameters for NFC-F Poll Mode]
# 		Bit Rate: 					1 Octet
# 		SENSF_RES Response Length: 	1 Octet
# 		SENSF_RES Response:			16 or 18 Octets
# 		"""""""""""""""
# 		bitrate = para_raw[para_payload:(para_payload+2*1)]	
# 		if(bitrate == "01"):
# 			print("  * Bit Rate: 212 kbps ("+bitrate+")")
# 		elif(bitrate == "02"):
# 			print("  * Bit Rate: 424 kbps ("+bitrate+")")
# 		else:
# 			print("  * Bit Rate: RFU ("+bitrate+")")			
# 		para_payload = para_payload + 2*1		

# 		sensf_res_rsp_len = para_raw[para_payload:(para_payload+2*1)]
# 		l = int(sensf_res_rsp_len,16)
# 		print("  * SENSF_RES Rsp Len:", l, "("+sensf_res_rsp_len+")")
# 		para_payload = para_payload + 2*1

# 		sensf_res_rsp = para_raw[para_payload:(para_payload+2*l)]	
# 		print("  * SENSF_RES Rsp: "+sensf_res_rsp)
# 		# SENSF_RES_PARSER(sensf_res_rsp,sensf_res_rsp_len)
# 		para_payload = para_payload + 2*l
	
# 	elif(rf_tech_mode_type == "F_PASSIVE_LISTEN"):
# 		"""""""""""""""
# 			[Table 73: Specific Parameters for NFC-F Listen Mode]
# 		Local NFCID2 Length: 	1 Octet
# 		Local NFCID2:			0 or 8 Octet(s)
# 		"""""""""""""""
# 		local_nfcid2_len = para_raw[p_payload:(p_payload+2*1)]
# 		l = int(local_nfcid2_len,16)
# 		print("  * Local NFCID2 Len:", l, "("+local_nfcid2_len+")")
# 		p_payload = p_payload + 2*1
		
# 		nfcid_2 = para_raw[p_payload:(p_payload+2*l)]	
# 		print("  * Local NFCID2: "+nfcid_2)
# 		p_payload = p_payload + 2*l	

# 	elif(rf_tech_mode_type == "V_PASSIVE_POLL"):
# 		"""""""""""""""
# 			[Table 74: Specific Parameters for NFC-V Poll Mode]
# 		RES_FLAG: 	1 Octet
# 		DSFID: 		1 Octet
# 		UID:		8 Octets
# 		"""""""""""""""
# 		res_flag = para_raw[para_payload:(para_payload+2*1)]
# 		print("  * RES_FLAG: "+res_flag)
# 		para_payload = para_payload + 2*1

# 		dsfid = para_raw[para_payload:(para_payload+2*1)]
# 		print("  * DSFID: "+dsfid)
# 		para_payload = para_payload + 2*1
		
# 		uid = para_raw[para_payload:(para_payload+2*8)]
# 		print("  * UID: "+uid)
# 		para_payload = para_payload + 2*8

# 	elif(rf_tech_mode_type == "ACTIVE_POLL"):
# 		"""""""""""""""
# 			[Table 75: Specific Parameters for NFC-ACM Poll Mode]
# 		ATR_RES Response Length: 	1 Octet (n)
# 		ATR_RES Response: 			n Octet(s)
# 		"""""""""""""""
# 		atr_res_rsp_len = para_raw[p_payload:(p_payload+2*1)]
# 		l = int(atr_res_rsp_len,16)
# 		print("  * ATR_RES Response Len:", l, "("+atr_res_rsp_len+")")
# 		p_payload = p_payload + 2*1
		
# 		atr_res_rsp = para_raw[p_payload:(p_payload+2*l)]	
# 		print("  * ATR_RES Response: "+atr_res_rsp)
# 		p_payload = p_payload + 2*l	

# 	elif(rf_tech_mode_type == "ACTIVE_LISTEN"):
# 		"""""""""""""""
# 			[Table 76: Specific Parameters for NFC-ACM Listen Mode]
# 		ATR_REQ Command Length: 	1 Octet (n)
# 		ATR_REQ Command: 			n Octet(s)
# 		"""""""""""""""
# 		atr_req_cmd_len = para_raw[p_payload:(p_payload+2*1)]
# 		l = int(atr_req_cmd_len,16)
# 		print("  * ATR_REQ Cmd Len:", l, "("+atr_req_cmd_len+")")
# 		p_payload = p_payload + 2*1
		
# 		atr_req_cmd = para_raw[p_payload:(p_payload+2*l)]	
# 		print("  * ATR_REQ Cmd: "+atr_req_cmd)
# 		p_payload = p_payload + 2*l	

# 	else:
# 		print("  * Proprietary parameters: "+para_raw[para_payload::])

# 61 03
def RF_DISCOVER_NTF(raw):
	"""""""""""""""
		[RF_DISCOVER_NTF]
    RF Discovery ID: 								1 Octet
    RF Protocol: 									1 Octet
    RF Technology and Mode: 						1 Octet
    Length of RF Technology Specific Parameters:	1 Octet (n)
    RF Technology Specific Parameters: 				0-n Octet(s)
    Notification Type: 								1 Octet
	"""""""""""""""
	# print("RF_DISCOVER_NTF")
	p_payload = Origin.RF_DISCOVER_NTF(raw, "nxp")
	return p_payload

# 21 04
def RF_DISCOVER_SELECT_CMD(raw):
	"""""""""""""""
		[RF_DISCOVER_SELECT_CMD]
    RF Discovery ID:	1 Octet
    RF Protocol: 		1 Octet
    RF Interface:		1 Octet
	"""""""""""""""
	# print("RF_DISCOVER_SELECT_CMD")
	p_payload = Origin.RF_DISCOVER_SELECT_CMD(raw, "nxp")
	return p_payload

# 41 04
def RF_DISCOVER_SELECT_RSP(raw):
	"""""""""""""""
		[RF_DISCOVER_SELECT_RSP]
    Status:		1 Octet
	"""""""""""""""
	# print("RF_DISCOVER_SELECT_RSP")
	p_payload = Origin.RF_DISCOVER_SELECT_RSP(raw, "nxp")
	return p_payload
		
# 61 05
def RF_INTF_ACTIVATED_NTF(raw):
	"""""""""""""""
		[RF_INTF_ACTIVATED_NTF]
    RF Discovery ID:								1 Octet
    RF Interface:									1 Octet
    RF Protocol: 									1 Octet
	Activation RF Technology and Mode:				1 Octet
	Max Data Packet Payload Size:					1 Octet
	Initial Number of Credits:						1 Octet
	Length of RF Technology Specific Parameters:	1 Octet
	RF Technology Specific Parameters:				0-n Octet(s)
	Data Exchange RF Technology and Mode:			1 Octet
	Data Exchange Transmit Bit Rate:				1 Octet
	Data Exchange Receive Bit Rate:					1 Octet
	Length of Activation Parameters:				1 Octet
	Activation Parameters:							0-n Octet(s)
	"""""""""""""""
	# print("RF_INTF_ACTIVATED_NTF")
	p_payload = Origin.RF_INTF_ACTIVATED_NTF(raw, "nxp")
	return p_payload

# 21 06
def RF_DEACTIVATE_CMD(raw):
	"""""""""""""""
		[RF_DEACTIVATE_CMD]
    Deactivation Type:		1 Octet
	"""""""""""""""
	# print("RF_DEACTIVATE_CMD")
	p_payload = Origin.RF_DEACTIVATE_CMD(raw, "nxp")
	return p_payload
	
# 41 06
def RF_DEACTIVATE_RSP(raw):
	"""""""""""""""
		[RF_DEACTIVATE_RSP]
    Status:		1 Octet
	"""""""""""""""
	# print("RF_DEACTIVATE_RSP")
	p_payload = Origin.RF_DEACTIVATE_RSP(raw, "nxp")
	return p_payload

# 61 06
def RF_DEACTIVATE_NTF(raw):
	"""""""""""""""
		[RF_DEACTIVATE_NTF]
    Deactivation Type:		1 Octet
    Deactivation Reason:	1 Octet
	"""""""""""""""
	# print("RF_DEACTIVATE_NTF")
	p_payload = Origin.RF_DEACTIVATE_NTF(raw, "nxp")
	return p_payload
	
# 61 07
def RF_FIELD_INFO_NTF(raw):
	"""""""""""""""
		[RF_FIELD_INFO_NTF]
    RF Field Status:		1 Octet
	"""""""""""""""
	# print("RF_FIELD_INFO_NTF")
	p_payload = Origin.RF_FIELD_INFO_NTF(raw, "nxp")
	return p_payload
	
# 21 08
def RF_T3T_POLLING_CMD(raw):
	"""""""""""""""
		[RF_T3T_POLLING_CMD]
    SENSF_REQ_PARAMS:		4 Octets
	"""""""""""""""
	# print("RF_T3T_POLLING_CMD")
	p_payload = Origin.RF_T3T_POLLING_CMD(raw, "nxp")
	return p_payload

# 41 08
def RF_T3T_POLLING_RSP(raw):
	"""""""""""""""
		[RF_T3T_POLLING_RSP]
    Status:		1 Octet
	"""""""""""""""
	# print("RF_T3T_POLLING_RSP")
	p_payload = Origin.RF_T3T_POLLING_RSP(raw, "nxp")
	return p_payload

# 61 08
def RF_T3T_POLLING_NTF(raw):
	"""""""""""""""
		[RF_T3T_POLLING_RSP]
    Status:					1 Octet
	Number of Responses:	1 Octet (n)
	Responses [1..n]:		m+1 Octets
	﹂	Length:				﹂	1 Octet (m)
	﹂	SENSF_RES: 			﹂	m Octet(s)
	"""""""""""""""
	# print("RF_T3T_POLLING_NTF")
	p_payload = Origin.RF_T3T_POLLING_NTF(raw, "nxp")
	return p_payload

# 61 09
def RF_NFCEE_ACTION_NTF(raw):
	"""""""""""""""
		[RF_NFCEE_ACTION_NTF]
    NFCEE ID:					1 Octet
	Trigger:					1 Octet
	Supporting Data Length:		1 Octet
	Supporting Data:			n Octet(s)
	"""""""""""""""
	# print("RF_NFCEE_ACTION_NTF")
	p_payload = Origin.RF_NFCEE_ACTION_NTF(raw, "nxp")
	return p_payload

# 61 0A
def RF_NFCEE_DISCOVERY_REQ_NTF(raw):
	"""""""""""""""
		[RF_NFCEE_DISCOVERY_REQ_NTF]
	Number of Information Entries:		1 Octet (n)
	Information Entry [1..n]:			x+2 Octets
	﹂	Type:							﹂	1 Octet
	﹂	Length:							﹂	1 Octet (x)
	﹂	Value: 							﹂	x Octet(s)
	"""""""""""""""
	# print("RF_NFCEE_DISCOVERY_REQ_NTF")
	p_payload = Origin.RF_NFCEE_DISCOVERY_REQ_NTF(raw, "nxp")
	return p_payload

# 21 0B
def RF_PARAMETER_UPDATE_CMD(raw):
	# RF_PARAMETER_UPDATE_CMD is not fully supported as corresponding scenarios can automatically be fulfilled when using ISO-DEP RF Interface.
	"""""""""""""""
		[RF_PARAMETER_UPDATE_CMD]
	Number of Parameters:					1 Octet (n)
	RF Communication Parameters [1..n]:		x+2 Octets
	﹂	ID:									﹂	1 Octet
	﹂	Length:								﹂	1 Octet (x)
	﹂	Value: 								﹂	x Octet(s)
	"""""""""""""""
	# print("RF_PARAMETER_UPDATE_CMD")
	p_payload = Origin.RF_PARAMETER_UPDATE_CMD(raw, "nxp")
	return p_payload

# 41 0B
def RF_PARAMETER_UPDATE_RSP(raw):
	"""""""""""""""
		[RF_PARAMETER_UPDATE_RSP]
    Status:		1 Octet
	Number of Parameters:					1 Octet (n)
	RF Communication Parameters [1..n]:		1 Octets
	"""""""""""""""
	# print("RF_PARAMETER_UPDATE_RSP")
	p_payload = Origin.RF_PARAMETER_UPDATE_RSP(raw, "nxp")
	return p_payload

# 21 0C
def RF_INTF_EXT_START_CMD(raw):
	"""""""""""""""
		[RF_INTF_EXT_START_CMD]
	RF Interface Extension:		1 Octet
	Start Parameter Length:		1 Octet (x)
	Start Parameter: 			x Octet(s)
	"""""""""""""""
	# print("RF_INTF_EXT_START_CMD")
	p_payload = 0
	print("[NCI] control message No Support")
	return p_payload

# 41 0C
def RF_INTF_EXT_START_RSP(raw):
	"""""""""""""""
		[RF_INTF_EXT_START_RSP]
    Status:		1 Octet
	"""""""""""""""
	# print("RF_INTF_EXT_START_RSP")
	p_payload = 0
	print("[NCI] control message No Support")
	return p_payload

# 21 0D
def RF_INTF_EXT_STOP_CMD(raw):
	"""""""""""""""
		[RF_INTF_EXT_STOP_CMD]
    RF Interface Extension:		1 Octet
    Stop Parameter Length::		1 Octet (x)
    Stop Parameter:				x Octet(s)
	"""""""""""""""
	# print("RF_INTF_EXT_STOP_CMD")
	p_payload = 0
	print("[NCI] control message No Support")
	return p_payload

# 41 0D
def RF_INTF_EXT_STOP_RSP(raw):
	"""""""""""""""
		[RF_INTF_EXT_STOP_RSP]
    Status:		1 Octet
	"""""""""""""""
	# print("RF_INTF_EXT_STOP_RSP")
	p_payload = 0
	print("[NCI] control message No Support")
	return p_payload

# 21 0E
def RF_EXT_AGG_ABORT_CMD(raw):
	"""""""""""""""
		[RF_EXT_AGG_ABORT_CMD]
    (Empty)
	"""""""""""""""
	p_payload = 0
	print("[NCI] control message No Support")
	return p_payload

# 41 0E
def RF_EXT_AGG_ABORT_RSP(raw):
	"""""""""""""""
		[RF_EXT_AGG_ABORT_RSP]
    Status:		1 Octet
	"""""""""""""""
	# print("RF_EXT_AGG_ABORT_RSP")
	p_payload = 0
	print("[NCI] control message No Support")
	return p_payload

# 21 0F
def RF_NDEF_ABORT_CMD(raw):
	"""""""""""""""
		[RF_NDEF_ABORT_CMD]
    (Empty)
	"""""""""""""""
	p_payload = 0
	print("[NCI] control message No Support")
	return p_payload
	
# 41 0F
def RF_NDEF_ABORT_RSP(raw):
	"""""""""""""""
		[RF_NDEF_ABORT_RSP]
    Status:		1 Octet
	"""""""""""""""
	# print("RF_NDEF_ABORT_RSP")
	p_payload = 0
	print("[NCI] control message No Support")
	return p_payload

# 21 10
def RF_ISO_DEP_NAK_PRESENCE_CMD(raw):
	"""""""""""""""
		[RF_ISO_DEP_NAK_PRESENCE_CMD]
    (Empty)
	"""""""""""""""
	p_payload = Origin.RF_ISO_DEP_NAK_PRESENCE_CMD(raw, "nxp")
	return p_payload

# 41 10
def RF_ISO_DEP_NAK_PRESENCE_RSP(raw):
	"""""""""""""""
		[RF_ISO_DEP_NAK_PRESENCE_RSP]
    Status:		1 Octet
	"""""""""""""""
	# print("RF_ISO_DEP_NAK_PRESENCE_RSP")
	p_payload = Origin.RF_ISO_DEP_NAK_PRESENCE_RSP(raw)
	return p_payload
	
# 61 10
def RF_ISO_DEP_NAK_PRESENCE_NTF(raw):
	"""""""""""""""
		[RF_ISO_DEP_NAK_PRESENCE_NTF]
    Status:		1 Octet
	"""""""""""""""
	# print("RF_ISO_DEP_NAK_PRESENCE_NTF")
	p_payload = Origin.RF_ISO_DEP_NAK_PRESENCE_NTF(raw, "nxp")
	return p_payload
	
# 21 11
def RF_SET_FORCED_NFCEE_ROUTING_CMD(raw):
	"""""""""""""""
		[RF_SET_FORCED_NFCEE_ROUTING_CMD]
    Forced NFCEE Routing State:		1 Octet
	Forced NFCEE Value Field:		0 or 2 Octet(s)
	﹂	Forced NFCEE				﹂	1 Octet
	﹂	Forced Power State			﹂	1 Octet
	"""""""""""""""
	# print("RF_SET_FORCED_NFCEE_ROUTING_CMD")
	p_payload = 0
	print("[NCI] control message No Support")
	return p_payload
	
# 41 11
def RF_SET_FORCED_NFCEE_ROUTING_RSP(raw):
	"""""""""""""""
		[RF_SET_FORCED_NFCEE_ROUTING_RSP]
    Status:		1 Octet
	"""""""""""""""
	# print("RF_SET_FORCED_NFCEE_ROUTING_RSP")
	p_payload = 0
	print("[NCI] control message No Support")
	return p_payload

# 61 18
def IOT_RETRY_NTF(raw):
	"""""""""""""""
		[IOT_RETRY_NTF]
	WupCounter:		1 Octet		Counter incremented each time a response to WupA is sent
	"""""""""""""""
	p_payload = 0
	counter = raw[p_payload:(p_payload+2*1)]
	print("  * WupCounter:", int(counter, 16))
	p_payload = p_payload + 2*1
	return p_payload

# 61 20
def FIELD_DETECT_NTF(raw):
	"""""""""""""""
		[FIELD_DETECT_NTF]
    Detection:		1 Octet
    RFU Field:		1 Octet
    System Code:	2 Octets
	"""""""""""""""
	p_payload = 0
	# print("FIELD_DETECT_NTF")
	detect = raw[p_payload:(p_payload+2*1)]
	detect_b = bin(int(detect, 16))[2::].zfill(8)
	print("  * Detection:", detect_b, "("+detect+")")
	print("   ~ Bit0 = RFU")
	print("   ~ Bit1 = WupA/ReqA detected")
	print("   ~ Bit2 = WupB/ReqB detected")
	print("   ~ Bit3 = PollReq (typeF) detected")
	print("   ~ Bit6 = RFU")
	print("   ~ Bit7 = RX error detected")
	p_payload = p_payload + 2*1
	# RFU
	p_payload = p_payload + 2*1

	sys_code = raw[p_payload:(p_payload+2*2)]
	if(detect_b[3:4] == '1'):
		print("  * POLL_REQ SC0-SC1:", sys_code)
	else:
		print("  * System Code:", sys_code)
	# print("")
	return p_payload

# 61 21
def PLL_UNLOCKED_NTF(raw):
	"""""""""""""""
		[PLL_UNLOCKED_NTF]
    (Empty)
	"""""""""""""""
	p_payload = 0
	# print("PLL_UNLOCKED_NTF")
	print('{0:^25}'.format("(Empty)"))
	# print("")
	return p_payload

# 61 23
def TxLDO_ERROR_NTF(raw):
	"""""""""""""""
		[TxLDO_ERROR_NTF]
    (Empty)
	"""""""""""""""
	p_payload = 0
	# print("TxLDO_ERROR_NTF")
	print('{0:^25}'.format("(Empty)"))
	# print("")
	return p_payload

# 61 28
def PLL_LOSTLOCK_NTF(raw):
	"""""""""""""""
		[PLL_LOSTLOCK_NTF]
    (Empty)
	"""""""""""""""
	p_payload = 0
	# print("PLL_LOSTLOCK_NTF")
	print('{0:^25}'.format("(Empty)"))
	# print("")
	return p_payload

# 61 29
def SETTINGS_CHANGE_NTF(raw):
	"""""""""""""""
		[SETTINGS_CHANGE_NTF]
	Index:		1 Octet		Index of the current settings change table
	"""""""""""""""
	p_payload = 0
	index = raw[p_payload:(p_payload+2*1)]
	print("  * Index:", index)
	p_payload = p_payload + 2*1
	return p_payload

# 61 2A
def RF_FREQ_ERROR_NTF(raw):
	"""""""""""""""
		[RF_FREQ_ERROR_NTF]
    (Empty)
	"""""""""""""""
	p_payload = 0
	# print("RF_FREQ_ERROR_NTF")
	print('{0:^25}'.format("(Empty)"))
	# print("")
	return p_payload

# 61 2B
def LPDET_ERROR_NTF(raw):
	"""""""""""""""
		[LPDET_ERROR_NTF]
    (Empty)
	"""""""""""""""
	p_payload = 0
	# print("LPDET_ERROR_NTF")
	print('{0:^25}'.format("(Empty)"))
	# print("")
	return p_payload