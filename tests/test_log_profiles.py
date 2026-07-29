import log_profiles


# --- get_profile -------------------------------------------------------

def test_get_profile_st_lowercase_returns_st_profile():
    assert log_profiles.get_profile("st") is log_profiles.PROFILES["st"]


def test_get_profile_st_uppercase_is_case_insensitive():
    assert log_profiles.get_profile("ST") is log_profiles.PROFILES["st"]
    assert log_profiles.get_profile("St") is log_profiles.PROFILES["st"]


def test_get_profile_other_keyword_returns_default_profile_shape():
    profile = log_profiles.get_profile("Nxp")
    assert profile["trigger"] == "NxpNci"
    assert profile["sequence"] is None
    assert profile["redacted_markers"] == []


def test_get_profile_arbitrary_keyword_still_builds_default_profile():
    profile = log_profiles.get_profile("Foo")
    assert profile["trigger"] == "FooNci"
    assert profile["sequence"] is None


# --- build_default_profile ----------------------------------------------

def test_build_default_profile_trigger_and_region():
    profile = log_profiles.build_default_profile("Nxp")
    assert profile["trigger"] == "NxpNci"
    assert profile["region"] == {"mode": "after_last_literal", "marker": ">"}


def test_build_default_profile_tx_direction_matches_only_x_suffix():
    profile = log_profiles.build_default_profile("Nxp")
    tx_name, tx_pat = profile["directions"][0]
    rx_name, rx_pat = profile["directions"][1]
    assert tx_name == "TX" and rx_name == "RX"
    assert tx_pat.search("...NxpNciX...")
    assert not tx_pat.search("...NxpNciR...")
    assert rx_pat.search("...NxpNciR...")
    assert not rx_pat.search("...NxpNciX...")


def test_build_default_profile_escapes_regex_metacharacters_in_key():
    # decode_key could contain regex-special characters (user-typed keyword);
    # re.escape must keep the direction patterns from misbehaving.
    profile = log_profiles.build_default_profile("A.B")
    tx_name, tx_pat = profile["directions"][0]
    assert tx_pat.search("A.BNciX")
    assert not tx_pat.search("AxBNciX")  # literal dot must not act as wildcard


# --- _locate_region -------------------------------------------------------

def test_locate_region_after_last_literal_found():
    region_cfg = {"mode": "after_last_literal", "marker": ">"}
    line = "prefix >> 0004F10000006EEF"
    assert log_profiles._locate_region(line, region_cfg) == " 0004F10000006EEF"


def test_locate_region_after_last_literal_uses_last_occurrence():
    region_cfg = {"mode": "after_last_literal", "marker": ">"}
    line = "a > b > c"
    assert log_profiles._locate_region(line, region_cfg) == " c"


def test_locate_region_after_last_literal_not_found():
    region_cfg = {"mode": "after_last_literal", "marker": ">"}
    assert log_profiles._locate_region("no marker here", region_cfg) == ""


def test_locate_region_after_regex_end_found():
    import re
    region_cfg = {"mode": "after_regex_end", "pattern": re.compile(r"\b[TtRr]x\b")}
    line = "(#00004) Rx 60 00 1f"
    assert log_profiles._locate_region(line, region_cfg) == " 60 00 1f"


def test_locate_region_after_regex_end_not_found():
    import re
    region_cfg = {"mode": "after_regex_end", "pattern": re.compile(r"\b[TtRr]x\b")}
    assert log_profiles._locate_region("nothing matches here", region_cfg) == ""


def test_locate_region_unknown_mode_returns_empty():
    assert log_profiles._locate_region("anything", {"mode": "bogus"}) == ""


# --- _extract_ts ------------------------------------------------------

def test_extract_ts_matches_two_token_prefix():
    line = "08-21 06:14:35.847  DH --> NFCC  NxpNciX  << ... >>"
    assert log_profiles._extract_ts(line) == "08-21 06:14:35.847"


def test_extract_ts_empty_string_when_no_second_token():
    assert log_profiles._extract_ts("") == ""
    assert log_profiles._extract_ts("onlyoneword") == ""


# --- _extract_hex -------------------------------------------------------

def test_extract_hex_contiguous():
    assert log_profiles._extract_hex("  0004F10000006EEF") == "0004F10000006EEF"


def test_extract_hex_space_separated():
    assert log_profiles._extract_hex(" 60 00 1f 02") == "60001f02"


def test_extract_hex_no_match_returns_empty():
    assert log_profiles._extract_hex("no hex here at all only words") == ""


def test_extract_hex_trailing_newline_not_embedded():
    # Regression: HEX_RUN_RE's trailing \s* can swallow a line's terminating
    # newline; _extract_hex must strip ALL whitespace, not just literal spaces,
    # or the newline corrupts length math when concatenating ST fragments.
    result = log_profiles._extract_hex(" 20 01\n")
    assert result == "2001"
    assert "\n" not in result


# --- extract_candidate: default (non-sequence) profile -------------------

def test_extract_candidate_default_profile_non_triggering_line_returns_none():
    profile = log_profiles.get_profile("Nxp")
    assert log_profiles.extract_candidate("some unrelated log line", profile) is None


def test_extract_candidate_default_profile_tx_hex_extraction():
    profile = log_profiles.get_profile("Nxp")
    line = "08-21 06:14:35.847  DH --> NFCC  NxpNciX  << Nxp HDLL: DL_GET_VERSION >>  0004F10000006EEF"
    cand = log_profiles.extract_candidate(line, profile)
    assert cand == {
        "kind": "candidate",
        "direction": "TX",
        "ts": "08-21 06:14:35.847",
        "hex": "0004F10000006EEF",
    }


def test_extract_candidate_default_profile_rx_direction():
    profile = log_profiles.get_profile("Nxp")
    line = "08-21 06:14:37.654  DH <-- NFCC  NxpNciR  << RF_DISCOVER_RSP >>  41030100"
    cand = log_profiles.extract_candidate(line, profile)
    assert cand["direction"] == "RX"
    assert cand["hex"] == "41030100"


def test_extract_candidate_default_profile_trigger_present_but_no_direction():
    profile = log_profiles.get_profile("Nxp")
    line = "this has NxpNci in it but no X or R suffix"
    assert log_profiles.extract_candidate(line, profile) is None


# --- extract_candidate: ST sequence-based profile ------------------------

def test_extract_candidate_st_start_line():
    profile = log_profiles.get_profile("st")
    line = ("07-06 09:54:12.323   843  4342 D StNfcHal: (#00004) Rx 60 00 1f 02 01 20 02 1a "
            "06 03 02 06 17 50 03 02 01 00 44 02 15 00 00 55 97 00 00 00 00 00 01 22")
    cand = log_profiles.extract_candidate(line, profile)
    assert cand["kind"] == "candidate"
    assert cand["seq"] == "00004"
    assert cand["direction"] == "RX"
    assert cand["is_start"] is True
    assert cand["is_continue"] is False
    expected_hex = "".join(
        "60 00 1f 02 01 20 02 1a 06 03 02 06 17 50 03 02 "
        "01 00 44 02 15 00 00 55 97 00 00 00 00 00 01 22".split()
    )
    assert cand["hex"] == expected_hex
    assert len(cand["hex"]) == 64  # 32 bytes


def test_extract_candidate_st_continuation_line_same_sequence():
    profile = log_profiles.get_profile("st")
    line = "07-06 09:54:12.323   843  4342 D StNfcHal: (#00004) rx 20 01"
    cand = log_profiles.extract_candidate(line, profile)
    assert cand["kind"] == "candidate"
    assert cand["seq"] == "00004"
    assert cand["direction"] == "RX"
    assert cand["is_start"] is False
    assert cand["is_continue"] is True
    assert cand["hex"] == "2001"


def test_extract_candidate_st_hex_sequence_number():
    # Sequence numbers can be hexadecimal, not just decimal (#0000A).
    profile = log_profiles.get_profile("st")
    line = "07-06 09:54:12.333   843  4342 D StNfcHal: (#0000A) Rx 4f 02 01 00"
    cand = log_profiles.extract_candidate(line, profile)
    assert cand is not None
    assert cand["seq"] == "0000A"
    assert cand["is_start"] is True


def test_extract_candidate_st_tx_start():
    profile = log_profiles.get_profile("st")
    line = "07-06 09:54:12.328   843  4342 D StNfcHal: (#00008) Tx 2f 02 02 02 01"
    cand = log_profiles.extract_candidate(line, profile)
    assert cand["direction"] == "TX"
    assert cand["is_start"] is True
    assert cand["hex"] == "2f02020201"


def test_extract_candidate_st_redacted_marker():
    profile = log_profiles.get_profile("st")
    line = "07-06 09:54:12.400   843  4342 D StNfcHal: (#00005) Tx (hidden)"
    cand = log_profiles.extract_candidate(line, profile)
    assert cand["kind"] == "redacted"
    assert cand["seq"] == "00005"
    assert cand["direction"] == "TX"


def test_extract_candidate_st_sequence_present_but_no_direction_returns_none():
    profile = log_profiles.get_profile("st")
    line = "07-06 09:54:12.400   843  4342 D StNfcHal: (#00006) some other content"
    assert log_profiles.extract_candidate(line, profile) is None


def test_extract_candidate_st_non_triggering_line_returns_none():
    profile = log_profiles.get_profile("st")
    assert log_profiles.extract_candidate("no StNfcHal marker in this line", profile) is None


def test_extract_candidate_st_lowercase_start_word_is_not_a_start():
    # Lowercase "rx"/"tx" only ever mark continuations, never a fresh packet -
    # a lone lowercase direction word with no prior start should still report
    # is_continue=True / is_start=False (accumulation logic lives in Decoder.py,
    # not here; extract_candidate just reports what it saw on this one line).
    profile = log_profiles.get_profile("st")
    line = "07-06 09:54:12.323   843  4342 D StNfcHal: (#00009) tx 01 02"
    cand = log_profiles.extract_candidate(line, profile)
    assert cand["is_start"] is False
    assert cand["is_continue"] is True
