import contextlib
import io

from nci_decoder.nfc_forum_2_0_pkg import NFCEE_Management, RF_Management


def _capture(fn, *args):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        fn(*args)
    return buf.getvalue()


# These 5 sites were converted to range_lookup.find_range_key alongside the
# original 8 (NFCEE-ID) sites, but use a different table per site and were
# never buggy (single-condition or two-branch collapse, no missing-else
# UnboundLocalError case) - covered here to lock in behavior, not as a
# regression-of-a-known-bug test.


def test_listen_mode_routing_info_protocol_bucket():
    # Protocol-based routing entry (Qualifier-Type low nibble "1"): More(1) +
    # NumRoutingEntries(1) + [QType(1)=01 + Len(1)=03 + Route(1) +
    # PowerState(1) + Protocol(1)=90 (0x90, in tbl_rf_proto's 80-FE bucket)].
    raw = "00" + "01" + "01" + "03" + "50" + "00" + "90"
    out = _capture(RF_Management.LISTEN_MODE_ROUTING_INFO, raw, "None", "None")
    assert "For proprietary use" in out


def test_rf_nfcee_action_ntf_trigger_bucket():
    # NFCEE ID(1) + Trigger(1)=50 (0x50, in tbl_nfcee_ntf_trig's 10-7F bucket,
    # "Application specific") + Supporting Data Len(1)=00.
    raw = "50" + "50" + "00"
    out = _capture(RF_Management.RF_NFCEE_ACTION_NTF, raw, "None", "None")
    assert "Application specific" in out


def test_rf_nfcee_discovery_req_ntf_type_key_bucket():
    # NumInfoEntries(1)=01 + [Type(1)=90 (0x90, in tbl_nfcee_disc_req_type's
    # 80-FF bucket, "For proprietary use") + Len(1)=00].
    raw = "01" + "90" + "00"
    out = _capture(RF_Management.RF_NFCEE_DISCOVERY_REQ_NTF, raw, "None", "None")
    assert "For proprietary use" in out


def test_rf_nfcee_discovery_req_ntf_rf_tech_mode_bucket():
    # NumInfoEntries(1)=01 + [Type(1)=00 (triggers the NFCEE/TechMode/Proto
    # sub-print) + Len(1)=03 + Value: NFCEE(1) + RFTechMode(1)=78 (0x78, in
    # tbl_rf_tech_mode's 70-7F bucket) + RFProtocol(1)].
    raw = "01" + "00" + "03" + "50" + "78" + "00"
    out = _capture(RF_Management.RF_NFCEE_DISCOVERY_REQ_NTF, raw, "None", "None")
    assert "Reserved for Proprietary Technologies in Poll Mode" in out


def test_nfcee_discover_ntf_tlv_type_bucket():
    # NFCEE ID(1) + Status(1)=00 + NumProtoInfo(1)=00 + NumNfceeInfoTlv(1)=01
    # + [TLV Type(1)=B0 (0xB0, in tbl_tlv_type's A0-FF bucket, "For
    # proprietary use") + TLV Len(1)=00] + Power Supply(1)=00.
    raw = "50" + "00" + "00" + "01" + "B0" + "00" + "00"
    out = _capture(NFCEE_Management.NFCEE_DISCOVER_NTF, raw, "None", "None")
    assert "For proprietary use" in out
