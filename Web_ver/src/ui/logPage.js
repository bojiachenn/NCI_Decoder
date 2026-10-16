// Log page: decode whole log files (NXP "<key>NciX/NciR" or ST HAL format),
// browse/filter packets, download the CLI-identical "<file>_d.txt".
import { h, download } from './dom.js';
import { renderPacket } from '../render/html.js';
import { VENDORS } from '../core/registry.js';
import { decodeLog } from '../log/decodeLog.js';
import { detectDecodeKey } from '../log/detect.js';
import LogWorker from '../log/worker.js?worker&inline';

const PAGE = 400;

let workerBroken = false;

/** Decode in a Web Worker; if workers are unavailable (e.g. some browsers block
 *  them for pages opened from file://) fall back to the main thread. */
function runInWorker(text, opts) {
  const mainThread = () => decodeLog(text, opts);
  if (workerBroken) return Promise.resolve().then(mainThread);
  return new Promise((resolve, reject) => {
    let worker;
    try {
      worker = new LogWorker();
    } catch {
      workerBroken = true;
      resolve(mainThread());
      return;
    }
    worker.onmessage = (e) => {
      worker.terminate();
      if (e.data.ok) resolve(e.data);
      else reject(new Error(e.data.error));
    };
    worker.onerror = (e) => {
      e.preventDefault?.();
      worker.terminate();
      workerBroken = true;
      try {
        resolve(mainThread());
      } catch (err) {
        reject(err);
      }
    };
    worker.postMessage({ id: 1, text, opts });
  });
}

const isErrorResult = (res) => !!res?.lines?.some((l) => l.level === 'error');

export function mountLog(root, app) {
  const state = { files: [], results: [] };

  const fileInput = h('input', { type: 'file', multiple: true, hidden: true, onchange: () => addFiles(fileInput.files) });
  const drop = h('div', { class: 'dropzone', onclick: () => fileInput.click() },
    h('div', {}, '拖放 log 檔到這裡，或點擊選擇檔案（可多選）'),
    h('div', { class: 'hint' }, '檔案只在瀏覽器內處理，不會上傳'));
  drop.addEventListener('dragover', (e) => { e.preventDefault(); drop.classList.add('over'); });
  drop.addEventListener('dragleave', () => drop.classList.remove('over'));
  drop.addEventListener('drop', (e) => {
    e.preventDefault();
    drop.classList.remove('over');
    addFiles(e.dataTransfer.files);
  });

  const paste = h('textarea', { class: 'log-paste', spellcheck: 'false', placeholder: '或直接貼上 log 內容…' });
  const keyInput = h('input', {
    type: 'text', size: 8, value: localStorage.getItem('nci.log.key') || 'auto',
    title: 'auto = 自動偵測 log 格式；NXP 格式填 "<keyword>NciX / <keyword>NciR" 的前綴（例如 Nxp）；ST HAL 格式填 St',
  });
  const filterInput = h('input', {
    type: 'text', size: 24, value: localStorage.getItem('nci.log.filter') || 'remain_all',
    title: '非 NCI 的 log 行：包含任一關鍵字（空白分隔）才保留；remain_all = 全部保留',
  });

  const status = h('span', { class: 'hint' });
  const fileTabs = h('div', { class: 'file-tabs' });
  const resultBox = h('div', { class: 'log-results' });

  async function addFiles(list) {
    for (const f of list) state.files.push({ name: f.name, text: await f.text() });
    fileInput.value = '';
    await decodeAll();
  }

  async function decodeAll() {
    localStorage.setItem('nci.log.key', keyInput.value.trim());
    localStorage.setItem('nci.log.filter', filterInput.value.trim());
    const inputs = [...state.files];
    if (paste.value.trim()) inputs.push({ name: 'pasted_log.txt', text: paste.value });
    if (!inputs.length) {
      status.textContent = '請先選擇檔案或貼上 log。';
      return;
    }
    status.textContent = '解碼中…';
    const t0 = performance.now();
    const keyword = keyInput.value.trim() || 'auto';
    const filter = filterInput.value.trim() || 'remain_all';
    const results = [];
    for (const f of inputs) {
      let decodeKey = keyword;
      let vendor = app.vendorKey();
      let detect = null;
      if (keyword.toLowerCase() === 'auto') {
        detect = detectDecodeKey(f.text);
        decodeKey = detect.key || 'Nxp';
        // NXP proprietary / HDLL packets only decode with the NXP package
        if (decodeKey.toLowerCase() === 'nxp') vendor = 'nxp';
      }
      const info = { name: f.name, decodeKey, vendor, detect };
      try {
        results.push({ ...info, ...(await runInWorker(f.text, { decodeKey, filter, vendor, fileName: f.name })) });
      } catch (e) {
        results.push({ ...info, error: e.message, entries: [], text: '' });
      }
    }
    state.results = results;
    status.textContent = `完成：${results.length} 個檔案，${((performance.now() - t0) / 1000).toFixed(2)} 秒`;
    renderTabs(0);
  }

  function renderTabs(idx) {
    fileTabs.replaceChildren(...state.results.map((r, i) => h('button', {
      class: `seg${i === idx ? ' on' : ''}`,
      onclick: () => renderTabs(i),
    }, r.name)));
    showResult(state.results[idx]);
  }

  // ---- result view --------------------------------------------------------
  const filters = { CMD: true, RSP: true, NTF: true, DATA: true, HDLL: true, onlyErrors: false, showLines: true, q: '' };

  function showResult(r) {
    if (!r) {
      resultBox.replaceChildren();
      return;
    }
    if (r.error) {
      resultBox.replaceChildren(h('div', { class: 'ln error' }, r.error));
      return;
    }
    const packets = r.entries.filter((e) => e.type === 'packet');
    const info = h('div', { class: 'log-info' },
      `Keyword：${r.decodeKey}　Vendor：${VENDORS[r.vendor].label}`,
      r.detect ? `　（自動偵測：${r.detect.reason}）` : '');
    const warn = packets.length ? null : h('div', { class: 'log-warn' },
      '這個檔案中沒有找到任何 NCI 封包。',
      h('br'),
      r.detect && !r.detect.key
        ? '自動偵測也認不出格式。請確認 log 有開啟 NCI log（NXP：NXPLOG_NCIX/NCIR_LOGLEVEL；ST：StNfcHal debug log），或在 Decode keyword 手動填入 log 中 "<keyword>NciX" 的 keyword。'
        : `目前用的 keyword 是「${r.decodeKey}」：NXP log 要填 "<keyword>NciX / <keyword>NciR" 的前綴（通常是 Nxp），ST log 要填 St，或填 auto 讓工具自動偵測。`);
    const counts = {};
    let errors = 0;
    for (const p of packets) {
      const k = p.result?.mt || '?';
      counts[k] = (counts[k] || 0) + 1;
      if (isErrorResult(p.result)) errors++;
    }

    const list = h('div', { class: 'log-list' });
    const summary = h('span', { class: 'hint' });
    let shown = PAGE;

    const chip = (key, label) => h('label', { class: 'chip' },
      h('input', { type: 'checkbox', checked: filters[key], onchange: (e) => { filters[key] = e.target.checked; renderList(); } }),
      label);
    const search = h('input', {
      type: 'search', value: filters.q, placeholder: '搜尋（指令名稱、hex、欄位內容…）',
      oninput: (e) => { filters.q = e.target.value.toLowerCase(); renderList(); },
    });

    function match(e) {
      if (e.type !== 'packet') {
        if (!filters.showLines || filters.onlyErrors) return false;
        return !filters.q || e.text.toLowerCase().includes(filters.q);
      }
      const res = e.result;
      if (res?.mt && filters[res.mt] === false) return false;
      if (filters.onlyErrors && !isErrorResult(res)) return false;
      if (!filters.q) return true;
      return [e.prefix, res?.title, res?.raw, ...(res?.lines || []).map((l) => l.text)]
        .join('\n').toLowerCase().includes(filters.q);
    }

    function row(e) {
      if (e.type !== 'packet') return h('div', { class: `log-line ${e.type}` }, e.text);
      const res = e.result;
      const el = h('div', { class: `log-pkt${isErrorResult(res) ? ' has-error' : ''}` });
      let body = null;
      const head = h('div', {
        class: 'log-pkt-head',
        onclick: () => {
          if (body) {
            body.remove();
            body = null;
            el.classList.remove('open');
            return;
          }
          body = res
            ? renderPacket(res, { onDoc: app.openDoc, vendorDocDir: VENDORS[app.vendorKey()].docDir })
            : h('div', { class: 'ln error' }, e.prefix);
          el.append(body);
          el.classList.add('open');
        },
      },
      h('span', { class: 'ts' }, e.ts || ''),
      h('span', { class: 'dir' }, e.direction === 'TX' ? 'DH → NFCC' : e.direction === 'RX' ? 'DH ← NFCC' : ''),
      res?.mt ? h('span', { class: `badge mt-${res.mt}` }, res.mt) : null,
      h('span', { class: 'name' }, res?.title || 'Error'),
      h('span', { class: 'raw' }, res?.raw || ''));
      el.append(head);
      return el;
    }

    function renderList() {
      const rows = r.entries.filter(match);
      list.replaceChildren(...rows.slice(0, shown).map(row));
      if (rows.length > shown) {
        list.append(h('button', { class: 'more', onclick: () => { shown += PAGE * 5; renderList(); } },
          `顯示更多（還有 ${rows.length - shown} 筆）`));
      }
      summary.textContent = `顯示 ${Math.min(rows.length, shown)} / ${rows.length} 筆`;
    }

    resultBox.replaceChildren(...[
      info,
      warn,
      h('div', { class: 'stats' },
        h('span', {}, `封包 ${packets.length}`),
        Object.entries(counts).map(([k, v]) => h('span', { class: `badge mt-${k}` }, `${k} ${v}`)),
        errors ? h('span', { class: 'badge err' }, `錯誤 ${errors}`) : null,
        h('button', { onclick: () => download(`${r.name}_d.txt`, r.text) }, `下載 ${r.name}_d.txt`)),
      h('div', { class: 'toolbar' },
        chip('CMD', 'CMD'), chip('RSP', 'RSP'), chip('NTF', 'NTF'), chip('DATA', 'DATA'), chip('HDLL', 'HDLL'),
        chip('onlyErrors', '只看錯誤'), chip('showLines', '顯示一般 log 行'),
        search, summary),
      list].filter(Boolean));
    renderList();
  }

  root.replaceChildren(h('section', { class: 'page log-page' },
    h('div', { class: 'log-inputs' }, drop, fileInput, paste),
    h('div', { class: 'toolbar' },
      h('label', {}, 'Decode keyword ', keyInput),
      h('label', {}, 'Filter ', filterInput),
      h('button', { class: 'primary', onclick: decodeAll }, '解碼'),
      h('button', {
        onclick: () => {
          state.files = [];
          state.results = [];
          paste.value = '';
          fileTabs.replaceChildren();
          resultBox.replaceChildren();
          status.textContent = '';
        },
      }, '清除'),
      status),
    fileTabs,
    resultBox));

  return { onVendorChange: () => { if (state.results.length) decodeAll(); } };
}
