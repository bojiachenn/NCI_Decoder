import NFC_table

#	    Jimmt Chen  	#
#	Done on: 2024/2/20	#

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
	print("RF_DISCOVER_MAP_CMD")
	p_payload = 0
	
	num_of_cfg = raw[p_payload:(p_payload+2*1)]
	n = int(num_of_cfg, 16)
	print("- Number of Mapping Configurations:", n, "("+num_of_cfg+")\n")
	p_payload = p_payload + 2*1
	
	# print("- Mapping Configuration: ")
	for i in range(n):
		print("  -- [Mapping Cfg "+str(i)+"] --  ")
		rf_proto = raw[p_payload:(p_payload+2*1)]
		if((int(rf_proto,16) >= 128) & (int(rf_proto,16) <= 254)):
			rf_proto = '80-FE'
		print("  -- RF Protocol: "+NFC_table.tbl_rf_proto.get(rf_proto,"RFU")+" ("+raw[p_payload:(p_payload+2*1)]+")")
		p_payload = p_payload + 2*1

		mode = raw[p_payload:(p_payload+2*1)]	
		print("  -- Mode: "+NFC_table.tbl_mode.get(mode,"RFU")+" ("+mode+")")
		p_payload = p_payload + 2*1

		rf_if = raw[p_payload:(p_payload+2*1)]	
		print("  -- RF Interface: "+NFC_table.tbl_rf_if.get(rf_if,"RFU")+" ("+rf_if+")")
		p_payload = p_payload + 2*1		
		print("")
	print("")

# 41 00
def RF_DISCOVER_MAP_RSP(raw):
	"""""""""""""""
		[RF_DISCOVER_MAP_RSP]
    Status: 1 Octet
	"""""""""""""""
	print("RF_DISCOVER_MAP_RSP")
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]	
	print("- Status: "+NFC_table.tbl_status_codes.get(status,"RFU")+" ("+status+")")
	p_payload = p_payload + 2*1
	print("")

def LISTEN_MODE_ROUTING_INFO(raw):
	"""重複使用"""
	"""""""""""""""
		[RF_SET_LISTEN_MODE_ROUTING_CMD]
		[RF_GET_LISTEN_MODE_ROUTING_NTF]
	More:						1 Octet
	Number of Routing Entries:	1 Octet (n)
	Routing Entry [1..n]: 		x+2 Octets
	﹂	Qualifier-Type:			﹂	1 Octet
	﹂	Length: 				﹂	1 Octet (x)
	﹂	Value: 					﹂	x Octet
	"""""""""""""""
	p_payload = 0

	more = raw[p_payload:(p_payload+2*1)]	
	print("- More: "+NFC_table.tbl_more.get(more,"RFU")+" ("+more+")")
	p_payload = p_payload + 2*1
	
	num_of_router = raw[p_payload:(p_payload+2*1)]
	n = int(num_of_router, 16)
	print("- Number of Routing Entries:", n, "("+num_of_router+")\n")
	p_payload = p_payload + 2*1	
	
	# print("- Routing Entry:")
	for i in range(n):
		print("  -- [Routing Entry "+str(i)+"] --  ")
		q_type = raw[p_payload:(p_payload+2*1)]	
		print("  -- Type: "+NFC_table.tbl_L_mode_routing_entry_type.get(q_type[1:2],"0x5-0x9: RFU, 0xA-0xF: For proprietary use")+" ("+q_type+")")
		q_type_b=bin(int(q_type[0:1],16))[2::].zfill(4) # ref to Table 52
		if (q_type_b[1:2] == "1"):
			print("Routing is blocked for the power modes where it is not supported.")
		if (q_type_b[2:3] == "1"):
			print("Match is allowed when the SELECT AID is shorter than the AID in this routing table entry.")
		if (q_type_b[3:4] == "1"):
			print("Match is allowed when the SELECT AID is longer than the AID in this routing table entry.")
		p_payload = p_payload + 2*1

		len = raw[p_payload:(p_payload+2*1)]	
		x = int(len, 16)
		print("  -- Length:", x, "("+len+")")
		p_payload = p_payload + 2*1

		val_raw = raw[p_payload:(p_payload+2*x)]
		val_payload = 0
		p_payload = p_payload + 2*x

		print("  -- Value: "+val_raw)
		route_val = val_raw[val_payload:(val_payload+2*1)]
		if((int(route_val,16) >= 2) & (int(route_val,16) <= 15)):
			route_val = '02-0F'
		elif((int(route_val,16) >= 16) & (int(route_val,16) <= 127)):
			route_val = '10-7F'
		elif((int(route_val,16) >= 128) & (int(route_val,16) <= 254)):
			route_val = '80-FE'
		print("   --- Route: "+NFC_table.tbl_nfcee_id.get(route_val,"RFU")+" ("+val_raw[val_payload:(val_payload+2*1)]+")")
		val_payload = val_payload + 2*1
		
		pwr_state = val_raw[val_payload:(val_payload+2*1)]	
		pwr_state_b = bin(int(pwr_state,16))[2::].zfill(8)
		print("   --- Power State: "+pwr_state_b+" ("+pwr_state+")")
		for j in range (5,-1,-1):
			print('{0:<34}'.format("    * "+NFC_table.tbl_pwr_state.get(j,"RFU")+":"), end="")
			if(pwr_state_b[7-j:8-j] == "1"):
				print('{0:<10}'.format("Apply"))
			else:
				print('{0:<10}'.format("Not apply"))
		val_payload = val_payload + 2*1

		if (q_type[1:2] == "0"):
			"""""""""""""""
				[Table 54: Value Field for Technology-based Routing]
			Technology:		1 Octet
			"""""""""""""""	
			tech = val_raw[val_payload:(val_payload+2*1)]	
			print("   --- Technology: "+NFC_table.tbl_rf_tech.get(tech,"0x04–0x7F & 0XFF: RFU, 0x80-0xFE: For proprietary use")+" ("+tech+")")
			val_payload = val_payload + 2*1
			
		elif (q_type[1:2] == "1"):
			"""""""""""""""
				[Table 55: Value Field for Protocol-based Routing]
			Protocol:		1 Octet
			"""""""""""""""
			proto = val_raw[val_payload:(val_payload+2*1)]
			if((int(proto,16) >= 128) & (int(proto,16) <= 254)):
				proto = '80-FE'
			print("   --- Protocol: "+NFC_table.tbl_rf_proto.get(proto,"RFU")+" ("+proto+")")
			val_payload = val_payload + 2*1
		
		elif (q_type[1:2] == "2"):
			"""""""""""""""
				[Table 56: Value Field for AID-based Routing]
			AID:		    0-16 Octets
			"""""""""""""""
			# aid_value = val_raw[val_payload:]
			print("   --- AID: "+val_raw[val_payload:])
		
		elif (q_type[1:2] == "3"):			
			"""""""""""""""
				[Table 57: Value Field for System Code-based Routing]
			SC Route List:  2n Octets
			"""""""""""""""
			n = (x-2)/2
			for j in range(n):
				print("   --- SC Route "+str(i)+": "+val_raw[val_payload:(val_payload+2*2)])
				val_payload = val_payload + 2*2

		elif (q_type[1:2] == "4"):			
			"""""""""""""""
				[Table 58: Value Field for APDU Pattern-based Routing]
			Reference data:	n Octet(s)
			Mask:       	n Octet(s)
			"""""""""""""""
			n = (x-2)/2
			print("   --- Reference data: "+val_raw[val_payload:(val_payload+2*1)])
			val_payload = val_payload + 2*n
			print("   --- Mask: "+val_raw[val_payload:(val_payload+2*1)])
			val_payload = val_payload + 2*n
		print("")

# 21 01
def RF_SET_LISTEN_MODE_ROUTING_CMD(raw):
	print("RF_SET_LISTEN_MODE_ROUTING_CMD")
	LISTEN_MODE_ROUTING_INFO(raw)
	print("")

# 41 01
def RF_SET_LISTEN_MODE_ROUTING_RSP(raw):
	"""""""""""""""
		[RF_SET_LISTEN_MODE_ROUTING_RSP]
    Status: 1 Octet
	"""""""""""""""
	print("RF_SET_LISTEN_MODE_ROUTING_RSP")
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]
	print("- Status: "+NFC_table.tbl_status_codes.get(status,"RFU")+" ("+status+")")
	p_payload = p_payload + 2*1
	print("")

# 21 02
def RF_GET_LISTEN_MODE_ROUTING_CMD(raw):
	"""""""""""""""
		[RF_GET_LISTEN_MODE_ROUTING_CMD]
    (Empty)
	"""""""""""""""
	print("RF_GET_LISTEN_MODE_ROUTING_CMD")
	print("(Empty)")
	print("")

# 41 02
def RF_GET_LISTEN_MODE_ROUTING_RSP(raw):
	"""""""""""""""
		[RF_SET_LISTEN_MODE_ROUTING_RSP]
    Status: 1 Octet
	"""""""""""""""
	print("RF_GET_LISTEN_MODE_ROUTING_RSP")
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]
	print("- Status: "+NFC_table.tbl_status_codes.get(status,"RFU")+" ("+status+")")
	p_payload = p_payload + 2*1
	print("")

# 61 02
def RF_GET_LISTEN_MODE_ROUTING_NTF(raw):
	print("RF_GET_LISTEN_MODE_ROUTING_NTF")
	LISTEN_MODE_ROUTING_INFO(raw)
	print("")

# 21 03
def RF_DISCOVER_CMD(raw):
	"""""""""""""""
		[RF_DISCOVER_CMD]
	Number of Configurations:		1 Octet (n)
	Configuration [0..n]: 			2 Octets
	﹂	RF Technology and Mode:		﹂	1 Octet
	﹂	Discovery Frequency: 		﹂	1 Octet
	"""""""""""""""
	print("RF_DISCOVER_CMD")
	p_payload = 0

	num_cfg = raw[p_payload:(p_payload+2*1)]
	n = int(num_cfg, 16)
	print("- Number of Configurations:", n, "("+num_cfg+")\n")
	p_payload = p_payload + 2*1
	
	for i in range(n):
		print("  -- [Configuration "+str(i)+"] --  ")
		rf_tech_mode = raw[p_payload:(p_payload+2*1)]
		if((int(rf_tech_mode,16) >= 112) & (int(rf_tech_mode,16) <= 127)):
			rf_tech_mode = '70-7F'
		elif((int(rf_tech_mode,16) >= 240) & (int(rf_tech_mode,16) <= 255)):
			rf_tech_mode = 'F0-FF'
		print("  -- RF Technology and Mode: "+NFC_table.tbl_rf_tech_mode.get(rf_tech_mode,"RFU")+" ("+raw[p_payload:(p_payload+2*1)]+")")
		p_payload = p_payload + 2*1

		discovery_freq = raw[p_payload:(p_payload+2*1)]	
		freq = int(discovery_freq, 16)
		if((freq == 0) | (freq > 10)):
			print("  -- Discovery Frequency: "+"RFU")		
		else:
			print("  -- Discovery Frequency:", freq, "("+discovery_freq+")")
		p_payload = p_payload + 2*1
		print("")
	# print("")
	# print("  Note:Discovery Frequency: ")
	# print("  ---- 00/0B-FF: RFU")
	# print("  ---- 01: RF Technology and Mode will be executed in every discovery period")
	# print("  ---- 02-0A: These values are allowed for Poll Mode RF Technology and Mode values.")
	# print("  ----        This value specifies how often the Poll period of the specific RF Technology will be executed.")
	# print("  ----        For example, a value of 10 indicates that this Polling will be executed in every 10th discovery period.")
	print("")

# 41 03
def RF_DISCOVER_RSP(raw):
	"""""""""""""""
		[RF_DISCOVER_RSP]
    Status: 1 Octet
	"""""""""""""""
	print("RF_DISCOVER_RSP")
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]	
	print("- Status: "+NFC_table.tbl_status_codes.get(status,"RFU")+" ("+status+")")
	p_payload = p_payload + 2*1
	print("")

def RF_TECH_SPEC_PARA(rf_tech_mode, para_raw):
	"""部分共用"""
	"""""""""""""""
		[RF_DISCOVER_NTF]
		[RF_INTF_ACTIVATED_NTF]
	"""""""""""""""
	para_payload = 0
	rf_tech_mode_type = NFC_table.tbl_rf_tech_mode.get(rf_tech_mode,"RFU")
	if(rf_tech_mode_type == "NFC_A_PASSIVE_POLL_MODE"):
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
		sens_res_rsp = para_raw[para_payload:(para_payload+2*2)]
		print("- SENS_RES Response: "+sens_res_rsp)
		para_payload = para_payload + 2*2		
		
		id_len = para_raw[para_payload:(para_payload+2*1)]
		l = int(id_len,16)
		print("- NFCID1 Length:", l, "("+id_len+")")
		para_payload = para_payload + 2*1	

		id = para_raw[para_payload:(para_payload+2*l)]
		print("- NFCID1: "+id)
		para_payload = para_payload + 2*l	
		
		sel_res_rsp_len = para_raw[para_payload:(para_payload+2*1)]	
		l = int(sel_res_rsp_len,16)
		print("- SEL_RES Response Length:", l, "("+sel_res_rsp_len+")")
		para_payload = para_payload + 2*1	

		sel_res_rsp = para_raw[para_payload:(para_payload+2*l)]	
		print("- SEL_RES Response: "+sel_res_rsp)
		para_payload = para_payload + 2*l
	
		hrx_len = para_raw[para_payload:(para_payload+2*1)]	
		l = int(hrx_len,16)
		print("- HRx Length:", l, "("+hrx_len+")")
		para_payload = para_payload + 2*1	
		
		hrx_val = para_raw[para_payload:(para_payload+2*l)]	
		print("- HRx: "+hrx_val)
		para_payload = para_payload + 2*l

	elif(rf_tech_mode_type == "NFC_A_PASSIVE_LISTEN_MODE"):
		"""""""""""""""
			[Table 69: Specific Parameters for NFC-A Listen Mode]
		(Empty)
		"""""""""""""""
		print("- There is no RF Technology Specific Parameters")
		
	elif(rf_tech_mode_type == "NFC_B_PASSIVE_POLL_MODE"):
		"""""""""""""""
			[Table 70: Specific Parameters for NFC-B Poll Mode]
		SENSB_RES Response Length: 			1 Octet
		SENSB_RES Response: 				11 or 12 Octets
		"""""""""""""""
		sensb_res_rsp_len = para_raw[para_payload:(para_payload+2*1)]
		l = int(sensb_res_rsp_len,16)
		print("- SENSB_RES Response Length:", l, "("+sensb_res_rsp_len+")")
		para_payload = para_payload + 2*1

		sensb_res_rsp = para_raw[para_payload:(para_payload+2*l)]	
		print("- SENSB_RES Response: "+sensb_res_rsp)
		para_payload = para_payload + 2*l

	elif(rf_tech_mode_type == "NFC_B_PASSIVE_LISTEN_MODE"):
		"""""""""""""""
			[Table 71: Specific Parameters for NFC-B Listen Mode]
		SENSB_REQ Command:		1 Octet
		"""""""""""""""
		sensb_req_cmd = para_raw[para_payload:(para_payload+2*1)]	
		print("- SENSB_REQ Command:: "+sensb_req_cmd)
		para_payload = para_payload + 2*1

	elif(rf_tech_mode_type == "NFC_F_PASSIVE_POLL_MODE"):
		"""""""""""""""
			[Table 72: Specific Parameters for NFC-F Poll Mode]
		Bit Rate: 					1 Octet
		SENSF_RES Response Length: 	1 Octet
		SENSF_RES Response:			16 or 18 Octets
		"""""""""""""""
		bitrate = para_raw[para_payload:(para_payload+2*1)]	
		if(bitrate == "01"):
			print("- Bit Rate: 212 kbps ("+bitrate+")")
		elif(bitrate == "02"):
			print("- Bit Rate: 424 kbps ("+bitrate+")")
		else:
			print("- Bit Rate: RFU ("+bitrate+")")			
		para_payload = para_payload + 2*1		

		sensf_res_rsp_len = para_raw[para_payload:(para_payload+2*1)]
		l = int(sensf_res_rsp_len,16)
		print("- SENSF_RES Response Length:", l, "("+sensf_res_rsp_len+")")
		para_payload = para_payload + 2*1

		sensf_res_rsp = para_raw[para_payload:(para_payload+2*l)]	
		print("- SENSF_RES Response: "+sensf_res_rsp)
		# SENSF_RES_PARSER(sensf_res_rsp,sensf_res_rsp_len)
		para_payload = para_payload + 2*l
	
	elif(rf_tech_mode_type == "NFC_F_PASSIVE_LISTEN_MODE"):
		"""""""""""""""
			[Table 73: Specific Parameters for NFC-F Listen Mode]
		Local NFCID2 Length: 	1 Octet
		Local NFCID2:			0 or 8 Octet(s)
		"""""""""""""""
		local_nfcid2_len = para_raw[p_payload:(p_payload+2*1)]
		l = int(local_nfcid2_len,16)
		print("- Local NFCID2 Length:", l, "("+local_nfcid2_len+")")
		p_payload = p_payload + 2*1
		
		nfcid_2 = para_raw[p_payload:(p_payload+2*l)]	
		print("- Local NFCID2: "+nfcid_2)
		p_payload = p_payload + 2*l	

	elif(rf_tech_mode_type == "NFC_V_PASSIVE_POLL_MODE"):
		"""""""""""""""
			[Table 74: Specific Parameters for NFC-V Poll Mode]
		RES_FLAG: 	1 Octet
		DSFID: 		1 Octet
		UID:		8 Octets
		"""""""""""""""
		res_flag = para_raw[para_payload:(para_payload+2*1)]
		print("- RES_FLAG: "+res_flag)
		para_payload = para_payload + 2*1

		dsfid = para_raw[para_payload:(para_payload+2*1)]
		print("- DSFID: "+dsfid)
		para_payload = para_payload + 2*1
		
		uid = para_raw[para_payload:(para_payload+2*8)]
		print("- UID: "+uid)
		para_payload = para_payload + 2*8

	elif(rf_tech_mode_type == "NFC_ACTIVE_POLL_MODE"):
		"""""""""""""""
			[Table 75: Specific Parameters for NFC-ACM Poll Mode]
		ATR_RES Response Length: 	1 Octet (n)
		ATR_RES Response: 			n Octet(s)
		"""""""""""""""
		atr_res_rsp_len = para_raw[p_payload:(p_payload+2*1)]
		l = int(atr_res_rsp_len,16)
		print("- ATR_RES Response Length:", l, "("+atr_res_rsp_len+")")
		p_payload = p_payload + 2*1
		
		atr_res_rsp = para_raw[p_payload:(p_payload+2*l)]	
		print("- ATR_RES Response: "+atr_res_rsp)
		p_payload = p_payload + 2*l	

	elif(rf_tech_mode_type == "NFC_ACTIVE_LISTEN_MODE"):
		"""""""""""""""
			[Table 76: Specific Parameters for NFC-ACM Listen Mode]
		ATR_REQ Command Length: 	1 Octet (n)
		ATR_REQ Command: 			n Octet(s)
		"""""""""""""""
		atr_req_cmd_len = para_raw[p_payload:(p_payload+2*1)]
		l = int(atr_req_cmd_len,16)
		print("- ATR_REQ Command Length:", l, "("+atr_req_cmd_len+")")
		p_payload = p_payload + 2*1
		
		atr_req_cmd = para_raw[p_payload:(p_payload+2*l)]	
		print("- ATR_REQ Command: "+atr_req_cmd)
		p_payload = p_payload + 2*l	

	else:
		print("- Proprietary parameters: "+para_raw[para_payload::])

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
	print("RF_DISCOVER_NTF")
	p_payload = 0
	
	rf_dis_id = raw[p_payload:(p_payload+2*1)]	
	print("- RF Discovery ID: "+NFC_table.tbl_rf_dis_id.get(rf_dis_id,"Dynamically assigned by the NFCC")+" ("+rf_dis_id+")")
	p_payload = p_payload + 2*1
	
	rf_proto = raw[p_payload:(p_payload+2*1)]
	if((int(rf_proto,16) >= 128) & (int(rf_proto,16) <= 254)):
		rf_proto = '80-FE'
	print("- RF Protocol: "+NFC_table.tbl_rf_proto.get(rf_proto,"RFU")+" ("+rf_proto+")")
	p_payload = p_payload + 2*1
	
	rf_tech_mode = raw[p_payload:(p_payload+2*1)]
	if((int(rf_tech_mode,16) >= 112) & (int(rf_tech_mode,16) <= 127)):
		rf_tech_mode = '70-7F'
	elif((int(rf_tech_mode,16) >= 240) & (int(rf_tech_mode,16) <= 255)):
		rf_tech_mode = 'F0-FF'
	print("- RF Technology and Mode: "+NFC_table.tbl_rf_tech_mode.get(rf_tech_mode,"RFU")+" ("+raw[p_payload:(p_payload+2*1)]+")")
	p_payload = p_payload + 2*1

	rf_tech_len = raw[p_payload:(p_payload+2*1)]
	n = int(rf_tech_len,16)
	print("- Length of RF Technology Specific Parameters:", n, "("+rf_tech_len+")")
	p_payload = p_payload + 2*1
	
	para_raw = raw[p_payload:(p_payload+2*n)]
	RF_TECH_SPEC_PARA(rf_tech_mode, para_raw)
	p_payload = p_payload + 2*n
	
	notificaiton_type = raw[p_payload:(p_payload+2*1)]	
	if(notificaiton_type == "00"):
		print("- Notification Type: Last Notification ("+notificaiton_type+")")
	elif(notificaiton_type == "01"):
		print("- Notification Type: Last Notification (due to NFCC reaching its resource limit) ("+notificaiton_type+")")
	elif(notificaiton_type == "02"):
		print("- Notification Type: More Notification to follow ("+notificaiton_type+")")
	else:
		print("- Notification Type: RFU ("+notificaiton_type+")")	
	p_payload = p_payload + 2*1
	print("")

# 21 04
def RF_DISCOVER_SELECT_CMD(raw):
	"""""""""""""""
		[RF_DISCOVER_SELECT_CMD]
    RF Discovery ID:	1 Octet
    RF Protocol: 		1 Octet
    RF Interface:		1 Octet
	"""""""""""""""
	print("RF_DISCOVER_SELECT_CMD")
	p_payload = 0
	
	rf_dis_id = raw[p_payload:(p_payload+2*1)]	
	print("- RF Discovery ID: "+NFC_table.tbl_rf_dis_id.get(rf_dis_id,"Dynamically assigned by the NFCC")+" ("+rf_dis_id+")")
	p_payload = p_payload + 2*1

	rf_proto = raw[p_payload:(p_payload+2*1)]	
	if((int(rf_proto,16) >= 128) & (int(rf_proto,16) <= 254)):
		rf_proto = '80-FE'
	print("- RF Protocol: "+NFC_table.tbl_rf_proto.get(rf_proto,"RFU")+" ("+raw[p_payload:(p_payload+2*1)]+")")
	p_payload = p_payload + 2*1
	
	rf_if = raw[p_payload:(p_payload+2*1)]
	if((int(rf_if,16) >= 128) & (int(rf_if,16) <= 254)):
		rf_if = '80-FE'
	print("- RF Interface: "+NFC_table.tbl_rf_if.get(rf_if,"RFU")+" ("+raw[p_payload:(p_payload+2*1)]+")")
	p_payload = p_payload + 2*1
	print("")	

# 41 04
def RF_DISCOVER_SELECT_RSP(raw):
	"""""""""""""""
		[RF_DISCOVER_SELECT_RSP]
    Status:		1 Octet
	"""""""""""""""
	print("RF_DISCOVER_SELECT_RSP")
	p_payload = 0
	
	status=raw[p_payload:(p_payload+2*1)]	
	print("- Status: "+NFC_table.tbl_status_codes.get(status,"RFU")+" ("+status+")")
	p_payload = p_payload + 2*1
	print("")
		
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
	print("RF_INTF_ACTIVATED_NTF")
	p_payload = 0
	
	rf_dis_id = raw[p_payload:(p_payload+2*1)]	
	print("- RF Discovery ID: "+NFC_table.tbl_rf_dis_id.get(rf_dis_id,"Dynamically assigned by the NFCC")+" ("+rf_dis_id+")")
	p_payload = p_payload + 2*1
	
	rf_if = raw[p_payload:(p_payload+2*1)]	
	print("- RF Interface: "+NFC_table.tbl_rf_if.get(rf_if,"RFU")+" ("+rf_if+")")
	p_payload = p_payload + 2*1
	
	rf_proto=raw[p_payload:(p_payload+2*1)]
	if((int(rf_proto,16) >= 128) & (int(rf_proto,16) <= 254)):
		rf_proto = '80-FE'
	print("- RF Protocol: "+NFC_table.tbl_rf_proto.get(rf_proto,"RFU")+" ("+rf_proto+")")
	p_payload = p_payload + 2*1
	activ_rf_tech_mode=raw[p_payload:(p_payload+2*1)]
	if((int(activ_rf_tech_mode,16) >= 112) & (int(activ_rf_tech_mode,16) <= 127)):
		activ_rf_tech_mode = '70-7F'
	elif((int(activ_rf_tech_mode,16) >= 240) & (int(activ_rf_tech_mode,16) <= 255)):
		activ_rf_tech_mode = 'F0-FF'
	print("- Activation RF Technology and Mode: "+NFC_table.tbl_rf_tech_mode.get(activ_rf_tech_mode,"RFU")+" ("+raw[p_payload:(p_payload+2*1)]+")")
	p_payload = p_payload + 2*1
	
	max_data_size=raw[p_payload:(p_payload+2*1)]
	size = int(max_data_size,16)
	print("- Max Data Packet Payload Size:", size, "("+max_data_size+")")
	p_payload = p_payload + 2*1

	num_credits = raw[p_payload:(p_payload+2*1)]
	if(num_credits == "FF"):
		print("- Initial Number of Credits: "+"Data flow control is not used"+" ("+num_credits+")")
	else:
		print("- Initial Number of Credits: ", int(num_credits), "("+num_credits+")")
	p_payload = p_payload + 2*1
	
	len_rf_tech_para = raw[p_payload:(p_payload+2*1)]
	l = int(len_rf_tech_para,16)
	print("- Length of RF Technology Specific Parameters:", l, "("+len_rf_tech_para+")")
	p_payload = p_payload + 2*1

	if(l != 0):
		para_raw = raw[p_payload:(p_payload+2*l)]
		RF_TECH_SPEC_PARA(activ_rf_tech_mode, para_raw)
		p_payload = p_payload + 2*l
		
	data_ex_rf_tech_mode = raw[p_payload:(p_payload+2*1)]
	if((int(data_ex_rf_tech_mode,16) >= 112) & (int(data_ex_rf_tech_mode,16) <= 127)):
		data_ex_rf_tech_mode = '70-7F'
	elif((int(data_ex_rf_tech_mode,16) >= 240) & (int(data_ex_rf_tech_mode,16) <= 255)):
		data_ex_rf_tech_mode = 'F0-FF'
	print("- Data Exchange RF Technology and Mode: "+NFC_table.tbl_rf_tech_mode.get(data_ex_rf_tech_mode,"RFU")+" ("+raw[p_payload:(p_payload+2*1)]+")")
	p_payload = p_payload + 2*1

	data_ex_tx_bitrate = raw[p_payload:(p_payload+2*1)]	
	if((int(data_ex_tx_bitrate,16) >= 128) & (int(data_ex_tx_bitrate,16) <= 254)):
		data_ex_tx_bitrate = '80-FE'
	print("- Data Exchange Transmit Bit Rate: "+NFC_table.tbl_bit_rates.get(data_ex_tx_bitrate,"RFU")+" ("+raw[p_payload:(p_payload+2*1)]+")")
	p_payload = p_payload + 2*1

	data_ex_rx_bitrate=raw[p_payload:(p_payload+2*1)]
	if((int(data_ex_rx_bitrate,16) >= 128) & (int(data_ex_rx_bitrate,16) <= 254)):
		data_ex_rx_bitrate = '80-FE'
	print("- Data Exchange Receive Bit Rate: "+NFC_table.tbl_bit_rates.get(data_ex_rx_bitrate,"RFU")+" ("+raw[p_payload:(p_payload+2*1)]+")")
	p_payload = p_payload + 2*1
	
	len_activate_para = raw[p_payload:(p_payload+2*1)]
	n = int(len_activate_para,16)
	print("- Length of Activation Parameters:", n, "("+len_activate_para+")")
	p_payload = p_payload + 2*1
	
	rf_if_type = NFC_table.tbl_rf_if.get(rf_if,"RFU")
	rf_tech_mode_type = NFC_table.tbl_rf_tech_mode.get(activ_rf_tech_mode,"RFU")
	if(rf_if_type == "ISO-DEP RF Interface"):
		if(rf_tech_mode_type == "NFC_A_PASSIVE_POLL_MODE"): # Table 95
			rat_rsp_len = raw[p_payload:(p_payload+2*1)]
			l = int(rat_rsp_len,16)
			print("- RATS Response Length:", l, "("+rat_rsp_len+")")
			p_payload = p_payload + 2*1
			
			rat_rsp=raw[p_payload:(p_payload+2*l)]	
			print("- RATS Response: "+rat_rsp)
			p_payload = p_payload + 2*l
		
		elif(rf_tech_mode_type == "NFC_B_PASSIVE_POLL_MODE"): # Table 96
			attrib_len = raw[p_payload:(p_payload+2*1)]
			l = int(attrib_len,16)
			print("- ATTRIB Response Length:", l, "("+attrib_len+")")
			p_payload = p_payload + 2*1
			
			attrib_rsp = raw[p_payload:(p_payload+2*l)]	
			print("- ATTRIB Response: "+attrib_rsp)
			p_payload = p_payload + 2*l

		elif(rf_tech_mode_type == "NFC_A_PASSIVE_LISTEN_MODE"): # Table 98
			rat_cmd_para = raw[p_payload:(p_payload+2*1)]	
			print("- RATS Command Param: "+rat_cmd_para)
			p_payload = p_payload + 2*1

		elif(rf_tech_mode_type == "NFC_B_PASSIVE_LISTEN_MODE"): # Table 99
			attrib_cmd_len = raw[p_payload:(p_payload+2*1)]
			l = int(attrib_cmd_len,16)
			print("- ATTRIB Command Length:", l, "("+attrib_cmd_len+")")
			p_payload = p_payload + 2*1
			
			attrib_cmd_rsp = raw[p_payload:(p_payload+2*l)]	
			print("- ATTRIB Command: "+attrib_cmd_rsp)
			p_payload = p_payload + 2*l	

		else:
			if (n > 0):
				activate_para = raw[p_payload:(p_payload+2*n)]	
				print("- Activation Parameters: "+activate_para)
				p_payload = p_payload + 2*n
			
	elif(rf_if_type == "NFC-DEP RF Interface"):
		if((rf_tech_mode_type == "NFC_A_PASSIVE_POLL_MODE") | (rf_tech_mode_type == "NFC_F_PASSIVE_POLL_MODE")): # Table 102
			atr_res_rsp_len = raw[p_payload:(p_payload+2*1)]
			l = int(atr_res_rsp_len,16)
			print("- ATR_RES Response Length:", l, "("+atr_res_rsp_len+")")
			p_payload = p_payload + 2*1

			attrib_cmd_rsp = raw[p_payload:(p_payload+2*l)]	
			print("- ATR_RES Response: "+attrib_cmd_rsp)
			p_payload = p_payload + 2*l

		elif((rf_tech_mode_type == "NFC_A_PASSIVE_LISTEN_MODE") | (rf_tech_mode_type == "NFC_F_PASSIVE_LISTEN_MODE")): # Table 103
			atr_req_cmd_len = raw[p_payload:(p_payload+2*1)]
			l = int(atr_req_cmd_len,16)
			print("- ATR_REQ Command Length:", l, "("+atr_req_cmd_len+")")
			p_payload = p_payload + 2*1

			atr_req_cmd = raw[p_payload:(p_payload+2*l)]	
			print("- ATR_REQ Command: "+atr_req_cmd)
			p_payload = p_payload + 2*l

			len_rdu_val = raw[p_payload:(p_payload+2*1)]
			print("- Data Exchange Length Reduction: "+NFC_table.tbl_len_rdu_val.get(len_rdu_val,"RFU")+" ("+len_rdu_val+")")
			p_payload = p_payload + 2*1

		else:
			if (n > 0):
				activate_para = raw[p_payload:(p_payload+2*n)]	
				print("- Activation Parameters: "+activate_para)
				p_payload = p_payload + 2*n

	else:
		if (n > 0):
			activate_para=raw[p_payload:(p_payload+2*n)]	
			print("- Activation Parameters: "+activate_para)
			p_payload = p_payload + 2*n
	print("")	

# 21 06
def RF_DEACTIVATE_CMD(raw):
	"""""""""""""""
		[RF_DEACTIVATE_CMD]
    Deactivation Type:		1 Octet
	"""""""""""""""
	print("RF_DEACTIVATE_CMD")
	p_payload = 0
	
	deactivate_type = raw[p_payload:(p_payload+2*1)]	
	print("- Deactivation Type: "+NFC_table.tbl_deactivate_type.get(deactivate_type,"RFU")+" ("+deactivate_type+")")
	p_payload = p_payload + 2*1
	print("")	
	
# 41 06
def RF_DEACTIVATE_RSP(raw):
	"""""""""""""""
		[RF_DEACTIVATE_RSP]
    Status:		1 Octet
	"""""""""""""""
	print("RF_DEACTIVATE_RSP")
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]	
	print("- Status: "+NFC_table.tbl_status_codes.get(status,"RFU")+" ("+status+")")
	p_payload = p_payload + 2*1
	print("")

# 61 06
def RF_DEACTIVATE_NTF(raw):
	"""""""""""""""
		[RF_DEACTIVATE_NTF]
    Deactivation Type:		1 Octet
    Deactivation Reason:	1 Octet
	"""""""""""""""
	print("RF_DEACTIVATE_NTF")
	p_payload = 0
	
	deactivate_type = raw[p_payload:(p_payload+2*1)]	
	print("- Deactivation Type: "+NFC_table.tbl_deactivate_type.get(deactivate_type,"RFU")+" ("+deactivate_type+")")
	p_payload = p_payload + 2*1

	deactivate_reason = raw[p_payload:(p_payload+2*1)]	
	print("- Deactivation Reason: "+NFC_table.tbl_deactivate_reason.get(deactivate_reason,"RFU")+" ("+deactivate_reason+")")
	p_payload = p_payload + 2*1
	print("")	
	
# 61 07
def RF_FIELD_INFO_NTF(raw):
	"""""""""""""""
		[RF_FIELD_INFO_NTF]
    RF Field Status:		1 Octet
	"""""""""""""""
	print("RF_FIELD_INFO_NTF")
	p_payload = 0
	
	rf_field_status = raw[p_payload:(p_payload+2*1)]
	if(int(rf_field_status,16) == 1):
		print("- RF Field Status: "+"Operating field generated by Remote NFC Endpoint. ("+rf_field_status+")")
	else:
		print("- RF Field Status: "+"No Operating field generated by Remote NFC Endpoint. ("+rf_field_status+")")
	p_payload = p_payload + 2*1
	print("")	
	
# 21 08
def RF_T3T_POLLING_CMD(raw):
	"""""""""""""""
		[RF_T3T_POLLING_CMD]
    SENSF_REQ_PARAMS:		4 Octets
	"""""""""""""""
	print("RF_T3T_POLLING_CMD")
	p_payload = 0
	
	sensf_req = raw[p_payload:(p_payload+2*4)]	
	print("- SENSF_REQ_PARAMS: "+sensf_req)
	p_payload = p_payload + 2*4
	print("")	

# 41 08
def RF_T3T_POLLING_RSP(raw):
	"""""""""""""""
		[RF_T3T_POLLING_RSP]
    Status:		1 Octet
	"""""""""""""""
	print("RF_T3T_POLLING_RSP")
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]	
	print("- Status: "+NFC_table.tbl_status_codes.get(status,"RFU")+" ("+status+")")
	p_payload = p_payload + 2*1
	print("")

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
	print("RF_T3T_POLLING_NTF")
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]	
	print("- Status: "+NFC_table.tbl_status_codes.get(status,"RFU")+" ("+status+")")
	p_payload = p_payload + 2*1
	
	num_rsp = raw[p_payload:(p_payload+2*1)]	
	n = int(num_rsp,16)
	print("- Number of Responses:", n, "("+num_rsp+")\n")
	p_payload = p_payload + 2*1
	
	for i in range(n):
		print("  -- [Response "+str(i)+"] --  ")
		len_sensf_res = raw[p_payload:(p_payload+2*1)]
		l = int(len_sensf_res,16)
		print("  -- Length:", l, "("+len_sensf_res+")")
		p_payload = p_payload + 2*1
		
		sensf_res_data = raw[p_payload:(p_payload+2*l)]	
		print("  -- SENSF_RES: "+sensf_res_data)
		# SENSF_RES_PARSER(sensf_res_data,len_sensf_res)
		p_payload = p_payload + 2*l
		print("")
	print("")

# 61 09
def RF_NFCEE_ACTION_NTF(raw):
	"""""""""""""""
		[RF_NFCEE_ACTION_NTF]
    NFCEE ID:					1 Octet
	Trigger:					1 Octet
	Supporting Data Length:		1 Octet
	Supporting Data:			n Octet(s)
	"""""""""""""""
	print("RF_NFCEE_ACTION_NTF")
	p_payload = 0
	
	nfcee_id = raw[p_payload:(p_payload+2*1)]
	if((int(nfcee_id,16) >= 2) & (int(nfcee_id,16) <= 15)):
		nfcee_id = '02-0F'
	elif((int(nfcee_id,16) >= 16) & (int(nfcee_id,16) <= 127)):
		nfcee_id = '10-7F'
	elif((int(nfcee_id,16) >= 128) & (int(nfcee_id,16) <= 254)):
		nfcee_id = '80-FE'
	print("- NFCEE ID: "+NFC_table.tbl_nfcee_id.get(nfcee_id,"RFU")+" ("+raw[p_payload:(p_payload+2*1)]+")")
	p_payload = p_payload + 2*1

	nfcee_ntf_trig = raw[p_payload:(p_payload+2*1)]
	if((int(nfcee_ntf_trig,16) >= 16) & (int(nfcee_ntf_trig,16) <= 127)):
		nfcee_ntf_trig = '10-7F'
	print("- Trigger: "+NFC_table.tbl_nfcee_ntf_trig.get(nfcee_ntf_trig,"RFU")+" ("+raw[p_payload:(p_payload+2*1)]+")")
	p_payload = p_payload + 2*1
	
	data_len = raw[p_payload:(p_payload+2*1)]	
	n = int(data_len,16)
	print("- Supporting Data Length:", n, "("+data_len+")")
	p_payload = p_payload + 2*1
	
	data_val = raw[p_payload:(p_payload+2*n)]	
	print("- Supporting Data: ")
	if(nfcee_ntf_trig == "00"):
		print("  -- AID: "+data_val)
	elif(nfcee_ntf_trig == "01"):
		if((int(data_val,16) >= 128) & (int(data_val,16) <= 254)):
			rf_proto = '80-FE'
		else:
			rf_proto = data_val
		print("  -- RF Protocol: "+NFC_table.tbl_rf_proto.get(rf_proto,"RFU")+" ("+data_val+")")
	elif((nfcee_ntf_trig == "02") | (nfcee_ntf_trig == "05")):
		print("  -- RF Technology: "+NFC_table.tbl_rf_tech.get(data_val,"RFU")+" ("+data_val+")")
	elif(nfcee_ntf_trig == "03"):
		print("  -- SC Route: "+data_val)
	elif(nfcee_ntf_trig == "04"):
		print("  -- Reference data: "+data_val[:(n/2)])
		print("  -- Mask: "+data_val[(n/2):])
	p_payload = p_payload + 2*n
	print("")

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
	print("RF_NFCEE_DISCOVERY_REQ_NTF")
	p_payload = 0
	
	num_info = raw[p_payload:(p_payload+2*1)]
	n = int(num_info,16)
	print("- Number Of Information Entries:", n, "("+num_info+")\n")
	p_payload = p_payload + 2*1

	for i in range(int(num_info,16)):
		print("  -- [Information Entry "+str(i)+"] --  ")
		type_val = raw[p_payload:(p_payload+2*1)]
		if(type_val == "00"): # Table 85
			print("  -- Type: "+"Information about the particular discovery request in this TLV is to be added to the list"+" ("+type_val+")")
		elif(type_val == "01"):
			print("  -- Type: "+"Information about the particular discovery request in this TLV is to be removed to the list"+" ("+type_val+")")
		p_payload = p_payload + 2*1	

		data_len = raw[p_payload:(p_payload+2*1)]	
		x = int(data_len,16)
		print("  -- Length:", x, "("+data_len+")")
		p_payload = p_payload + 2*1	
		
		data_val = raw[p_payload:(p_payload+2*x)]	
		print("  -- Value: "+data_val)
		if((type_val == "00") | (type_val == "01")):
			nfcee_id = data_val[0:2]
			if((int(nfcee_id,16) >= 2) & (int(nfcee_id,16) <= 15)):
				nfcee_id = '02-0F'
			elif((int(nfcee_id,16) >= 16) & (int(nfcee_id,16) <= 127)):
				nfcee_id = '10-7F'
			elif((int(nfcee_id,16) >= 128) & (int(nfcee_id,16) <= 254)):
				nfcee_id = '80-FE'
			print("   --- NFCEE: "+NFC_table.tbl_nfcee_id.get(nfcee_id,"RFU")+" ("+data_val[0:2]+")")
			rf_tech_mode = data_val[2:4]
			if((int(rf_tech_mode,16) >= 112) & (int(rf_tech_mode,16) <= 127)):
				rf_tech_mode = '70-7F'
			elif((int(rf_tech_mode,16) >= 240) & (int(rf_tech_mode,16) <= 255)):
				rf_tech_mode = 'F0-FF'
			print("   --- RF Technology and Mode: "+NFC_table.tbl_rf_tech_mode.get(rf_tech_mode,"RFU")+" ("+data_val[2:4]+")")
			rf_proto = data_val[4:6]
			if((int(rf_proto,16) >= 128) & (int(rf_proto,16) <= 254)):
				rf_proto = '80-FE'
			print("   --- RF Protocol: "+NFC_table.tbl_rf_proto.get(rf_proto,"RFU")+" ("+rf_proto+")")
		p_payload = p_payload + 2*x
		print("")
	print("")

# 21 0B
def RF_PARAMETER_UPDATE_CMD(raw):
	"""""""""""""""
		[RF_PARAMETER_UPDATE_CMD]
	Number of Parameters:					1 Octet (n)
	RF Communication Parameters [1..n]:		x+2 Octets
	﹂	ID:									﹂	1 Octet
	﹂	Length:								﹂	1 Octet (x)
	﹂	Value: 								﹂	x Octet(s)
	"""""""""""""""
	print("RF_PARAMETER_UPDATE_CMD")
	p_payload = 0
	
	num_para = raw[p_payload:(p_payload+2*1)]	
	n = int(num_para,16)
	print("- Number of Parameters:", n, "("+num_para+")\n")
	p_payload = p_payload + 2*1

	for i in range(n):
		print("- [RF Communication "+str(i)+"] --  ")
		id_val = raw[p_payload:(p_payload+2*1)]
		if(int(id_val,16) >= 128):
			id_val = '80-FF'
		print("- Type ID: "+NFC_table.tbl_rf_commu_para_id.get(id_val,"RFU")+" ("+raw[p_payload:(p_payload+2*1)]+")")
		p_payload = p_payload + 2*1

		data_len = raw[p_payload:(p_payload+2*1)]	
		x = int(data_len,16)
		print("- Length:", x, "("+data_len+")")
		p_payload = p_payload + 2*1
		
		data_val = raw[p_payload:(p_payload+2*x)]	
		print("- Value: "+data_val)
		if(id_val == "00"):	# Table 91
			para_val = data_val[0:2]
			if((int(para_val,16) >= 112) & (int(para_val,16) <= 127)):
				para_val = '70-7F'
			elif((int(para_val,16) >= 240) & (int(para_val,16) <= 255)):
				para_val = 'F0-FF'
			print("  -- RF Technology and Mode: "+NFC_table.tbl_rf_tech_mode.get(para_val,"RFU")+" ("+data_val[0:2]+")")
		elif((id_val == "01") | (id_val == "02")):
			para_val = data_val[0:2]
			if((int(para_val,16) >= 128) & (int(para_val,16) <= 254)):
				para_val = '80-FE'
			if(id_val == "01"):
				print("  -- Transmit Bit Rate: "+NFC_table.tbl_bit_rates.get(para_val,"RFU")+" ("+data_val[0:2]+")")
			elif(id_val == "02"):
				print("  -- Receive Bit Rate: "+NFC_table.tbl_bit_rates.get(para_val,"RFU")+" ("+data_val[0:2]+")")
		elif(id_val == "03"): # Table 92
			para_val = data_val[0:2]
			print("  -- NFC-B Data Exchange Configuration: "+para_val)
			data_ex_cfg_b = bin(int(para_val,16))[2::].zfill(8)
			print('{0:<25}'.format("  * Minimum TR0:"), end="")
			print('{0:>2}'.format(data_ex_cfg_b[0:2]))
			print('{0:<25}'.format("  * Minimum TR1:"), end="")
			print('{0:>2}'.format(data_ex_cfg_b[2:4]))
			print('{0:<25}'.format("  * Suppression of EoS:"), end="")
			print('{0:>2}'.format(data_ex_cfg_b[4:5]))
			print('{0:<25}'.format("  * Suppression of SoS:"), end="")
			print('{0:>2}'.format(data_ex_cfg_b[5:6]))
			print('{0:<25}'.format("  * Minimum TR3:"), end="")
			print('{0:>2}'.format(data_ex_cfg_b[6:8]))
		p_payload = p_payload + 2*x
		print("")
	print("")

# 41 0B
def RF_PARAMETER_UPDATE_RSP(raw):
	"""""""""""""""
		[RF_PARAMETER_UPDATE_RSP]
    Status:		1 Octet
	Number of Parameters:					1 Octet (n)
	RF Communication Parameters [1..n]:		1 Octets
	"""""""""""""""
	print("RF_PARAMETER_UPDATE_RSP")
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]	
	print("- Status: "+NFC_table.tbl_status_codes.get(status,"RFU")+" ("+status+")")
	p_payload = p_payload + 2*1
	
	num_para = raw[p_payload:(p_payload+2*1)]	
	n = int(num_para,16)
	print("- Number of Parameters:", n, "("+num_para+")")
	p_payload = p_payload + 2*1
	
	print("- RF Communication Parameter ID: ")
	for i in range(n):
		id_val = raw[p_payload:(p_payload+2*1)]
		if(int(id_val,16) >= 128):
			id_val = '80-FF'
		print("- Type ID "+str(i)+": "+NFC_table.tbl_rf_commu_para_id.get(id_val,"RFU")+" ("+raw[p_payload:(p_payload+2*1)]+")")
		p_payload = p_payload + 2*1
	print("")

# 21 0C
def RF_INTF_EXT_START_CMD(raw):
	"""""""""""""""
		[RF_INTF_EXT_START_CMD]
	RF Interface Extension:		1 Octet
	Start Parameter Length:		1 Octet (x)
	Start Parameter: 			x Octet(s)
	"""""""""""""""
	print("RF_INTF_EXT_START_CMD")
	p_payload = 0

	exten = raw[p_payload:(p_payload+2*1)]
	print("- RF Interface Extension: "+NFC_table.tbl_rf_if_exten.get(exten,"RFU")+" ("+exten+")")
	p_payload = p_payload + 2*1
	
	start_para_len = raw[p_payload:(p_payload+2*1)]
	x = int(start_para_len,16)
	print("- Start Parameter Length:", x, "("+start_para_len+")")
	p_payload = p_payload + 2*1

	start_para = raw[p_payload:(p_payload+2*x)]
	print("- Start Parameter Length: "+start_para)
	p_payload = p_payload + 2*x
	print("")

# 41 0C
def RF_INTF_EXT_START_RSP(raw):
	"""""""""""""""
		[RF_INTF_EXT_START_RSP]
    Status:		1 Octet
	"""""""""""""""
	print("RF_INTF_EXT_START_RSP")
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]	
	print("- Status: "+NFC_table.tbl_status_codes.get(status,"RFU")+" ("+status+")")
	p_payload = p_payload + 2*1
	print("")

# 21 0D
def RF_INTF_EXT_STOP_CMD(raw):
	print("RF_INTF_EXT_STOP_CMD")
	p_payload = 0

	exten = raw[p_payload:(p_payload+2*1)]
	print("- RF Interface Extension: "+NFC_table.tbl_rf_if_exten.get(exten,"RFU")+" ("+exten+")")
	p_payload = p_payload + 2*1
	
	start_para_len = raw[p_payload:(p_payload+2*1)]
	x = int(start_para_len,16)
	print("- Start Parameter Length:", x, "("+start_para_len+")")
	p_payload = p_payload + 2*1

	start_para = raw[p_payload:(p_payload+2*x)]
	print("- Start Parameter Length: "+start_para)
	p_payload = p_payload + 2*x
	print("")

# 41 0D
def RF_INTF_EXT_STOP_RSP(raw):
	"""""""""""""""
		[RF_INTF_EXT_STOP_RSP]
    Status:		1 Octet
	"""""""""""""""
	print("RF_INTF_EXT_STOP_RSP")
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]	
	print("- Status: "+NFC_table.tbl_status_codes.get(status,"RFU")+" ("+status+")")
	p_payload = p_payload + 2*1
	print("")

# 21 0E
def RF_EXT_AGG_ABORT_CMD(raw):
	"""""""""""""""
		[RF_EXT_AGG_ABORT_CMD]
    (Empty)
	"""""""""""""""
	print("RF_EXT_AGG_ABORT_CMD")
	print("(Empty)")
	print("")

# 41 0E
def RF_EXT_AGG_ABORT_RSP(raw):
	"""""""""""""""
		[RF_EXT_AGG_ABORT_RSP]
    Status:		1 Octet
	"""""""""""""""
	print("RF_EXT_AGG_ABORT_RSP")
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]	
	print("- Status: "+NFC_table.tbl_status_codes.get(status,"RFU")+" ("+status+")")
	p_payload = p_payload + 2*1
	print("")

# 21 0F
def RF_NDEF_ABORT_CMD(raw):
	"""""""""""""""
		[RF_NDEF_ABORT_CMD]
    (Empty)
	"""""""""""""""
	print("RF_NDEF_ABORT_CMD")
	print("(Empty)")
	print("")
	
# 41 0F
def RF_NDEF_ABORT_RSP(raw):
	"""""""""""""""
		[RF_NDEF_ABORT_RSP]
    Status:		1 Octet
	"""""""""""""""
	print("RF_NDEF_ABORT_RSP")
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]	
	print("- Status: "+NFC_table.tbl_status_codes.get(status,"RFU")+" ("+status+")")
	p_payload = p_payload + 2*1
	print("")

# 21 10
def RF_ISO_DEP_NAK_PRESENCE_CMD(raw):
	"""""""""""""""
		[RF_ISO_DEP_NAK_PRESENCE_CMD]
    (Empty)
	"""""""""""""""
	print("RF_ISO_DEP_NAK_PRESENCE_CMD")
	print("(Empty)")
	print("")

# 41 10
def RF_ISO_DEP_NAK_PRESENCE_RSP(raw):
	"""""""""""""""
		[RF_ISO_DEP_NAK_PRESENCE_RSP]
    Status:		1 Octet
	"""""""""""""""
	print("RF_ISO_DEP_NAK_PRESENCE_RSP")
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]	
	print("- Status: "+NFC_table.tbl_status_codes.get(status,"RFU")+" ("+status+")")
	p_payload = p_payload + 2*1
	print("")
	
# 61 10
def RF_ISO_DEP_NAK_PRESENCE_NTF(raw):
	"""""""""""""""
		[RF_ISO_DEP_NAK_PRESENCE_NTF]
    Status:		1 Octet
	"""""""""""""""
	print("RF_ISO_DEP_NAK_PRESENCE_NTF")
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]	
	print("- Status: "+NFC_table.tbl_status_codes.get(status,"RFU")+" ("+status+")")
	p_payload = p_payload + 2*1
	print("")
	
# 21 11
def RF_SET_FORCED_NFCEE_ROUTING_CMD(raw):
	"""""""""""""""
		[RF_SET_FORCED_NFCEE_ROUTING_CMD]
    Forced NFCEE Routing State:		1 Octet
	Forced NFCEE Value Field:		0 or 2 Octet(s)
	﹂	Forced NFCEE				﹂	1 Octet
	﹂	Forced Power State			﹂	1 Octet
	"""""""""""""""
	print("RF_SET_FORCED_NFCEE_ROUTING_CMD")
	p_payload = 0

	forced_nfcee_rout_state = raw[p_payload:(p_payload+2*1)]
	p_payload = p_payload + 2*1
	if(forced_nfcee_rout_state == "00"):
		print("- Forced NFCEE Routing State: "+"Disabled"+" ("+forced_nfcee_rout_state+")")

	elif(forced_nfcee_rout_state == "01"):
		print("- Forced NFCEE Routing State: "+"Enabled"+" ("+forced_nfcee_rout_state+")")
		forced_nfcee = raw[p_payload:(p_payload+2*1)]
		route_val = forced_nfcee
		if((int(forced_nfcee,16) >= 2) & (int(forced_nfcee,16) <= 15)):
			route_val = '02-0F'
		elif((int(forced_nfcee,16) >= 16) & (int(forced_nfcee,16) <= 127)):
			route_val = '10-7F'
		elif((int(forced_nfcee,16) >= 128) & (int(forced_nfcee,16) <= 254)):
			route_val = '80-FE'
		print("- Forced NFCEE: "+NFC_table.tbl_nfcee_id.get(route_val,"RFU")+" ("+forced_nfcee+")")
		p_payload = p_payload + 2*1

		forced_pwr_state = raw[p_payload:(p_payload+2*1)]
		pwr_state_b = bin(int(forced_pwr_state,16))[2::].zfill(8)
		print("  -- Power State: "+pwr_state_b+" ("+forced_pwr_state+")")
		for j in range (5,-1,-1):
			print('{0:<33}'.format("   * "+NFC_table.tbl_pwr_state.get(j,"RFU")+":"), end="")
			if(pwr_state_b[7-j:8-j] == "1"):
				print('{0:<10}'.format("Apply"))
			else:
				print('{0:<10}'.format("Not apply"))
		val_payload = val_payload + 2*1

	else:
		print("- Forced NFCEE Routing State: "+"Error"+" ("+forced_nfcee_rout_state+")")
	print("")
	
# 41 11
def RF_SET_FORCED_NFCEE_ROUTING_RSP(raw):
	"""""""""""""""
		[RF_SET_FORCED_NFCEE_ROUTING_RSP]
    Status:		1 Octet
	"""""""""""""""
	print("RF_SET_FORCED_NFCEE_ROUTING_RSP")
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]	
	print("- Status: "+NFC_table.tbl_status_codes.get(status,"RFU")+" ("+status+")")
	p_payload = p_payload + 2*1
	print("")