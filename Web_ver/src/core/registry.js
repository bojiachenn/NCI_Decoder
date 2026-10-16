// Vendor packages: tables + dispatch (GID/OID/MT -> handler name -> function).
// Mirrors nci_decoder/vendor_registry.py + each package's __ctrl__.py.
import tablesForum20 from '../data/tables.forum20.json';
import tablesNxp from '../data/tables.nxp.json';
import { CTRL_FORUM20, CTRL_NXP } from './ctrl_spec.js';

import f20Core from '../handlers/forum20/nciCore.js';
import f20Rf from '../handlers/forum20/rfManagement.js';
import f20Nfcee from '../handlers/forum20/nfceeManagement.js';
import nxpCore from '../handlers/nxp/nciCore.js';
import nxpRf from '../handlers/nxp/rfManagement.js';
import nxpNfcee from '../handlers/nxp/nfceeManagement.js';
import nxpProp from '../handlers/nxp/proprietary.js';
import nxpHdll from '../handlers/nxp/hdll.js';

// GID name -> docs file (docs/<dir>/<file>.md)
export const GID_DOC_FILE = {
  'NCI Core': 'NCI_Core',
  'RF Management': 'RF_Management',
  'NFCEE Management': 'NFCEE_Management',
  Proprietary: 'Proprietary',
  HDLL: 'HDLL',
};

export const VENDORS = {
  forum20: {
    key: 'forum20',
    label: 'NFC Forum NCI 2.0',
    docDir: 'nfc_forum_2_0',
    tables: tablesForum20,
    ctrl: CTRL_FORUM20,
    handlers: {
      'NCI Core': f20Core,
      'RF Management': f20Rf,
      'NFCEE Management': f20Nfcee,
    },
  },
  nxp: {
    key: 'nxp',
    label: 'NXP (SN2x0)',
    docDir: 'nxp',
    tables: tablesNxp,
    ctrl: CTRL_NXP,
    handlers: {
      'NCI Core': nxpCore,
      'RF Management': nxpRf,
      'NFCEE Management': nxpNfcee,
      Proprietary: nxpProp,
      HDLL: nxpHdll,
    },
  },
};

/** vendor_registry.resolve(): "nxp" (any case) -> nxp, anything else -> forum20 */
export function resolveVendor(name) {
  const k = String(name || '').toLowerCase();
  if (k === 'nxp') return 'nxp';
  return VENDORS[k] ? k : 'forum20';
}

/** handler function + docs ref for a control message, or null */
export function findHandler(vendor, gidName, oid, mt) {
  const name = vendor.ctrl[gidName]?.[oid]?.[mt];
  if (!name) return null;
  const fn = vendor.handlers[gidName]?.[name];
  return {
    name,
    fn: fn || null,
    doc: { dir: vendor.docDir, file: GID_DOC_FILE[gidName], anchor: name.toLowerCase() },
  };
}
