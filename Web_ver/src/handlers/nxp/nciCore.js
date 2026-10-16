// Port of Nxp_pkg/NCI_Core.py (GID 0x0 NCI Core, NXP SN2x0).
// Most handlers delegate to the forum port (tables come from ctx = NXP set).
// NXP-specific: CORE_RESET_NTF, CORE_SET_CONFIG_CMD, CORE_SET_CONFIG_RSP (bug fix:
// A0xx/A1xx extended IDs), CORE_GET_CONFIG_CMD/RSP, CORE_CONN_CREATE_RSP, plus the
// NXP copy of VALUE_OF_CFG_PARA and VALUE_OF_REGISTER (A0xx / A1xx parameters).
// Cross-packet module globals live in ctx.state: ULPDET_CFG (A10F -> A015),
// RSTN_CFG (A007 -> A08E), PWR_MODE_00 (Proprietary 2F 00 -> A10B).
import forum from '../forum20/nciCore.js';

// ---------------------------------------------------------------- py helpers

class PyValueError extends Error {
  constructor(message) {
    super(message);
    this.name = 'ValueError';
  }
}

/** Python int(s, 16) (raises on '' / non-hex) -> Number */
function int16(s) {
  if (!/^[0-9A-Fa-f]+$/.test(s)) throw new PyValueError(`invalid literal for int() with base 16: '${s}'`);
  return Number(BigInt(`0x${s}`));
}
/** Python str(int(s, 16)) (exact for long values) */
function int16Str(s) {
  if (!/^[0-9A-Fa-f]+$/.test(s)) throw new PyValueError(`invalid literal for int() with base 16: '${s}'`);
  return BigInt(`0x${s}`).toString();
}
/** Python bin(int(s, 16))[2:].zfill(n) */
function bin(s, n = 8) {
  if (!/^[0-9A-Fa-f]+$/.test(s)) throw new PyValueError(`invalid literal for int() with base 16: '${s}'`);
  return BigInt(`0x${s}`).toString(2).padStart(n, '0');
}
/** Python int(binstr, 2) */
function int2(s) {
  if (!/^[01]+$/.test(s)) throw new PyValueError(`invalid literal for int() with base 2: '${s}'`);
  return parseInt(s, 2);
}
/** little-endian 2 octets at hex-char offset off: int(v[o:o+2]) + int(v[o+2:o+4])*256 */
const le2 = (v, off) => int16(v.slice(off, off + 2)) + int16(v.slice(off + 2, off + 4)) * 256;
/** little-endian hex string of any length -> BigInt (Python _le_int) */
const leInt = (v) => BigInt(int16Str((v.match(/../g) || []).reverse().join('')));

/** Python repr(float) */
export function pyFloat(x) {
  if (Number.isNaN(x)) return 'nan';
  if (!Number.isFinite(x)) return x > 0 ? 'inf' : '-inf';
  if (x === 0) return Object.is(x, -0) ? '-0.0' : '0.0';
  const [m, e] = x.toExponential().split('e');
  const exp = Number(e);
  const neg = m.startsWith('-');
  const digits = m.replace('-', '').replace('.', '');
  let s;
  if (exp >= -4 && exp < 16) {
    if (exp >= 0) {
      s = digits.length <= exp + 1
        ? `${digits}${'0'.repeat(exp + 1 - digits.length)}.0`
        : `${digits.slice(0, exp + 1)}.${digits.slice(exp + 1)}`;
    } else {
      s = `0.${'0'.repeat(-exp - 1)}${digits}`;
    }
  } else {
    s = `${digits[0]}${digits.length > 1 ? `.${digits.slice(1)}` : ''}e${exp < 0 ? '-' : '+'}${String(Math.abs(exp)).padStart(2, '0')}`;
  }
  return neg ? `-${s}` : s;
}

/** Python '{:.Nf}'.format(x) (round-half-even on exact ties, like CPython) */
export function pyFixed(x, d) {
  const exact = Math.abs(x).toFixed(Math.min(100, d + 60));
  const [ip, fp = ''] = exact.split('.');
  const tail = fp.slice(d);
  if (tail[0] === '5' && /^0*$/.test(tail.slice(1))) {
    let n = BigInt(ip + fp.slice(0, d));
    if (n % 2n === 1n) n += 1n;
    let s = n.toString().padStart(d + 1, '0');
    s = d > 0 ? `${s.slice(0, -d)}.${s.slice(-d)}` : s;
    return x < 0 && Number(n) !== 0 ? `-${s}` : s;
  }
  return x.toFixed(d);
}

/** Python str.format alignment: '<', '>', '^' */
function fmt(v, width, align = '<') {
  const s = String(v);
  if (s.length >= width) return s;
  const pad = width - s.length;
  if (align === '>') return ' '.repeat(pad) + s;
  if (align === '^') {
    const left = Math.floor(pad / 2);
    return ' '.repeat(left) + s + ' '.repeat(pad - left);
  }
  return s + ' '.repeat(pad);
}

/** Python str() of print args (None for undefined) */
const ps = (v) => (v === undefined || v === null ? 'None' : String(v));
/** Python print(*args) */
const pj = (...args) => args.map(ps).join(' ');
/** dict.get(key) without default */
const get = (tbl, key) => (Object.prototype.hasOwnProperty.call(tbl, key) ? tbl[key] : undefined);

// ---------------------------------------------------------------- VALUE_OF_CFG_PARA (NXP copy)

/**
 * NXP local copy of forum VALUE_OF_CFG_PARA (only 0x82 NFCDEP_OP differs).
 * @param {(text: string) => void} p  print one line
 */
export function VALUE_OF_CFG_PARA(id, val, p, ctx) {
  let lenWarning = null;
  if (BITFIELD_1OCT.has(id) && val.length > 2) {
    lenWarning = `      * Warning: Len ${val.length / 2}, expected 1 (raw ${val})`;
    val = val.slice(0, 2);
  }
  VALUE_OF_CFG_PARA_BODY(id, val, p, ctx);
  if (lenWarning !== null) p(lenWarning);
}

/** 1-octet bit-field parameters: decoded from the first octet only if Len > 1 */
const BITFIELD_1OCT = new Set(['02', '13', '2A', '30', '31', '32', '38', '3C', '50', '5C', '62', '82', '85']);

function VALUE_OF_CFG_PARA_BODY(id, val, p, ctx) {
  const idn = int16(id);
  if (id === '00') { // TOTAL_DURATION
    p(pj('    * Val:', int16(val.slice(2, 4) + val.slice(0, 2)), 'ms', `(${val})`));
  } else if (id === '02') { // CON_DISCOVERY_PARAM
    const b = bin(val);
    p(pj('    * Val:', b, `(${val})`));
    p(`${fmt('     ~ Polling Mode:', 20)} ${b.slice(7, 8) === '1' ? 'Enabled' : 'Disabled'}`);
    p(`${fmt('     ~ DH-NFCEE:', 20)} ${b.slice(6, 7) === '1' ? 'Disabled' : 'Enabled'}`);
  } else if (id === '03') { // POWER_STATE
    p(pj('    * Val:', val));
    p(val === '02' ? '     ~ Current CORE_GET_CONFIG_CMD apply for Switched Off State' : '     ~ RFU');
  } else if (id === '08' || id === '11' || id === '19') { // PA/PB/PF_BAIL_OUT
    p(`    * Val: ${val}`);
    const tech = { '08': 'NFC-A', 11: 'NFC-B', 19: 'NFC-F' }[id];
    const res = val === '00' ? 'Not apply' : val === '01' ? 'Apply' : 'RFU';
    p(pj(`     ~ Bail out when ${tech} Technology has been detected:`, res));
  } else if (['09', '14', '1A', '2F'].includes(id)) { // Px_DEVICES_LIMIT
    p(pj('    * Val:', val));
    p('     ~ As defined in [ACTIVITY] for the Collision Resolution Activity.');
  } else if (id === '10') { // PB_AFI
    p(pj('    * Val: ', val));
    p('     ~ Application family identifier (as defined in [DIGITAL]).');
  } else if (id === '12') { // PB_ATTRIB_PARAM1
    p(pj('    * Val:', val));
    p('     ~ The values and coding of this parameter SHALL be as defined in [DIGITAL] for Param 1 of the ATTRIB command.');
  } else if (id === '13') { // PB_SENSB_REQ_PARAM
    const b = bin(val);
    p(pj('    * Val:', b, `(${val})`));
    p(b.slice(3, 4) === '1' ? '     ~ Extended SENSB_RES: Support' : '     ~ Extended SENSB_RES: Not support');
  } else if (['18', '21', '3E', '5B', '68'].includes(id)) { // *_BIT_RATE
    p(pj('    * Val:', ctx.lookup('tbl_bit_rates', val, 'For proprietary use'), `(${val})`));
  } else if (id === '20') { // PI_B_H_INFO
    p(pj('    * Val:', val));
    p('     ~ Higher layer INF field of the ATTRIB Command (as defined in [DIGITAL]).');
  } else if (id === '28') { // PN_NFC_DEP_PSL
    p(pj('    * Val:', val));
    const res = val === '00' ? 'Highest available' : val === '01' ? 'Maintain' : 'RFU';
    p(pj('     ~ Bit Rates and Length Reduction:', res));
  } else if (id === '29') { // PN_ATR_REQ_GEN_BYTES
    p(pj('    * Val:', val));
    p('     ~ General Bytes for ATR_REQ.');
  } else if (id === '2A' || id === '62') { // PN_ATR_REQ_CONFIG, LN_ATR_RES_CONFIG
    const b = bin(val);
    p(pj('    * Val:', b, `(${val})`));
    p('     ~ NOTE: Needs to be always set to 0x30 for LLCP');
    p(pj('     ~ Value for LR:', b.slice(2, 4)));
  } else if (id === '30') { // LA_BIT_FRAME_SDD
    p(pj('    * Val:', bin(val), `(${val})`));
    p('     ~ Bit Frame SDD value to be sent in Byte 1 of SENS_RES. This is a 5-bit value.');
  } else if (id === '31') { // LA_PLATFORM_CONFIG
    p(pj('    * Val:', bin(val), `(${val})`));
    p('     ~ Platform Configuration value to be sent in Byte 2 of SENS_RES. This is a 4-bit value.');
  } else if (id === '32') { // LA_SEL_INFO
    const b = bin(val);
    p(pj('    * Val:', b, `(${val})`));
    p(b.slice(1, 2) === '1' ? '     ~ NFC-DEP Protocol: Supported' : '     ~ NFC-DEP Protocol: Not supported');
    p(b.slice(2, 3) === '1' ? '     ~ ISO-DEP Protocol: Supported' : '     ~ ISO-DEP Protocol: Not supported');
  } else if (id === '33') { // LA_NFCID1
    p(pj('    * Val:', val));
    p('     ~ NFCID1 as defined in [DIGITAL].');
  } else if (id === '38') { // LB_SENSB_INFO
    const b = bin(val);
    p(pj('    * Val:', b, `(${val})`));
    p(b.slice(7, 8) === '1' ? '     ~ ISO-DEP Protocol: Supported' : '     ~ ISO-DEP Protocol: Not supported');
  } else if (id === '39') { // LB_NFCID0
    p(pj('    * Val:', val));
    p('     ~ NFCID0 as defined in [DIGITAL].');
  } else if (id === '3A') { // LB_APPLICATION_DATA
    p(pj('    * Val:', val));
    p('     ~ Application Data (Bytes 6-9) of SENSB_RES (as defined in [DIGITAL]).');
  } else if (id === '3B') { // LB_SFGI
    p(pj('    * Val:', val));
    p('     ~ Start-Up Frame Guard Time, as defined in [DIGITAL].');
  } else if (id === '3C') { // LB_FWI_ADC_FO
    const b = bin(val);
    p(pj('    * Val:', b, `(${val})`));
    p(pj('     ~ Frame Waiting time Integer:', int2(b.slice(0, 4)), `(${b.slice(0, 4)})`));
    p(pj('     ~ b3 of ADC Coding field of SENSB_RES (Byte 12) as defined in [DIGITAL]', `(${b.slice(5, 6)})`));
    p(pj('     ~ If set to 1b DID MAY be used. Otherwise it SHALL NOT be used.', `(${b.slice(7, 8)})`));
  } else if (idn >= 64 && idn <= 79) { // LF_T3T_IDENTIFIERS_1~16
    p(pj('    * Val:', val));
    p(pj('     ~ System Code of T3T Emulation:', val.slice(0, 4)));
    p(pj('     ~ NFCID2 for the T3T Platform:', val.slice(4, 20)));
    p(pj('     ~ PAD0, PAD1, MRTI_check, MRTI_update and PAD2 of SENSF_RES:', val.slice(20, 36)));
  } else if (id === '52') { // LF_T3T_MAX
    if (int16(val) <= 16) p(pj('    * Val:', int16Str(val)));
    else p(pj('    * Val:', 'RFU', `(${val})`));
  } else if (id === '53') { // LF_T3T_FLAGS
    const o0 = bin(val.slice(0, 2));
    const o1 = bin(val.slice(2, 4));
    const r = [...o0].reverse().join('') + [...o1].reverse().join('');
    p(pj('    * Val:', o0, o1, `(${val})`));
    for (let i = 1; i < 17; i++) {
      if (r[i - 1] === undefined) throw new Error(`IndexError: string index out of range`);
      p(`${fmt(`     ~ LF_T3T_IDENTIFIERS_${i}:`, 30)} ${r[i - 1] === '1' ? 'Enabled' : 'Disabled'}`);
    }
  } else if (id === '55') { // LF_T3T_RD_ALLOWED
    if (val === '00') {
      p(pj('    * Val:', val));
      p('     ~ The NFCC SHALL NOT include RD bytes in its SENSF_RES if it receives a SENSF_REQ with RC set to 0x02.');
    } else if (val === '01') {
      p(pj('    * Val:', val));
      p('     ~ The NFCC MAY include RD bytes in its SENSF_RES if it receives a SENSF_REQ with RC set to 0x02.');
    } else {
      p(pj('    * Val:', 'RFU', `(${val})`));
    }
  } else if (id === '50') { // LF_PROTOCOL_TYPE
    const b = bin(val);
    p(pj('    * Val:', b, `(${val})`));
    p(b.slice(6, 7) === '1' ? '     ~ NFC-DEP Protocol: Supported' : '     ~ NFC-DEP Protocol: Not supported');
  } else if (id === '58') { // LI_A_RATS_TB1
    p(pj('    * Val:', val));
    p('     ~ RATS Response Interface Byte TB(1) (defined in [DIGITAL]).');
  } else if (id === '59') { // LI_A_HIST_BY
    p(pj('    * Val:', val));
    p('     ~ Historical Bytes (only applicable for Type 4A Tag) (defined in [DIGITAL]).');
  } else if (id === '5A') { // LI_B_H_INFO_RESP
    p(pj('    * Val:', val));
    p('     ~ Higher Layer – Response field of the ATTRIB response (defined in [DIGITAL]).');
  } else if (id === '5C') { // LI_A_RATS_TC1
    const b = bin(val);
    p(pj('    * Val:', b, `(${val})`));
    p(pj('     ~ If set to 1b DID MAY be used. Otherwise it SHALL NOT be used.', `(${b.slice(6, 7)})`));
  } else if (id === '60') { // LN_WT
    p(pj('    * Val:', int16Str(val), `ms (${val})`));
    p('     ~ Waiting Time defined in [DIGITAL].');
  } else if (id === '61') { // LN_ATR_RES_GEN_BYTES
    p(pj('    * Val:', val));
    p('     ~ General Bytes in ATR_RES (defined in [DIGITAL]).');
  } else if (id === '80' || id === '81') { // RF_FIELD_INFO, RF_NFCEE_ACTION
    const what = id === '80' ? 'RF_FIELD_INFO_NTF:' : 'RF_NFCEE_ACTION_NTF:';
    if (val === '00' || val === '01') {
      p(pj('    * Val:', val));
      p(pj(`     ~ ${what}`, val === '00' ? 'Disabled' : 'Enabled'));
    } else {
      p(pj('    * Val:', 'RFU', `(${val})`));
    }
  } else if (id === '82') { // NFCDEP_OP
    const b = bin(val);
    const ap = (bit) => (bit === '1' ? 'Apply' : 'Not apply');
    p(pj('    * Val:', b, `(${val})`));
    p(pj('     ~ Waiting Time:', b.slice(3, 4) === '1' ? '<= 10' : '<= WT_(NFCDEP,MAX)'));
    p(pj('     ~ PDUs chaining (MI bit set) with max Transport Data Bytes:', ap(b.slice(4, 5))));
    p(pj('     ~ PDU with no Transport Data Bytes SHALL NOT be sent:', ap(b.slice(5, 6))));
    p(pj('     ~ Initiator SHALL use ATTENTION CMD only as error recovery procedure:', ap(b.slice(6, 7))));
    p(pj('     ~ NFC-DEP Target SHALL NOT send RTOX requests:', ap(b.slice(7, 8))));
  } else if (id === '83') { // LLCP_VERSION
    p(pj('    * Val:', `${int16(val.slice(0, 1))}.${int16(val.slice(1, 2))}`, `(${val})`));
  } else if (id === '85') { // NFCC_CONFIG_CONTROL
    const b = bin(val);
    p(pj('    * Val:', b, `(${val})`));
    if (b.slice(7, 8) === '0') p('     ~ NFCC is not allowed to manage RF config.');
    else if (b.slice(7, 8) === '1') p('     ~ NFCC is allowed to manage RF config.');
  } else {
    p(`    * Val: ${val}`);
  }
}

// ---------------------------------------------------------------- VALUE_OF_REGISTER

const TBL_CAP_VAL = { 0: 'no internal cap (2 pF parasitic cap) (default)', 1: '4 pF', 2: '5 pF', 3: '6 pF', 4: '7 pF', 5: '8 pF', 6: '9 pF', 7: '10 pF' };
const TBL_SWP_BAUD = { '01': '200', '02': '416.7', '03': '833.3', '04': '910', '05': '1000', '06': '1250', '07': '1667' };
const TBL_PIPE = {
  A022: '      * Connectivity Pipe from NFCEE_eSE:',
  A023: '      * APDU Pipe from NFCEE_eSE:',
  A024: '      * Connectivity Pipe from NFCEE_UICC1:',
  A025: '      * APDU Pipe from NFCEE_UICC1:',
  A0E9: '      * Connectivity Pipe from NFCEE_UICC2:',
  A012: '      * APDU Pipe from NFCEE_eUICC:',
};
const TBL_PIPE_STATUS = { '00': 'Deleted', '01': 'Closed', '02': 'Open' };
const TBL_PIP_STATUS = { '00': 'Not created', '01': 'Created & Closed', '02': 'Open' };
const TBL_MERGE_SAK = { '01': 'Merge between different NFCEE requests.', '02': 'Force clear', '03': 'Force merge' };

/** signed 4-bit nibble: (x ^ 0x8) - 0x8 */
const s4 = (h) => (int16(h) ^ 0x8) - 0x8;
/** signed byte: (x ^ 0x80) - 0x80 */
const s8 = (h) => (int16(h) ^ 0x80) - 0x80;

/**
 * NXP extended config parameter (2-octet tag A0xx / A1xx).
 * @param {string} tag   e.g. 'A015'
 * @param {string} val   value hex
 * @param {number} valLen Len field (octets)
 * @param {(text: string) => void} p  print one line
 */
export function VALUE_OF_REGISTER(tag, val, valLen, p, ctx) {
  const st = ctx.state;
  st.ULPDET_CFG ??= '00';
  st.RSTN_CFG ??= '0';
  const gsT = ctx.t('tbl_general_status');
  const gsnT = ctx.t('tbl_general_status_n');
  const gs = (k) => get(gsT, k); // tbl_general_status.get(k)
  const gsn = (k) => get(gsnT, k);
  const gsb = (bit) => gs(`0${bit}`);
  const gsnb = (bit) => gsn(`0${bit}`);
  const v = (a, b) => val.slice(a, b);
  const val0 = () => p(pj('    * Val:', val));

  switch (tag) {
    // Table 97. Core configuration parameters
    case 'A015': { // DEFAULT_POWER
      if (val === '01') p(pj('    * Val:', 'Standby State'));
      else if (val === '02') p(pj('    * Val:', 'Autonomous Mode'));
      else if (val === '03') p(pj('    * Val:', 'Autonomous Mode') + (st.ULPDET_CFG === '01' ? ' + ULPDET' : ''));
      else if (val === '05') p(pj('    * Val:', 'Autonomous Mode') + (st.ULPDET_CFG === '01' ? ' + ULPDET With Notification' : ''));
      // bug fix: Python printed nothing for other values
      else p(pj('    * Val:', 'RFU', `(${val})`));
      break;
    }
    case 'A00A': // WAIT_FOR_STABLE_SYSCLOCK
      val0();
      p(pj('      * Guard Time:', pyFloat(18.8 * int16(val)), 'μs'));
      break;
    case 'A010': { // CLKGEN
      const x = bin(v(2, 4));
      val0();
      p(pj('      * Calibration Restart on Wake-up:', gsb(x.slice(7, 8))));
      if (x.slice(7, 8) === '1') p(pj('      * Internal Cap Val:', get(TBL_CAP_VAL, int2(x.slice(4, 7)))));
      break;
    }
    case 'A011': { // RF_CLOCK_CFG
      val0();
      p(pj('      * Input clock freq:', ctx.lookup('tbl_in_clk_freq', v(0, 2)), `(${v(0, 2)})`));
      const b1 = bin(v(2, 4));
      if (b1.slice(0, 1) === '1' && v(0, 2) === '09') p('      * Reader mode: disable , * Card mode: Clock-less mode');
      else if (b1.slice(0, 1) === '1') p('      * Reader mode: NFC_CLK_XTAL1 / NFC_XTAL2 , * Card mode: Clock-less mode');
      else p('      * Reader mode: NFC_CLK_XTAL1 / NFC_XTAL2 , * Card mode: NFC_CLK_XTAL1 / NFC_XTAL2');
      if (b1.slice(2, 3) === '1') p(pj('       ~ Phone off:', 'Force XTAL'));
      p(pj('      * Initial delay before check of PLL lock:', int16(v(4, 6)), 'μs'));
      p(pj('      * Delay between check of successive check of lock bit:', int16(v(6, 8)), 'μs'));
      p(pj('      * Number of successive checks:', int16(v(8, 10))));
      break;
    }
    case 'A00E': { // PMU_CFG
      val0();
      let o = 0;
      for (const [label, n] of [['IRQ Enable', 4], ['Power Cfg', 3], ['DCDC Cfg', 5], ['TxLdo Cfg', 4], ['TxLdo Cfg2', 4],
        ['TxLdo Vddpa Cfg', 4], ['TxLdo delay', 4], ['Startup Wait', 4]]) {
        p(pj(`      * ${label}:`, v(o, o + 2 * n)));
        o += 2 * n;
      }
      break;
    }
    case 'A007': // RSTN_CFG
      st.RSTN_CFG = bin(val).slice(7, 8);
      val0();
      p(pj('    * RSTN_internal:', st.RSTN_CFG === '1' ? 'Disabled' : 'Enabled'));
      break;
    case 'A08E': // PHONE_OFF_ALLOWED
      val0();
      p(pj('      * Card Emulation in phone off:', val === '01' && st.RSTN_CFG === '1' ? 'Enabled' : 'Disabled'));
      break;
    case 'A009': // TO_BEFORE_STDBY_CFG
      val0();
      p(pj('      * Time:', pyFloat(Number(leInt(val)) / 1000), 's')); // little endian
      p('       ~ Time-out used to wait after last DH/NFCEE communication before going into standby.');
      break;
    case 'A01D': { // Lx_DEBUG_CFG
      val0();
      const o0 = bin(v(0, 2));
      const o1 = bin(v(2, 4));
      const row = (label, x) => p(pj(`      ${fmt(label, 45)}`, gsb(x)));
      row('* Modulation Detected Notification:', o0.slice(2, 3));
      row('* L1 Events:', o0.slice(3, 4));
      row('* L2 Reader Events:', o0.slice(4, 5));
      row('* Felica SystemCode:', o0.slice(5, 6));
      row('* Felica RF (all Felica CM events):', o0.slice(6, 7));
      row('* L2 Events CE:', o0.slice(7, 8));
      row('* L2 Events during RF activation ISO14443-3:', o1.slice(2, 3));
      p('       ~ [L1 Events]: {ISO14443-4, ISO18092}');
      p('       ~ [L2 Events]: Reader {ROW specific}, CE {ISO14443-3, RF Field ON/OFF}');
      break;
    }
    case 'A0FB': // HW_RESET_NTF
      val0();
      p('     ~ If set to 0x04 (and DH did not send SET_NFC_SERVICE_STATUS with 0x00),');
      p('     ~ It enables the sent of CORE_RESET_NTF on each HW reset (Power On Reset) received.');
      break;

    // Table 98. Poll Mode configuration
    case 'A064': // EMVCo_PCD_SETTINGS (bug fix: Python computed b0 + (b1*256)/1000)
      val0();
      p(pj('      * Polling delay between 2 phases:', pyFloat(le2(val, 0) / 1000), 'ms'));
      p(pj('      * Max nb of WupA/WupB when LPCD is triggered:', int16(v(4, 6))));
      break;
    case 'A044': { // POLL_PROFILE_SEL_CFG
      const b = bin(val);
      p(pj('    * Val:', b, `(${val})`));
      p(pj('      * Bit 0:', get({ 0: 'NFC FORUM profile', 1: 'EMVCo PCD profile' }, b.slice(7, 8))));
      p(pj('      * Bit 1:', get({ 0: 'Removal on Idle deactivation', 1: 'Power OFF on Idle deactivation' }, b.slice(6, 7))));
      p(pj('      * Bit 2:', get({ 0: 'Removal on discover deactivation', 1: ' Power OFF on discover deactivation' }, b.slice(5, 6))));
      p(pj('      * Bit 3:', 'RFU'));
      p(pj('      * Bit 4:', get({ 0: 'Polling Type B first', 1: 'Polling Type A first' }, b.slice(3, 4))));
      p(pj('      * Bit 5:', get({ 0: 'EMVCo PCD polling (digital)', 1: 'EMVCo PCD polling (analog)' }, b.slice(2, 3))));
      break;
    }
    case 'A05D': // FSDI_CFG
      val0();
      p(pj('      * Frame Size display in RATS / ATTRIB:', int16Str(val)));
      break;
    case 'A106': // LPCD_FPC
      val0();
      p(pj('      * Threshold val:', le2(val, 0)));
      break;
    case 'A148': // RF_PATTERN_CHK
      val0();
      p(pj('      * Short RF guard time check feature:', gsb(bin(v(0, 2)).slice(7, 8))));
      break;
    case 'A14B': // PLL_FREQ_CHECK
      val0();
      p(pj('      * RF output freq check:', gs(val) ?? 'RFU'));
      break;

    // Table 99. Listen Mode Configuration
    case 'A080': // TO_RF_OFF_CFG
      val0();
      p(pj('      * Time:', le2(val, 0), 'ms'));
      p('       ~ Time-out before restarts a Polling sequence, after it has detected a Field-OFF in Listen Mode.');
      break;
    case 'A062': // SLOW_HOST_CFG
      val0();
      if (val === '00') p('     ~ SN2x0 keeps sending the RF_FIELD_INFO_NTFs in screen Off power mode.');
      else if (val === '01') {
        p('     ~ SN2x0 stops sending the RF_FIELD_INFO_NTFs in screen Off power mode.');
        p('     ~ Unless there is a successful activation by an external reader.');
      } else p('     ~ RFU');
      break;
    case 'A085': { // RF_MISC_SETTINGS (4 octets LE)
      val0();
      const b = bin(v(6, 8)) + bin(v(4, 6)) + bin(v(2, 4)) + bin(v(0, 2));
      p(pj('      * b_val:', b));
      const row = (label, x) => p(pj(`      ${fmt(label, 42)}`, x));
      const sup = { 0: 'Not support', 1: 'Support' };
      row('* Uncomplia nt 13.5MHz readers:', gsb(b.slice(28, 29)));
      row('* SFGT Early Exchange:', gsb(b.slice(27, 28)));
      row('* PCD Block nb Check:', gsb(b.slice(25, 26)));
      row('* Mute To RATS with non ISO-DEP SAK:', gsb(b.slice(22, 23)));
      row('* Multiple Tag during collision:', gsb(b.slice(19, 20)));
      row('* NAK To RATS:', gsb(b.slice(18, 19)));
      row('* Illegal Uid 0 (Yangchengtong):', get(sup, b.slice(14, 15)));
      row('* Non Compliant Mifare Reader:', get(sup, b.slice(13, 14)));
      row('* Non Compliant Mifare Reader (Changchun):', get(sup, b.slice(1, 2)));
      break;
    }
    case 'A10E': { // GUARD_TIMEOUT_Tx2Rx
      val0();
      const t = (o) => pyFixed(le2(val, o) * (8 / 13.56), 2);
      p(pj('      * FDT 14443-A activ (Tx to Rx):', t(0), 'µs'));
      p(pj('      * FDT Mifare trans (Rx to Tx):', t(4), 'µs'));
      p(pj('      * FDT Mifare trans (Tx to Rx):', t(8), 'µs'));
      break;
    }
    case 'A095': { // NDEF_NFCEE
      val0();
      const b = bin(v(0, 2));
      const row = (label, x) => p(pj(`      ${fmt(label, 30)}`, gsb(x)));
      row('* NDEF NFCEE:', b.slice(7, 8));
      row('* FID E108 write from RF IF:', b.slice(5, 6));
      row('* FID E107 write from RF IF:', b.slice(4, 5));
      row('* FID E106 write from RF IF:', b.slice(3, 4));
      row('* FID E105 write from RF IF:', b.slice(2, 3));
      row('* FID E104 write from RF IF:', b.slice(1, 2));
      row('* Additional proprietary TLV:', b.slice(0, 1));
      break;
    }
    case 'A110': { // NDEF_NFCEE_CFG2
      val0();
      const b = bin(v(0, 2));
      const row = (label, x) => p(pj(`      ${fmt(label, 31)}`, gsb(x)));
      row('* FID E108 write from Host IF:', b.slice(5, 6));
      row('* FID E107 write from Host IF:', b.slice(4, 5));
      row('* FID E106 write from Host IF:', b.slice(3, 4));
      row('* FID E105 write from Host IF:', b.slice(2, 3));
      row('* FID E104 write from Host IF:', b.slice(1, 2));
      break;
    }
    case 'A10B': { // AUTONOMOUS_START_TIMEOUT
      val0();
      const pm = st.PWR_MODE_00 ?? '0';
      if (val === '00' && pm !== '02' && pm !== '04') p('      * Autonomous Mode: Disabled');
      else p(pj('      * Autonomous Mode:', 'starts afetr guard time', int16Str(val), 'seconds.'));
      break;
    }
    case 'A10F': { // ULPDET_CFG
      st.ULPDET_CFG = v(0, 2);
      val0();
      p(pj('      * ULPDET mode:', gs(v(0, 2))));
      if (v(0, 2) === '01') {
        const b = bin(v(2, 4));
        const g2 = { 0: 'is not used during ULPDET mode', 1: 'is high when wake up from ULPDET mode, Low when enter in Standby mode.' };
        p(pj('       ~ NFC_GPIO2_AO', get(g2, b.slice(7, 8))));
        if (b.slice(6, 7) === '1') p('       ~ NFC_GPIO2_AO is high when external RF field is ON and low when OFF, in all modes (ULPDET,LPDET).');
        if (b.slice(5, 6) === '1') p('       ~ NFC_GPIO3_AO is high when card is activated in any RF technology. Set low when NFCC enters standby.');
      }
      break;
    }
    case 'A096': case 'A111': { // NOTIFY_ALL_AID / NOTIFY_ALL_FID
      val0();
      const b = bin(val);
      p(pj(`      ${fmt('* Action Notification:', 30)}`, gsb(b.slice(3, 4))));
      p(pj(`      ${fmt('* Notification in Screen OFF:', 30)}`, gsb(b.slice(4, 5))));
      break;
    }
    case 'A086': case 'A087': { // RF_BITRATE_LIMIT_A/B_CFG
      val0();
      const b = bin(val);
      p(pj('      * Bit Rate Cfg1:', gsb(b.slice(5, 6)), gsb(b.slice(6, 7)), gsb(b.slice(7, 8))));
      p(pj('      * Bit Rate Cfg2:', gsb(b.slice(1, 2)), gsb(b.slice(2, 3)), gsb(b.slice(3, 4))));
      // bug fix: Python looked up val_b[0:1] without the '0' prefix -> always None
      p(pj('      * UICC usage:', gsb(b.slice(0, 1))));
      break;
    }
    case 'A11B': // MERGE_SAK
      val0();
      // bug fix: Python printed None for undefined values
      p(pj('      * Handle SAK merge:', get(TBL_MERGE_SAK, val) ?? 'RFU'));
      break;
    case 'A155': // RSSI_CONTINUOUS_NTF
      val0();
      p(pj('      * Byte:', gs(v(0, 2)) ?? 'RFU'));
      p(pj('      * Interval between NTFs:', int16(v(2, 4)) * 10, 'ms'));
      break;

    // Table 100. SWP configuration parameters
    case 'A0C0': case 'A0D1': // SWP_BITRATE_UICC1/2
      val0();
      p(pj('      * Req SWP baud rate:', get(TBL_SWP_BAUD, val) ?? 'RFU', 'kb/s'));
      break;
    case 'A0CB': case 'A0D3': { // SWP_TS1_HIGHV_UICC1/2 (4 octets LE)
      val0();
      const t = int16(v(0, 2)) + int16(v(2, 4)) * 256 + int16(v(4, 6)) * 65536 + int16(v(6, 8)) * 16777216;
      p(pj('      * Time-out between SIMVCC HIGH and NFC_SIM_SWIO1 HIGH:', pyFloat(t / 45 / 1000), 'ms'));
      break;
    }
    case 'A0EC': case 'A0D4': // SWP_UICC1/2_IF_EN_CFG
      val0();
      p(pj(`      * UICC${tag === 'A0EC' ? '1' : '2'} IF:`, gs(val) ?? 'RFU'));
      break;
    case 'A0F1': case 'A0F8': // SWP_UICC1/2_SPECIAL_PWR_MODE_CFG
      val0();
      p(pj(`      * UICC${tag === 'A0F1' ? '1' : '2'} Power Mode:`, get({ '00': 'Low', '01': 'Full' }, val) ?? 'RFU'));
      break;
    case 'A0C5': // SWP_UICC1_ACT_RSET_WAIT
      val0();
      p(pj('      * Delay before RSET frame:', (BigInt(int16Str(val)) * 128n).toString(), 'μs'));
      break;
    case 'A11C': { // SWP_EXT_RESUME
      val0();
      const b = bin(val);
      const t = { 0: 'Extended resume not used.', 1: 'Extended resume may be used, if also supported by UICC.' };
      p(pj('      * UICC1:', get(t, b.slice(7, 8))));
      p(pj('      * UICC2:', get(t, b.slice(6, 7))));
      break;
    }

    // Table 101. Mailbox configuration parameters
    case 'A0B8': { // SE_APDU_LOGGING_EN_CFG
      val0();
      const b = bin(val);
      p(pj('      * APDU Logging:                  ', gsb(b.slice(7, 8))));
      p(pj('      * APDU Logging during Mifare CLT:', gsnb(b.slice(5, 6))));
      break;
    }
    case 'A0ED': { // NFCEE_eSE_IF_EN_CFG
      val0();
      const t = { '00': 'Disabled', '01': 'NFCEE_eSE', '02': 'NFCEE_eUICC', '03': 'NFCEE_eSE and NFCEE_eUICC' };
      if (val === '00') p(pj('      * NFCEE_eSE IF:', 'Disabled'));
      else p(pj(`      * ${get(t, val) ?? 'RFU'} IF:`, 'Enabled'));
      break;
    }
    case 'A0F9': // SE_COLD_RESET_NTF
      val0();
      p(pj('      * eSE cold reset NTF through NFC_GPIO0 pin:', gs(val)));
      break;
    case 'A08A': // SE_POWER_ON_TO_WAKE_UP_GUARD_TIME
      val0();
      p(pj('      * Delay before waking-up the eSE:', le2(val, 0), 'µs'));
      break;
    case 'A08C': // SE_POWER_OFF_TO_SW_RESET_DELAY_TIME
      val0();
      p(pj('      * Delay before resetting the mailbox:', le2(val, 0), 'µs'));
      break;
    case 'A08D': // WAKE_UP_SE_TO_ACT_FRAME_DELAY_TIME
      val0();
      p(pj('      * Delay before sensing an ACT frame:', le2(val, 0), 'µs'));
      break;
    case 'A089': // ACT_RESPONSE_GUARD_TIME
      val0();
      p(pj('      * Max time to send ACK:', le2(val, 0), 'ms'));
      break;
    case 'A08B': case 'A082': // CLT_F_TIMEOUT / CLT_A_TIMEOUT
      val0();
      p(pj('      * Time-out to abort:', le2(val, 0), 'ms'));
      break;
    case 'A094': { // SE_TEMP_ERROR_DELAY_TIME
      val0();
      // NXP UM: 1 octet; Bit[0:3] timeout value, Bit[7] = 1 -> value in seconds, Bit[4:6] RFU
      const b = parseInt(val.slice(0, 2), 16);
      p(pj('      * Delay after TEMP_ERROR:', b & 0x0f) + (b & 0x80 ? ' s' : ' (No unit defined)'));
      if (val.length !== 2) p(`      * Warning: Len ${val.length / 2}, expected 1 (raw ${val})`);
      break;
    }
    case 'A084': // VBAT_THRESHOLD_PHONE_OFF
      val0();
      p(pj('      * VBAT threshold:', le2(val, 0), 'mV'));
      break;

    // Table 102. HCI configuration parameters
    case 'A0EF': case 'A0E8': case 'A0F0': { // RF_PARAM_CE_UICC1/UICC2/eSE
      val0();
      let o = 0;
      const take = (n) => { const s = v(o, o + 2 * n); o += 2 * n; return s; };
      p('     ~ Card Emulation for Type A ~');
      p(pj('      * Pipe Status:', get(TBL_PIP_STATUS, take(1))));
      p(pj('      * MODE parameter:', take(1)));
      const nid = int16(take(1));
      p(pj('      * UID:', take(nid)));
      p(pj('      * SAK:', take(1)));
      p(pj('      * ATQA:', take(2)));
      const app = int16(take(1));
      p(pj('      * App. Data:', take(app)));
      p(pj('      * FWI_SFGI:', take(1)));
      p(pj('      * CID support:', take(1)));
      p(pj('      * CLT support:', take(1)));
      p(pj('      * Data Rate Max:', take(3)));
      p('     ~ Card Emulation for Type B ~');
      p(pj('      * Pipe Status:', get(TBL_PIP_STATUS, take(1))));
      p(pj('      * MODE parameter:', take(1)));
      const pupi = int16(take(1));
      p(pj('      * PUPI:', take(pupi)));
      p(pj('      * AFI:', take(1)));
      p(pj('      * ATQB:', take(4)));
      const hl = int16(take(1));
      p(pj('      * Higher Layer RSP:', take(hl)));
      p(pj('      * Data Rate Max:', take(3)));
      break;
    }
    case 'A11A': { // PHONEOFF_TECH_CONFIG
      val0();
      const b = bin(val);
      p(pj('      * CE A: ', gsnb(b.slice(7, 8))));
      p(pj('      * CE B: ', gsnb(b.slice(6, 7))));
      p(pj('      * CE F: ', gsnb(b.slice(5, 6))));
      break;
    }
    case 'A022': case 'A023': case 'A024': case 'A025': case 'A0E9': case 'A012': // HCI pipe status
      val0();
      p(pj(TBL_PIPE[tag], get(TBL_PIPE_STATUS, val) ?? 'RFU'));
      break;

    // Table 103. RF transitions
    case 'A017': { // RF_CUST_PHASE_COMPENSATION (bug fix: Python parsed the LE hex as decimal)
      let x = int16(v(2, 4) + v(0, 2));
      if (x & 0x8000) x = -((x ^ 0xFFFF) + 1);
      p(pj('    * Phase:', pyFloat(x * 0.25), '°'));
      break;
    }
    case 'A068': { // RF_LPCD_CFG
      val0();
      let o = 18;
      const mode = v(o, o + 4);
      const lpcd = bin(v(o, o + 2));
      o += 2;
      if (lpcd.slice(0, 1) === '1') {
        const retry = lpcd.slice(2, 3) === '1' && lpcd.slice(4, 5) === '1';
        p(`${pj('      * LPCD:', 'Enabled')} ${retry ? pj('with retry poll', `(${mode})`) : `(${mode})`}`);
        let line = '      * Mode: ';
        const adv = bin(v(o, o + 2));
        o += 2;
        if (adv.slice(3, 4) === '1') line += 'Advanced ';
        const hybrid = v(o, o + 2);
        o += 2;
        if (hybrid === '00') p(`${line}LPCD`);
        else {
          p(`${line}Hybrid LPCD`);
          p(pj('      * Fall-back Counter:', int16(hybrid), `(${hybrid})`));
        }
        p(pj('      * Threshold coarse:', int16(v(o + 2, o + 4) + v(o, o + 2)), `(${v(o, o + 4)})`));
        o += 4 + 4 + 40;
        p(pj('      * LPCD Period:', pyFixed(le2(val, o) * 2.63, 2), 'ms'));
      } else {
        p(pj('      * LPCD:', 'Disabled', `(${mode})`));
      }
      break;
    }
    case 'A034': { // RF_DLMA_CFG
      val0();
      const ab = v(12, 204);
      const f = v(208, 400);
      p(pj('      * APC_ID_REF_AB:', int16(v(8, 10))));
      p(pj('      * NB_ENTRIES_AB:', int16(v(10, 12))));
      p('      * Type A & B RSSI threshold:');
      rssiTable(ab, p);
      p(pj('      * APC_ID_REF_F:', int16(v(204, 206))));
      p(pj('      * NB_ENTRIES_F:', int16(v(206, 208))));
      p('      * Type F RSSI threshold:');
      rssiTable(f, p);
      break;
    }
    case 'A10A': { // RF_DLMA_CLOCK_LESS_CEF_CFG
      val0();
      const f = v(4, 196);
      p(pj('      * APC_ID_REF_F:', int16(v(0, 2))));
      p(pj('      * NB_ENTRIES_F:', int16(v(2, 4))));
      p('      * Type F RSSI threshold:');
      rssiTable(f, p);
      break;
    }
    case 'A00B': { // RF_DPC_CFG
      val0();
      const b = bin(v(0, 2));
      p(pj('      * bConfig:', b));
      p(pj(`        ${fmt('* DPC in Reader:', 29)}`, gsb(b.slice(7, 8))));
      p(pj(`        ${fmt('* Overcurrent prevention:', 29)}`, gsnb(b.slice(4, 5))));
      p(pj(`        ${fmt('* GPADC threshold detection:', 29)}`, gsb(b.slice(3, 4))));
      p(pj(`        ${fmt('* Periodic Timer:', 29)}`, gsb(b.slice(2, 3))));
      let o = 2;
      p(pj('      * Target Current:', le2(val, o), 'mA'));
      o += 4;
      p(pj('      * Hysteresis:', int16(v(o, o + 2)), 'mA'));
      o += 2 + 4;
      p('     ~  #  ~  VDDPA  ~  Target I reduct  ~  MAL change  ~  ASK100 rise/fall  ~  ASK10 rise/fall  ~');
      for (let i = 0; i < 37; i++) {
        const e = v(o, o + 8);
        // bug fix: ASK100 rise = byte2 high nibble (Python reused byte1, the MAL change)
        p(`      ${fmt(i, 5, '^')} ${fmt(pyFixed(i * 0.05 + 1.5, 2), 6, '>')} V  ${fmt(int16(e.slice(0, 2)), 10, '>')} mA       `
          + `${fmt(s8(e.slice(2, 4)), 14, '^')} ${fmt(`${s4(e.slice(4, 5))} / ${s4(e.slice(5, 6))}`, 20, '^')} `
          + `${fmt(`${s4(e.slice(6, 7))} / ${s4(e.slice(7, 8))}`, 19, '^')}`);
        o += 8;
      }
      break;
    }
    case 'A00D': { // RF_TRANSITION_CFG
      val0();
      const transId = v(0, 2);
      const regAddr = v(2, 4);
      const regVal = val.slice(4);
      // bug fix: Python only handled Len 3/4/6 (UnboundLocalError otherwise) and sliced the
      // 32-bit field positions out of an 8/16-bit string. The register value is LE of any
      // length; bit fields are taken from it zero-extended to 32 bits.
      const bytes = regVal.match(/../g) || [];
      const bRegVal = bytes.slice().reverse().map((h) => bin(h)).join('');
      const b32 = bRegVal.padStart(32, '0').slice(-32);
      p(pj('      * Transition ID:', ctx.lookup('tbl_rf_trans_id', transId), `(${transId})`));
      p(pj('      * CLIF register offset:', ctx.lookup('tbl_register', regAddr), `(${regAddr})`));
      p(pj('      * Register Val:', regVal, `( ${bRegVal} )`));
      if (regAddr === '50') {
        p(pj('        * GSP_DEFAULT_TX2:', b32.slice(2, 7)));
        p(pj('        * GSP_DEFAULT_TX1:', b32.slice(7, 12)));
        p(pj('        * GSP_CM_TX2:', b32.slice(12, 17)));
        p(pj('        * GSP_CM_TX1:', b32.slice(17, 22)));
        p(pj('        * GSP_RM_TX2:', b32.slice(22, 27)));
        p(pj('        * GSP_RM_TX1:', b32.slice(27, 32)));
      } else if (regAddr === '4E' || regAddr === '4F') {
        const sym = regAddr === '4E' ? 'TX1' : 'TX2';
        p(pj(`        * GSN_DEFAULT_${sym}:`, b32.slice(7, 12)));
        p(pj(`        * GSN_MOD_CM_${sym}:`, b32.slice(12, 17)));
        p(pj(`        * GSN_CW_CM_${sym}:`, b32.slice(17, 22)));
        p(pj(`        * GSN_MOD_RM_${sym}:`, b32.slice(22, 27)));
        p(pj(`        * GSN_CW_RM_${sym}:`, b32.slice(27, 32)));
      } else if (regAddr === 'AB') {
        const b0 = bytes[0] ?? '00';
        const b1 = bytes[1] ?? '00';
        p(pj('        * TX1_SS_TARGET_SCALE:', int16(b0), `( ${b0} )`));
        p(pj('        * TX2_SS_TARGET_SCALE:', int16(b1), `( ${b1} )`));
      } else if (regAddr === '32') {
        p(pj('        * TX_UNDERSHOOT_PATTERN:', b32.slice(0, 16)));
        p(pj('        * TX_EXTENDED_TRANSMISSION:', b32.slice(24, 26)));
        p(pj('        * TX_UNDERSHOOT_PATTERN_LEN:', b32.slice(27, 31)));
        p(pj('        * TX_UNDERSHOOT_PROT_ENABLE:', gsb(b32.slice(31, 32))));
      } else if (regAddr === '40') {
        p(pj('        * DGRM_RSSI_TARGET:', b32.slice(15, 25)));
        p(pj('        * DGRM_SIGNAL_DETECT_TH_OVR_VAL:', b32.slice(25, 32)));
      }
      void valLen;
      break;
    }
    case 'A09E': { // RX_CTRL_CFG
      val0();
      const b = bin(v(0, 2));
      p(pj('      * Config:', b));
      p(pj('        * Rx improvements for GreenCar:', gsb(b.slice(5, 6))));
      p(pj('        * Clock-less CeB field strength RSSI conversion:', gsb(b.slice(4, 5))));
      p(pj('      * Ref Interpolated RSSI measured at 8 A/m:', pyFixed(le2(val, 2) / 2048, 2), 'mV'));
      p(pj('      * LPDET:', le2(val, 6), 'mA/m'));
      p(pj('      * NFCLD ON:', le2(val, 10), 'mA/m'));
      p(pj('      * NFCLD ON/OFF ratio:', int16(v(14, 16)), '%'));
      p(pj('      * Green Car threshold:', le2(val, 16), 'mA/m'));
      p(pj('      * Clock-less CeB:', le2(val, 20), 'mA/m'));
      break;
    }
    case 'A17E': { // ADVANCED_HYBRID_LPCD_CFG
      val0();
      const b = bin(v(0, 2)) + bin(v(2, 4));
      p(pj('      * Config:', b));
      p(pj('        * POLL_TYPE_A:          ', gsb(b.slice(15, 16))));
      p(pj('        * POLL_TYPE_B:          ', gsb(b.slice(14, 15))));
      p(pj('        * POLL_TYPE_F:          ', gsb(b.slice(13, 14))));
      p(pj('        * POLL_TYPE_V:          ', gsb(b.slice(12, 13))));
      p(pj('        * Advanced Hybrid LPCD: ', gsb(b.slice(0, 1))));
      break;
    }
    case 'A12E': // FDT_CONFIG
      val0();
      p(pj('      * Tx BitPhase Ext Clock:  ', v(0, 2)));
      p(pj('      * Tx BitPhase Clock-less: ', v(2, 4)));
      p(pj('      * Tx BitPhase Bpsk Delay: ', v(4, 6)));
      p('       ~ A variation of +1 in the register means a shift of +1/13.56Mhz s on the FDT time');
      break;

    // SN220 RF Register Setting Guidelines / AN13076
    case 'A06A': { // RF_CLK_PLL_DPLL3
      val0();
      const four = (s) => [0, 4, 8, 12].map((o) => `${pyFixed(le2(s, o) / 4, 2)} °`);
      const sx = four(v(0, 16));
      const cl = four(v(16, 32));
      p('     ~ Sys / Xtal clk:');
      p(pj('      * RF ON:', sx[0], ' * A:', sx[1], ' * B:', sx[2], ' * F:', sx[3]));
      p('     ~ Clock-less:');
      p(pj('      * RF ON:', cl[0], ' * A:', cl[1], ' * B:', cl[2], ' * F:', cl[3]));
      break;
    }
    case 'A0A4': { // HFatt. Phase Correction
      val0();
      let o = 10;
      p('     ~  HFatt_code  ~  Val  ~  Hex  ~');
      for (let i = 0; i < 64; i++) {
        const h = v(o + 2, o + 4) + v(o, o + 2);
        p(`         ${fmt(i, 9, '^')}  ${fmt(pyFixed(int16(h) * 0.125, 3), 6, '>')}  ${fmt(h, 8, '^')}`);
        o += 4;
      }
      break;
    }
    case 'A0AF': { // DLMA_CTRL (2.7 Card Mode Cfg)
      val0();
      const cfgAb = v(0, 2);
      const refAb = v(6, 8);
      const cfgF = v(8, 10);
      // bug fix: Ref VDDPA F is octet 7 of the F block (Python reused octet 3 = AB)
      const refF = v(14, 16);
      const bAb = bin(cfgAb);
      const bF = bin(cfgF);
      if (cfgAb.slice(1, 2) === '0' && cfgF.slice(1, 2) === '0') {
        p(pj('      * DLMA:', 'Disabled'));
        const ab = pj('      * Ref. VDDPA AB:           ', pyFloat(1.5 + int16(refAb) * 0.05), 'V');
        p(refF ? pj(ab, '      * Ref. VDDPA F:           ', pyFloat(1.5 + int16(refF) * 0.05), 'V') : ab);
      } else {
        p(pj('      * DLMA:', 'Enable'));
        const row = (la, lf, i) => p(pj(la, fmt(ps(gsb(bAb.slice(i, i + 1))), 11), lf, fmt(ps(gsb(bF.slice(i, i + 1))), 11)));
        row('      * APC TX AB:               ', '* APC TX F:               ', 7);
        row('      * BPSK AB (m3):            ', '* BPSK F (m3):            ', 6);
        row('      * Single Driver AB (m1):   ', '* Single Driver F (m1):   ', 5);
        row('      * APC Arbitrary Phase AB:  ', '* APC Arbitrary Phase F:  ', 4);
      }
      const rssi = { 0: 'Raw', 1: 'Interpolated' };
      p(`      ${fmt('* APC AB uses RSSI:', 20)}${fmt(ps(get(rssi, bAb.slice(3, 4))), 20, '^')}`
        + `${fmt('* APC F uses RSSI:', 19)}${fmt(ps(get(rssi, bF.slice(3, 4))), 20, '^')}`);
      break;
    }
    case 'A0A7': { // RM_GLOBAL_TX_SHAPING
      val0();
      p(pj('      * GSN_MOD_RM:', bin(v(8, 10)).slice(3)));
      p(pj('      * GSN_CW_RM:', bin(v(10, 12)).slice(3)));
      p(pj('      * GSP_RM:', bin(v(12, 14)).slice(3)));
      p(pj('      * TX_SS_TARGET_SCALE:', int16(v(16, 18))));
      p(pj('      * TX_PH_SHIFT_DIV10:', `${int16(v(18, 20)) * 9} °`));
      p(pj('      * TX_PH_SHIFT_MOD10:', `${pyFixed(int16(v(20, 22)) * 0.9, 1)} °`));
      break;
    }
    case 'A0A8': { // RM_TECHNO_TX_SHAPING
      val0();
      const a = v(0, 32);
      const b = v(32, 64);
      const f = v(64, 80);
      const tv = v(80, 128);
      const tc = (s, o) => s.slice(o, o + 2);
      const edge = (name, s, o) => pj(`      * ${name}, Time const cfg of falling / rising edge:`, tc(s, o));
      const resid = (name, s, o) => pj(`      * ${name}, RESIDUAL carrier:`, tc(s, o));
      p('     ~ Type A ~');
      p(edge('A106', a, 4));
      p(edge('A212', a, 12));
      p(edge('A424', a, 20));
      p(edge('A848', a, 28));
      p('     ~ Type B ~');
      p(edge('B106', b, 4) + resid('B106', b, 0));
      p(edge('B212', b, 12) + resid('B212', b, 8));
      p(edge('B424', b, 20) + resid('B424', b, 16));
      p(edge('B848', b, 28) + resid('B848', b, 24));
      p('     ~ Type F ~');
      p(edge('F212', f, 4) + resid('F212', f, 0));
      p(edge('F424', f, 12) + resid('F424', f, 8));
      p('     ~ Type V ~');
      p(edge('V100_26', tv, 4));
      p(edge('V10_26', tv, 12) + resid('V10_26', tv, 8));
      p(edge('V100_53', tv, 20));
      p(edge('V10_53', tv, 28) + resid('V10_53', tv, 24));
      p(edge('V100_106', tv, 36));
      p(edge('V100_212', tv, 44));
      break;
    }
    case 'A098': // MEASURED_LMA_RSSI
      val0();
      p(pj('      * Measured LMA phone ON:', int16(v(0, 2)), 'mV'));
      p(pj('      * Measured RSSI:', le2(val, 2)));
      p(pj('      * Ref. field strength:', int16(v(6, 7)), 'A/m')); // NXP UM: byte3 Bit[4:7]
      p(pj('      * Ref. VDDPA DLMA OFF:', pyFloat(1.5 + int16(v(8, 10)) * 0.05), 'V'));
      p(pj('      * Measured LMA Type A clock-less mode:', int16(v(10, 12)), 'mV'));
      p(pj('      * Measured LMA Type B clock-less mode:', int16(v(12, 14)), 'mV'));
      p(pj('      * Measured LMA Type F clock-less mode:', int16(v(14, 16)), 'mV'));
      break;
    case 'A0AB': // RSSI_GAIN
      val0();
      for (let i = 1; i < 65; i++) {
        const s = v(i * 4, i * 4 + 4);
        p(pj(`      * HFatt code ${fmt(i - 1, 2, '>')}:`, fmt(le2(s, 0), 5, '>'), 'set', `(${s})`));
      }
      break;
    case 'A0A9': { // DLMA_TX
      val0();
      let pre = '0';
      p('     ~  Entry  ~  ID  ~  Equiv TX (Vpp)  ~  VDDPA (V)  ~  TxScaling  ~  Mode 3  ~  DriNum  ~  NCIcmd  ~');
      for (let i = 0; i < Math.trunc(valLen / 3); i++) {
        const e = v(i * 6, i * 6 + 6);
        if (e === pre) continue;
        const vddpa = int16(e.slice(2, 4)) * 0.05 + 1.5;
        const txs = int16(e.slice(4, 6));
        const n0 = bin(e.slice(0, 1), 4);
        const mode3 = int2(n0.slice(1, 2));
        const dv = 2 - int2(n0.slice(0, 1));
        const id = int2(bin(e.slice(0, 2)).slice(2));
        p(`          ${fmt(i, 2, '>')}      ${fmt(id, 2, '>')}        ${fmt(pyFixed(vddpa * (txs / 255) * dv * (1 + mode3), 2), 5, '>')}`
          + `            ${fmt(pyFixed(vddpa, 2), 4, '>')}            ${fmt(txs, 3, '>')}           ${mode3}          ${dv}       ${e}`);
        pre = e;
      }
      break;
    }
    default:
      val0();
  }
}

function rssiTable(s, p) {
  for (let i = 0; i < 24; i++) {
    const e = s.slice(i * 8, i * 8 + 8);
    p(pj(`        * No.${fmt(i, 2, '>')}:`, fmt(le2(e, 0), 5, '>'), `(${e.slice(0, 4)})`));
  }
}

// ---------------------------------------------------------------- shared param walker

const isExt = (id) => id === 'A0' || id === 'A1';

/** read one "ID/Register, Len, Val" parameter (SET_CONFIG_CMD / GET_CONFIG_RSP) */
function configParam(r, out, ctx, i) {
  out.blank();
  out.line(`   ~ [Param_${i}] ~  `);
  let start = r.abs;
  const id = r.peekHex(1);
  let key;
  if (isExt(id)) {
    key = r.hex(2, 'Register');
    out.line(pj('    * Register:', ctx.lookup('tbl_cfg_para', key), `(${key})`), { start, end: r.abs, table: 'tbl_cfg_para' });
  } else {
    key = r.hex(1, 'ID');
    out.line(pj('    * ID:', ctx.lookup('tbl_cfg_para', key), `(${key})`), { start, end: r.abs, table: 'tbl_cfg_para' });
  }
  start = r.abs;
  const m = r.u8('Len');
  out.line(pj('    * Len:', m), { start, end: r.abs });
  if (m !== 0) {
    const vs = r.abs;
    const val = r.hex(m, 'Val');
    const meta = { start: vs, end: r.abs };
    const p = (text) => out.line(text, meta);
    if (isExt(id)) VALUE_OF_REGISTER(key, val, m, p, ctx);
    else VALUE_OF_CFG_PARA(key, val, p, ctx);
  }
}

// ---------------------------------------------------------------- handlers

const handlers = {
  ...forum,

  // 60 00
  CORE_RESET_NTF(r, out, ctx) {
    const trig = out.enumField(r, 1, 'Reset Trigger', 'tbl_rst_trig');
    out.enumField(r, 1, 'Config Status', 'tbl_cfg_status');
    if (trig === 'A0') {
      out.hexField(r, 1, 'dw Assertion Program Counter', 4);
      return;
    }
    out.enumField(r, 1, 'NCI Version', 'tbl_nci_ver');
    const start = r.abs;
    const mfg = r.hex(1, 'Manufacturer ID');
    out.line(mfg === '00' ? '  * Manufacturer ID: Info is not available.' : `  * Manufacturer ID: ${mfg}`, { start, end: r.abs });
    // Manufacturer Specific Info: named fields from the first 5 octets, extra octets as hex;
    // shorter info printed whole
    const n = r.done ? 0 : r.u8('Manufacturer Specific Information Length');
    if (n >= 5) {
      out.hexField(r, 1, 'Model ID');
      out.hexField(r, 1, 'Hw Ver nb');
      out.hexField(r, 1, 'ROM Code Ver nb');
      out.hexField(r, 1, 'FLASH Ver', 2);
      if (n > 5) out.hexField(r, 1, 'Manufacturer Specific Info (extra)', n - 5);
    } else if (n > 0) {
      out.hexField(r, 1, 'Manufacturer Specific Info', n);
    }
  },

  // 20 02
  CORE_SET_CONFIG_CMD(r, out, ctx) {
    const start = r.abs;
    const n = r.u8('Number of Parameters');
    out.kv(1, 'Number of Params', n, { start, end: r.abs });
    for (let i = 0; i < n; i++) configParam(r, out, ctx, i);
  },

  // 40 02 -- bug fix: Python delegated to forum (1-octet IDs only), splitting A0xx/A1xx in two
  CORE_SET_CONFIG_RSP(r, out, ctx) {
    out.enumField(r, 1, 'Status', 'tbl_status_codes');
    const start = r.abs;
    const n = r.u8('Number of Parameters');
    out.kv(1, 'Number of Params', n, { start, end: r.abs });
    if (n !== 0) {
      out.line('  * Set Param ID:');
      for (let i = 0; i < n; i++) {
        const s = r.abs;
        const id = r.hex(isExt(r.peekHex(1)) ? 2 : 1, 'Parameter ID');
        out.line(`    * ID ${i}: ${ctx.lookup('tbl_cfg_para', id)} (${id})`, { start: s, end: r.abs, table: 'tbl_cfg_para' });
      }
    }
  },

  // 20 03
  CORE_GET_CONFIG_CMD(r, out, ctx) {
    const start = r.abs;
    const n = r.u8('Number of Parameters');
    out.kv(1, 'Number of Params', n, { start, end: r.abs });
    out.line('  * Get Param ID:');
    for (let i = 0; i < n; i++) {
      const s = r.abs;
      if (isExt(r.peekHex(1))) {
        const reg = r.hex(2, 'Register');
        out.line(`    * Register: ${ctx.lookup('tbl_cfg_para', reg)} (${reg})`, { start: s, end: r.abs, table: 'tbl_cfg_para' });
      } else {
        const id = r.hex(1, 'Parameter ID');
        out.line(`    * ID ${i}: ${ctx.lookup('tbl_cfg_para', id)} (${id})`, { start: s, end: r.abs, table: 'tbl_cfg_para' });
      }
    }
  },

  // 40 03
  CORE_GET_CONFIG_RSP(r, out, ctx) {
    out.enumField(r, 1, 'Status', 'tbl_status_codes');
    const start = r.abs;
    const n = r.u8('Number of Parameters');
    out.kv(1, 'Number of Params', n, { start, end: r.abs });
    for (let i = 0; i < n; i++) configParam(r, out, ctx, i);
  },

  // 40 04
  CORE_CONN_CREATE_RSP(r, out, ctx) {
    const status = out.enumField(r, 1, 'Status', 'tbl_status_codes');
    if (status !== '00') return;
    let start = r.abs;
    out.kv(1, 'Max Data Packet Payload Size', r.u8('Max Data Packet Payload Size'), { start, end: r.abs });
    start = r.abs;
    const cr = r.hex(1, 'Initial Number of Credits');
    const credits = ctx.t('tbl_init_credits');
    out.kv(1, 'Initial Number of Credits', Object.prototype.hasOwnProperty.call(credits, cr) ? credits[cr] : parseInt(cr, 16),
      { start, end: r.abs, table: 'tbl_init_credits' });
    start = r.abs;
    const conn = r.u8('Conn ID');
    const meaning = ctx.lookup('tbl_conn_id', (conn & 0x0f).toString(2).padStart(4, '0'), 'Dynamically assigned by the NFCC');
    // Conn ID is the low 4 bits only (upper bits RFU)
    out.kv(1, 'Conn ID', `${conn & 0x0f} (${meaning})`, { start, end: r.abs, table: 'tbl_conn_id' });
  },
};

export default handlers;
