// Port of NCI_Decoder/tests/test_log_profiles.py (+ a few JS-regex specific checks).
import { describe, it, expect } from 'vitest';
import {
  PROFILES, getProfile, buildDefaultProfile, locateRegion, extractTs, extractHex,
  extractCandidate, HEX_RUN_RE, TS_RE,
} from '../src/log/profiles.js';

describe('getProfile', () => {
  it('st lowercase returns st profile', () => {
    expect(getProfile('st')).toBe(PROFILES.st);
  });
  it('st uppercase is case insensitive', () => {
    expect(getProfile('ST')).toBe(PROFILES.st);
    expect(getProfile('St')).toBe(PROFILES.st);
  });
  it('other keyword returns default profile shape', () => {
    const p = getProfile('Nxp');
    expect(p.trigger).toBe('NxpNci');
    expect(p.sequence).toBeNull();
    expect(p.redacted_markers).toEqual([]);
  });
  it('arbitrary keyword still builds default profile', () => {
    const p = getProfile('Foo');
    expect(p.trigger).toBe('FooNci');
    expect(p.sequence).toBeNull();
  });
});

describe('buildDefaultProfile', () => {
  it('trigger and region', () => {
    const p = buildDefaultProfile('Nxp');
    expect(p.trigger).toBe('NxpNci');
    expect(p.region).toEqual({ mode: 'after_last_literal', marker: '>' });
  });
  it('tx direction matches only X suffix', () => {
    const p = buildDefaultProfile('Nxp');
    const [txName, txPat] = p.directions[0];
    const [rxName, rxPat] = p.directions[1];
    expect(txName).toBe('TX');
    expect(rxName).toBe('RX');
    expect(txPat.test('...NxpNciX...')).toBe(true);
    expect(txPat.test('...NxpNciR...')).toBe(false);
    expect(rxPat.test('...NxpNciR...')).toBe(true);
    expect(rxPat.test('...NxpNciX...')).toBe(false);
  });
  it('escapes regex metacharacters in key', () => {
    const [, txPat] = buildDefaultProfile('A.B').directions[0];
    expect(txPat.test('A.BNciX')).toBe(true);
    expect(txPat.test('AxBNciX')).toBe(false);
  });
  it('escapes every regex metacharacter without throwing (JS /u mode)', () => {
    const key = 'a-b/c(d)[e]{f}*+?^$|\\';
    const [, txPat] = buildDefaultProfile(key).directions[0];
    expect(txPat.test(`xx ${key}NciX yy`)).toBe(true);
  });
});

describe('locateRegion', () => {
  const lit = { mode: 'after_last_literal', marker: '>' };
  const rx = { mode: 'after_regex_end', pattern: PROFILES.st.region.pattern };
  it('after_last_literal found', () => {
    expect(locateRegion('prefix >> 0004F10000006EEF', lit)).toBe(' 0004F10000006EEF');
  });
  it('after_last_literal uses last occurrence', () => {
    expect(locateRegion('a > b > c', lit)).toBe(' c');
  });
  it('after_last_literal not found', () => {
    expect(locateRegion('no marker here', lit)).toBe('');
  });
  it('after_regex_end found', () => {
    expect(locateRegion('(#00004) Rx 60 00 1f', rx)).toBe(' 60 00 1f');
  });
  it('after_regex_end not found', () => {
    expect(locateRegion('nothing matches here', rx)).toBe('');
  });
  it('unknown mode returns empty', () => {
    expect(locateRegion('anything', { mode: 'bogus' })).toBe('');
  });
});

describe('extractTs', () => {
  it('matches two token prefix', () => {
    expect(extractTs('08-21 06:14:35.847  DH --> NFCC  NxpNciX  << ... >>')).toBe('08-21 06:14:35.847');
  });
  it('empty string when no second token', () => {
    expect(extractTs('')).toBe('');
    expect(extractTs('onlyoneword')).toBe('');
  });
  it('TS_RE is anchored at the start', () => {
    expect(TS_RE.exec(' a b')).toBeNull();
  });
});

describe('extractHex', () => {
  it('contiguous', () => {
    expect(extractHex('  0004F10000006EEF')).toBe('0004F10000006EEF');
  });
  it('space separated', () => {
    expect(extractHex(' 60 00 1f 02')).toBe('60001f02');
  });
  it('no match returns empty', () => {
    expect(extractHex('no hex here at all only words')).toBe('');
  });
  it('trailing newline not embedded', () => {
    const r = extractHex(' 20 01\n');
    expect(r).toBe('2001');
    expect(r).not.toContain('\n');
  });
  it('Python whitespace semantics (\\x1f counts as whitespace)', () => {
    expect(extractHex(' 20\x1f01')).toBe('2001');
    expect(HEX_RUN_RE.exec('zz 20 01')[0]).toBe('20 01');
  });
});

describe('extractCandidate: default profile', () => {
  const p = getProfile('Nxp');
  it('non triggering line returns null', () => {
    expect(extractCandidate('some unrelated log line', p)).toBeNull();
  });
  it('tx hex extraction', () => {
    const line = '08-21 06:14:35.847  DH --> NFCC  NxpNciX  << Nxp HDLL: DL_GET_VERSION >>  0004F10000006EEF';
    expect(extractCandidate(line, p)).toEqual({
      kind: 'candidate', direction: 'TX', ts: '08-21 06:14:35.847', hex: '0004F10000006EEF',
    });
  });
  it('rx direction', () => {
    const line = '08-21 06:14:37.654  DH <-- NFCC  NxpNciR  << RF_DISCOVER_RSP >>  41030100';
    const c = extractCandidate(line, p);
    expect(c.direction).toBe('RX');
    expect(c.hex).toBe('41030100');
  });
  it('trigger present but no direction', () => {
    expect(extractCandidate('this has NxpNci in it but no X or R suffix', p)).toBeNull();
  });
});

describe('extractCandidate: ST sequence profile', () => {
  const p = getProfile('st');
  it('start line', () => {
    const line = '07-06 09:54:12.323   843  4342 D StNfcHal: (#00004) Rx 60 00 1f 02 01 20 02 1a '
      + '06 03 02 06 17 50 03 02 01 00 44 02 15 00 00 55 97 00 00 00 00 00 01 22';
    const c = extractCandidate(line, p);
    expect(c.kind).toBe('candidate');
    expect(c.seq).toBe('00004');
    expect(c.direction).toBe('RX');
    expect(c.is_start).toBe(true);
    expect(c.is_continue).toBe(false);
    const expected = ('60 00 1f 02 01 20 02 1a 06 03 02 06 17 50 03 02 '
      + '01 00 44 02 15 00 00 55 97 00 00 00 00 00 01 22').split(/\s+/).join('');
    expect(c.hex).toBe(expected);
    expect(c.hex.length).toBe(64);
  });
  it('continuation line same sequence', () => {
    const c = extractCandidate('07-06 09:54:12.323   843  4342 D StNfcHal: (#00004) rx 20 01', p);
    expect(c.kind).toBe('candidate');
    expect(c.seq).toBe('00004');
    expect(c.direction).toBe('RX');
    expect(c.is_start).toBe(false);
    expect(c.is_continue).toBe(true);
    expect(c.hex).toBe('2001');
  });
  it('hex sequence number', () => {
    const c = extractCandidate('07-06 09:54:12.333   843  4342 D StNfcHal: (#0000A) Rx 4f 02 01 00', p);
    expect(c).not.toBeNull();
    expect(c.seq).toBe('0000A');
    expect(c.is_start).toBe(true);
  });
  it('tx start', () => {
    const c = extractCandidate('07-06 09:54:12.328   843  4342 D StNfcHal: (#00008) Tx 2f 02 02 02 01', p);
    expect(c.direction).toBe('TX');
    expect(c.is_start).toBe(true);
    expect(c.hex).toBe('2f02020201');
  });
  it('redacted marker', () => {
    const c = extractCandidate('07-06 09:54:12.400   843  4342 D StNfcHal: (#00005) Tx (hidden)', p);
    expect(c.kind).toBe('redacted');
    expect(c.seq).toBe('00005');
    expect(c.direction).toBe('TX');
  });
  it('sequence present but no direction returns null', () => {
    expect(extractCandidate('07-06 09:54:12.400   843  4342 D StNfcHal: (#00006) some other content', p)).toBeNull();
  });
  it('non triggering line returns null', () => {
    expect(extractCandidate('no StNfcHal marker in this line', p)).toBeNull();
  });
  it('lowercase start word is not a start', () => {
    const c = extractCandidate('07-06 09:54:12.323   843  4342 D StNfcHal: (#00009) tx 01 02', p);
    expect(c.is_start).toBe(false);
    expect(c.is_continue).toBe(true);
  });
  it('word boundary is Unicode-aware like Python (no match inside a CJK word)', () => {
    expect(extractCandidate('a b StNfcHal: (#00001) 中Tx 20 00 01 01', p)).toBeNull();
    expect(extractCandidate('a b StNfcHal: (#00001) Txx 20', p)).toBeNull();
    expect(extractCandidate('a b StNfcHal: (#00001) :Tx: 20 00 01 01', p).hex).toBe('20000101');
  });
});
