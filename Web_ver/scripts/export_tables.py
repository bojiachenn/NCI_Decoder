"""Export every module-level tbl_* dict from the Python decoder's __table__.py
files into JSON, so the JS decoder never hand-copies enum tables.

Usage:  python scripts/export_tables.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))  # NCI_Decoder repo root (Web_ver/..)
OUT = os.path.normpath(os.path.join(HERE, "..", "src", "data"))

sys.path.insert(0, REPO)
import nci_decoder  # noqa: E402,F401  (sets up sys.path for flat package imports)
import importlib  # noqa: E402

PACKAGES = {"forum20": "nfc_forum_2_0_pkg", "nxp": "Nxp_pkg"}


def _stringify(obj):
    """JSON needs str keys; a few tables use int keys (kept as decimal strings)."""
    if isinstance(obj, dict):
        return {str(k): _stringify(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_stringify(v) for v in obj]
    return obj


def export(pkg_dir):
    mod = importlib.import_module(f"{pkg_dir}.__table__")
    tables = {}
    for name in dir(mod):
        val = getattr(mod, name)
        if name.startswith("tbl_") and isinstance(val, dict):
            tables[name] = _stringify(val)
    return tables


def main():
    os.makedirs(OUT, exist_ok=True)
    for key, pkg_dir in PACKAGES.items():
        tables = export(pkg_dir)
        path = os.path.join(OUT, f"tables.{key}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(tables, f, ensure_ascii=False, indent=1, sort_keys=True, default=str)
        print(f"{path}: {len(tables)} tables")


if __name__ == "__main__":
    main()
