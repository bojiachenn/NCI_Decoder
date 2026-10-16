import { describe, it, expect } from 'vitest';
import { detectDecodeKey } from '../src/log/detect.js';

describe('detectDecodeKey', () => {
  it('NXP logcat', () => {
    const t = '08-21 06:14:35.836 628 628 D NxpExtns: find found NXPLOG_NCIX_LOGLEVEL=(0x4)\n'
      + '08-21 06:14:37.118   628  4213 I NxpNciX : len =   4 > 20000100\n';
    expect(detectDecodeKey(t).key).toBe('Nxp');
  });
  it('ST logcat', () => {
    expect(detectDecodeKey('07-14 01:55:23.998 848 4361 D StNfcHal: (#00002) Tx 20 00 01 00 \n').key).toBe('St');
  });
  it('ST logcat with LL/UL layer markers', () => {
    const t = '09-29 12:33:23.685  1160  3185 D StNfcHal: HAL st21nfc: async_callback_thread_fct event 0 status 0\n'
      + '09-29 12:33:23.703  1160  1160 D StNfcHal: (#00003) UL Tx 20 00 01 01 \n'
      + '09-29 12:33:23.704  1160  3190 D StNfcHal: (#00005) LL Rx 40 00 01 00 \n';
    expect(detectDecodeKey(t).key).toBe('St');
  });
  it('config dump only -> unknown', () => {
    expect(detectDecodeKey('D NxpExtns: find found NXPLOG_NCIX_LOGLEVEL=(0x4)\n').key).toBe(null);
  });
});
