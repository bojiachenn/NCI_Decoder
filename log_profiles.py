import re

# Shared extraction primitive: pulls hex bytes out of a located region,
# handling both contiguous ("20000100") and space-separated ("20 00 01 01") styles.
HEX_RUN_RE = re.compile(r'(?:[0-9A-Fa-f]{2}\s*)+')

# First two whitespace-separated tokens are the timestamp in both known formats
# (Android logcat "MM-DD HH:MM:SS.mmm" style).
TS_RE = re.compile(r'^(\S+)\s+(\S+)')

PROFILES = {
    "st": {
        "trigger": "StNfcHal",
        "sequence": re.compile(r"\(#([0-9A-Fa-f]+)\)"),
        # Uppercase Tx/Rx = first segment of a new packet; lowercase tx/rx = continuation
        # of the same packet (ST HAL splits long packets across multiple log lines).
        "start_directions": [("TX", re.compile(r"\bTx\b")), ("RX", re.compile(r"\bRx\b"))],
        "continue_directions": [("TX", re.compile(r"\btx\b")), ("RX", re.compile(r"\brx\b"))],
        "region": {"mode": "after_regex_end", "pattern": re.compile(r"\b[TtRr]x\b")},
        "redacted_markers": ["(hidden)"],
    },
}


def build_default_profile(decode_key):
    """NXP-style profile: '<decode_key>NciX'/'<decode_key>NciR' tags, contiguous hex
    after the last '>', explicit 'len = N' field which we ignore (length is
    self-computed from the extracted hex, same as mode_2). decode_key is whatever
    the user configured/typed (historically "Nxp", but works for any prefix that
    follows this exact shape - not hardcoded to NXP specifically)."""
    return {
        "trigger": decode_key + "Nci",
        "directions": [
            ("TX", re.compile(re.escape(decode_key) + "NciX")),
            ("RX", re.compile(re.escape(decode_key) + "NciR")),
        ],
        "region": {"mode": "after_last_literal", "marker": ">"},
        "redacted_markers": [],
        "sequence": None,
    }


def get_profile(decode_key):
    """Pick the log profile for a given vendor/keyword string. 'st' gets the
    fragment-aware ST HAL profile; everything else falls back to the generic
    NXP-shaped '<decode_key>NciX/NciR' profile that already worked before this
    module existed, so existing configs/custom keywords keep working unchanged."""
    if decode_key.lower() == "st":
        return PROFILES["st"]
    return build_default_profile(decode_key)


def _locate_region(line, region_cfg):
    mode = region_cfg["mode"]
    if mode == "after_last_literal":
        marker = region_cfg["marker"]
        idx = line.rfind(marker)
        return line[idx + len(marker):] if idx != -1 else ""
    elif mode == "after_regex_end":
        m = region_cfg["pattern"].search(line)
        return line[m.end():] if m else ""
    return ""


def _extract_ts(line):
    m = TS_RE.match(line)
    return f"{m.group(1)} {m.group(2)}" if m else ""


def _extract_hex(region):
    """Pull the hex bytes out of a located region and strip ALL whitespace
    (not just literal spaces) - HEX_RUN_RE's trailing \\s* can swallow a
    line's terminating newline, which must not end up embedded in the hex
    string or every length calculation downstream breaks."""
    hex_match = HEX_RUN_RE.search(region)
    return "".join(hex_match.group().split()) if hex_match else ""


def extract_candidate(line, profile):
    """Try to recognize an NCI packet (or fragment of one) in a single log line.

    Returns None if the line doesn't belong to this profile at all (caller should
    fall through to the existing filter-keyword passthrough). Otherwise returns a
    dict describing what was found; shape depends on whether the profile uses
    sequence-based multi-line assembly (see PROFILES' "sequence" key).
    """
    if profile["trigger"] not in line:
        return None

    ts = _extract_ts(line)

    if profile.get("sequence") is None:
        direction = None
        for name, pat in profile["directions"]:
            if pat.search(line):
                direction = name
                break
        if direction is None:
            return None

        region = _locate_region(line, profile["region"])
        if any(marker in region for marker in profile["redacted_markers"]):
            return {"kind": "redacted", "direction": direction, "ts": ts}

        hex_str = _extract_hex(region)
        return {"kind": "candidate", "direction": direction, "ts": ts, "hex": hex_str}

    # Sequence-based (fragmentable) profile.
    seq_match = profile["sequence"].search(line)
    if seq_match is None:
        return None
    seq = seq_match.group(1)

    is_start = any(pat.search(line) for _, pat in profile["start_directions"])
    is_continue = any(pat.search(line) for _, pat in profile["continue_directions"])
    if not is_start and not is_continue:
        return None

    direction = None
    for name, pat in (profile["start_directions"] if is_start else profile["continue_directions"]):
        if pat.search(line):
            direction = name
            break

    region = _locate_region(line, profile["region"])
    if any(marker in region for marker in profile["redacted_markers"]):
        return {"kind": "redacted", "seq": seq, "direction": direction, "ts": ts,
                "is_start": is_start, "is_continue": is_continue}

    hex_str = _extract_hex(region)
    return {"kind": "candidate", "seq": seq, "direction": direction, "ts": ts,
            "is_start": is_start, "is_continue": is_continue, "hex": hex_str}
