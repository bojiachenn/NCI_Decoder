import contextlib
import io

from nci_decoder.nfc_forum_2_0_pkg import NCI_Core as forum_NCI_Core
from nci_decoder.template_pkg import RF_Management, NFCEE_Management, Proprietary, __ctrl__

# __ctrl__.py itself does `from template_pkg import NCI_Core` (flat, matching
# the codebase's sys.path-flat-import convention) rather than the dotted
# `nci_decoder.template_pkg.NCI_Core` path used elsewhere in this test file -
# import it the same way here so the identity check below compares the same
# module object __ctrl__.py actually dispatches to, not a second, separately
# loaded copy of the same file under a different sys.modules key.
from template_pkg import NCI_Core


def _capture(fn, *args):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        fn(*args)
    return buf.getvalue()


def test_all_four_modules_import_without_error():
    # Import alone is the assertion here - the module-level `import
    # nfc_forum_pkg...`/no-vendor-forwarding bugs both raised or misbehaved
    # at import/call time before this fix.
    assert NCI_Core is not None
    assert RF_Management is not None
    assert NFCEE_Management is not None
    assert Proprietary is not None


def test_ctrl_table_top_level_gids_match_forum_package():
    from nci_decoder.nfc_forum_2_0_pkg import __ctrl__ as forum_ctrl

    assert set(__ctrl__.tbl_nci_ctrl.keys()) >= set(forum_ctrl.tbl_nci_ctrl.keys())


def test_ctrl_table_dispatches_to_templates_own_modules():
    assert __ctrl__.tbl_nci_ctrl["NCI Core"]["00"]["CMD"] is NCI_Core.CORE_RESET_CMD


def test_ctrl_table_structurally_mirrors_forum_package():
    # template_pkg/__ctrl__.py is meant to be a 1:1 structural mirror of
    # nfc_forum_2_0_pkg/__ctrl__.py (same GID/OID/message-type shape, just
    # pointing at template_pkg's own modules) - a single spot-check (above)
    # can't catch a transcription error elsewhere in this ~32-entry,
    # hand-copied literal (e.g. an OID typo, or a handler wired under the
    # wrong OID/message type).
    from nci_decoder.nfc_forum_2_0_pkg import __ctrl__ as forum_ctrl

    for gid, oids in forum_ctrl.tbl_nci_ctrl.items():
        assert gid in __ctrl__.tbl_nci_ctrl, f"missing GID {gid!r}"
        for oid, handlers in oids.items():
            assert oid in __ctrl__.tbl_nci_ctrl[gid], f"missing OID {gid}/{oid}"
            for mt, forum_fn in handlers.items():
                assert mt in __ctrl__.tbl_nci_ctrl[gid][oid], f"missing MT {gid}/{oid}/{mt}"
                template_fn = __ctrl__.tbl_nci_ctrl[gid][oid][mt]
                assert template_fn.__name__ == forum_fn.__name__, (
                    f"{gid}/{oid}/{mt}: template wires {template_fn.__name__!r}, "
                    f"forum has {forum_fn.__name__!r}"
                )


def test_delegation_output_matches_forum_function_directly():
    # Proves the vendor-forwarding fix actually works end-to-end, not just
    # "imports without crashing": calling CORE_RESET_CMD through the
    # template's thin delegation must produce byte-identical stdout to
    # calling the forum function directly with the same vendor string.
    raw = "01"  # Reset Type: Reset Config

    via_template = _capture(NCI_Core.CORE_RESET_CMD, raw, "None", "None")
    via_forum_directly = _capture(forum_NCI_Core.CORE_RESET_CMD, raw, "None", "None")

    assert via_template == via_forum_directly
    assert "Reset Config" in via_template
