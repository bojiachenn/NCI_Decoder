# NCI_Decoder
This is the decoder for NFC Controller Interface (NCI).

1. First, you must get a "raw data" in hex code or a "Log File" from your NFC device.

2. Execute "python Decoder.py" on your Terminal.

3. Select decode mode "file mode" or "raw data mode".

4. Check the result.

Package into executable file with pyinstaller

1. pyinstaller NCI_Decoder.spec

2. Check the .exe file in ./dist

## config.json settings

`config.json` (next to `Decoder.py`) pre-fills the interactive menu's prompts so you don't have to type them every run:

| Key | Meaning | Example |
|---|---|---|
| `vendor` | Drives two things at once: (1) which vendor decode package is used to interpret packets, and (2) which log-line recognition rule file mode (mode 1) uses to find packets in a log file (see below). Set to `"None"` to be prompted for a keyword interactively instead. | `"Nxp"`, `"St"` |
| `chip_model` | Passed through to decode handlers; not currently used to change any decoding behavior. | `"None"` |
| `filter` | Space-separated keywords. In file mode, any log line that isn't recognized as an NCI packet is still printed as-is if it contains one of these keywords (case-insensitive). `"remain_all"` prints every non-packet line unchanged. | `"remain_all"`, `"nxpncir nxpncix"` |

Example:
```json
{
    "vendor": "Nxp",
    "chip_model": "None",
    "filter": "remain_all"
}
```

## How mode 1 (file mode) recognizes packets in a log

Mode 1 doesn't scan for one hardcoded log format — the recognition rules live in `log_profiles.py`, keyed off `config.json`'s `vendor` value:

- `vendor = "St"` uses the ST (STMicroelectronics) NFC HAL log profile: packets are identified by a `(#0000N)` sequence number; an uppercase `Tx`/`Rx` marks the start of a packet and a lowercase `tx`/`rx` marks a continuation segment (ST's HAL splits long packets across multiple log lines). The tool automatically reassembles the segments before decoding.
- Any other value (including `"Nxp"`, or a custom keyword you type when `vendor` is `"None"`) uses the default profile: it looks for `"<vendor>NciX"` (DH → NFCC) / `"<vendor>NciR"` (DH ← NFCC) tags and reads the hex bytes that follow, whether they're written with or without spaces.

If your device's log doesn't match either shape (a different chip vendor, or a different product line's logging style), you don't need to touch `Decoder.py` — add a new entry to the `PROFILES` dict in `log_profiles.py` instead. Each entry is usually just 10-15 lines of declarative data:

- `trigger`: a substring used to cheaply skip lines that clearly aren't relevant (e.g. the log's tag name).
- `directions` (or `start_directions` / `continue_directions`, if a packet can be split across multiple lines): how to tell whether a line is outgoing or incoming.
- `region`: where in the line to look for the hex bytes — `after_last_literal` locates text after the last occurrence of a character (e.g. NXP's `>`), `after_regex_end` locates text after a regex match ends (e.g. ST's `Tx`/`Rx` word itself).
- `redacted_markers` (optional): placeholder text a log uses when it deliberately hides payload data (e.g. `"(hidden)"`) — lines matching this are reported as redacted instead of being mis-decoded or erroring out.

Once added, set `config.json`'s `vendor` to the name you used and mode 1 will pick it up automatically — no other code changes needed. 
