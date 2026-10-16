// Web Worker wrapper: decode a log off the main thread.
import { decodeLog } from './decodeLog.js';

self.onmessage = (e) => {
  const { id, text, opts } = e.data;
  try {
    const out = decodeLog(text, opts);
    // Error objects are not worth cloning back
    for (const en of out.entries) if (en.result) delete en.result.exception;
    self.postMessage({ id, ok: true, ...out });
  } catch (err) {
    self.postMessage({ id, ok: false, error: String((err && err.stack) || err) });
  }
};
