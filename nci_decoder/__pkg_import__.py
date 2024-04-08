import importlib

def tbl_import(vendor, model):
	if vendor.lower() == "nxp":
        # 動態導入 Nxp_pkg 的 Table
		NFC_table = importlib.import_module("Nxp_pkg.__table__")
	else:
        # 默認導入 nfc_forum_pkg 的 Table
		NFC_table = importlib.import_module("nci_decoder.nfc_forum_2_0_pkg.__table__")
	return NFC_table