from tests.helpers import decode


def test_field_detect_consumes_system_code():
    out = decode("61 20 04 02 00 12 FC", vendor="Nxp")
    assert "  * System Code: 12FC" in out
    assert "Payload error" not in out


def test_field_detect_poll_req_uses_bit3():
    out = decode("61 20 04 08 00 12 FC", vendor="Nxp")
    assert "  * POLL_REQ SC0-SC1: 12FC" in out
    assert "Payload error" not in out


def test_field_detect_bit4_is_not_poll_req():
    out = decode("61 20 04 10 00 12 FC", vendor="Nxp")
    assert "POLL_REQ" not in out
    assert "  * System Code: 12FC" in out


def test_nak_presence_rsp_uses_nxp_status_table():
    out = decode("41 10 01 E3", vendor="Nxp")
    assert "STATUS_PMU_TXLDO_OVERCURRENT" in out
