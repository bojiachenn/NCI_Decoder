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
