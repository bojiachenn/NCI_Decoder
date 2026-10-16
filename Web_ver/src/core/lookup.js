// Table lookup shared by every handler.
// Mirrors Python's `tbl.get(value, "RFU")`, plus range keys ("80-FE") which the
// Python code only honoured at a few call sites (find_range_key) - here every
// lookup falls back to a covering range key, fixing the "range value shows RFU" bug.

const RANGE_KEY_RE = /^([0-9A-Fa-f]{2})-([0-9A-Fa-f]{2})$/;

export function findRangeKey(table, value) {
  const v = typeof value === 'number' ? value : parseInt(value, 16);
  if (Number.isNaN(v)) return null;
  for (const key of Object.keys(table)) {
    const m = RANGE_KEY_RE.exec(key);
    if (!m) continue;
    if (parseInt(m[1], 16) <= v && v <= parseInt(m[2], 16)) return key;
  }
  return null;
}

export function lookup(table, value, fallback = 'RFU') {
  if (!table) return fallback;
  if (Object.prototype.hasOwnProperty.call(table, value)) return table[value];
  if (typeof value === 'string') {
    const up = value.toUpperCase();
    if (Object.prototype.hasOwnProperty.call(table, up)) return table[up];
    if (/^[0-9A-Fa-f]{2}$/.test(value)) {
      const key = findRangeKey(table, value);
      if (key !== null) return table[key];
    }
  }
  return fallback;
}
