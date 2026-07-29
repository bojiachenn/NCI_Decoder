import template_pkg.__table__ as NFC_table

# Proprietary messages are inherently vendor-specific - there's no forum
# baseline to delegate to here, unlike NCI_Core.py/RF_Management.py/
# NFCEE_Management.py. Functions here are plain (raw) handlers, registered
# directly under __ctrl__.py's "Proprietary" GID dict by OID (see
# Nxp_pkg/__ctrl__.py's "Proprietary" section and Nxp_pkg/Proprietary.py for
# a real, currently-dispatched example of this shape).
#
# The two functions below are illustrative only (not registered in
# __ctrl__.py's tbl_nci_ctrl["Proprietary"] by default) - replace or remove
# them once this chip's actual proprietary command set is documented.


def NCI_PROPRIETARY_ACT_CMD(rawdata):
    p_payload = 0

    status = NFC_table.tbl_status_codes.get(rawdata[p_payload:p_payload+2*1], "Forbidden")
    print("  * Status:", status)
    p_payload = p_payload + 2*1
    return p_payload


def NCI_PROPRIETARY_ACT_RSP(rawdata):
    p_payload = 0

    status = NFC_table.tbl_status_codes.get(rawdata[p_payload:p_payload+2*1], "Forbidden")
    print("  * Status:", status)
    p_payload = p_payload + 2*1

    print("  * FW_Build_Nb:", rawdata[p_payload:p_payload+2*4])
    p_payload = p_payload + 2*4
    return p_payload
