# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Language

請一律使用繁體中文與使用者對話（程式碼、identifier、commit message 等仍維持原文）。

## What this is

A terminal tool that decodes NFC Controller Interface (NCI) protocol packets — either a single raw hex string or full log files captured from an NFC device — into a human-readable breakdown of each field, per the NFC Forum NCI spec plus NXP vendor-proprietary extensions.

## Commands

Run from this directory (`Decoder.py`'s relative imports depend on the CWD):

```
python Decoder.py
```

Interactive menu: `1` decode a log file or directory of files, `2` decode a single raw hex string, `3` exit, `r` reload `config.json`.

Build the standalone Windows executable:

```
pyinstaller NCI_Decoder.spec
```

Output goes to `./dist`. There are no automated tests or linters in this repo.

## Configuration

`config.json` (next to `Decoder.py`) pre-fills the interactive prompts:
- `vendor` — `"Nxp"` selects the NXP proprietary decode package; anything else falls back to the plain NFC Forum 2.0 decoder. When set to `"None"`, the tool prompts interactively instead.
- `chip_model` — passed through to handlers but not currently used to branch behavior.
- `filter` — space-separated keywords; in file mode, non-NCI log lines containing any keyword are passed through to the output unmodified (default `remain_all` keeps everything).

## Architecture

**Entry point (`Decoder.py`)** — the CLI menu. Mode 1 (file mode) scans each line of the input file(s) for markers `"<vendor>NciX"` (host→controller) / `"<vendor>NciR"` (controller→host, e.g. `NxpNciX`/`NxpNciR`), extracts the hex payload from the matched line, and writes a decoded transcript to `NCI_output/<filename>_d.txt` (falls back to cp950 decoding for garbled bytes on non-matching lines). Mode 2 decodes one hex string typed at the prompt.

**Dispatch (`nci_decoder/Decoder_Main.py`, function `NFC_NCI_DECODER`)** — the only place that understands the NCI packet header. It parses octet 0 into Message Type (DATA/CMD/RSP/NTF) and Group ID (NCI Core / RF Management / NFCEE Management / Proprietary), validates the declared payload length, and either:
- prints DATA packets directly, or
- looks up `pkg.tbl_nci_ctrl[gid][oid][mt]` in the selected vendor package and calls that handler, or
- for NXP's 2-byte-header + CRC16 framing (used by the bootloader/download protocol), delegates to `pkg.HDLL(...)`.

Each handler's return value (hex chars consumed) is compared against the declared length to flag `Payload error!!`.

**Vendor/spec packages (`nci_decoder/*_pkg/`)** — each package is a self-contained decoder for one spec/vendor and follows the same shape:
- `__ctrl__.py` — the `tbl_nci_ctrl` dispatch table: `{GID name: {OID hex: {"CMD"/"RSP"/"NTF": handler_fn}}}`.
- `__table__.py` — lookup tables (named `tbl_*`, referencing NFC Forum spec table numbers in comments) mapping raw hex values to human-readable enum names.
- `NCI_Core.py`, `RF_Management.py`, `NFCEE_Management.py` — one function per NCI message. Each takes the hex payload string and walks it with a running offset (`p_payload`, counted in hex chars, i.e. 2 per byte), printing each field via `NFC_table.tbl_*.get(value, "RFU")`, and returns the final offset.

Packages present:
- `nfc_forum_2_0_pkg` — baseline NFC Forum NCI 2.0 decoder; the default when `vendor` isn't `"Nxp"`.
- `nfc_forum_2_3_pkg` — NCI 2.3 additions. **Not currently wired up** — `Decoder_Main.py` and `__pkg_import__.py` only branch between `"Nxp"` and the 2.0 package, so this package is dead code until that dispatch is extended.
- `Nxp_pkg` — NXP's proprietary superset: re-exports/extends the forum handlers, adds the `Proprietary` GID table, and adds `HDLL.py` (the NXP secure-download/bootloader frame protocol, separate framing from normal NCI control packets).
- `template_pkg` — scaffold for adding a new vendor package: each function just calls `Origin.<name>(raw)` from the forum package; copy this when a new vendor needs its own proprietary extensions, then override only the functions that actually differ.

**`nci_decoder/__pkg_import__.py`** (`tbl_import(vendor, model)`) — chooses which `__table__` module a handler should read enum values from (NXP vs. forum default). Handlers call this themselves rather than receiving the table as an argument.

**Import path setup** — `nci_decoder/__init__.py` appends each vendor/spec package directory to `sys.path` at import time, which is why submodules use flat imports like `from Nxp_pkg import NCI_Core` instead of `nci_decoder.Nxp_pkg...`. This only works when the process is launched with this directory as the working directory (matches the README's `python Decoder.py` usage).

**`notepad++_form/NCI_Log.xml`** — a Notepad++ User Defined Language definition for syntax-highlighting raw/decoded NCI logs. Its keyword lists are a manually maintained mirror of the handler function names in `__ctrl__.py`/`Proprietary.py` — update it when adding new commands if log highlighting should stay in sync.

## Adding a new decodable message

1. Add the field-parsing function to the appropriate `*_Management.py`/`NCI_Core.py`/`Proprietary.py` file (or create a vendor package from `template_pkg` if it's vendor-specific).
2. Register it under the correct GID/OID/message-type in that package's `__ctrl__.py`.
3. Add any new enum values to `__table__.py`.
