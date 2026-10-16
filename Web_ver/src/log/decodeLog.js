// Port of the per-file loop of mode_1() in NCI_Decoder/Decoder.py (log-file mode).
// Pure JS, no DOM: safe to run inside a Web Worker.
import { createContext } from '../core/context.js';
import { decodePacket } from '../core/decoder.js';
import { resolveVendor } from '../core/registry.js';
import { renderText } from '../render/text.js';
import { getProfile, extractCandidate, PY_WS } from './profiles.js';

export const DEFAULT_FILTER = 'remain_all';

const RSTRIP_RE = new RegExp(`[${PY_WS}]+$`, 'u');
const SPLIT_RE = new RegExp(`[${PY_WS}]+`, 'u');

/** Python str.rstrip() */
export const pyRstrip = (s) => s.replace(RSTRIP_RE, '');

/** Python str.split() (no args) */
export const pySplit = (s) => String(s).split(SPLIT_RE).filter((x) => x !== '');

/** Python repr() of a str */
export function pyStrRepr(s) {
  const q = s.includes("'") && !s.includes('"') ? '"' : "'";
  let body = '';
  for (const ch of s) {
    const c = ch.codePointAt(0);
    if (ch === '\\') body += '\\\\';
    else if (ch === q) body += '\\' + q;
    else if (ch === '\t') body += '\\t';
    else if (ch === '\n') body += '\\n';
    else if (ch === '\r') body += '\\r';
    else if (c < 0x20 || (c >= 0x7f && c <= 0xa0) || c === 0xad) body += '\\x' + c.toString(16).padStart(2, '0');
    else if (/[\p{Cc}\p{Cf}\p{Cs}\p{Co}\p{Cn}\p{Zl}\p{Zp}]/u.test(ch) || (/\p{Zs}/u.test(ch) && ch !== ' ')) {
      body += c > 0xffff ? '\\U' + c.toString(16).padStart(8, '0') : '\\u' + c.toString(16).padStart(4, '0');
    } else body += ch;
  }
  return q + body + q;
}

/** Python repr() of a list of str, as print(filter_key_list) writes it */
export const pyListRepr = (list) => `[${list.map(pyStrRepr).join(', ')}]`;

/** file.readlines() in text mode (universal newlines); each line keeps a trailing '\n' */
export function splitLines(text) {
  const lines = String(text).split(/\r\n|\r|\n/);
  const last = lines.pop();
  const out = lines.map((l) => l + '\n');
  if (last !== '') out.push(last);
  return out;
}

const arrowOf = (dir) => (dir === 'TX' ? 'DH --> NFCC' : 'DH <-- NFCC');

/**
 * Decode one log file the way Decoder.py mode_1 does.
 *
 * @param {string} text  whole log file content
 * @param {object} opts
 *   fileName   shown in the "File Path:" header
 *   decodeKey  keyword selecting the log profile ("Nxp" -> NxpNciX/NxpNciR tags, "st" -> StNfcHal)
 *   filter     filter keywords (string, whitespace-separated, or array); default 'remain_all'
 *   vendor     decoder vendor (config "vendor"); defaults to decodeKey like Python
 *   onProgress optional (linesDone, totalLines) callback, called every 2000 lines
 * @returns {{entries: object[], text: string, count: number, filter: string[]}}
 *   entries (in output order):
 *     {type:'note', role:'header'|'redacted'|'incomplete'|'footer', text}
 *     {type:'line', text}                                   passthrough log line
 *     {type:'packet', ts, direction:'TX'|'RX', prefix, result, seq?}  result = decodePacket(..., 1)
 *   text: the full "<file>_d.txt" content (with '\n' newlines).
 */
export function decodeLog(text, opts = {}) {
  const decodeKey = opts.decodeKey ?? 'Nxp';
  const vendor = opts.vendor ?? decodeKey;
  let filterList = Array.isArray(opts.filter) ? opts.filter.slice() : pySplit(opts.filter ?? '');
  if (filterList.length === 0) filterList = [DEFAULT_FILTER];
  const fileName = opts.fileName ?? '';
  const remainAll = filterList[0] === DEFAULT_FILTER;
  const filterLower = filterList.map((k) => k.toLowerCase());

  const ctx = opts.ctx ?? createContext(resolveVendor(vendor));
  const profile = getProfile(decodeKey);
  const entries = [];
  const chunks = [];
  const emit = (s) => chunks.push(s + '\n');
  const note = (role, s) => { entries.push({ type: 'note', role, text: s }); emit(s); };

  const header = [
    `File Path: ${fileName}`,
    `Searching Keyword: ${decodeKey}`,
    `Filter: ${pyListRepr(filterList)}`,
    '',
  ];
  entries.push({ type: 'note', role: 'header', text: header.join('\n') });
  for (const h of header) emit(h);

  const decodeAndPrint = (prefix, hex, ts, direction, extra) => {
    // Python: print(prefix, end="") then the decoder output (or the exception report)
    const result = decodePacket(hex, ctx, 1);
    entries.push({ type: 'packet', ts, direction, prefix, result, ...extra });
    chunks.push(prefix + renderText(result));
  };

  let count = 0;
  const pending = new Map(); // ST sequence number -> {redacted} | {direction, ts, hex}
  const lines = splitLines(text);
  const total = lines.length;

  for (let i = 0; i < total; i++) {
    if (opts.onProgress && i % 2000 === 0) opts.onProgress(i, total);
    const line = lines[i];
    const cand = extractCandidate(line, profile);

    if (cand === null) {
      if (remainAll || filterLower.some((k) => line.toLowerCase().includes(k))) {
        // Python re-decodes the line as cp950 (mangling non-ASCII); we keep the original.
        const t = pyRstrip(line);
        entries.push({ type: 'line', text: t });
        emit(t);
      }
      continue;
    }

    if (profile.sequence == null) {
      // No fragmentation (e.g. NXP): one line = one complete packet
      const arrow = arrowOf(cand.direction);
      const tag = decodeKey + (cand.direction === 'TX' ? 'NciX' : 'NciR');
      if (cand.kind === 'redacted') {
        note('redacted', `${cand.ts}  ${arrow}  ${tag}  [REDACTED: payload hidden by HAL]`);
        count++;
        continue;
      }
      if (cand.hex.length < 6) continue;
      count++;
      decodeAndPrint(`${cand.ts}  ${arrow}  ${tag}`, cand.hex, cand.ts, cand.direction);
      continue;
    }

    // Fragmented (e.g. ST): accumulate hex per sequence number until the declared length is reached
    const seq = cand.seq;
    if (cand.kind === 'redacted') {
      pending.set(seq, { redacted: true });
      continue;
    }
    if (cand.is_start || !pending.has(seq)) {
      pending.set(seq, { direction: cand.direction, ts: cand.ts, hex: cand.hex });
    } else if (cand.is_continue && !pending.get(seq).redacted) {
      pending.get(seq).hex += cand.hex;
    }

    const entry = pending.get(seq);
    if (entry && !entry.redacted && entry.hex.length >= 6) {
      const declaredTotalBytes = 3 + parseInt(entry.hex.slice(4, 6), 16);
      if (entry.hex.length >= declaredTotalBytes * 2) {
        count++;
        decodeAndPrint(`${entry.ts}  ${arrowOf(entry.direction)}`, entry.hex, entry.ts, entry.direction, { seq });
        pending.delete(seq);
      }
    }
  }

  for (const [seq, entry] of pending) {
    count++;
    if (entry.redacted) note('redacted', `[REDACTED: packet #${seq} payload hidden by HAL]`);
    else note('incomplete', `[INCOMPLETE: packet #${seq} never reached its declared length]`);
  }

  const footer = `Total ${count} matche(s) in the file.`;
  entries.push({ type: 'note', role: 'footer', text: footer });
  emit('\n' + footer);
  if (opts.onProgress) opts.onProgress(total, total);

  return { entries, text: chunks.join(''), count, filter: filterList };
}
