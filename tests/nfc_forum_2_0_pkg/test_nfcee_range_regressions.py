import contextlib
import io

import pytest

from nci_decoder.nfc_forum_2_0_pkg import NFCEE_Management, RF_Management


def _capture(fn, *args):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        fn(*args)
    return buf.getvalue()


# Boundary values that fall outside all three declared NFCEE-ID range buckets
# ('02-0F', '10-7F', '80-FE'): 00 and 01 are the two named-exception IDs, FF is
# the top-of-range RFU value. Before commit 5f5cb72 these either crashed
# (UnboundLocalError) or printed the resolved lookup text twice. "50" (0x50 =
# 80 decimal, inside 10-7F) is included as the normal/dynamic control case that
# always worked, to confirm the fix didn't regress it.
#
# tbl_nfcee_id (both nfc_forum_2_0_pkg and Nxp_pkg define the same entries for
# these four keys) resolves 00/01/FF to a fixed name; that name must appear
# exactly once in the output, not twice.
BOUNDARY_EXPECTED_NAME = {
    "00": "DH-NFCEE",
    "01": "HCI-NTWK-NFCEE (RFU)",
    "FF": "(RFU)",
}
DYNAMIC_VALUE = "50"  # inside 10-7F ("(NFCEE)"), never buggy - sanity control

# name -> (handler function, payload builder given the NFCEE-ID byte)
# All five share the (raw, vendor="None", model="None") signature.
SIMPLE_NFCEE_ID_CASES = {
    "NFCEE_MODE_SET_CMD": (
        NFCEE_Management.NFCEE_MODE_SET_CMD,
        lambda nfcee_byte: nfcee_byte + "00",  # + NFCEE Mode (Disable)
    ),
    "NFCEE_STATUS_NTF": (
        NFCEE_Management.NFCEE_STATUS_NTF,
        lambda nfcee_byte: nfcee_byte + "00",  # + NFCEE Status
    ),
    "NFCEE_POWER_AND_LINK_CNTRL_CMD": (
        NFCEE_Management.NFCEE_POWER_AND_LINK_CNTRL_CMD,
        lambda nfcee_byte: nfcee_byte + "00",  # + Power/Link Cfg
    ),
    "RF_NFCEE_ACTION_NTF": (
        RF_Management.RF_NFCEE_ACTION_NTF,
        lambda nfcee_byte: nfcee_byte + "00" + "00",  # + Trigger + Supporting Data Len(0)
    ),
    # This handler's Nxp_pkg wrapper is a no-op stub that never calls back
    # into this forum function (see Nxp_pkg/RF_Management.py), so the
    # vendor="Nxp" case below tests a combination the real dispatcher never
    # reaches. Kept for consistency with the other 6 handlers rather than
    # special-cased out - see plan-eng-review discussion.
    "RF_SET_FORCED_NFCEE_ROUTING_CMD": (
        RF_Management.RF_SET_FORCED_NFCEE_ROUTING_CMD,
        lambda nfcee_byte: "01" + nfcee_byte + "00",  # Enabled + NFCEE + Power State
    ),
}


@pytest.mark.parametrize("vendor", ["None", "Nxp"])
@pytest.mark.parametrize("nfcee_byte", sorted(BOUNDARY_EXPECTED_NAME))
@pytest.mark.parametrize("name", sorted(SIMPLE_NFCEE_ID_CASES))
def test_nfcee_id_boundary_no_crash_no_duplicate(name, nfcee_byte, vendor):
    fn, build_payload = SIMPLE_NFCEE_ID_CASES[name]
    raw = build_payload(nfcee_byte)

    out = _capture(fn, raw, vendor, "None")

    expected_name = BOUNDARY_EXPECTED_NAME[nfcee_byte]
    assert out.count(expected_name) == 1, (
        f"{name}({nfcee_byte=}, {vendor=}) printed {expected_name!r} "
        f"{out.count(expected_name)} times, expected exactly once:\n{out}"
    )


@pytest.mark.parametrize("vendor", ["None", "Nxp"])
@pytest.mark.parametrize("name", sorted(SIMPLE_NFCEE_ID_CASES))
def test_nfcee_id_dynamic_value_still_works(name, vendor):
    # Sanity control: the in-range dynamic case never crashed before the fix
    # and shouldn't regress now.
    fn, build_payload = SIMPLE_NFCEE_ID_CASES[name]
    raw = build_payload(DYNAMIC_VALUE)

    out = _capture(fn, raw, vendor, "None")

    assert "(NFCEE)" in out


@pytest.mark.parametrize("vendor", ["None", "Nxp"])
@pytest.mark.parametrize("route_byte", sorted(BOUNDARY_EXPECTED_NAME))
def test_listen_mode_routing_info_route_boundary(route_byte, vendor):
    # LISTEN_MODE_ROUTING_INFO(raw, vendor, model) has no default args - it's
    # shared by RF_SET_LISTEN_MODE_ROUTING_CMD and RF_GET_LISTEN_MODE_ROUTING_NTF.
    # Payload: More(1) + NumRoutingEntries(1) + [Qualifier-Type(1) + Len(1) +
    # Value: Route(1) + PowerState(1) + Technology(1)] for one
    # technology-based routing entry (Qualifier-Type low nibble = 0).
    raw = "00" + "01" + "00" + "03" + route_byte + "00" + "00"

    out = _capture(RF_Management.LISTEN_MODE_ROUTING_INFO, raw, vendor, "None")

    expected_name = BOUNDARY_EXPECTED_NAME[route_byte]
    assert out.count(expected_name) == 1, (
        f"LISTEN_MODE_ROUTING_INFO({route_byte=}, {vendor=}) printed "
        f"{expected_name!r} {out.count(expected_name)} times, expected exactly once:\n{out}"
    )


def test_listen_mode_routing_info_dynamic_value_still_works():
    raw = "00" + "01" + "00" + "03" + DYNAMIC_VALUE + "00" + "00"
    out = _capture(RF_Management.LISTEN_MODE_ROUTING_INFO, raw, "None", "None")
    assert "(NFCEE)" in out


@pytest.mark.parametrize("vendor", ["None", "Nxp"])
@pytest.mark.parametrize("nfcee_byte", sorted(BOUNDARY_EXPECTED_NAME))
def test_rf_nfcee_discovery_req_ntf_nfcee_boundary(nfcee_byte, vendor):
    # RF_NFCEE_DISCOVERY_REQ_NTF: NumInfoEntries(1) + [Type(1)=00 (triggers
    # the NFCEE-ID sub-print) + Len(1)=03 + Value: NFCEE(1) + RFTechMode(1) +
    # RFProtocol(1)].
    raw = "01" + "00" + "03" + nfcee_byte + "00" + "00"

    out = _capture(RF_Management.RF_NFCEE_DISCOVERY_REQ_NTF, raw, vendor, "None")

    expected_name = BOUNDARY_EXPECTED_NAME[nfcee_byte]
    assert out.count(expected_name) == 1, (
        f"RF_NFCEE_DISCOVERY_REQ_NTF({nfcee_byte=}, {vendor=}) printed "
        f"{expected_name!r} {out.count(expected_name)} times, expected exactly once:\n{out}"
    )


def test_rf_nfcee_discovery_req_ntf_dynamic_value_still_works():
    raw = "01" + "00" + "03" + DYNAMIC_VALUE + "00" + "00"
    out = _capture(RF_Management.RF_NFCEE_DISCOVERY_REQ_NTF, raw, "None", "None")
    assert "(NFCEE)" in out
