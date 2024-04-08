import nfc_forum_pkg.__table__ as NFC_table

def NCI_PROPRIETARY_ACT_CMD(rawdata):
    p_payload = 0

    status = NFC_table.tbl_status_codes.get(rawdata[p_payload:p_payload+2*1], "Forbidden")
    print("  * Status:", status)
    p_payload = p_payload + 2*1
    return p_payload


def NCI_PROPRIETARY_ACT_RSP(rawdata):
    p_payload = 0

    # payload_len = int(rawdata[p_payload:p_payload+2*1], 16)
    # print("payload len:", payload_len)
    p_payload = p_payload + 2*1

    status = NFC_table.tbl_status_codes.get(rawdata[p_payload:p_payload+2*1], "Forbidden")
    print("  * Status:", status)
    p_payload = p_payload + 2*1

    print("  * FW_Build_Nb:", rawdata[p_payload:p_payload+2*4])
    p_payload = p_payload + 2*4
    return p_payload

tbl_prop_ctrl = {
    "000010":  {"CMD": NCI_PROPRIETARY_ACT_CMD, "RSP": NCI_PROPRIETARY_ACT_RSP}
}

def call_proprietary(len, oid, mt, rawdata):

    function = f"{tbl_prop_ctrl[oid][mt]}"
    function_name = function.split(" ")[1]
    print("   << "+function_name+" >>")
    check = tbl_prop_ctrl[oid][mt](rawdata)
    if(check != 2*(int(len)-2)):
        print("Payload Length:", int(len)-2, "Octet(s)")
        print("Error: Payload error!!")
