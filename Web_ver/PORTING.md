# Porting Python handlers to JS — conventions

Source of truth for behaviour: the Python decoder `../nci_decoder/<pkg>/*.py` (same repo). Python and JS must print identical text — change both together.
Field layouts / known bugs: `../Docs/<pkg>/*.md` (sections "Payload 格式" and "實作備註").

## Handler shape

```js
// src/handlers/<vendor>/<file>.js
const handlers = {
  // 20 00
  CORE_RESET_CMD(r, out, ctx) {
    out.enumField(r, 1, 'Reset Type', 'tbl_cfg_status');
  },
};
export default handlers;
```

- Key = exact Python function name (it is what `src/core/ctrl_spec.js` dispatches to and the docs anchor).
- `r` (`src/core/reader.js`) — byte cursor over the payload (header already stripped).
  `r.hex(n)` → uppercase hex string, `r.u8()`, `r.u16le()`, `r.u16be()`, `r.uintLE(n)`, `r.rest()`, `r.remaining`, `r.abs`, `r.sub(n)`.
  Reading past the end throws `DecodeError` → the decoder prints `Error: Payload too short ...`. Don't guard reads that Python didn't guard.
- `out` (`src/core/out.js`) — collects lines. Each line must be **exactly the text Python's print() produces**
  (remember `print(a, b)` inserts one space; `end=''` joins lines). Helpers:
  - `out.line(text, {start, end, table})` — raw line. Pass `start = r.abs` captured before reading and `end = r.abs` after, so the UI can highlight bytes. Lines without a byte range are fine (headings).
  - `out.kv(level, label, value, meta)` → `'  '.repeat(level) + '* label: value'`
  - `out.hexField(r, level, label, n)` → `* label: HEX`
  - `out.enumField(r, level, label, tableName, n=1)` → `* label: MEANING (HEX)`, records `table` meta.
  - `out.blank()` for `print("")`.
- `ctx` (`src/core/context.js`) — `ctx.t('tbl_x')` table object, `ctx.lookup('tbl_x', hex)` (= Python `.get(v,"RFU")` + range keys), `ctx.state` for cross-packet state that Python keeps in module globals (HDLL_CMD, PWR_MODE_00, TEST_ID_3F, ...). Initialise lazily: `ctx.state.HDLL_CMD ??= '00'`.
- Tables come from `src/data/tables.<vendor>.json` (exported from Python by `scripts/export_tables.py`, never hand-edit). Tables whose Python keys are ints (e.g. `tbl_pwr_state`, `tbl_nfcc_feat_oct1`) have decimal-string keys: `ctx.t('tbl_pwr_state')['5']`.
- Python `int(x)` on a hex string where the field is hex is a **bug** → use base 16 and record a known diff (below).
- Local dicts defined inside a Python function → copy them as local constants in the JS file.
- Helpers shared between handlers (e.g. `VALUE_OF_CFG_PARA`, `RF_TECH_SPEC_PARA`, `LISTEN_MODE_ROUTING_INFO`) → named exports, so the NXP files can reuse them.
- The decoder checks `r.pos === payload length` after the handler and prints the `Payload error!!` block itself — don't print it in handlers, and don't return anything.

### NXP files
Python `Nxp_pkg` handlers that just call `Origin.X(raw, "nxp")` → reuse the forum handler: the forum code already reads tables through `ctx`, which is the NXP table set when vendor = nxp.

```js
import forum from '../forum20/nciCore.js';
const handlers = { ...forum, CORE_RESET_NTF(r, out, ctx) { /* NXP-specific */ } };
export default handlers;
```

## Bug-fix policy (user decision: the JS version fixes known bugs)

Reproduce Python output exactly, **except** for genuine bugs (crashes, hex parsed as decimal, wrong table, range key not resolved, wrong offset/bit, wrong label). Fix those to the NCI-spec-correct behaviour, then record every golden case whose output therefore changes in **your own** file `tests/known_diffs/<your-area>.json`:

```json
[{ "vendor": "None", "hex": "61 05 ...", "prev": [], "reason": "Credits parsed as hex, Python used int() base 10" }]
```

`vendor` is `"None"` for forum20 cases and `"Nxp"` for NXP — copy it from the golden case. Range-key fixes in `lookup()` are already global, so cases that change only because of them still go into known_diffs, with reason "range key resolved".

Cosmetic differences (missing `)`, extra spaces, trailing spaces) are already ignored by the comparison — fix them freely without an entry.

## Tests

- `npx vitest run` — whole suite. Filter: `npx vitest run -t "CORE_RESET"` matches the test name (`[vendor] hex <source>`).
- Golden data: `tests/golden/*.json`, generated from the Python decoder by `python scripts/gen_golden.py`.
  - `docs.json` = every `Raw：` example in ../Docs (don't regenerate unless needed; it's shared).
  - Add your own cases (edge cases, stateful sequences with `prev`) in `tests/golden_inputs/<your-area>.json` and run `python scripts/gen_golden.py <your-area>` → writes `tests/golden/<your-area>.json`. Only touch your own files.
- Cases where Python raises: the JS decoder must not throw (it prints an `Error:` line instead); text isn't compared.
- Goal: every golden case for your handlers passes or is listed in your known_diffs with a reason.
