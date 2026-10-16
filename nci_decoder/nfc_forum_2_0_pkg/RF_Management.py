# import nfc_forum_pkg.__table__ as NFC_table
import __pkg_import__ as pkg_import
import range_lookup
from range_lookup import lookup


class _ShortField(Exception):
	"""A field inside a length-bounded structure runs past its declared length."""
	pass


class _SubRaw:
	"""Cursor over a length-bounded structure (hex string, hex-char offsets).

	Reads never go past the declared length: a too-short field raises
	_ShortField instead of silently yielding '' (mirrors the JS sub-reader).
	"""
	def __init__(self, raw):
		self.raw = raw
		self.p = 0

	def remaining(self):
		return (len(self.raw) - self.p) // 2

	def read(self, n, what):
		if (n < 0) or (self.remaining() < n):
			raise _ShortField("Payload too short: need "+str(n)+" byte(s) for "+what+", "+str(max(self.remaining(), 0))+" left")
		val = self.raw[self.p:(self.p+2*n)]
		self.p = self.p + 2*n
		return val


def _with_sub(sub_raw, what, fn):
	"""Run fn(_SubRaw(sub_raw)); a too-short inner field prints an error line
	and decoding continues after the declared length."""
	try:
		fn(_SubRaw(sub_raw))
	except _ShortField as e:
		print("  * Error: "+what+": "+str(e))

# 21 00
def RF_DISCOVER_MAP_CMD(raw, vendor="None", model="None"):
	"""""""""""""""
		[RF_DISCOVER_MAP_CMD]
	Number of Mapping Configurations:	1 Octet (n)
	Mapping Configuration [1..n]: 		3 Octets
	﹂	RF Protocol:					﹂	1 Octet
	﹂	Mode: 							﹂	1 Octet
	﹂	RF Interface: 					﹂	1 Octet
	"""""""""""""""
	# print("RF_DISCOVER_MAP_CMD")
	NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0
	
	num_of_cfg = raw[p_payload:(p_payload+2*1)]
	n = int(num_of_cfg, 16)
	print("  * Number of Mapping Configs:", n, "("+num_of_cfg+")")
	p_payload = p_payload + 2*1
	
	# print("  * Mapping Configuration: ")
	for i in range(n):
		print()
		print("   ~ [Mapping Cfg_"+str(i)+"] ~  ")
		rf_proto = raw[p_payload:(p_payload+2*1)]
		print("    * RF Protocol: "+lookup(NFC_table.tbl_rf_proto, rf_proto), "("+rf_proto+")")
		p_payload = p_payload + 2*1

		mode = raw[p_payload:(p_payload+2*1)]	
		print("    * Mode: "+lookup(NFC_table.tbl_mode, mode), "("+mode+")")
		p_payload = p_payload + 2*1

		rf_if = raw[p_payload:(p_payload+2*1)]	
		print("    * RF Interface: "+lookup(NFC_table.tbl_rf_if, rf_if), "("+rf_if+")")
		p_payload = p_payload + 2*1		
		
		# if(i < n-1):
		# 	print("")
	# print("#end")
	return p_payload

# 41 00
def RF_DISCOVER_MAP_RSP(raw, vendor="None", model="None"):
	"""""""""""""""
		[RF_DISCOVER_MAP_RSP]
    Status: 1 Octet
	"""""""""""""""
	# print("RF_DISCOVER_MAP_RSP")
	NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]	
	print("  * Status: "+lookup(NFC_table.tbl_status_codes, status), "("+status+")")
	p_payload = p_payload + 2*1
	# print("")
	return p_payload

def LISTEN_MODE_ROUTING_INFO(raw, vendor, model):
	"""""""""""""""
		共用
		[RF_SET_LISTEN_MODE_ROUTING_CMD]
		[RF_GET_LISTEN_MODE_ROUTING_NTF]
	More:						1 Octet
	Number of Routing Entries:	1 Octet (n)
	Routing Entry [1..n]: 		x+2 Octets
	﹂	Qualifier-Type:			﹂	1 Octet
	﹂	Length: 				﹂	1 Octet (x)
	﹂	Value: 					﹂	x Octet
	"""""""""""""""
	NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0

	more = raw[p_payload:(p_payload+2*1)]	
	print("  * More: "+lookup(NFC_table.tbl_more, more), "("+more+")")
	p_payload = p_payload + 2*1
	
	num_of_router = raw[p_payload:(p_payload+2*1)]
	n = int(num_of_router, 16)
	print("  * Number of Routing Entries:", n, "("+num_of_router+")")
	p_payload = p_payload + 2*1	
	
	# print("  * Routing Entry:")
	for i in range(n):
		print()
		print("   ~ [Routing Entry_"+str(i)+"] ~  ")
		q_type = raw[p_payload:(p_payload+2*1)]	
		print("    * Type: "+lookup(NFC_table.tbl_L_mode_routing_entry_type, q_type[1:2]), "("+q_type+")")
		q_type_b = bin(int(q_type[0:1],16))[2::].zfill(4) # ref to Table 52
		if (q_type_b[1:2] == "1"):
			print("     ~ Routing is blocked for the power modes where it is not supported.")
		if (q_type_b[2:3] == "1"):
			print("     ~ Match is allowed when the SELECT AID is shorter than the AID in this routing table entry.")
		if (q_type_b[3:4] == "1"):
			print("     ~ Match is allowed when the SELECT AID is longer than the AID in this routing table entry.")
		p_payload = p_payload + 2*1

		len = raw[p_payload:(p_payload+2*1)]	
		x = int(len, 16)
		print("    * Len:", x)
		p_payload = p_payload + 2*1

		val_raw = raw[p_payload:(p_payload+2*x)]
		p_payload = p_payload + 2*x

		print("    * Val: "+val_raw)
		def routing_value(v):
			route_val = v.read(1, "Route")
			route_val_range = range_lookup.find_range_key(NFC_table.tbl_nfcee_id, int(route_val, 16))
			print("      * Route:", NFC_table.tbl_nfcee_id.get(route_val, route_val), NFC_table.tbl_nfcee_id.get(route_val_range, ""), "("+route_val+")")

			pwr_state = v.read(1, "Power State")
			pwr_state_b = bin(int(pwr_state,16))[2::].zfill(8)
			print("      * Power State: "+pwr_state_b+" ("+pwr_state+")")
			for j in range (5,-1,-1):
				print('{0:<43}'.format("       ~ "+NFC_table.tbl_pwr_state.get(j,"RFU")+":"), end="")
				if(pwr_state_b[7-j:8-j] == "1"):
					print('{0:>10}'.format("Apply"))
				else:
					print('{0:>10}'.format("Not apply"))

			if (q_type[1:2] == "0"):
				"""""""""""""""
					[Table 54: Value Field for Technology-based Routing]
				Technology:		1 Octet
				"""""""""""""""
				tech = v.read(1, "Technology")
				print("      * Technology: "+lookup(NFC_table.tbl_rf_tech, tech), "("+tech+")")

			elif (q_type[1:2] == "1"):
				"""""""""""""""
					[Table 55: Value Field for Protocol-based Routing]
				Protocol:		1 Octet
				"""""""""""""""
				proto = v.read(1, "Protocol")
				print("      * Protocol: "+lookup(NFC_table.tbl_rf_proto, proto), "("+proto+")")

			elif (q_type[1:2] == "2"):
				"""""""""""""""
					[Table 56: Value Field for AID-based Routing]
				AID:		    0-16 Octets
				"""""""""""""""
				if(v.remaining() > 0):
					print("      * AID: "+v.read(v.remaining(), "AID"))

			elif (q_type[1:2] == "3"):
				"""""""""""""""
					[Table 57: Value Field for System Code-based Routing]
				SC Route List:  2n Octets
				"""""""""""""""
				route_num = (x-2)//2
				for j in range(route_num):
					print("      * SC Route "+str(j)+": "+v.read(2, "SC Route"))

			elif (q_type[1:2] == "4"):
				"""""""""""""""
					[Table 58: Value Field for APDU Pattern-based Routing]
				Reference data:	n Octet(s)
				Mask:       	n Octet(s)
				"""""""""""""""
				data_len = (x-2)//2
				print("      * Reference data: "+v.read(data_len, "Reference data"))
				print("      * Mask: "+v.read(data_len, "Mask"))
		_with_sub(val_raw, "Routing Entry Value", routing_value)
		
		# if(i < n-1):
		# 	print("")
	return p_payload

# 21 01
def RF_SET_LISTEN_MODE_ROUTING_CMD(raw, vendor="None", model="None"):
	# print("RF_SET_LISTEN_MODE_ROUTING_CMD")
	p_payload = LISTEN_MODE_ROUTING_INFO(raw, vendor, model)
	# print("#end")
	return p_payload

# 41 01
def RF_SET_LISTEN_MODE_ROUTING_RSP(raw, vendor="None", model="None"):
	"""""""""""""""
		[RF_SET_LISTEN_MODE_ROUTING_RSP]
    Status: 1 Octet
	"""""""""""""""
	# print("RF_SET_LISTEN_MODE_ROUTING_RSP")
	NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]
	print("  * Status: "+lookup(NFC_table.tbl_status_codes, status), "("+status+")")
	p_payload = p_payload + 2*1
	# print("")
	return p_payload

# 21 02
def RF_GET_LISTEN_MODE_ROUTING_CMD(raw, vendor="None", model="None"):
	"""""""""""""""
		[RF_GET_LISTEN_MODE_ROUTING_CMD]
    (Empty)
	"""""""""""""""
	# print("RF_GET_LISTEN_MODE_ROUTING_CMD")
	NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0
	print('{0:^25}'.format("(Empty)"))
	# print("")
	return p_payload

# 41 02
def RF_GET_LISTEN_MODE_ROUTING_RSP(raw, vendor="None", model="None"):
	"""""""""""""""
		[RF_SET_LISTEN_MODE_ROUTING_RSP]
    Status: 1 Octet
	"""""""""""""""
	# print("RF_GET_LISTEN_MODE_ROUTING_RSP")
	NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]
	print("  * Status: "+lookup(NFC_table.tbl_status_codes, status), "("+status+")")
	p_payload = p_payload + 2*1
	# print("")
	return p_payload

# 61 02
def RF_GET_LISTEN_MODE_ROUTING_NTF(raw, vendor="None", model="None"):
	# print("RF_GET_LISTEN_MODE_ROUTING_NTF")
	p_payload = LISTEN_MODE_ROUTING_INFO(raw, vendor, model)
	# print("#end")
	return p_payload

# 21 03
def RF_DISCOVER_CMD(raw, vendor="None", model="None"):
	"""""""""""""""
		[RF_DISCOVER_CMD]
	Number of Configurations:		1 Octet (n)
	Configuration [0..n]: 			2 Octets
	﹂	RF Technology and Mode:		﹂	1 Octet
	﹂	Discovery Frequency: 		﹂	1 Octet
	"""""""""""""""
	# print("RF_DISCOVER_CMD")
	NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0

	num_cfg = raw[p_payload:(p_payload+2*1)]
	n = int(num_cfg, 16)
	print("  * Number of Configs:", n, "("+num_cfg+")")
	p_payload = p_payload + 2*1
	
	for i in range(n):
		print()
		print("   ~ [Config_"+str(i)+"] ~  ")
		rf_tech_mode = raw[p_payload:(p_payload+2*1)]
		print("    * Mode: "+lookup(NFC_table.tbl_rf_tech_mode, rf_tech_mode), "("+rf_tech_mode+")")
		p_payload = p_payload + 2*1

		discovery_freq = raw[p_payload:(p_payload+2*1)]	
		freq = int(discovery_freq, 16)
		if((freq == 0) | (freq > 10)):
			print("    * Discovery Freq: "+"RFU")		
		else:
			print("    * Discovery Freq:", freq)
		p_payload = p_payload + 2*1
		
		# if(i < n-1):
		# 	print("")
	# # print("")
	# print("  Note:Discovery Frequency: ")
	# print("  *-- 00/0B-FF: RFU")
	# print("  *-- 01: RF Technology and Mode will be executed in every discovery period")
	# print("  *-- 02-0A: These values are allowed for Poll Mode RF Technology and Mode values.")
	# print("  *--        This value specifies how often the Poll period of the specific RF Technology will be executed.")
	# print("  *--        For example, a value of 10 indicates that this Polling will be executed in every 10th discovery period.")
	# print("#end")
	return p_payload

# 41 03
def RF_DISCOVER_RSP(raw, vendor="None", model="None"):
	"""""""""""""""
		[RF_DISCOVER_RSP]
    Status: 1 Octet
	"""""""""""""""
	# print("RF_DISCOVER_RSP")
	NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]	
	print("  * Status: "+lookup(NFC_table.tbl_status_codes, status), "("+status+")")
	p_payload = p_payload + 2*1
	# print("")
	return p_payload

def RF_TECH_SPEC_PARA(rf_tech_mode, p, NFC_table):
	"""""""""""""""
		部分共用
		[RF_DISCOVER_NTF]
		[RF_INTF_ACTIVATED_NTF]
	p: _SubRaw over exactly the declared RF Technology Specific Parameters.
	Branches on the RF Technology and Mode hex code (not the table string:
	NXP's tbl_rf_tech_mode says e.g. "ACTIVE_POLL ( Not supported )").
	"""""""""""""""
	def len_field(label):
		val = p.read(1, label)
		l = int(val,16)
		print("  * "+label+":", l)
		return l

	def hex_field(label, n):
		print("  * "+label+": "+p.read(n, label))

	rf_tech_mode = rf_tech_mode.upper()
	if(rf_tech_mode == "00"):
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
		hex_field("SENS_RES Response", 2)
		hex_field("NFCID1", len_field("NFCID1 Len"))
		hex_field("SEL_RES Rsp", len_field("SEL_RES Rsp Len"))
		l = len_field("HRx Len")
		if(l != 0):
			hex_field("HRx", l)

	elif(rf_tech_mode == "80"):
		"""""""""""""""
			[Table 69: Specific Parameters for NFC-A Listen Mode]
		(Empty)
		"""""""""""""""
		print("  * There is no RF Technology Specific Parameters")

	elif(rf_tech_mode == "01"):
		"""""""""""""""
			[Table 70: Specific Parameters for NFC-B Poll Mode]
		SENSB_RES Response Length: 			1 Octet
		SENSB_RES Response: 				11 or 12 Octets
		"""""""""""""""
		hex_field("SENSB_RES Rsp", len_field("SENSB_RES Rsp Len"))

	elif(rf_tech_mode == "81"):
		"""""""""""""""
			[Table 71: Specific Parameters for NFC-B Listen Mode]
		SENSB_REQ Command:		1 Octet
		"""""""""""""""
		hex_field("SENSB_REQ Command", 1)

	elif(rf_tech_mode == "02"):
		"""""""""""""""
			[Table 72: Specific Parameters for NFC-F Poll Mode]
		Bit Rate: 					1 Octet
		SENSF_RES Response Length: 	1 Octet
		SENSF_RES Response:			16 or 18 Octets
		"""""""""""""""
		bitrate = p.read(1, "Bit Rate")
		if(bitrate == "01"):
			print("  * Bit Rate: 212 kbps")
		elif(bitrate == "02"):
			print("  * Bit Rate: 424 kbps")
		else:
			print("  * Bit Rate: RFU ("+bitrate+")")
		hex_field("SENSF_RES Rsp", len_field("SENSF_RES Rsp Len"))

	elif(rf_tech_mode == "82"):
		"""""""""""""""
			[Table 73: Specific Parameters for NFC-F Listen Mode]
		Local NFCID2 Length: 	1 Octet
		Local NFCID2:			0 or 8 Octet(s)
		"""""""""""""""
		hex_field("Local NFCID2", len_field("Local NFCID2 Len"))

	elif(rf_tech_mode == "06"):
		"""""""""""""""
			[Table 74: Specific Parameters for NFC-V Poll Mode]
		RES_FLAG: 	1 Octet
		DSFID: 		1 Octet
		UID:		8 Octets
		"""""""""""""""
		hex_field("RES_FLAG", 1)
		hex_field("DSFID", 1)
		hex_field("UID", 8)

	elif(rf_tech_mode == "03"):
		"""""""""""""""
			[Table 75: Specific Parameters for NFC-ACM Poll Mode]
		ATR_RES Response Length: 	1 Octet (n)
		ATR_RES Response: 			n Octet(s)
		"""""""""""""""
		hex_field("ATR_RES Rsp", len_field("ATR_RES Rsp Len"))

	elif(rf_tech_mode == "83"):
		"""""""""""""""
			[Table 76: Specific Parameters for NFC-ACM Listen Mode]
		ATR_REQ Command Length: 	1 Octet (n)
		ATR_REQ Command: 			n Octet(s)
		"""""""""""""""
		hex_field("ATR_REQ Cmd", len_field("ATR_REQ Cmd Len"))

	else:
		print("  * Proprietary parameters: "+p.read(p.remaining(), "Proprietary parameters"))

def ACTIVATION_PARA(rf_if, rf_tech_mode, a, NFC_table):
	"""""""""""""""
		[RF_INTF_ACTIVATED_NTF] Activation Parameters (Tables 95-103)
	a: _SubRaw over exactly the declared Activation Parameters (n octets);
	nothing is read when n = 0. Branches on the RF Interface and the
	Activation RF Technology and Mode hex codes.
	"""""""""""""""
	def raw_params():
		if(a.remaining() > 0):
			print("  * Activation Params: "+a.read(a.remaining(), "Activation Params"))

	def len_field(label, with_hex=False):
		val = a.read(1, label)
		l = int(val,16)
		if(with_hex):
			print("  * "+label+":", l, "("+val+")")
		else:
			print("  * "+label+":", l)
		return l

	def hex_field(label, n):
		print("  * "+label+": "+a.read(n, label))

	if(a.remaining() == 0):
		return
	rf_if = rf_if.upper()
	rf_tech_mode = rf_tech_mode.upper()
	if(rf_if == "02"): # ISO-DEP
		if(rf_tech_mode == "00"): # Table 95
			hex_field("RATS Rsp", len_field("RATS Rsp Len", True))
		elif(rf_tech_mode == "01"): # Table 96
			hex_field("ATTRIB Rsp", len_field("ATTRIB Rsp Len", True))
		elif(rf_tech_mode == "80"): # Table 98
			hex_field("RATS Cmd Param", 1)
		elif(rf_tech_mode == "81"): # Table 99
			hex_field("ATTRIB Cmd", len_field("ATTRIB Cmd Len"))
		else:
			raw_params()
			return

	elif(rf_if == "03"): # NFC-DEP
		if((rf_tech_mode == "00") | (rf_tech_mode == "02")): # Table 102
			hex_field("ATR_RES Rsp", len_field("ATR_RES Rsp Len"))
			len_rdu_val = a.read(1, "Data Exchange LR")
			print("  * Data Exchange LR: "+lookup(NFC_table.tbl_len_rdu_val, len_rdu_val), "("+len_rdu_val+")")
		elif((rf_tech_mode == "80") | (rf_tech_mode == "82")): # Table 103
			hex_field("ATR_REQ Cmd", len_field("ATR_REQ Cmd Len"))
			len_rdu_val = a.read(1, "Data Exchange LR")
			print("  * Data Exchange LR: "+lookup(NFC_table.tbl_len_rdu_val, len_rdu_val), "("+len_rdu_val+")")
		else:
			raw_params()
			return

	else:
		raw_params()
		return

	if(a.remaining() > 0):
		print("  * Remaining Activation Params: "+a.read(a.remaining(), "Activation Params"))

# 61 03
def RF_DISCOVER_NTF(raw, vendor="None", model="None"):
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
	NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0
	
	rf_dis_id = raw[p_payload:(p_payload+2*1)]	
	print("  * RF Discovery ID:", NFC_table.tbl_rf_dis_id.get(rf_dis_id, rf_dis_id))
	p_payload = p_payload + 2*1
	
	rf_proto = raw[p_payload:(p_payload+2*1)]
	print("  * RF Protocol: "+lookup(NFC_table.tbl_rf_proto, rf_proto), "("+rf_proto+")")
	p_payload = p_payload + 2*1
	
	rf_tech_mode = raw[p_payload:(p_payload+2*1)]
	print("  * Mode: "+lookup(NFC_table.tbl_rf_tech_mode, rf_tech_mode), "("+rf_tech_mode+")")
	p_payload = p_payload + 2*1

	rf_tech_len = raw[p_payload:(p_payload+2*1)]
	n = int(rf_tech_len,16)
	print("  * Len of RF Tech Specific Params:", n)
	p_payload = p_payload + 2*1
	
	para_raw = raw[p_payload:(p_payload+2*n)]
	_with_sub(para_raw, "RF Technology Specific Parameters", lambda p: RF_TECH_SPEC_PARA(rf_tech_mode, p, NFC_table))
	p_payload = p_payload + 2*n
	
	notificaiton_type = raw[p_payload:(p_payload+2*1)]	
	if(notificaiton_type == "00"):
		print("  * NTF Type: Last NTF (00)")
	elif(notificaiton_type == "01"):
		print("  * NTF Type: Last NTF (due to NFCC reaching its resource limit) (01)")
	elif(notificaiton_type == "02"):
		print("  * NTF Type: More NTF to follow (02)")
	else:
		print("  * NTF Type: RFU ("+notificaiton_type+")")	
	p_payload = p_payload + 2*1
	# print("")
	return p_payload

# 21 04
def RF_DISCOVER_SELECT_CMD(raw, vendor="None", model="None"):
	"""""""""""""""
		[RF_DISCOVER_SELECT_CMD]
    RF Discovery ID:	1 Octet
    RF Protocol: 		1 Octet
    RF Interface:		1 Octet
	"""""""""""""""
	# print("RF_DISCOVER_SELECT_CMD")
	NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0
	
	rf_dis_id = raw[p_payload:(p_payload+2*1)]	
	print("  * RF Discovery ID:", NFC_table.tbl_rf_dis_id.get(rf_dis_id, rf_dis_id))
	p_payload = p_payload + 2*1

	rf_proto = raw[p_payload:(p_payload+2*1)]
	print("  * RF Protocol: "+lookup(NFC_table.tbl_rf_proto, rf_proto), "("+rf_proto+")")
	p_payload = p_payload + 2*1
	
	rf_if = raw[p_payload:(p_payload+2*1)]
	print("  * RF Interface: "+lookup(NFC_table.tbl_rf_if, rf_if), "("+rf_if+")")
	p_payload = p_payload + 2*1
	# print("")	
	return p_payload

# 41 04
def RF_DISCOVER_SELECT_RSP(raw, vendor="None", model="None"):
	"""""""""""""""
		[RF_DISCOVER_SELECT_RSP]
    Status:		1 Octet
	"""""""""""""""
	# print("RF_DISCOVER_SELECT_RSP")
	NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0
	
	status=raw[p_payload:(p_payload+2*1)]	
	print("  * Status: "+lookup(NFC_table.tbl_status_codes, status), "("+status+")")
	p_payload = p_payload + 2*1
	# print("")
	return p_payload
		
# 61 05
def RF_INTF_ACTIVATED_NTF(raw, vendor="None", model="None"):
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
	NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0
	
	rf_dis_id = raw[p_payload:(p_payload+2*1)]	
	print("  * RF Discovery ID:", NFC_table.tbl_rf_dis_id.get(rf_dis_id, rf_dis_id))
	p_payload = p_payload + 2*1
	
	rf_if = raw[p_payload:(p_payload+2*1)]	
	print("  * RF Interface: "+lookup(NFC_table.tbl_rf_if, rf_if), "("+rf_if+")")
	p_payload = p_payload + 2*1
	
	rf_proto = raw[p_payload:(p_payload+2*1)]
	print("  * RF Protocol: "+lookup(NFC_table.tbl_rf_proto, rf_proto), "("+rf_proto+")")
	p_payload = p_payload + 2*1
	activ_rf_tech_mode=raw[p_payload:(p_payload+2*1)]
	print("  * Activation Mode: "+lookup(NFC_table.tbl_rf_tech_mode, activ_rf_tech_mode), "("+activ_rf_tech_mode+")")
	p_payload = p_payload + 2*1
	
	max_data_size=raw[p_payload:(p_payload+2*1)]
	size = int(max_data_size,16)
	print("  * Max Data Size:", size, "("+max_data_size+")")
	p_payload = p_payload + 2*1

	num_credits = raw[p_payload:(p_payload+2*1)]
	if(num_credits == "FF"):
		print("  * Number of Credits: "+"Not used"+" ("+num_credits+")")
	else:
		print("  * Number of Credits:", int(num_credits,16))
	p_payload = p_payload + 2*1
	
	len_rf_tech_para = raw[p_payload:(p_payload+2*1)]
	l = int(len_rf_tech_para,16)
	print("  * Len of RF Tech Specific Params:", l)
	p_payload = p_payload + 2*1

	if(l != 0):
		para_raw = raw[p_payload:(p_payload+2*l)]
		_with_sub(para_raw, "RF Technology Specific Parameters", lambda p: RF_TECH_SPEC_PARA(activ_rf_tech_mode, p, NFC_table))
		p_payload = p_payload + 2*l
		
	data_ex_rf_tech_mode = raw[p_payload:(p_payload+2*1)]
	print("  * Data Mode: "+lookup(NFC_table.tbl_rf_tech_mode, data_ex_rf_tech_mode), "("+data_ex_rf_tech_mode+")")
	p_payload = p_payload + 2*1

	data_ex_tx_bitrate = raw[p_payload:(p_payload+2*1)]	
	print("  * Tx: "+lookup(NFC_table.tbl_bit_rates, data_ex_tx_bitrate), "("+data_ex_tx_bitrate+")")
	p_payload = p_payload + 2*1

	data_ex_rx_bitrate=raw[p_payload:(p_payload+2*1)]
	print("  * Rx: "+lookup(NFC_table.tbl_bit_rates, data_ex_rx_bitrate), "("+data_ex_rx_bitrate+")")
	p_payload = p_payload + 2*1
	
	len_activate_para = raw[p_payload:(p_payload+2*1)]
	n = int(len_activate_para,16)
	print("  * Len of Activation Params:", n)
	p_payload = p_payload + 2*1
	
	activate_para = raw[p_payload:(p_payload+2*n)]
	_with_sub(activate_para, "Activation Parameters", lambda a: ACTIVATION_PARA(rf_if, activ_rf_tech_mode, a, NFC_table))
	p_payload = p_payload + 2*n
	# print("")	
	return p_payload

# 21 06
def RF_DEACTIVATE_CMD(raw, vendor="None", model="None"):
	"""""""""""""""
		[RF_DEACTIVATE_CMD]
    Deactivation Type:		1 Octet
	"""""""""""""""
	# print("RF_DEACTIVATE_CMD")
	NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0
	
	deactivate_type = raw[p_payload:(p_payload+2*1)]	
	print("  * Deactivation Type: "+lookup(NFC_table.tbl_deactivate_type, deactivate_type), "("+deactivate_type+")")
	p_payload = p_payload + 2*1
	# print("")	
	return p_payload
	
# 41 06
def RF_DEACTIVATE_RSP(raw, vendor="None", model="None"):
	"""""""""""""""
		[RF_DEACTIVATE_RSP]
    Status:		1 Octet
	"""""""""""""""
	# print("RF_DEACTIVATE_RSP")
	NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]	
	print("  * Status: "+lookup(NFC_table.tbl_status_codes, status), "("+status+")")
	p_payload = p_payload + 2*1
	# print("")
	return p_payload

# 61 06
def RF_DEACTIVATE_NTF(raw, vendor="None", model="None"):
	"""""""""""""""
		[RF_DEACTIVATE_NTF]
    Deactivation Type:		1 Octet
    Deactivation Reason:	1 Octet
	"""""""""""""""
	# print("RF_DEACTIVATE_NTF")
	NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0
	
	deactivate_type = raw[p_payload:(p_payload+2*1)]	
	print("  * Deactivation Type: "+lookup(NFC_table.tbl_deactivate_type, deactivate_type), "("+deactivate_type+")")
	p_payload = p_payload + 2*1

	deactivate_reason = raw[p_payload:(p_payload+2*1)]	
	print("  * Deactivation Reason: "+lookup(NFC_table.tbl_deactivate_reason, deactivate_reason), "("+deactivate_reason+")")
	p_payload = p_payload + 2*1
	# print("")	
	return p_payload
	
# 61 07
def RF_FIELD_INFO_NTF(raw, vendor="None", model="None"):
	"""""""""""""""
		[RF_FIELD_INFO_NTF]
    RF Field Status:		1 Octet
	"""""""""""""""
	# print("RF_FIELD_INFO_NTF")
	NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0
	
	rf_field_status = raw[p_payload:(p_payload+2*1)]
	if((rf_field_status in NFC_table.tbl_rf_field_status) & (rf_field_status != "name")):
		print("  * RF Field Status: "+NFC_table.tbl_rf_field_status[rf_field_status])
	else:
		print("  * RF Field Status: RFU ("+rf_field_status+")")
	p_payload = p_payload + 2*1
	# print("")	
	return p_payload
	
# 21 08
def RF_T3T_POLLING_CMD(raw, vendor="None", model="None"):
	"""""""""""""""
		[RF_T3T_POLLING_CMD]
    SENSF_REQ_PARAMS:		4 Octets
	"""""""""""""""
	# print("RF_T3T_POLLING_CMD")
	NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0
	
	sensf_req = raw[p_payload:(p_payload+2*4)]	
	print("  * SENSF_REQ_PARAMS: "+sensf_req)
	p_payload = p_payload + 2*4
	# print("")	
	return p_payload

# 41 08
def RF_T3T_POLLING_RSP(raw, vendor="None", model="None"):
	"""""""""""""""
		[RF_T3T_POLLING_RSP]
    Status:		1 Octet
	"""""""""""""""
	# print("RF_T3T_POLLING_RSP")
	NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]	
	print("  * Status: "+lookup(NFC_table.tbl_status_codes, status), "("+status+")")
	p_payload = p_payload + 2*1
	# print("")
	return p_payload

# 61 08
def RF_T3T_POLLING_NTF(raw, vendor="None", model="None"):
	"""""""""""""""
		[RF_T3T_POLLING_RSP]
    Status:					1 Octet
	Number of Responses:	1 Octet (n)
	Responses [1..n]:		m+1 Octets
	﹂	Length:				﹂	1 Octet (m)
	﹂	SENSF_RES: 			﹂	m Octet(s)
	"""""""""""""""
	# print("RF_T3T_POLLING_NTF")
	NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]	
	print("  * Status: "+lookup(NFC_table.tbl_status_codes, status), "("+status+")")
	p_payload = p_payload + 2*1
	
	num_rsp = raw[p_payload:(p_payload+2*1)]	
	n = int(num_rsp,16)
	print("  * Number of Rsp:", n, "("+num_rsp+")")
	p_payload = p_payload + 2*1
	
	for i in range(n):
		print()
		print("   ~ [Rsp_"+str(i)+"] ~  ")
		len_sensf_res = raw[p_payload:(p_payload+2*1)]
		l = int(len_sensf_res,16)
		print("    * Len:", l, "("+len_sensf_res+")")
		p_payload = p_payload + 2*1
		
		sensf_res_data = raw[p_payload:(p_payload+2*l)]	
		print("    * SENSF_RES: "+sensf_res_data)
		# SENSF_RES_PARSER(sensf_res_data,len_sensf_res)
		p_payload = p_payload + 2*l
		# if(i < n-1):
		# 	print("")
	# print("#end")
	return p_payload

# 61 09
def RF_NFCEE_ACTION_NTF(raw, vendor="None", model="None"):
	"""""""""""""""
		[RF_NFCEE_ACTION_NTF]
    NFCEE ID:					1 Octet
	Trigger:					1 Octet
	Supporting Data Length:		1 Octet
	Supporting Data:			n Octet(s)
	"""""""""""""""
	# print("RF_NFCEE_ACTION_NTF")
	NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0
	
	nfcee_id = raw[p_payload:(p_payload+2*1)]
	nfcee_id_range = range_lookup.find_range_key(NFC_table.tbl_nfcee_id, int(nfcee_id, 16))
	print("  * NFCEE ID:", nfcee_id, NFC_table.tbl_nfcee_id.get(nfcee_id, ""), NFC_table.tbl_nfcee_id.get(nfcee_id_range, ""))
	p_payload = p_payload + 2*1

	nfcee_ntf_trig = raw[p_payload:(p_payload+2*1)]
	print("  * Trigger: "+lookup(NFC_table.tbl_nfcee_ntf_trig, nfcee_ntf_trig), "("+nfcee_ntf_trig+")")
	p_payload = p_payload + 2*1
	
	data_len = raw[p_payload:(p_payload+2*1)]	
	n = int(data_len,16)
	print("  * Supporting Data Len:", n)
	p_payload = p_payload + 2*1
	
	data_val = raw[p_payload:(p_payload+2*n)]	
	print("  * Supporting Data: ")
	if(nfcee_ntf_trig == "00"):
		print("    * AID: "+data_val)
	elif(nfcee_ntf_trig == "01"):
		print("    * RF Protocol: "+lookup(NFC_table.tbl_rf_proto, data_val), "("+data_val+")")
	elif((nfcee_ntf_trig == "02") | (nfcee_ntf_trig == "05")):
		print("    * RF Technology: "+lookup(NFC_table.tbl_rf_tech, data_val), "("+data_val+")")
	elif(nfcee_ntf_trig == "03"):
		print("    * SC Route: "+data_val)
	elif(nfcee_ntf_trig == "04"):
		# Table 58: Reference data (n/2 octets) + Mask (n/2 octets)
		half = (n//2)*2
		print("    * Reference data: "+data_val[:half])
		print("    * Mask: "+data_val[half:])
	elif(n > 0):
		# RFU / application specific trigger: raw Supporting Data
		print("    * Data: "+data_val)
	p_payload = p_payload + 2*n
	# print("")
	return p_payload

# 61 0A
def RF_NFCEE_DISCOVERY_REQ_NTF(raw, vendor="None", model="None"):
	"""""""""""""""
		[RF_NFCEE_DISCOVERY_REQ_NTF]
	Number of Information Entries:		1 Octet (n)
	Information Entry [1..n]:			x+2 Octets
	﹂	Type:							﹂	1 Octet
	﹂	Length:							﹂	1 Octet (x)
	﹂	Value: 							﹂	x Octet(s)
	"""""""""""""""
	# print("RF_NFCEE_DISCOVERY_REQ_NTF")
	NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0
	
	num_info = raw[p_payload:(p_payload+2*1)]
	n = int(num_info,16)
	print("  * Number Of Info Entries:", n)
	p_payload = p_payload + 2*1

	for i in range(n):
		print()
		print("   ~ [Info Entry_"+str(i)+"] ~  ")
		type_val = raw[p_payload:(p_payload+2*1)] # Table 85
		print("    * Type: "+lookup(NFC_table.tbl_nfcee_disc_req_type, type_val))
		p_payload = p_payload + 2*1

		data_len = raw[p_payload:(p_payload+2*1)]	
		x = int(data_len,16)
		print("    * Len:", x)
		p_payload = p_payload + 2*1	
		
		data_val = raw[p_payload:(p_payload+2*x)]	
		print("    * Val: "+data_val)
		def info_value(v):
			if((type_val != "00") & (type_val != "01")):
				return
			nfcee_id = v.read(1, "NFCEE ID")
			nfcee_id_range = range_lookup.find_range_key(NFC_table.tbl_nfcee_id, int(nfcee_id, 16))
			print("      * NFCEE:", nfcee_id, NFC_table.tbl_nfcee_id.get(nfcee_id, ""), NFC_table.tbl_nfcee_id.get(nfcee_id_range, ""))
			rf_tech_mode = v.read(1, "RF Technology and Mode")
			print("      * Mode: "+lookup(NFC_table.tbl_rf_tech_mode, rf_tech_mode), "("+rf_tech_mode+")")
			rf_proto = v.read(1, "RF Protocol")
			print("      * RF Protocol: "+lookup(NFC_table.tbl_rf_proto, rf_proto), "("+rf_proto+")")
		_with_sub(data_val, "Information Entry Value", info_value)
		p_payload = p_payload + 2*x
		
		# if(i < n-1):
		# 	print("")
	# print("#end")
	return p_payload

# 21 0B
def RF_PARAMETER_UPDATE_CMD(raw, vendor="None", model="None"):
	"""""""""""""""
		[RF_PARAMETER_UPDATE_CMD]
	Number of Parameters:					1 Octet (n)
	RF Communication Parameters [1..n]:		x+2 Octets
	﹂	ID:									﹂	1 Octet
	﹂	Length:								﹂	1 Octet (x)
	﹂	Value: 								﹂	x Octet(s)
	"""""""""""""""
	# print("RF_PARAMETER_UPDATE_CMD")
	NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0
	
	num_para = raw[p_payload:(p_payload+2*1)]	
	n = int(num_para,16)
	print("  * Number of Params:", n, "("+num_para+")")
	p_payload = p_payload + 2*1

	for i in range(n):
		print()
		print("   ~ [RF Communication "+str(i)+"] ~  ")
		id_val = raw[p_payload:(p_payload+2*1)]
		print("  * Type ID: "+lookup(NFC_table.tbl_rf_commu_para_id, id_val), "("+id_val+")")
		p_payload = p_payload + 2*1

		data_len = raw[p_payload:(p_payload+2*1)]	
		x = int(data_len,16)
		print("  * Len:", x)
		p_payload = p_payload + 2*1
		
		data_val = raw[p_payload:(p_payload+2*x)]	
		print("  * Val: "+data_val)
		if(data_val == ""):
			pass # empty value: nothing to decode
		elif(id_val == "00"):	# Table 91
			para_val = data_val[0:2]
			print("    * Mode: "+lookup(NFC_table.tbl_rf_tech_mode, para_val), "("+para_val+")")
		elif((id_val == "01") | (id_val == "02")):
			para_val = data_val[0:2]
			if(id_val == "01"):
				print("    * Tx: "+lookup(NFC_table.tbl_bit_rates, para_val), "("+data_val[0:2]+")")
			elif(id_val == "02"):
				print("    * Rx: "+lookup(NFC_table.tbl_bit_rates, para_val), "("+data_val[0:2]+")")
		elif(id_val == "03"): # Table 92
			para_val = data_val[0:2]
			print("    * NFC-B Data Exchange Config: "+para_val)
			data_ex_cfg_b = bin(int(para_val,16))[2::].zfill(8)
			print('{0:<25}'.format("     ~ Minimum TR0:"), end="")
			print('{0:>2}'.format(data_ex_cfg_b[0:2]))
			print('{0:<25}'.format("     ~ Minimum TR1:"), end="")
			print('{0:>2}'.format(data_ex_cfg_b[2:4]))
			print('{0:<25}'.format("     ~ Suppression of EoS:"), end="")
			print('{0:>2}'.format(data_ex_cfg_b[4:5]))
			print('{0:<25}'.format("     ~ Suppression of SoS:"), end="")
			print('{0:>2}'.format(data_ex_cfg_b[5:6]))
			print('{0:<25}'.format("     ~ Minimum TR3:"), end="")
			print('{0:>2}'.format(data_ex_cfg_b[6:8]))
		p_payload = p_payload + 2*x
		
		# if(i < n-1):
		# 	print("")
	# print("#end")
	return p_payload

# 41 0B
def RF_PARAMETER_UPDATE_RSP(raw, vendor="None", model="None"):
	"""""""""""""""
		[RF_PARAMETER_UPDATE_RSP]
    Status:		1 Octet
	Number of Parameters:					1 Octet (n)
	RF Communication Parameters [1..n]:		1 Octets
	"""""""""""""""
	# print("RF_PARAMETER_UPDATE_RSP")
	NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]	
	print("  * Status: "+lookup(NFC_table.tbl_status_codes, status), "("+status+")")
	p_payload = p_payload + 2*1
	
	num_para = raw[p_payload:(p_payload+2*1)]	
	n = int(num_para,16)
	print("  * Number of Params:", n)
	p_payload = p_payload + 2*1
	
	print("  * RF Communication Param ID: ")
	for i in range(n):
		id_val = raw[p_payload:(p_payload+2*1)]
		print("  * Type ID "+str(i)+": "+lookup(NFC_table.tbl_rf_commu_para_id, id_val), "("+id_val+")")
		p_payload = p_payload + 2*1
	# print("")
	return p_payload

# 21 0C
def RF_INTF_EXT_START_CMD(raw, vendor="None", model="None"):
	"""""""""""""""
		[RF_INTF_EXT_START_CMD]
	RF Interface Extension:		1 Octet
	Start Parameter Length:		1 Octet (x)
	Start Parameter: 			x Octet(s)
	"""""""""""""""
	# print("RF_INTF_EXT_START_CMD")
	NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0

	exten = raw[p_payload:(p_payload+2*1)]
	print("  * RF Interface Extension: "+lookup(NFC_table.tbl_rf_if_exten, exten), "("+exten+")")
	p_payload = p_payload + 2*1
	
	start_para_len = raw[p_payload:(p_payload+2*1)]
	x = int(start_para_len,16)
	print("  * Start Param Len:", x)
	p_payload = p_payload + 2*1

	start_para = raw[p_payload:(p_payload+2*x)]
	print("  * Start Param: "+start_para)
	p_payload = p_payload + 2*x
	# print("")
	return p_payload

# 41 0C
def RF_INTF_EXT_START_RSP(raw, vendor="None", model="None"):
	"""""""""""""""
		[RF_INTF_EXT_START_RSP]
    Status:		1 Octet
	"""""""""""""""
	# print("RF_INTF_EXT_START_RSP")
	NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]	
	print("  * Status: "+lookup(NFC_table.tbl_status_codes, status), "("+status+")")
	p_payload = p_payload + 2*1
	# print("")
	return p_payload

# 21 0D
def RF_INTF_EXT_STOP_CMD(raw, vendor="None", model="None"):
	"""""""""""""""
		[RF_INTF_EXT_STOP_CMD]
    RF Interface Extension:		1 Octet
    Stop Parameter Length::		1 Octet (x)
    Stop Parameter:				x Octet(s)
	"""""""""""""""
	# print("RF_INTF_EXT_STOP_CMD")
	NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0

	exten = raw[p_payload:(p_payload+2*1)]
	print("  * RF Interface Extension: "+lookup(NFC_table.tbl_rf_if_exten, exten), "("+exten+")")
	p_payload = p_payload + 2*1
	
	start_para_len = raw[p_payload:(p_payload+2*1)]
	x = int(start_para_len,16)
	print("  * Stop Param Len:", x)
	p_payload = p_payload + 2*1

	start_para = raw[p_payload:(p_payload+2*x)]
	print("  * Stop Param: "+start_para)
	p_payload = p_payload + 2*x
	# print("")
	return p_payload

# 41 0D
def RF_INTF_EXT_STOP_RSP(raw, vendor="None", model="None"):
	"""""""""""""""
		[RF_INTF_EXT_STOP_RSP]
    Status:		1 Octet
	"""""""""""""""
	# print("RF_INTF_EXT_STOP_RSP")
	NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]	
	print("  * Status: "+lookup(NFC_table.tbl_status_codes, status), "("+status+")")
	p_payload = p_payload + 2*1
	# print("")
	return p_payload

# 21 0E
def RF_EXT_AGG_ABORT_CMD(raw, vendor="None", model="None"):
	"""""""""""""""
		[RF_EXT_AGG_ABORT_CMD]
    (Empty)
	"""""""""""""""
	NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0
	# print("RF_EXT_AGG_ABORT_CMD")
	print('{0:^25}'.format("(Empty)"))
	# print("")
	return p_payload

# 41 0E
def RF_EXT_AGG_ABORT_RSP(raw, vendor="None", model="None"):
	"""""""""""""""
		[RF_EXT_AGG_ABORT_RSP]
    Status:		1 Octet
	"""""""""""""""
	# print("RF_EXT_AGG_ABORT_RSP")
	NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]	
	print("  * Status: "+lookup(NFC_table.tbl_status_codes, status), "("+status+")")
	p_payload = p_payload + 2*1
	# print("")
	return p_payload

# 21 0F
def RF_NDEF_ABORT_CMD(raw, vendor="None", model="None"):
	"""""""""""""""
		[RF_NDEF_ABORT_CMD]
    (Empty)
	"""""""""""""""
	NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0
	# print("RF_NDEF_ABORT_CMD")
	print('{0:^25}'.format("(Empty)"))
	# print("")
	return p_payload
	
# 41 0F
def RF_NDEF_ABORT_RSP(raw, vendor="None", model="None"):
	"""""""""""""""
		[RF_NDEF_ABORT_RSP]
    Status:		1 Octet
	"""""""""""""""
	# print("RF_NDEF_ABORT_RSP")
	NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]	
	print("  * Status: "+lookup(NFC_table.tbl_status_codes, status), "("+status+")")
	p_payload = p_payload + 2*1
	# print("")
	return p_payload

# 21 10
def RF_ISO_DEP_NAK_PRESENCE_CMD(raw, vendor="None", model="None"):
	"""""""""""""""
		[RF_ISO_DEP_NAK_PRESENCE_CMD]
    (Empty)
	"""""""""""""""
	NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0
	# print("RF_ISO_DEP_NAK_PRESENCE_CMD")
	print('{0:^25}'.format("(Empty)"))
	# print("")
	return p_payload

# 41 10
def RF_ISO_DEP_NAK_PRESENCE_RSP(raw, vendor="None", model="None"):
	"""""""""""""""
		[RF_ISO_DEP_NAK_PRESENCE_RSP]
    Status:		1 Octet
	"""""""""""""""
	# print("RF_ISO_DEP_NAK_PRESENCE_RSP")
	NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]	
	print("  * Status: "+lookup(NFC_table.tbl_status_codes, status), "("+status+")")
	p_payload = p_payload + 2*1
	# print("")
	return p_payload
	
# 61 10
def RF_ISO_DEP_NAK_PRESENCE_NTF(raw, vendor="None", model="None"):
	"""""""""""""""
		[RF_ISO_DEP_NAK_PRESENCE_NTF]
    Status:		1 Octet
	"""""""""""""""
	# print("RF_ISO_DEP_NAK_PRESENCE_NTF")
	NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]	
	print("  * Status: "+lookup(NFC_table.tbl_status_codes, status), "("+status+")")
	p_payload = p_payload + 2*1
	# print("")
	return p_payload
	
# 21 11
def RF_SET_FORCED_NFCEE_ROUTING_CMD(raw, vendor="None", model="None"):
	"""""""""""""""
		[RF_SET_FORCED_NFCEE_ROUTING_CMD]
    Forced NFCEE Routing State:		1 Octet
	Forced NFCEE Value Field:		0 or 2 Octet(s)
	﹂	Forced NFCEE				﹂	1 Octet
	﹂	Forced Power State			﹂	1 Octet
	"""""""""""""""
	# print("RF_SET_FORCED_NFCEE_ROUTING_CMD")
	NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0

	forced_nfcee_rout_state = raw[p_payload:(p_payload+2*1)]
	p_payload = p_payload + 2*1
	if(forced_nfcee_rout_state == "00"):
		print("  * Forced NFCEE Routing State: "+"Disabled")

	elif(forced_nfcee_rout_state == "01"):
		print("  * Forced NFCEE Routing State: "+"Enabled")
		forced_nfcee = raw[p_payload:(p_payload+2*1)]
		route_val = range_lookup.find_range_key(NFC_table.tbl_nfcee_id, int(forced_nfcee, 16))
		print("  * Forced NFCEE:", forced_nfcee, NFC_table.tbl_nfcee_id.get(forced_nfcee, ""), NFC_table.tbl_nfcee_id.get(route_val, ""))
		p_payload = p_payload + 2*1

		forced_pwr_state = raw[p_payload:(p_payload+2*1)]
		pwr_state_b = bin(int(forced_pwr_state,16))[2::].zfill(8)
		print("    * Power State: "+pwr_state_b+" ("+forced_pwr_state+")")
		for j in range (5,-1,-1):
			print('{0:<33}'.format("     ~ "+lookup(NFC_table.tbl_pwr_state, j)+":"), end="")
			if(pwr_state_b[7-j:8-j] == "1"):
				print('{0:<10}'.format("Apply"))
			else:
				print('{0:<10}'.format("Not apply"))
		p_payload = p_payload + 2*1

	else:
		print("  * Forced NFCEE Routing State: "+"Error"+" ("+forced_nfcee_rout_state+")")
	# print("")
	return p_payload
	
# 41 11
def RF_SET_FORCED_NFCEE_ROUTING_RSP(raw, vendor="None", model="None"):
	"""""""""""""""
		[RF_SET_FORCED_NFCEE_ROUTING_RSP]
    Status:		1 Octet
	"""""""""""""""
	# print("RF_SET_FORCED_NFCEE_ROUTING_RSP")
	NFC_table = pkg_import.tbl_import(vendor, model)
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]	
	print("  * Status: "+lookup(NFC_table.tbl_status_codes, status), "("+status+")")
	p_payload = p_payload + 2*1
	# print("")
	return p_payload