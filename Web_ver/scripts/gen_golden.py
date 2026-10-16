"""Generate the golden corpus: hex -> exact Python decoder output.

Inputs:
  * every "Raw：`...`" example in ../Docs (Docs/nxp -> vendor "Nxp",
    Docs/nfc_forum_2_0 -> vendor "None"; nfc_forum_2_3 is not dispatchable)
  * tests/golden_inputs/<name>.json: [{"vendor", "hex", "prev": [hex, ...]}]
    for extra / stateful cases ("prev" packets are decoded first, output dropped)

Outputs: tests/golden/docs.json (docs examples) and tests/golden/<name>.json
(one per input file, so several people can add cases without touching each other's file).

Each case runs with the Python modules' global state reset to its import-time
values, so cross-packet state (HDLL_CMD, PWR_MODE_00, ...) only comes from "prev".

Usage:  python scripts/gen_golden.py            # regenerate everything
        python scripts/gen_golden.py <name> ...  # only these sources ("docs" or input file stem)
"""
import contextlib
import io
import json
import os
import re
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))  # NCI_Decoder repo root (Web_ver/..)
DOCS = os.path.join(REPO, "Docs")
TESTS = os.path.normpath(os.path.join(HERE, "..", "tests"))

sys.path.insert(0, REPO)
import nci_decoder  # noqa: E402,F401
from nci_decoder import Decoder_Main  # noqa: E402
import importlib  # noqa: E402

for pkg in ("nfc_forum_2_0_pkg", "Nxp_pkg"):
    importlib.import_module(f"{pkg}.__ctrl__")

# "Raw：`..`" and "Raw（description）：`..`"
RAW_RE = re.compile(r"Raw(?:\s*[（(][^）)\n]*[）)])?\s*[：:]\s*`([0-9A-Fa-f ]+)`")
DOC_VENDOR = {"nxp": "Nxp", "nfc_forum_2_0": "None"}


def _snapshot():
    """Module-level scalar globals of every decoder module (cross-packet state)."""
    snap = {}
    for name, mod in list(sys.modules.items()):
        f = getattr(mod, "__file__", None) or ""
        if not isinstance(mod, types.ModuleType) or not f.startswith(REPO):
            continue
        snap[name] = {k: v for k, v in vars(mod).items()
                      if not k.startswith("__") and isinstance(v, (str, int, float, bool))}
    return snap


def _restore(snap):
    for name, values in snap.items():
        mod = sys.modules.get(name)
        if mod is not None:
            for k, v in values.items():
                setattr(mod, k, v)


def _run(hex_str, vendor):
    raw = hex_str.replace(" ", "").upper()
    buf = io.StringIO()
    error = None
    try:
        with contextlib.redirect_stdout(buf):
            Decoder_Main.NFC_NCI_DECODER(len(raw) // 2, raw, vendor, "None", 2)
    except Exception as e:  # recorded, the JS port must not crash on these
        error = f"{type(e).__name__}: {e}"
    return buf.getvalue(), error


def docs_inputs():
    cases = []
    for sub, vendor in DOC_VENDOR.items():
        folder = os.path.join(DOCS, sub)
        for fn in sorted(os.listdir(folder)):
            if not fn.endswith(".md"):
                continue
            with open(os.path.join(folder, fn), encoding="utf-8") as f:
                for m in RAW_RE.finditer(f.read()):
                    cases.append({"vendor": vendor, "hex": m.group(1).strip(), "prev": [],
                                  "source": f"Docs/{sub}/{fn}"})
    return cases


def sources():
    srcs = {"docs": docs_inputs}
    folder = os.path.join(TESTS, "golden_inputs")
    for fn in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
        if fn.endswith(".json"):
            path = os.path.join(folder, fn)

            def load(path=path, fn=fn):
                with open(path, encoding="utf-8") as f:
                    cases = json.load(f)
                for c in cases:
                    c.setdefault("prev", [])
                    c.setdefault("source", f"golden_inputs/{fn}")
                return cases
            srcs[fn[:-5]] = load
    return srcs


def dedup(cases):
    seen, out = set(), []
    for c in cases:
        key = (c["vendor"], tuple(p.replace(" ", "").upper() for p in c["prev"]),
               c["hex"].replace(" ", "").upper())
        if key not in seen:
            seen.add(key)
            out.append(c)
    return out


def main(only):
    snap = _snapshot()
    os.makedirs(os.path.join(TESTS, "golden"), exist_ok=True)
    for name, load in sources().items():
        if only and name not in only:
            continue
        golden = []
        for c in dedup(load()):
            _restore(snap)
            for p in c["prev"]:
                _run(p, c["vendor"])
            output, error = _run(c["hex"], c["vendor"])
            golden.append({**c, "output": output, "error": error})
        path = os.path.join(TESTS, "golden", f"{name}.json")
        tmp = f"{path}.{os.getpid()}.tmp"  # atomic replace: safe when several runs overlap
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(golden, f, ensure_ascii=False, indent=1)
        os.replace(tmp, path)
        n_err = sum(1 for g in golden if g["error"])
        print(f"{path}: {len(golden)} cases ({n_err} raise in Python)")


if __name__ == "__main__":
    main(set(sys.argv[1:]))
