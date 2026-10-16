// Reference page: browse/search the docs (commands by name or header hex, tables by name).
import { h } from './dom.js';
import { VENDORS, GID_DOC_FILE } from '../core/registry.js';
import { GID_NAMES } from '../core/decoder.js';
import { DOC_GROUPS, docKey, renderDoc, scrollToAnchor, refRoute, DOCS } from './docs.js';

const MT_BITS = { CMD: 1, RSP: 2, NTF: 3 };
const GID_BY_NAME = Object.fromEntries(Object.entries(GID_NAMES).map(([k, v]) => [v, Number(k)]));

/** every command + table as a searchable item */
function buildIndex() {
  const items = [];
  for (const v of Object.values(VENDORS)) {
    for (const [gidName, oids] of Object.entries(v.ctrl)) {
      const file = GID_DOC_FILE[gidName];
      if (gidName === 'HDLL') {
        for (const [op, name] of Object.entries(oids)) {
          items.push({ vendor: v, kind: 'HDLL', name, hex: `op ${op}`, key: docKey(v.docDir, file), anchor: name.toLowerCase() });
        }
        continue;
      }
      const gid = GID_BY_NAME[gidName];
      for (const [oid, mts] of Object.entries(oids)) {
        for (const [mt, name] of Object.entries(mts)) {
          const b0 = ((MT_BITS[mt] << 5) | gid).toString(16).toUpperCase().padStart(2, '0');
          items.push({ vendor: v, kind: mt, name, hex: `${b0} ${oid}`, key: docKey(v.docDir, file), anchor: name.toLowerCase() });
        }
      }
    }
    for (const t of Object.keys(v.tables)) {
      items.push({ vendor: v, kind: 'TBL', name: t, hex: '', key: docKey(v.docDir, 'Tables'), anchor: t });
    }
  }
  return items;
}

export function mountReference(root, app, route) {
  const index = buildIndex();
  const content = h('article', { class: 'md doc-content' });
  const results = h('div', { class: 'ref-results' });
  const search = h('input', {
    type: 'search', class: 'ref-search',
    placeholder: '搜尋指令 / header hex（如 61 05）/ 表名',
    oninput: () => renderResults(),
  });

  const docNav = h('div', { class: 'doc-nav' }, DOC_GROUPS.map((g) => h('div', { class: 'doc-group' },
    h('div', { class: 'doc-group-label' }, g.label),
    g.files.filter((f) => DOCS[docKey(g.dir, f)] != null).map((f) => h('a', {
      href: refRoute(docKey(g.dir, f)),
      dataset: { key: docKey(g.dir, f) },
    }, f.replace(/_/g, ' '))))));

  function renderResults() {
    const q = search.value.trim().toLowerCase();
    if (!q) {
      results.replaceChildren();
      docNav.hidden = false;
      return;
    }
    docNav.hidden = true;
    const qHex = q.replace(/\s+/g, '');
    const hits = index.filter((it) => it.name.toLowerCase().includes(q)
      || (qHex.length >= 2 && it.hex.replace(/\s+/g, '').toLowerCase().startsWith(qHex)));
    results.replaceChildren(
      h('div', { class: 'hint' }, `${hits.length} 筆`),
      ...hits.slice(0, 300).map((it) => h('a', { class: 'ref-hit', href: refRoute(it.key, it.anchor) },
        h('span', { class: `badge mt-${it.kind}` }, it.kind),
        h('span', { class: 'name' }, it.name),
        h('span', { class: 'hex' }, it.hex),
        h('span', { class: 'vendor-tag' }, it.vendor.key === 'nxp' ? 'NXP' : 'Forum'))),
    );
  }

  let currentKey = null;
  function show(key, anchor) {
    key = key || 'README';
    if (key !== currentKey) {
      renderDoc(content, key);
      currentKey = key;
      for (const a of docNav.querySelectorAll('a')) a.classList.toggle('on', a.dataset.key === key);
    }
    requestAnimationFrame(() => {
      if (!scrollToAnchor(content, anchor)) content.scrollTop = 0;
    });
  }

  root.replaceChildren(h('section', { class: 'page ref-page' },
    h('nav', { class: 'ref-side' }, search, results, docNav),
    content));
  show(route.key, route.anchor);

  return { onRoute: (r) => show(r.key, r.anchor) };
}
