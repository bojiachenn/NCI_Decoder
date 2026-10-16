// Byte-oriented cursor over a hex payload. Python handlers walk `p_payload` in hex
// chars (2 per byte); here everything is in bytes and reading past the end throws
// instead of silently yielding '' (which made Python raise int('', 16) later).

export class DecodeError extends Error {
  constructor(message) {
    super(message);
    this.name = 'DecodeError';
  }
}

export class Reader {
  /**
   * @param {string} hex  uppercase hex string without spaces
   * @param {number} base absolute byte offset of hex[0] inside the packet (for highlighting)
   */
  constructor(hex, base = 0) {
    this.data = hex.toUpperCase();
    this.base = base;
    this.pos = 0; // bytes consumed
  }

  get length() { return this.data.length / 2; }
  get remaining() { return this.length - this.pos; }
  get done() { return this.remaining <= 0; }
  /** absolute byte offset in the packet of the next unread byte */
  get abs() { return this.base + this.pos; }

  need(n, what = 'field') {
    if (n < 0 || this.remaining < n) {
      throw new DecodeError(`Payload too short: need ${n} byte(s) for ${what}, ${Math.max(this.remaining, 0)} left`);
    }
  }

  /** read n bytes as uppercase hex */
  hex(n = 1, what) {
    this.need(n, what);
    const s = this.data.slice(this.pos * 2, (this.pos + n) * 2);
    this.pos += n;
    return s;
  }

  peekHex(n = 1) { return this.data.slice(this.pos * 2, (this.pos + n) * 2); }
  u8(what) { return parseInt(this.hex(1, what), 16); }
  u16be(what) { return parseInt(this.hex(2, what), 16); }
  u16le(what) { const h = this.hex(2, what); return parseInt(h.slice(2, 4) + h.slice(0, 2), 16); }
  /** n bytes, little-endian integer */
  uintLE(n, what) { return parseInt(reverseBytes(this.hex(n, what)), 16); }
  uintBE(n, what) { return parseInt(this.hex(n, what), 16); }
  skip(n, what) { this.hex(n, what); }
  /** consume everything left */
  rest() { return this.hex(this.remaining); }

  /** sub-reader over the next n bytes (consumes them from this reader) */
  sub(n, what) {
    const start = this.abs;
    return new Reader(this.hex(n, what), start);
  }
}

export function reverseBytes(hex) {
  return (hex.match(/../g) || []).reverse().join('');
}

export const hexToBin = (hex, bits = hex.length * 4) => parseInt(hex, 16).toString(2).padStart(bits, '0');
export const toHex = (n, bytes = 1) => n.toString(16).toUpperCase().padStart(bytes * 2, '0');
