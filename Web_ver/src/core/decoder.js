// Port of nci_decoder/Decoder_Main.py NFC_NCI_DECODER: header parsing + dispatch.
// Returns a structured result; render/text.js turns it back into CLI-identical text.
import { Reader, DecodeError } from './reader.js';
import { Out } from './out.js';
import { findHandler, GID_DOC_FILE } from './registry.js';

export const MT_NAMES = { 0: 'DATA', 1: 'CMD', 2: 'RSP', 3: 'NTF' };
// Table 139
export const GID_NAMES = {
  0x0: 'NCI Core',
  0x1: 'RF Management',
  0x2: 'NFCEE Management',
  0x3: 'NFCC Management',
  0x4: 'Test Management',
  0xF: 'Proprietary',
};

/** mode_2 input normalisation: drop "0x", commas, whitespace; uppercase */
export function normalizeHex(input) {
  return String(input).replace(/0x/gi, '').replace(/[,\s]/g, '').toUpperCase();
}

const pyFloat = (n) => (Number.isInteger(n) ? `${n}.0` : String(n));

/**
 * Decode one packet.
 * @param {string} hexInput raw packet hex (spaces allowed)
 * @param {object} ctx      from createContext()
 * @param {number} mode     1 = file mode (title line echoes raw), 2 = single-hex mode
 */
export function decodePacket(hexInput, ctx, mode = 2) {
  const raw = normalizeHex(hexInput);
  const out = new Out(ctx);
  const res = { raw, kind: 'UNKNOWN', title: null, mode, lines: out.lines, pbf: false, end: true };

  if (!/^[0-9A-F]*$/.test(raw) || raw.length % 2 !== 0) {
    res.end = false;
    out.error('Error: NCI raw data invalid (not an even-length hex string)');
    return res;
  }
  const len = raw.length / 2;
  if (len < 3) {
    res.end = false;
    out.error('Error: Unknown raw data!');
    return res;
  }

  const b0 = parseInt(raw.slice(0, 2), 16);
  const b1 = parseInt(raw.slice(2, 4), 16);
  const mt = b0 >> 5;
  const pbf = (b0 >> 4) & 1;
  const payloadLen = parseInt(raw.slice(4, 6), 16);
  res.mt = MT_NAMES[mt] || 'RFU';

  if (payloadLen === len - 3) {
    res.pbf = pbf === 1;
    if (res.mt === 'DATA' && (b1 >> 2) === 0) {
      decodeData(raw, b0, b1, payloadLen, res, out);
      return res;
    }
    // Control packet
    const gid = b0 & 0x0f;
    const oid = raw.slice(2, 4);
    const gidName = GID_NAMES[gid];
    Object.assign(res, { kind: 'CTRL', gid, gidName, oid });
    const h = gidName ? findHandler(ctx.vendor, gidName, oid, res.mt) : null;
    if (!h) {
      res.title = 'ERROR_NOT_FOUND';
      out.error(`Error: control code not found (GID ${gidName || gid.toString(16).toUpperCase()} / OID ${oid} / ${res.mt}) for ${ctx.vendor.label}, please check the documentation.`);
      if (gidName === 'Proprietary' && ctx.vendor.key !== 'nxp') {
        out.error('  (Proprietary 指令是廠商自訂格式，目前只支援 NXP；其他廠商（例如 ST）的專屬指令尚未實作)');
      }
      return res;
    }
    res.title = h.name;
    res.name = h.name;
    res.doc = h.doc;
    if (!h.fn) {
      out.error(`Error: ${h.name} is not implemented in the web decoder yet.`);
      return res;
    }
    const r = new Reader(raw.slice(6), 3);
    try {
      h.fn(r, out, ctx);
    } catch (e) {
      out.error(`Error: ${e instanceof DecodeError ? e.message : `${e.name}: ${e.message}`}`);
      res.exception = e;
      return res;
    }
    if (r.pos !== payloadLen) {
      out.error('Error: Payload error!!');
      out.error(`  Packet Len: ${len} Octet(s)`);
      out.error(`  Payload Len: ${payloadLen} Octet(s)`);
      out.error(`  Check Len: ${pyFloat(r.pos)} Octet(s)`);
      res.payloadError = true;
    }
    return res;
  }

  // NXP Host Data Link Layer: 2-byte header (13-bit frame length) + CRC16
  const frameLen = ((b0 & 0x1f) << 8) | b1;
  if (frameLen === len - 4) {
    Object.assign(res, { kind: 'HDLL', mt: 'HDLL', gidName: 'HDLL', pbf: false });
    const hdll = ctx.vendor.handlers.HDLL;
    if (!hdll || !hdll.frame) {
      res.title = 'HDLL';
      out.error(`Error: HDLL frames are only decoded with the NXP vendor (current: ${ctx.vendor.label}).`);
      return res;
    }
    try {
      const name = hdll.frame(raw, out, ctx);
      res.name = name;
      res.title = `Nxp HDLL: ${name}`;
      if (Object.values(ctx.vendor.ctrl.HDLL || {}).includes(name)) {
        res.doc = { dir: ctx.vendor.docDir, file: GID_DOC_FILE.HDLL, anchor: String(name).toLowerCase() };
      }
    } catch (e) {
      res.title = res.title || 'Nxp HDLL';
      out.error(`Error: ${e instanceof DecodeError ? e.message : `${e.name}: ${e.message}`}`);
      res.exception = e;
    }
    return res;
  }

  res.end = false;
  out.error('Error: Unknown raw data!');
  return res;
}

function decodeData(raw, b0, b1, payloadLen, res, out) {
  const connId = b0 & 0x0f;
  const cr = b1 & 0x03;
  Object.assign(res, { kind: 'DATA', title: 'NCI: DATA Packet', connId });
  const connText = connId === 0 ? '(Static: DH -- Remote NFC Endpoint)'
    : connId === 1 ? '(Static: DH -- HCI Network)' : '(Dynamically assigned)';
  out.line(`  * Conn ID: ${connId} ${connText}`, { start: 0, end: 1 });
  out.line(`  * Credits: ${cr}`, { start: 1, end: 2 });
  out.line(`  * Payload Length: ${payloadLen}`, { start: 2, end: 3 });
  out.line(`  * data: ${raw.slice(6)}`, { start: 3, end: 3 + payloadLen });
}
