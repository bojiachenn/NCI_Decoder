from tests.helpers import decode


# B2 - CORE_RESET_NTF Manufacturer Specific Info length + "Reset Trigger" label

def test_reset_ntf_label_spelling():
    out = decode("60 00 0A 02 01 20 02 05 01 02 03 04 05", vendor="Nxp")
    assert "  * Reset Trigger: " in out
    assert "Rest Trigger" not in out


def test_reset_ntf_info_len_5_named_fields():
    out = decode("60 00 0A 02 01 20 02 05 01 02 03 04 05", vendor="Nxp")
    assert "  * Model ID: 01" in out
    assert "  * FLASH Ver: 0405" in out
    assert "(extra)" not in out
    assert "Payload error" not in out


def test_reset_ntf_info_len_over_5_prints_extra():
    out = decode("60 00 0C 02 01 20 02 07 01 02 03 04 05 AA BB", vendor="Nxp")
    assert "  * FLASH Ver: 0405" in out
    assert "  * Manufacturer Specific Info (extra): AABB" in out
    assert "Payload error" not in out


def test_reset_ntf_info_len_under_5_prints_whole_info():
    out = decode("60 00 08 02 01 20 02 03 01 02 03", vendor="Nxp")
    assert "  * Manufacturer Specific Info: 010203" in out
    assert "Model ID" not in out
    assert "Payload error" not in out


# C - VALUE_OF_REGISTER little-endian fixes

def test_a009_to_before_stdby_cfg_little_endian():
    out = decode("40 03 07 00 01 A0 09 02 E8 03", vendor="Nxp")
    assert "      * Time: 1.0 s" in out


def test_a094_one_byte_unit_flag_b7():
    # NXP UM: Bit[0:3] timeout value, Bit[7] = 1 -> seconds
    out = decode("40 03 06 00 01 A0 94 01 85", vendor="Nxp")
    assert "      * Delay after TEMP_ERROR: 5 s" in out
    out = decode("40 03 06 00 01 A0 94 01 05", vendor="Nxp")
    assert "      * Delay after TEMP_ERROR: 5 (No unit defined)" in out


def test_a094_rfu_bits_4_to_6_ignored():
    out = decode("40 03 06 00 01 A0 94 01 95", vendor="Nxp")
    assert "      * Delay after TEMP_ERROR: 5 s" in out


def test_a094_len_over_1_uses_first_octet_and_warns():
    out = decode("40 03 07 00 01 A0 94 02 0A 80", vendor="Nxp")
    assert "      * Delay after TEMP_ERROR: 10 (No unit defined)" in out
    assert "      * Warning: Len 2, expected 1 (raw 0A80)" in out


def test_a098_ref_field_strength_high_nibble_of_byte3():
    # NXP UM: Reference field strength = byte3 Bit[4:7]
    out = decode("40 03 0D 00 01 A0 98 08 10 20 03 1F 0A 11 12 13", vendor="Nxp")
    assert "      * Ref. field strength: 1 A/m" in out


# A - Python caught up with JS (former known_diffs)

def test_set_config_rsp_reads_extended_id_as_2_octets():
    out = decode("40 02 04 09 01 A0 15", vendor="Nxp")
    assert "    * ID 0: DEFAULT_POWER (A015)" in out
    assert "Payload error" not in out


def test_a064_polling_delay_precedence():
    out = decode("40 03 08 00 01 A0 64 03 E8 03 05", vendor="Nxp")
    assert "      * Polling delay between 2 phases: 1.0 ms" in out


def test_a017_phase_parsed_as_hex():
    out = decode("40 03 07 00 01 A0 17 02 00 80", vendor="Nxp")
    assert "    * Phase: -8192.0 °" in out


# B6 - NXP VALUE_OF_CFG_PARA: 1-octet bit-field IDs with Len > 1

def test_cfg_para_bitfield_len_over_1_warns_and_uses_first_octet():
    out = decode("40 03 06 00 01 02 02 03 FF", vendor="Nxp")
    assert "    * Val: 00000011 (03)" in out
    assert "      * Warning: Len 2, expected 1 (raw 03FF)" in out


def test_cfg_para_bitfield_len_1_no_warning():
    out = decode("40 03 06 00 01 85 01 01", vendor="Nxp")
    assert "Warning" not in out


# B7 - NXP's own CORE_CONN_CREATE_RSP masks Conn ID to the low 4 bits (upper bits RFU)

def test_conn_create_rsp_conn_id_masked():
    out = decode("40 04 04 00 FF 01 12", vendor="Nxp")
    assert "  * Conn ID: 2 (Dynamically assigned by the NFCC)" in out
