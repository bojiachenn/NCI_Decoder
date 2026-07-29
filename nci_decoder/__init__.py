import os
import sys

from . import vendor_registry

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(_BASE_DIR)
for _pkg_dir in vendor_registry.all_pkg_dirs():
    sys.path.append(os.path.join(_BASE_DIR, _pkg_dir))

# nfc_forum_2_3_pkg is fully written but has no vendor_registry entry - it is
# not dispatchable (see CLAUDE.md), kept importable only for now.
sys.path.append(os.path.join(_BASE_DIR, "nfc_forum_2_3_pkg"))
