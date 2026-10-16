// Bundles ../Docs/**/*.md (repo root Docs/) at build time and renders them with marked.
// Doc keys are paths relative to Docs/ without ".md", e.g. "nxp/RF_Management".
import { marked } from 'marked';

const RAW = import.meta.glob('../../../Docs/**/*.md', { query: '?raw', import: 'default', eager: true });

export const DOCS = {};
for (const [path, text] of Object.entries(RAW)) {
  const key = path.replace(/^.*\/Docs\//, '').replace(/\.md$/, '');
  DOCS[key] = text;
}

export const DOC_GROUPS = [
  { dir: '', label: '總覽', files: ['README'] },
  { dir: 'nfc_forum_2_0', label: 'NFC Forum 2.0', files: ['NCI_Core', 'RF_Management', 'NFCEE_Management', 'Tables'] },
  { dir: 'nxp', label: 'NXP', files: ['NCI_Core', 'RF_Management', 'NFCEE_Management', 'Proprietary', 'HDLL', 'Tables'] },
  { dir: 'nfc_forum_2_3', label: 'NFC Forum 2.3 (未接上)', files: ['README'] },
];

export const docKey = (dir, file) => (dir ? `${dir}/${file}` : file);

const htmlCache = new Map();
export function docHtml(key) {
  if (!htmlCache.has(key)) {
    const text = DOCS[key];
    htmlCache.set(key, text == null ? `<p>找不到文件：${key}</p>` : marked.parse(text));
  }
  return htmlCache.get(key);
}

/** "/a/b/../c" -> "a/c" */
function normPath(p) {
  const out = [];
  for (const part of p.split('/')) {
    if (!part || part === '.') continue;
    if (part === '..') out.pop();
    else out.push(part);
  }
  return out.join('/');
}

export const refRoute = (key, anchor) => `#/ref/${key}${anchor ? `/${encodeURIComponent(anchor)}` : ''}`;

/**
 * Render a doc into `container` and rewrite its links:
 *   *.md(#anchor) -> app route #/ref/<key>/<anchor>, "#x" -> same doc anchor,
 *   python source links -> inert (not available in the web build), http -> new tab.
 */
export function renderDoc(container, key) {
  container.innerHTML = docHtml(key);
  const dir = key.includes('/') ? key.slice(0, key.lastIndexOf('/')) : '';
  for (const a of container.querySelectorAll('a[href]')) {
    const href = a.getAttribute('href');
    if (/^https?:/.test(href)) {
      a.target = '_blank';
      a.rel = 'noopener';
      continue;
    }
    const [path, anchor] = href.split('#');
    if (!path) {
      a.setAttribute('href', refRoute(key, anchor));
    } else if (path.endsWith('.md')) {
      const target = normPath(`${dir}/${path.slice(0, -3)}`);
      if (DOCS[target] != null) a.setAttribute('href', refRoute(target, anchor));
      else a.replaceWith(inert(a, '此文件不在網頁版中'));
    } else {
      a.replaceWith(inert(a, '原始碼連結（網頁版不提供）'));
    }
  }
  // Tables wide -> horizontal scroll wrapper
  for (const t of container.querySelectorAll('table')) {
    const wrap = document.createElement('div');
    wrap.className = 'table-wrap';
    t.replaceWith(wrap);
    wrap.append(t);
  }
}

function inert(a, title) {
  const span = document.createElement('span');
  span.className = 'inert-link';
  span.title = title;
  span.append(...a.childNodes);
  return span;
}

/** scroll to an anchor id inside container (ids are lower/upper-case handler/table names) */
export function scrollToAnchor(container, anchor) {
  if (!anchor) {
    container.scrollTop = 0;
    return null;
  }
  const el = container.querySelector(`[id="${CSS.escape(anchor)}"]`)
    || container.querySelector(`[id="${CSS.escape(anchor.toLowerCase())}"]`);
  if (el) {
    el.scrollIntoView({ block: 'start' });
    const heading = el.nextElementSibling && /^H\d$/.test(el.nextElementSibling.tagName) ? el.nextElementSibling : el;
    heading.classList.add('flash');
    setTimeout(() => heading.classList.remove('flash'), 1600);
  }
  return el;
}
