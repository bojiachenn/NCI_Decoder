import importlib

import vendor_registry


def tbl_import(vendor, model):
	return importlib.import_module(vendor_registry.resolve(vendor).table_module)