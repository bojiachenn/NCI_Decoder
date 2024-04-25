import Nxp_pkg.__table__ as NFC_table

# Table 13. SN2x0 NFCC-NCI additional commands/notifications

PWR_MODE_00 = '0'
TEST_ID_3F = '32'
DPC_TYPE = '02'
AST_LOOP = '00'

# 2F 00
def CORE_SET_POWER_MODE_CMD(raw):
    """""""""""""""
		[CORE_SET_POWER_MODE_CMD]
    Mode:       1 Octet     Command to request the SN2x0 NFCC to enable/disable
                            the Standby State
	"""""""""""""""
    # print("  << CORE_SET_POWER_MODE_CMD >>  ")
    p_payload = 0
    
    global PWR_MODE_00
    PWR_MODE_00 = raw[p_payload:(p_payload+2*1)]	
    if(PWR_MODE_00 == '00'):
        print("  * Mode:", "Standby State disabled")
    elif(PWR_MODE_00 == '01'):
        print("  * Mode:", "Standby State enabled")
    elif(PWR_MODE_00 == '02'):
        print("  * Mode:", "Autonomous Mode enabled")
    elif(PWR_MODE_00 == '03'):
        print("  * Mode:", "ULPDET State enabled")
    elif(PWR_MODE_00 == '04'):
        print("  * Mode:", "Autonomous Mode enabled with Poll")
    elif(PWR_MODE_00 == '05'):
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
    # print("  << CORE_SET_POWER_MODE_RSP >>  ")
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
    # print("  << SET_NFC_SERVICE_STATUS_CMD >>  ")
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
    # print("  << SET_NFC_SERVICE_STATUS_RSP >>  ")
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
    # print("  << NCI_PROPRIETARY_ACT_CMD >>  ")
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
    # print("  << NCI_PROPRIETARY_ACT_RSP >>  ")
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
		[APDU_LOGGING_NTF]
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
    # print("  << APDU_LOGGING_NTF >>  ")
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
    # print("  << RF_GET_TRANSITION_CMD >>  ")
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
    # print("  << RF_GET_TRANSITION_RSP >>  ")
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
    # print("  << WTX_NTF >>  ")
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
    # print("  << LOW_POWER_TAG_REMOVAL_CMD >>  ")
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
    # print("  << LOW_POWER_TAG_REMOVAL_RSP >>  ")
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
    # print("  << LOW_POWER_TAG_REMOVAL_NTF >>  ")
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
    # print("  << SYSTEM_ESE_POWER_CYCLE_CMD >>  ")
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
    # print("  << SYSTEM_ESE_POWER_CYCLE_RSP >>  ")
    p_payload = 0

    status = raw[p_payload:(p_payload+2*1)]	
    if(status == '00' or status == '01' or status == '09'):
        print("  * Status:", NFC_table.tbl_status_codes.get(status, "RFU"))
    else:
        print("  * Status:", "Forbidden")
    p_payload = p_payload + 2*1
    return p_payload

# 2F 1F
def COLD_RESET_CMD(raw):
    """""""""""""""
		[COLD_RESET_CMD]
    RESET by pin:         1 Octet
	"""""""""""""""
    # print("  << COLD_RESET_CMD >>  ")
    p_payload = 0

    rst_pin = raw[p_payload:(p_payload+2*1)]
    print("  * RESET by pin:", "SE reset "+NFC_table.tbl_general_status_n(rst_pin))
    p_payload = p_payload + 2*1
    return p_payload

# 4F 1F
def COLD_RESET_RSP(raw):
    """""""""""""""
		[COLD_RESET_RSP]
    Status:         1 Octet     Status of Cold Reset
	"""""""""""""""
    # print("  << COLD_RESET_RSP >>  ")
    p_payload = 0

    status = raw[p_payload:(p_payload+2*1)]	
    print("  * Status:", NFC_table.tbl_status_codes.get(status, "RFU"))
    p_payload = p_payload + 2*1
    return p_payload

# 6F 1F
def COLD_RESET_NTF(raw):
    """""""""""""""
		[COLD_RESET_NTF]
    Status:         1 Octet     Status of Cold Reset
	"""""""""""""""
    # print("  << COLD_RESET_NTF >>  ")
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
    # print("  << FLUSH_SRAM_AO_TO_FLASH_CMD >>  ")
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
    # print("  << FLUSH_SRAM_AO_TO_FLASH_RSP >>  ")
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
    # print("  << TEST_PRBS_CMD >>  ")
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
    # print("  << TEST_PRBS_RSP >>  ")
    p_payload = 0

    status = raw[p_payload:(p_payload+2*1)]	
    if(status == '00' or status == '05' or status == '06' or status == '09'):
        print("  * Status:", NFC_table.tbl_status_codes.get(status, "RFU"))
    else:
        print("  * Status:", "RFU")
    p_payload = p_payload + 2*1
    return p_payload

# 2F 32
def READ_OPTION_CMD(raw):
    """""""""""""""
		[READ_TXLDO_CURRENT_CMD]        |       [READ_RSSI_CMD]                 |       [RF_TEST_API_CMD]
    Test ID:            1 Octet (0x08)  |   Test ID:            1 Octet (0x20)  |   HW Regi:      1 Octet
    Wait_Time:          1 Octet         |   Wait_Time:          1 Octet         |   
	"""""""""""""""
    p_payload = 0

    if(AST_LOOP == '01'):
        print("  << READ_TXLDO_CURRENT_CMD >>  ")
        print("  * Test ID:", "Read TxLdo current", "("+raw[p_payload:(p_payload+2*1)]+")")
        p_payload = p_payload + 2*1

        print("  * Wait_Time:", int(raw[p_payload:(p_payload+2*1)], 16), "µs")
        p_payload = p_payload + 2*1
    
    elif(AST_LOOP == '02'):
        print("  << READ_RSSI_CMD >>  ")
        print("  * Test ID:", "Read RSSI Command", "("+raw[p_payload:(p_payload+2*1)]+")")
        p_payload = p_payload + 2*1

        print("  * Wait_Time:", int(raw[p_payload:(p_payload+2*1)], 16), "µs")
        p_payload = p_payload + 2*1

    elif(AST_LOOP == '00'):
        print("  << RF_TEST_API_CMD >>  ")
        tbl_hw_regi = {'08': 'GPADC_SENSOR_TXLDO_CURRENT', '0C': 'GPADC_SENSOR_RSSI', '0D': 'GPADC_SENSOR_VDDPA', }
        print("  * HW Regi:", tbl_hw_regi.get(raw[p_payload:(p_payload+2*1)], 'RFU'))
        p_payload = p_payload + 2*1

    return p_payload

# 4F 32
def READ_OPTION_RSP(raw):
    """""""""""""""
		[READ_TXLDO_CURRENT_RSP]        |   	[READ_RSSI_RSP]             |       [RF_TEST_API_RSP]
    Status:             1 Octet         |   Status:             1 Octet     |   Status:             1 Octet
    TXLDO_CURRENT:      2 Octets        |   RSSI_VALUE:         4 Octets    |   HW Regi Val:        2 Octets
                                        |   Interpolated RSSI:  4 Octets    |   
	"""""""""""""""
    p_payload = 0
    
    if(AST_LOOP == '01'):
        print("  << READ_TXLDO_CURRENT_RSP >>  ")
        print("  * Status:", NFC_table.tbl_status_codes.get(raw[p_payload:(p_payload+2*1)], "RFU"))
        p_payload = p_payload + 2*1

        print("  * TXLDO_CURRENT:", int(raw[p_payload:(p_payload+2*1)]) + int(raw[(p_payload+2*1):(p_payload+2*2)]) * 256, "mA")
        p_payload = p_payload + 2*2

    elif(AST_LOOP == '02'):
        print("  << READ_RSSI_RSP >>  ")
        print("  * Status:", NFC_table.tbl_status_codes.get(raw[p_payload:(p_payload+2*1)], "RFU"))
        p_payload = p_payload + 2*1

        p_payload = p_payload + 2*2

        print("  * RSSI_VALUE:", raw[p_payload:(p_payload+2*4)])
        p_payload = p_payload + 2*4
        
        print("  * Interpolated RSSI:", raw[p_payload:(p_payload+2*4)])
        p_payload = p_payload + 2*4

    elif(AST_LOOP == '00'):
        print("  << RF_TEST_API_RSP >>  ")
        print("  * Status:", NFC_table.tbl_status_codes.get(raw[p_payload:(p_payload+2*1)], "RFU"))
        p_payload = p_payload + 2*1
        
        print("  * HW Regi Val:", raw[p_payload:(p_payload+2*2)])
        p_payload = p_payload + 2*2

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
    # print("  << TEST_PRBS_CARD_CMD >>  ")
    p_payload = 0

    prbs_mode = raw[p_payload:(p_payload+2*1)]
    tbl_prbs_mode = {'00': 'Start PRBS Card Mode', '01': 'Stop PRBS Card Mode'}
    print("  * PRBS Mode:", tbl_prbs_mode.get(prbs_mode, 'RFU'))
    p_payload = p_payload + 2*1

    if(prbs_mode == '00'):
        tbl_tech = {'00': 'Type A', '01': 'Type B', '10': 'Type F',}
        tbl_bitrate = {'00': '106k', '01': '212k', '10': '424k', '11': '848k', }
        test_type = raw[p_payload:(p_payload+2*1)]
        test_type_b = bin(int(test_type, 16))[2::].zfill(8)
        print("  * Test Type:", test_type_b, "("+test_type+")")
        sys_clk_status = NFC_table.tbl_general_status.get('0'+test_type_b[2:3])
        clk_less_status = NFC_table.tbl_general_status.get('0'+test_type_b[3:4])
        print("   ~ {:<20}".format("Sys clk platform:"), sys_clk_status)
        print("   ~ {:<20}".format("Clk-less platform:"), clk_less_status)
        print("   ~ {:<20}".format("Technology:"), tbl_tech.get(test_type_b[4:6]))
        print("   ~ {:<20}".format("Bit Rate:"), tbl_bitrate.get(test_type_b[6:8]))
        p_payload = p_payload + 2*1

        if(clk_less_status == 'Enabled '):
            print("  * Pseudo random pattern:", raw[p_payload:(p_payload+2*1)])
            p_payload = p_payload + 2*1
        if(sys_clk_status == 'Enabled '):
            fixed_pattern = raw[p_payload:(p_payload+2*16)]
            pairs = [fixed_pattern[i:i+2] for i in range(0, len(fixed_pattern), 2)]
            pattern = ' '.join(['0x' + pair.upper() for pair in pairs])
            print("  Fixed Pattern:", pattern)
            p_payload = p_payload + 2*16

    return p_payload

# 4F 33
def TEST_PRBS_CARD_RSP(raw):
    """""""""""""""
		[TEST_PRBS_CARD_RSP]
    Status:         1 Octet
	"""""""""""""""
    # print("  << TEST_PRBS_CARD_RSP >>  ")
    p_payload = 0

    status = raw[p_payload:(p_payload+2*1)]	
    print("  * Status:", NFC_table.tbl_status_codes.get(status, "RFU"))
    p_payload = p_payload + 2*1

    return p_payload

# 6F 35
def L1_DEBUG_NTF(raw):
    """""""""""""""
		[L1_DEBUG_NTF]
    Major_Time_Stamp:   2 Octets
    Minor_Time_Stamp:   2 Octets
    RSSI or DLMA:       2 or 4 Octets
    CLIF State:         1 Octet
    Extra Debug data    1 Octet (optional)
	"""""""""""""""
    # print("  << L1_DEBUG_NTF >>  ") 
    tbl_tech_mode = {
        '0': 'Not detected yet',
        '1': 'Card Emulation NFC-A',
        '2': 'Card Emulation NFC-B',
        '3': 'Card Emulation NFC-F',
        '8': 'Reader mode NFC-A',
        '9': 'Reader mode NFC-B',
        'A': 'Reader mode NFC-F',
        'F': 'Reader mode NFC-V',
    }
    tbl_TTC_1 = {
        '1': 'ACTIVATED',
        '2': 'DATA_RX',
        '3': 'RX_DESELECT',
        '4': 'RX_WTX',
        '5': 'ERROR',
        '6': 'RX_ACK',
        '7': 'RX_NAK',
        '8': 'DATA_TX',
        'A': 'TX_DESELECT',
        'B': 'TX_WTX',
        'C': 'TX_ACK',
        'D': 'TX_NAK',
        'E': 'EXTENDED',
    }
    tbl_TTC_2 = {
        '1': 'ACTIVATED',
        '2': 'DATA_RX',
        '3': 'RX_READ',
        '4': 'RX_WRITE',
        '5': 'ERROR',
        '6': 'DATA_TX',
        '7': 'TX_READ',
        '8': 'TX_WRITE',
    }
    tbl_TTC_3 = {
        '2': 'DATA_RX',
        '8': 'DATA_TX',
    }

    p_payload = 0
    major_time = int(raw[(p_payload+2*1):(p_payload+2*2)] + raw[p_payload:(p_payload+2*1)], 16)
    p_payload = p_payload + 2*2
    minor_time = int(raw[(p_payload+2*1):(p_payload+2*2)] + raw[p_payload:(p_payload+2*1)], 16)
    p_payload = p_payload + 2*2
    print("  * Time:", major_time, "ms", minor_time, "µs")
   
    val_len = len(raw[p_payload:])
    if(val_len == 3 or val_len == 4): # non-TX event
        rssi = raw[p_payload:(p_payload+2*2)]
        p_payload = p_payload + 2*2
        print("  * RSSI:", rssi, "(MSB)")

    elif(val_len == 5 or val_len == 6): # TX event
        dlma = raw[p_payload:(p_payload+2*4)]
        p_payload = p_payload + 2*4
        print("  * DLMA:", dlma, "(LSB)")

    clif_state = raw[p_payload:(p_payload+2*1)]
    print("  * CLIF State:", clif_state)
    print("    * Tech & Mode:", tbl_tech_mode.get(clif_state[0:1], 'RFU'))
    p_payload = p_payload + 2*1

    if(clif_state[0:1] != '0' and clif_state[0:1] != '3'):
        if(clif_state[0:1] == '1' or clif_state[0:1] == '2' or clif_state[0:1] == '8' or clif_state[0:1] == '9'):
            print("    * Trigger Type:", tbl_TTC_1.get(clif_state[1:2], 'RFU'))
        elif(clif_state[0:1] == 'A'):
            print("    * Trigger Type:", tbl_TTC_2.get(clif_state[1:2], 'RFU'))
        elif(clif_state[0:1] == 'F'):
            print("    * Trigger Type:", tbl_TTC_3.get(clif_state[1:2], 'RFU'))
    
    if(val_len == 4 or val_len == 6):
        print("  * Extra Debug data:", raw[p_payload:(p_payload+2*1)])
        p_payload = p_payload + 2*1

    return p_payload

# 6F 36
def L2_DEBUG_NTF(raw):
    """""""""""""""
		[L2_DEBUG_NTF]
    Tag:                4 Bits
    Length:             4 Bits
    Major_Time_Stamp:   2 Octets
    Minor_Time_Stamp:   2 Octets
    RSSI or DLMA:       2 or 4 Octets 
    CLIF State:         1 Octet              |   FeliCa CMD:   1 Octet   |          FeliCa CMD:     2 Octets
    Extra Debug data    1 Octet (optional)   |                           |          
	"""""""""""""""
    # print("  << L2_DEBUG_NTF >>  ") 
    tbl_tag = {
        '1': 'L2 EVENT',
        '2': 'FELICA CMD',
        '3': 'FELICA SYSTEM CODE',
        '4': 'FELICA RSP',
        '5': 'MISC',
        'A': 'CMA',
    }
    tbl_tech_mode = {
        '1': 'Card Emulation NFC-A',
        '2': 'Card Emulation NFC-B',
        '3': 'Card Emulation NFC-F',
        '8': 'Reader mode NFC-A',
        '9': 'Reader mode NFC-B',
        'A': 'Reader mode NFC-F',
        'F': 'Reader mode NFC-V',
    }
    tbl_TTC_1 = {
        '1': 'MODULATION_DETECTED',
        '2': 'DATA_RX',
        '3': 'TIMEOUT/RSSI',
        '4': 'ACTIVE_ISO14443_3',
        '5': 'ERROR',
        '6': 'SENSING',
        '7': 'ACTIVE_ISO14443_4',
        '8': 'RF_ON',
        '9': 'RF_OFF',
        'A': 'DATA_TX',
        'C': 'LPCD_WUP',
    }
    tbl_TTC_2 = {
        '1': 'SLPV_REQ',
        '2': 'INVENTORY_RESP',
        '6': 'INVENTORY_REQ_1_SLOT',
        '7': 'ACTIVATION',
        'A': 'INVENTORY_REQ_16_SLOT',
    }
    tbl_misc_event = {
        '01': 'GENERIC ERROR',
        '02': 'FELICA CM: EMPTY FRAME FROM ESE',
        '03': 'L2 NTF BUFFER OVERFLOW',
        '05': 'FELICA CM: RF ERROR',
    }
    tbl_TT_cma = {
        '03': 'CLT_CMD',
        '04': 'CLT_DATA_RX',
        '05': 'CLT_DATA_TX',
        '06': 'RATS_RECEIVED',
        '07': 'ATQA_SENT',
        '08': 'UID_SENT',
        '0A': 'ATS_SENT',
        '0B': 'HLTA_DETECTED',
        '0C': 'ERROR',
        '0D': 'EMD_DETECTED',
    }

    p_payload = 0

    tag = raw[p_payload:(p_payload+1)]
    print("  * Tag:", tbl_tag.get(tag, 'RFU'))
    p_payload = p_payload + 1

    length = int(raw[p_payload:(p_payload+1)], 16)
    p_payload = p_payload + 1
    
    major_time = int(raw[(p_payload+2*1):(p_payload+2*2)] + raw[p_payload:(p_payload+2*1)], 16)
    p_payload = p_payload + 2*2
    minor_time = int(raw[(p_payload+2*1):(p_payload+2*2)] + raw[p_payload:(p_payload+2*1)], 16)
    p_payload = p_payload + 2*2
    print("  * Time:", major_time, "ms", minor_time, "µs")

    if(tag == '1'): # L2 event
        if(length == 7 or length == 8): # non-TX event
            rssi = raw[p_payload:(p_payload+2*2)]
            p_payload = p_payload + 2*2
            print("  * RSSI:", rssi, "(MSB)")

        elif(length == 9 or length == 10): # TX event
            dlma = raw[p_payload:(p_payload+2*4)]
            p_payload = p_payload + 2*4
            print("  * DLMA:", dlma, "(LSB)")

        clif_state = raw[p_payload:(p_payload+2*1)]
        print("  * CLIF State:", clif_state)
        print("    * Tech & Mode:", tbl_tech_mode.get(clif_state[0:1], 'RFU'))
        p_payload = p_payload + 2*1

        if(clif_state[0:1] != '0' and clif_state[0:1] != '3'):
            if(clif_state[0:1] == '1' or clif_state[0:1] == '2' or clif_state[0:1] == '8' or clif_state[0:1] == '9' or clif_state[0:1] == 'A'):
                print("    * Trigger Type:", tbl_TTC_1.get(clif_state[1:2], 'RFU'))
            elif(clif_state[0:1] == 'F'):
                print("    * Trigger Type:", tbl_TTC_2.get(clif_state[1:2], 'RFU'))

        if(length == 8 or length == 10):
            print("  * Extra data info:", raw[p_payload:(p_payload+2*1)])
            p_payload = p_payload + 2*1

    elif(tag == '2'): # FELICA CMD
        rssi = raw[p_payload:(p_payload+2*2)]
        p_payload = p_payload + 2*2
        print("  * RSSI:", rssi, "(MSB)")

        f_cmd = raw[p_payload:(p_payload+2*1)]
        p_payload = p_payload + 2*1
        print("  * FeliCa CMD:", f_cmd)
        
        if(length == 8):
            print("  * Extra data info:", raw[p_payload:(p_payload+2*1)])
            p_payload = p_payload + 2*1

    elif(tag == '3'): # FELICA SYSTEM CODE
        f_cmd = raw[p_payload:(p_payload+2*2)]
        p_payload = p_payload + 2*2
        print("  * FeliCa CMD:", f_cmd)

    elif(tag == '4'): # FELICA RSP
        dlma = raw[p_payload:(p_payload+2*4)]
        p_payload = p_payload + 2*4
        print("  * DLMA:", dlma, "(LSB)")

        f_rsp = raw[p_payload:(p_payload+2*1)]
        p_payload = p_payload + 2*1
        print("  * FeliCa RSP:", f_rsp)

        rsp_flag = raw[p_payload:(p_payload+2*2)]
        p_payload = p_payload + 2*2
        print("  * RSP status flag:", rsp_flag)

        if(length == 12):
            print("  * Extra data info:", raw[p_payload:(p_payload+2*1)])
            p_payload = p_payload + 2*1

    elif(tag == '5'): # MISC
        misc_event = raw[p_payload:(p_payload+2*1)]
        p_payload = p_payload + 2*1
        print("  * Misc Event trig:", tbl_misc_event.get(misc_event, 'RFU'))

        if(length == 6):
            print("  * Extra data info:", raw[p_payload:(p_payload+2*1)])
            p_payload = p_payload + 2*1
            
    elif(tag == 'A'): # CMA
        trig_type = raw[p_payload:(p_payload+2*1)]
        p_payload = p_payload + 2*1
        print("  * Trig type:", tbl_TT_cma.get(trig_type, 'RFU'))

        if(length > 5):
            print("  * Extra data info:", raw[p_payload:])
            if(trig_type == '03'):
                if(raw[p_payload:(p_payload+2*1)] == '08'):
                    print("    * Type: CLT_IDLE (08)")
                elif(raw[p_payload:(p_payload+2*1)] == '09'):
                    print("    * Type: CLT_HALT (09)")
                p_payload = p_payload + 2*1

            elif(trig_type == '04'):
                rx_len = int(raw[p_payload:(p_payload+2*1)], 16)
                p_payload = p_payload + 2*1
                rx_len = rx_len if rx_len < 9 else 9
                clt_rx = raw[p_payload:(p_payload+2*rx_len)]
                p_payload = p_payload + 2*rx_len
                print("    * CLT RX Data:", clt_rx)

            elif(trig_type == '05'):
                tx_len = int(raw[p_payload:(p_payload+2*1)], 16)
                p_payload = p_payload + 2*1
                tx_len = tx_len if tx_len < 9 else 9
                clt_tx = raw[p_payload:(p_payload+2*tx_len)]
                p_payload = p_payload + 2*tx_len
                print("    * CLT TX Data:", clt_tx)

            elif(trig_type == '06'):
                rats = raw[p_payload:(p_payload+2*2)]
                p_payload = p_payload + 2*2
                print("    * RATS received:", rats)

            elif(trig_type == '07'):
                t = raw[p_payload:(p_payload+2*1)]
                p_payload = p_payload + 2*1
                if(t == '26'):
                    print("    * Type: REQA (26)")
                elif(t == '52'):
                    print("    * Type: WUPA (52)")
                print("    * ATQA sent:", raw[p_payload:(p_payload+2*2)])
                p_payload = p_payload + 2*2

            elif(trig_type == '08'):
                anticollision_lv = raw[p_payload:(p_payload+2*1)]
                p_payload = p_payload + 2*1
                print("    * Anti-Collision Lv:", anticollision_lv)

            elif(trig_type == '0A'):
                apc = raw[p_payload:(p_payload+2*4)]
                p_payload = p_payload + 2*4
                print("    * APC:", apc)
                ats = raw[p_payload:(p_payload+2*5)]
                p_payload = p_payload + 2*5
                print("    * ATS sent:", ats)

            elif(trig_type == '0B'):
                hlta = raw[p_payload:(p_payload+2*2)]
                p_payload = p_payload + 2*2
                print("    * HLTA received:", hlta)
                
            elif(trig_type == '0C'):
                data_len = int(raw[(p_payload+2*1):(p_payload+2*2)] + raw[p_payload:(p_payload+2*1)], 16)
                p_payload = p_payload + 2*2
                data_len = data_len if data_len < 8 else 8
                data = raw[p_payload:(p_payload+2*data_len)]
                p_payload = p_payload + 2*data_len
                print("    * Data received:", data)

    return p_payload

# 2F 3D
def RF_SPC_CMD(raw):
    """""""""""""""
        [RF_SPC_CMD]
    SPC Config:     1 Octet
    """""""""""""""
    # print("  << RF_SPC_CMD >>  ")
    p_payload = 0

    tbl_spc_cfg = {'30': 'Configure NFCC for SPC', '31': 'Start SPC algorithm'}
    spc_cfg = raw[p_payload:(p_payload+2*1)]
    print("  * SPC Cfg:", tbl_spc_cfg.get(spc_cfg, 'RFU'))
    p_payload = p_payload + 2*1
    
    if(spc_cfg == '30'):
        block_nb = raw[p_payload:(p_payload+2*1)]
        print("  * Block Nb:", block_nb)
        p_payload = p_payload + 2*1

        content = raw[p_payload:]
        if(block_nb == '00'):
            print("  * Algo settings:", content)
        else:
            print("  * PLL settings:", content)
        p_payload = p_payload + len(content)

    return p_payload    

# 4F 3D
def RF_SPC_RSP(raw):
    """""""""""""""
        [RF_SPC_RSP]
    Status:         1 Octet
    """""""""""""""
    # print("  << RF_SPC_RSP >>  ")
    p_payload = 0

    status = raw[p_payload:(p_payload+2*1)]	
    print("  * Status:", NFC_table.tbl_status_codes.get(status, "RFU"))
    p_payload = p_payload + 2*1

    return p_payload    
    
# 6F 3D
def RF_SPC_NTF(raw):
    """""""""""""""
        [RF_SPC_NTF]
    Status:                 1 Octet
    IndexStart:             1 Octet
    IndexEnd:               1 Octet
    RSSI:                   2 Octets
    CustomerPhaseTrim:      2 Octets
    """""""""""""""
    # print("  << RF_SPC_NTF >>  ")
    p_payload = 0

    status = raw[p_payload:(p_payload+2*1)]	
    tbl_spc_status = {
        '00': 'SPC_STATUS_OK (OK, phase offset updated)',
        '01': 'SPC_STATUS_RX_PROTECTION (NOK)',
        '02': 'SPC_STATUS_OVERCURRENT (NOK)',
        '04': 'SPC_STATUS_OVERCURRENT_DISCARD (OK, phase offset updated)',
        '08': 'SPC_STATUS_RSSITHRESH_DISCARD',
        'F0': 'RFU',
    }
    print("  * Status:", tbl_spc_status.get(status))
    p_payload = p_payload + 2*1

    print("  * IndexStart:", int(raw[p_payload:(p_payload+2*1)], 16), "("+raw[p_payload:(p_payload+2*1)]+")")
    p_payload = p_payload + 2*1

    print("  * IndexEnd:", int(raw[p_payload:(p_payload+2*1)], 16), "("+raw[p_payload:(p_payload+2*1)]+")")
    p_payload = p_payload + 2*1
    
    print("  * RSSI:", int(raw[p_payload:(p_payload+2*1)], 16) + int(raw[(p_payload+2*1):(p_payload+2*2)], 16) * 256)
    p_payload = p_payload + 2*2
    

    phase = int(raw[(p_payload+2*1):(p_payload+2*2)] + raw[p_payload:(p_payload+2*1)])
    if phase & 0x8000:
        phase = -((phase ^ 0xFFFF) + 1)
    degrees = phase * 0.25
    print("  * Phase:", degrees, "°")
    p_payload = p_payload + 2*2

    return p_payload    

# 2F 3E
def TEST_SWP_CMD(raw):
    """""""""""""""
        [TEST_SWP_CMD]
    Link Identifer:     1 Octet
    """""""""""""""
    # print("  << TEST_SWP_CMD >>  ")
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
    # print("  << TEST_SWP_RSP >>  ")
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
    # print("  << TEST_SWP_NTF >>  ")
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

# 2F 3F
def OPTIONAL_CMD(raw):
    """""""""""""""
		[AST_UTILITY_CMD]          |        [DPC_HELPER_ACT_CMD]       |        [DPC_HELPER_CMD]           |        [SWITCH_RF_FIELD_CMD]
    Param 1:        1 Octet (0x70) |    Test ID:        1 Octet (0x04) |    Test ID:        1 Octet (0x05) |    Test ID:        1 Octet (0x32)
    Param 2:        1 Octet        |    Reserved:       1 Octet (RFU)  |    Reserved:       1 Octet (RFU)  |    Field Type:     1 Octet
    Input:          1 Octet        |    Reserved:       1 Octet (RFU)  |    Reserved:       1 Octet (RFU)  |    Reserved:       1 Octet (RFU)
	"""""""""""""""
    p_payload = 0

    global TEST_ID_3F
    TEST_ID_3F = raw[p_payload:(p_payload+2*1)]
    if(TEST_ID_3F == '70'):
        print("  << AST_UTILITY_CMD >>  ")
        print("  * Param 1:", "Antenna Self-Test utility APIs")
        p_payload = p_payload + 2*1

        tbl_ast_param2 = {
            '02': 'FORCE_DPC_OFF_CMD',
            '01': 'FORCE_NEW_VDDPA_CMD',
            '00': 'READ_VDDPA_CODE_CMD',
            }
        global DPC_TYPE
        DPC_TYPE = raw[p_payload:(p_payload+2*1)]
        print("  * Param 2:", tbl_ast_param2.get(DPC_TYPE, 'RFU'))
        p_payload = p_payload + 2*1

        print("  * Input:", raw[p_payload:(p_payload+2*1)])
        p_payload = p_payload + 2*1
    
    elif(TEST_ID_3F == "04"):
        print("  << DPC_HELPER_ACT_CMD >>  ")
        print("  * Test ID:", "ENABLE DPC HELPER")
        p_payload = p_payload + 2*3
        
    elif(TEST_ID_3F == "05"):
        print("  << DPC_HELPER_CMD >>  ")
        print("  * Test ID:", "READ DPC HELPER DATA")
        p_payload = p_payload + 2*3
        
    elif(TEST_ID_3F == "32"):
        print("  << SWITCH_RF_FIELD_CMD >>  ")
        print("  * Test ID:", "Switch RF Field On/Off")
        p_payload = p_payload + 2*1

        tbl_field_type = {
            '00': 'Field Off',
            '01': 'Field On AST1',
            '02': 'Field On AST2',
            }
        print("  * Field Type:", tbl_field_type.get(raw[p_payload:(p_payload+2*1)], 'RFU'))
        p_payload = p_payload + 2*2
    return p_payload

# 4F 3F
def OPTIONAL_RSP(raw):
    """""""""""""""
		[AST_UTILITY_RSP]          |        [DPC_HELPER_ACT_RSP]       |        [DPC_HELPER_RSP]               |        [SWITCH_RF_FIELD_RSP]
    Status:             1 Octet    |    Test ID:        1 Octet (0x04) |    Status:             1 Octet        |    Status:        1 Octet
        or                         |    Reserved:       1 Octet (RFU)  |    DPC Info:           x Octet(s)     |
    VDDPA voltage code: 1 Octet    |    Reserved:       1 Octet (RFU)  |                                       |
	"""""""""""""""
    p_payload = 0

    if(TEST_ID_3F == '70'):
        print("  << AST_UTILITY_RSP >>  ")
        if(DPC_TYPE == '02' or DPC_TYPE == '01'):
            print("  * Status:", NFC_table.tbl_status_codes.get(raw[p_payload:(p_payload+2*1)], "RFU"))
        elif(DPC_TYPE == '00'):
            print("  * VDDPA:", 1.5 + int(raw[p_payload:(p_payload+2*1)]) * 0.05, "V")
        p_payload = p_payload + 2*1
    
    elif(TEST_ID_3F == "04"):
        print("  << DPC_HELPER_ACT_RSP >>  ")
        print("  * Test ID:", "ENABLE DPC HELPER")
        p_payload = p_payload + 2*3
        
    elif(TEST_ID_3F == "05"):
        print("  << DPC_HELPER_RSP >>  ")
        # 4F3F 3E 00 0F 36810D000000 37810C000000 37810C000000 37810C000000 36810D000000 36810D000000 36810D000000 37810C000000 36810D000000 37810C000000
        print("  * Status:", NFC_table.tbl_status_codes.get(raw[p_payload:(p_payload+2*1)], "RFU"))
        p_payload = p_payload + 2*1

        p_payload = p_payload + 2*1 # (0F) 不確定用途

        dpc_info = raw[p_payload:]
        x = len(dpc_info)
        x = int(x / 12)
        print("  * DPC Info:", dpc_info)
        print("   ~  #  ~  Power  ~  VDDPA  ~  Current  ~  NCI cmd  ~")
        for i in range(x):
            info = raw[p_payload:(p_payload+2*6)]
            vddpa = int(info[4:6], 16) * 0.05 + 1.5
            current = int(info[0:2], 16) + int(info[3:4], 16) * 256
            print("    {0:^5} {1:>6.3f} W  {2:>6.2f} V  {3:>6} mA   {4:>9}".format(i, (vddpa*current)/1000, vddpa, current, info[0:6]))
            # print(raw[p_payload:(p_payload+2*6)])
            p_payload = p_payload + 2*6
        
    elif(TEST_ID_3F == "32"):
        print("  << SWITCH_RF_FIELD_RSP >>  ")
        print("  * Status:", NFC_table.tbl_status_codes.get(raw[p_payload:(p_payload+2*1)], "RFU"))
        p_payload = p_payload + 2*1
    return p_payload
