// Port of nfc_forum_2_0_pkg/NCI_Core.py (GID 0x0 NCI Core).
// Conventions (see web/PORTING.md): handler(r: Reader, out: Out, ctx) — read with r,
// print with out using the exact Python text; tables via ctx.t()/out.enumField.
//
// Fixes vs. the original Python (now applied to Python too):
//   * CORE_RESET_NTF: label "Rest Trigger" -> "Reset Trigger"; zero-length
//     Manufacturer Specific Info no longer prints an empty line.
//   * CORE_INIT_RSP: Max Routing Table Size / Max NFC-V RF Frame Size decoded as
//     little-endian integers ("512 (0002)") instead of raw hex only.
//   * CORE_CONN_CREATE_CMD: NFCEE ID resolved through tbl_nfcee_id (was hardcoded),
//     RF Discovery ID resolves the "01-FF" range key, unknown Type no longer prints
//     "Val:" twice and the range notes are indented and only the matching one shown.
//   * CORE_SET_POWER_SUB_STATE_CMD: 03 (Sub-State 3) = Screen Off / Device Locked.
//   * VALUE_OF_CFG_PARA: LB_FWI_ADC_FO shows b3 (was b2); LN_WT is a WT exponent,
//     not milliseconds; undefined bit-rate values are RFU (only 80-FE proprietary).
import { DecodeError, reverseBytes } from '../../core/reader.js';
import { lookup } from '../../core/lookup.js';

// ---------- small helpers (Python idioms) ----------

/** Python: bin(int(hex, 16))[2:].zfill(8) — BigInt so multi-octet values stay exact */
export function bin8(hex) {
  if (!hex) throw new DecodeError('empty value');
  return BigInt(`0x${hex}`).toString(2).padStart(8, '0');
}

/** Python: int(hex, 16) printed in decimal */
export function dec(hex) {
  if (!hex) throw new DecodeError('empty value');
  return BigInt(`0x${hex}`).toString();
}

/** Python: '{0:<n}'.format(s) */
const ljust = (s, n) => s.padEnd(n);

/** low 4 bits of a Conn ID octet as the binary-string key of tbl_conn_id */
export function connIdText(ctx, hex) {
  const bits = parseInt(hex, 16).toString(2).padStart(8, '0').slice(4);
  return lookup(ctx.t('tbl_conn_id'), bits, 'Dynamically assigned by the NFCC');
}

/** read one octet and print "<indent>* label: <conn & 0x0F> (<conn id meaning>)" */
function connIdField(r, out, ctx, level, label) {
  const start = r.abs;
  const v = r.hex(1, label);
  // Conn ID is the low 4 bits only (upper bits RFU)
  out.kv(level, label, `${parseInt(v, 16) & 0x0f} (${connIdText(ctx, v)})`, { start, end: r.abs, table: 'tbl_conn_id' });
  return v;
}

/** read n octets, print "<indent>* label: <LE int> (<HEX>)" */
function leIntField(r, out, level, label, n) {
  const start = r.abs;
  const v = r.hex(n, label);
  out.kv(level, label, `${parseInt(reverseBytes(v), 16)} (${v})`, { start, end: r.abs });
  return v;
}

// ---------- NFCC Features (CORE_INIT_RSP) ----------

/** decode the 4-octet NFCC Features field (Table 10). `feat` = 8 hex chars, start = abs offset */
export function NFCC_FEATURES(out, ctx, feat, start) {
  const m = (k) => ({ start: start + k, end: start + k + 1 });
  const oct0 = bin8(feat.slice(0, 2));
  out.blank();
  out.line(`    * Octet 0: ${oct0}`, m(0));
  out.line(ljust('     ~ Active Communication Mode: ', 40)
    + (oct0[3] === '1' ? 'Support' : 'Not support'), m(0));
  out.line(ljust('     ~ HCI Network Support: ', 40)
    + (oct0[4] === '1' ? 'Implements as defined in [ETSI_102622]' : 'Not implement'), m(0));
  const cfgMode = oct0.slice(5, 7);
  out.line(ljust('     ~ Discovery Cfg Mode: ', 40)
    + (cfgMode === '00' ? 'The DH is the only entity that configs the NFCC.'
      : cfgMode === '01' ? 'The NFCC can receive configs from the DH and other NFCEEs.' : 'RFU'), m(0));
  out.line(ljust('     ~ Discovery Freq Cfg: ', 40)
    + (oct0[7] === '1' ? 'Supported in RF_DISCOVER_CMD' : 'Ignored in RF_DISCOVER_CMD'), m(0));

  const oct1 = bin8(feat.slice(2, 4));
  out.blank();
  out.line(`    * Octet 1: ${oct1}`, m(1));
  const t1 = ctx.t('tbl_nfcc_feat_oct1');
  for (let i = 6; i > 0; i--) {
    out.line(ljust(`     ~ ${t1[String(i)] ?? 'RFU'}: `, 40)
      + (oct1[7 - i] === '1' ? 'Support' : 'Not support'), { ...m(1), table: 'tbl_nfcc_feat_oct1' });
  }

  const oct2 = bin8(feat.slice(4, 6));
  out.blank();
  out.line(`    * Octet 2: ${oct2}`, m(2));
  const t2 = ctx.t('tbl_nfcc_feat_oct2');
  for (let i = 3; i >= 0; i--) {
    out.line(ljust(`     ~ ${t2[String(i)] ?? 'RFU'}: `, 40)
      + (oct2[7 - i] === '1' ? 'Support' : 'Not support'), { ...m(2), table: 'tbl_nfcc_feat_oct2' });
  }

  const oct3 = bin8(feat.slice(6, 8));
  out.blank();
  out.line(`    * Octet 3: ${oct3} -- Proprietary`, m(3));
  out.blank();
}

// ---------- Config parameter values (SET_CONFIG_CMD / GET_CONFIG_RSP) ----------

const BAIL_OUT_TECH = { '08': 'NFC-A', 11: 'NFC-B', 19: 'NFC-F' };
const TEXT_PARAMS = {
  '09': 'As defined in [ACTIVITY] for the Collision Resolution Activity.',
  14: 'As defined in [ACTIVITY] for the Collision Resolution Activity.',
  '1A': 'As defined in [ACTIVITY] for the Collision Resolution Activity.',
  '2F': 'As defined in [ACTIVITY] for the Collision Resolution Activity.',
  10: 'Application family identifier (as defined in [DIGITAL]).',
  12: 'The values and coding of this parameter SHALL be as defined in [DIGITAL] for Param 1 of the ATTRIB command.',
  20: 'Higher layer INF field of the ATTRIB Command (as defined in [DIGITAL]).',
  29: 'General Bytes for ATR_REQ.',
  33: 'NFCID1 as defined in [DIGITAL].',
  39: 'NFCID0 as defined in [DIGITAL].',
  '3A': 'Application Data (Bytes 6-9) of SENSB_RES (as defined in [DIGITAL]).',
  '3B': 'Start-Up Frame Guard Time, as defined in [DIGITAL].',
  58: 'RATS Response Interface Byte TB(1) (defined in [DIGITAL]).',
  59: 'Historical Bytes (only applicable for Type 4A Tag) (defined in [DIGITAL]).',
  '5A': 'Higher Layer – Response field of the ATTRIB response (defined in [DIGITAL]).',
  61: 'General Bytes in ATR_RES (defined in [DIGITAL]).',
};
const BIT_RATE_PARAMS = new Set(['18', '21', '3E', '5B', '68']);
/** 1-octet bit-field parameters: decoded from the first octet only if Len > 1 */
const BITFIELD_1OCT = new Set(['02', '13', '2A', '30', '31', '32', '38', '3C', '50', '5C', '62', '82', '85']);

/** Table 132 bit rate: defined value, 80-FE proprietary, anything else RFU */
export function bitRateText(ctx, val) {
  const tbl = ctx.t('tbl_bit_rates');
  const v = lookup(tbl, val, null);
  if (v !== null) return v;
  const n = /^[0-9A-F]{2}$/.test(val) ? parseInt(val, 16) : -1;
  return n >= 0x80 && n <= 0xfe ? 'For proprietary use' : 'RFU';
}

/**
 * Print the decoded value of a configuration parameter (Python VALUE_OF_CFG_PARA).
 * @param {Out} out
 * @param {object} ctx
 * @param {string} id    1-octet parameter ID, uppercase hex
 * @param {string} val   whole value, uppercase hex (non-empty)
 * @param {number} [start] absolute byte offset of val in the packet (for highlighting)
 */
export function VALUE_OF_CFG_PARA(out, ctx, id, val, start) {
  const meta = start === undefined ? {} : { start, end: start + val.length / 2 };
  let lenWarning = null;
  if (BITFIELD_1OCT.has(id) && val.length > 2) {
    lenWarning = `      * Warning: Len ${val.length / 2}, expected 1 (raw ${val})`;
    val = val.slice(0, 2);
  }
  VALUE_OF_CFG_PARA_BODY(out, ctx, id, val, meta);
  if (lenWarning !== null) out.line(lenWarning, meta);
}

function VALUE_OF_CFG_PARA_BODY(out, ctx, id, val, meta) {
  const p = (text) => out.line(text, meta);
  const idN = parseInt(id, 16);

  if (id === '00') { // TOTAL_DURATION
    p(`    * Val: ${parseInt(val.slice(2, 4) + val.slice(0, 2), 16)} ms (${val})`);
  } else if (id === '02') { // CON_DISCOVERY_PARAM
    const b = bin8(val);
    p(`    * Val: ${b} (${val})`);
    p(`${ljust('     ~ Polling Mode:', 20)} ${b[7] === '1' ? 'Enabled' : 'Disabled'}`);
    p(`${ljust('     ~ DH-NFCEE:', 20)} ${b[6] === '1' ? 'Disabled' : 'Enabled'}`);
  } else if (id === '03') { // POWER_STATE
    p(`    * Val: ${val}`);
    p(val === '02' ? '     ~ Current CORE_GET_CONFIG_CMD apply for Switched Off State' : '     ~ RFU');
  } else if (id in BAIL_OUT_TECH) { // PA/PB/PF_BAIL_OUT
    p(`    * Val: ${val}`);
    const res = val === '00' ? 'Not apply' : val === '01' ? 'Apply' : 'RFU';
    p(`     ~ Bail out when ${BAIL_OUT_TECH[id]} Technology has been detected: ${res}`);
  } else if (id === '13') { // PB_SENSB_REQ_PARAM
    const b = bin8(val);
    p(`    * Val: ${b} (${val})`);
    p(`     ~ Extended SENSB_RES: ${b[3] === '1' ? 'Support' : 'Not support'}`);
  } else if (BIT_RATE_PARAMS.has(id)) { // PF/PI/LB/LI_A/PACM_BIT_RATE
    out.line(`    * Val: ${bitRateText(ctx, val)} (${val})`, { ...meta, table: 'tbl_bit_rates' });
  } else if (id === '28') { // PN_NFC_DEP_PSL
    p(`    * Val: ${val}`);
    p(`     ~ Bit Rates and Length Reduction: ${val === '00' ? 'Highest available' : val === '01' ? 'Maintain' : 'RFU'}`);
  } else if (id === '2A' || id === '62') { // PN_ATR_REQ_CONFIG, LN_ATR_RES_CONFIG
    const b = bin8(val);
    p(`    * Val: ${b} (${val})`);
    p('     ~ NOTE: Needs to be always set to 0x30 for LLCP');
    p(`     ~ Value for LR: ${b.slice(2, 4)}`);
  } else if (id === '30') { // LA_BIT_FRAME_SDD
    p(`    * Val: ${bin8(val)} (${val})`);
    p('     ~ Bit Frame SDD value to be sent in Byte 1 of SENS_RES. This is a 5-bit value.');
  } else if (id === '31') { // LA_PLATFORM_CONFIG
    p(`    * Val: ${bin8(val)} (${val})`);
    p('     ~ Platform Configuration value to be sent in Byte 2 of SENS_RES. This is a 4-bit value.');
  } else if (id === '32') { // LA_SEL_INFO
    const b = bin8(val);
    p(`    * Val: ${b} (${val})`);
    p(`     ~ NFC-DEP Protocol: ${b[1] === '1' ? 'Supported' : 'Not supported'}`);
    p(`     ~ ISO-DEP Protocol: ${b[2] === '1' ? 'Supported' : 'Not supported'}`);
  } else if (id === '38') { // LB_SENSB_INFO
    const b = bin8(val);
    p(`    * Val: ${b} (${val})`);
    p(`     ~ ISO-DEP Protocol: ${b[7] === '1' ? 'Supported' : 'Not supported'}`);
  } else if (id === '3C') { // LB_FWI_ADC_FO
    const b = bin8(val);
    p(`    * Val: ${b} (${val})`);
    p(`     ~ Frame Waiting time Integer: ${parseInt(b.slice(0, 4), 2)} (${b.slice(0, 4)})`);
    // fix: b3 is val_b[4] (Python printed val_b[5], i.e. b2)
    p(`     ~ b3 of ADC Coding field of SENSB_RES (Byte 12) as defined in [DIGITAL] (${b[4]})`);
    p(`     ~ If set to 1b DID MAY be used. Otherwise it SHALL NOT be used. (${b[7]})`);
  } else if (idN >= 0x40 && idN <= 0x4f) { // LF_T3T_IDENTIFIERS_1..16
    p(`    * Val: ${val}`);
    p(`     ~ System Code of T3T Emulation: ${val.slice(0, 4)}`);
    p(`     ~ NFCID2 for the T3T Platform: ${val.slice(4, 20)}`);
    p(`     ~ PAD0, PAD1, MRTI_check, MRTI_update and PAD2 of SENSF_RES: ${val.slice(20, 36)}`);
  } else if (id === '52') { // LF_T3T_MAX
    const n = BigInt(`0x${val}`);
    p(n <= 16n ? `    * Val: ${n}` : `    * Val: RFU (${val})`);
  } else if (id === '53') { // LF_T3T_FLAGS
    if (val.length < 4) throw new DecodeError('LF_T3T_FLAGS needs 2 octets');
    const o0 = bin8(val.slice(0, 2));
    const o1 = bin8(val.slice(2, 4));
    const rev = [...o0].reverse().join('') + [...o1].reverse().join('');
    p(`    * Val: ${o0} ${o1} (${val})`);
    for (let i = 1; i <= 16; i++) {
      p(`${ljust(`     ~ LF_T3T_IDENTIFIERS_${i}:`, 30)} ${rev[i - 1] === '1' ? 'Enabled' : 'Disabled'}`);
    }
  } else if (id === '55') { // LF_T3T_RD_ALLOWED
    if (val === '00') {
      p(`    * Val: ${val}`);
      p('     ~ The NFCC SHALL NOT include RD bytes in its SENSF_RES if it receives a SENSF_REQ with RC set to 0x02.');
    } else if (val === '01') {
      p(`    * Val: ${val}`);
      p('     ~ The NFCC MAY include RD bytes in its SENSF_RES if it receives a SENSF_REQ with RC set to 0x02.');
    } else {
      p(`    * Val: RFU (${val})`);
    }
  } else if (id === '50') { // LF_PROTOCOL_TYPE
    const b = bin8(val);
    p(`    * Val: ${b} (${val})`);
    p(`     ~ NFC-DEP Protocol: ${b[6] === '1' ? 'Supported' : 'Not supported'}`);
  } else if (id === '5C') { // LI_A_RATS_TC1
    const b = bin8(val);
    p(`    * Val: ${b} (${val})`);
    p(`     ~ If set to 1b DID MAY be used. Otherwise it SHALL NOT be used. (${b[6]})`);
  } else if (id === '60') { // LN_WT
    // fix: WT is an exponent (0..14), not milliseconds: RWT = (256*16/fc) * 2^WT
    const n = Number(BigInt(`0x${val}`));
    p(`    * Val: ${n} (${val})`);
    if (n <= 14) {
      const ms = ((256 * 16) / 13.56e6) * 2 ** n * 1000;
      p(`     ~ Waiting Time defined in [DIGITAL]: RWT = 256*16/fc * 2^WT = ${ms.toFixed(3)} ms`);
    } else {
      p('     ~ Waiting Time defined in [DIGITAL]: RFU (WT > 14)');
    }
  } else if (id in TEXT_PARAMS) {
    p(`    * Val: ${val}`);
    p(`     ~ ${TEXT_PARAMS[id]}`);
  } else if (id === '80' || id === '81') { // RF_FIELD_INFO, RF_NFCEE_ACTION
    const ntf = id === '80' ? 'RF_FIELD_INFO_NTF' : 'RF_NFCEE_ACTION_NTF';
    if (val === '00' || val === '01') {
      p(`    * Val: ${val}`);
      p(`     ~ ${ntf}: ${val === '00' ? 'Disabled' : 'Enabled'}`);
    } else {
      p(`    * Val: RFU (${val})`);
    }
  } else if (id === '82') { // NFCDEP_OP
    const b = bin8(val);
    p(`    * Val: ${b} (${val})`);
    p(`     ~ Waiting Time: ${b[3] === '1' ? '<= 10' : '<= WT_(NFCDEP,MAX)'}`);
    if (b[4] === '1') p('     ~ All PDUs indicating chaining (MI bit set) SHALL use the maximum number of Transport Data Bytes.');
    if (b[5] === '1') p('     ~ Info PDU with no Transport Data Bytes SHALL NOT be sent.');
    if (b[6] === '1') p('     ~ NFC-DEP Initiator SHALL use the ATTENTION command only as the error recovery procedure described in [DIGITAL].');
    if (b[7] === '1') p('     ~ NFC-DEP Target SHALL NOT send RTOX requests.');
  } else if (id === '83') { // LLCP_VERSION
    p(`    * Val: ${parseInt(val[0], 16)}.${parseInt(val[1], 16)} (${val})`);
  } else if (id === '85') { // NFCC_CONFIG_CONTROL
    const b = bin8(val);
    p(`    * Val: ${b} (${val})`);
    p(b[7] === '0' ? '     ~ NFCC is not allowed to manage RF config.' : '     ~ NFCC is allowed to manage RF config.');
  } else {
    p(`    * Val: ${val}`);
  }
}

/**
 * Parameter [1..n] TLV list shared by CORE_SET_CONFIG_CMD and CORE_GET_CONFIG_RSP.
 * `valueFn(out, ctx, id, val, start)` decodes each value (VALUE_OF_CFG_PARA by default,
 * vendors pass their own).
 */
export function CFG_PARAM_LIST(r, out, ctx, n, valueFn = VALUE_OF_CFG_PARA) {
  for (let i = 0; i < n; i++) {
    out.blank();
    out.line(`   ~ [Param_${i}] ~  `);
    const id = out.enumField(r, 2, 'ID', 'tbl_cfg_para');
    const lenStart = r.abs;
    const m = r.u8('Len');
    out.kv(2, 'Len', m, { start: lenStart, end: r.abs });
    if (m !== 0) {
      const start = r.abs;
      const val = r.hex(m, 'Val');
      valueFn(out, ctx, id, val, start);
    }
  }
}

/** "  * Number of Params: n" */
function numParams(r, out, label = 'Number of Params') {
  const start = r.abs;
  const n = r.u8(label);
  out.kv(1, label, n, { start, end: r.abs });
  return n;
}

/** "    * ID i: NAME (XX)" list */
function paramIdList(r, out, ctx, n) {
  for (let i = 0; i < n; i++) {
    const start = r.abs;
    const id = r.hex(1, 'Param ID');
    out.line(`    * ID ${i}: ${ctx.lookup('tbl_cfg_para', id)} (${id})`, { start, end: r.abs, table: 'tbl_cfg_para' });
  }
}

// CORE_CONN_CREATE_CMD: notes for NFCEE ID / dest-spec Type ranges
const stripParens = (s) => s.replace(/^\((.*)\)$/, '$1');

const handlers = {
  // 20 00
  CORE_RESET_CMD(r, out) {
    out.enumField(r, 1, 'Reset Type', 'tbl_cfg_status');
  },

  // 40 00
  CORE_RESET_RSP(r, out) {
    out.enumField(r, 1, 'Status', 'tbl_status_codes');
  },

  // 60 00
  CORE_RESET_NTF(r, out) {
    out.enumField(r, 1, 'Reset Trigger', 'tbl_rst_trig'); // fix: Python label "Rest Trigger"
    out.enumField(r, 1, 'Config Status', 'tbl_cfg_status');
    out.enumField(r, 1, 'NCI Version', 'tbl_nci_ver');
    let start = r.abs;
    const mfg = r.hex(1, 'Manufacturer ID');
    out.kv(1, 'Manufacturer ID', mfg === '00' ? 'Info is not available.' : mfg, { start, end: r.abs });
    const n = r.u8('Manufacturer Specific Information Length');
    if (n !== 0) { // fix: Python compared the hex string with 0 (always true)
      start = r.abs;
      const info = r.hex(n, 'Manufacturer Specific Information');
      out.kv(1, 'Manufacturer Specific Info', info, { start, end: r.abs });
    }
  },

  // 20 01
  CORE_INIT_CMD(r, out) {
    const start = r.abs;
    const feature = r.hex(2, 'Feature Enable');
    out.line(`  * Feature Enable: ${feature} -- RFU`, { start, end: r.abs });
  },

  // 40 01
  CORE_INIT_RSP(r, out, ctx) {
    out.enumField(r, 1, 'Status', 'tbl_status_codes');

    let start = r.abs;
    const feat = r.hex(4, 'NFCC Features');
    out.kv(1, 'NFCC Features', feat, { start, end: r.abs });
    NFCC_FEATURES(out, ctx, feat, start);

    start = r.abs;
    const maxConn = r.hex(1, 'Max Logical Connections');
    const maxConnN = parseInt(maxConn, 16);
    out.kv(1, 'Max Logical Connections',
      maxConnN >= 15 && ctx.vendorKey === 'forum20' ? `RFU (${maxConn})` : `${maxConnN} (${maxConn})`,
      { start, end: r.abs });

    leIntField(r, out, 1, 'Max Routing Table Size', 2); // fix: was raw hex only

    start = r.abs;
    const maxCtl = r.hex(1, 'Max Control Packet Payload Size');
    const maxCtlN = parseInt(maxCtl, 16);
    out.kv(1, 'Max Control Packet Payload Size',
      maxCtlN < 32 ? `Invalid size (${maxCtl})` : `${maxCtlN} (${maxCtl})`, { start, end: r.abs });

    for (const label of ['Max Data Packet Payload Size of the Static HCI Connection',
      'Number of Credits of the Static HCI Connection']) {
      start = r.abs;
      const v = r.hex(1, label);
      out.kv(1, label, `${parseInt(v, 16)} (${v})`, { start, end: r.abs });
    }

    leIntField(r, out, 1, 'Max NFC-V RF Frame Size', 2); // fix: was raw hex only

    start = r.abs;
    const n = r.u8('Number of Supported RF Interfaces');
    out.kv(1, 'Number of Supported RF Interfaces', n, { start, end: r.abs });
    out.kv(1, 'Supported RF Interface', r.peekHex(r.remaining), { start: r.abs, end: r.abs + r.remaining });
    for (let i = 0; i < n; i++) {
      out.blank();
      out.line(`   ~ [RF_IF_${i}] ~  `);
      out.enumField(r, 2, 'Interface', 'tbl_rf_if');
      start = r.abs;
      const x = r.u8('Number of Extensions');
      out.kv(2, 'Number of Extensions', x, { start, end: r.abs });
      for (let j = 0; j < x; j++) out.enumField(r, 2, `Extension ${j}`, 'tbl_rf_if_exten');
    }
  },

  // 20 02
  CORE_SET_CONFIG_CMD(r, out, ctx) {
    const n = numParams(r, out);
    CFG_PARAM_LIST(r, out, ctx, n);
  },

  // 40 02
  CORE_SET_CONFIG_RSP(r, out, ctx) {
    out.enumField(r, 1, 'Status', 'tbl_status_codes');
    const n = numParams(r, out);
    if (n !== 0) {
      out.line('  * Set Param ID:');
      paramIdList(r, out, ctx, n);
    }
  },

  // 20 03
  CORE_GET_CONFIG_CMD(r, out, ctx) {
    const n = numParams(r, out);
    out.line('  * Get Param ID:');
    paramIdList(r, out, ctx, n);
  },

  // 40 03
  CORE_GET_CONFIG_RSP(r, out, ctx) {
    out.enumField(r, 1, 'Status', 'tbl_status_codes');
    const n = numParams(r, out);
    CFG_PARAM_LIST(r, out, ctx, n);
  },

  // 20 04
  CORE_CONN_CREATE_CMD(r, out, ctx) {
    out.enumField(r, 1, 'Destination Type', 'tbl_dest_type');
    const n = numParams(r, out, 'Number of Destination-specific Params');
    for (let i = 0; i < n; i++) {
      out.blank();
      out.line(`   ~ [Dest-spec Parameter_${i}] ~  `);
      const type = out.enumField(r, 2, 'Type', 'tbl_d_spec_type');
      let start = r.abs;
      const m = r.u8('Len');
      out.kv(2, 'Len', m, { start, end: r.abs });
      start = r.abs;
      const val = r.hex(m, 'Val');
      const meta = { start, end: r.abs };
      out.kv(2, 'Val', val, meta);
      const o0 = val.slice(0, 2);
      const o1 = val.slice(2, 4);
      const m0 = { start, end: start + 1 };
      const m1 = { start: start + 1, end: start + 2 };
      if (type === '00') { // RF Discovery ID (Table 67) + RF Protocol (Table 133)
        // fix: range key "01-FF" resolved (Python printed the bare hex)
        out.kv(3, 'RF Discovery ID', `${ctx.lookup('tbl_rf_dis_id', o0)} (${o0})`, { ...m0, table: 'tbl_rf_dis_id' });
        out.kv(3, 'RF Protocol', `${ctx.lookup('tbl_rf_proto', o1)} (${o1})`, { ...m1, table: 'tbl_rf_proto' });
      } else if (type === '01') { // NFCEE ID (Table 116) + NFCEE Interface Protocol (Table 136)
        // fix: use tbl_nfcee_id instead of hardcoded strings + unindented range notes
        out.kv(3, 'NFCEE ID', `${stripParens(ctx.lookup('tbl_nfcee_id', o0))} (${o0})`, { ...m0, table: 'tbl_nfcee_id' });
        out.kv(3, 'NFCEE Interface Protocol', `${ctx.lookup('tbl_nfcee_proto', o1)} (${o1})`, { ...m1, table: 'tbl_nfcee_proto' });
      } else {
        // fix: Python printed "Val:" a second time plus both range notes unindented
        const t = parseInt(type, 16);
        out.line(`      ~ Type ${type}: ${t >= 0xa0 ? 'For proprietary use' : 'RFU'}`, meta);
      }
    }
  },

  // 40 04
  CORE_CONN_CREATE_RSP(r, out, ctx) {
    out.enumField(r, 1, 'Status', 'tbl_status_codes');
    let start = r.abs;
    const maxData = r.hex(1, 'Max Data Packet Payload Size');
    out.kv(1, 'Max Data Packet Payload Size', parseInt(maxData, 16), { start, end: r.abs });
    start = r.abs;
    const cr = r.hex(1, 'Initial Number of Credits');
    const tbl = ctx.t('tbl_init_credits');
    out.kv(1, 'Initial Number of Credits',
      Object.prototype.hasOwnProperty.call(tbl, cr) ? tbl[cr] : parseInt(cr, 16),
      { start, end: r.abs, table: 'tbl_init_credits' });
    connIdField(r, out, ctx, 1, 'Conn ID');
  },

  // 20 05
  CORE_CONN_CLOSE_CMD(r, out, ctx) {
    connIdField(r, out, ctx, 1, 'Conn ID');
  },

  // 40 05
  CORE_CONN_CLOSE_RSP(r, out) {
    out.enumField(r, 1, 'Status', 'tbl_status_codes');
  },

  // 60 06
  CORE_CONN_CREDITS_NTF(r, out, ctx) {
    const n = numParams(r, out, 'Number of Entries');
    for (let i = 0; i < n; i++) {
      out.blank();
      out.line(`   ~ [Entry_${i}] ~  `);
      connIdField(r, out, ctx, 2, 'Conn ID');
      const start = r.abs;
      const cr = r.u8('Credits');
      out.kv(2, 'Credits', cr, { start, end: r.abs });
    }
  },

  // 60 07
  CORE_GENERIC_ERROR_NTF(r, out) {
    out.enumField(r, 1, 'Status', 'tbl_status_codes');
  },

  // 60 08
  CORE_INTERFACE_ERROR_NTF(r, out, ctx) {
    out.enumField(r, 1, 'Status', 'tbl_status_codes');
    connIdField(r, out, ctx, 1, 'Conn ID');
  },

  // 20 09
  CORE_SET_POWER_SUB_STATE_CMD(r, out) {
    const start = r.abs;
    const v = r.hex(1, 'Power State');
    const meta = { start, end: r.abs };
    const states = {
      '00': ['Switched On State', 'On', 'Unlocked'],
      '01': ['Switched On Sub-State 1', 'Off', 'Unlocked'],
      '02': ['Switched On Sub-State 2', 'On', 'Locked'],
      '03': ['Switched On Sub-State 3', 'Off', 'Locked'], // fix: Python said Unlocked (Table 59: Screen Off lock)
    };
    const s = states[v];
    if (s) {
      out.kv(1, 'Power State', s[0], meta);
      out.kv(2, 'Screen', s[1], meta);
      out.kv(2, 'Device', s[2], meta);
    } else {
      out.kv(1, 'Power State', `RFU (${v})`, meta);
    }
  },

  // 40 09
  CORE_SET_POWER_SUB_STATE_RSP(r, out) {
    out.enumField(r, 1, 'Status', 'tbl_status_codes');
  },
};

export default handlers;
