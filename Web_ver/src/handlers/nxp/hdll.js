// Port of Nxp_pkg/HDLL.py + the HDLL() frame function / "HDLL" op-code table in
// Nxp_pkg/__ctrl__.py (NXP Host Data Link Layer, download/bootloader framing).
//
// Frame: | b0: --C LLLLL | b1: len[7:0] | op code | payload (len-1) | CRC16 (BE) |
// decoder.js prints the title "Nxp HDLL: <name>" and "#end"; frame() prints the rest.
// Python global HDLL_CMD (op code of the previous frame, initially '00') -> ctx.state.HDLL_CMD.
//
// Bug fixes vs Python (see tests/known_diffs/nxp_hdll.json):
//   * chunk bit was compared with '01' (one-char string) -> "* Chunk:" never printed.
//   * unknown op code raised KeyError -> now an error line.
//   * CRC was only echoed -> additionally verified (CRC-16-CCITT-FALSE); a mismatch adds a line.
//   * handlers reading past the payload (e.g. DL_OK after E0 with a 3-byte payload raised
//     ValueError) -> "Error: Payload too short ..." line, CRC still printed.
// The first three are now fixed in Python too. Round-2 fixes (Python + JS): unknown Session
// State -> "RFU (xx)"; DL_OK after DL_CHECK_INTEGRITY also prints code-only section rows.
import { Reader, DecodeError } from '../../core/reader.js';

const pyFloat = (n) => (Number.isInteger(n) ? `${n}.0` : String(n));
const rpad = (s, w) => String(s).padStart(w, ' ');
// Python only advances p_payload here (no read, no bounds check)
const adv = (r, n) => { r.pos += n; };
const bin8 = (hex) => parseInt(hex, 16).toString(2).padStart(8, '0');

/** CRC-16/CCITT-FALSE: poly 0x1021, init 0xFFFF, no reflection, xorout 0 */
export function crc16CcittFalse(hex) {
  let crc = 0xffff;
  for (let i = 0; i < hex.length; i += 2) {
    crc ^= parseInt(hex.slice(i, i + 2), 16) << 8;
    for (let b = 0; b < 8; b++) crc = crc & 0x8000 ? ((crc << 1) ^ 0x1021) & 0xffff : (crc << 1) & 0xffff;
  }
  return crc.toString(16).toUpperCase().padStart(4, '0');
}

// ---- op-code handlers: (r, out, len, preOp) ---------------------------------

const cmd = (name) => (r, out) => {
  out.line(`  * HDLL CMD: ${name}`);
  adv(r, 3); // empty
};
const rspEmpty = (r) => { adv(r, 3); };

function hexLine(r, out, label, n) {
  const start = r.abs;
  const v = r.hex(n, label);
  out.line(`  * ${label}: ${v}`, { start, end: r.abs });
  return v;
}

const ops = {
  // CMD
  DL_RESET: cmd('DL_RESET'),
  DL_GET_VERSION: cmd('DL_GET_VERSION'),
  DL_GET_SESSION_STATE: cmd('DL_GET_SESSION_STATE'),
  DL_GET_DIE_ID: cmd('DL_GET_DIE_ID'),
  DL_CHECK_INTEGRITY: cmd('DL_CHECK_INTEGRITY'),

  DL_SEC_WRITE(r, out, len) {
    out.line('  * HDLL CMD: DL_SEC_WRITE');
    if (len === 502) { // first
      adv(r, 1);
      for (const [label, n] of [['FW version', 2], ['NONCE', 16], ['DIEID', 16], ['CHIPMASK', 2],
        ['MASKEDKEY', 16], ['UDFSEED', 32], ['HASH', 32], ['SIGN', 384]]) hexLine(r, out, label, n);
    } else { // Middle & Last
      const size = r.u16be('Data size');
      hexLine(r, out, 'ADDR', 3);
      hexLine(r, out, 'DATA', size);
      if (len - 1 > r.pos) hexLine(r, out, 'HASH', 32); // Middle
    }
  },

  DL_CERT_FRAME(r, out) {
    out.line('  * HDLL CMD: DL_CERT_FRAME');
    adv(r, 1);
    for (const [label, n] of [['Chip version', 2], ['Chip Life Cycle', 2], ['Certificate version', 2],
      ['PK_MOD', 384], ['PK_EXP', 8], ['PK_CRC', 4], ['SIGN', 384]]) hexLine(r, out, label, n);
  },

  // RSP
  DL_OK(r, out, len, preOp) {
    out.line('  * HDLL RSP: DL_STATUS_OK');
    if (preOp === 'F1') {
      for (const [label, n] of [['HW version', 1], ['ROM code', 1], ['Model ID', 1], ['FW version', 2],
        ['Internal FW build revision', 4], ['Chip version', 2], ['Chip Life Cycle', 2],
        ['Certificate version', 2]]) hexLine(r, out, label, n);
    } else if (preOp === 'F2') {
      const start = r.abs;
      const s = r.peekHex(1);
      adv(r, 3);
      out.line(`  * Session State: ${{ '00': 'closed', '01': 'open', '02': 'locked' }[s] ?? `RFU (${s})`}`, { start, end: r.abs });
    } else if (preOp === 'F4') {
      adv(r, 3);
      hexLine(r, out, 'DIEID', 16);
    } else if (preOp === 'E0') {
      let start = r.abs;
      const dataNum = r.u8('Nb of data sections');
      const codeNum = r.u8('Nb of code sections');
      adv(r, 1);
      const chk = r.hex(4, 'CRC check status').match(/../g); // little-endian: byte 3 = sections 1..8
      const meta = { start, end: r.abs };
      out.line(`  * CRC check for sections  1 to  8: ${chk[3]}`, meta);
      out.line(`  *                         9 to 16: ${chk[2]}`, meta);
      out.line(`  *                        17 to 24: ${chk[1]}`, meta);
      out.line(`  *                        25 to 32: ${chk[0]}`, meta);
      const bits = bin8(chk[3]) + bin8(chk[2]) + bin8(chk[1]) + bin8(chk[0]);
      start = r.abs;
      const data = r.hex(4 * 28, 'Data sections'); // up to 28 Data sections
      const code = r.hex(4 * 4, 'Code sections');
      const status = (b) => ({ 1: 'OK', 0: 'KO' }[b] ?? '');
      const le = (s, i) => `(${s.slice(8 * i + 6, 8 * i + 8)}${s.slice(8 * i + 4, 8 * i + 6)}${s.slice(8 * i + 2, 8 * i + 4)}${s.slice(8 * i, 8 * i + 2)})`;
      out.line('  * Flash integrity:', { start, end: r.abs });
      out.line(`         Data: ${rpad(dataNum, 2)}               Code: ${rpad(codeNum, 2)}`);
      for (let i = 0; i < Math.min(Math.max(dataNum, codeNum), 28); i++) {
        const sec = { start: start + 4 * i, end: start + 4 * i + 4 };
        if (i < dataNum && i < codeNum) {
          out.line(`    ${rpad(i + 1, 2)}   ${rpad(status(bits.slice(i, i + 1)), 2)} ${le(data, i)}          `
            + `${rpad(status(bits.slice(i + 28, i + 29)), 2)} ${le(code, i)}`, sec);
        } else if (i < dataNum) {
          out.line(`    ${rpad(i + 1, 2)}   ${rpad(status(bits.slice(i, i + 1)), 2)} ${le(data, i)}`, sec);
        } else { // code section only
          out.line(`    ${rpad(i + 1, 2)}   ${''.padEnd(13)}          `
            + `${rpad(status(bits.slice(i + 28, i + 29)), 2)} ${le(code, i)}`, sec);
        }
      }
    } else {
      adv(r, 3); // empty
    }
  },
  EDL_INVALID_ADDR: rspEmpty,
  EDL_GENERIC_ERROR: rspEmpty,
  EDL_UNKNOW_CMD: rspEmpty,
  EDL_ABORTED_CMD: rspEmpty,
  EDL_ADDR_RANGE_OFL_ERROR: rspEmpty,
  EDL_BUFFER_OFL_ERROR: rspEmpty,
  EDL_MEM_BSY: rspEmpty,
  EDL_SIGNATURE_ERROR: rspEmpty,
  EDL_FIRMWARE_VERSION_ERROR: rspEmpty,
  EDL_PROTOCOL_ERROR: rspEmpty,
  PH_STATUS_DL_FIRST_CHUNK: rspEmpty,
  PH_STATUS_DL_NEXT_CHUNK: rspEmpty,
  PH_STATUS_EDL_CERT_ERROR: rspEmpty,
};

// __ctrl__.py tbl_nci_ctrl["HDLL"]
export const OP_CODES = {
  // CMD
  F0: 'DL_RESET',
  F1: 'DL_GET_VERSION',
  F2: 'DL_GET_SESSION_STATE',
  F4: 'DL_GET_DIE_ID',
  E0: 'DL_CHECK_INTEGRITY',
  C0: 'DL_SEC_WRITE',
  C1: 'DL_CERT_FRAME',
  // RSP
  '00': 'DL_OK',
  '01': 'EDL_INVALID_ADDR',
  '02': 'EDL_GENERIC_ERROR',
  '0B': 'EDL_UNKNOW_CMD',
  '0C': 'EDL_ABORTED_CMD',
  '1E': 'EDL_ADDR_RANGE_OFL_ERROR',
  '1F': 'EDL_BUFFER_OFL_ERROR',
  20: 'EDL_MEM_BSY',
  21: 'EDL_SIGNATURE_ERROR',
  24: 'EDL_FIRMWARE_VERSION_ERROR',
  28: 'EDL_PROTOCOL_ERROR',
  '2D': 'PH_STATUS_DL_FIRST_CHUNK',
  '2E': 'PH_STATUS_DL_NEXT_CHUNK',
  31: 'PH_STATUS_EDL_CERT_ERROR',
};

/**
 * Decode one HDLL frame (port of __ctrl__.HDLL()).
 * @param {string} raw full uppercase hex incl. 2-byte header and CRC
 * @returns {string} op-code function name (title is "Nxp HDLL: <name>")
 */
function frame(raw, out, ctx) {
  ctx.state.HDLL_CMD ??= '00';
  const total = raw.length / 2;
  const b0 = parseInt(raw.slice(0, 2), 16);
  const chunk = (b0 >> 5) & 1;
  const frameLen = ((b0 & 0x1f) << 8) | parseInt(raw.slice(2, 4), 16);
  const op = raw.slice(4, 6);
  const msg = raw.slice(6, 6 + 2 * (frameLen - 1));
  const name = Object.prototype.hasOwnProperty.call(OP_CODES, op) ? OP_CODES[op] : null;

  if (chunk === 1) out.line('  * Chunk: 1', { start: 0, end: 1 });

  const r = new Reader(msg, 3);
  let handlerError = false;
  if (!name) {
    out.error(`Error: unknown HDLL op code ${op}, raw: ${raw}`);
    handlerError = true;
  } else {
    try {
      ops[name](r, out, frameLen, ctx.state.HDLL_CMD);
    } catch (e) {
      if (!(e instanceof DecodeError)) throw e;
      out.error(`Error: ${e.message}`);
      handlerError = true;
    }
  }
  ctx.state.HDLL_CMD = op;

  const crcPos = 4 + 2 * frameLen; // Python: hdll_payload after msg
  const crc = raw.slice(crcPos, crcPos + 4);
  const crcMeta = { start: crcPos / 2, end: crcPos / 2 + 2 };
  out.line(`  * CRC: ${crc} (CRC-16-CCITT-FALSE)`, crcMeta);
  const calc = crc16CcittFalse(raw.slice(0, crcPos));
  if (calc !== crc) out.line(`    ! CRC mismatch: calculated ${calc}`, { ...crcMeta, level: 'warn' });

  if (!handlerError && (crcPos + 4 !== raw.length || r.pos !== frameLen - 1)) {
    out.blank();
    out.error('Error: Payload error!!');
    out.error(`  check: ${r.pos} Octet(s)`);
    out.error(`  Packet Len: ${pyFloat(total)} Octet(s)`);
    out.error(`  Frame Len: ${frameLen} Octet(s)`);
  }
  return name || `UNKNOWN (${op})`;
}

export default { frame, ...ops };
