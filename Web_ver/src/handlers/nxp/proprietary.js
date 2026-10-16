// Port of Nxp_pkg/Proprietary.py (GID 0xF Proprietary, SN2x0 additional commands).
// Conventions: see web/PORTING.md. Python module globals live in ctx.state with the
// same names: PWR_MODE_00 (read by the NXP NCI Core port), TEST_ID_3F, DPC_TYPE, AST_LOOP.
//
// Bug fixes vs Python (see tests/known_diffs/nxp_prop.json):
//   * COLD_RESET_CMD called the dict tbl_general_status_n -> TypeError; now looked up.
//   * TEST_PRBS_CMD had no `return p_payload` -> TypeError in Decoder_Main; now consumes 6 bytes.
//   * L1_DEBUG_NTF compared the remaining *hex-char* count with byte counts 3/4/5/6.
//   * RF_SPC_NTF phase parsed with int() base 10; now base 16 (little-endian, signed).
//   * READ_TXLDO_CURRENT (AST_LOOP '01') and AST_UTILITY VDDPA parsed bytes as decimal.
// (All of the above are now fixed in Python too.)
// Round-2 fixes (Python + JS): L2_DEBUG_NTF CMA data no longer capped at 9/8 bytes,
// APDU_LOGGING_NTF unknown Category prints the rest as APDU Data, RF_GET_TRANSITION_RSP
// shows the little-endian value, DPC_HELPER_RSP Current uses the full byte 1.

// NOTE AST_LOOP: nothing sets AST_LOOP (Python neither), so it stays '00' and the
// READ_TXLDO_CURRENT ('01') / READ_RSSI ('02') branches of OID 0x32 are currently
// unreachable. The NXP UM is needed to determine the switch condition.

const DEFAULTS = { PWR_MODE_00: '0', TEST_ID_3F: '32', DPC_TYPE: '02', AST_LOOP: '00' };
function st(ctx, key) {
  ctx.state[key] ??= DEFAULTS[key];
  return ctx.state[key];
}

// Python str() of a float
export const pyFloat = (n) => (Number.isInteger(n) ? `${n}.0` : String(n));

/** Python '{:.Nf}'.format(x): like toFixed, but exact ties round half-to-even */
export function pyFixed(x, digits) {
  const s = x.toFixed(digits);
  const exact = Math.abs(x).toFixed(Math.min(100, digits + 40));
  const tail = exact.slice(exact.indexOf('.') + 1 + digits);
  if (/^50*$/.test(tail)) {
    // tie: toFixed rounded away from zero; Python rounds to even
    const down = (Math.trunc(Math.abs(x) * 10 ** digits) / 10 ** digits);
    const lastDigit = Math.trunc(Math.abs(x) * 10 ** digits) % 10;
    if (lastDigit % 2 === 0) return (x < 0 ? '-' : '') + down.toFixed(digits);
  }
  return s;
}

const pad = (s, w, align) => {
  s = String(s);
  const n = w - s.length;
  if (n <= 0) return s;
  if (align === '>') return ' '.repeat(n) + s;
  if (align === '<') return s + ' '.repeat(n);
  const l = Math.floor(n / 2);
  return ' '.repeat(l) + s + ' '.repeat(n - l);
};

const EMPTY = pad('(Empty)', 25, '^');
// Python only advances p_payload here (no read, no bounds check)
const adv = (r, n) => { r.pos += n; };
const bin8 = (hex) => parseInt(hex, 16).toString(2).padStart(8, '0');

function statusLine(r, out, ctx, allowed, other = 'Forbidden', label = 'Status') {
  const start = r.abs;
  const v = r.hex(1, label);
  const text = !allowed || allowed.includes(v) ? ctx.lookup('tbl_status_codes', v) : other;
  out.kv(1, label, text, { start, end: r.abs, table: 'tbl_status_codes' });
  return v;
}

function mapField(r, out, level, label, map, fallback = 'RFU', n = 1) {
  const start = r.abs;
  const v = r.hex(n, label);
  out.kv(level, label, Object.prototype.hasOwnProperty.call(map, v) ? map[v] : fallback, { start, end: r.abs });
  return v;
}

const empty = (r, out) => { out.line(EMPTY); };

const PWR_MODE = {
  '00': 'Standby State disabled',
  '01': 'Standby State enabled',
  '02': 'Autonomous Mode enabled',
  '03': 'ULPDET State enabled',
  '04': 'Autonomous Mode enabled with Poll',
  '05': 'ULPDET enabled with NCI notifications',
};

// L1_DEBUG_NTF local tables
const L1_TECH_MODE = {
  0: 'Not detected yet', 1: 'Card Emulation NFC-A', 2: 'Card Emulation NFC-B', 3: 'Card Emulation NFC-F',
  8: 'Reader mode NFC-A', 9: 'Reader mode NFC-B', A: 'Reader mode NFC-F', F: 'Reader mode NFC-V',
};
const L1_TTC_1 = {
  1: 'ACTIVATED', 2: 'DATA_RX', 3: 'RX_DESELECT', 4: 'RX_WTX', 5: 'ERROR', 6: 'RX_ACK', 7: 'RX_NAK',
  8: 'DATA_TX', A: 'TX_DESELECT', B: 'TX_WTX', C: 'TX_ACK', D: 'TX_NAK', E: 'EXTENDED',
};
const L1_TTC_2 = { 1: 'ACTIVATED', 2: 'DATA_RX', 3: 'RX_READ', 4: 'RX_WRITE', 5: 'ERROR', 6: 'DATA_TX', 7: 'TX_READ', 8: 'TX_WRITE' };
const L1_TTC_3 = { 2: 'DATA_RX', 8: 'DATA_TX' };

// L2_DEBUG_NTF local tables
const L2_TAG = { 1: 'L2 EVENT', 2: 'FELICA CMD', 3: 'FELICA SYSTEM CODE', 4: 'FELICA RSP', 5: 'MISC', A: 'CMA' };
const L2_TECH_MODE = {
  1: 'Card Emulation NFC-A', 2: 'Card Emulation NFC-B', 3: 'Card Emulation NFC-F',
  8: 'Reader mode NFC-A', 9: 'Reader mode NFC-B', A: 'Reader mode NFC-F', F: 'Reader mode NFC-V',
};
const L2_TTC_1 = {
  1: 'MODULATION_DETECTED', 2: 'DATA_RX', 3: 'TIMEOUT/RSSI', 4: 'ACTIVE_ISO14443_3', 5: 'ERROR', 6: 'SENSING',
  7: 'ACTIVE_ISO14443_4', 8: 'RF_ON', 9: 'RF_OFF', A: 'DATA_TX', C: 'LPCD_WUP',
};
const L2_TTC_2 = { 1: 'SLPV_REQ', 2: 'INVENTORY_RESP', 6: 'INVENTORY_REQ_1_SLOT', 7: 'ACTIVATION', A: 'INVENTORY_REQ_16_SLOT' };
const L2_MISC_EVENT = {
  '01': 'GENERIC ERROR', '02': 'FELICA CM: EMPTY FRAME FROM ESE', '03': 'L2 NTF BUFFER OVERFLOW', '05': 'FELICA CM: RF ERROR',
};
const L2_TT_CMA = {
  '03': 'CLT_CMD', '04': 'CLT_DATA_RX', '05': 'CLT_DATA_TX', '06': 'RATS_RECEIVED', '07': 'ATQA_SENT',
  '08': 'UID_SENT', '0A': 'ATS_SENT', '0B': 'HLTA_DETECTED', '0C': 'ERROR', '0D': 'EMD_DETECTED',
};
const get = (map, k, fb = 'RFU') => (Object.prototype.hasOwnProperty.call(map, k) ? map[k] : fb);

function timeLine(r, out) {
  const start = r.abs;
  const major = r.u16le('Major_Time_Stamp');
  const minor = r.u16le('Minor_Time_Stamp');
  out.line(`  * Time: ${major} ms ${minor} µs`, { start, end: r.abs });
}

function hexLine(r, out, text, n, suffix = '') {
  const start = r.abs;
  const v = r.hex(n, text);
  out.line(`${text} ${v}${suffix}`, { start, end: r.abs });
  return v;
}

/** CLIF State + Tech & Mode + Trigger Type (shared by L1/L2, tables differ) */
function clifState(r, out, techTbl, ttc) {
  const start = r.abs;
  const cs = r.hex(1, 'CLIF State');
  const meta = { start, end: r.abs };
  out.line(`  * CLIF State: ${cs}`, meta);
  out.line(`    * Tech & Mode: ${get(techTbl, cs[0])}`, meta);
  const t = ttc(cs[0]);
  if (cs[0] !== '0' && cs[0] !== '3' && t) out.line(`    * Trigger Type: ${get(t, cs[1])}`, meta);
}

const handlers = {
  // 2F 00
  CORE_SET_POWER_MODE_CMD(r, out, ctx) {
    ctx.state.PWR_MODE_00 = r.peekHex(1);
    mapField(r, out, 1, 'Mode', PWR_MODE);
  },
  // 4F 00
  CORE_SET_POWER_MODE_RSP(r, out, ctx) { statusLine(r, out, ctx); },

  // 2F 01
  SET_NFC_SERVICE_STATUS_CMD(r, out) {
    mapField(r, out, 1, 'Mode', { '00': 'NFC service OFF', '01': 'NFC service ON' });
  },
  // 4F 01
  SET_NFC_SERVICE_STATUS_RSP(r, out, ctx) { statusLine(r, out, ctx); },

  // 2F 02
  NCI_PROPRIETARY_ACT_CMD: empty,
  // 4F 02
  NCI_PROPRIETARY_ACT_RSP(r, out, ctx) {
    statusLine(r, out, ctx, ['00', '03']);
    out.hexField(r, 1, 'FW_Build_Nb', 4);
  },

  // 6F 04
  APDU_LOGGING_NTF(r, out) {
    let start = r.abs;
    const op = r.hex(1, 'Logging Opcode');
    out.line(`  * Logging Opcode: ${op}${op !== '60' ? ' (Should be 0x60)' : ''}`, { start, end: r.abs });
    adv(r, 1, 'RFU Length'); // Do not Care
    start = r.abs;
    const step = r.u16be('Timestamp'); // 1 step = 16 µs
    out.line(`  * Timestamp: ${pyFloat((step * 16) / 1000)} ms`, { start, end: r.abs });
    start = r.abs;
    const cat = r.hex(1, 'Category');
    const CAT = { '0B': 'C-APDU from eSE', '1B': 'R-APDU from eSE', '2B': 'C-APDU from UICCx', '3B': 'R-APDU from UICCx' };
    out.line(`  * Category: ${CAT[cat] ?? `Error ${cat}`}`, { start, end: r.abs });
    if (cat === '0B' || cat === '2B') hexLine(r, out, '  * APDU Data:', 5, ' (First 5 bytes of the C-APDU)');
    else if (cat === '1B' || cat === '3B') hexLine(r, out, '  * APDU Data:', 2, ' (Last 2 bytes of the R-APDU)');
    else hexLine(r, out, '  * APDU Data:', r.remaining); // unknown Category: show whatever is left
  },

  // 2F 14
  RF_GET_TRANSITION_CMD(r, out) {
    out.enumField(r, 1, 'RF Transition ID', 'tbl_rf_trans_id');
    out.hexField(r, 1, 'CLIF Register Offset');
  },
  // 4F 14
  RF_GET_TRANSITION_RSP(r, out, ctx) {
    statusLine(r, out, ctx, ['00', '01', '06']);
    const start = r.abs;
    const l = r.u8('RF Transition Len');
    out.kv(1, 'RF Transition Len', l, { start, end: r.abs });
    const s = r.abs;
    const val = r.hex(l, 'RF Transition Val');
    const le = (val.match(/../g) || []).reverse().join(''); // Little Endian
    out.kv(1, 'RF Transition Val', `0x${le} (raw ${val})`, { start: s, end: r.abs });
  },

  // 6F 17
  WTX_NTF: empty,

  // 2F 1C
  LOW_POWER_TAG_REMOVAL_CMD: empty,
  // 4F 1C
  LOW_POWER_TAG_REMOVAL_RSP(r, out, ctx) { statusLine(r, out, ctx, ['00', '01', '09']); },
  // 6F 1C
  LOW_POWER_TAG_REMOVAL_NTF: empty,

  // 2F 1E
  SYSTEM_ESE_POWER_CYCLE_CMD: empty,
  // 4F 1E
  SYSTEM_ESE_POWER_CYCLE_RSP(r, out, ctx) { statusLine(r, out, ctx, ['00', '01', '09']); },

  // 2F 1F  (Python: tbl_general_status_n(rst_pin) -> TypeError, fixed to a lookup)
  COLD_RESET_CMD(r, out, ctx) {
    const start = r.abs;
    const v = r.hex(1, 'RESET by pin');
    out.kv(1, 'RESET by pin', `SE reset ${ctx.lookup('tbl_general_status_n', v)}`, { start, end: r.abs, table: 'tbl_general_status_n' });
  },
  // 4F 1F
  COLD_RESET_RSP(r, out, ctx) { statusLine(r, out, ctx); },
  // 6F 1F
  COLD_RESET_NTF(r, out) {
    const start = r.abs;
    const v = r.hex(1, 'Status');
    out.kv(1, 'Status', v === '00' ? 'successfully done' : 'at least one internal verification failed', { start, end: r.abs });
  },

  // 2F 21
  FLUSH_SRAM_AO_TO_FLASH_CMD: empty,
  // 4F 21
  FLUSH_SRAM_AO_TO_FLASH_RSP(r, out, ctx) { statusLine(r, out, ctx, ['00', '01', '09', '06']); },

  // 2F 30  (Python forgot `return p_payload` -> crashed after printing everything)
  TEST_PRBS_CMD(r, out, ctx) {
    mapField(r, out, 1, 'PRBS Mode', { '00': 'Firmware generated PRBS', '01': 'Firmware generated PRBS' });
    mapField(r, out, 1, 'PRBS Type', {
      '00': 'PRBS9 when Hardware generated PRBS selected',
      '01': 'PRBS15 when Hardware generated PRBS selected',
    }, 'Ignored when Firmware generated PRBS is selected');
    mapField(r, out, 1, 'Technology to stream', { '00': 'Type A', '01': 'Type B', '02': 'Type F', '03': 'Type V' });
    const start = r.abs;
    const br = r.hex(1, 'Bitrate');
    let text = 'RFU';
    if (['00', '01', '02', '03'].includes(br)) text = ctx.lookup('tbl_bit_rates', br);
    else if (br === '04') text = '26 Kbit/s';
    out.kv(1, 'Bitrate', text, { start, end: r.abs, table: 'tbl_bit_rates' });
    out.hexField(r, 1, 'PRBS series length', 2);
  },
  // 4F 30
  TEST_PRBS_RSP(r, out, ctx) { statusLine(r, out, ctx, ['00', '05', '06', '09'], 'RFU'); },

  // 2F 32
  // AST_LOOP is never set (see NOTE at the top): the '01'/'02' branches are unreachable for now.
  READ_OPTION_CMD(r, out, ctx) {
    const loop = st(ctx, 'AST_LOOP');
    if (loop === '01' || loop === '02') {
      out.line(loop === '01' ? '  << READ_TXLDO_CURRENT_CMD >>  ' : '  << READ_RSSI_CMD >>  ');
      let start = r.abs;
      const id = r.hex(1, 'Test ID');
      out.kv(1, 'Test ID', `${loop === '01' ? 'Read TxLdo current' : 'Read RSSI Command'} (${id})`, { start, end: r.abs });
      start = r.abs;
      const wt = r.u8('Wait_Time');
      out.kv(1, 'Wait_Time', `${wt} µs`, { start, end: r.abs });
    } else if (loop === '00') {
      out.line('  << RF_TEST_API_CMD >>  ');
      mapField(r, out, 1, 'HW Regi', { '08': 'GPADC_SENSOR_TXLDO_CURRENT', '0C': 'GPADC_SENSOR_RSSI', '0D': 'GPADC_SENSOR_VDDPA' });
    }
  },
  // 4F 32
  // AST_LOOP is never set (see NOTE at the top): the '01'/'02' branches are unreachable for now.
  READ_OPTION_RSP(r, out, ctx) {
    const loop = st(ctx, 'AST_LOOP');
    if (loop === '01') {
      out.line('  << READ_TXLDO_CURRENT_RSP >>  ');
      statusLine(r, out, ctx);
      // Python: int(byte0) + int(byte1) * 256 (decimal parse of hex) -> fixed to hex LE
      const start = r.abs;
      const cur = r.u16le('TXLDO_CURRENT');
      out.kv(1, 'TXLDO_CURRENT', `${cur} mA`, { start, end: r.abs });
    } else if (loop === '02') {
      out.line('  << READ_RSSI_RSP >>  ');
      statusLine(r, out, ctx);
      adv(r, 2);
      out.hexField(r, 1, 'RSSI_VALUE', 4);
      out.hexField(r, 1, 'Interpolated RSSI', 4);
    } else if (loop === '00') {
      out.line('  << RF_TEST_API_RSP >>  ');
      statusLine(r, out, ctx);
      out.hexField(r, 1, 'HW Regi Val', 2);
    }
  },

  // 2F 33
  TEST_PRBS_CARD_CMD(r, out, ctx) {
    const mode = mapField(r, out, 1, 'PRBS Mode', { '00': 'Start PRBS Card Mode', '01': 'Stop PRBS Card Mode' });
    if (mode !== '00') return;
    const TECH = { '00': 'Type A', '01': 'Type B', 10: 'Type F' };
    const BITRATE = { '00': '106k', '01': '212k', 10: '424k', 11: '848k' };
    const start = r.abs;
    const tt = r.hex(1, 'Test Type');
    const meta = { start, end: r.abs };
    const b = bin8(tt);
    out.line(`  * Test Type: ${b} (${tt})`, meta);
    const gs = ctx.t('tbl_general_status');
    const sysClk = gs[`0${b[2]}`];
    const clkLess = gs[`0${b[3]}`];
    out.line(`   ~ ${pad('Sys clk platform:', 20, '<')} ${sysClk}`, { ...meta, table: 'tbl_general_status' });
    out.line(`   ~ ${pad('Clk-less platform:', 20, '<')} ${clkLess}`, { ...meta, table: 'tbl_general_status' });
    out.line(`   ~ ${pad('Technology:', 20, '<')} ${get(TECH, b.slice(4, 6), 'None')}`, meta);
    out.line(`   ~ ${pad('Bit Rate:', 20, '<')} ${get(BITRATE, b.slice(6, 8), 'None')}`, meta);
    if (clkLess === 'Enabled ') out.hexField(r, 1, 'Pseudo random pattern');
    if (sysClk === 'Enabled ') {
      const s = r.abs;
      const fp = r.hex(16, 'Fixed Pattern');
      out.line(`  Fixed Pattern: ${fp.match(/../g).map((p) => `0x${p}`).join(' ')}`, { start: s, end: r.abs });
    }
  },
  // 4F 33
  TEST_PRBS_CARD_RSP(r, out, ctx) { statusLine(r, out, ctx); },

  // 6F 35  (Python compared the remaining hex-char count with byte counts; fixed)
  L1_DEBUG_NTF(r, out) {
    timeLine(r, out);
    const valLen = r.remaining;
    if (valLen === 3 || valLen === 4) hexLine(r, out, '  * RSSI:', 2, ' (MSB)'); // non-TX event
    else if (valLen === 5 || valLen === 6) hexLine(r, out, '  * DLMA:', 4, ' (LSB)'); // TX event
    clifState(r, out, L1_TECH_MODE, (t) => {
      if ('1289'.includes(t)) return L1_TTC_1;
      if (t === 'A') return L1_TTC_2;
      if (t === 'F') return L1_TTC_3;
      return null;
    });
    if (valLen === 4 || valLen === 6) out.hexField(r, 1, 'Extra Debug data');
  },

  // 6F 36
  L2_DEBUG_NTF(r, out) {
    let start = r.abs;
    const tl = r.hex(1, 'Tag/Length');
    const tag = tl[0];
    const length = parseInt(tl[1], 16);
    out.line(`  * Tag: ${get(L2_TAG, tag)}`, { start, end: r.abs });
    timeLine(r, out);
    const extra = () => out.hexField(r, 1, 'Extra data info');

    if (tag === '1') { // L2 event
      if (length === 7 || length === 8) hexLine(r, out, '  * RSSI:', 2, ' (MSB)');
      else if (length === 9 || length === 10) hexLine(r, out, '  * DLMA:', 4, ' (LSB)');
      clifState(r, out, L2_TECH_MODE, (t) => ('1289A'.includes(t) ? L2_TTC_1 : t === 'F' ? L2_TTC_2 : null));
      if (length === 8 || length === 10) extra();
    } else if (tag === '2') { // FELICA CMD
      hexLine(r, out, '  * RSSI:', 2, ' (MSB)');
      out.hexField(r, 1, 'FeliCa CMD');
      if (length === 8) extra();
    } else if (tag === '3') { // FELICA SYSTEM CODE
      out.hexField(r, 1, 'FeliCa CMD', 2);
    } else if (tag === '4') { // FELICA RSP
      hexLine(r, out, '  * DLMA:', 4, ' (LSB)');
      out.hexField(r, 1, 'FeliCa RSP');
      out.hexField(r, 1, 'RSP status flag', 2);
      if (length === 12) extra();
    } else if (tag === '5') { // MISC
      mapField(r, out, 1, 'Misc Event trig', L2_MISC_EVENT);
      if (length === 6) extra();
    } else if (tag === 'A') { // CMA
      const trig = mapField(r, out, 1, 'Trig type', L2_TT_CMA);
      if (length > 5) {
        out.line(`  * Extra data info: ${r.peekHex(r.remaining)}`, { start: r.abs, end: r.abs + r.remaining });
        // data runs up to the end of the Tag's data (no 9/8-byte cap)
        const capped = (label) => {
          start = r.abs;
          let n = r.u8(label);
          n = Math.min(n, r.remaining);
          const d = r.hex(n, label);
          out.line(`    * ${label}: ${d}`, { start, end: r.abs });
        };
        if (trig === '03') {
          start = r.abs;
          const t = r.hex(1, 'Type');
          if (t === '08') out.line('    * Type: CLT_IDLE (08)', { start, end: r.abs });
          else if (t === '09') out.line('    * Type: CLT_HALT (09)', { start, end: r.abs });
        } else if (trig === '04') {
          capped('CLT RX Data');
        } else if (trig === '05') {
          capped('CLT TX Data');
        } else if (trig === '06') {
          out.hexField(r, 2, 'RATS received', 2);
        } else if (trig === '07') {
          start = r.abs;
          const t = r.hex(1, 'Type');
          if (t === '26') out.line('    * Type: REQA (26)', { start, end: r.abs });
          else if (t === '52') out.line('    * Type: WUPA (52)', { start, end: r.abs });
          out.hexField(r, 2, 'ATQA sent', 2);
        } else if (trig === '08') {
          out.hexField(r, 2, 'Anti-Collision Lv');
        } else if (trig === '0A') {
          out.hexField(r, 2, 'APC', 4);
          out.hexField(r, 2, 'ATS sent', 5);
        } else if (trig === '0B') {
          out.hexField(r, 2, 'HLTA received', 2);
        } else if (trig === '0C') {
          start = r.abs;
          let n = r.u16le('Data received');
          n = Math.min(n, r.remaining);
          const d = r.hex(n, 'Data received');
          out.line(`    * Data received: ${d}`, { start, end: r.abs });
        }
      }
    }
  },

  // 2F 3D
  RF_SPC_CMD(r, out) {
    const cfg = mapField(r, out, 1, 'SPC Cfg', { 30: 'Configure NFCC for SPC', 31: 'Start SPC algorithm' });
    if (cfg === '30') {
      const blk = out.hexField(r, 1, 'Block Nb');
      out.hexField(r, 1, blk === '00' ? 'Algo settings' : 'PLL settings', r.remaining);
    }
  },
  // 4F 3D
  RF_SPC_RSP(r, out, ctx) { statusLine(r, out, ctx); },
  // 6F 3D  (Python parsed the phase with int() base 10; fixed to base 16)
  RF_SPC_NTF(r, out) {
    mapField(r, out, 1, 'Status', {
      '00': 'SPC_STATUS_OK (OK, phase offset updated)',
      '01': 'SPC_STATUS_RX_PROTECTION (NOK)',
      '02': 'SPC_STATUS_OVERCURRENT (NOK)',
      '04': 'SPC_STATUS_OVERCURRENT_DISCARD (OK, phase offset updated)',
      '08': 'SPC_STATUS_RSSITHRESH_DISCARD',
      F0: 'RFU',
    }, 'None');
    for (const label of ['IndexStart', 'IndexEnd']) {
      const start = r.abs;
      const v = r.hex(1, label);
      out.kv(1, label, `${parseInt(v, 16)} (${v})`, { start, end: r.abs });
    }
    let start = r.abs;
    out.kv(1, 'RSSI', r.u16le('RSSI'), { start, end: r.abs });
    start = r.abs;
    let phase = r.u16le('CustomerPhaseTrim');
    if (phase & 0x8000) phase = -((phase ^ 0xffff) + 1);
    out.kv(1, 'Phase', `${pyFloat(phase * 0.25)} °`, { start, end: r.abs });
  },

  // 2F 3E
  TEST_SWP_CMD(r, out) {
    mapField(r, out, 1, 'Link ID', { '00': 'NFC_SIM_SWIO1 (UICC1)', '01': 'Mailbox (eSE)', '02': 'NFC_SIM_SWIO2 (UICC2)' }, 'Forbidden');
  },
  // 4F 3E
  TEST_SWP_RSP(r, out, ctx) { statusLine(r, out, ctx, ['00', '05']); },
  // 6F 3E
  TEST_SWP_NTF(r, out, ctx) {
    statusLine(r, out, ctx, ['00', '03']);
    mapField(r, out, 1, 'Power Mode', { '00': 'No SIMVCC', '01': 'SIMVCC = 1.8V', '02': 'SIMVCC = 3.3V', '03': 'SIMVCC undetermined' });
  },

  // 2F 3F
  OPTIONAL_CMD(r, out, ctx) {
    const id = r.peekHex(1);
    ctx.state.TEST_ID_3F = id;
    if (id === '70') {
      out.line('  << AST_UTILITY_CMD >>  ');
      let start = r.abs;
      adv(r, 1);
      out.kv(1, 'Param 1', 'Antenna Self-Test utility APIs', { start, end: r.abs });
      start = r.abs;
      ctx.state.DPC_TYPE = r.peekHex(1);
      mapField(r, out, 1, 'Param 2', { '02': 'FORCE_DPC_OFF_CMD', '01': 'FORCE_NEW_VDDPA_CMD', '00': 'READ_VDDPA_CODE_CMD' });
      out.hexField(r, 1, 'Input');
    } else if (id === '04' || id === '05') {
      out.line(id === '04' ? '  << DPC_HELPER_ACT_CMD >>  ' : '  << DPC_HELPER_CMD >>  ');
      const start = r.abs;
      adv(r, 3);
      out.kv(1, 'Test ID', id === '04' ? 'ENABLE DPC HELPER' : 'READ DPC HELPER DATA', { start, end: r.abs });
    } else if (id === '32') {
      out.line('  << SWITCH_RF_FIELD_CMD >>  ');
      const start = r.abs;
      adv(r, 1);
      out.kv(1, 'Test ID', 'Switch RF Field On/Off', { start, end: r.abs });
      mapField(r, out, 1, 'Field Type', { '00': 'Field Off', '01': 'Field On AST1', '02': 'Field On AST2' });
      adv(r, 1); // Reserved
    }
  },
  // 4F 3F
  OPTIONAL_RSP(r, out, ctx) {
    const id = st(ctx, 'TEST_ID_3F');
    if (id === '70') {
      out.line('  << AST_UTILITY_RSP >>  ');
      const dpc = st(ctx, 'DPC_TYPE');
      if (dpc === '02' || dpc === '01') {
        statusLine(r, out, ctx);
      } else if (dpc === '00') {
        // Python: int(code) base 10 -> fixed to base 16
        const start = r.abs;
        const code = r.u8('VDDPA');
        out.kv(1, 'VDDPA', `${pyFloat(1.5 + code * 0.05)} V`, { start, end: r.abs });
      } else {
        adv(r, 1);
      }
    } else if (id === '04') {
      out.line('  << DPC_HELPER_ACT_RSP >>  ');
      const start = r.abs;
      adv(r, 3);
      out.kv(1, 'Test ID', 'ENABLE DPC HELPER', { start, end: r.abs });
    } else if (id === '05') {
      out.line('  << DPC_HELPER_RSP >>  ');
      statusLine(r, out, ctx);
      adv(r, 1); // (0F) purpose unknown
      const info = r.peekHex(r.remaining);
      out.line(`  * DPC Info: ${info}`, { start: r.abs, end: r.abs + r.remaining });
      out.line('   ~  #  ~  Power  ~  VDDPA  ~  Current  ~  NCI cmd  ~');
      const x = Math.floor(info.length / 12);
      for (let i = 0; i < x; i++) {
        const start = r.abs;
        const e = r.hex(6, 'DPC Info');
        const vddpa = parseInt(e.slice(4, 6), 16) * 0.05 + 1.5;
        // 12-bit current: byte1 high nibble is flags/RFU (NXP UM)
        const current = parseInt(e.slice(0, 2), 16) + (parseInt(e.slice(2, 4), 16) & 0x0f) * 256;
        out.line(`    ${pad(i, 5, '^')} ${pad(pyFixed((vddpa * current) / 1000, 3), 6, '>')} W  `
          + `${pad(pyFixed(vddpa, 2), 6, '>')} V  ${pad(current, 6, '>')} mA   ${pad(e.slice(0, 6), 9, '>')}`, { start, end: r.abs });
      }
    } else if (id === '32') {
      out.line('  << SWITCH_RF_FIELD_RSP >>  ');
      statusLine(r, out, ctx);
    }
  },
};

export default handlers;
