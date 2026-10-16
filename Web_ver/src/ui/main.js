// App shell: hash router (#/decode, #/log, #/ref/<doc>/<anchor>), global vendor
// selector and the docs drawer used by "click a command/table name" links.
import '../styles.css';
import { VENDORS, resolveVendor } from '../core/registry.js';
import { mountDecode } from './decodePage.js';
import { mountLog } from './logPage.js';
import { mountReference } from './referencePage.js';
import { docKey, renderDoc, scrollToAnchor, refRoute } from './docs.js';

const appEl = document.getElementById('app');
const vendorSel = document.getElementById('vendor');
const drawer = document.getElementById('drawer');
const drawerBody = document.getElementById('drawer-body');
const drawerTitle = document.getElementById('drawer-title');
const drawerOpen = document.getElementById('drawer-open');

for (const v of Object.values(VENDORS)) vendorSel.append(new Option(v.label, v.key));

const query = new URLSearchParams(location.hash.split('?')[1] || '');
let vendor = resolveVendor(query.get('v') || localStorage.getItem('nci.vendor') || 'forum20');
vendorSel.value = vendor;

let page = null; // { name, api }

const app = {
  vendorKey: () => vendor,
  setVendor(key) {
    vendor = resolveVendor(key);
    vendorSel.value = vendor;
    localStorage.setItem('nci.vendor', vendor);
  },
  /** open a docs section ({dir, file, anchor}) in the side drawer */
  openDoc(doc) {
    const key = docKey(doc.dir, doc.file);
    drawerTitle.textContent = `${doc.file}${doc.anchor ? ` › ${doc.anchor}` : ''}`;
    drawerOpen.href = refRoute(key, doc.anchor);
    renderDoc(drawerBody, key);
    drawer.hidden = false;
    requestAnimationFrame(() => scrollToAnchor(drawerBody, doc.anchor));
  },
};

vendorSel.addEventListener('change', () => {
  app.setVendor(vendorSel.value);
  page?.api?.onVendorChange?.();
});
document.getElementById('drawer-close').addEventListener('click', () => { drawer.hidden = true; });
drawerOpen.addEventListener('click', () => { drawer.hidden = true; });
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') drawer.hidden = true; });
// links inside the drawer navigate the drawer itself, not the page
drawerBody.addEventListener('click', (e) => {
  const a = e.target.closest('a[href^="#/ref/"]');
  if (!a) return;
  e.preventDefault();
  const r = parseRef(a.getAttribute('href'));
  const [dir, file] = r.key.includes('/') ? r.key.split('/') : ['', r.key];
  app.openDoc({ dir, file, anchor: r.anchor });
});

function parseRef(hash) {
  const parts = hash.replace(/^#\/ref\/?/, '').split('?')[0].split('/').filter(Boolean);
  // keys are "README" or "<dir>/<file>"; anything after is the anchor
  let key;
  let rest;
  if (parts[0] === 'README' || parts.length === 1) {
    key = parts[0];
    rest = parts.slice(1);
  } else {
    key = parts.slice(0, 2).join('/');
    rest = parts.slice(2);
  }
  return { key, anchor: rest.length ? decodeURIComponent(rest.join('/')) : null };
}

function route() {
  const hash = location.hash || '#/decode';
  const name = hash.startsWith('#/log') ? 'log' : hash.startsWith('#/ref') ? 'ref' : 'decode';
  for (const a of document.querySelectorAll('.tabs a')) a.classList.toggle('on', a.dataset.tab === name);
  if (name === 'ref') {
    const r = parseRef(hash);
    if (page?.name === 'ref') {
      page.api.onRoute(r);
      return;
    }
    page = { name, api: mountReference(appEl, app, r) };
    return;
  }
  if (page?.name === name) return;
  page = { name, api: name === 'log' ? mountLog(appEl, app) : mountDecode(appEl, app) };
}

window.addEventListener('hashchange', route);
route();
