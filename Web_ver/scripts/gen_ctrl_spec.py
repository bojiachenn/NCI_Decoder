"""Regenerate src/core/ctrl_spec.js (handler names per GID/OID/MT) from the Python
__ctrl__.py tbl_nci_ctrl tables.

Usage:  python scripts/gen_ctrl_spec.py
"""
import importlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))  # NCI_Decoder repo root (Web_ver/..)
OUT = os.path.normpath(os.path.join(HERE, "..", "src", "core", "ctrl_spec.js"))

sys.path.insert(0, REPO)
import nci_decoder  # noqa: E402,F401

PACKAGES = [("forum20", "nfc_forum_2_0_pkg"), ("nxp", "Nxp_pkg")]


def main():
    parts = []
    for key, pkg in PACKAGES:
        m = importlib.import_module(pkg + ".__ctrl__")
        spec = {}
        for gid, oids in m.tbl_nci_ctrl.items():
            if gid == "HDLL":
                spec[gid] = {op: fn.__name__ for op, fn in oids.items()}
            else:
                spec[gid] = {oid: {mt: fn.__name__ for mt, fn in mts.items()} for oid, mts in oids.items()}
        parts.append(f"export const CTRL_{key.upper()} = {json.dumps(spec, indent=2)};\n")
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("// Generated from the Python __ctrl__.py tbl_nci_ctrl tables (handler names only).\n"
                "// Regenerate with: python scripts/gen_ctrl_spec.py\n\n" + "\n".join(parts))
    print(OUT)


if __name__ == "__main__":
    main()
