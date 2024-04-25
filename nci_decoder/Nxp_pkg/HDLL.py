# CMD

# F0
def DL_RESET(len, raw, pre_op):
    p_payload = 0
    print("  * HDLL CMD: DL_RESET")
    p_payload = p_payload + 2*3
    # empty
    return p_payload

# F1
def DL_GET_VERSION(len, raw, pre_op):
    p_payload = 0
    p_payload = p_payload + 2*3
    # empty
    print("  * HDLL CMD: DL_GET_VERSION")
    return p_payload

# F2
def DL_GET_SESSION_STATE(len, raw, pre_op):
    p_payload = 0
    p_payload = p_payload + 2*3
    # empty
    print("  * HDLL CMD: DL_GET_SESSION_STATE")
    return p_payload

# F4
def DL_GET_DIE_ID(len, raw, pre_op):
    p_payload = 0
    p_payload = p_payload + 2*3
    # empty
    print("  * HDLL CMD: DL_GET_DIE_ID")
    return p_payload

# E0
def DL_CHECK_INTEGRITY(len, raw, pre_op):
    p_payload = 0
    p_payload = p_payload + 2*3
    # empty
    print("  * HDLL CMD: DL_CHECK_INTEGRITY")
    return p_payload

# C0
def DL_SEC_WRITE(len, raw, pre_op):
    p_payload = 0
    print("  * HDLL CMD: DL_SEC_WRITE")

    if(len == 502): # first
        p_payload = p_payload + 2*1

        print("  * FW version:", raw[p_payload:(p_payload+2*2)])
        p_payload = p_payload + 2*2

        print("  * NONCE:", raw[p_payload:(p_payload+2*16)])
        p_payload = p_payload + 2*16

        print("  * DIEID:", raw[p_payload:(p_payload+2*16)])
        p_payload = p_payload + 2*16

        print("  * CHIPMASK:", raw[p_payload:(p_payload+2*2)])
        p_payload = p_payload + 2*2

        print("  * MASKEDKEY:", raw[p_payload:(p_payload+2*16)])
        p_payload = p_payload + 2*16

        print("  * UDFSEED:", raw[p_payload:(p_payload+2*32)])
        p_payload = p_payload + 2*32

        print("  * HASH:", raw[p_payload:(p_payload+2*32)])
        p_payload = p_payload + 2*32

        print("  * SIGN:", raw[p_payload:(p_payload+2*384)])
        p_payload = p_payload + 2*384

    else: # Middle & Last
        data_size = int(raw[p_payload:(p_payload+2*2)], 16)
        p_payload = p_payload + 2*2
        
        print("  * ADDR:", raw[p_payload:(p_payload+2*3)])
        p_payload = p_payload + 2*3
        
        print("  * DATA:", raw[p_payload:(p_payload+2*data_size)])
        p_payload = p_payload + 2*data_size

        if((len-1) * 2 > p_payload): # Middle
            print("  * HASH:", raw[p_payload:(p_payload+2*32)])
            p_payload = p_payload + 2*32

    return p_payload

# C1
def DL_CERT_FRAME(len, raw, pre_op):
    p_payload = 0
    print("  * HDLL CMD: DL_CERT_FRAME")
    
    p_payload = p_payload + 2*1
    
    print("  * Chip version:", raw[p_payload:(p_payload+2*2)])
    p_payload = p_payload + 2*2
    print("  * Chip Life Cycle:", raw[p_payload:(p_payload+2*2)])
    p_payload = p_payload + 2*2
    print("  * Certificate version:", raw[p_payload:(p_payload+2*2)])
    p_payload = p_payload + 2*2
    
    print("  * PK_MOD:", raw[p_payload:(p_payload+2*384)])
    p_payload = p_payload + 2*384
    print("  * PK_EXP:", raw[p_payload:(p_payload+2*8)])
    p_payload = p_payload + 2*8
    print("  * PK_CRC:", raw[p_payload:(p_payload+2*4)])
    p_payload = p_payload + 2*4
    
    print("  * SIGN:", raw[p_payload:(p_payload+2*384)])    
    p_payload = p_payload + 2*384

    return p_payload

# RSP

# 00
def DL_OK(len, raw, pre_op):
    p_payload = 0
    print("  * HDLL RSP: DL_STATUS_OK")
    if(pre_op == 'F1'):
        print("  * HW version:", raw[p_payload:(p_payload+2*1)])
        p_payload = p_payload + 2*1
        print("  * ROM code:", raw[p_payload:(p_payload+2*1)])
        p_payload = p_payload + 2*1
        print("  * Model ID:", raw[p_payload:(p_payload+2*1)])
        p_payload = p_payload + 2*1
        print("  * FW version:", raw[p_payload:(p_payload+2*2)])
        p_payload = p_payload + 2*2
        print("  * Internal FW build revision:", raw[p_payload:(p_payload+2*4)])
        p_payload = p_payload + 2*4
        print("  * Chip version:", raw[p_payload:(p_payload+2*2)])
        p_payload = p_payload + 2*2
        print("  * Chip Life Cycle:", raw[p_payload:(p_payload+2*2)])
        p_payload = p_payload + 2*2
        print("  * Certificate version:", raw[p_payload:(p_payload+2*2)])
        p_payload = p_payload + 2*2

    elif(pre_op == 'F2'):
        tbl_ssta = {'00': 'closed', '01': 'open', '02': 'locked'}
        print("  * Session State:", tbl_ssta.get(raw[p_payload:(p_payload+2*1)]))
        p_payload = p_payload + 2*3

    elif(pre_op == 'F4'):
        p_payload = p_payload + 2*3
        print("  * DIEID:", raw[p_payload:(p_payload+2*16)])
        p_payload = p_payload + 2*16
        
    elif(pre_op == 'E0'):
        data_num = int(raw[p_payload:(p_payload+2*1)], 16)
        # print("  * Nb of data sections:", data_num, "("+raw[p_payload:(p_payload+2*1)]+")")
        p_payload = p_payload + 2*1
        code_num = int(raw[p_payload:(p_payload+2*1)], 16)
        # print("  * Nb of code sections:", code_num, "("+raw[p_payload:(p_payload+2*1)]+")")
        p_payload = p_payload + 2*2
        check_1to8 = raw[(p_payload+2*3):(p_payload+2*4)]
        print("  * CRC check for sections  1 to  8:", check_1to8)
        check_9to16 = raw[(p_payload+2*2):(p_payload+2*3)]
        print("  *                         9 to 16:", check_9to16)
        check_17to24 = raw[(p_payload+2*1):(p_payload+2*2)]
        print("  *                        17 to 24:", check_17to24)
        check_25to32 = raw[p_payload:(p_payload+2*1)]
        print("  *                        25 to 32:", check_25to32)
        crc_check_status = bin(int(check_1to8, 16))[2::].zfill(8) + bin(int(check_9to16, 16))[2::].zfill(8) + bin(int(check_17to24, 16))[2::].zfill(8) + bin(int(check_25to32, 16))[2::].zfill(8)
        p_payload = p_payload + 2*4
        data = raw[p_payload:(p_payload+2*4*28)] # up to 28 Data sections
        p_payload = p_payload + 2*4*28
        code = raw[p_payload:(p_payload+2*4*4)]
        p_payload = p_payload + 2*4*4
        tbl_status = {'1': 'OK', '0': 'KO'}
        print("  * Flash integrity:")
        print("         Data: {0:>2}               Code: {1:>2}".format(data_num, code_num))
        for i in range(28):
            if(i < data_num and i < code_num):
                print("    {0:>2}   {1:>2} {2}          {3:>2} {4}".format(i+1, tbl_status.get(crc_check_status[i:i+1], ""), "(" + data[8*i+6:8*i+8] + data[8*i+4:8*i+6] + data[8*i+2:8*i+4] + data[8*i+0:8*i+2] + ")", 
                                                                     tbl_status.get(crc_check_status[i+28:i+29], ""), "(" + code[8*i+6:8*i+8] + code[8*i+4:8*i+6] + code[8*i+2:8*i+4] + code[8*i+0:8*i+2] + ")"))
            elif(i < data_num):
                print("    {0:>2}   {1:>2} {2}".format(i+1, tbl_status.get(crc_check_status[i:i+1], ""), "(" + data[8*i+6:8*i+8] + data[8*i+4:8*i+6] + data[8*i+2:8*i+4] + data[8*i+0:8*i+2] + ")"))
    else:
        p_payload = p_payload + 2*3
        # empty
    return p_payload

# 01
def EDL_INVALID_ADDR(len, raw, pre_op):
    p_payload = 0
    p_payload = p_payload + 2*3
    # empty
    return p_payload

# 02
def EDL_GENERIC_ERROR(len, raw, pre_op):
    p_payload = 0
    p_payload = p_payload + 2*3
    # empty
    return p_payload

# 0B
def EDL_UNKNOW_CMD(len, raw, pre_op):
    p_payload = 0
    p_payload = p_payload + 2*3
    # empty
    return p_payload

# 0C
def EDL_ABORTED_CMD(len, raw, pre_op):
    p_payload = 0
    p_payload = p_payload + 2*3
    # empty
    return p_payload

# 1E
def EDL_ADDR_RANGE_OFL_ERROR(len, raw, pre_op):
    p_payload = 0
    p_payload = p_payload + 2*3
    # empty
    return p_payload

# 1F
def EDL_BUFFER_OFL_ERROR(len, raw, pre_op):
    p_payload = 0
    p_payload = p_payload + 2*3
    # empty
    return p_payload

# 20
def EDL_MEM_BSY(len, raw, pre_op):
    p_payload = 0
    p_payload = p_payload + 2*3
    # empty
    return p_payload

# 21
def EDL_SIGNATURE_ERROR(len, raw, pre_op):
    p_payload = 0
    p_payload = p_payload + 2*3
    # empty
    return p_payload

# 24
def EDL_FIRMWARE_VERSION_ERROR(len, raw, pre_op):
    p_payload = 0
    p_payload = p_payload + 2*3
    # empty
    return p_payload

# 28
def EDL_PROTOCOL_ERROR(len, raw, pre_op):
    p_payload = 0
    p_payload = p_payload + 2*3
    # empty
    return p_payload

# 2D
def PH_STATUS_DL_FIRST_CHUNK(len, raw, pre_op):
    p_payload = 0
    p_payload = p_payload + 2*3
    # empty
    return p_payload

# 2E
def PH_STATUS_DL_NEXT_CHUNK(len, raw, pre_op):
    p_payload = 0
    p_payload = p_payload + 2*3
    # empty
    return p_payload

# 31
def PH_STATUS_EDL_CERT_ERROR(len, raw, pre_op):
    p_payload = 0
    p_payload = p_payload + 2*3
    # empty
    return p_payload

