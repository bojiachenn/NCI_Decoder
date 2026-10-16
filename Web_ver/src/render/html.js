// Structured decode result -> interactive DOM (byte strip + field lines).
// Hovering a field highlights its bytes and vice versa; command / table names
// call opts.onDoc({dir, file, anchor}) to open the matching docs section.
import { h } from '../ui/dom.js';
import { titleLine } from './text.js';

function byteRole(res, i, n) {
  if (res.kind === 'HDLL') return i < 2 ? 'hdr' : i >= n - 2 ? 'crc' : 'pl';
  if (res.kind === 'CTRL' || res.kind === 'DATA') return i < 3 ? 'hdr' : 'pl';
  return 'pl';
}

export function headerDescription(res) {
  if (res.kind === 'CTRL') return `${res.mt} · ${res.gidName ?? `GID ${res.gid}`} · OID 0x${res.oid}`;
  if (res.kind === 'DATA') return `DATA · Conn ID ${res.connId}`;
  if (res.kind === 'HDLL') return 'NXP HDLL frame';
  return '';
}

/**
 * @param res   decodePacket() result
 * @param opts  { onDoc(doc), vendorDocDir, compact }
 */
export function renderPacket(res, opts = {}) {
  const bytes = res.raw.match(/../g) || [];
  const byteEls = bytes.map((b, i) => h('span', { class: `b ${byteRole(res, i, bytes.length)}`, dataset: { i } }, b));
  const lineEls = [];

  const docLink = (doc, text, cls) => (doc && opts.onDoc
    ? h('a', { href: '#', class: cls, title: '開啟文件說明', onclick: (e) => { e.preventDefault(); opts.onDoc(doc); } }, text)
    : h('span', { class: cls }, text));

  const lines = res.lines.map((l) => {
    const m = /^( *)(.*)$/.exec(l.text);
    const indent = m[1].length;
    let body = m[2];
    const parts = [];
    let bullet = '';
    if (body.startsWith('* ')) { bullet = '•'; body = body.slice(2); }
    const kv = /^([^:]{1,60}):(\s?)(.*)$/.exec(body);
    if (kv && !l.level) {
      parts.push(h('span', { class: 'k' }, `${kv[1]}:`), kv[2], h('span', { class: 'v' }, kv[3]));
    } else {
      parts.push(body);
    }
    if (l.table) {
      parts.push(' ', docLink({ dir: opts.vendorDocDir, file: 'Tables', anchor: l.table }, l.table, 'tbl'));
    }
    const hasRange = l.start != null && l.end != null && l.end > l.start;
    const el = h('div', {
      class: `ln${l.level ? ` ${l.level}` : ''}${hasRange ? ' ranged' : ''}${l.text.trim() === '' ? ' empty' : ''}`,
      style: `padding-left:${0.4 + indent * 0.45}em`,
    }, bullet ? h('span', { class: 'bullet' }, bullet) : null, parts);
    if (hasRange) {
      el.addEventListener('mouseenter', () => highlight(l.start, l.end, true));
      el.addEventListener('mouseleave', () => highlight(l.start, l.end, false));
      lineEls.push({ el, start: l.start, end: l.end });
    }
    return el;
  });

  function highlight(start, end, on) {
    for (let i = start; i < end && i < byteEls.length; i++) byteEls[i].classList.toggle('hl', on);
  }
  byteEls.forEach((b, i) => {
    b.addEventListener('mouseenter', () => lineEls.forEach((x) => x.el.classList.toggle('hl', i >= x.start && i < x.end)));
    b.addEventListener('mouseleave', () => lineEls.forEach((x) => x.el.classList.remove('hl')));
  });

  const hasError = res.lines.some((l) => l.level === 'error');
  const title = res.title
    ? docLink(res.doc, res.title, 'name')
    : h('span', { class: 'name' }, '(無法解析)');

  return h('div', { class: `pkt kind-${res.kind} mt-${res.mt || ''}${hasError ? ' has-error' : ''}` },
    h('div', { class: 'pkt-head' },
      res.mt ? h('span', { class: `badge mt-${res.mt}` }, res.mt) : null,
      title,
      h('span', { class: 'desc' }, headerDescription(res)),
      res.pbf ? h('span', { class: 'badge pbf', title: 'Packet Boundary Flag = 1（分段封包）' }, 'PBF') : null),
    opts.compact ? null : h('div', { class: 'bytes' }, byteEls),
    h('div', { class: 'fields' }, lines));
}

export { titleLine };
