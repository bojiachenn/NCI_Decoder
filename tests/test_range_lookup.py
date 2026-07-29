import pytest

from nci_decoder import range_lookup


TBL_NFCEE_ID_SHAPE = {
    "name": "Table 116: NFCEE IDs:",
    "00": "DH-NFCEE",
    "01": "HCI-NTWK-NFCEE (RFU)",
    "02-0F": "(Static IDs)",
    "10-7F": "(NFCEE)",
    "80-FE": "(HCI-NFCEE)",
    "FF": "(RFU)",
}

# A table with a different bucket shape, to prove the function is generic
# and doesn't hardcode any specific range set.
TBL_TLV_TYPE_SHAPE = {
    "name": "Table 118: TLV Coding for NFCEE Discovery:",
    "00": "Hardware / Registration Identification",
    "05-9F": "RFU",
    "A0-FF": "For proprietary use",
}


def test_finds_containing_range_for_value_in_first_bucket():
    assert range_lookup.find_range_key(TBL_NFCEE_ID_SHAPE, 0x05) == "02-0F"


def test_finds_containing_range_for_value_in_middle_bucket():
    assert range_lookup.find_range_key(TBL_NFCEE_ID_SHAPE, 0x50) == "10-7F"


def test_range_boundaries_are_inclusive():
    assert range_lookup.find_range_key(TBL_NFCEE_ID_SHAPE, 0x02) == "02-0F"
    assert range_lookup.find_range_key(TBL_NFCEE_ID_SHAPE, 0x0F) == "02-0F"
    assert range_lookup.find_range_key(TBL_NFCEE_ID_SHAPE, 0x10) == "10-7F"
    assert range_lookup.find_range_key(TBL_NFCEE_ID_SHAPE, 0x7F) == "10-7F"
    assert range_lookup.find_range_key(TBL_NFCEE_ID_SHAPE, 0x80) == "80-FE"
    assert range_lookup.find_range_key(TBL_NFCEE_ID_SHAPE, 0xFE) == "80-FE"


def test_values_outside_every_range_return_none():
    # These are exactly the boundary values that caused the 8 real bugs in
    # commit 5f5cb72: 0x00/0x01/0xFF fall outside all three declared ranges.
    assert range_lookup.find_range_key(TBL_NFCEE_ID_SHAPE, 0x00) is None
    assert range_lookup.find_range_key(TBL_NFCEE_ID_SHAPE, 0x01) is None
    assert range_lookup.find_range_key(TBL_NFCEE_ID_SHAPE, 0xFF) is None


def test_non_range_keys_are_ignored_not_matched():
    # 'name' and exact single-byte keys must never be mistaken for a range.
    assert range_lookup.find_range_key({"name": "x", "00": "y"}, 0x00) is None


def test_generic_across_a_table_with_different_bucket_boundaries():
    assert range_lookup.find_range_key(TBL_TLV_TYPE_SHAPE, 0x10) == "05-9F"
    assert range_lookup.find_range_key(TBL_TLV_TYPE_SHAPE, 0xA0) == "A0-FF"
    assert range_lookup.find_range_key(TBL_TLV_TYPE_SHAPE, 0xFF) == "A0-FF"


def test_empty_table_returns_none():
    assert range_lookup.find_range_key({}, 0x50) is None


def _range_entries(table):
    for key in table:
        match = range_lookup._RANGE_KEY_RE.match(key) if isinstance(key, str) else None
        if match:
            yield key, int(match.group(1), 16), int(match.group(2), 16)


def _assert_well_formed(table):
    # find_range_key can't tell a malformed/ambiguous table from a real
    # single-match case (it just returns the first hit) - a reversed key
    # (e.g. a typo'd 'FE-80') silently becomes permanently dead (every value
    # falls through to ""), and overlapping ranges silently pick whichever
    # entry iterates first. Neither produces a crash, so this must be caught
    # here rather than at find_range_key's call sites.
    entries = list(_range_entries(table))
    for key, low, high in entries:
        assert low <= high, f"{key!r} has low > high - dead range, never matches"
    for i, (key_a, low_a, high_a) in enumerate(entries):
        for key_b, low_b, high_b in entries[i + 1:]:
            overlap = low_a <= high_b and low_b <= high_a
            assert not overlap, f"{key_a!r} and {key_b!r} overlap - ambiguous match"


def test_production_nfcee_id_tables_are_well_formed():
    # All 8 current call sites in nfc_forum_2_0_pkg pass NFC_table.tbl_nfcee_id
    # (from either nfc_forum_2_0_pkg or Nxp_pkg, depending on vendor) to
    # find_range_key - both real tables must have sane, non-overlapping
    # ranges, since ST-chip work is expected to add further tables via the
    # same `from nfc_forum_2_0_pkg.__table__ import *` + override shadowing
    # documented in template_pkg/README.md.
    from nci_decoder.nfc_forum_2_0_pkg import __table__ as forum_table
    from nci_decoder.Nxp_pkg import __table__ as nxp_table

    _assert_well_formed(forum_table.tbl_nfcee_id)
    _assert_well_formed(nxp_table.tbl_nfcee_id)


def test_well_formed_helper_catches_reversed_range():
    with pytest.raises(AssertionError):
        _assert_well_formed({"FE-80": "typo'd reversed range"})


def test_well_formed_helper_catches_overlapping_ranges():
    with pytest.raises(AssertionError):
        _assert_well_formed({"10-7F": "a", "40-9F": "b"})
