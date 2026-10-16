// Port of NCI_Decoder/log_profiles.py: recognise NCI packets (or fragments)
// inside vendor HAL log lines. No DOM dependencies (usable in a Web Worker).
//
// Regex notes (Python `re` on str -> JS):
//   * Python \s / \S / str.split() use str.isspace(), which also covers
//     \x1c-\x1f and \x85 (JS \s doesn't) and excludes ﻿ (JS \s includes it),
//     so an explicit class is used.
//   * Python \b on str is Unicode-aware (\w = letters/digits/_ of any script);
//     JS \b is ASCII-only even with /u, so word boundaries are lookarounds.

export const PY_WS = '\\t-\\r \\x1c-\\x1f\\x85\\xa0\\u1680\\u2000-\\u200a\\u2028\\u2029\\u202f\\u205f\\u3000';
const S = `[${PY_WS}]`;
const NS = `[^${PY_WS}]`;
const W = '[\\p{L}\\p{N}_]';

/** Python-style \b<word>\b */
const wordRe = (body) => new RegExp(`(?<!${W})${body}(?!${W})`, 'u');

/** re.escape equivalent for building patterns from a user-typed key */
export const escapeRegExp = (s) => String(s).replace(/[.*+?^${}()|[\]\\/]/g, '\\$&');

// Shared extraction primitive: pulls hex bytes out of a located region,
// handling both contiguous ("20000100") and space-separated ("20 00 01 01") styles.
export const HEX_RUN_RE = new RegExp(`(?:[0-9A-Fa-f]{2}${S}*)+`, 'u');

// First two whitespace-separated tokens are the timestamp ("MM-DD HH:MM:SS.mmm").
export const TS_RE = new RegExp(`^(${NS}+)${S}+(${NS}+)`, 'u');

export const PROFILES = {
  st: {
    trigger: 'StNfcHal',
    sequence: /\(#([0-9A-Fa-f]+)\)/,
    // Uppercase Tx/Rx = first segment of a new packet; lowercase tx/rx = continuation
    // of the same packet (ST HAL splits long packets across multiple log lines).
    start_directions: [['TX', wordRe('Tx')], ['RX', wordRe('Rx')]],
    continue_directions: [['TX', wordRe('tx')], ['RX', wordRe('rx')]],
    region: { mode: 'after_regex_end', pattern: wordRe('[TtRr]x') },
    redacted_markers: ['(hidden)'],
  },
};

/** NXP-style profile: '<key>NciX' / '<key>NciR' tags, hex after the last '>'. */
export function buildDefaultProfile(decodeKey) {
  return {
    trigger: decodeKey + 'Nci',
    directions: [
      ['TX', new RegExp(escapeRegExp(decodeKey) + 'NciX', 'u')],
      ['RX', new RegExp(escapeRegExp(decodeKey) + 'NciR', 'u')],
    ],
    region: { mode: 'after_last_literal', marker: '>' },
    redacted_markers: [],
    sequence: null,
  };
}

/** 'st' (any case) -> ST HAL profile; anything else -> default NXP-shaped profile */
export function getProfile(decodeKey) {
  if (String(decodeKey).toLowerCase() === 'st') return PROFILES.st;
  return buildDefaultProfile(decodeKey);
}

export function locateRegion(line, regionCfg) {
  if (regionCfg.mode === 'after_last_literal') {
    const idx = line.lastIndexOf(regionCfg.marker);
    return idx !== -1 ? line.slice(idx + regionCfg.marker.length) : '';
  }
  if (regionCfg.mode === 'after_regex_end') {
    const m = regionCfg.pattern.exec(line);
    return m ? line.slice(m.index + m[0].length) : '';
  }
  return '';
}

export function extractTs(line) {
  const m = TS_RE.exec(line);
  return m ? `${m[1]} ${m[2]}` : '';
}

const WS_SPLIT_RE = new RegExp(`${S}+`, 'gu');

/** Hex bytes of a region with ALL whitespace stripped (incl. a swallowed newline). */
export function extractHex(region) {
  const m = HEX_RUN_RE.exec(region);
  return m ? m[0].replace(WS_SPLIT_RE, '') : '';
}

const firstMatch = (dirs, line) => {
  for (const [name, pat] of dirs) if (pat.test(line)) return name;
  return null;
};

/**
 * Try to recognise an NCI packet (or fragment) in one log line.
 * Returns null if the line doesn't belong to this profile; otherwise
 *   default profile:  {kind:'candidate'|'redacted', direction, ts, hex?}
 *   sequence profile: {kind, seq, direction, ts, is_start, is_continue, hex?}
 */
export function extractCandidate(line, profile) {
  if (!line.includes(profile.trigger)) return null;

  const ts = extractTs(line);

  if (profile.sequence == null) {
    const direction = firstMatch(profile.directions, line);
    if (direction === null) return null;
    const region = locateRegion(line, profile.region);
    if (profile.redacted_markers.some((mk) => region.includes(mk))) {
      return { kind: 'redacted', direction, ts };
    }
    return { kind: 'candidate', direction, ts, hex: extractHex(region) };
  }

  // Sequence-based (fragmentable) profile.
  const seqMatch = profile.sequence.exec(line);
  if (seqMatch === null) return null;
  const seq = seqMatch[1];

  const isStart = profile.start_directions.some(([, pat]) => pat.test(line));
  const isContinue = profile.continue_directions.some(([, pat]) => pat.test(line));
  if (!isStart && !isContinue) return null;

  const direction = firstMatch(isStart ? profile.start_directions : profile.continue_directions, line);

  const region = locateRegion(line, profile.region);
  if (profile.redacted_markers.some((mk) => region.includes(mk))) {
    return { kind: 'redacted', seq, direction, ts, is_start: isStart, is_continue: isContinue };
  }
  return {
    kind: 'candidate', seq, direction, ts,
    is_start: isStart, is_continue: isContinue, hex: extractHex(region),
  };
}
