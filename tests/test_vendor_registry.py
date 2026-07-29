from nci_decoder import vendor_registry


def test_resolve_nxp_is_case_insensitive():
    for key in ("nxp", "Nxp", "NXP"):
        pkg = vendor_registry.resolve(key)
        assert pkg.pkg_dir == "Nxp_pkg"
        assert pkg.ctrl_module == "Nxp_pkg.__ctrl__"
        assert pkg.table_module == "Nxp_pkg.__table__"


def test_resolve_unregistered_or_empty_falls_back_to_forum_default():
    # Must reproduce the exact pre-refactor semantics: vendor.lower() == "nxp"
    # selects Nxp_pkg, anything else (including "None", "", "St", typos)
    # falls back to the nfc_forum_2_0_pkg default.
    for key in ("None", "", "St", "bogus-vendor"):
        pkg = vendor_registry.resolve(key)
        assert pkg is vendor_registry.DEFAULT_VENDOR_PACKAGE
        assert pkg.pkg_dir == "nfc_forum_2_0_pkg"
        assert pkg.ctrl_module == "nfc_forum_2_0_pkg.__ctrl__"
        assert pkg.table_module == "nfc_forum_2_0_pkg.__table__"


def test_resolve_handles_real_none_not_just_the_string():
    # config.get("vendor") can yield a real None (e.g. `"vendor": null` in
    # config.json), unlike the pre-refactor `vendor.lower()` which would have
    # raised AttributeError on that input. `(vendor or "").lower()` must not
    # crash and must fall back to the same default as any other unregistered
    # value.
    assert vendor_registry.resolve(None) is vendor_registry.DEFAULT_VENDOR_PACKAGE


def test_all_pkg_dirs_has_no_duplicates_and_includes_default():
    dirs = vendor_registry.all_pkg_dirs()
    assert len(dirs) == len(set(dirs))
    assert "Nxp_pkg" in dirs
    assert "nfc_forum_2_0_pkg" in dirs


def test_registering_a_new_vendor_requires_no_other_code_changes():
    # Smoke-checks the extensibility contract itself: VENDOR_PACKAGES is a
    # plain dict a future vendor package registers into directly.
    assert isinstance(vendor_registry.VENDOR_PACKAGES, dict)
    assert "nxp" in vendor_registry.VENDOR_PACKAGES
