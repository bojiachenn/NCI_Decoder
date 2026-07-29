import contextlib
import io

from nci_decoder import Decoder_Main


def decode(hex_str, vendor="None", model="None", mode=2):
    """Call NFC_NCI_DECODER directly and capture everything it prints.

    Mirrors what Decoder.py's mode_1/mode_2 do: normalize whitespace/case and
    self-compute the byte length from the hex string (same as mode_2's own
    logic), rather than trusting any vendor-printed length field.

    mode=2 (default) matches single-hex-string decoding (no raw-echo line);
    pass mode=1 if a test needs to assert on the file-mode raw-echo behavior.

    Deliberately does not swallow exceptions - KeyError for an unmapped
    GID/OID/MT combination (Decoder_Main.py's control-packet branch) must
    propagate to the caller so tests can assert on it with pytest.raises.
    Decoder_Main prints "<< ERROR_NOT_FOUND >>" plus the raw hex before
    raising, so on exception the partial output is stashed on the exception
    object as `captured_output` (e.g. `exc_info.value.captured_output`) since
    the normal return path never executes.
    """
    raw = hex_str.replace(" ", "").upper()
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            Decoder_Main.NFC_NCI_DECODER(len(raw) // 2, raw, vendor, model, mode)
    except Exception as e:
        e.captured_output = buf.getvalue()
        raise
    return buf.getvalue()


def decode_lines(hex_str, **kwargs):
    return decode(hex_str, **kwargs).splitlines()
