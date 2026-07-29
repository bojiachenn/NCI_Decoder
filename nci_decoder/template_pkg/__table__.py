from nfc_forum_2_0_pkg.__table__ import *

# Only declare a table dict here if this vendor's chip genuinely reads a
# different enum name for that field than the NFC Forum baseline - a
# redeclared name here shadows the imported one of the same name. Most new
# vendor packages need zero overrides to start; see Nxp_pkg/__table__.py for
# an example of a heavily-overridden table (kept as-is, not a pattern to copy
# by default - it predates this template and duplicates far more than it
# needs to).
