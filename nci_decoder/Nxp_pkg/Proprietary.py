import Nxp_pkg.__table__ as NFC_table

# Table 13. SN2x0 NFCC-NCI additional commands/notifications

# 2F 00
def CORE_SET_POWER_MODE_CMD(raw):
    """""""""""""""
		[CORE_SET_POWER_MODE_CMD]
    Mode:       1 Octet     Command to request the SN2x0 NFCC to enable/disable
                            the Standby State
	"""""""""""""""
    p_payload = 0
    
    mode = raw[p_payload:(p_payload+2*1)]	
    if(mode == '00'):
        print("  * Mode:", "Standby State disabled")
    elif(mode == '01'):
        print("  * Mode:", "Standby State enabled")
    elif(mode == '02'):
        print("  * Mode:", "Autonomous Mode enabled")
    elif(mode == '03'):
        print("  * Mode:", "ULPDET State enabled")
    elif(mode == '04'):
        print("  * Mode:", "Autonomous Mode enabled with Poll")
    elif(mode == '05'):
        print("  * Mode:", "ULPDET enabled with NCI notifications")
    else:
        print("  * Mode:", "RFU")

    p_payload = p_payload + 2*1
    return p_payload


# 4F 00
def CORE_SET_POWER_MODE_RSP(raw):
    """""""""""""""
		[CORE_SET_POWER_MODE_RSP]
    Status:         1 Octet
	"""""""""""""""
    p_payload = 0

    status = raw[p_payload:(p_payload+2*1)]
    print("  * Status:", NFC_table.tbl_status_codes.get(status, "RFU"))
    p_payload = p_payload + 2*1
    return p_payload

# 2F 01
def SET_NFC_SERVICE_STATUS_CMD(raw):
    """""""""""""""
		[SET_NFC_SERVICE_STATUS_CMD]
    Mode:       1 Octet
	"""""""""""""""
    p_payload = 0
    
    mode = raw[p_payload:(p_payload+2*1)]	
    if(mode == '00'):
        print("  * Mode:", "NFC service OFF")
    elif(mode == '01'):
        print("  * Mode:", "NFC service ON")
    else:
        print("  * Mode:", "RFU")
    p_payload = p_payload + 2*1
    return p_payload

# 4F 01
def SET_NFC_SERVICE_STATUS_RSP(raw):
    """""""""""""""
		[SET_NFC_SERVICE_STATUS_RSP]
    Status:         1 Octet
	"""""""""""""""
    p_payload = 0

    status = raw[p_payload:(p_payload+2*1)]
    print("  * Status:", NFC_table.tbl_status_codes.get(status, "RFU"))
    p_payload = p_payload + 2*1
    return p_payload

# 2F 02
def NCI_PROPRIETARY_ACT_CMD(raw):
	"""""""""""""""
		[NCI_PROPRIETARY_ACT_CMD]
    (Empty)
	"""""""""""""""
	p_payload = 0
	
	print('{0:^25}'.format("(Empty)"))
	# print("")
	return p_payload

# 4F 02
def NCI_PROPRIETARY_ACT_RSP(raw):
    """""""""""""""
		[NCI_PROPRIETARY_ACT_RSP]
    Status:         1 Octet
    FW_Build_Nb:    4 Octets
	"""""""""""""""
    p_payload = 0

    status = raw[p_payload:(p_payload+2*1)]	
    if(status == '00' or status == '03'):
        print("  * Status:", NFC_table.tbl_status_codes.get(status, "RFU"))
    else:
        print("  * Status:", "Forbidden")
    p_payload = p_payload + 2*1

    print("  * FW_Build_Nb:", raw[p_payload:p_payload+2*4])
    p_payload = p_payload + 2*4
    return p_payload

# 6F 04
def APDU_LOGGING_NTF(raw):
    """""""""""""""
		[NCI_PROPRIETARY_ACT_RSP]
    Logging Opcode:     1 octet     0x60
    RFU Length:         1 octet     Do not Care
    Timestamp:          2 octets    Indicates a timestamp with a maximum recording time of 1024ms with step of 16μs
    Category:           1 octet     0x0B: C-APDU from eSE
                                    0x1B: R-APDU from eSE
                                    0x2B: C-APDU from UICCx
                                    0x3B: R-APDU from UICCx
    APDU Data:          5 octets    First 5 bytes of the C-APDU
                        2 octets    Last 2 bytes of the R-APDU
	"""""""""""""""
    p_payload = 0
    op_code = raw[p_payload:(p_payload+2*1)]
    if(op_code != '60'):
        print("  * Logging Opcode:", op_code, "(Should be 0x60)")
    else:
        print("  * Logging Opcode:", op_code)
    p_payload = p_payload + 2*1

    # Do not Care
    p_payload = p_payload + 2*1

    step = raw[p_payload:(p_payload+2*2)] # max: 6400 step = 1024 ms
    time = int(step, 16) * 16   # 1 step = 16 μs
    time_ms = time / 1000       # 1000 μs = 1 ms
    print("  * Timestamp:", time_ms, "ms")
    p_payload = p_payload + 2*2

    category = raw[p_payload:(p_payload+2*1)]
    if(category == '0B'):
        print("  * Category:", "C-APDU from eSE")
    elif(category == '1B'):
        print("  * Category:", "R-APDU from eSE")
    elif(category == '2B'):
        print("  * Category:", "C-APDU from UICCx")
    elif(category == '3B'):
        print("  * Category:", "R-APDU from UICCx")
    else:
        print("  * Category:", "Error", category)
    p_payload = p_payload + 2*1

    if(category == '0B' or category == '2B'): # C-APDU
        first_c_apdu = raw[p_payload:(p_payload+2*5)]
        print("  * APDU Data:", first_c_apdu, "(First 5 bytes of the C-APDU)")
        p_payload = p_payload + 2*5
    elif(category == '1B' or category == '3B'): # R-APDU
        last_r_apdu = raw[p_payload:(p_payload+2*2)]
        print("  * APDU Data:", last_r_apdu, "(Last 2 bytes of the R-APDU)")
        p_payload = p_payload + 2*2
    return p_payload

# 2F 14
def RF_GET_TRANSITION_CMD(raw):
    """""""""""""""
		[RF_GET_TRANSITION_CMD]
    RF Transition ID:       1 Octet         RF Transition Identifier
    CLIF Register Offset:   1 Octet         Offset of the register to read out from the CLIF
	"""""""""""""""
    p_payload = 0
    trans_id = raw[p_payload:(p_payload+2*1)]
    print("  * RF Transition ID:", NFC_table.tbl_rf_trans_id.get(trans_id, "RFU ("+trans_id+")"), "("+trans_id+")")
    p_payload = p_payload + 2*1
    
    offset = raw[p_payload:(p_payload+2*1)]
    print("  * CLIF Register Offset:", offset)
    p_payload = p_payload + 2*1
	
    return p_payload

# 4F 14
def RF_GET_TRANSITION_RSP(raw):
    """""""""""""""
		[RF_GET_TRANSITION_RSP]
    Status:                 1 Octet                 
    RF Transition Length:   1 Octet                 
    RF Transition Value:    1, 2 or 4 Octet(s)      Value coded in Little Endian
    """""""""""""""
    p_payload = 0
    status = raw[p_payload:(p_payload+2*1)]
    if(status == '00' or status == '01' or status == '06'):
        print("  * Status:", NFC_table.tbl_status_codes.get(status, "RFU"))
    else:
        print("  * Status:", "Forbidden")
    p_payload = p_payload + 2*1
    
    l = raw[p_payload:(p_payload+2*1)]
    print("  * RF Transition Len:", int(l, 16))
    p_payload = p_payload + 2*1
    
    val = raw[p_payload:(p_payload+2*int(l, 16))]
    print("  * RF Transition Val:", val)
    p_payload = p_payload + 2*int(l, 16)
    return p_payload

# 6F 17
def WTX_NTF(raw):
	"""""""""""""""
		[WTX_NTF]
    (Empty)     Notification indicating that RF communication is in phase of
                WTX(RTOX) REQ/RESP exchange for longer period of time
	"""""""""""""""
	p_payload = 0
	
	print('{0:^25}'.format("(Empty)"))
	# print("")
	return p_payload

# 2F 1C
def LOW_POWER_TAG_REMOVAL_CMD(raw):
	"""""""""""""""
		[LOW_POWER_TAG_REMOVAL_CMD]
    (Empty)     Starts the low power tag removal detection command
	"""""""""""""""
	p_payload = 0
	
	print('{0:^25}'.format("(Empty)"))
	# print("")
	return p_payload

# 4F 1C
def LOW_POWER_TAG_REMOVAL_RSP(raw):
    """""""""""""""
	    [LOW_POWER_TAG_REMOVAL_RSP]
    Status:         1 Octet     The NFCC reset the eSE if the eSE is currently powered on.
                                Then it returns STATUS_OK.
    """""""""""""""
    p_payload = 0
    
    status = raw[p_payload:(p_payload+2*1)]	
    if(status == '00' or status == '01' or status == '09'):
        print("  * Status:", NFC_table.tbl_status_codes.get(status, "RFU"))
    else:
        print("  * Status:", "Forbidden")
    p_payload = p_payload + 2*1
    return p_payload

# 6F 1C
def LOW_POWER_TAG_REMOVAL_NTF(raw):
	"""""""""""""""
		[LOW_POWER_TAG_REMOVAL_NTF]
    (Empty)     Notify the host that the previously detected target has been
                removed from the NFCC proximity.
	"""""""""""""""
	p_payload = 0
	
	print('{0:^25}'.format("(Empty)"))
	# print("")
	return p_payload

# 2F 1E
def SYSTEM_ESE_POWER_CYCLE_CMD(raw):
      
	"""""""""""""""
		[SYSTEM_ESE_POWER_CYCLE_CMD]
    (Empty)     Command to reset the eSE
	"""""""""""""""
	p_payload = 0
	
	print('{0:^25}'.format("(Empty)"))
	# print("")
	return p_payload

# 4F 1E
def SYSTEM_ESE_POWER_CYCLE_RSP(raw):
    """""""""""""""
		[SYSTEM_ESE_POWER_CYCLE_RSP]
    Status:         1 Octet     The NFCC reset the eSE if the eSE is currently powered on. 
                                Then it returns STATUS_OK.
	"""""""""""""""
    p_payload = 0

    status = raw[p_payload:(p_payload+2*1)]	
    if(status == '00' or status == '01' or status == '09'):
        print("  * Status:", NFC_table.tbl_status_codes.get(status, "RFU"))
    else:
        print("  * Status:", "Forbidden")
    p_payload = p_payload + 2*1
    return p_payload

# 6F 1F
def COLD_RESET_NTF(raw):
    """""""""""""""
		[COLD_RESET_NTF]
    Status:         1 Octet     Status of Cold Reset
	"""""""""""""""
    p_payload = 0

    status = raw[p_payload:(p_payload+2*1)]	
    if(status == '00'):
        print("  * Status:", "successfully done")
    else:
        print("  * Status:", "at least one internal verification failed")
    p_payload = p_payload + 2*1
    return p_payload

# 2F 21
def FLUSH_SRAM_AO_TO_FLASH_CMD(raw):
	"""""""""""""""
		[FLUSH_SRAM_AO_TO_FLASH_CMD]
    (Empty)     Command to save the content of the SRAM Always ON to FLASH.
	"""""""""""""""
	p_payload = 0
	
	print('{0:^25}'.format("(Empty)"))
	# print("")
	return p_payload

# 4F 21
def FLUSH_SRAM_AO_TO_FLASH_RSP(raw):
    """""""""""""""
		[FLUSH_SRAM_AO_TO_FLASH_RSP]
    Status:         1 Octet     The NFCC writes the SRAM Always On content into flash if 
                                content of both areas is different. Then it returns STATUS_OK.
	"""""""""""""""
    p_payload = 0

    status = raw[p_payload:(p_payload+2*1)]	
    if(status == '00' or status == '01' or status == '09' or status == '06'):
        print("  * Status:", NFC_table.tbl_status_codes.get(status, "RFU"))
    else:
        print("  * Status:", "Forbidden")
    p_payload = p_payload + 2*1
    return p_payload

# 2F 30
def TEST_PRBS_CMD(raw):
    """""""""""""""
        [TEST_PRBS_CMD]
    PRBS Mode:              1 Octet
    PRBS type:              1 Octet
    Technology to stream:   1 Octet
    Bitrate:                1 Octet
    PRBS series length:     2 Octets
    """""""""""""""
    p_payload = 0

    prbs_mode = raw[p_payload:(p_payload+2*1)]
    if(prbs_mode == '00'):
        print("  * PRBS Mode:", "Firmware generated PRBS")
    elif(prbs_mode == '01'):
        print("  * PRBS Mode:", "Firmware generated PRBS")
    else:
        print("  * PRBS Mode:", "RFU")
    p_payload = p_payload + 2*1
    
    prbs_type = raw[p_payload:(p_payload+2*1)]
    if(prbs_type == '00'):
        print("  * PRBS Type:", "PRBS9 when Hardware generated PRBS selected")
    elif(prbs_type == '01'):
        print("  * PRBS Type:", "PRBS15 when Hardware generated PRBS selected")
    else:
        print("  * PRBS Type:", "Ignored when Firmware generated PRBS is selected")
    p_payload = p_payload + 2*1
    
    tech = raw[p_payload:(p_payload+2*1)]
    if(tech == '00'):
        print("  * Technology to stream:", "Type A")
    elif(tech == '01'):
        print("  * Technology to stream:", "Type B")
    elif(tech == '02'):
        print("  * Technology to stream:", "Type F")
    elif(tech == '03'):
        print("  * Technology to stream:", "Type V")
    else:
        print("  * Technology to stream:", "RFU")
    p_payload = p_payload + 2*1
    
    br = raw[p_payload:(p_payload+2*1)]
    if(br == '00' or br == '01' or br == '02' or br == '03'):
        print("  * Bitrate:", NFC_table.tbl_bit_rates.get(br))
    elif(br == '04'):
        print("  * Bitrate:", "26 Kbit/s")
    else:
        print("  * Bitrate:", "RFU")
    p_payload = p_payload + 2*1
    
    prbs_srs = raw[p_payload:(p_payload+2*2)]
    # if(prbs_mode == '00' or prbs_mode == '01'):
    print("  * PRBS series length:", prbs_srs)
    p_payload = p_payload + 2*2
    
# 4F 30
def TEST_PRBS_RSP(raw):
    """""""""""""""
		[TEST_PRBS_RSP]
    Status:         1 Octet
	"""""""""""""""
    p_payload = 0

    status = raw[p_payload:(p_payload+2*1)]	
    if(status == '00' or status == '05' or status == '06' or status == '09'):
        print("  * Status:", NFC_table.tbl_status_codes.get(status, "RFU"))
    else:
        print("  * Status:", "RFU")
    p_payload = p_payload + 2*1
    return p_payload

# 2F 33
def TEST_PRBS_CARD_CMD(raw):
    """""""""""""""
		[TEST_PRBS_CARD_CMD]
    PRBS Mode:                                   1 Octet
    Test Type:                                   1 Octet
    Pseudo random pattern:  (clock-less mode)    1 Octet
    Fixed Pattern:          (clock mode)         16 Octets
	"""""""""""""""

# 2F 3E
def TEST_SWP_CMD(raw):
    """""""""""""""
        [TEST_SWP_CMD]
    Link Identifer:     1 Octet
    """""""""""""""
    p_payload = 0

    link_id = raw[p_payload:(p_payload+2*1)]	
    if(link_id == '00'):
        print("  * Link ID:", "NFC_SIM_SWIO1 (UICC1)")
    elif(link_id == '01'):
        print("  * Link ID:", "Mailbox (eSE)")
    elif(link_id == '02'):
        print("  * Link ID:", "NFC_SIM_SWIO2 (UICC2)")
    else:
        print("  * Link ID:", "Forbidden")
    p_payload = p_payload + 2*1
    return p_payload

# 4F 3E
def TEST_SWP_RSP(raw):
    """""""""""""""
		[TEST_SWP_RSP]
    Status:         1 Octet     
	"""""""""""""""
    p_payload = 0

    status = raw[p_payload:(p_payload+2*1)]	
    if(status == '00' or status == '05'):
        print("  * Status:", NFC_table.tbl_status_codes.get(status, "RFU"))
    else:
        print("  * Status:", "Forbidden")
    p_payload = p_payload + 2*1
    return p_payload

# 6F 3E
def TEST_SWP_NTF(raw):
    """""""""""""""
		[TEST_SWP_NTF]
    Status:         1 Octet     
    Power Mode:     1 Octet    
	"""""""""""""""
    p_payload = 0

    status = raw[p_payload:(p_payload+2*1)]	
    if(status == '00' or status == '03'):
        print("  * Status:", NFC_table.tbl_status_codes.get(status, "RFU"))
    else:
        print("  * Status:", "Forbidden")
    p_payload = p_payload + 2*1

    pwr_mode = raw[p_payload:(p_payload+2*1)]
    if(pwr_mode == '00'):
        print("  * Power Mode:", "No SIMVCC")
    elif(pwr_mode == '01'):
        print("  * Power Mode:", "SIMVCC = 1.8V")
    elif(pwr_mode == '02'):
        print("  * Power Mode:", "SIMVCC = 3.3V")
    elif(pwr_mode == '03'):
        print("  * Power Mode:", "SIMVCC undetermined")
    else:
        print("  * Power Mode:", "RFU")

    return p_payload