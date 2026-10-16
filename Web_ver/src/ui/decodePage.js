// Decode page: one packet per line (decoded in order with a shared context, so
// stateful sequences like HDLL CMD -> DL_OK work), structured or text view.
import { h, copyText } from './dom.js';
import { createContext } from '../core/context.js';
import { decodePacket } from '../core/decoder.js';
import { renderText } from '../render/text.js';
import { renderPacket } from '../render/html.js';
import { VENDORS } from '../core/registry.js';

const SAMPLES = [
  { label: 'CORE_RESET_CMD', vendor: 'forum20', hex: '20 00 01 01' },
  { label: 'CORE_RESET_NTF', vendor: 'forum20', hex: '60 00 09 02 01 20 04 04 AA BB CC DD' },
  { label: 'CORE_INIT_RSP', vendor: 'forum20', hex: '40 01 15 00 11 1E 0E 00 08 00 02 FF FF 01 01 00 03 01 00 02 00 03 01 01' },
  { label: 'CORE_SET_CONFIG_CMD', vendor: 'forum20', hex: '20 02 0E 04 00 02 E8 03 02 01 01 32 01 60 80 01 01' },
  { label: 'RF_DISCOVER_CMD', vendor: 'forum20', hex: '21 03 09 04 00 01 01 01 02 01 80 01' },
  { label: 'RF_INTF_ACTIVATED_NTF (ISO-DEP)', vendor: 'forum20', hex: '61 05 1B 01 02 04 00 FF FF 0A 04 00 04 11 22 33 44 01 20 00 00 00 00 06 05 05 78 80 70 02' },
  { label: 'RF_DEACTIVATE_NTF', vendor: 'forum20', hex: '61 06 02 03 00' },
  { label: 'NFCEE_DISCOVER_NTF', vendor: 'forum20', hex: '62 00 0C C0 00 01 00 01 00 04 11 22 33 44 01' },
  { label: 'DATA packet', vendor: 'forum20', hex: '00 00 03 90 00 AB' },
  { label: 'NXP CORE_SET_CONFIG_CMD (A0xx)', vendor: 'nxp', hex: '20 02 14 05 00 02 E8 03 80 01 01 A1 0F 02 01 01 A0 15 01 03 A5 01 00' },
  { label: 'NXP CORE_GET_CONFIG_RSP', vendor: 'nxp', hex: '40 03 10 00 03 A0 15 01 02 A0 85 04 78 88 AA 2C 85 01 01' },
  { label: 'NXP FIELD_DETECT_NTF', vendor: 'nxp', hex: '61 20 04 02 00 12 FC' },
  { label: 'NXP HDLL GET_VERSION → DL_OK', vendor: 'nxp', hex: '00 04 F1 00 00 00 6E EF\n00 10 00 12 40 04 01 03 01 02 03 04 33 00 C5 A0 01 00 CD D5' },
];

const LS_KEY = 'nci.decode.input';

export function mountDecode(root, app) {
  const input = h('textarea', {
    class: 'hex-input',
    spellcheck: 'false',
    placeholder: '貼上 NCI raw hex，例如 20 00 01 01\n可接受空白、0x、逗號；一行一個封包（依序解碼，可解析 HDLL CMD → RSP 這類前後相依的封包）',
  });
  input.value = new URLSearchParams(location.hash.split('?')[1] || '').get('hex') ?? localStorage.getItem(LS_KEY) ?? '';

  let view = localStorage.getItem('nci.decode.view') || 'tree';
  const results = h('div', { class: 'results' });

  const sampleSel = h('select', {
    onchange: () => {
      const s = SAMPLES[sampleSel.value];
      if (!s) return;
      app.setVendor(s.vendor);
      input.value = s.hex;
      sampleSel.value = '';
      run();
    },
  }, h('option', { value: '' }, '範例…'), SAMPLES.map((s, i) => h('option', { value: i }, `${VENDORS[s.vendor].label} — ${s.label}`)));

  const viewBtns = ['tree', 'text'].map((v) => h('button', {
    class: 'seg', dataset: { v },
    onclick: () => { view = v; localStorage.setItem('nci.decode.view', v); run(); },
  }, v === 'tree' ? '結構' : '文字'));

  let lastText = '';
  const toolbar = h('div', { class: 'toolbar' },
    h('button', { class: 'primary', onclick: () => run() }, '解碼'),
    sampleSel,
    h('span', { class: 'segmented' }, viewBtns),
    h('button', { onclick: () => copyText(lastText) }, '複製文字結果'),
    h('button', {
      title: '複製可直接開啟此結果的網址',
      onclick: () => {
        const url = `${location.href.split('#')[0]}#/decode?v=${app.vendorKey()}&hex=${encodeURIComponent(input.value.trim())}`;
        copyText(url);
      },
    }, '複製分享連結'),
    h('span', { class: 'hint' }, 'Ctrl+Enter 解碼 · 滑過欄位會標示對應 bytes'));

  function run() {
    localStorage.setItem(LS_KEY, input.value);
    viewBtns.forEach((b) => b.classList.toggle('on', b.dataset.v === view));
    results.replaceChildren();
    const packets = input.value.split(/\r?\n/).map((s) => s.trim()).filter(Boolean);
    if (!packets.length) {
      results.append(h('div', { class: 'empty-state' }, '輸入封包 hex 後按「解碼」，或從「範例…」選一個。'));
      lastText = '';
      return;
    }
    const ctx = createContext(app.vendorKey());
    const texts = [];
    for (const p of packets) {
      let res;
      try {
        res = decodePacket(p, ctx, 2);
      } catch (e) {
        results.append(h('div', { class: 'pkt has-error' }, h('div', { class: 'ln error' }, `Unexpected error: ${e.message}`)));
        continue;
      }
      const text = renderText(res);
      texts.push(`decoding... ${res.raw}\n\n${text}`);
      if (view === 'text') {
        results.append(h('div', { class: 'pkt' }, h('div', { class: 'raw-echo' }, res.raw), h('pre', { class: 'text-out' }, text)));
      } else {
        results.append(renderPacket(res, { onDoc: app.openDoc, vendorDocDir: ctx.vendor.docDir }));
      }
    }
    lastText = texts.join('\n');
  }

  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) { e.preventDefault(); run(); }
  });
  let timer;
  input.addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(run, 300); });

  root.replaceChildren(h('section', { class: 'page decode-page' }, input, toolbar, results));
  run();
  return { onVendorChange: run };
}
