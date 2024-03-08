from nci_decoder.nfc_forum_pkg import __table__ as NFC_table

# 20 02
def CORE_SET_CONFIG_CMD(raw):
	"""""""""""""""
		[CORE_SET_CONFIG_CMD]
	Number of Parameters: 	1 Octet (n)
	Parameter [1..n]: 		m+2 Octets
	﹂	Register:	        ﹂	2 Octets
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
		reg = raw[p_payload:(p_payload+2*2)]
		print("  -- Register: "+reg)
		p_payload = p_payload + 2*2
		
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