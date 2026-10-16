// Port of nfc_forum_2_0_pkg/RF_Management.py (GID 0x1 RF Management).
// Conventions (see web/PORTING.md): handler(r: Reader, out: Out, ctx) — read with r,
// print with out using the exact Python text; tables via ctx.t()/out.enumField.
//
// Fixes vs the original Python (Python RF_Management.py now mirrors all of them):
//  * RF_INTF_ACTIVATED_NTF: Initial Number of Credits parsed as hex (Python int() base 10).
//  * RF_INTF_ACTIVATED_NTF: Activation Parameters parsed inside their declared length n
//    (n = 0 -> nothing is read; Python read inner length fields anyway and crashed).
//  * RF Technology / Interface branches use the hex code, not the table string
//    (NXP's tbl_rf_tech_mode says "ACTIVE_POLL ( Not supported )").
//  * RF_DISCOVER_SELECT_CMD: RF Interface line shows the interface hex, not the protocol.
//  * LISTEN_MODE_ROUTING_INFO: AID printed whenever it is non-empty, SC Route label uses
//    the SC index, APDU Reference data / Mask printed in full, protocol hex not replaced by
//    the range key.
//  * RF_NFCEE_ACTION_NTF: trigger 04 split into Reference data / Mask halves (Python
//    crashed on n/2); other triggers show the raw Supporting Data.
//  * RF_FIELD_INFO_NTF: unknown status prints "RFU (XX)" instead of the meaning of 00.
//  * NFC-DEP Poll activation params (Table 102) read the Data Exchange Length Reduction
//    octet after ATR_RES, like the Listen branch (Table 103) (fixed in Python too).
//  * Malformed RF Technology Specific / Activation Parameters print an error line and the
//    decoder continues after the declared length.
import { DecodeError } from '../../core/reader.js';
import { findRangeKey } from '../../core/lookup.js';

// Python '{0:^25}'.format("(Empty)")
const EMPTY = `${' '.repeat(9)}(Empty)${' '.repeat(9)}`;

const has = (tbl, k) => k != null && Object.prototype.hasOwnProperty.call(tbl, k);
/** Python dict.get(k, fb) — exact key only, no range resolution */
const exactGet = (tbl, k, fb) => (has(tbl, k) ? tbl[k] : fb);

/** read n bytes, returning value + absolute byte range for highlighting */
function rd(r, n, what) {
  const start = r.abs;
  const v = r.hex(n, what);
  return { v, start, end: r.abs };
}

/**
 * Run fn on a sub-reader over the next n bytes of r. The outer reader always advances
 * by n; a too-short inner structure prints an error line instead of aborting.
 */
function withSub(r, n, out, what, fn) {
  const sub = r.sub(n, what);
  try {
    fn(sub);
  } catch (e) {
    if (!(e instanceof DecodeError)) throw e;
    out.error(`  * Error: ${what}: ${e.message}`);
  }
  return sub;
}

function status(r, out) {
  out.enumField(r, 1, 'Status', 'tbl_status_codes');
}

function empty(r, out) {
  out.line(EMPTY);
}

/** Python: print("  * RF Discovery ID:", tbl_rf_dis_id.get(id, id)) (exact lookup) */
function discoveryId(r, out, ctx) {
  const f = rd(r, 1, 'RF Discovery ID');
  out.line(`  * RF Discovery ID: ${exactGet(ctx.t('tbl_rf_dis_id'), f.v, f.v)}`,
    { start: f.start, end: f.end, table: 'tbl_rf_dis_id' });
  return f.v;
}

/** tbl_nfcee_id exact meaning + range meaning, as Python prints them */
export function nfceeIdNames(ctx, id) {
  const tbl = ctx.t('tbl_nfcee_id');
  const range = findRangeKey(tbl, id);
  return { exact: exactGet(tbl, id, ''), range: exactGet(tbl, range, '') };
}

/**
 * Power State bit lines (Table 59), bits 5..0.
 * @param labelWidth Python '{0:<W}' width of the label column
 * @param valueAlign 'right' => '{0:>10}' (routing info), 'left' => '{0:<10}' (forced routing)
 */
export function powerStateLines(out, ctx, value, indent, labelWidth, valueAlign, meta = {}) {
  const tbl = ctx.t('tbl_pwr_state');
  const v = parseInt(value, 16);
  for (let j = 5; j >= 0; j--) {
    const label = `${indent}~ ${exactGet(tbl, String(j), 'RFU')}:`.padEnd(labelWidth);
    const txt = (v >> j) & 1 ? 'Apply' : 'Not apply';
    out.line(label + (valueAlign === 'right' ? txt.padStart(10) : txt.padEnd(10)), { ...meta, table: 'tbl_pwr_state' });
  }
}

/** "label: MEANING (HEX)" for one byte at level 1/2/... using ctx lookup */
function enumLine(out, ctx, indent, label, tableName, f) {
  out.line(`${indent}* ${label}: ${ctx.lookup(tableName, f.v)} (${f.v})`, { start: f.start, end: f.end, table: tableName });
}

// ---------------------------------------------------------------------------
// Shared structure A: Listen Mode Routing (RF_SET_LISTEN_MODE_ROUTING_CMD /
// RF_GET_LISTEN_MODE_ROUTING_NTF)
// ---------------------------------------------------------------------------
export function LISTEN_MODE_ROUTING_INFO(r, out, ctx) {
  out.enumField(r, 1, 'More', 'tbl_more');
  const nf = rd(r, 1, 'Number of Routing Entries');
  const n = parseInt(nf.v, 16);
  out.line(`  * Number of Routing Entries: ${n} (${nf.v})`, { start: nf.start, end: nf.end });

  const typeTbl = ctx.t('tbl_L_mode_routing_entry_type');
  for (let i = 0; i < n; i++) {
    out.blank();
    out.line(`   ~ [Routing Entry_${i}] ~  `);
    const qf = rd(r, 1, 'Qualifier-Type');
    const q = qf.v;
    const type = q[1];
    out.line(`    * Type: ${exactGet(typeTbl, type, 'RFU')} (${q})`, { start: qf.start, end: qf.end, table: 'tbl_L_mode_routing_entry_type' });
    const hi = parseInt(q[0], 16); // Table 52
    if (hi & 0x4) out.line('     ~ Routing is blocked for the power modes where it is not supported.', { start: qf.start, end: qf.end });
    if (hi & 0x2) out.line('     ~ Match is allowed when the SELECT AID is shorter than the AID in this routing table entry.', { start: qf.start, end: qf.end });
    if (hi & 0x1) out.line('     ~ Match is allowed when the SELECT AID is longer than the AID in this routing table entry.', { start: qf.start, end: qf.end });

    const lf = rd(r, 1, 'Routing Entry Length');
    const x = parseInt(lf.v, 16);
    out.line(`    * Len: ${x}`, { start: lf.start, end: lf.end });

    const valStart = r.abs;
    const valHex = r.peekHex(x);
    out.line(`    * Val: ${valHex}`, { start: valStart, end: valStart + valHex.length / 2 });
    withSub(r, x, out, 'Routing Entry Value', (v) => {
      const rf = rd(v, 1, 'Route');
      const names = nfceeIdNames(ctx, rf.v);
      out.line(`      * Route: ${exactGet(ctx.t('tbl_nfcee_id'), rf.v, rf.v)} ${names.range} (${rf.v})`,
        { start: rf.start, end: rf.end, table: 'tbl_nfcee_id' });

      const pf = rd(v, 1, 'Power State');
      const bits = parseInt(pf.v, 16).toString(2).padStart(8, '0');
      out.line(`      * Power State: ${bits} (${pf.v})`, { start: pf.start, end: pf.end });
      powerStateLines(out, ctx, pf.v, '       ', 43, 'right', { start: pf.start, end: pf.end });

      if (type === '0') {
        // Table 54: Technology
        enumLine(out, ctx, '      ', 'Technology', 'tbl_rf_tech', rd(v, 1, 'Technology'));
      } else if (type === '1') {
        // Table 55: Protocol
        enumLine(out, ctx, '      ', 'Protocol', 'tbl_rf_proto', rd(v, 1, 'Protocol'));
      } else if (type === '2') {
        // Table 56: AID 0-16 octets
        if (v.remaining > 0) {
          const af = rd(v, v.remaining, 'AID');
          out.line(`      * AID: ${af.v}`, { start: af.start, end: af.end });
        }
      } else if (type === '3') {
        // Table 57: SC Route List, 2 octets each
        const num = Math.floor((x - 2) / 2);
        for (let j = 0; j < num; j++) {
          const sf = rd(v, 2, 'SC Route');
          out.line(`      * SC Route ${j}: ${sf.v}`, { start: sf.start, end: sf.end });
        }
      } else if (type === '4') {
        // Table 58: Reference data n octets + Mask n octets
        const dataLen = Math.floor((x - 2) / 2);
        const ref = rd(v, dataLen, 'Reference data');
        out.line(`      * Reference data: ${ref.v}`, { start: ref.start, end: ref.end });
        const mask = rd(v, dataLen, 'Mask');
        out.line(`      * Mask: ${mask.v}`, { start: mask.start, end: mask.end });
      }
    });
  }
}

// ---------------------------------------------------------------------------
// Shared structure B: RF Technology Specific Parameters (Tables 68-76)
// ---------------------------------------------------------------------------
/**
 * @param rfTechMode RF Technology and Mode hex ('00', '80', ...) — branches on the code
 * @param p          Reader over exactly the parameter bytes
 */
export function RF_TECH_SPEC_PARA(rfTechMode, p, out, ctx) { // eslint-disable-line no-unused-vars
  const lenField = (label) => {
    const f = rd(p, 1, label);
    const l = parseInt(f.v, 16);
    out.line(`  * ${label}: ${l}`, { start: f.start, end: f.end });
    return l;
  };
  const hexField = (label, n) => {
    const f = rd(p, n, label);
    out.line(`  * ${label}: ${f.v}`, { start: f.start, end: f.end });
  };

  switch (String(rfTechMode).toUpperCase()) {
    case '00': { // Table 68: NFC-A Poll
      hexField('SENS_RES Response', 2);
      hexField('NFCID1', lenField('NFCID1 Len'));
      hexField('SEL_RES Rsp', lenField('SEL_RES Rsp Len'));
      const l = lenField('HRx Len');
      if (l !== 0) hexField('HRx', l);
      break;
    }
    case '80': // Table 69: NFC-A Listen
      out.line('  * There is no RF Technology Specific Parameters');
      break;
    case '01': // Table 70: NFC-B Poll
      hexField('SENSB_RES Rsp', lenField('SENSB_RES Rsp Len'));
      break;
    case '81': // Table 71: NFC-B Listen
      hexField('SENSB_REQ Command', 1);
      break;
    case '02': { // Table 72: NFC-F Poll
      const f = rd(p, 1, 'Bit Rate');
      const txt = f.v === '01' ? '212 kbps' : f.v === '02' ? '424 kbps' : `RFU (${f.v})`;
      out.line(`  * Bit Rate: ${txt}`, { start: f.start, end: f.end });
      hexField('SENSF_RES Rsp', lenField('SENSF_RES Rsp Len'));
      break;
    }
    case '82': // Table 73: NFC-F Listen
      hexField('Local NFCID2', lenField('Local NFCID2 Len'));
      break;
    case '06': // Table 74: NFC-V Poll
      hexField('RES_FLAG', 1);
      hexField('DSFID', 1);
      hexField('UID', 8);
      break;
    case '03': // Table 75: NFC-ACM Poll
      hexField('ATR_RES Rsp', lenField('ATR_RES Rsp Len'));
      break;
    case '83': // Table 76: NFC-ACM Listen
      hexField('ATR_REQ Cmd', lenField('ATR_REQ Cmd Len'));
      break;
    default: {
      const start = p.abs;
      const v = p.rest();
      out.line(`  * Proprietary parameters: ${v}`, { start, end: p.abs });
    }
  }
}

/**
 * Activation Parameters of RF_INTF_ACTIVATED_NTF (Tables 95-103), branching on the
 * RF Interface code and the Activation RF Technology and Mode code.
 * @param a Reader over exactly the n parameter bytes
 */
export function ACTIVATION_PARA(rfIf, rfTechMode, a, out, ctx) {
  const raw = () => {
    if (a.remaining > 0) {
      const f = rd(a, a.remaining, 'Activation Params');
      out.line(`  * Activation Params: ${f.v}`, { start: f.start, end: f.end });
    }
  };
  const lenField = (label, withHex) => {
    const f = rd(a, 1, label);
    const l = parseInt(f.v, 16);
    out.line(`  * ${label}: ${l}${withHex ? ` (${f.v})` : ''}`, { start: f.start, end: f.end });
    return l;
  };
  const hexField = (label, n) => {
    const f = rd(a, n, label);
    out.line(`  * ${label}: ${f.v}`, { start: f.start, end: f.end });
  };
  if (a.remaining === 0) return;
  const ifc = String(rfIf).toUpperCase();
  const mode = String(rfTechMode).toUpperCase();
  if (ifc === '02') { // ISO-DEP
    if (mode === '00') { // Table 95
      hexField('RATS Rsp', lenField('RATS Rsp Len', true));
    } else if (mode === '01') { // Table 96
      hexField('ATTRIB Rsp', lenField('ATTRIB Rsp Len', true));
    } else if (mode === '80') { // Table 98
      hexField('RATS Cmd Param', 1);
    } else if (mode === '81') { // Table 99
      hexField('ATTRIB Cmd', lenField('ATTRIB Cmd Len'));
    } else {
      raw();
      return;
    }
  } else if (ifc === '03') { // NFC-DEP
    if (mode === '00' || mode === '02') { // Table 102
      hexField('ATR_RES Rsp', lenField('ATR_RES Rsp Len'));
      enumLine(out, ctx, '  ', 'Data Exchange LR', 'tbl_len_rdu_val', rd(a, 1, 'Data Exchange LR'));
    } else if (mode === '80' || mode === '82') { // Table 103
      hexField('ATR_REQ Cmd', lenField('ATR_REQ Cmd Len'));
      enumLine(out, ctx, '  ', 'Data Exchange LR', 'tbl_len_rdu_val', rd(a, 1, 'Data Exchange LR'));
    } else {
      raw();
      return;
    }
  } else {
    raw();
    return;
  }
  if (a.remaining > 0) {
    const f = rd(a, a.remaining, 'Activation Params');
    out.line(`  * Remaining Activation Params: ${f.v}`, { start: f.start, end: f.end });
  }
}

const handlers = {
  // 21 00
  RF_DISCOVER_MAP_CMD(r, out) {
    const nf = rd(r, 1, 'Number of Mapping Configurations');
    const n = parseInt(nf.v, 16);
    out.line(`  * Number of Mapping Configs: ${n} (${nf.v})`, { start: nf.start, end: nf.end });
    for (let i = 0; i < n; i++) {
      out.blank();
      out.line(`   ~ [Mapping Cfg_${i}] ~  `);
      out.enumField(r, 2, 'RF Protocol', 'tbl_rf_proto');
      out.enumField(r, 2, 'Mode', 'tbl_mode');
      out.enumField(r, 2, 'RF Interface', 'tbl_rf_if');
    }
  },

  // 41 00
  RF_DISCOVER_MAP_RSP: status,

  // 21 01
  RF_SET_LISTEN_MODE_ROUTING_CMD(r, out, ctx) {
    LISTEN_MODE_ROUTING_INFO(r, out, ctx);
  },

  // 41 01
  RF_SET_LISTEN_MODE_ROUTING_RSP: status,

  // 21 02
  RF_GET_LISTEN_MODE_ROUTING_CMD: empty,

  // 41 02
  RF_GET_LISTEN_MODE_ROUTING_RSP: status,

  // 61 02
  RF_GET_LISTEN_MODE_ROUTING_NTF(r, out, ctx) {
    LISTEN_MODE_ROUTING_INFO(r, out, ctx);
  },

  // 21 03
  RF_DISCOVER_CMD(r, out) {
    const nf = rd(r, 1, 'Number of Configurations');
    const n = parseInt(nf.v, 16);
    out.line(`  * Number of Configs: ${n} (${nf.v})`, { start: nf.start, end: nf.end });
    for (let i = 0; i < n; i++) {
      out.blank();
      out.line(`   ~ [Config_${i}] ~  `);
      out.enumField(r, 2, 'Mode', 'tbl_rf_tech_mode');
      const ff = rd(r, 1, 'Discovery Frequency');
      const freq = parseInt(ff.v, 16);
      out.line(`    * Discovery Freq: ${freq === 0 || freq > 10 ? 'RFU' : freq}`, { start: ff.start, end: ff.end });
    }
  },

  // 41 03
  RF_DISCOVER_RSP: status,

  // 61 03
  RF_DISCOVER_NTF(r, out, ctx) {
    discoveryId(r, out, ctx);
    out.enumField(r, 1, 'RF Protocol', 'tbl_rf_proto');
    const mode = out.enumField(r, 1, 'Mode', 'tbl_rf_tech_mode');
    const lf = rd(r, 1, 'Length of RF Technology Specific Parameters');
    const n = parseInt(lf.v, 16);
    out.line(`  * Len of RF Tech Specific Params: ${n}`, { start: lf.start, end: lf.end });
    withSub(r, n, out, 'RF Technology Specific Parameters', (p) => RF_TECH_SPEC_PARA(mode, p, out, ctx));

    const tf = rd(r, 1, 'Notification Type');
    const txt = {
      '00': 'Last NTF (00)',
      '01': 'Last NTF (due to NFCC reaching its resource limit) (01)',
      '02': 'More NTF to follow (02)',
    }[tf.v] || `RFU (${tf.v})`;
    out.line(`  * NTF Type: ${txt}`, { start: tf.start, end: tf.end });
  },

  // 21 04
  RF_DISCOVER_SELECT_CMD(r, out, ctx) {
    discoveryId(r, out, ctx);
    out.enumField(r, 1, 'RF Protocol', 'tbl_rf_proto');
    // Python printed the RF Protocol hex in the parentheses (bug)
    out.enumField(r, 1, 'RF Interface', 'tbl_rf_if');
  },

  // 41 04
  RF_DISCOVER_SELECT_RSP: status,

  // 61 05
  RF_INTF_ACTIVATED_NTF(r, out, ctx) {
    discoveryId(r, out, ctx);
    const rfIf = out.enumField(r, 1, 'RF Interface', 'tbl_rf_if');
    out.enumField(r, 1, 'RF Protocol', 'tbl_rf_proto');
    const mode = out.enumField(r, 1, 'Activation Mode', 'tbl_rf_tech_mode');

    const mf = rd(r, 1, 'Max Data Packet Payload Size');
    out.line(`  * Max Data Size: ${parseInt(mf.v, 16)} (${mf.v})`, { start: mf.start, end: mf.end });

    const cf = rd(r, 1, 'Initial Number of Credits');
    // Python: int(num_credits) (decimal) -> fixed to hex
    out.line(cf.v === 'FF' ? `  * Number of Credits: Not used (${cf.v})` : `  * Number of Credits: ${parseInt(cf.v, 16)}`,
      { start: cf.start, end: cf.end });

    const lf = rd(r, 1, 'Length of RF Technology Specific Parameters');
    const l = parseInt(lf.v, 16);
    out.line(`  * Len of RF Tech Specific Params: ${l}`, { start: lf.start, end: lf.end });
    if (l !== 0) {
      withSub(r, l, out, 'RF Technology Specific Parameters', (p) => RF_TECH_SPEC_PARA(mode, p, out, ctx));
    }

    out.enumField(r, 1, 'Data Mode', 'tbl_rf_tech_mode');
    out.enumField(r, 1, 'Tx', 'tbl_bit_rates');
    out.enumField(r, 1, 'Rx', 'tbl_bit_rates');

    const af = rd(r, 1, 'Length of Activation Parameters');
    const n = parseInt(af.v, 16);
    out.line(`  * Len of Activation Params: ${n}`, { start: af.start, end: af.end });
    withSub(r, n, out, 'Activation Parameters', (a) => ACTIVATION_PARA(rfIf, mode, a, out, ctx));
  },

  // 21 06
  RF_DEACTIVATE_CMD(r, out) {
    out.enumField(r, 1, 'Deactivation Type', 'tbl_deactivate_type');
  },

  // 41 06
  RF_DEACTIVATE_RSP: status,

  // 61 06
  RF_DEACTIVATE_NTF(r, out) {
    out.enumField(r, 1, 'Deactivation Type', 'tbl_deactivate_type');
    out.enumField(r, 1, 'Deactivation Reason', 'tbl_deactivate_reason');
  },

  // 61 07
  RF_FIELD_INFO_NTF(r, out, ctx) {
    const f = rd(r, 1, 'RF Field Status');
    const tbl = ctx.t('tbl_rf_field_status');
    // Python fell back to the meaning of 00 (without the hex) for undefined values
    const txt = has(tbl, f.v) && f.v !== 'name' ? tbl[f.v] : `RFU (${f.v})`;
    out.line(`  * RF Field Status: ${txt}`, { start: f.start, end: f.end, table: 'tbl_rf_field_status' });
  },

  // 21 08
  RF_T3T_POLLING_CMD(r, out) {
    out.hexField(r, 1, 'SENSF_REQ_PARAMS', 4);
  },

  // 41 08
  RF_T3T_POLLING_RSP: status,

  // 61 08
  RF_T3T_POLLING_NTF(r, out) {
    out.enumField(r, 1, 'Status', 'tbl_status_codes');
    const nf = rd(r, 1, 'Number of Responses');
    const n = parseInt(nf.v, 16);
    out.line(`  * Number of Rsp: ${n} (${nf.v})`, { start: nf.start, end: nf.end });
    for (let i = 0; i < n; i++) {
      out.blank();
      out.line(`   ~ [Rsp_${i}] ~  `);
      const lf = rd(r, 1, 'SENSF_RES Length');
      const l = parseInt(lf.v, 16);
      out.line(`    * Len: ${l} (${lf.v})`, { start: lf.start, end: lf.end });
      const sf = rd(r, l, 'SENSF_RES');
      out.line(`    * SENSF_RES: ${sf.v}`, { start: sf.start, end: sf.end });
    }
  },

  // 61 09
  RF_NFCEE_ACTION_NTF(r, out, ctx) {
    const idf = rd(r, 1, 'NFCEE ID');
    const names = nfceeIdNames(ctx, idf.v);
    out.line(`  * NFCEE ID: ${idf.v} ${names.exact} ${names.range}`, { start: idf.start, end: idf.end, table: 'tbl_nfcee_id' });

    const tf = rd(r, 1, 'Trigger');
    enumLine(out, ctx, '  ', 'Trigger', 'tbl_nfcee_ntf_trig', tf);

    const lf = rd(r, 1, 'Supporting Data Length');
    const n = parseInt(lf.v, 16);
    out.line(`  * Supporting Data Len: ${n}`, { start: lf.start, end: lf.end });

    const df = rd(r, n, 'Supporting Data');
    const d = df.v;
    const meta = { start: df.start, end: df.end };
    out.line('  * Supporting Data: ');
    switch (tf.v) {
      case '00':
        out.line(`    * AID: ${d}`, meta);
        break;
      case '01':
        out.line(`    * RF Protocol: ${ctx.lookup('tbl_rf_proto', d)} (${d})`, { ...meta, table: 'tbl_rf_proto' });
        break;
      case '02':
      case '05':
        out.line(`    * RF Technology: ${ctx.lookup('tbl_rf_tech', d)} (${d})`, { ...meta, table: 'tbl_rf_tech' });
        break;
      case '03':
        out.line(`    * SC Route: ${d}`, meta);
        break;
      case '04': {
        // Table 58: Reference data (n/2 octets) + Mask (n/2 octets); Python crashed on n/2
        const half = Math.floor(n / 2) * 2; // hex chars
        out.line(`    * Reference data: ${d.slice(0, half)}`, { start: df.start, end: df.start + half / 2 });
        out.line(`    * Mask: ${d.slice(half)}`, { start: df.start + half / 2, end: df.end });
        break;
      }
      default:
        // RFU / application specific: Python printed nothing
        if (n > 0) out.line(`    * Data: ${d}`, meta);
    }
  },

  // 61 0A
  RF_NFCEE_DISCOVERY_REQ_NTF(r, out, ctx) {
    const nf = rd(r, 1, 'Number of Information Entries');
    const n = parseInt(nf.v, 16);
    out.line(`  * Number Of Info Entries: ${n}`, { start: nf.start, end: nf.end });
    for (let i = 0; i < n; i++) {
      out.blank();
      out.line(`   ~ [Info Entry_${i}] ~  `);
      const tf = rd(r, 1, 'Type');
      out.line(`    * Type: ${ctx.lookup('tbl_nfcee_disc_req_type', tf.v)}`, { start: tf.start, end: tf.end, table: 'tbl_nfcee_disc_req_type' });
      const lf = rd(r, 1, 'Length');
      const x = parseInt(lf.v, 16);
      out.line(`    * Len: ${x}`, { start: lf.start, end: lf.end });
      const valStart = r.abs;
      const valHex = r.peekHex(x);
      out.line(`    * Val: ${valHex}`, { start: valStart, end: valStart + valHex.length / 2 });
      withSub(r, x, out, 'Information Entry Value', (v) => {
        if (tf.v !== '00' && tf.v !== '01') return;
        const idf = rd(v, 1, 'NFCEE ID');
        const names = nfceeIdNames(ctx, idf.v);
        out.line(`      * NFCEE: ${idf.v} ${names.exact} ${names.range}`, { start: idf.start, end: idf.end, table: 'tbl_nfcee_id' });
        enumLine(out, ctx, '      ', 'Mode', 'tbl_rf_tech_mode', rd(v, 1, 'RF Technology and Mode'));
        enumLine(out, ctx, '      ', 'RF Protocol', 'tbl_rf_proto', rd(v, 1, 'RF Protocol'));
      });
    }
  },

  // 21 0B
  RF_PARAMETER_UPDATE_CMD(r, out, ctx) {
    const nf = rd(r, 1, 'Number of Parameters');
    const n = parseInt(nf.v, 16);
    out.line(`  * Number of Params: ${n} (${nf.v})`, { start: nf.start, end: nf.end });
    for (let i = 0; i < n; i++) {
      out.blank();
      out.line(`   ~ [RF Communication ${i}] ~  `);
      const idf = rd(r, 1, 'ID');
      enumLine(out, ctx, '  ', 'Type ID', 'tbl_rf_commu_para_id', idf);
      const lf = rd(r, 1, 'Length');
      const x = parseInt(lf.v, 16);
      out.line(`  * Len: ${x}`, { start: lf.start, end: lf.end });
      const valStart = r.abs;
      const valHex = r.peekHex(x);
      out.line(`  * Val: ${valHex}`, { start: valStart, end: valStart + valHex.length / 2 });
      withSub(r, x, out, 'RF Communication Parameter Value', (v) => {
        const id = idf.v;
        if (v.remaining === 0) return; // Python printed e.g. "Rx: RFU ()" for an empty value
        if (id === '00') { // Table 91
          enumLine(out, ctx, '    ', 'Mode', 'tbl_rf_tech_mode', rd(v, 1, 'RF Technology and Mode'));
        } else if (id === '01') {
          enumLine(out, ctx, '    ', 'Tx', 'tbl_bit_rates', rd(v, 1, 'Transmit Bit Rate'));
        } else if (id === '02') {
          enumLine(out, ctx, '    ', 'Rx', 'tbl_bit_rates', rd(v, 1, 'Receive Bit Rate'));
        } else if (id === '03') { // Table 92
          const f = rd(v, 1, 'NFC-B Data Exchange Configuration');
          const meta = { start: f.start, end: f.end };
          out.line(`    * NFC-B Data Exchange Config: ${f.v}`, meta);
          const b = parseInt(f.v, 16).toString(2).padStart(8, '0');
          const row = (label, bits) => out.line(`     ~ ${label}:`.padEnd(25) + bits.padStart(2), meta);
          row('Minimum TR0', b.slice(0, 2));
          row('Minimum TR1', b.slice(2, 4));
          row('Suppression of EoS', b.slice(4, 5));
          row('Suppression of SoS', b.slice(5, 6));
          row('Minimum TR3', b.slice(6, 8));
        }
      });
    }
  },

  // 41 0B
  RF_PARAMETER_UPDATE_RSP(r, out, ctx) {
    out.enumField(r, 1, 'Status', 'tbl_status_codes');
    const nf = rd(r, 1, 'Number of Parameters');
    const n = parseInt(nf.v, 16);
    out.line(`  * Number of Params: ${n}`, { start: nf.start, end: nf.end });
    out.line('  * RF Communication Param ID: ');
    for (let i = 0; i < n; i++) {
      enumLine(out, ctx, '  ', `Type ID ${i}`, 'tbl_rf_commu_para_id', rd(r, 1, 'RF Communication Parameter ID'));
    }
  },

  // 21 0C
  RF_INTF_EXT_START_CMD(r, out) {
    out.enumField(r, 1, 'RF Interface Extension', 'tbl_rf_if_exten');
    const lf = rd(r, 1, 'Start Parameter Length');
    const x = parseInt(lf.v, 16);
    out.line(`  * Start Param Len: ${x}`, { start: lf.start, end: lf.end });
    out.hexField(r, 1, 'Start Param', x);
  },

  // 41 0C
  RF_INTF_EXT_START_RSP: status,

  // 21 0D
  RF_INTF_EXT_STOP_CMD(r, out) {
    out.enumField(r, 1, 'RF Interface Extension', 'tbl_rf_if_exten');
    const lf = rd(r, 1, 'Stop Parameter Length');
    const x = parseInt(lf.v, 16);
    out.line(`  * Stop Param Len: ${x}`, { start: lf.start, end: lf.end });
    out.hexField(r, 1, 'Stop Param', x);
  },

  // 41 0D
  RF_INTF_EXT_STOP_RSP: status,

  // 21 0E
  RF_EXT_AGG_ABORT_CMD: empty,

  // 41 0E
  RF_EXT_AGG_ABORT_RSP: status,

  // 21 0F
  RF_NDEF_ABORT_CMD: empty,

  // 41 0F
  RF_NDEF_ABORT_RSP: status,

  // 21 10
  RF_ISO_DEP_NAK_PRESENCE_CMD: empty,

  // 41 10
  RF_ISO_DEP_NAK_PRESENCE_RSP: status,

  // 61 10
  RF_ISO_DEP_NAK_PRESENCE_NTF: status,

  // 21 11
  RF_SET_FORCED_NFCEE_ROUTING_CMD(r, out, ctx) {
    const sf = rd(r, 1, 'Forced NFCEE Routing State');
    const meta = { start: sf.start, end: sf.end };
    if (sf.v === '00') {
      out.line('  * Forced NFCEE Routing State: Disabled', meta);
    } else if (sf.v === '01') {
      out.line('  * Forced NFCEE Routing State: Enabled', meta);
      const idf = rd(r, 1, 'Forced NFCEE');
      const names = nfceeIdNames(ctx, idf.v);
      out.line(`  * Forced NFCEE: ${idf.v} ${names.exact} ${names.range}`, { start: idf.start, end: idf.end, table: 'tbl_nfcee_id' });
      const pf = rd(r, 1, 'Forced Power State');
      const bits = parseInt(pf.v, 16).toString(2).padStart(8, '0');
      out.line(`    * Power State: ${bits} (${pf.v})`, { start: pf.start, end: pf.end });
      powerStateLines(out, ctx, pf.v, '     ', 33, 'left', { start: pf.start, end: pf.end });
    } else {
      out.line(`  * Forced NFCEE Routing State: Error (${sf.v})`, meta);
    }
  },

  // 41 11
  RF_SET_FORCED_NFCEE_ROUTING_RSP: status,
};

export default handlers;
