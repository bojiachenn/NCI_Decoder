"""Drive Decoder.mode_1() (file mode) end-to-end on temp log files.

input() and clear_terminal are monkeypatched, cwd is a temp dir (mode_1 writes
NCI_output/<name>_d.txt relative to cwd), same approach as
web/scripts/gen_log_golden.py.
"""
import builtins
import contextlib
import io

import pytest

import Decoder
from nci_decoder import Decoder_Main

# NXP HDLL frames (2-byte header + op code + payload + CRC-16-CCITT-FALSE), see Nxp_pkg/__ctrl__.py HDLL()
HDLL_GET_VERSION_CMD = "0004F10000006EEF"   # sets HDLL_CMD = 'F1'
HDLL_DL_OK_RSP = "0004000000008716"         # DL_OK: decoded according to the previous op code


def _nxp_line(direction, hex_str):
    tag = "NxpNciX" if direction == "TX" else "NxpNciR"
    return f"10-15 12:00:00.000  1234  5678 D NxpNciX : {tag}: len = {len(hex_str)//2} > {hex_str}\n"


def _run_mode_1(monkeypatch, tmp_path, paths, vendor="Nxp", filt="remain_all"):
    answers = iter([str(p) for p in paths] + ["-1"])
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(builtins, "input", lambda *a: next(answers))
    monkeypatch.setattr(Decoder, "clear_terminal", lambda: None)
    monkeypatch.setattr(Decoder, "config", {"vendor": vendor, "chip_model": "None", "filter": filt})
    with contextlib.redirect_stdout(io.StringIO()):
        Decoder.mode_1()


def _output(tmp_path, name):
    raw = (tmp_path / "NCI_output" / (name + "_d.txt")).read_bytes()
    return raw.decode("utf-8")   # must be valid UTF-8 (raises otherwise)


@pytest.fixture(autouse=True)
def _reset_nxp_state():
    Decoder_Main.reset_state("Nxp")
    yield
    Decoder_Main.reset_state("Nxp")


def _write(tmp_path, name, text):
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return p


def test_non_ascii_passthrough_line_preserved_and_output_is_utf8(monkeypatch, tmp_path):
    marker = "中文測試 ✓ kaomoji (o´∀`o) 日本語"
    log = _write(tmp_path, "a.log", f"plain line {marker}\n" + _nxp_line("TX", "20000101"))
    _run_mode_1(monkeypatch, tmp_path, [log])
    out = _output(tmp_path, "a.log")
    assert f"plain line {marker}" in out.splitlines()
    assert "CORE_RESET_CMD" in out
    assert "Error" not in out


@pytest.mark.parametrize("filt", ["   ", "\t"])
def test_whitespace_only_filter_from_config_keeps_all(monkeypatch, tmp_path, filt):
    log = _write(tmp_path, "b.log", "some other line\n" + _nxp_line("TX", "20000101"))
    _run_mode_1(monkeypatch, tmp_path, [log], filt=filt)   # used to raise IndexError
    out = _output(tmp_path, "b.log")
    assert "Filter: ['remain_all']" in out
    assert "some other line" in out
    assert "CORE_RESET_CMD" in out


def _two_file_hdll_run(monkeypatch, tmp_path):
    f1 = _write(tmp_path, "f1.log", _nxp_line("TX", HDLL_GET_VERSION_CMD))
    f2 = _write(tmp_path, "f2.log", _nxp_line("RX", HDLL_DL_OK_RSP))
    _run_mode_1(monkeypatch, tmp_path, [f1, f2])
    return _output(tmp_path, "f1.log"), _output(tmp_path, "f2.log")


def test_state_reset_between_files(monkeypatch, tmp_path):
    out1, out2 = _two_file_hdll_run(monkeypatch, tmp_path)
    assert "DL_GET_VERSION" in out1
    assert "DL_STATUS_OK" in out2
    # with the default pre-op ('00') DL_OK has no version fields
    assert "HW version" not in out2
    for out in (out1, out2):
        assert "Error" not in out


def test_state_leaks_between_files_without_reset(monkeypatch, tmp_path):
    # Control: proves the test above actually exercises cross-file state.
    monkeypatch.setattr(Decoder_Main, "reset_state", lambda vendor: None)
    _, out2 = _two_file_hdll_run(monkeypatch, tmp_path)
    assert "HW version" in out2
