import re

_RANGE_KEY_RE = re.compile(r'^([0-9A-Fa-f]{2})-([0-9A-Fa-f]{2})$')


def find_range_key(table, value):
    """Return the "XX-YY" hex-range key in `table` whose inclusive range
    contains `value`, or None if no declared range covers it.

    Generic over whatever bucket boundaries a given table happens to use
    (e.g. tbl_nfcee_id's '02-0F'/'10-7F'/'80-FE' vs tbl_tlv_type's
    '05-9F'/'A0-FF') - callers must not assume any specific range set.
    Non-range keys (e.g. 'name', exact single-byte keys) are ignored rather
    than mistaken for a range.
    """
    for key in table:
        match = _RANGE_KEY_RE.match(key) if isinstance(key, str) else None
        if match is None:
            continue
        low, high = int(match.group(1), 16), int(match.group(2), 16)
        if low <= value <= high:
            return key
    return None
