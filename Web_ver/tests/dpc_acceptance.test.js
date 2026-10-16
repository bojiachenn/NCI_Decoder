// User-supplied acceptance vector for DPC_HELPER_RSP (12-bit current per NXP UM).
// Compared exactly (only trailing spaces ignored) — the golden test collapses spaces.
import { it, expect } from 'vitest';
import { createContext } from '../src/core/context.js';
import { decodePacket } from '../src/core/decoder.js';
import { renderText } from '../src/render/text.js';

const EXPECTED = `  << OPTIONAL_RSP >>
  << DPC_HELPER_RSP >>
  * Status: STATUS_OK
  * DPC Info: 36810D00000037810C00000037810C00000037810C00000036810D00000036810D00000036810D00000037810C00000036810D00000037810C000000
   ~  #  ~  Power  ~  VDDPA  ~  Current  ~  NCI cmd  ~
      0    0.666 W    2.15 V     310 mA      36810D
      1    0.653 W    2.10 V     311 mA      37810C
      2    0.653 W    2.10 V     311 mA      37810C
      3    0.653 W    2.10 V     311 mA      37810C
      4    0.666 W    2.15 V     310 mA      36810D
      5    0.666 W    2.15 V     310 mA      36810D
      6    0.666 W    2.15 V     310 mA      36810D
      7    0.653 W    2.10 V     311 mA      37810C
      8    0.666 W    2.15 V     310 mA      36810D
      9    0.653 W    2.10 V     311 mA      37810C
#end`;

it('DPC_HELPER_RSP acceptance vector', () => {
  const ctx = createContext('nxp');
  decodePacket('2F3F03050000', ctx, 2);
  const res = decodePacket(
    '4F3F3E000F36810D00000037810C00000037810C00000037810C00000036810D00000036810D00000036810D00000037810C00000036810D00000037810C000000',
    ctx, 2,
  );
  const text = renderText(res).split('\n').map((l) => l.trimEnd()).join('\n').trimEnd();
  expect(text).toBe(EXPECTED);
});
