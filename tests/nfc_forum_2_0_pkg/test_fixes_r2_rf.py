from tests.helpers import decode_lines


# B1: NFC-DEP Poll Mode activation parameters (NCI 2.0 Table 102) end with the
# 1-octet "Data Exchange Length Reduction" after ATR_RES, exactly like the
# Listen branch (Table 103); looked up in tbl_len_rdu_val (Table 137).

def test_nfc_dep_poll_a_reads_data_exchange_lr():
    # RF IF 03 (NFC-DEP), Mode 00 (A_PASSIVE_POLL), Activation Params:
    # ATR_RES len 03 + AABBCC + LR 01.
    lines = decode_lines("61 05 1A 01 03 05 00 FB 01 0A 44 00 04 11 22 33 44 01 60 00 00 00 00 05 03 AA BB CC 01")
    assert "  * ATR_RES Rsp: AABBCC" in lines
    assert "  * Data Exchange LR: 254 Bytes (01)" in lines
    assert not any("Payload error" in l for l in lines)


def test_nfc_dep_poll_f_reads_data_exchange_lr():
    lines = decode_lines("61 05 11 01 03 05 02 FB 01 02 01 00 02 01 01 04 02 AA BB 00")
    assert "  * Data Exchange LR: No PSL_REQ and PSL_RES were exchanged (00)" in lines
    assert not any("Payload error" in l for l in lines)


def test_nfc_dep_poll_missing_lr_reports_error_inside_declared_length():
    lines = decode_lines("61 05 0E 01 03 05 00 FB 01 00 00 00 00 03 02 AA BB")
    assert "  * Error: Activation Parameters: Payload too short: need 1 byte(s) for Data Exchange LR, 0 left" in lines


def test_nfc_dep_poll_extra_bytes_shown_as_remaining():
    lines = decode_lines("61 05 11 01 03 05 00 FB 01 00 00 00 00 06 02 AA BB 30 EE 55")
    assert "  * Data Exchange LR: RFU (30)" in lines
    assert "  * Remaining Activation Params: EE55" in lines


def test_nfc_dep_poll_nxp_reads_data_exchange_lr():
    lines = decode_lines("61 05 1A 01 03 05 00 FB 01 0A 44 00 04 11 22 33 44 01 60 00 00 00 00 05 03 AA BB CC 01", vendor="Nxp")
    assert "  * Data Exchange LR: 254 Bytes (01)" in lines
