// Every handler named in the dispatch tables (ported from __ctrl__.py) must exist.
import { describe, it, expect } from 'vitest';
import { VENDORS } from '../src/core/registry.js';

describe('registry completeness', () => {
  for (const v of Object.values(VENDORS)) {
    for (const [gid, oids] of Object.entries(v.ctrl)) {
      if (gid === 'HDLL') {
        it(`${v.key} HDLL op codes`, () => {
          const missing = Object.values(oids).filter((n) => typeof v.handlers.HDLL[n] !== 'function');
          expect(missing).toEqual([]);
          expect(typeof v.handlers.HDLL.frame).toBe('function');
        });
        continue;
      }
      it(`${v.key} ${gid}`, () => {
        const names = Object.values(oids).flatMap((m) => Object.values(m));
        const missing = names.filter((n) => typeof v.handlers[gid]?.[n] !== 'function');
        expect(missing).toEqual([]);
      });
    }
  }
});
