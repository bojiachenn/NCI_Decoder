import __table__ as NFC_table

#	    Jimmt Chen  	#
#	Done on: 2024/2/20	#

# 22 00
def NFCEE_DISCOVER_CMD(raw):
	"""""""""""""""
		[NFCEE_DISCOVER_CMD]
    (Empty)
	"""""""""""""""
	# print("NFCEE_DISCOVER_CMD")
	print('{0:^25}'.format("(Empty)"))
	print("")

# 42 00
def NFCEE_DISCOVER_RSP(raw):
	"""""""""""""""
		[NFCEE_DISCOVER_RSP]
    Status:				1 Octet
	Number of NFCEEs:	1 Octet
	"""""""""""""""
	# print("NFCEE_DISCOVER_RSP")
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]	
	print("- Status: "+NFC_table.tbl_status_codes.get(status,"RFU")+" ("+status+")")
	p_payload = p_payload + 2*1
	
	num_nfcee  =raw[p_payload:(p_payload+2*1)]	
	n = int(num_nfcee,16)
	print("- Number of NFCEEs:", n, "("+num_nfcee+")")
	p_payload = p_payload + 2*1
	print("")

# 62 00
def NFCEE_DISCOVER_NTF(raw):
	"""""""""""""""
		[NFCEE_DISCOVER_NTF]
    NFCEE ID: 									1 Octet
	NFCEE Status: 								1 Octet
	Number of Protocol Information Entries: 	1 Octet (n)
	Supported NFCEE Protocols [0..n]:  			n Octet(s)
	Number of NFCEE Information TLVs: 			1 Octet
	NFCEE Information TLV [0..m]: 				x+2 Octet
	﹂	Type:									﹂	1 Octet
	﹂	Length:									﹂	1 Octet (x)
	﹂	Value: 									﹂	x Octet(s)
	NFCEE Power Supply: 						1 Octet
	"""""""""""""""
	# print("NFCEE_DISCOVER_NTF")
	p_payload = 0

	nfcee_id = raw[p_payload:(p_payload+2*1)]
	nfcee_id_i = int(nfcee_id, 16)
	if((nfcee_id_i >= 2) & (nfcee_id_i <= 15)):
		nfcee_id = '02-0F'
	elif((nfcee_id_i >= 16) & (nfcee_id_i <= 127)):
		nfcee_id = '10-7F'
	elif((nfcee_id_i >= 128) & (nfcee_id_i <= 254)):
		nfcee_id = '80-FE'
	print("- NFCEE ID:", nfcee_id_i, "("+NFC_table.tbl_nfcee_id.get(nfcee_id,"RFU")+") ("+raw[p_payload:(p_payload+2*1)]+")")
	p_payload = p_payload + 2*1
	
	nfcee_status = raw[p_payload:(p_payload+2*1)]
	if(nfcee_status == "00"):
		print("- NFCEE Status: "+"Enabled"+" ("+nfcee_status+")")
	elif(nfcee_status == "01"):
		print("- NFCEE Status: "+"Disabled"+" ("+nfcee_status+")")
	elif(nfcee_status == "02"):
		print("- NFCEE Status: "+"Unresponsive"+" ("+nfcee_status+")")
	else:
		print("- NFCEE Status: "+"RFU"+" ("+nfcee_status+")")
	p_payload = p_payload + 2*1

	num_proto_info = raw[p_payload:(p_payload+2*1)]
	n = int(num_proto_info, 16)
	print("- Number of Protocol Information Entries:", n, "("+num_proto_info+")")
	p_payload = p_payload + 2*1

	if(n != 0):
		support_proto_val = raw[p_payload:(p_payload+2*n)]
		print("- Supported NFCEE Protocols: "+ support_proto_val)
		entry_payload = 0
		for i in range(n):
			nfcee_proto = support_proto_val[entry_payload:(entry_payload+2*1)]	
			print("  -- Protocol "+str(i)+": "+NFC_table.tbl_nfcee_proto.get(nfcee_proto,"RFU")+" ("+nfcee_proto+")")
			entry_payload = entry_payload + 2*1	
		p_payload = p_payload + 2*n	

	num_nfcee_info_tlv = raw[p_payload:(p_payload+2*1)]	
	m = int(num_nfcee_info_tlv, 16)
	print("- Number of NFCEE Information TLVs:", m, "("+num_nfcee_info_tlv+")\n")
	p_payload = p_payload + 2*1
	
	if(m != 0):
		for i in range(m):
			print("  -- [NFCEE Info TLV_"+str(i)+"] --  ")
			tlv_type = raw[p_payload:(p_payload+2*1)]
			if((int(tlv_type, 16) >= 5) & (int(tlv_type, 16) <= 159)):
				tlv_type = '05-9F'
			elif((int(tlv_type, 16) >= 160) & (int(tlv_type, 16) <= 255)):
				tlv_type = 'A0-FF'
			print("  -- Type: "+NFC_table.tbl_tlv_type.get(tlv_type,"RFU")+" ("+raw[p_payload:(p_payload+2*1)]+")")
			p_payload = p_payload + 2*1		

			tlv_len = raw[p_payload:(p_payload+2*1)]
			x = int(tlv_len, 16)
			print("  -- Length:", x, "("+tlv_len+")")
			p_payload = p_payload + 2*1	

			tlv_val = raw[p_payload:(p_payload+2*x)]
			print("  -- Value: "+tlv_val)

			if(tlv_type == "02"):
				print("   --- PMm: "+tlv_val[0:16])
				num_entry = int(tlv_val[16:18],16)
				print("   --- Number of Entries:", num_entry, "("+tlv_val[16:18]+")\n")
				for j in range(num_entry):
					print("    ---- [Entry_"+str(j)+"] ----   ")
					print("    ---- System Code: "+tlv_val[18 + 2*10*j : 18 + 2*10*j + 2*2])
					print("    ---- Idm: "+tlv_val[18 + 2*10*j + 2*2 : 18 + 2*10*j + 2*10])
					print("")

			elif(tlv_type == "04"):
				print("   --- NDEF max size: "+tlv_val[0:8])
				pwr_state = tlv_val[8:10]
				pwr_state_b = bin(int(pwr_state,16))[2::].zfill(8)
				print("   --- Power State: "+pwr_state_b+" ("+pwr_state+")")
				for j in range (5,-1,-1):
					print('{0:<33}'.format("   * "+NFC_table.tbl_pwr_state.get(j,"RFU")+":"), end="")
					if(pwr_state_b[7-j:8-j] == "1"):
						print('{0:<10}'.format("Apply"))
					else:
						print('{0:<10}'.format("Not apply"))
				ndef_nfcee_char = tlv_val[10:12]
				ndef_nfcee_char_b0 = bin(int(ndef_nfcee_char,16))[2::].zfill(8)[7:8]
				if(ndef_nfcee_char_b0 == "0"):
					print("   --- NDEF-NFCEE characteristics: "+"The NDEF message is not persistent over a power off/on and NCI initialization sequence.")
				elif(ndef_nfcee_char_b0 == "1"):
					print("   --- NDEF-NFCEE characteristics: "+"The NDEF message is persistent over a power off/on and NCI initialization sequence.")

			p_payload = p_payload + 2*x	
			print("")
	
	nfcee_pwr_sup = raw[p_payload:(p_payload+2*1)]
	if(nfcee_pwr_sup == "00"):
		print("- NFCEE Power Supply: "+"The NFCC has no control of the NFCEE Power Supply"+" ("+nfcee_pwr_sup+")")
	elif(nfcee_pwr_sup == "01"):
		print("- NFCEE Power Supply: "+"The NFCC has control of the NFCEE Power Supply"+" ("+nfcee_pwr_sup+")")
	else:
		print("- NFCEE Power Supply: "+"RFU"+" ("+nfcee_pwr_sup+")")
	print("")

# 22 01
def NFCEE_MODE_SET_CMD(raw):
	"""""""""""""""
		[NFCEE_MODE_SET_CMD]
    NFCEE ID:			1 Octet
	NFCEE Mode:			1 Octet
	"""""""""""""""
	# print("NFCEE_MODE_SET_CMD")
	p_payload = 0
	
	nfcee_id = raw[p_payload:(p_payload+2*1)]
	nfcee_id_i = int(nfcee_id, 16)
	if((nfcee_id_i >= 2) & (nfcee_id_i <= 15)):
		nfcee_id = '02-0F'
	elif((nfcee_id_i >= 16) & (nfcee_id_i <= 127)):
		nfcee_id = '10-7F'
	elif((nfcee_id_i >= 128) & (nfcee_id_i <= 254)):
		nfcee_id = '80-FE'
	print("- NFCEE ID:", nfcee_id_i, "("+NFC_table.tbl_nfcee_id.get(nfcee_id,"RFU")+") ("+raw[p_payload:(p_payload+2*1)]+")")
	p_payload = p_payload + 2*1
	
	nfcee_mode = raw[p_payload:(p_payload+2*1)]
	if(nfcee_mode == "00"):
		print("- NFCEE Mode: "+"Disable"+" ("+nfcee_mode+")")
	elif(nfcee_mode == "01"):
		print("- NFCEE Mode: "+"Enable"+" ("+nfcee_mode+")")
	else:
		print("- NFCEE Mode: "+"RFU"+" ("+nfcee_mode+")")
	p_payload = p_payload + 2*1	
	print("")

# 42 01
def NFCEE_MODE_SET_RSP(raw):
	"""""""""""""""
		[NFCEE_MODE_SET_RSP]
    Status:		1 Octet
	"""""""""""""""
	# print("NFCEE_MODE_SET_RSP")
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]	
	print("- Status: "+NFC_table.tbl_status_codes.get(status,"RFU")+" ("+status+")")
	p_payload = p_payload + 2*1
	print("")
		
# 62 01
def NFCEE_MODE_SET_NTF(raw):
	"""""""""""""""
		[NFCEE_MODE_SET_NTF]
    Status:		1 Octet
	"""""""""""""""
	# print("NFCEE_MODE_SET_NTF")
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]	
	print("- Status: "+NFC_table.tbl_status_codes.get(status,"RFU")+" ("+status+")")
	p_payload = p_payload + 2*1
	print("")

# 62 02
def NFCEE_STATUS_NTF(raw):
	"""""""""""""""
		[NFCEE_STATUS_NTF]
    NFCEE ID:			1 Octet
	NFCEE Status:		1 Octet
	"""""""""""""""
	# print("NFCEE_STATUS_NTF")
	p_payload = 0
	
	nfcee_id = raw[p_payload:(p_payload+2*1)]
	nfcee_id_i = int(nfcee_id, 16)
	if((nfcee_id_i >= 2) & (nfcee_id_i <= 15)):
		nfcee_id = '02-0F'
	elif((nfcee_id_i >= 16) & (nfcee_id_i <= 127)):
		nfcee_id = '10-7F'
	elif((nfcee_id_i >= 128) & (nfcee_id_i <= 254)):
		nfcee_id = '80-FE'
	print("- NFCEE ID:", nfcee_id_i, "("+NFC_table.tbl_nfcee_id.get(nfcee_id,"RFU")+") ("+raw[p_payload:(p_payload+2*1)]+")")
	p_payload = p_payload + 2*1
	
	nfcee_status = raw[p_payload:(p_payload+2*1)]
	if(nfcee_status == "00"):
		print("- NFCEE Status: "+"Unrecoverable error"+" ("+nfcee_status+")")
	elif(nfcee_status == "01"):
		print("- NFCEE Status: "+"NFCEE Initialization sequence started"+" ("+nfcee_status+")")
	elif(nfcee_status == "02"):
		print("- NFCEE Status: "+"NFCEE Initialization sequence completed"+" ("+nfcee_status+")")
	elif((int(nfcee_status,16) >= 3) & (int(nfcee_status,16) <= 127)):
		print("- NFCEE Status: "+"RFU"+" ("+nfcee_status+")")
	else:
		print("- NFCEE Status: "+"Proprietary"+" ("+nfcee_status+")")
	p_payload = p_payload + 2*1	
	print("")

# 22 03
def NFCEE_POWER_AND_LINK_CNTRL_CMD(raw):
	"""""""""""""""
		[NFCEE_POWER_AND_LINK_CNTRL_CMD]
    NFCEE ID:								1 Octet
	NFCEE Power and Link Configuration:		1 Octet
	"""""""""""""""
	# print("NFCEE_POWER_AND_LINK_CNTRL_CMD")
	p_payload = 0
	
	nfcee_id = raw[p_payload:(p_payload+2*1)]
	nfcee_id_i = int(nfcee_id, 16)
	if((nfcee_id_i >= 2) & (nfcee_id_i <= 15)):
		nfcee_id = '02-0F'
	elif((nfcee_id_i >= 16) & (nfcee_id_i <= 127)):
		nfcee_id = '10-7F'
	elif((nfcee_id_i >= 128) & (nfcee_id_i <= 254)):
		nfcee_id = '80-FE'
	print("- NFCEE ID:", nfcee_id_i, "("+NFC_table.tbl_nfcee_id.get(nfcee_id,"RFU")+") ("+raw[p_payload:(p_payload+2*1)]+")")
	p_payload = p_payload + 2*1
	
	nfcee_cfg = raw[p_payload:(p_payload+2*1)]
	if(nfcee_cfg == "00"):
		print("- NFCEE Power and Link Cfg: "+"NFCC decides (default state)."+" ("+nfcee_cfg+")")
	elif(nfcee_cfg == "01"):
		print("- NFCEE Power and Link Cfg: "+"NFCEE Power Supply always On."+" ("+nfcee_cfg+")")
	elif(nfcee_cfg == "02"):
		print("- NFCEE Power and Link Cfg: "+"NFCC to NFCEE Communication link always active when the NFCEE is powered on."+" ("+nfcee_cfg+")")
	elif(nfcee_cfg == "03"):	
		print("- NFCEE Power and Link Cfg: "+"NFCEE Power supply and NFCC to NFCEE communication link are always on."+" ("+nfcee_cfg+")")
	else:
		print("- NFCEE Power and Link Cfg: "+"RFU"+" ("+nfcee_cfg+")")
	p_payload = p_payload + 2*1	
	print("")
			
# 22 03
def NFCEE_POWER_AND_LINK_CNTRL_RSP(raw):
	"""""""""""""""
		[NFCEE_POWER_AND_LINK_CNTRL_RSP]
    Status:		1 Octet
	"""""""""""""""
	# print("NFCEE_POWER_AND_LINK_CNTRL_RSP")
	p_payload = 0
	
	status = raw[p_payload:(p_payload+2*1)]	
	print("- Status: "+NFC_table.tbl_status_codes.get(status,"RFU")+" ("+status+")")
	p_payload = p_payload + 2*1
	print("")