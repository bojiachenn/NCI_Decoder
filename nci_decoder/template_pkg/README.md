# Adding a new vendor/chip package

1. Copy this `template_pkg/` directory to a new name (e.g. `St_pkg/`).
2. In the copy, every handler function already forwards `vendor`/`model` to
   the forum function it delegates to (`Origin.X(raw, vendor, model)`).
   Override only the functions whose fields genuinely differ for this chip -
   delete the delegating body and write the real parsing logic instead.
3. In `__table__.py`, add overriding dicts only for enum values this chip
   reads differently than the forum baseline (`from nfc_forum_2_0_pkg.__table__
   import *` already pulls in everything else).
4. In `__ctrl__.py`, the `tbl_nci_ctrl` dispatch table is already wired to
   this package's own modules - add entries to `"Proprietary"` if/when this
   chip has vendor-specific commands (see `Nxp_pkg/__ctrl__.py`).
5. Register the new package in `nci_decoder/vendor_registry.py`
   (`VENDOR_PACKAGES["<vendor-key>"] = _package("St_pkg")`) - this is the
   only file outside the new package's own directory that needs a change to
   make it dispatchable and put it on `sys.path`.
6. If you also package this as a Windows executable, add the new package's
   modules to `NCI_Decoder.spec`'s `hiddenimports` - PyInstaller's static
   analysis can't see the dynamic `importlib.import_module` calls the
   registry uses.
