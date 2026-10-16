"""Crash fixes synced into nfc_forum_2_3_pkg (still not wired into dispatch).

Each input below raised before the fix (see docs/nfc_forum_2_3/README.md,
section 2.4 and the "已實測會丟例外" summary). Handlers are called directly with
the payload (header stripped), since 2.3 is not reachable via Decoder_Main.
"""
import contextlib
import io

import pytest

from nci_decoder.nfc_forum_2_3_pkg import RF_Management


def _run(fn, payload):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ret = fn(payload.replace(" ", ""))
    return ret, buf.getvalue()


def test_listen_mode_routing_sc_based_no_typeerror():
    # 21 01 08 00 01 03 04 01 3B FE FE -> TypeError (float range)
    ret, out = _run(RF_Management.RF_SET_LISTEN_MODE_ROUTING_CMD, "00 01 03 04 01 3B FE FE")
    assert "SC Route" in out
    assert "FEFE" in out
    assert ret == 16


def test_listen_mode_routing_apdu_pattern_no_typeerror():
    # type 4 (APDU pattern), len 6: route 01, power 3B, ref A0A1, mask FFFF
    ret, out = _run(RF_Management.RF_SET_LISTEN_MODE_ROUTING_CMD, "00 01 04 06 01 3B A0 A1 FF FF")
    assert "Reference data" in out
    assert "Mask" in out
    assert ret == 20


@pytest.mark.parametrize("payload, expect", [
    # 61 03 06 01 03 82 01 00 02 -> UnboundLocalError 'p_payload' (F_PASSIVE_LISTEN)
    ("01 03 82 01 00 02", "Local NFCID2 Len: 0"),
    # ACTIVE_POLL (03) with a 1-byte ATR_RES
    ("01 03 03 02 01 AA 02", "ATR_RES Rsp: AA"),
    # ACTIVE_LISTEN (83) with a 1-byte ATR_REQ
    ("01 03 83 02 01 BB 02", "ATR_REQ Cmd: BB"),
])
def test_rf_discover_ntf_tech_spec_para_no_unboundlocal(payload, expect):
    ret, out = _run(RF_Management.RF_DISCOVER_NTF, payload)
    assert expect in out
    assert ret == len(payload.replace(" ", ""))


def test_set_forced_nfcee_routing_enabled_no_unboundlocal():
    # 21 11 03 01 80 3B -> UnboundLocalError 'val_payload'
    ret, out = _run(RF_Management.RF_SET_FORCED_NFCEE_ROUTING_CMD, "01 80 3B")
    assert "Forced NFCEE: 80" in out
    assert "Power State: 00111011" in out
    assert ret == 6


def test_nfcee_action_ntf_apdu_trigger_no_typeerror():
    # trigger 04 (APDU pattern): ref A0A1 + mask FFFF; n/2 slice used to raise TypeError
    ret, out = _run(RF_Management.RF_NFCEE_ACTION_NTF, "80 04 04 A0 A1 FF FF")
    assert "Reference data: A0A1" in out
    assert "Mask: FFFF" in out
    assert ret == 14
