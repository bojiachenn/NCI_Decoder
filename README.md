# NCI_Decoder
This is the decoder for NFC Controller Interface (NCI).

The repo contains three ways to use / read about the decoder:

| Folder | What it is |
|---|---|
| `Decoder.py`, `nci_decoder/` | The original Python command-line decoder (also packaged as a Windows `.exe`) |
| [`Web_ver/`](Web_ver/) | Browser version of the same decoder — no Python or install needed |
| [`Docs/`](Docs/README.md) | Reference docs: payload layout of every NCI message, all lookup tables, known issues |

## Command-line decoder

1. First, you must get a "raw data" in hex code or a "Log File" from your NFC device.

2. Execute "python Decoder.py" on your Terminal.

3. Select decode mode "file mode" or "raw data mode".

4. Check the result.

Package into executable file with pyinstaller

1. pyinstaller NCI_Decoder.spec

2. Check the .exe file in ./dist

File mode writes `NCI_output/<filename>_d.txt` (UTF-8). Non-NCI log lines are copied through unchanged, so Chinese / other non-ASCII text in logs is preserved.

## Web version (`Web_ver/`)

A JavaScript port of the decoder that runs entirely in the browser. Log files are processed locally and never uploaded.

**Use it:** double-click [`Web_ver/dist/index.html`](Web_ver/dist/index.html). It is a single self-contained file (code, styles and the `Docs/` content are all embedded), so you can also copy it to a colleague or put it on any web server. No Node.js or Python required.

The **Vendor** selector (top right) works like `config.json`'s `vendor`: `NFC Forum NCI 2.0` (default) or `NXP` (adds NXP proprietary commands and the HDLL download protocol).

| Page | How to use |
|---|---|
| **Decode** | Paste raw hex (spaces, `0x` and commas are fine). One packet per line — lines are decoded in order, so packets that depend on an earlier one (e.g. an HDLL command followed by its `DL_OK` response) decode correctly. Hover a field to highlight its bytes; click a command or `tbl_*` name to open its documentation. Switch between structured and plain-text (CLI-identical) output, copy the result, or copy a share link. |
| **Log** | Drag & drop (or choose / paste) one or more logcat files. Leave **Decode keyword** as `auto` to detect the format automatically (NXP `NxpNciX`/`NxpNciR`, or ST `StNfcHal: (#N) [LL/UL] Tx/Rx`); NXP logs are then decoded with the NXP vendor. Filter by CMD/RSP/NTF/DATA/HDLL, errors only, or text search, expand any packet for the field breakdown, and download `<file>_d.txt` in the same format as the CLI. |
| **Reference** | Browse everything in `Docs/`. Search by command name, header hex (e.g. `61 05`) or table name. |

The web and Python decoders print identical text for the same packet (enforced by tests), so you can use whichever is more convenient.

**Develop / rebuild** (needs Node.js), from `Web_ver/`:

```
npm install
npm run dev        # http://localhost:5173
npm test           # compares JS output with the Python decoder (golden tests)
npm run build      # regenerates dist/index.html
```

When a Python handler changes, make the same change in `Web_ver/src/handlers/`, regenerate the comparison data with `python Web_ver/scripts/gen_golden.py`, run both `pytest` and `npm test`, then `npm run build` and commit the new `dist/index.html`. See [`Web_ver/README.md`](Web_ver/README.md) and [`Web_ver/PORTING.md`](Web_ver/PORTING.md) for details.

## Documentation (`Docs/`)

Markdown reference for every message the decoder understands (written in Traditional Chinese). Start at [`Docs/README.md`](Docs/README.md), which explains the NCI packet header and links to:

| File | Contents |
|---|---|
| `Docs/nfc_forum_2_0/NCI_Core.md`, `RF_Management.md`, `NFCEE_Management.md` | NFC Forum NCI 2.0 messages: payload fields, how each is parsed, example raw hex + decoder output, implementation notes |
| `Docs/nfc_forum_2_0/Tables.md` | All `tbl_*` lookup tables (value → meaning) and which messages use them |
| `Docs/nxp/*.md` | The same for the NXP package, plus `Proprietary.md` (GID 0xF commands) and `HDLL.md` (download / bootloader frames) |
| `Docs/nfc_forum_2_3/README.md` | What NCI 2.3 adds on top of 2.0 (that package is not wired into the decoder yet) |

Every example output in the docs is the decoder's real output, and each section links to the handler's source line. The same content is available, searchable, on the web version's **Reference** page.

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
