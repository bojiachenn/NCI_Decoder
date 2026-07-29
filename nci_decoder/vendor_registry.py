from typing import NamedTuple


class VendorPackage(NamedTuple):
    pkg_dir: str
    ctrl_module: str
    table_module: str


def _package(pkg_dir):
    return VendorPackage(pkg_dir, f"{pkg_dir}.__ctrl__", f"{pkg_dir}.__table__")


DEFAULT_VENDOR_PACKAGE = _package("nfc_forum_2_0_pkg")

VENDOR_PACKAGES = {
    "nxp": _package("Nxp_pkg"),
}


def resolve(vendor):
    return VENDOR_PACKAGES.get((vendor or "").lower(), DEFAULT_VENDOR_PACKAGE)


def all_pkg_dirs():
    dirs = [pkg.pkg_dir for pkg in VENDOR_PACKAGES.values()]
    dirs.append(DEFAULT_VENDOR_PACKAGE.pkg_dir)
    return list(dict.fromkeys(dirs))
