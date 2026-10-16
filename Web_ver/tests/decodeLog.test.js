// Log-file mode (Decoder.py mode_1) port.
//  * structure tests: hand-written inputs, checked against mode_1 semantics
//  * golden tests: tests/log_golden/golden.json (python scripts/gen_log_golden.py runs the
//    real mode_1 on raw_log.txt + the synthetic *.log files here).
//    - Everything OUTSIDE packet blocks (header, passthrough lines, REDACTED/INCOMPLETE notes,
//      footer/count) must match exactly.
//    - Packet blocks must appear in the same order with the same prefix.
//    - Packet block text (= handler output, owned by the handler ports and already covered by
//      golden.test.js) is compared only with LOG_GOLDEN_PACKETS=1, with the cosmetic
//      normalisation of golden.test.js, and only when neither side has a line starting with
//      "Error:" (Python exceptions / payload errors / handlers not ported yet) and the hex
//      isn't listed in tests/known_diffs (intentional bug fixes are otherwise reported).
import { describe, it, expect } from 'vitest';
import golden from './log_golden/golden.json';
import { decodeLog, splitLines, pyStrRepr, pyListRepr } from '../src/log/decodeLog.js';
import { renderText } from '../src/render/text.js';
import { resolveVendor } from '../src/core/registry.js';
import { normalizeHex } from '../src/core/decoder.js';
import { createContext } from '../src/core/context.js';

const knownDiffs = Object.values(import.meta.glob('./known_diffs/*.json', { eager: true, import: 'default' })).flat();
const knownHex = new Set(knownDiffs.map((d) => `${resolveVendor(d.vendor)}|${normalizeHex(d.hex)}`));

// same as golden.test.js normalizeOutput (copied: importing a test file would re-register its tests)
function normalizeOutput(text) {
  return text
    .split('\n')
    .map((l) => l.replace(/[()]/g, '').replace(/ {2,}/g, ' ').trimEnd())
    .join('\n')
    .replace(/\n+$/, '');
}

const PACKET_START = /^(?:\S+ \S+)?  DH (?:-->|<--) NFCC/;

/** Split mode_1 output into {other: lines outside packets, packets: [block lines]} */
function splitPython(text) {
  const lines = text.replace(/\r\n/g, '\n').split('\n');
  const other = [];
  const packets = [];
  for (let i = 0; i < lines.length; i++) {
    if (!PACKET_START.test(lines[i])) { other.push(lines[i]); continue; }
    const block = [lines[i]];
    if (!lines[i].includes('Error: Unknown raw data!')) {
      while (block[block.length - 1] !== '#end' && i + 1 < lines.length && !PACKET_START.test(lines[i + 1])) {
        block.push(lines[++i]);
      }
    }
    packets.push(block);
  }
  return { other, packets };
}

/** Same split built from the JS structured entries */
function splitJs(res) {
  const other = [];
  const packets = [];
  for (const e of res.entries) {
    if (e.type === 'packet') packets.push((e.prefix + renderText(e.result)).replace(/\n$/, '').split('\n'));
    else if (e.role === 'footer') other.push('', e.text);
    else other.push(...e.text.split('\n'));
  }
  other.push(''); // text ends with '\n'
  return { other, packets };
}

const COMPARE_PACKETS = typeof process !== 'undefined' && process.env.LOG_GOLDEN_PACKETS === '1';

const hasError = (block) => block.some((l, i) => (i === 0 ? /Error:/.test(l) : l.startsWith('Error:')));

describe('decodeLog: golden (Python mode_1)', () => {
  for (const c of golden) {
    const opts = { fileName: c.log, decodeKey: c.decodeKey, filter: c.filter, vendor: c.decodeKey };
    const res = decodeLog(c.input, opts);
    const py = splitPython(c.output);
    const js = splitJs(res);

    describe(c.name, () => {
      it('text is consistent with entries', () => {
        expect(splitPython(res.text)).toEqual(js);
      });
      it('lines outside packet blocks match exactly', () => {
        expect(js.other.join('\n')).toBe(py.other.join('\n'));
      });
      it('same packets in the same order with the same prefix', () => {
        expect(res.entries.filter((e) => e.type === 'packet').map((e) => e.prefix))
          .toEqual(py.packets.map((b, i) => b[0].slice(0, res.entries.filter((e) => e.type === 'packet')[i]?.prefix.length)));
        expect(js.packets.length).toBe(py.packets.length);
      });
      const vendor = resolveVendor(c.decodeKey);
      const packets = res.entries.filter((e) => e.type === 'packet');
      py.packets.forEach((pyBlock, i) => {
        const jsBlock = js.packets[i];
        const hex = packets[i]?.result.raw;
        const name = `packet ${i}: ${pyBlock[0]}`;
        if (!COMPARE_PACKETS) {
          it.skip(`${name} (packet text: set LOG_GOLDEN_PACKETS=1 to compare)`, () => {});
        } else if (!jsBlock || hasError(pyBlock) || hasError(jsBlock) || knownHex.has(`${vendor}|${hex}`)) {
          it.skip(`${name} (error/known diff, not compared)`, () => {});
        } else {
          it(name, () => {
            expect(normalizeOutput(jsBlock.join('\n'))).toBe(normalizeOutput(pyBlock.join('\n')));
          });
        }
      });
    });
  }
});

describe('decodeLog: structure', () => {
  it('header, footer and empty log', () => {
    const r = decodeLog('', { fileName: 'a.log', decodeKey: 'Nxp', filter: 'remain_all' });
    expect(r.text).toBe("File Path: a.log\nSearching Keyword: Nxp\nFilter: ['remain_all']\n\n\nTotal 0 matche(s) in the file.\n");
    expect(r.entries.map((e) => e.role)).toEqual(['header', 'footer']);
    expect(r.count).toBe(0);
  });

  it('default filter is remain_all; filter accepts string or array', () => {
    expect(decodeLog('x', { decodeKey: 'Nxp' }).filter).toEqual(['remain_all']);
    expect(decodeLog('x', { decodeKey: 'Nxp', filter: '  ' }).filter).toEqual(['remain_all']);
    expect(decodeLog('x', { decodeKey: 'Nxp', filter: ' a  b ' }).filter).toEqual(['a', 'b']);
    expect(decodeLog('x', { decodeKey: 'Nxp', filter: ['A'] }).filter).toEqual(['A']);
  });

  it('filter keywords are case-insensitive substrings; packets ignore the filter', () => {
    const log = 'keep ERROR here\ndrop this\nalso Warn me\n08-21 06:14:37.118 1 2 I NxpNciX : len = 4 > 20000100\n';
    const r = decodeLog(log, { decodeKey: 'Nxp', filter: 'error warn' });
    expect(r.entries.filter((e) => e.type === 'line').map((e) => e.text)).toEqual(['keep ERROR here', 'also Warn me']);
    expect(r.entries.filter((e) => e.type === 'packet')).toHaveLength(1);
    expect(r.count).toBe(1);
  });

  it('remain_all only when it is the FIRST keyword (Python filter_key_list[0])', () => {
    const r = decodeLog('abc\nremain_all here\n', { decodeKey: 'Nxp', filter: 'zzz remain_all' });
    expect(r.entries.filter((e) => e.type === 'line').map((e) => e.text)).toEqual(['remain_all here']);
  });

  it('passthrough lines are rstripped, non-ASCII kept (no cp950 mangling), CRLF/CR handled', () => {
    const r = decodeLog('a  \t\r\n中文 log\rlast', { decodeKey: 'Nxp' });
    expect(r.entries.filter((e) => e.type === 'line').map((e) => e.text)).toEqual(['a', '中文 log', 'last']);
  });

  it('NXP-style: packet entries, prefix, short hex skipped, redacted never happens', () => {
    const log = [
      '08-21 06:14:37.118   628  4213 I NxpNciX : len =   4 > 20000100',
      '08-21 06:14:37.123   628  4212 I NxpNciR : len =   4 > 40000100',
      '08-21 06:14:37.140   628  4213 I NxpNciX : len =   1 > 20',
    ].join('\n');
    const r = decodeLog(log, { decodeKey: 'Nxp', filter: 'remain_all' });
    const pk = r.entries.filter((e) => e.type === 'packet');
    expect(pk.map((e) => [e.ts, e.direction, e.prefix])).toEqual([
      ['08-21 06:14:37.118', 'TX', '08-21 06:14:37.118  DH --> NFCC  NxpNciX'],
      ['08-21 06:14:37.123', 'RX', '08-21 06:14:37.123  DH <-- NFCC  NxpNciR'],
    ]);
    expect(pk[0].result.raw).toBe('20000100');
    expect(pk[0].result.mode).toBe(1);
    expect(r.count).toBe(2);
    // the short-hex line is consumed (not passed through)
    expect(r.entries.filter((e) => e.type === 'line')).toHaveLength(0);
    expect(r.text).toContain('08-21 06:14:37.118  DH --> NFCC  NxpNciX  << CORE_RESET_CMD >>  20000100\n');
  });

  it('custom decode key builds the tag from the key; vendor defaults to the key', () => {
    const r = decodeLog('1 2 FooNciR > 40000100', { decodeKey: 'Foo' });
    const pk = r.entries.find((e) => e.type === 'packet');
    expect(pk.prefix).toBe('1 2  DH <-- NFCC  FooNciR');
  });

  it('ST-style: fragments, redacted, incomplete, restart, order of leftovers', () => {
    const L = (s) => `07-06 09:54:12.319   843  4341 D StNfcHal: ${s}`;
    const log = [
      L('(#00001) Tx 20 00 01 01 '),
      L('(#00002) Rx 6f 02 14 (hidden)'),
      L('(#00003) Rx 60 00 05 01 02'),
      L('(#00004) Rx 61 05 0a 01'),
      L('(#00003) rx 03 04 05'),
      L('(#00005) tx 20 00 01 00'), // continuation without start => treated as start
      L('(#00006) Tx 20 04 06 03'),
      L('(#00006) Tx 20 04 01 03'), // restart replaces the pending fragment
      L('(#00007) Rx (hidden)'),
      L('(#00007) rx 01 02 03'), // continuation of a redacted packet is ignored
      'unrelated',
    ].join('\n') + '\n';
    const r = decodeLog(log, { decodeKey: 'st', filter: 'remain_all' });
    const kinds = r.entries.slice(1).map((e) => (e.type === 'packet' ? `P:${e.result.raw}:${e.seq}` : `${e.role || e.type}:${e.text}`));
    expect(kinds).toEqual([
      'P:20000101:00001',
      'P:60000501020304 05'.replace(' ', '') + ':00003',
      'P:20000100:00005',
      'P:20040103:00006',
      'line:unrelated',
      'redacted:[REDACTED: packet #00002 payload hidden by HAL]',
      'incomplete:[INCOMPLETE: packet #00004 never reached its declared length]',
      'redacted:[REDACTED: packet #00007 payload hidden by HAL]',
      'footer:Total 7 matche(s) in the file.',
    ]);
    const p = r.entries.find((e) => e.type === 'packet');
    expect(p.prefix).toBe('07-06 09:54:12.319  DH --> NFCC');
    expect(p.direction).toBe('TX');
  });

  it('an explicit ctx can be injected (e.g. to keep decoder state across files)', () => {
    const ctx = createContext('nxp');
    const used = [];
    const spy = new Proxy(ctx, { get(t, k) { used.push(k); return Reflect.get(t, k); } });
    const r = decodeLog('1 2 NxpNciX > 20000100', { decodeKey: 'Nxp', ctx: spy });
    expect(r.entries.filter((e) => e.type === 'packet')).toHaveLength(1);
    expect(used.length).toBeGreaterThan(0);
  });

  it('onProgress is called', () => {
    const calls = [];
    decodeLog('a\nb\n', { decodeKey: 'Nxp', onProgress: (d, t) => calls.push([d, t]) });
    expect(calls[0]).toEqual([0, 2]);
    expect(calls[calls.length - 1]).toEqual([2, 2]);
  });

  it('python helpers: readlines splitting and repr', () => {
    expect(splitLines('a\nb')).toEqual(['a\n', 'b']);
    expect(splitLines('a\r\nb\n')).toEqual(['a\n', 'b\n']);
    expect(splitLines('')).toEqual([]);
    expect(pyStrRepr("it's")).toBe('"it\'s"');
    expect(pyStrRepr('a\'b"c')).toBe("'a\\'b\"c'");
    expect(pyStrRepr('a\\b')).toBe("'a\\\\b'");
    expect(pyListRepr(['nxpncir', 'nxpncix'])).toBe("['nxpncir', 'nxpncix']");
  });
});
