"""Bug-fix round 2: Nxp_pkg Proprietary.py / HDLL.py / __ctrl__.HDLL()."""
import importlib

import pytest

from tests.helpers import decode_lines

NXP = {"vendor": "Nxp"}


@pytest.fixture(autouse=True)
def _reset_state():
    """Cross-packet module globals start from their import-time values."""
    ctrl = importlib.import_module("Nxp_pkg.__ctrl__")
    prop = importlib.import_module("Nxp_pkg.Proprietary")
    saved = (ctrl.HDLL_CMD, prop.TEST_ID_3F, prop.DPC_TYPE, prop.AST_LOOP)
    yield
    ctrl.HDLL_CMD, prop.TEST_ID_3F, prop.DPC_TYPE, prop.AST_LOOP = saved


def run(hex_str, prev=()):
    for p in prev:
        decode_lines(p, **NXP)
    return decode_lines(hex_str, **NXP)


# ---- Phase A ---------------------------------------------------------------

def test_cold_reset_cmd_looks_up_table():
    assert "  * RESET by pin: SE reset Disabled" in run("2F 1F 01 01")


def test_test_prbs_cmd_returns_offset():
    out = run("2F 30 06 01 01 01 04 00 10")
    assert "  * PRBS series length: 0010" in out
    assert not any("Payload error" in l for l in out)


def test_l1_debug_ntf_branches_on_bytes():
    out = run("6F 35 07 10 00 20 00 01 23 12")
    assert "  * RSSI: 0123 (MSB)" in out
    assert "  * CLIF State: 12" in out


def test_rf_spc_ntf_phase_base16():
    assert "  * Phase: -8192.0 °" in run("6F 3D 07 04 01 02 00 01 00 80")


def test_ast_utility_vddpa_base16():
    assert "  * VDDPA: 2.3 V" in run("4F 3F 01 10", prev=["2F 3F 03 70 00 00"])


def test_hdll_chunk_bit_printed():
    assert "  * Chunk: 1" in run("20 04 F1 00 00 00 5B E7")


def test_hdll_unknown_op_code_does_not_raise():
    out = run("00 04 77 00 00 00 94 4E")
    assert out[0].startswith("  << Nxp HDLL: UNKNOWN (77) >>")
    assert "Error: unknown HDLL op code 77, raw: 000477000000944E" in out


def test_hdll_crc_mismatch_line():
    out = run("00 04 00 00 00 00 AB CD")
    assert "    ! CRC mismatch: calculated 8716" in out
    assert not any("CRC mismatch" in l for l in run("00 04 00 00 00 00 87 16"))


# ---- Phase B ---------------------------------------------------------------

def test_l2_cma_rx_data_not_capped():
    out = run("6F 36 12 AF 10 00 20 00 04 0B 01 02 03 04 05 06 07 08 09 0A 0B")
    assert "    * CLT RX Data: 0102030405060708090A0B" in out
    assert not any("Payload error" in l for l in out)


def test_l2_cma_error_data_not_capped():
    out = run("6F 36 12 AF 10 00 20 00 0C 0A 00 01 02 03 04 05 06 07 08 09 0A")
    assert "    * Data received: 0102030405060708090A" in out


def test_apdu_logging_unknown_category_prints_rest():
    out = run("6F 04 07 60 00 00 10 5A 11 22")
    assert "  * APDU Data: 1122" in out
    assert not any("Payload error" in l for l in out)


def test_hdll_session_state_unknown_is_rfu():
    out = run("00 04 00 03 00 00 DE 46", prev=["00 04 F2 00 00 00 F5 33"])
    assert "  * Session State: RFU (03)" in out


def test_hdll_check_integrity_code_only_rows():
    frame = ("00 88 00 01 03 00 00 00 00 80 11 22 33 44 " + "00 " * 108
             + "AA BB CC DD 01 02 03 04 05 06 07 08 00 00 00 00 55 BF")
    out = run(frame, prev=["00 04 E0 00 00 00 03 FC"])
    assert "     1   OK (44332211)          KO (DDCCBBAA)" in out
    assert any(l.strip() == "2                          KO (04030201)" for l in out)
    assert any(l.strip() == "3                          KO (08070605)" for l in out)


def test_low_power_tag_removal_ntf_registered():
    out = run("6F 1C 00")
    assert out[0].startswith("  << LOW_POWER_TAG_REMOVAL_NTF >>")
    assert out[1].strip() == "(Empty)"


# ---- Phase C ---------------------------------------------------------------

def test_dpc_helper_rsp_current_12bit():
    # NXP UM: 12-bit current = byte0 + (byte1 & 0x0F) * 256; byte1 high nibble is flags/RFU
    out = run("4F 3F 0E 00 0F 2C 01 0D 00 00 00 F4 01 0C 00 00 00", prev=["2F 3F 03 05 00 00"])
    assert any("300 mA" in l and "2C010D" in l for l in out)
    assert any("500 mA" in l and "F4010C" in l for l in out)


DPC_ACCEPTANCE_RAW = (
    "4F3F3E000F36810D00000037810C00000037810C00000037810C00000036810D00000036810D00000036810D"
    "00000037810C00000036810D00000037810C000000"
)
DPC_ACCEPTANCE_EXPECTED = """  << OPTIONAL_RSP >>
  << DPC_HELPER_RSP >>
  * Status: STATUS_OK
  * DPC Info: 36810D00000037810C00000037810C00000037810C00000036810D00000036810D00000036810D00000037810C00000036810D00000037810C000000
   ~  #  ~  Power  ~  VDDPA  ~  Current  ~  NCI cmd  ~
      0    0.666 W    2.15 V     310 mA      36810D
      1    0.653 W    2.10 V     311 mA      37810C
      2    0.653 W    2.10 V     311 mA      37810C
      3    0.653 W    2.10 V     311 mA      37810C
      4    0.666 W    2.15 V     310 mA      36810D
      5    0.666 W    2.15 V     310 mA      36810D
      6    0.666 W    2.15 V     310 mA      36810D
      7    0.653 W    2.10 V     311 mA      37810C
      8    0.666 W    2.15 V     310 mA      36810D
      9    0.653 W    2.10 V     311 mA      37810C
#end"""


def test_dpc_helper_rsp_acceptance_vector():
    # user-supplied acceptance vector (NXP UM based), compared line by line
    out = run(DPC_ACCEPTANCE_RAW, prev=["2F 3F 03 05 00 00"])
    assert [l.rstrip() for l in out] == DPC_ACCEPTANCE_EXPECTED.splitlines()


def test_rf_get_transition_rsp_little_endian():
    out = run("4F 14 06 00 04 01 02 03 04")
    assert "  * RF Transition Val: 0x04030201 (raw 01020304)" in out
