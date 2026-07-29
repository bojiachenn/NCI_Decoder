import os

# Must run before any `import nci_decoder...` anywhere in the test suite:
# nci_decoder/__init__.py appends vendor package directories to sys.path using
# CWD-relative paths at import time, so pytest's rootdir must already be the
# current directory before collection imports any test module. pytest always
# loads the rootdir conftest.py first, so this is the one place guaranteed to
# run before that import happens - regardless of what directory pytest itself
# was invoked from.
os.chdir(os.path.dirname(os.path.abspath(__file__)))
