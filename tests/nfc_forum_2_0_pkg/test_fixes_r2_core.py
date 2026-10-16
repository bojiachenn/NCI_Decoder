"""Bug-fix round 2 regressions for nfc_forum_2_0_pkg/NCI_Core.py (kept in sync with web/src/handlers/forum20/nciCore.js)."""
from tests.helpers import decode_lines


# ---- B6: 1-octet bit-field config parameter with Len > 1 ----

def test_bitfield_param_len_gt_1_decodes_first_octet_and_warns():
	lines = decode_lines("20 02 05 01 3C 02 85 21")
	assert "    * Val: 10000101 (85)" in lines
	assert "     ~ Frame Waiting time Integer: 8 (1000)" in lines
	assert "      * Warning: Len 2, expected 1 (raw 8521)" in lines


def test_bitfield_param_len_3_warns():
	lines = decode_lines("40 03 0B 00 02 02 02 03 FF 85 03 01 02 03")
	assert "    * Val: 00000011 (03)" in lines
	assert "      * Warning: Len 2, expected 1 (raw 03FF)" in lines
	assert "    * Val: 00000001 (01)" in lines
	assert "      * Warning: Len 3, expected 1 (raw 010203)" in lines


def test_bitfield_param_len_1_has_no_warning():
	lines = decode_lines("20 02 04 01 3C 01 85")
	assert not any("Warning" in l for l in lines)


# ---- B7: Conn ID masked to low 4 bits ----

def test_conn_create_rsp_conn_id_masked():
	lines = decode_lines("40 04 04 00 FF 01 F3")
	assert "  * Conn ID: 3 (Dynamically assigned by the NFCC)" in lines


def test_conn_close_cmd_conn_id_masked():
	lines = decode_lines("20 05 01 F1")
	assert "  * Conn ID: 1 (Static: DH -- HCI Network)" in lines


def test_conn_credits_ntf_conn_id_masked():
	lines = decode_lines("60 06 05 02 01 01 A3 02")
	assert "    * Conn ID: 1 (Static: DH -- HCI Network)" in lines
	assert "    * Conn ID: 3 (Dynamically assigned by the NFCC)" in lines


def test_interface_error_ntf_conn_id_masked():
	lines = decode_lines("60 08 02 00 80")
	assert "  * Conn ID: 0 (Static: DH -- Remote NFC Endpoint)" in lines


# ---- Phase A (Python caught up with JS) ----

def test_reset_ntf_label_and_no_empty_mfg_info():
	lines = decode_lines("60 00 05 01 00 20 00 00")
	assert any(l.startswith("  * Reset Trigger: ") for l in lines)
	assert not any("Manufacturer Specific Info" in l for l in lines)


def test_init_rsp_sizes_little_endian():
	lines = decode_lines("40 01 15 00 11 1E 0E 00 08 00 02 FF FF 01 01 00 03 01 00 02 00 03 01 01")
	assert "  * Max Routing Table Size: 512 (0002)" in lines
	assert "  * Max NFC-V RF Frame Size: 1 (0100)" in lines


def test_power_sub_state_3_is_locked():
	lines = decode_lines("20 09 01 03")
	assert lines[-4:-1] == [
		"  * Power State: Switched On Sub-State 3",
		"    * Screen: Off",
		"    * Device: Locked",
	]


def test_lb_fwi_adc_fo_shows_b3():
	# 0x08 = 00001000 -> b4..b1 = 1000, b3 (index 4) = 1
	lines = decode_lines("40 03 05 00 01 3C 01 08")
	assert "     ~ b3 of ADC Coding field of SENSB_RES (Byte 12) as defined in [DIGITAL] (1)" in lines


def test_ln_wt_is_exponent():
	lines = decode_lines("40 03 08 00 02 60 01 04 60 01 0F")
	assert "     ~ Waiting Time defined in [DIGITAL]: RWT = 256*16/fc * 2^WT = 4.833 ms" in lines
	assert "     ~ Waiting Time defined in [DIGITAL]: RFU (WT > 14)" in lines


def test_bit_rate_rfu_vs_proprietary():
	lines = decode_lines("40 03 08 00 02 18 01 07 18 01 85")
	assert "    * Val: RFU (07)" in lines
	assert "    * Val: For proprietary use (85)" in lines


def test_conn_create_cmd_nfcee_id_and_unknown_type():
	lines = decode_lines("20 04 06 03 01 01 02 80 00")
	assert any(l.startswith("      * NFCEE ID: HCI-NFCEE (80)") for l in lines)
	lines = decode_lines("20 04 07 00 02 05 01 AA A0 00")
	assert "      ~ Type 05: RFU" in lines
	assert lines.count("    * Val: AA") == 1
	assert "      ~ Type A0: For proprietary use" in lines
