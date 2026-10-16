// Decoder context: which vendor/table set is active plus cross-packet state.
// Python keeps this state in module globals (HDLL_CMD, PWR_MODE_00, TEST_ID_3F,
// DPC_TYPE, AST_LOOP, A10F/A007 values...). Here it lives in ctx.state, one per
// decode session (single-hex page keeps one; each log file gets a fresh one).
import { lookup } from './lookup.js';
import { VENDORS } from './registry.js';

export function createContext(vendorKey = 'forum20') {
  const vendor = VENDORS[vendorKey] || VENDORS.forum20;
  return {
    vendorKey: vendor.key,
    vendor,
    state: {},
    t(name) {
      const tbl = vendor.tables[name];
      if (!tbl) throw new Error(`Unknown table ${name} for vendor ${vendor.key}`);
      return tbl;
    },
    lookup(name, value, fallback = 'RFU') {
      return lookup(this.t(name), value, fallback);
    },
  };
}
