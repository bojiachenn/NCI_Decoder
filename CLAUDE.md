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

Output goes to `./dist`. There are no linters in this repo; run the pytest suite with:

```
pytest
```

## Configuration

`config.json` (next to `Decoder.py`) pre-fills the interactive prompts:
- `vendor` — drives two independent things off the same value: `"Nxp"` selects the NXP proprietary decode package (anything else falls back to the plain NFC Forum 2.0 decoder), and it also selects the mode-1 log-line profile from `log_profiles.py` (`"St"` gets the ST HAL profile, anything else gets the generic NXP-shaped `"<value>NciX"/"<value>NciR"` profile — so a custom keyword still works for any log that follows that same tag+length shape). When set to `"None"`, the tool prompts interactively instead.
- `chip_model` — passed through to handlers but not currently used to branch behavior.
- `filter` — space-separated keywords; in file mode, non-NCI log lines containing any keyword are passed through to the output unmodified (default `remain_all` keeps everything).

## Architecture

**Entry point (`Decoder.py`)** — the CLI menu. Mode 1 (file mode) scans each line of the input file(s) using a `log_profiles` profile (chosen by `config.json`'s `vendor`/typed keyword, see below), extracts the hex payload, and writes a decoded transcript to `NCI_output/<filename>_d.txt` (falls back to cp950 decoding for garbled bytes on non-matching lines). Mode 2 decodes one hex string typed at the prompt.

**`log_profiles.py`** (repo root) — recognizes NCI packets embedded in arbitrary log line formats, decoupled from `Decoder_Main.py`'s decode logic. `get_profile(decode_key)` returns a profile dict; `extract_candidate(line, profile)` tries to pull a packet (or fragment) out of one line. Two shapes exist:
- **Single-line profiles** (`sequence: None`, e.g. the default NXP-shaped `"<decode_key>NciX"`/`"<decode_key>NciR"` profile built by `build_default_profile`) — each matching line is a complete packet; length is self-computed as `len(hex)//2` (mirroring mode 2) rather than parsed from any vendor-printed length field.
- **Sequence-based profiles** (e.g. `PROFILES["st"]`, for ST HAL logs) — a packet too long for one line gets split across multiple lines sharing a `(#0000N)` sequence number, with an uppercase `Tx`/`Rx` marking the first segment and lowercase `tx`/`rx` marking continuations. `Decoder.py`'s `mode_1()` accumulates hex per sequence number in a `pending` dict until the running byte count satisfies the packet's own declared payload length, then decodes it; anything still incomplete (or explicitly redacted, e.g. ST's `(hidden)` placeholder) when the file ends is reported rather than silently dropped.

**Dispatch (`nci_decoder/Decoder_Main.py`, function `NFC_NCI_DECODER`)** — the only place that understands the NCI packet header. It parses octet 0 into Message Type (DATA/CMD/RSP/NTF) and Group ID (NCI Core / RF Management / NFCEE Management / Proprietary), validates the declared payload length, and either:
- prints DATA packets directly, or
- looks up `pkg.tbl_nci_ctrl[gid][oid][mt]` in the selected vendor package and calls that handler, or
- for NXP's 2-byte-header + CRC16 framing (used by the bootloader/download protocol), delegates to `pkg.HDLL(...)`.

Each handler's return value (hex chars consumed) is compared against the declared length to flag `Payload error!!`.

**Vendor selection (`nci_decoder/vendor_registry.py`)** — single source of truth for "which vendor string maps to which package". `resolve(vendor)` returns a `VendorPackage(pkg_dir, ctrl_module, table_module)`, falling back to the `nfc_forum_2_0_pkg` default for anything not explicitly registered (case-insensitive, mirrors `log_profiles.get_profile`'s explicit-override-else-default shape). `Decoder_Main.py` and `nci_decoder/__pkg_import__.py`'s `tbl_import(vendor, model)` both resolve through this registry via `importlib.import_module(...)` instead of a hardcoded if/else — **adding a vendor never requires editing either of those two files**, only registering an entry here (see "Adding a new vendor package" below).

**Vendor/spec packages (`nci_decoder/*_pkg/`)** — each package is a self-contained decoder for one spec/vendor and follows the same shape:
- `__ctrl__.py` — the `tbl_nci_ctrl` dispatch table: `{GID name: {OID hex: {"CMD"/"RSP"/"NTF": handler_fn}}}`.
- `__table__.py` — lookup tables (named `tbl_*`, referencing NFC Forum spec table numbers in comments) mapping raw hex values to human-readable enum names.
- `NCI_Core.py`, `RF_Management.py`, `NFCEE_Management.py` — one function per NCI message. Each takes the hex payload string and walks it with a running offset (`p_payload`, counted in hex chars, i.e. 2 per byte), printing each field via `NFC_table.tbl_*.get(value, "RFU")`, and returns the final offset. Several handlers collapse a raw ID byte into a range-bucket key (e.g. `'02-0F'`/`'10-7F'`/`'80-FE'`) before a second table lookup — use `nci_decoder/range_lookup.py`'s `find_range_key(table, value)` for this rather than hand-rolling another if/elif/else chain (that copy-pasted pattern caused 8 real bugs, fixed in commit `5f5cb72`).

Packages present:
- `nfc_forum_2_0_pkg` — baseline NFC Forum NCI 2.0 decoder; the registry's default.
- `nfc_forum_2_3_pkg` — NCI 2.3 additions. **Deliberately not wired up.** This is a spec-*version* delta of the default forum package, not a new *vendor* — orthogonal to what `vendor_registry.py` models, and folding it in would force a premature design decision (a `mode`/version axis vs. overloading the vendor key). Needs its own follow-up design before it's dispatchable.
- `Nxp_pkg` — NXP's proprietary superset: re-exports/extends the forum handlers, adds the `Proprietary` GID table, and adds `HDLL.py` (the NXP secure-download/bootloader frame protocol, separate framing from normal NCI control packets). Predates `template_pkg`'s delegation convention, so a lot of it is a forked copy of the forum package rather than thin delegation — left as-is, not a pattern to copy for new vendors.
- `template_pkg` — working scaffold for adding a new vendor package (see `template_pkg/README.md` and "Adding a new vendor package" below).

**Import path setup** — `nci_decoder/__init__.py` appends `nci_decoder/vendor_registry.py`'s `all_pkg_dirs()` (plus `nfc_forum_2_3_pkg`, kept importable but not dispatchable) to `sys.path` at import time, `__file__`-relative — which is why submodules use flat imports like `from Nxp_pkg import NCI_Core` instead of `nci_decoder.Nxp_pkg...`.

**`notepad++_form/NCI_Log.xml`** — a Notepad++ User Defined Language definition for syntax-highlighting raw/decoded NCI logs. Its keyword lists are a manually maintained mirror of the handler function names in `__ctrl__.py`/`Proprietary.py` — update it when adding new commands if log highlighting should stay in sync.

## Adding a new decodable message

1. Add the field-parsing function to the appropriate `*_Management.py`/`NCI_Core.py`/`Proprietary.py` file (or create a vendor package from `template_pkg` if it's vendor-specific).
2. Register it under the correct GID/OID/message-type in that package's `__ctrl__.py`.
3. Add any new enum values to `__table__.py`.

## Adding a new vendor package

Full steps are in `nci_decoder/template_pkg/README.md` — summary: copy `template_pkg/` to a new name, override only the handlers that genuinely differ (every function already forwards `vendor`/`model` to its forum delegate), then register it in `nci_decoder/vendor_registry.py`. That registry entry is the **only** file outside the new package's own directory that needs a change to make it dispatchable — `Decoder_Main.py`, `__pkg_import__.py`, and `__init__.py`'s `sys.path` all resolve through it automatically.

One manual step still survives the registry, though: **`NCI_Decoder.spec`'s `pathex`/`hiddenimports`** must list the new package's modules explicitly for the packaged `.exe` to include them — PyInstaller's static analysis can't see the dynamic `importlib.import_module()` calls the registry uses. This is an accepted, documented limitation, not automated.

## Adding a new mode-1 log format

Add an entry to `log_profiles.PROFILES` (or a new `get_profile` branch) describing: a `trigger` substring to cheaply skip irrelevant lines, how to tell direction apart (a single `directions` list, or `start_directions`/`continue_directions` if the format can split one packet across multiple lines), and a `region` locator (`after_last_literal` or `after_regex_end`) telling the shared `HEX_RUN_RE` where to look for the hex bytes on that line — this is usually 10-15 lines of data, no changes needed to `Decoder.py`'s loop or `Decoder_Main.py`.
