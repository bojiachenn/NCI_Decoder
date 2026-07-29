import pytest

from tests.helpers import decode


# Packet layout (see nci_decoder/Decoder_Main.py):
#   octet0: high 3 bits = Message Type (000 DATA/001 CMD/010 RSP/011 NTF),
#           bit 3 = PBF, low 4 bits = GID
#   octet1: OID (control packets) / CR+RFU (DATA packets)
#   octet2: declared payload length in bytes
#
# "20 00 01 01" = CORE_RESET_CMD (NCI Core, OID 00) with 1-byte payload "01".


def test_dispatch_success_core_reset_cmd_vendor_none():
    out = decode("20000101", vendor="None")
    assert "CORE_RESET_CMD" in out
    assert "Payload error" not in out


def test_dispatch_success_core_reset_cmd_vendor_nxp_routes_to_nxp_pkg():
    # Nxp_pkg.NCI_Core.CORE_RESET_CMD is a thin wrapper around the same forum
    # function (Origin.CORE_RESET_CMD(raw, "nxp")) - this just confirms the
    # vendor="Nxp" path actually reaches Nxp_pkg instead of nfc_forum_2_0_pkg.
    out = decode("20000101", vendor="Nxp")
    assert "CORE_RESET_CMD" in out
    assert "Payload error" not in out


def test_dispatch_unknown_gid_oid_raises_key_error_with_captured_output():
    # octet0=0x23: MT=CMD(001), PBF=0, GID=0011 ("NFCC Management"), which
    # nfc_forum_2_0_pkg/__ctrl__.py's tbl_nci_ctrl never defines a key for.
    with pytest.raises(KeyError) as exc_info:
        decode("230000", vendor="None")
    assert "ERROR_NOT_FOUND" in exc_info.value.captured_output


def test_dispatch_payload_length_mismatch_prints_payload_error():
    # Declares a 2-byte payload (octet2=02) but CORE_RESET_CMD structurally
    # only ever consumes 1 byte, so the post-call length check must fire.
    out = decode("2000020199", vendor="None")
    assert "Payload error" in out


def test_data_packet_branch():
    # octet0=0x00: MT=DATA(000), conn_id=0000 (static DH<->Remote Endpoint).
    # octet1=0x00 satisfies the "top 6 bits of octet1 are zero" DATA guard.
    out = decode("000001AB", vendor="None", mode=1)
    assert "DATA Packet" in out
    assert "Static: DH -- Remote NFC Endpoint" in out
    assert "Payload error" not in out


def test_pbf_flag_branch():
    # Same CORE_RESET_CMD packet as the success case, but with the PBF bit
    # (octet0 bit 3) set to 1.
    out = decode("30000101", vendor="None")
    assert "PBF: 1" in out


def test_hdll_branch_nxp():
    # 2-byte HDLL header + CRC16 framing (Nxp_pkg-only; the forum package has
    # no HDLL table). frame_len=1, op_code=F1 (DL_GET_VERSION), no message
    # bytes, arbitrary 2-byte CRC "0000".
    out = decode("0001F10000", vendor="Nxp", mode=1)
    assert "HDLL: DL_GET_VERSION" in out


def test_unknown_raw_data_fallback():
    # Matches neither the 3-byte-header length check nor the 2-byte HDLL
    # framing check.
    out = decode("FFFFFFFF", vendor="None")
    assert "Unknown raw data" in out
