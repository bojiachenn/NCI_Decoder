import nfc_forum_pkg.__table__ as NFC_table
from nfc_forum_pkg import NFCEE_Management as Origin

#       模板       #

# 22 00
def NFCEE_DISCOVER_CMD(raw):
	"""""""""""""""
		[NFCEE_DISCOVER_CMD]
    (Empty)
	"""""""""""""""
	# print("NFCEE_DISCOVER_CMD")
	p_payload = Origin.NFCEE_DISCOVER_CMD(raw)
	return p_payload

# 42 00
def NFCEE_DISCOVER_RSP(raw):
	"""""""""""""""
		[NFCEE_DISCOVER_RSP]
    Status:				1 Octet
	Number of NFCEEs:	1 Octet
	"""""""""""""""
	# print("NFCEE_DISCOVER_RSP")
	p_payload = Origin.NFCEE_DISCOVER_RSP(raw)
	return p_payload

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
	p_payload = Origin.NFCEE_DISCOVER_NTF(raw)
	return p_payload

# 22 01
def NFCEE_MODE_SET_CMD(raw):
	"""""""""""""""
		[NFCEE_MODE_SET_CMD]
    NFCEE ID:			1 Octet
	NFCEE Mode:			1 Octet
	"""""""""""""""
	# print("NFCEE_MODE_SET_CMD")
	p_payload = Origin.NFCEE_MODE_SET_CMD(raw)
	return p_payload

# 42 01
def NFCEE_MODE_SET_RSP(raw):
	"""""""""""""""
		[NFCEE_MODE_SET_RSP]
    Status:		1 Octet
	"""""""""""""""
	# print("NFCEE_MODE_SET_RSP")
	p_payload = Origin.NFCEE_MODE_SET_RSP(raw)
	return p_payload
		
# 62 01
def NFCEE_MODE_SET_NTF(raw):
	"""""""""""""""
		[NFCEE_MODE_SET_NTF]
    Status:		1 Octet
	"""""""""""""""
	# print("NFCEE_MODE_SET_NTF")
	p_payload = Origin.NFCEE_MODE_SET_NTF(raw)
	return p_payload

# 62 02
def NFCEE_STATUS_NTF(raw):
	"""""""""""""""
		[NFCEE_STATUS_NTF]
    NFCEE ID:			1 Octet
	NFCEE Status:		1 Octet
	"""""""""""""""
	# print("NFCEE_STATUS_NTF")
	p_payload = Origin.NFCEE_STATUS_NTF(raw)
	return p_payload

# 22 03
def NFCEE_POWER_AND_LINK_CNTRL_CMD(raw):
	"""""""""""""""
		[NFCEE_POWER_AND_LINK_CNTRL_CMD]
    NFCEE ID:								1 Octet
	NFCEE Power and Link Configuration:		1 Octet
	"""""""""""""""
	# print("NFCEE_POWER_AND_LINK_CNTRL_CMD")
	p_payload = Origin.NFCEE_POWER_AND_LINK_CNTRL_CMD(raw)
	return p_payload
			
# 22 03
def NFCEE_POWER_AND_LINK_CNTRL_RSP(raw):
	"""""""""""""""
		[NFCEE_POWER_AND_LINK_CNTRL_RSP]
    Status:		1 Octet
	"""""""""""""""
	# print("NFCEE_POWER_AND_LINK_CNTRL_RSP")
	p_payload = Origin.NFCEE_POWER_AND_LINK_CNTRL_RSP(raw)
	return p_payload