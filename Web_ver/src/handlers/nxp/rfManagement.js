// Port of Nxp_pkg/RF_Management.py (GID 0x1 RF Management, NXP SN2x0).
// Standard OIDs delegate to the forum handlers (Python: Origin.X(raw, "nxp")); the
// forum code reads tables through ctx, which is the NXP table set here.
// NXP-specific: "No Support" stubs for OID 0C/0D/0E/0F/11 and the SN2x0 extension NTFs.
import forum from '../forum20/rfManagement.js';

const NO_SUPPORT = '[NCI] control message No Support';
// Python '{0:^25}'.format("(Empty)")
const EMPTY = `${' '.repeat(9)}(Empty)${' '.repeat(9)}`;

// Python stubs print "No Support" and return 0 without reading the payload, so a
// non-empty payload ends in "Payload error!!" (kept: the decoder prints it).
const noSupport = (r, out) => { out.line(NO_SUPPORT); };
const empty = (r, out) => { out.line(EMPTY); };

const handlers = {
  ...forum,

  // 21 0C / 41 0C
  RF_INTF_EXT_START_CMD: noSupport,
  RF_INTF_EXT_START_RSP: noSupport,
  // 21 0D / 41 0D
  RF_INTF_EXT_STOP_CMD: noSupport,
  RF_INTF_EXT_STOP_RSP: noSupport,
  // 21 0E / 41 0E
  RF_EXT_AGG_ABORT_CMD: noSupport,
  RF_EXT_AGG_ABORT_RSP: noSupport,
  // 21 0F / 41 0F
  RF_NDEF_ABORT_CMD: noSupport,
  RF_NDEF_ABORT_RSP: noSupport,
  // 21 11 / 41 11
  RF_SET_FORCED_NFCEE_ROUTING_CMD: noSupport,
  RF_SET_FORCED_NFCEE_ROUTING_RSP: noSupport,

  // 41 10 -- Python calls Origin.X(raw) without "nxp" (forum status table). Bug:
  // delegating with ctx = NXP tables resolves NXP status codes (e.g. E3) correctly.
  // (inherited from forum via the spread above)

  // 61 18
  IOT_RETRY_NTF(r, out) {
    const start = r.abs;
    const v = r.u8('WupCounter');
    out.line(`  * WupCounter: ${v}`, { start, end: r.abs });
  },

  // 61 20
  FIELD_DETECT_NTF(r, out) {
    let start = r.abs;
    const detect = r.hex(1, 'Detection');
    const d = parseInt(detect, 16);
    out.line(`  * Detection: ${d.toString(2).padStart(8, '0')} (${detect})`, { start, end: r.abs });
    out.line('   ~ Bit0 = RFU');
    out.line('   ~ Bit1 = WupA/ReqA detected');
    out.line('   ~ Bit2 = WupB/ReqB detected');
    out.line('   ~ Bit3 = PollReq (typeF) detected');
    out.line('   ~ Bit6 = RFU');
    out.line('   ~ Bit7 = RX error detected');
    r.skip(1, 'RFU');
    start = r.abs;
    // Bug fixes vs Python: it tested detect_b[3:4] (= bit4) instead of bit3, and
    // did not advance past System Code (always "Payload error!!", Check Len 2.0).
    const sc = r.hex(2, 'System Code');
    const label = (d & 0x08) ? 'POLL_REQ SC0-SC1' : 'System Code';
    out.line(`  * ${label}: ${sc}`, { start, end: r.abs });
  },

  // 61 21
  PLL_UNLOCKED_NTF: empty,
  // 61 23
  TxLDO_ERROR_NTF: empty,
  // 61 28
  PLL_LOSTLOCK_NTF: empty,

  // 61 29
  SETTINGS_CHANGE_NTF(r, out) {
    out.hexField(r, 1, 'Index');
  },

  // 61 2A
  RF_FREQ_ERROR_NTF: empty,
  // 61 2B
  LPDET_ERROR_NTF: empty,
};

export default handlers;
