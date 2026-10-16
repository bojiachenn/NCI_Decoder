// Port of nfc_forum_2_0_pkg/NFCEE_Management.py (GID 0x2 NFCEE Management).
// Conventions: see web/PORTING.md.
// Bug fixes vs Python (recorded in tests/known_diffs/nfcee.json):
//   * Supported NFCEE Protocols / NFCEE Status lookups resolve range keys
//     (global lookup(): 80-FE "For proprietary use", 80-FF "Proprietary").
//   * T3T / NDEF TLV sub-fields are read from the TLV Value with bounds checks:
//     a Value shorter than its sub-fields gives "Payload too short" instead of
//     printing empty slices / crashing on int('').
import { findRangeKey } from '../../core/lookup.js';

const NFCEE_MODE = { '00': 'Disable', '01': 'Enable' };

const NFCEE_PWR_LINK_CFG = {
  '00': 'NFCC decides (default state).',
  '01': 'NFCEE Power Supply always On.',
  '02': 'NFCC to NFCEE Communication link always active when the NFCEE is powered on.',
  '03': 'NFCEE Power supply and NFCC to NFCEE communication link are always on.',
};

const NFCEE_PWR_SUPPLY = {
  '00': 'NFCC control power supply for any NFCEE_UICCx',
  '01': 'NFCC control power supply for NFCEE_eSE and NFCEE_NDEF',
};

const own = (o, k) => Object.prototype.hasOwnProperty.call(o, k);

/** "  * NFCEE ID: <hex> <exact name> <range name>" (Python prints both, one is usually '') */
export function NFCEE_ID_FIELD(r, out, ctx, level = 1) {
  const start = r.abs;
  const id = r.hex(1, 'NFCEE ID');
  const tbl = ctx.t('tbl_nfcee_id');
  const exact = own(tbl, id) ? tbl[id] : '';
  const rk = findRangeKey(tbl, id);
  const range = rk !== null ? tbl[rk] : '';
  out.line(`${'  '.repeat(level)}* NFCEE ID: ${id} ${exact} ${range}`, { start, end: r.abs, table: 'tbl_nfcee_id' });
  return id;
}

/** "* label: <hardcoded meaning>" or "* label: RFU (xx)" */
function fixedField(r, out, label, map) {
  const start = r.abs;
  const v = r.hex(1, label);
  out.kv(1, label, own(map, v) ? map[v] : `RFU (${v})`, { start, end: r.abs });
  return v;
}

function statusOnly(r, out) {
  out.enumField(r, 1, 'Status', 'tbl_status_codes');
}

/** TLV Type 02: T3T Command Set Interface Supplementary Information */
function t3tSupplementary(v, out) {
  out.hexField(v, 3, 'PMm', 8);
  let start = v.abs;
  const k = v.u8('Number of Entries');
  out.kv(3, 'Number of Entries', k, { start, end: v.abs });
  for (let j = 0; j < k; j++) {
    out.line(`       ~ [Entry_${j}] ~   `);
    start = v.abs;
    out.line(`        * System Code: ${v.hex(2, 'System Code')}`, { start, end: v.abs });
    start = v.abs;
    out.line(`        * Idm: ${v.hex(8, 'Idm')}`, { start, end: v.abs });
  }
}

/** TLV Type 04: NDEF */
function ndefInfo(v, out, ctx) {
  let start = v.abs;
  const sizeHex = v.peekHex(4);
  const size = v.uintLE(4, 'NDEF max size');
  out.line(`      * NDEF max size: ${size} Bytes (${sizeHex})`, { start, end: v.abs });

  start = v.abs;
  const ps = v.hex(1, 'Power State');
  const psBin = parseInt(ps, 16).toString(2).padStart(8, '0');
  out.line(`      * Power State: ${psBin} (${ps})`, { start, end: v.abs, table: 'tbl_pwr_state' });
  const pwr = ctx.t('tbl_pwr_state');
  for (let j = 5; j >= 0; j--) {
    const name = own(pwr, String(j)) ? pwr[String(j)] : 'RFU';
    const label = `       ~ ${name}:`.padEnd(43);
    const val = (psBin[7 - j] === '1' ? 'Apply' : 'Not apply').padEnd(10);
    out.line(label + val, { start, end: start + 1, table: 'tbl_pwr_state' });
  }

  start = v.abs;
  const ch = v.u8('NDEF-NFCEE characteristics');
  out.line(`      * NDEF-NFCEE characteristics: ${ch & 1 ? 'Persistent' : 'Not persistent'}`, { start, end: v.abs });
}

const handlers = {
  // 22 00
  NFCEE_DISCOVER_CMD(r, out) {
    out.line('(Empty)'.padStart(16).padEnd(25));
  },

  // 42 00
  NFCEE_DISCOVER_RSP(r, out) {
    statusOnly(r, out);
    const start = r.abs;
    const n = r.u8('Number of NFCEEs');
    out.kv(1, 'Number of NFCEEs', n, { start, end: r.abs });
  },

  // 62 00
  NFCEE_DISCOVER_NTF(r, out, ctx) {
    NFCEE_ID_FIELD(r, out, ctx);
    out.enumField(r, 1, 'NFCEE Status', 'tbl_nfcee_disc_status');

    let start = r.abs;
    const n = r.u8('Number of Protocol Information Entries');
    out.kv(1, 'Number of Protocol Info Entries', n, { start, end: r.abs });

    if (n !== 0) {
      start = r.abs;
      let text = '  * Supported NFCEE Protocols: ';
      for (let i = 0; i < n; i++) {
        const p = r.hex(1, 'Supported NFCEE Protocol');
        text += `${ctx.lookup('tbl_nfcee_proto', p)} (${p}), `;
      }
      out.line(text, { start, end: r.abs, table: 'tbl_nfcee_proto' });
    } else {
      out.blank();
    }

    start = r.abs;
    const m = r.u8('Number of NFCEE Information TLVs');
    out.kv(1, 'Number of NFCEE Info TLVs', m, { start, end: r.abs });

    if (m !== 0) {
      out.line('  * NFCEE Information:');
      for (let i = 0; i < m; i++) {
        out.blank();
        out.line(`   ~ [NFCEE Info TLV_${i}] ~  `);
        const type = out.enumField(r, 2, 'Type', 'tbl_tlv_type');
        start = r.abs;
        const x = r.u8('TLV Length');
        out.kv(2, 'Len', x, { start, end: r.abs });
        start = r.abs;
        const v = r.sub(x, 'TLV Value');
        out.kv(2, 'Val', v.data, { start, end: r.abs });
        if (type === '02') t3tSupplementary(v, out);
        else if (type === '04') ndefInfo(v, out, ctx);
      }
    }
    out.blank();

    fixedField(r, out, 'NFCEE Power Supply', NFCEE_PWR_SUPPLY);
  },

  // 22 01
  NFCEE_MODE_SET_CMD(r, out, ctx) {
    NFCEE_ID_FIELD(r, out, ctx);
    fixedField(r, out, 'NFCEE Mode', NFCEE_MODE);
  },

  // 42 01
  NFCEE_MODE_SET_RSP: statusOnly,

  // 62 01
  NFCEE_MODE_SET_NTF: statusOnly,

  // 62 02
  NFCEE_STATUS_NTF(r, out, ctx) {
    NFCEE_ID_FIELD(r, out, ctx);
    out.enumField(r, 1, 'NFCEE Status', 'tbl_nfcee_status');
  },

  // 22 03
  NFCEE_POWER_AND_LINK_CNTRL_CMD(r, out, ctx) {
    NFCEE_ID_FIELD(r, out, ctx);
    fixedField(r, out, 'NFCEE Power and Link Cfg', NFCEE_PWR_LINK_CFG);
  },

  // 42 03
  NFCEE_POWER_AND_LINK_CNTRL_RSP: statusOnly,
};

export default handlers;
