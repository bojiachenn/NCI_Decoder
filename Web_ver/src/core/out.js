// Output collector. Each line is the exact text the Python CLI would print
// (so render/text.js stays byte-for-byte comparable with the golden corpus) plus
// metadata used by the HTML renderer:
//   start/end : absolute byte range in the packet the line describes (hover highlight)
//   table     : tbl_* name used to resolve the value (link into docs Tables.md)
//   doc       : {dir, file, anchor} explicit docs link
//   level     : 'error' | 'warn' for styling
import { lookup } from './lookup.js';

export class Out {
  constructor(ctx) {
    this.ctx = ctx;
    this.lines = [];
  }

  line(text, meta = {}) {
    this.lines.push({ text, ...meta });
    return this;
  }

  blank() { return this.line(''); }
  error(text) { return this.line(text, { level: 'error' }); }

  /** "<indent>* label: value" with indent = 2*level spaces (level 1 => "  * ") */
  kv(level, label, value, meta = {}) {
    return this.line(`${'  '.repeat(level)}* ${label}: ${value}`, meta);
  }

  /** read n bytes and print "* label: HEX" */
  hexField(r, level, label, n = 1) {
    const start = r.abs;
    const v = r.hex(n, label);
    this.kv(level, label, v, { start, end: r.abs });
    return v;
  }

  /** read n bytes, look up tableName, print "* label: MEANING (HEX)" */
  enumField(r, level, label, tableName, n = 1, fallback = 'RFU') {
    const start = r.abs;
    const v = r.hex(n, label);
    const meaning = lookup(this.ctx.t(tableName), v, fallback);
    this.kv(level, label, `${meaning} (${v})`, { start, end: r.abs, table: tableName });
    return v;
  }
}
