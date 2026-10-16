// Guess the mode-1 decode keyword from the log content, so users don't have to know
// that ST logs need "St" and NXP logs need the "<key>" of "<key>NciX/<key>NciR".

const NXP_TAG_RE = /\b([A-Za-z0-9_]+)Nci[XR]\b/g;

/** @returns {{key: string|null, reason: string}} */
export function detectDecodeKey(text) {
  const sample = text.length > 4_000_000 ? text.slice(0, 4_000_000) : text;
  // "(#00002) Tx 20 00 ..." and the layered variant "(#00003) UL Tx 20 00 ..." / "LL Rx ..."
  if (/StNfcHal:\s*\(#[0-9A-Fa-f]+\)[^\n]*?\b[TtRr]x\b/.test(sample)) {
    return { key: 'St', reason: '偵測到 ST HAL 格式（StNfcHal: (#000N) [LL/UL] Tx/Rx ...）' };
  }
  const counts = {};
  for (const m of sample.matchAll(NXP_TAG_RE)) {
    // skip config-dump noise like "NXPLOG_NCIX_LOGLEVEL"
    if (/LOG/i.test(m[1])) continue;
    counts[m[1]] = (counts[m[1]] || 0) + 1;
  }
  const best = Object.entries(counts).sort((a, b) => b[1] - a[1])[0];
  if (best) return { key: best[0], reason: `偵測到 "${best[0]}NciX / ${best[0]}NciR" 格式` };
  return { key: null, reason: '找不到已知的 NCI log 格式（NXP 的 "<keyword>NciX/NciR" 或 ST 的 "StNfcHal: (#N) Tx/Rx"）' };
}
